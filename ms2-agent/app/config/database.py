"""
MS2 database configuration.

MS2 connects to its OWN PostgreSQL database (MS2_DATABASE_URL).
It must NEVER connect to MS1's database.

Responsibility: store MS2-owned execution state (AgentRun, etc.).
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config.env import env

_engine = create_engine(env.MS2_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


class Base(DeclarativeBase):
    """Declarative base for all MS2 ORM models."""
    pass


def connect_ms2_database() -> None:
    """Test MS2 PostgreSQL connectivity on startup."""
    with _engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    print("[INFO] MS2 PostgreSQL connection established successfully.")


def create_ms2_tables() -> None:
    """
    Create all MS2-owned tables if they do not already exist.
    Called during application startup after connectivity is verified.
    """
    Base.metadata.create_all(bind=_engine)
    print("[INFO] MS2 database tables verified/created successfully.")
