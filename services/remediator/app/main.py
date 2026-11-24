from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.responses import PlainTextResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import os, requests
import time as _time

def _with_retry(fn, attempts=3, backoff=1.0):
    last = None
    for i in range(attempts):
        try:
            return fn()
        except Exception as e:
            last = e
            print(f'GLPI attempt {i+1}/{attempts} failed: {e}')
            if i < attempts - 1:
                _time.sleep(backoff * (2 ** i))
    raise last if last else RuntimeError('GLPI retry exhausted')
import json, time
from pydantic import BaseModel
from typing import Optional

PRISM_API_KEY = os.environ.get("PRISM_API_KEY", "")

def require_key(x_prism_api_key: str = Header(default="")):
    if not PRISM_API_KEY or x_prism_api_key != PRISM_API_KEY:
        raise HTTPException(status_code=401, detail="invalid API key")

app = FastAPI(title="PRISM Remediator")

AUDIT_FILE = "/data/remediator-audit.jsonl"

def load_audit():
    try:
        with open(AUDIT_FILE) as f:
            return [json.loads(line) for line in f if line.strip()]
    except FileNotFoundError:
        return []

def audit(event, data):
    entry = {"ts": int(time.time()), "event": event, "data": data}
    try:
        os.makedirs(os.path.dirname(AUDIT_FILE), exist_ok=True)
        with open(AUDIT_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print(f"audit write failed: {e}")
    return entry

# Restore actions_log from audit on startup
actions_log = []
for _e in load_audit():
    if _e.get("event") == "action_executed" and isinstance(_e.get("data"), dict):
        actions_log.append(_e["data"])

GLPI_URL = os.getenv("GLPI_URL", "http://glpi:80/apirest.php")
GLPI_USER = os.environ["GLPI_USER"]
GLPI_PASS = os.environ["GLPI_PASS"]
GLPI_APP_TOKEN = os.getenv("GLPI_APP_TOKEN", "")

def update_glpi_ticket(ticket_id, approval_id, action):
    try:
        h = {}
        if GLPI_APP_TOKEN:
            h["App-Token"] = GLPI_APP_TOKEN
        r = _with_retry(lambda: requests.get(f"{GLPI_URL}/initSession", auth=(GLPI_USER, GLPI_PASS), headers=h, timeout=5))
        j = r.json()
        if isinstance(j, list):
            print(f"GLPI initSession error: {j}")
            return False
        sess = j.get("session_token")
        if not sess:
            return False
        h2 = {"Session-Token": sess, "Content-Type": "application/json"}
        if GLPI_APP_TOKEN:
            h2["App-Token"] = GLPI_APP_TOKEN
        r2 = _with_retry(lambda: requests.put(f"{GLPI_URL}/Ticket/{ticket_id}", headers=h2, json={"input": {"status": 5, "content": f"Executed {action} via approval {approval_id}"}}, timeout=5))
        print(f"GLPI Ticket {ticket_id} update status {r2.status_code} body {r2.text[:200]}")
        return r2.status_code in (200, 201)
    except Exception as e:
        print(f"GLPI ticket update failed: {e}")
        return False

class ExecuteReq(BaseModel):
    incident_id: str
    action: str
    approval_id: Optional[str] = None
    glpi_ticket_id: Optional[int] = None

@app.get("/healthz")
def health():
    return {"status": "ok", "service": "remediator"}

@app.get("/actions")
def actions():
    return {"actions": actions_log}

@app.get("/audit")
def get_audit():
    return {"entries": load_audit()}

@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    return PlainTextResponse(generate_latest().decode(), media_type=CONTENT_TYPE_LATEST)

@app.post("/execute")
def execute(req: ExecuteReq, _auth=Depends(require_key)):
    if not req.approval_id:
        return {"error": "approval required", "status": "forbidden"}
    glpi_updated = False
    if req.glpi_ticket_id:
        glpi_updated = update_glpi_ticket(req.glpi_ticket_id, req.approval_id, req.action)
    entry = {"incident_id": req.incident_id, "action": req.action, "approval_id": req.approval_id, "status": "executed", "glpi_ticket_id": req.glpi_ticket_id, "glpi_ticket_updated": glpi_updated}
    actions_log.append(entry)
    audit("action_executed", entry)
    return entry
