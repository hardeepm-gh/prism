from fastapi import FastAPI
import os, requests
app = FastAPI(title="PRISM Remediator")

@app.get("/healthz")
def health():
    return {"status": "ok", "service": "remediator"}

@app.get("/actions")
def actions():
    return {"actions": actions_log}


from pydantic import BaseModel
from typing import Optional

GLPI_URL = os.getenv("GLPI_URL", "http://glpi:80/apirest.php")
GLPI_USER = os.getenv("GLPI_USER", "glpi")
GLPI_PASS = os.getenv("GLPI_PASS", "glpi")
GLPI_APP_TOKEN = os.getenv("GLPI_APP_TOKEN", "")

def update_glpi_ticket(ticket_id, approval_id, action):
    try:
        h = {}
        if GLPI_APP_TOKEN:
            h["App-Token"] = GLPI_APP_TOKEN
        r = requests.get(f"{GLPI_URL}/initSession", auth=(GLPI_USER, GLPI_PASS), headers=h, timeout=5)
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
        r2 = requests.put(f"{GLPI_URL}/Ticket/{ticket_id}", headers=h2, json={"input": {"status": 5, "content": f"Executed {action} via approval {approval_id}"}}, timeout=5)
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

actions_log = []

@app.post("/execute")
def execute(req: ExecuteReq):
    if not req.approval_id:
        return {"error": "approval required", "status": "forbidden"}
    glpi_updated = False
    if req.glpi_ticket_id:
        glpi_updated = update_glpi_ticket(req.glpi_ticket_id, req.approval_id, req.action)
    entry = {"incident_id": req.incident_id, "action": req.action, "approval_id": req.approval_id, "status": "executed", "glpi_ticket_id": req.glpi_ticket_id, "glpi_ticket_updated": glpi_updated}
    actions_log.append(entry)
    return entry
