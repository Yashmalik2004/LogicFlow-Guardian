from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="LogicFlow Guardian AI Service", version="1.0.0")

@app.get("/internal/health")
def health_check():
    return JSONResponse(
        content={
            "status": "OK",
            "service": "ms2-agent"
        },
        status_code=200
    )
