from fastapi import FastAPI
app = FastAPI(title="PRISM Correlator")

@app.get("/healthz")
def health():
    return {"status": "ok", "service": "correlator"}

@app.get("/root-incidents")
def incidents():
    return {"parent": None, "children": []}
