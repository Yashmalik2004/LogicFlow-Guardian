"""
LangGraph State — defines the schema and Pydantic validation models
for the orchestration workflow state.
"""
from typing import TypedDict, List, Dict, Any
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# LangGraph State (TypedDict)
# ---------------------------------------------------------------------------

class AnalysisState(TypedDict, total=False):
    """
    Standard LangGraph State object representing the execution context.
    """
    analysis_id: int
    project_id: int
    payload: Dict[str, Any]
    repository_path: str
    repository_name: str
    language: str
    framework: str
    status: str
    errors: List[str]
    metadata: Dict[str, Any]


# ---------------------------------------------------------------------------
# State Models (Pydantic validation schema)
# ---------------------------------------------------------------------------

class AnalysisStateModel(BaseModel):
    """
    Pydantic schema used for input/output verification of the orchestration state.
    """
    analysis_id: int = Field(..., description="Unique database identifier for the run")
    project_id: int = Field(..., description="Project identifier from MS1")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Original request parameters")
    repository_path: str = Field("", description="Local cloned repository path")
    repository_name: str = Field("", description="Target repository name")
    language: str = Field("", description="Primary programming language detected")
    framework: str = Field("", description="Detected web framework")
    status: str = Field("PENDING", description="Current analysis status")
    errors: List[str] = Field(default_factory=list, description="Collection of execution error logs")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Inter-node communication metadata")
