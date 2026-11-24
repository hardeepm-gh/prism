from fastapi import FastAPI, Header, HTTPException, Depends
import os
from fastapi.responses import PlainTextResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter
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
from pathlib import Path
from pydantic import BaseModel
from typing import List, Dict, Any

PRISM_API_KEY = os.environ.get("PRISM_API_KEY", "")

def require_key(x_prism_api_key: str = Header(default=""), authorization: str = Header(default="")):
    if PRISM_API_KEY and (x_prism_api_key == PRISM_API_KEY or authorization == f"Bearer {PRISM_API_KEY}"):
        return
    raise HTTPException(status_code=401, detail="invalid API key")

app = FastAPI(title="PRISM Correlator")
GLPI_URL = os.getenv("GLPI_URL", "http://glpi:80/apirest.php")
GLPI_USER = os.environ["GLPI_USER"]
GLPI_PASS = os.environ["GLPI_PASS"]
GLPI_APP_TOKEN = os.getenv("GLPI_APP_TOKEN", "")
AUDIT_FILE = Path(os.getenv("AUDIT_FILE", "/data/correlator-audit.jsonl"))
WEBHOOK_COUNT = Counter("prism_webhook_total", "Total webhooks received")
TICKETS_CREATED = Counter("prism_glpi_tickets_total", "GLPI tickets auto-created")

def audit(event, data):
    try:
        AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(AUDIT_FILE, "a") as f:
            f.write(json.dumps({"ts": int(time.time()), "event": event, "data": data}) + "\n")
    except Exception as e:
        print(f"audit write failed: {e}")

def load_audit():
    out = []
    try:
        if AUDIT_FILE.exists():
            for line in open(AUDIT_FILE):
                line = line.strip()
                if line:
                    out.append(json.loads(line))
    except Exception as e:
        print(f"audit load failed: {e}")
    return out

@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    return PlainTextResponse(generate_latest().decode(), media_type=CONTENT_TYPE_LATEST)

store = {"parent": None, "children": [], "glpi_ticket_id": None}
# Restore last incident from audit on startup (survives pod restart if /data is on PVC)
for entry in load_audit():
    if entry.get("event") == "correlation":
        d = entry.get("data", {})
        store["parent"] = d.get("parent")
        store["children"] = d.get("children", [])
        store["glpi_ticket_id"] = d.get("glpi_ticket_id")

def create_glpi_ticket(parent, children):
    try:
        headers = {}
        if GLPI_APP_TOKEN:
            headers["App-Token"] = GLPI_APP_TOKEN
        r = _with_retry(lambda: requests.get(f"{GLPI_URL}/initSession", auth=(GLPI_USER, GLPI_PASS), headers=headers, timeout=5))
        print(f"GLPI initSession status {r.status_code} body {r.text[:300]}")
        j = r.json()
        if isinstance(j, list):
            print(f"GLPI initSession error list: {j}")
            return None
        sess = j.get("session_token")
        if not sess:
            return None
        name = f"[PRISM] {parent.get('root_correlation_key','unknown')} - {parent.get('alertname','unknown')}"
        content = f"Parent: {parent.get('alertname')} | Children: {', '.join([c.get('alertname','?') for c in children])} suppressed: {len(children)} | Root correlation: {parent.get('root_correlation_key')} | Approval: pending | Action: restart-vm"
        h2 = {"Session-Token": sess, "Content-Type": "application/json"}
        if GLPI_APP_TOKEN:
            h2["App-Token"] = GLPI_APP_TOKEN
        r2 = _with_retry(lambda: requests.post(f"{GLPI_URL}/Ticket", headers=h2, json={"input": {"name": name, "content": content, "status": 2, "priority": 5, "type": 1}}, timeout=5))
        j = r2.json()
        _with_retry(lambda: requests.get(f"{GLPI_URL}/killSession", headers={"Session-Token": sess}, timeout=5))
        return j.get("id")
    except Exception as e:
        print(f"GLPI ticket failed: {e}")
        return None

@app.get("/healthz")
def health():
    return {"status": "ok", "service": "correlator"}

@app.get("/root-incidents")
def incidents():
    return store

@app.get("/audit")
def get_audit():
    return {"entries": load_audit()}

class Alert(BaseModel):
    labels: Dict[str, Any]
    annotations: Dict[str, Any] = {}

class Webhook(BaseModel):
    alerts: List[Alert]

@app.post("/webhook")
def webhook(payload: Webhook, _auth=Depends(require_key)):
    WEBHOOK_COUNT.inc()
    alerts = payload.alerts
    audit("webhook_received", {"alerts": [a.labels for a in alerts]})
    parent = None
    for a in alerts:
        if a.labels.get("alertname") == "vm_metrics_down":
            parent = a.labels
            break
    if not parent and alerts:
        parent = alerts[0].labels
    children = [a.labels for a in alerts if a.labels != parent]
    ticket_id = create_glpi_ticket(parent, children)
    if ticket_id:
        TICKETS_CREATED.inc()
    store["parent"] = parent
    store["children"] = children
    store["glpi_ticket_id"] = ticket_id
    audit("correlation", {"parent": parent, "children": children, "glpi_ticket_id": ticket_id})
    return {"parent": parent, "children": children, "suppressed": len(children), "glpi_ticket_id": ticket_id}
