"""Workflow state definitions using Pydantic."""

from typing import Optional, Literal
from pydantic import BaseModel, Field

from schema.models import (
    CandidateExtractedData,
    ProjectExtractedData,
    AnalysisResult,
    Recommendation,
)


class AgentState(BaseModel):
    """Main state passed through the LangGraph workflow."""

    # Input
    input_text: str = ""
    input_type: Literal["candidate", "project"] = "candidate"
    jd_text: Optional[str] = None  # Optional job description for matching

    # Middle state
    extracted_data: Optional[dict] = None
    analysis_result: Optional[dict] = None

    # Output
    final_output: Optional[dict] = None

    # Metadata
    step_logs: list[str] = Field(default_factory=list)

    def add_log(self, message: str):
        self.step_logs.append(f"[{len(self.step_logs) + 1}] {message}")