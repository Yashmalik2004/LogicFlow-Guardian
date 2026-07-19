from fastapi import APIRouter, BackgroundTasks

from schemas.analysis_schemas import AnalysisStartRequest, AnalysisStartResponse
from app.services import repository_intake_service

internal_router = APIRouter(prefix="/internal")


@internal_router.post("/analysis/start", response_model=AnalysisStartResponse)
def start_analysis(payload: AnalysisStartRequest, background_tasks: BackgroundTasks):
    """
    Internal endpoint: MS1 dispatches an analysis job here.
    MS2 validates the payload, acknowledges receipt immediately, then
    runs the repository intake pipeline in the background so that
    MS1 is never kept waiting.
    """
    print("============================================================")
    print("MS2 REQUEST RECEIVED")
    print(f"Analysis ID : {payload.analysisId}")
    print(f"Project ID  : {payload.projectId}")
    print(f"User ID     : {payload.userId}")
    print(f"Repo URL    : {payload.repoUrl}")
    print("============================================================")

    background_tasks.add_task(
        repository_intake_service.run,
        payload.analysisId,
        payload.projectId,
        payload.model_dump(),
    )

    print(f"[INFO] Sending ACK back to MS1.")

    return AnalysisStartResponse(
        accepted=True,
        message="Analysis job received. Repository intake started.",
    )

