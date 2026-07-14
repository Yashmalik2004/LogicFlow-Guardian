from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.routers.internal import internal_router

app = FastAPI(title="LogicFlow Guardian AI Service", version="1.0.0")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={
            "detail": exc.errors(),
            "message": "Validation failed.",
        },
    )


@app.get("/internal/health")
def health_check():
    return JSONResponse(
        content={
            "status": "OK",
            "service": "ms2-agent"
        },
        status_code=200
    )


@app.get("/health")
def standard_health_check():
    return JSONResponse(
        content={
            "status": "OK",
            "service": "ms2-agent"
        },
        status_code=200
    )


app.include_router(internal_router)
