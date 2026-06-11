from pydantic import BaseModel


class OpportunityAnalysis(BaseModel):

    market_gaps: list[str]

    underserved_users: list[str]

    high_impact_opportunities: list[str]

    technical_opportunities: list[str]

    innovation_opportunities: list[str]

    ai_opportunities: list[str]

    unique_hackathon_angles: list[str]

    monetization_opportunities: list[str]