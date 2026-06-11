from __future__ import annotations

from pydantic import BaseModel, Field


class OpportunityAnalysis(BaseModel):
    market_gaps: list[str] = Field(default_factory=list)
    underserved_users: list[str] = Field(default_factory=list)
    high_impact_opportunities: list[str] = Field(default_factory=list)
    technical_opportunities: list[str] = Field(default_factory=list)
    innovation_opportunities: list[str] = Field(default_factory=list)
    ai_opportunities: list[str] = Field(default_factory=list)
    unique_hackathon_angles: list[str] = Field(default_factory=list)
    monetization_opportunities: list[str] = Field(default_factory=list)
