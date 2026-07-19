"""
Graph Invocation — entry point to execute the compiled LangGraph orchestration.
"""
from typing import Dict, Any
from app.models.agent_run_model import update_agent_run_status
from app.services import webhook_service
from app.services.repository_intake_service import _mark_failed

from graphs.builder import build_analysis_graph
from graphs.state import AnalysisState


def run_analysis_workflow(analysis_id: int, project_id: int, payload: dict) -> Dict[str, Any]:
    """
    Instantiates and executes the compiled LangGraph workflow.

    Catches any run failures, logs them, updates database states, and issues
    webhook notifications.
    """
    print(f"[INFO] [GraphInvocation] Instantiating LangGraph for analysis_id={analysis_id}")
    compiled_graph = build_analysis_graph()

    # Define initial state configuration
    initial_state: AnalysisState = {
        "analysis_id": analysis_id,
        "project_id": project_id,
        "payload": payload,
        "errors": [],
        "metadata": {},
        "status": "STARTING",
    }

    try:
        # Execute workflow
        final_state = compiled_graph.invoke(initial_state)

        # Process outcome
        status = final_state.get("status")
        errors = final_state.get("errors") or []

        if status == "FAILED" or errors:
            err_msg = errors[-1] if errors else "Unknown pipeline error."
            _mark_failed(analysis_id, err_msg)
            return final_state

        # Mark COMPLETED in DB and webhook to MS1
        update_agent_run_status(analysis_id, "COMPLETED")
        webhook_service.send_status_update(analysis_id, "COMPLETED")
        print(f"[INFO] [GraphInvocation] Workflow finished successfully for analysis_id={analysis_id}")

        return final_state

    except Exception as exc:
        err_msg = str(exc)
        print(f"[ERROR] [GraphInvocation] Exception during workflow execution: {err_msg}")
        _mark_failed(analysis_id, err_msg)
        return {
            "status": "FAILED",
            "errors": [err_msg]
        }
