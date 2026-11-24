from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.responses import PlainTextResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from pydantic import BaseModel
from uuid import uuid4
import os, json, time
from pathlib import Path

PRISM_API_KEY = os.environ.get("PRISM_API_KEY", "")

def require_key(x_prism_api_key: str = Header(default="")):
    if not PRISM_API_KEY or x_prism_api_key != PRISM_API_KEY:
        raise HTTPException(status_code=401, detail="invalid API key")

app = FastAPI(title="PRISM Approval Gateway")
AUDIT_FILE = Path(os.getenv("AUDIT_FILE", "/data/approval-audit.jsonl"))

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

approvals = {}
for entry in load_audit():
    d = entry.get("data", {})
    if entry.get("event") in ("approval_created", "approval_approved"):
        aid = d.get("id")
        if aid:
            approvals[aid] = d

@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    return PlainTextResponse(generate_latest().decode(), media_type=CONTENT_TYPE_LATEST)

@app.get("/healthz")
def health():
    return {"status": "ok", "service": "approval-gateway"}

@app.get("/approvals")
def list_approvals():
    return approvals

@app.get("/audit")
def get_audit():
    return {"entries": load_audit()}

class ApprovalRequest(BaseModel):
    incident_id: str
    action: str
    risk: str = "L4"

@app.post("/approvals")
def create_approval(req: ApprovalRequest, _auth=Depends(require_key)):
    aid = str(uuid4())[:8]
    approvals[aid] = {"id": aid, "incident_id": req.incident_id, "action": req.action, "risk": req.risk, "status": "pending", "created_at": int(time.time())}
    audit("approval_created", approvals[aid])
    return approvals[aid]

@app.post("/approvals/{aid}/approve")
def approve(aid: str, approver: str = "human", _auth=Depends(require_key)):
    if aid not in approvals:
        return {"error": "not found"}
    approvals[aid]["status"] = "approved"
    approvals[aid]["approver"] = approver
    approvals[aid]["approved_at"] = int(time.time())
    audit("approval_approved", approvals[aid])
    return approvals[aid]
