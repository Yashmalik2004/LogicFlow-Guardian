"""
Workspace service — manages per-analysis clone directories.

Each analysis gets an isolated directory under WORKSPACE_ROOT:
    workspace/
    └── analysis-{analysisId}/
"""
import os

from app.config.env import env


def _root() -> str:
    """Resolve and return the absolute workspace root path."""
    return os.path.abspath(env.WORKSPACE_ROOT)


def get_workspace_path(analysis_id: int) -> str:
    """Return the absolute path for a given analysis workspace."""
    return os.path.join(_root(), f"analysis-{analysis_id}")


def workspace_exists(analysis_id: int) -> bool:
    """Return True if the workspace directory already exists."""
    return os.path.isdir(get_workspace_path(analysis_id))


def create_workspace(analysis_id: int) -> str:
    """
    Create an isolated workspace directory for the given analysis.

    Returns the absolute path to the created directory.
    Raises RuntimeError if the directory already exists (analyses must not share workspaces).
    Raises OSError if directory creation fails.
    """
    path = get_workspace_path(analysis_id)

    if os.path.exists(path):
        raise RuntimeError(
            f"Workspace already exists for analysis_id={analysis_id}: {path}"
        )

    os.makedirs(path, exist_ok=False)
    print(f"[INFO] [Workspace] Created workspace: {path}")
    return path
