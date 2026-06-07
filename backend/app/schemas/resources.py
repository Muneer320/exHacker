from pydantic import BaseModel, Field


class ResourceCollection(BaseModel):
    tracks: list[str] = Field(default_factory=list)
    datasets: list[str] = Field(default_factory=list)
    apis: list[str] = Field(default_factory=list)
    documentation_links: list[str] = Field(default_factory=list)
