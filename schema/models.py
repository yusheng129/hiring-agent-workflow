"""Pydantic models for the hiring agent workflow."""

from typing import Literal, Optional
from pydantic import BaseModel, Field


class SkillTag(BaseModel):
    """A skill tag with confidence."""
    name: str
    confidence: float = Field(ge=0.0, le=1.0)


class CandidateExtractedData(BaseModel):
    """Extracted data for candidate input."""
    name: Optional[str] = None
    age: Optional[int] = None
    education: Optional[str] = None
    work_years: Optional[int] = None
    current_company: Optional[str] = None
    current_title: Optional[str] = None
    skills: list[SkillTag] = Field(default_factory=list)
    project_experience: list[str] = Field(default_factory=list)
    expected_salary: Optional[str] = None
    raw_text: str


class ProjectExtractedData(BaseModel):
    """Extracted data for project input."""
    project_name: str
    industry: Optional[str] = None
    tech_stack: list[str] = Field(default_factory=list)
    core_metrics: list[str] = Field(default_factory=list)
    risk_points: list[str] = Field(default_factory=list)
    delivery_time: Optional[str] = None
    team_size: Optional[int] = None
    raw_text: str


class AnalysisResult(BaseModel):
    """Analysis result with tags, match score, and risk points."""
    tags: list[str] = Field(default_factory=list)
    match_score: int = Field(ge=0, le=100)
    score_reason: str = ""
    risk_points: list[dict] = Field(default_factory=list)  # {"point": str, "severity": str}
    input_type: Literal["candidate", "project"] = "candidate"


class Recommendation(BaseModel):
    """Recommendation with next action and follow-up questions."""
    next_action: str = ""
    next_action_reason: str = ""
    follow_up_questions: list[str] = Field(default_factory=list)
    suggested_tags: list[str] = Field(default_factory=list)


class FinalOutput(BaseModel):
    """Final output combining all stages."""
    extracted_data: dict
    analysis: dict
    recommendation: dict
    input_type: Literal["candidate", "project"]