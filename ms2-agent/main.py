import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.config.env import env
from app.config.postgres import connect_postgres
from app.config.neo4j import connect_neo4j, close_neo4j
from app.app import app

@app.on_event("startup")
def on_startup():
    print("[INFO] Starting up ms2-agent service...")
    connect_postgres()
    connect_neo4j()

@app.on_event("shutdown")
def on_shutdown():
    print("[INFO] Shutting down ms2-agent service...")
    close_neo4j()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=env.FASTAPI_PORT,
        reload=(env.PYTHON_ENV == "development")
    )
