from fastapi import FastAPI
app = FastAPI(title="PRISM Remediator")

@app.get("/healthz")
def health():
    return {"status": "ok", "service": "remediator"}

@app.get("/actions")
def actions():
    return {"actions": actions_log}


from pydantic import BaseModel
from typing import Optional

class ExecuteReq(BaseModel):
    incident_id: str
    action: str
    approval_id: Optional[str] = None

actions_log = []

@app.post("/execute")
def execute(req: ExecuteReq):
    if not req.approval_id:
        return {"error": "approval required", "status": "forbidden"}
    entry = {"incident_id": req.incident_id, "action": req.action, "approval_id": req.approval_id, "status": "executed"}
    actions_log.append(entry)
    return entry
