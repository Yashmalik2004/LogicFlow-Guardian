import os
from dotenv import load_dotenv

load_dotenv()

_required = [
    "FASTAPI_PORT",
    "MS2_DATABASE_URL",
    "NEO4J_URI",
    "NEO4J_USERNAME",
    "NEO4J_PASSWORD",
    "PYTHON_ENV",
    "MS1_BASE_URL",
]

for _key in _required:
    if not os.getenv(_key):
        raise RuntimeError(f"Missing required environment variable: {_key}")


class Env:
    FASTAPI_PORT: int = int(os.environ["FASTAPI_PORT"])
    # MS2's own PostgreSQL database — NEVER the same as MS1's DATABASE_URL.
    MS2_DATABASE_URL: str = os.environ["MS2_DATABASE_URL"]
    NEO4J_URI: str = os.environ["NEO4J_URI"]
    NEO4J_USERNAME: str = os.environ["NEO4J_USERNAME"]
    NEO4J_PASSWORD: str = os.environ["NEO4J_PASSWORD"]
    PYTHON_ENV: str = os.environ["PYTHON_ENV"]
    # Root directory where per-analysis workspace folders are created.
    # Defaults to ./workspace relative to the working directory.
    WORKSPACE_ROOT: str = os.environ.get("WORKSPACE_ROOT", "./workspace")
    # MS1 base URL — used when sending webhook callbacks from MS2 to MS1.
    MS1_BASE_URL: str = os.environ["MS1_BASE_URL"]
    # Shared secret for authenticating webhook calls to MS1.
    # Must match MS2_WEBHOOK_SECRET in ms1-core-api/.env.
    MS2_WEBHOOK_SECRET: str = os.environ.get("MS2_WEBHOOK_SECRET", "")


env = Env()
