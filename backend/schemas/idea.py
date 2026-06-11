from __future__ import annotations

from pydantic import BaseModel, Field


class Idea(BaseModel):
    title: str = ""
    description: str = ""
    problem_solved: str = ""
    target_users: list[str] = Field(default_factory=list)
    core_features: list[str] = Field(default_factory=list)
    innovation_factor: str = ""
    why_it_wins: str = ""
    feasibility_score: int = 5
    innovation_score: int = 5
    hackathon_fit_score: int = 5


class IdeaList(BaseModel):
    ideas: list[Idea] = Field(default_factory=list)
