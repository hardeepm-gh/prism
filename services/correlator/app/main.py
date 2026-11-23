from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter
import os, requests
from pydantic import BaseModel
from typing import List, Dict, Any

app = FastAPI(title="PRISM Correlator")

GLPI_URL = os.getenv("GLPI_URL", "http://glpi:80/apirest.php")
GLPI_USER = os.getenv("GLPI_USER", "glpi")
GLPI_PASS = os.getenv("GLPI_PASS", "glpi")
GLPI_APP_TOKEN = os.getenv("GLPI_APP_TOKEN", "")

WEBHOOK_COUNT = Counter("prism_webhook_total", "Total webhooks received")
TICKETS_CREATED = Counter("prism_glpi_tickets_total", "GLPI tickets auto-created")

@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    return PlainTextResponse(generate_latest().decode(), media_type=CONTENT_TYPE_LATEST)

store = {"parent": None, "children": [], "glpi_ticket_id": None}

def create_glpi_ticket(parent, children):
    try:
        # 1. Get session
        headers = {}
        if GLPI_APP_TOKEN:
            headers["App-Token"] = GLPI_APP_TOKEN
        r = requests.get(f"{GLPI_URL}/initSession", auth=(GLPI_USER, GLPI_PASS), headers=headers, timeout=5)
        print(f"GLPI initSession status {r.status_code} body {r.text[:300]}")
        j = r.json()
        if isinstance(j, list):
            print(f"GLPI initSession error list: {j}")
            return None
        sess = j.get("session_token")
        if not sess:
            return None
        # 2. Create ticket
        name = f"[PRISM] {parent.get('root_correlation_key','unknown')} - {parent.get('alertname','unknown')}"
        content = f"Parent: {parent.get('alertname')} | Children: {', '.join([c.get('alertname','?') for c in children])} suppressed: {len(children)} | Root correlation: {parent.get('root_correlation_key')} | Approval: pending | Action: restart-vm"
        h2 = {"Session-Token": sess, "Content-Type": "application/json"}
        if GLPI_APP_TOKEN:
            h2["App-Token"] = GLPI_APP_TOKEN
        r2 = requests.post(f"{GLPI_URL}/Ticket", headers=h2, json={"input": {"name": name, "content": content, "status": 2, "priority": 5, "type": 1}}, timeout=5)
        j = r2.json()
        # 3. Kill session
        requests.get(f"{GLPI_URL}/killSession", headers={"Session-Token": sess}, timeout=5)
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

class Alert(BaseModel):
    labels: Dict[str, Any]
    annotations: Dict[str, Any] = {}

class Webhook(BaseModel):
    alerts: List[Alert]

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
    # GLPI wiring - auto-create ticket for new parent
    ticket_id = create_glpi_ticket(parent, children)
    store["parent"] = parent
    store["children"] = children
    store["glpi_ticket_id"] = ticket_id
    return {"parent": parent, "children": children, "suppressed": len(children), "glpi_ticket_id": ticket_id}
