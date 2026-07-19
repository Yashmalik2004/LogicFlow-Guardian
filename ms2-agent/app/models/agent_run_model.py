"""
AgentRun — MS2's own execution-state table.

Stores per-analysis execution metadata owned entirely by MS2.
This table lives in MS2's own database (MS2_DATABASE_URL) and must NEVER
be created or modified inside MS1's database.

The `analysis_id` and `project_id` fields are plain integers that reference
MS1 records BY VALUE — there are no foreign keys to MS1's database.
"""
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, BigInteger, DateTime
from sqlalchemy.orm import Session

from app.config.database import Base, SessionLocal


class AgentRun(Base):
    """
    Execution record for one analysis run handled by MS2.

    Lifecycle mirrors the intake pipeline stages:
      RECEIVED → CLONING → VALIDATING → READY_FOR_PARSING → COMPLETED / FAILED
    """
    __tablename__ = "agent_run"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Reference to MS1's Analysis record by value (no cross-DB foreign key).
    analysis_id = Column(Integer, nullable=False, unique=True, index=True)
    # Reference to MS1's Project record by value.
    project_id = Column(Integer, nullable=False, index=True)

    # Current execution status within MS2's pipeline
    status = Column(String(40), nullable=False, default="RECEIVED")

    # Repository metadata discovered during intake
    repository_path = Column(Text, nullable=True)
    repository_name = Column(Text, nullable=True)
    language = Column(Text, nullable=True)
    framework = Column(Text, nullable=True)
    repository_size = Column(BigInteger, nullable=True)

    # Error details if the run failed
    error_message = Column(Text, nullable=True)

    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


# ---------------------------------------------------------------------------
# Repository helpers
# ---------------------------------------------------------------------------

def create_agent_run(analysis_id: int, project_id: int) -> AgentRun:
    """Insert a new AgentRun record with RECEIVED status, or reset/return existing."""
    with SessionLocal() as session:
        run = session.query(AgentRun).filter(AgentRun.analysis_id == analysis_id).first()
        if run:
            run.project_id = project_id
            run.status = "RECEIVED"
            run.started_at = datetime.now(timezone.utc)
            run.completed_at = None
            run.error_message = None
            session.commit()
            session.refresh(run)
            return run

        run = AgentRun(
            analysis_id=analysis_id,
            project_id=project_id,
            status="RECEIVED",
            started_at=datetime.now(timezone.utc),
        )
        session.add(run)
        session.commit()
        session.refresh(run)
        return run


def update_agent_run_status(analysis_id: int, status: str) -> None:
    """Update the status of an AgentRun by analysis_id."""
    with SessionLocal() as session:
        run = session.query(AgentRun).filter(AgentRun.analysis_id == analysis_id).first()
        if run:
            run.status = status
            run.updated_at = datetime.now(timezone.utc)
            if status in ("COMPLETED", "FAILED"):
                run.completed_at = datetime.now(timezone.utc)
            session.commit()


def update_agent_run_metadata(
    analysis_id: int,
    *,
    repository_path: str | None,
    repository_name: str | None,
    language: str | None,
    framework: str | None,
    repository_size: int | None,
) -> None:
    """Persist repository intake metadata onto the AgentRun record."""
    with SessionLocal() as session:
        run = session.query(AgentRun).filter(AgentRun.analysis_id == analysis_id).first()
        if run:
            run.repository_path = repository_path
            run.repository_name = repository_name
            run.language = language
            run.framework = framework
            run.repository_size = repository_size
            run.updated_at = datetime.now(timezone.utc)
            session.commit()


def mark_agent_run_failed(analysis_id: int, error_message: str) -> None:
    """Mark an AgentRun as FAILED with an error message."""
    with SessionLocal() as session:
        run = session.query(AgentRun).filter(AgentRun.analysis_id == analysis_id).first()
        if run:
            run.status = "FAILED"
            run.error_message = error_message
            run.completed_at = datetime.now(timezone.utc)
            run.updated_at = datetime.now(timezone.utc)
            session.commit()
