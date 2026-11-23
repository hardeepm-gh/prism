from fastapi import FastAPI
from fastapi.responses import HTMLResponse, PlainTextResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import requests, os
app = FastAPI(title="PRISM Cockpit")
PROM = os.getenv("PROM_URL", "http://prometheus:9090")
CORR = os.getenv("CORR_URL", "http://correlator:8089")
def gj(url):
    try:
        return requests.get(url, timeout=3).json()
    except Exception as e:
        return {"error": str(e)}
@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    return PlainTextResponse(generate_latest().decode(), media_type=CONTENT_TYPE_LATEST)
@app.get("/healthz")
def health():
    return {"status": "ok", "service": "cockpit"}
@app.get("/api/live")
def live():
    t = gj(f"{PROM}/api/v1/targets?state=active")
    r = gj(f"{PROM}/api/v1/rules")
    a = gj(f"{PROM}/api/v1/alerts")
    c = gj(f"{CORR}/root-incidents")
    targets = []
    try:
        for x in t["data"]["activeTargets"]:
            targets.append({"job": x["labels"].get("job"), "instance": x["labels"].get("instance"), "health": x.get("health")})
    except Exception:
        pass
    rules = []
    try:
        for g in r["data"]["groups"]:
            for rule in g["rules"]:
                rules.append({"name": rule.get("name"), "state": rule.get("state")})
    except Exception:
        pass
    firing = []
    try:
        firing = [{"alertname": x["labels"].get("alertname"), "state": x.get("state")} for x in a["data"]["alerts"]]
    except Exception:
        pass
    return {"targets": targets, "rules": rules, "firing": firing, "correlator": c}
@app.get("/", response_class=HTMLResponse)
def home():
    t = gj(f"{PROM}/api/v1/targets?state=active")
    r = gj(f"{PROM}/api/v1/rules")
    a = gj(f"{PROM}/api/v1/alerts")
    c = gj(f"{CORR}/root-incidents")
    up = 0
    rows = ""
    try:
        for x in t["data"]["activeTargets"]:
            job = x["labels"].get("job"); inst = x["labels"].get("instance"); h = x.get("health")
            if h == "up": up += 1
            rows += f"<tr><td>{job}</td><td>{inst}</td><td>{h}</td></tr>"
    except Exception as e:
        rows = f"<tr><td colspan=3>Prometheus error: {e}</td></tr>"
    rule_rows = ""
    try:
        for g in r["data"]["groups"]:
            for rule in g["rules"]:
                rule_rows += f"<tr><td>{rule.get('name')}</td><td>{rule.get('state')}</td></tr>"
    except Exception as e:
        rule_rows = f"<tr><td colspan=2>Rules error: {e}</td></tr>"
    firing_n = 0
    try:
        firing_n = len(a["data"]["alerts"])
    except Exception:
        pass
    parent = c.get("parent", {}) if isinstance(c, dict) else {}
    ticket = c.get("glpi_ticket_id") if isinstance(c, dict) else None
    return f"""<h1>PRISM Cockpit - LIVE</h1><p>Targets: {up}/5 up | Firing: {firing_n} | Correlator Ticket: #{ticket} | Parent: {parent.get('alertname','-')}</p><h2>Prometheus Targets</h2><table border=1><tr><th>Job</th><th>Instance</th><th>Health</th></tr>{rows}</table><h2>Prometheus Rules</h2><table border=1><tr><th>Alert</th><th>State</th></tr>{rule_rows}</table><h2>Demo Chain</h2><p>4 alerts -&gt; Correlator -&gt; GLPI Ticket #2 Solved -&gt; Approval 54df53f8 -&gt; Remediator -&gt; GLPI Ticket #3 (PrismRemediatorDown, real Prometheus firing)</p><p><a href=/api/live>JSON: /api/live</a> | <a href=/metrics>Metrics</a></p>"""
