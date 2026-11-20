from fastapi import FastAPI
app = FastAPI(title="PRISM Remediator")

@app.get("/healthz")
def health():
    return {"status": "ok", "service": "remediator"}

@app.get("/actions")
def actions():
    return {"actions": []}
