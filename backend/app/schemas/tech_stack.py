from pydantic import BaseModel, Field


class TechStack(BaseModel):
    frontend: str = ""
    backend: str = ""
    database: str = ""
    hosting: str = ""
    ai_models: list[str] = Field(default_factory=list)
    vector_db: str | None = None
    auth_provider: str | None = None
