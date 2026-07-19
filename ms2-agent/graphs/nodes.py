"""
Graph Nodes — Node implementations for the LangGraph orchestration layer.

Contains nodes for Repository Intake, Parsing, Knowledge Graph Building,
and placeholder nodes for future stages (Planning, Execution, Reflection, Report).
"""
import os
import subprocess
from typing import Dict, Any

from app.models.agent_run_model import (
    create_agent_run,
    update_agent_run_status,
    update_agent_run_metadata,
)
from app.services import webhook_service
from app.services.workspace_service import create_workspace, workspace_exists, get_workspace_path
from parser.repository_discovery import detect_language_and_framework
from parser.engine import RepositoryParserEngine
from graphrag.graph_builder import GraphBuilder

from graphs.state import AnalysisState


# ---------------------------------------------------------------------------
# Reusing Intake Helpers
# ---------------------------------------------------------------------------

from app.services.repository_intake_service import (
    _validate_github_url,
    _clone_repository,
    _validate_repository,
    _compute_directory_size,
    _extract_repo_name,
)


# ---------------------------------------------------------------------------
# Repository Intake Node
# ---------------------------------------------------------------------------

def RepositoryIntakeNode(state: AnalysisState) -> Dict[str, Any]:
    """
    Step 1: Repository Intake Node.
    Creates workspace, clones target repository, validates files, detects
    metadata, and notifies MS1.
    """
    analysis_id = state.get("analysis_id")
    project_id = state.get("project_id")
    payload = state.get("payload") or {}

    print(f"[INFO] [RepositoryIntakeNode] Starting intake for analysis_id={analysis_id}")

    try:
        # Create MS2 AgentRun db record
        create_agent_run(analysis_id, project_id)

        repo_url = payload.get("repoUrl") or ""
        repo_name = payload.get("repoName") or _extract_repo_name(repo_url)
        branch = payload.get("branch") or "main"

        if not repo_url:
            raise ValueError(f"Payload missing repoUrl for analysis_id={analysis_id}")

        _validate_github_url(repo_url)

        # Update status to CLONING
        update_agent_run_status(analysis_id, "CLONING")
        webhook_service.send_status_update(analysis_id, "CLONING")

        # Create workspace or use existing if it's already there (useful for testing)
        if workspace_exists(analysis_id):
            workspace_path = get_workspace_path(analysis_id)
            print(f"[INFO] [RepositoryIntakeNode] Reusing existing workspace: {workspace_path}")
        else:
            workspace_path = create_workspace(analysis_id)
            _clone_repository(repo_url, workspace_path)

        # Update status to VALIDATING
        update_agent_run_status(analysis_id, "VALIDATING")
        webhook_service.send_status_update(analysis_id, "VALIDATING")

        # Validate repository contents
        _validate_repository(workspace_path)

        # Detect language and framework
        language, framework = detect_language_and_framework(workspace_path)
        repo_size = _compute_directory_size(workspace_path)

        # Persist discovered metadata
        update_agent_run_metadata(
            analysis_id,
            repository_path=workspace_path,
            repository_name=repo_name,
            language=language,
            framework=framework,
            repository_size=repo_size,
        )

        # Transition to READY_FOR_PARSING
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

        return {
            "repository_path": workspace_path,
            "repository_name": repo_name,
            "language": language,
            "framework": framework,
            "status": "READY_FOR_PARSING",
        }

    except Exception as exc:
        print(f"[ERROR] [RepositoryIntakeNode] Intake failed: {exc}")
        return {
            "status": "FAILED",
            "errors": [str(exc)],
        }


# ---------------------------------------------------------------------------
# Repository Parser Node
# ---------------------------------------------------------------------------

