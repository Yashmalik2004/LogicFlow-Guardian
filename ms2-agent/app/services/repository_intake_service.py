"""
Repository Intake Service — orchestrates the full intake pipeline.

Pipeline:
    1. Create AgentRun record in MS2's own database
    2. Send CLONING webhook to MS1
    3. Create workspace directory
    4. Clone the repository via git
    5. Send VALIDATING webhook to MS1
    6. Validate the cloned repository (non-empty, .git present, readable)
    7. Detect language and framework (metadata-only)
    8. Compute repository size
    9. Send READY_FOR_PARSING webhook to MS1 (with metadata)
   10. Update AgentRun in MS2's own database

Data contract:
    - All project data (repoUrl, repoName, branch, repositoryType) arrives in
      the payload from MS1. MS2 NEVER queries MS1's database.
    - Status updates are sent to MS1 via webhook_service.send_status_update().
    - MS2's own execution state is stored in the agent_run table.

This service has a single public entry point: run(analysis_id, project_id, payload).
All errors are caught, logged, and result in FAILED webhooks to MS1.
No source parsing, LangGraph, Docker, or Neo4j interaction occurs in the current phase.
"""
import os
import re
import subprocess

from app.models.agent_run_model import (
    create_agent_run,
    update_agent_run_status,
    update_agent_run_metadata,
    mark_agent_run_failed,
)
from app.services import webhook_service
from app.services.workspace_service import create_workspace
from parser.repository_discovery import detect_language_and_framework

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_GITHUB_URL_PATTERN = re.compile(
    r"^https://github\.com/[\w.\-]+/[\w.\-]+(\.git)?$", re.IGNORECASE
)
_GIT_CLONE_TIMEOUT_SECONDS = 300  # 5 minutes max for large repos


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _validate_github_url(url: str) -> None:
    """Raise ValueError if the URL is not a valid public GitHub HTTPS URL."""
    if not _GITHUB_URL_PATTERN.match(url.strip()):
        raise ValueError(
            f"Invalid or unsupported repository URL: '{url}'. "
            "Only public GitHub HTTPS URLs are supported."
        )


def _clone_repository(repo_url: str, target_dir: str) -> None:
    """
    Clone a GitHub repository into target_dir using git.
    Raises subprocess.CalledProcessError on clone failure.
    """
    print(f"[INFO] [Intake] Cloning repository: {repo_url} → {target_dir}")
    result = subprocess.run(
        ["git", "clone", "--depth", "1", repo_url, target_dir],
        capture_output=True,
        text=True,
        timeout=_GIT_CLONE_TIMEOUT_SECONDS,
    )
    if result.returncode != 0:
        raise subprocess.CalledProcessError(
            result.returncode,
            "git clone",
            output=result.stdout,
            stderr=result.stderr,
        )
    print(f"[INFO] [Intake] Clone complete: {target_dir}")


def _validate_repository(repo_path: str) -> None:
    """
    Verify the cloned repository meets basic structural requirements:
    - Directory exists
    - Contains .git metadata
    - Is not empty (beyond .git)
    - Files are readable
    """
    if not os.path.isdir(repo_path):
        raise RuntimeError(f"Repository directory does not exist: {repo_path}")

    git_dir = os.path.join(repo_path, ".git")
    if not os.path.isdir(git_dir):
        raise RuntimeError(f"No .git directory found in cloned repository: {repo_path}")

    entries = [e for e in os.listdir(repo_path) if e != ".git"]
    if not entries:
        raise RuntimeError(f"Repository appears to be empty (only .git found): {repo_path}")

    try:
        os.listdir(repo_path)
    except PermissionError as exc:
        raise RuntimeError(f"Repository files are not readable: {exc}") from exc

    print(f"[INFO] [Intake] Validation passed: {repo_path}")


