import os
from dotenv import load_dotenv

load_dotenv()

_required = [
    "FASTAPI_PORT",
    "DATABASE_URL",
    "NEO4J_URI",
    "NEO4J_USERNAME",
    "NEO4J_PASSWORD",
    "PYTHON_ENV",
]

for _key in _required:
    if not os.getenv(_key):
        raise RuntimeError(f"Missing required environment variable: {_key}")


class Env:
    FASTAPI_PORT: int = int(os.environ["FASTAPI_PORT"])
    DATABASE_URL: str = os.environ["DATABASE_URL"]
    NEO4J_URI: str = os.environ["NEO4J_URI"]
    NEO4J_USERNAME: str = os.environ["NEO4J_USERNAME"]
    NEO4J_PASSWORD: str = os.environ["NEO4J_PASSWORD"]
    PYTHON_ENV: str = os.environ["PYTHON_ENV"]


env = Env()
