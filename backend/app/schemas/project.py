from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, field_validator


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
    current_agent: str | None = None
    duration_hours: int
    team_data: dict[str, object] | None = None
    challenge_data: dict[str, object] | None = None
    resource_data: dict[str, object] | None = None
    state: dict[str, object] | None = None
    completed_agents: list[str] = Field(default_factory=list)
    agent_logs: list[dict[str, object]] = Field(default_factory=list)
    error_log: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    @field_validator("completed_agents", "agent_logs", "error_log", mode="before")
    @classmethod
    def none_to_empty_list(cls, v: list[Any] | None) -> list[Any]:
        return v if v is not None else []

    model_config = {"from_attributes": True}
