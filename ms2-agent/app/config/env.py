import os
# from dotenv import load_dotenv

from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parents[2] / ".env"

print(f"Loading .env from: {env_path}")

load_dotenv(dotenv_path=env_path, override=True)

print("Loaded NEO4J_URI:", os.getenv("NEO4J_URI"))
print("Loaded NEO4J_DATABASE:", os.getenv("NEO4J_DATABASE"))
print("Loaded NEO4J_USERNAME:", os.getenv("NEO4J_USERNAME"))

_required = [
    "FASTAPI_PORT",
    "MS2_DATABASE_URL",
    "NEO4J_URI",
    "NEO4J_USERNAME",
    "NEO4J_PASSWORD",
    "NEO4J_DATABASE",
    "PYTHON_ENV",
    "MS1_BASE_URL",
]

for key in _required:
    if not os.getenv(key):
        raise RuntimeError(f"Missing required environment variable: {key}")


class Env:
    # FastAPI
    FASTAPI_PORT: int = int(os.environ["FASTAPI_PORT"])

    # MS2 PostgreSQL
    MS2_DATABASE_URL: str = os.environ["MS2_DATABASE_URL"]

    # Neo4j
    NEO4J_URI: str = os.environ["NEO4J_URI"]
    NEO4J_USERNAME: str = os.environ["NEO4J_USERNAME"]
    NEO4J_PASSWORD: str = os.environ["NEO4J_PASSWORD"]
    NEO4J_DATABASE: str = os.environ["NEO4J_DATABASE"]

    # Environment
    PYTHON_ENV: str = os.environ["PYTHON_ENV"]

    # Workspace
    WORKSPACE_ROOT: str = os.environ.get(
        "WORKSPACE_ROOT",
        "./workspace"
    )

    # MS1
    MS1_BASE_URL: str = os.environ["MS1_BASE_URL"]
    MS2_WEBHOOK_SECRET: str = os.environ.get(
        "MS2_WEBHOOK_SECRET",
        ""
    )


env = Env()