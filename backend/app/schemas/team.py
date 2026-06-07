from enum import StrEnum

from pydantic import BaseModel, Field


class ExperienceLevel(StrEnum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Scope(StrEnum):
    MVP = "mvp"
    ADVANCED_MVP = "advanced_mvp"


class ComplexityBudget(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TeamProfile(BaseModel):
    team_size: int = Field(..., ge=1, le=10)
    experience_level: ExperienceLevel = ExperienceLevel.INTERMEDIATE
    skills: list[str] = Field(default_factory=list)
    complexity_budget: ComplexityBudget = ComplexityBudget.MEDIUM
    recommended_scope: Scope = Scope.MVP
    risk_tolerance: str = "medium"
    execution_capacity_score: float = Field(default=0.0, ge=0.0, le=100.0)
