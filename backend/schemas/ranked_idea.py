from pydantic import BaseModel, Field


class RankedIdea(BaseModel):
    title: str = Field(description="Name of the idea")
    final_score: float = Field(description="Weighted total score out of 10")
    innovation_score: int = Field(description="Innovation score 1-10")
    feasibility_score: int = Field(description="Execution feasibility score 1-10")
    hackathon_fit_score: int = Field(description="Hackathon demo impact score 1-10")
    market_potential_score: int = Field(description="Market potential score 1-10")
    technical_wow_factor: int = Field(
        default=5,
        description="Technical wow factor score 1-10: how impressive is the technical implementation?"
    )
    strengths: list[str] = Field(description="List of key strengths")
    weaknesses: list[str] = Field(description="List of key weaknesses")
    why_ranked_here: str = Field(description="Brief justification for this ranking position")


class RankedIdeaList(BaseModel):
    ranked_ideas: list[RankedIdea] = Field(description="All ideas ranked best to worst")