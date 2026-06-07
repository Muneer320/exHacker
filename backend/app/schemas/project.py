from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class ProjectStatus(StrEnum):
    DRAFT = "draft"
    RESEARCHING = "researching"
    IDEA_GENERATION = "idea_generation"
    ARCHITECTURE = "architecture"
    COMPLETED = "completed"


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    challenge_statements: list[str] = Field(..., min_length=1)
    duration_hours: int = Field(default=24, ge=1, le=168)
    team_size: int = Field(default=4, ge=1, le=10)
    experience_level: str = Field(default="intermediate")
    skills: list[str] = Field(default_factory=list)
    tracks: list[str] = Field(default_factory=list)
    datasets: list[str] = Field(default_factory=list)
    apis: list[str] = Field(default_factory=list)
    documentation_links: list[str] = Field(default_factory=list)
    evaluation_criteria: list[str] = Field(default_factory=list)
    notes: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = None
    status: ProjectStatus | None = None
    current_stage: str | None = None
    state: dict[str, object] | None = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    status: ProjectStatus
    current_stage: str
    duration_hours: int
    team_data: dict[str, object] | None = None
    challenge_data: dict[str, object] | None = None
    resource_data: dict[str, object] | None = None
    state: dict[str, object] | None = None
    completed_agents: list[str] = Field(default_factory=list)
    error_log: list[dict[str, str]] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
