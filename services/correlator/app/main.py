from fastapi import FastAPI
app = FastAPI(title="PRISM Correlator")

@app.get("/healthz")
def health():
    return {"status": "ok", "service": "correlator"}

@app.get("/root-incidents")
def incidents():
    return store


from pydantic import BaseModel
from typing import List, Dict, Any

class Alert(BaseModel):
    labels: Dict[str, Any]
    annotations: Dict[str, Any] = {}

class Webhook(BaseModel):
    alerts: List[Alert]

store = {"parent": None, "children": []}

@app.post("/webhook")
def webhook(payload: Webhook):
    alerts = payload.alerts
    parent = None
    for a in alerts:
        if a.labels.get("alertname") == "vm_metrics_down":
            parent = a.labels
            break
    if not parent and alerts:
        parent = alerts[0].labels
    children = [a.labels for a in alerts if a.labels != parent]
    store["parent"] = parent
    store["children"] = children
    return {"parent": parent, "children": children, "suppressed": len(children)}
