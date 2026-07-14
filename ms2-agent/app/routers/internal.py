from fastapi import APIRouter

from schemas.analysis_schemas import AnalysisStartRequest, AnalysisStartResponse

internal_router = APIRouter(prefix="/internal")


@internal_router.post("/analysis/start", response_model=AnalysisStartResponse)
def start_analysis(payload: AnalysisStartRequest):
    """
    Internal endpoint: MS1 dispatches an analysis job here.
    MS2 validates the payload and acknowledges receipt.
    No analysis is performed at this stage.
    """
    print(
        f"[INFO] [Internal] Analysis job received — "
        f"analysisId={payload.analysisId} "
        f"projectId={payload.projectId} "
        f"userId={payload.userId}"
    )

    return AnalysisStartResponse(
        accepted=True,
        message="Analysis job received."
    )
