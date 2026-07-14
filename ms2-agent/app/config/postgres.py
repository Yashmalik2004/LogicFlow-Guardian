from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.config.env import env

_engine = create_engine(env.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


def connect_postgres() -> None:
    """Test PostgreSQL connectivity on startup."""
    with _engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    print("[INFO] PostgreSQL connection established successfully.")
