from pydantic import BaseModel, Field


class ChallengeIntelligence(BaseModel):
    themes: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    resource_opportunities: list[str] = Field(default_factory=list)
    evaluation_focus: list[str] = Field(default_factory=list)
