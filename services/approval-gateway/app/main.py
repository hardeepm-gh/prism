from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
app = FastAPI(title="PRISM Approval Gateway")

approvals = {}

@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    return PlainTextResponse(generate_latest().decode(), media_type=CONTENT_TYPE_LATEST)

@app.get("/healthz")
def health():
    return {"status": "ok", "service": "approval-gateway"}

@app.get("/approvals")
def list_approvals():
    return approvals

from pydantic import BaseModel
from uuid import uuid4
import time

class ApprovalRequest(BaseModel):
    incident_id: str
    action: str
    risk: str = "L4"

@app.post("/approvals")
def create_approval(req: ApprovalRequest):
    aid = str(uuid4())[:8]
    approvals[aid] = {"id": aid, "incident_id": req.incident_id, "action": req.action, "risk": req.risk, "status": "pending", "created_at": int(time.time())}
    return approvals[aid]

@app.post("/approvals/{aid}/approve")
def approve(aid: str, approver: str = "human"):
    if aid not in approvals:
        return {"error": "not found"}
    approvals[aid]["status"] = "approved"
    approvals[aid]["approver"] = approver
    approvals[aid]["approved_at"] = int(time.time())
    return approvals[aid]
