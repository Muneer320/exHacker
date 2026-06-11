from __future__ import annotations

from pydantic import BaseModel, Field


class RankedIdea(BaseModel):
    title: str = ""
    final_score: float = 0.0
    innovation_score: int = 5
    feasibility_score: int = 5
    hackathon_fit_score: int = 5
    market_potential_score: int = 5
    technical_wow_factor: int = Field(default=5)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    why_ranked_here: str = ""


class RankedIdeaList(BaseModel):
    ranked_ideas: list[RankedIdea] = Field(default_factory=list)
