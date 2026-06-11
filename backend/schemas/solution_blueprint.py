from pydantic import BaseModel

class BackendComponent(BaseModel):
    endpoint: str
    method: str
    description: str
    live_logic: bool

class ProductVision(BaseModel):
    name: str
    description: str
    elevator_pitch: str
    problem_solved: str
    why_this_wins: str

class SolutionBlueprint(BaseModel):
    product_vision: ProductVision
    target_users: list[str]
    core_features: list[str]
    user_flow: list[str]
    architecture_overview: str
    frontend_components: list[str]
    backend_components: list[BackendComponent]
    database_schema: list[str]
    ai_components: list[str]
    integrations: list[str]
    mvp_scope: list[str]
    future_scope: list[str]
    implementation_steps: list[str]