def RepositoryParserNode(state: AnalysisState) -> Dict[str, Any]:
    """
    Step 2: Repository Parser Node.
    Scans source code files and generates normalized parser_output.json.
    """
    analysis_id = state.get("analysis_id")
    workspace_path = state.get("repository_path")
    status = state.get("status")

    if status == "FAILED":
        print(f"[INFO] [RepositoryParserNode] Skipping parse due to upstream FAILED status.")
        return {"status": "FAILED"}

    print(f"[INFO] [RepositoryParserNode] Starting repository parsing for analysis_id={analysis_id}")

    try:
        ir_output_path = os.path.join(workspace_path, "parser_output.json")
        engine = RepositoryParserEngine(
            analysis_id=analysis_id,
            repository_path=workspace_path,
        )
        ir = engine.run()
        engine.save(ir, ir_output_path)

        return {
            "status": "PARSED",
            "metadata": {
                **state.get("metadata", {}),
                "parser_supported_files": ir.supported_files,
            }
        }
    except Exception as exc:
        print(f"[ERROR] [RepositoryParserNode] Parsing failed: {exc}")
        return {
            "status": "FAILED",
            "errors": state.get("errors", []) + [str(exc)],
        }


# ---------------------------------------------------------------------------
# Knowledge Graph Node
# ---------------------------------------------------------------------------

def KnowledgeGraphNode(state: AnalysisState) -> Dict[str, Any]:
    """
    Step 3: Knowledge Graph Builder Node.
    Loads parsed AST entities and relationships into Neo4j graph database.
    """
    analysis_id = state.get("analysis_id")
    workspace_path = state.get("repository_path")
    repo_name = state.get("repository_name")
    status = state.get("status")

    if status == "FAILED":
        print(f"[INFO] [KnowledgeGraphNode] Skipping graph ingestion due to upstream FAILED status.")
        return {"status": "FAILED"}

    print(f"[INFO] [KnowledgeGraphNode] Starting graph build for analysis_id={analysis_id}")

    try:
        # Load parser output directly from file without reparsing
        ir_output_path = os.path.join(workspace_path, "parser_output.json")
        ir = RepositoryParserEngine.load_from_file(ir_output_path)

        # Build graph
        builder = GraphBuilder()
        report = builder.build_graph(ir, repo_name)

        if not report.get("success"):
            raise ValueError("Neo4j Repository root node validation failed.")

        return {
            "status": "GRAPH_BUILT",
            "metadata": {
                **state.get("metadata", {}),
                "graph_nodes": report.get("total_nodes"),
                "graph_relationships": report.get("total_relationships"),
            }
        }
    except Exception as exc:
        print(f"[ERROR] [KnowledgeGraphNode] Graph building failed: {exc}")
        return {
            "status": "FAILED",
            "errors": state.get("errors", []) + [str(exc)],
        }


# ---------------------------------------------------------------------------
# Future Placeholder Nodes (Simply pass state through)
# ---------------------------------------------------------------------------

def PlannerNode(state: AnalysisState) -> Dict[str, Any]:
    """Placeholder Node for future vulnerability/remediation planning."""
    print("[INFO] [PlannerNode] Running placeholder step (pass-through).")
    return {
        "status": "PLANNING_COMPLETED",
        "metadata": {
            **state.get("metadata", {}),
            "planner_placeholder": True
        }
    }


def ExecutionNode(state: AnalysisState) -> Dict[str, Any]:
    """Placeholder Node for future automated tool execution."""
    print("[INFO] [ExecutionNode] Running placeholder step (pass-through).")
    return {
        "status": "EXECUTION_COMPLETED",
        "metadata": {
            **state.get("metadata", {}),
            "execution_placeholder": True
        }
    }


def ReflectionNode(state: AnalysisState) -> Dict[str, Any]:
    """Placeholder Node for future result validation and reflection."""
    print("[INFO] [ReflectionNode] Running placeholder step (pass-through).")
    return {
        "status": "REFLECTION_COMPLETED",
        "metadata": {
            **state.get("metadata", {}),
            "reflection_placeholder": True
        }
    }


def ReportNode(state: AnalysisState) -> Dict[str, Any]:
    """Placeholder Node for future Markdown/PDF report generation."""
    print("[INFO] [ReportNode] Running placeholder step (pass-through).")
    return {
        "status": "REPORTS_GENERATED",
        "metadata": {
            **state.get("metadata", {}),
            "report_placeholder": True
        }
    }


# Conventions Naming Aliases
RepositoryParserNode = RepositoryParserNode
ExecutorNode = ExecutionNode
ReportGeneratorNode = ReportNode
