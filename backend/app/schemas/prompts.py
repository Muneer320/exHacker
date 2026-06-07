from pydantic import BaseModel, Field


class PromptPackage(BaseModel):
    frontend_prompts: list[str] = Field(default_factory=list)
    backend_prompts: list[str] = Field(default_factory=list)
    database_prompts: list[str] = Field(default_factory=list)
    ai_prompts: list[str] = Field(default_factory=list)
    testing_prompts: list[str] = Field(default_factory=list)
    deployment_prompts: list[str] = Field(default_factory=list)
