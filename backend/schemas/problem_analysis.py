from __future__ import annotations

from pydantic import BaseModel, Field


class ProblemAnalysis(BaseModel):
    problem_statement: str = ""
    pain_points: list[str] = Field(default_factory=list)
    stakeholders: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    success_metrics: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    ai_opportunities: list[str] = Field(default_factory=list)
    unique_hackathon_angles: list[str] = Field(default_factory=list)
    suggested_features: list[str] = Field(default_factory=list)
    technical_challenges: list[str] = Field(default_factory=list)
    judging_criteria_alignment: list[str] = Field(default_factory=list)
