from typing import Literal
from pydantic import BaseModel, Field


class AnalysisStartRequest(BaseModel):
    """
    Request payload sent by MS1 when dispatching a job to MS2.

    Includes all project metadata needed by MS2 so that MS2 never has to
    query MS1's database. MS1 gathers this data from its own database before
    dispatching.
    """
    analysisId: int = Field(..., gt=0, description="Internal Analysis record ID from MS1")
    projectId: int = Field(..., gt=0, description="Project ID associated with this analysis")
    userId: int = Field(..., gt=0, description="User ID who triggered the analysis")

    # Project data — MS2 uses these instead of querying MS1's database.
    repoUrl: str = Field(..., description="GitHub repository URL to clone")
    repoName: str = Field(..., description="Human-readable repository name")
    branch: str = Field(default="main", description="Branch to clone")
    repositoryType: Literal["github", "zip"] = Field(
        ..., description="Repository source type"
    )


class AnalysisStartResponse(BaseModel):
    """Acknowledgement response returned by MS2 to MS1."""
    accepted: bool
    message: str
