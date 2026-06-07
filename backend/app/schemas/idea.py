from pydantic import BaseModel, Field


class Competitor(BaseModel):
    name: str
    description: str
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)


class OpenSourceProject(BaseModel):
    name: str
    description: str
    url: str = ""


class ApiResource(BaseModel):
    name: str
    description: str
    url: str = ""


class ValidationReport(BaseModel):
    idea_id: str
    competitors: list[Competitor] = Field(default_factory=list)
    open_source_projects: list[OpenSourceProject] = Field(default_factory=list)
    available_apis: list[ApiResource] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    final_score: float = Field(default=0.0, ge=0.0, le=100.0)


class Idea(BaseModel):
    id: str
    title: str
    description: str
    target_users: list[str] = Field(default_factory=list)
    key_features: list[str] = Field(default_factory=list)
    innovation_score: float = Field(default=0.0, ge=0.0, le=100.0)
    feasibility_score: float = Field(default=0.0, ge=0.0, le=100.0)
    hackathon_fit_score: float = Field(default=0.0, ge=0.0, le=100.0)
    technical_wow_score: float = Field(default=0.0, ge=0.0, le=100.0)
    final_score: float = Field(default=0.0, ge=0.0, le=100.0)
