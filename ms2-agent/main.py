import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.config.env import env
from app.config.database import connect_ms2_database, create_ms2_tables
from app.config.neo4j import connect_neo4j, close_neo4j
from app.app import create_app


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Manage application startup and shutdown using the modern lifespan API."""
    # Startup
    print("[INFO] Starting up ms2-agent service...")
    connect_ms2_database()
    create_ms2_tables()
    connect_neo4j()
    yield
    # Shutdown
    print("[INFO] Shutting down ms2-agent service...")
    close_neo4j()


app = create_app(lifespan=lifespan)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=env.FASTAPI_PORT,
        reload=(env.PYTHON_ENV == "development"),
    )