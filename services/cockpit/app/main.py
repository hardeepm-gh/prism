from fastapi import FastAPI
from fastapi.responses import HTMLResponse
app = FastAPI(title="PRISM Cockpit")

@app.get("/healthz")
def health():
    return {"status": "ok", "service": "cockpit"}

@app.get("/", response_class=HTMLResponse)
def home():
    return "<h1>PRISM Cockpit</h1><p>Parent: vm_metrics_down | Children: 3 suppressed | Approval: pending -> approved | Action: restart-vm</p><p>GLPI Ticket: #2 | Status: Solved | <a href=http://localhost:8081/front/ticket.form.php?id=2>Open in GLPI</a></p><p>Chain: 4 alerts -\> Correlator -\> GLPI Ticket #2 (Processing) -\> Approval 54df53f8 -\> Remediator executed -\> GLPI Ticket #2 Solved</p>"
