from pydantic import BaseModel, Field


class ArchitectureDiagram(BaseModel):
    description: str = ""
    components: list[dict[str, object]] = Field(default_factory=list)
    connections: list[dict[str, object]] = Field(default_factory=list)


class Feature(BaseModel):
    title: str
    description: str
    priority: str = "medium"


class UserStory(BaseModel):
    actor: str
    goal: str
    benefit: str


class ApiDefinition(BaseModel):
    path: str
    method: str = "GET"
    description: str = ""
    request_body: dict[str, object] | None = None
    response_body: dict[str, object] | None = None


class DatabaseSchema(BaseModel):
    tables: list[dict[str, object]] = Field(default_factory=list)
    relationships: list[dict[str, object]] = Field(default_factory=list)


class Integration(BaseModel):
    name: str
    description: str
    type: str = "api"


class ArchitecturePackage(BaseModel):
    vision: str = ""
    product_scope: str = ""
    features: list[Feature] = Field(default_factory=list)
    user_stories: list[UserStory] = Field(default_factory=list)
    architecture: ArchitectureDiagram = Field(default_factory=ArchitectureDiagram)
    api_design: list[ApiDefinition] = Field(default_factory=list)
    database_schema: DatabaseSchema = Field(default_factory=DatabaseSchema)
    integrations: list[Integration] = Field(default_factory=list)
