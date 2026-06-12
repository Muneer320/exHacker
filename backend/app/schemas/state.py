from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class WorkflowStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    WAITING_FOR_USER = "waiting_for_user"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkflowStage(str, Enum):
    CHALLENGE_INTELLIGENCE = "challenge_intelligence"
    PROBLEM_ANALYSIS = "problem_analysis"
    OPPORTUNITY_DISCOVERY = "opportunity_discovery"
    IDEA_GENERATION = "idea_generation"
    IDEA_VALIDATION = "idea_validation"
    HUMAN_SELECTION = "human_selection"
    TECH_STACK = "tech_stack"
    ARCHITECTURE = "architecture"
    BUILD_ACCELERATOR = "build_accelerator"
    PRESENTATION = "presentation"
    PITCH = "pitch"
    EXPORT = "export"


class WorkflowMetadata(BaseModel):
    workflow_id: str
    project_id: str
    status: WorkflowStatus
    current_stage: WorkflowStage
    created_at: str
    updated_at: str


class Resource(BaseModel):
    name: str
    url: str
    type: Optional[str] = None


class TeamProfile(BaseModel):
    team_size: int
    experience_level: str
    known_technologies: List[str] = Field(default_factory=list)
    preferred_technologies: List[str] = Field(default_factory=list)


class Project(BaseModel):
    id: str
    name: str
    challenge_statements: List[str]
    duration_hours: int
    resources: List[Resource] = Field(default_factory=list)
    created_at: str


class ChallengeIntelligence(BaseModel):
    themes: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    opportunities: List[str] = Field(default_factory=list)
    evaluation_factors: List[str] = Field(default_factory=list)
    technical_opportunities: List[str] = Field(default_factory=list)


class ProblemAnalysis(BaseModel):
    stakeholders: List[str] = Field(default_factory=list)
    pain_points: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    success_metrics: List[str] = Field(default_factory=list)
    refined_problem_statement: str


class OpportunityAnalysis(BaseModel):
    market_gaps: List[str] = Field(default_factory=list)
    innovation_opportunities: List[str] = Field(default_factory=list)
    technical_opportunities: List[str] = Field(default_factory=list)
    impact_opportunities: List[str] = Field(default_factory=list)


class Idea(BaseModel):
    id: str
    title: str
    description: str
    target_users: List[str] = Field(default_factory=list)
    key_features: List[str] = Field(default_factory=list)
    innovation_score: float


class Competitor(BaseModel):
    name: str
    description: str
    url: Optional[str] = None


class OpenSourceProject(BaseModel):
    name: str
    description: str
    url: Optional[str] = None
    stars: Optional[int] = None


class ApiResource(BaseModel):
    name: str
    description: str
    url: Optional[str] = None


class ValidationReport(BaseModel):
    idea_id: str
    competitors: List[Competitor] = Field(default_factory=list)
    open_source_projects: List[OpenSourceProject] = Field(default_factory=list)
    apis: List[ApiResource] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    feasibility_score: float
    innovation_score: float
    final_score: float


class TechStack(BaseModel):
    frontend: str
    backend: str
    database: str
    ai_stack: List[str] = Field(default_factory=list)
    deployment: List[str] = Field(default_factory=list)
    reasoning: List[str] = Field(default_factory=list)


class Component(BaseModel):
    name: str
    description: str
    responsibilities: List[str] = Field(default_factory=list)


class Module(BaseModel):
    name: str
    description: str
    dependencies: List[str] = Field(default_factory=list)


class ApiDefinition(BaseModel):
    endpoint: str
    method: str
    description: str
    request_body: Optional[Dict[str, Any]] = None
    response_body: Optional[Dict[str, Any]] = None


class DatabaseDesign(BaseModel):
    tables: List[Dict[str, Any]] = Field(default_factory=list)
    relationships: List[str] = Field(default_factory=list)


class Integration(BaseModel):
    service_name: str
    purpose: str
    type: str


class ArchitecturePackage(BaseModel):
    system_design: str
    mermaid_diagram: Optional[str] = None
    components: List[Component] = Field(default_factory=list)
    modules: List[Module] = Field(default_factory=list)
    api_design: List[ApiDefinition] = Field(default_factory=list)
    database_design: DatabaseDesign
    integrations: List[Integration] = Field(default_factory=list)
    mvp_scope: List[str] = Field(default_factory=list)
    future_scope: List[str] = Field(default_factory=list)


class BuildPackage(BaseModel):
    frontend_tasks: List[str] = Field(default_factory=list)
    backend_tasks: List[str] = Field(default_factory=list)
    database_tasks: List[str] = Field(default_factory=list)
    testing_tasks: List[str] = Field(default_factory=list)
    deployment_tasks: List[str] = Field(default_factory=list)


class PromptPackage(BaseModel):
    frontend_prompts: List[str] = Field(default_factory=list)
    backend_prompts: List[str] = Field(default_factory=list)
    database_prompts: List[str] = Field(default_factory=list)
    testing_prompts: List[str] = Field(default_factory=list)
    deployment_prompts: List[str] = Field(default_factory=list)


class Slide(BaseModel):
    title: str
    content: List[str] = Field(default_factory=list)
    visual_notes: Optional[str] = None


class PresentationPackage(BaseModel):
    slide_order: List[str] = Field(default_factory=list)
    slide_content: List[Slide] = Field(default_factory=list)
    demo_story: str
    business_story: str


class QA(BaseModel):
    question: str
    answer: str


class PitchPackage(BaseModel):
    pitch_30s: str
    pitch_2m: str
    pitch_5m: str
    judge_questions: List[QA] = Field(default_factory=list)
    demo_script: str


class ExportPackage(BaseModel):
    readme: str
    architecture_doc: str
    presentation_doc: str
    pitch_doc: str
    implementation_guide: str


class WorkflowError(BaseModel):
    stage: str
    timestamp: str
    message: str
    retry_count: int


class ProviderUsage(BaseModel):
    provider: str
    tokens: int
    cost: float


class StageMetric(BaseModel):
    stage: str
    duration_seconds: float
    tokens: int
    cost: float


class ExecutionMetadata(BaseModel):
    total_duration_seconds: float = 0.0
    total_tokens: int = 0
    total_cost: float = 0.0
    provider_usage: List[ProviderUsage] = Field(default_factory=list)
    stage_metrics: List[StageMetric] = Field(default_factory=list)


class ExHackerStateSchema(BaseModel):
    metadata: WorkflowMetadata
    project: Project
    team_profile: Optional[TeamProfile] = None
    challenge_intelligence: Optional[ChallengeIntelligence] = None
    problem_analysis: Optional[ProblemAnalysis] = None
    opportunity_analysis: Optional[OpportunityAnalysis] = None
    generated_ideas: Optional[List[Idea]] = None
    validation_reports: Optional[List[ValidationReport]] = None
    selected_idea: Optional[Idea] = None
    tech_stack: Optional[TechStack] = None
    architecture: Optional[ArchitecturePackage] = None
    build_package: Optional[BuildPackage] = None
    prompt_package: Optional[PromptPackage] = None
    presentation: Optional[PresentationPackage] = None
    pitch: Optional[PitchPackage] = None
    exports: Optional[ExportPackage] = None
    execution: Optional[ExecutionMetadata] = Field(default_factory=ExecutionMetadata)
    errors: List[WorkflowError] = Field(default_factory=list)
