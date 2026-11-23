from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram
import time, random
app = FastAPI(title="PRISM Demo App")
REQ = Counter("demo_http_requests_total", "Total requests", ["path", "status"])
ERR = Counter("demo_http_errors_total", "Total errors", ["path"])
DUR = Histogram("demo_http_duration_seconds", "Request duration", ["path"])
@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    return PlainTextResponse(generate_latest().decode(), media_type=CONTENT_TYPE_LATEST)
@app.get("/healthz")
def health():
    return {"status": "ok", "service": "demo-app"}
@app.get("/")
def home():
    start = time.time()
    time.sleep(random.uniform(0.01, 0.05))
    DUR.labels(path="/").observe(time.time() - start)
    REQ.labels(path="/", status="200").inc()
    return {"service": "demo-app", "status": "ok", "hint": "GET /slow for latency, /fail for errors"}
@app.get("/slow")
def slow():
    start = time.time()
    time.sleep(2.0)
    DUR.labels(path="/slow").observe(time.time() - start)
    REQ.labels(path="/slow", status="200").inc()
    return {"service": "demo-app", "status": "slow", "slept_s": 2.0}
@app.get("/fail")
def fail():
    start = time.time()
    DUR.labels(path="/fail").observe(time.time() - start)
    REQ.labels(path="/fail", status="500").inc()
    ERR.labels(path="/fail").inc()
    return {"service": "demo-app", "status": "error", "error": "simulated failure"}