def _compute_directory_size(path: str) -> int:
    """Return the total size in bytes of all files under the given path."""
    total = 0
    for dirpath, _, filenames in os.walk(path):
        for fname in filenames:
            fpath = os.path.join(dirpath, fname)
            try:
                total += os.path.getsize(fpath)
            except OSError:
                pass
    return total


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run(analysis_id: int, project_id: int, payload: dict) -> None:
    """
    Execute the full repository intake pipeline for the given analysis.

    Parameters
    ----------
    analysis_id:  MS1's Analysis record ID (used in webhooks, not for DB queries)
    project_id:   MS1's Project record ID (stored in AgentRun for reference)
    payload:      Full dispatch payload from MS1 — contains repoUrl, repoName,
                  branch, repositoryType. MS2 uses this instead of querying MS1's DB.

    Runs synchronously (intended to be called inside a FastAPI BackgroundTask).
    All exceptions are caught and result in a FAILED webhook to MS1.
    """
    print(
        f"[INFO] [Intake] Pipeline started — "
        f"analysis_id={analysis_id} project_id={project_id}"
    )

    workspace_path: str | None = None

    try:
        # Step 1 — Create MS2's own AgentRun record
        create_agent_run(analysis_id, project_id)

        # Step 2 — Extract project metadata from the payload (NOT from MS1's DB)
        repo_url: str = payload.get("repoUrl") or ""
        repo_name: str = payload.get("repoName") or _extract_repo_name(repo_url)
        branch: str = payload.get("branch") or "main"

        if not repo_url:
            raise ValueError(
                f"Payload missing repoUrl for analysis_id={analysis_id}"
            )

        # Step 3 — Validate GitHub URL
        _validate_github_url(repo_url)

        # Step 4 — Notify MS1: status → CLONING
        update_agent_run_status(analysis_id, "CLONING")
        webhook_service.send_status_update(analysis_id, "CLONING")
        print(f"[INFO] [Intake] Status → CLONING (analysis_id={analysis_id})")

        # Step 5 — Create workspace
        workspace_path = create_workspace(analysis_id)

        # ----------------------------------------------------------------
        # STAGE: Repository Cloning
        # ----------------------------------------------------------------
        print("[INFO] Repository cloning started...")
        _clone_repository(repo_url, workspace_path)
        print(f"[INFO] [Intake] Repository cloned: {workspace_path}")
        print("[INFO] Repository cloning completed.")

        # Step 6 — Notify MS1: status → VALIDATING
        update_agent_run_status(analysis_id, "VALIDATING")
        webhook_service.send_status_update(analysis_id, "VALIDATING")
        print(f"[INFO] [Intake] Status → VALIDATING (analysis_id={analysis_id})")

        # Step 7 — Validate repository
        _validate_repository(workspace_path)

        # Step 8 — Detect language and framework
        language, framework = detect_language_and_framework(workspace_path)
        print(
            f"[INFO] [Intake] Detected — language={language} framework={framework}"
        )

        # Step 9 — Compute size
        repo_size = _compute_directory_size(workspace_path)
        print(f"[INFO] [Intake] Repository size: {repo_size} bytes")

        # Step 10 — Persist metadata to MS2's own AgentRun table
        update_agent_run_metadata(
            analysis_id,
            repository_path=workspace_path,
            repository_name=repo_name,
            language=language,
            framework=framework,
            repository_size=repo_size,
        )
        print(f"[INFO] [Intake] AgentRun metadata persisted (analysis_id={analysis_id})")

        # Step 11 — Notify MS1: status → READY_FOR_PARSING (with metadata)
        # MS1 will store this metadata in its own Analysis table via the webhook handler.
        update_agent_run_status(analysis_id, "READY_FOR_PARSING")
        webhook_service.send_status_update(
            analysis_id,
            "READY_FOR_PARSING",
            repository_path=workspace_path,
            repository_name=repo_name,
            language=language,
            framework=framework,
            repository_size=repo_size,
        )
        print(
            f"[INFO] [Intake] Status → READY_FOR_PARSING (analysis_id={analysis_id})"
        )

        # ----------------------------------------------------------------
        # STAGE: Repository Parser
        # ----------------------------------------------------------------
        print("[INFO] Repository parser started...")
        print("[INFO] Stage skipped (not implemented yet).")

        # ----------------------------------------------------------------
        # STAGE: Knowledge Graph Construction
        # ----------------------------------------------------------------
        print("[INFO] Knowledge graph construction started...")
        print("[INFO] Stage skipped (not implemented yet).")

        # ----------------------------------------------------------------
        # STAGE: LangGraph Workflow
        # ----------------------------------------------------------------
        print("[INFO] LangGraph workflow started...")
        print("[INFO] Stage skipped (not implemented yet).")

        # ----------------------------------------------------------------
        # STAGE: Report Generation
        # ----------------------------------------------------------------
        print("[INFO] Report generation started...")
        print("[INFO] Stage skipped (not implemented yet).")

        print(
            f"[INFO] [Intake] Pipeline complete — "
            f"analysis_id={analysis_id} language={language} framework={framework}"
        )

    except ValueError as exc:
        print(f"[ERROR] [Intake] Validation error — analysis_id={analysis_id}: {exc}")
        _mark_failed(analysis_id, str(exc))

    except subprocess.CalledProcessError as exc:
        msg = f"git clone failed: returncode={exc.returncode} stderr={exc.stderr}"
        print(f"[ERROR] [Intake] {msg} — analysis_id={analysis_id}")
        _mark_failed(analysis_id, msg)

    except subprocess.TimeoutExpired:
        msg = "git clone timed out"
        print(f"[ERROR] [Intake] {msg} — analysis_id={analysis_id}")
        _mark_failed(analysis_id, msg)

    except RuntimeError as exc:
        print(f"[ERROR] [Intake] Runtime error — analysis_id={analysis_id}: {exc}")
        _mark_failed(analysis_id, str(exc))

    except Exception as exc:
        print(f"[ERROR] [Intake] Unexpected error — analysis_id={analysis_id}: {exc}")
        _mark_failed(analysis_id, str(exc))


def _extract_repo_name(repo_url: str) -> str:
    """Extract the repository name from a GitHub URL."""
    name = repo_url.rstrip("/").split("/")[-1]
    return name.removesuffix(".git")


def _mark_failed(analysis_id: int, error_message: str) -> None:
    """Best-effort: update MS2's AgentRun to FAILED and send webhook to MS1."""
    try:
        mark_agent_run_failed(analysis_id, error_message)
    except Exception as exc:
        print(
            f"[ERROR] [Intake] Could not update AgentRun to FAILED "
            f"for analysis_id={analysis_id}: {exc}"
        )
    # Always attempt the webhook even if the local DB write fails
    webhook_service.send_status_update(
        analysis_id, "FAILED", error_message=error_message
    )
    print(f"[INFO] [Intake] Status → FAILED (analysis_id={analysis_id})")
