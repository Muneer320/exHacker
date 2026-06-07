from pydantic import BaseModel, Field


class ProblemAnalysis(BaseModel):
    stakeholders: list[str] = Field(default_factory=list)
    pain_points: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    success_metrics: list[str] = Field(default_factory=list)
    problem_definition: str = ""
