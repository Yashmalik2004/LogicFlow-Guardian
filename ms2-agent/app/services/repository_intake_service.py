"""
Repository Intake Service — orchestrates the full intake and parse pipeline.

Pipeline:
    1.  Create AgentRun record in MS2's own database
    2.  Send CLONING webhook to MS1
    3.  Create workspace directory
    4.  Clone the repository via git
    5.  Send VALIDATING webhook to MS1
    6.  Validate the cloned repository (non-empty, .git present, readable)
    7.  Detect language and framework (metadata-only)
    8.  Compute repository size
    9.  Send READY_FOR_PARSING webhook to MS1 (with metadata)
   10.  Update AgentRun in MS2's own database
   11.  Run the Repository Parser Engine
   12.  Save parser IR to workspace/analysis-{id}/parser_output.json
   13.  Send COMPLETED webhook to MS1

Data contract:
    - All project data (repoUrl, repoName, branch, repositoryType) arrives in
      the payload from MS1. MS2 NEVER queries MS1's database.
    - Status updates are sent to MS1 via webhook_service.send_status_update().
    - MS2's own execution state is stored in the agent_run table.

This service has a single public entry point: run(analysis_id, project_id, payload).
All errors are caught, logged, and result in FAILED webhooks to MS1.
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
from parser.engine import RepositoryParserEngine
from graphrag.graph_builder import GraphBuilder

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
    Execute the repository intake and analysis pipeline via LangGraph.

    Parameters
    ----------
    analysis_id:  MS1's Analysis record ID (used in webhooks, not for DB queries)
    project_id:   MS1's Project record ID (stored in AgentRun for reference)
    payload:      Full dispatch payload from MS1 — contains repoUrl, repoName,
                  branch, repositoryType.
    """
    from graphs import run_analysis_workflow

    print(
        f"[INFO] [Intake] Initiating LangGraph analysis workflow — "
        f"analysis_id={analysis_id} project_id={project_id}"
    )
    run_analysis_workflow(analysis_id, project_id, payload)


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
    print(f"[INFO] [Intake] Status -> FAILED (analysis_id={analysis_id})")
