from pydantic import BaseModel, Field


class OpportunityAnalysis(BaseModel):
    market_gaps: list[str] = Field(default_factory=list)
    innovation_opportunities: list[str] = Field(default_factory=list)
    high_impact_areas: list[str] = Field(default_factory=list)
    technical_opportunities: list[str] = Field(default_factory=list)
