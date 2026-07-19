from typing import Callable

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.routers.internal import internal_router


def create_app(lifespan: Callable | None = None) -> FastAPI:
    """
    FastAPI application factory.

    Accepts an optional lifespan context manager so that startup/shutdown
    hooks can be injected from main.py without relying on the deprecated
    @app.on_event decorator.
    """
    application = FastAPI(
        title="LogicFlow Guardian AI Service",
        version="1.0.0",
        lifespan=lifespan,
    )

    # ---------------------------------------------------------------------------
    # Exception handlers
    # ---------------------------------------------------------------------------

    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        return JSONResponse(
            status_code=400,
            content={
                "detail": exc.errors(),
                "message": "Validation failed.",
            },
        )

    # ---------------------------------------------------------------------------
    # Health endpoints
    # ---------------------------------------------------------------------------

    @application.get("/internal/health")
    def health_check():
        return JSONResponse(
            content={"status": "OK", "service": "ms2-agent"},
            status_code=200,
        )

    @application.get("/health")
    def standard_health_check():
        return JSONResponse(
            content={"status": "OK", "service": "ms2-agent"},
            status_code=200,
        )

    # ---------------------------------------------------------------------------
    # Routers
    # ---------------------------------------------------------------------------

    application.include_router(internal_router)

    return application


# Convenience instance used by uvicorn when main.py imports from app.app
# (kept for backwards-compatibility with any direct imports during development)
app = create_app()
