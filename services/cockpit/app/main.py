from fastapi import FastAPI
from fastapi.responses import HTMLResponse
app = FastAPI(title="PRISM Cockpit")

@app.get("/healthz")
def health():
    return {"status": "ok", "service": "cockpit"}

@app.get("/", response_class=HTMLResponse)
def home():
    return "<h1>PRISM Cockpit</h1><p>Parent: vm_metrics_down | Children: 3 suppressed | Approval: pending -> approved | Action: restart-vm</p>"
