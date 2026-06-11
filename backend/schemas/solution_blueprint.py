from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class BackendComponent(BaseModel):
    endpoint: str = ""
    method: str = "GET"
    description: str = ""
    live_logic: bool = False


class ProductVision(BaseModel):
    name: str = ""
    description: str = ""
    elevator_pitch: str = ""
    problem_solved: str = ""
    why_this_wins: str = ""


class SolutionBlueprint(BaseModel):
    product_vision: dict[str, Any] = Field(default_factory=dict)
    target_users: list[str] = Field(default_factory=list)
    core_features: list[str] = Field(default_factory=list)
    user_flow: list[str] = Field(default_factory=list)
    architecture_overview: str = ""
    frontend_components: list[str] = Field(default_factory=list)
    backend_components: list[BackendComponent] = Field(default_factory=list)
    database_schema: list[str] = Field(default_factory=list)
    ai_components: list[str] = Field(default_factory=list)
    integrations: list[str] = Field(default_factory=list)
    mvp_scope: list[str] = Field(default_factory=list)
    future_scope: list[str] = Field(default_factory=list)
    implementation_steps: list[str] = Field(default_factory=list)
