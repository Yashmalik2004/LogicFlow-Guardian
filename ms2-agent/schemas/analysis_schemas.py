from pydantic import BaseModel, Field


class AnalysisStartRequest(BaseModel):
    """Request payload sent by MS1 when dispatching a job to MS2."""
    analysisId: int = Field(..., gt=0, description="Internal Analysis record ID from MS1")
    projectId: int = Field(..., gt=0, description="Project ID associated with this analysis")
    userId: int = Field(..., gt=0, description="User ID who triggered the analysis")


class AnalysisStartResponse(BaseModel):
    """Acknowledgement response returned by MS2 to MS1."""
    accepted: bool
    message: str
