from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()  # noqa: UP017


class WorkflowMetadata(BaseModel):
    workflow_id: str = Field(default_factory=lambda: str(uuid4()))
    project_id: str = ""
    status: str = "created"
    current_stage: str = "challenge_intelligence"
    created_at: str = Field(default_factory=_now)
    updated_at: str = Field(default_factory=_now)


class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = ""
    challenge_statements: list[str] = Field(default_factory=list)
    duration_hours: int = 48
    resources: list[dict[str, Any]] | None = None
    created_at: str = Field(default_factory=_now)


class TeamProfile(BaseModel):
    team_size: int = 4
    experience_level: str = "intermediate"
    known_technologies: list[str] = Field(default_factory=list)
    preferred_technologies: list[str] = Field(default_factory=list)


class ChallengeIntelligence(BaseModel):
    themes: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    evaluation_factors: list[str] = Field(default_factory=list)
    technical_opportunities: list[str] = Field(default_factory=list)


class ProblemAnalysis(BaseModel):
    stakeholders: list[str] = Field(default_factory=list)
    pain_points: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    success_metrics: list[str] = Field(default_factory=list)
    refined_problem_statement: str = ""


class OpportunityAnalysis(BaseModel):
    market_gaps: list[str] = Field(default_factory=list)
    innovation_opportunities: list[str] = Field(default_factory=list)
    technical_opportunities: list[str] = Field(default_factory=list)
    impact_opportunities: list[str] = Field(default_factory=list)


class Idea(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = ""
    description: str = ""
    target_users: list[str] = Field(default_factory=list)
    key_features: list[str] = Field(default_factory=list)
    innovation_score: int = 5


class Competitor(BaseModel):
    name: str = ""
    description: str = ""
    website: str = ""
    similarity_score: float = 0.0


class OpenSourceProject(BaseModel):
    name: str = ""
    stars: int = 0
    license: str = ""
    relevance_score: float = 0.0


class ApiResource(BaseModel):
    name: str = ""
    provider: str = ""
    description: str = ""
    pricing: str = ""
    integration_effort: str = "medium"


class ValidationReport(BaseModel):
    idea_id: str = ""
    competitors: list[Competitor] = Field(default_factory=list)
    open_source_projects: list[OpenSourceProject] = Field(default_factory=list)
    apis: list[ApiResource] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    feasibility_score: int = 5
    innovation_score: int = 5
    final_score: float = 5.0


class TechStack(BaseModel):
    frontend: str = ""
    backend: str = ""
    database: str = ""
    ai_stack: list[str] = Field(default_factory=list)
    deployment: list[str] = Field(default_factory=list)
    reasoning: list[str] = Field(default_factory=list)


class Component(BaseModel):
    name: str = ""
    description: str = ""
    technology: str = ""


class Module(BaseModel):
    name: str = ""
    purpose: str = ""


class ApiDefinition(BaseModel):
    endpoint: str = ""
    method: str = "GET"
    description: str = ""


class DatabaseDesign(BaseModel):
    tables: list[dict[str, Any]] = Field(default_factory=list)


class Integration(BaseModel):
    name: str = ""
    purpose: str = ""


class ArchitecturePackage(BaseModel):
    system_design: str = ""
    components: list[Component] = Field(default_factory=list)
    modules: list[Module] = Field(default_factory=list)
    api_design: list[ApiDefinition] = Field(default_factory=list)
    database_design: DatabaseDesign | None = None
    integrations: list[Integration] = Field(default_factory=list)
    mvp_scope: list[str] = Field(default_factory=list)
    future_scope: list[str] = Field(default_factory=list)


class BuildPackage(BaseModel):
    frontend_tasks: list[str] = Field(default_factory=list)
    backend_tasks: list[str] = Field(default_factory=list)
    database_tasks: list[str] = Field(default_factory=list)
    testing_tasks: list[str] = Field(default_factory=list)
    deployment_tasks: list[str] = Field(default_factory=list)


class PromptPackage(BaseModel):
    frontend_prompts: list[str] = Field(default_factory=list)
    backend_prompts: list[str] = Field(default_factory=list)
    database_prompts: list[str] = Field(default_factory=list)
    testing_prompts: list[str] = Field(default_factory=list)
    deployment_prompts: list[str] = Field(default_factory=list)


class Slide(BaseModel):
    slide_number: int = 0
    title: str = ""
    objective: str = ""
    content: list[str] = Field(default_factory=list)
    speaker_notes: str = ""
    visual_suggestion: str = ""


class PresentationPackage(BaseModel):
    slide_order: list[str] = Field(default_factory=list)
    slide_content: list[Slide] = Field(default_factory=list)
    demo_story: str = ""
    business_story: str = ""


class QA(BaseModel):
    question: str = ""
    answer: str = ""


class PitchPackage(BaseModel):
    pitch_30s: str = ""
    pitch_2m: str = ""
    pitch_5m: str = ""
    judge_questions: list[QA] = Field(default_factory=list)
    demo_script: str = ""


class ExportPackage(BaseModel):
    readme: str = ""
    architecture_doc: str = ""
    presentation_doc: str = ""
    pitch_doc: str = ""
    implementation_guide: str = ""


class ProviderUsage(BaseModel):
    provider: str = ""
    calls: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0


class StageMetric(BaseModel):
    stage: str = ""
    duration_seconds: float = 0.0
    tokens: int = 0
    cost: float = 0.0


class ExecutionMetadata(BaseModel):
    total_duration_seconds: float = 0.0
    total_tokens: int = 0
    total_cost: float = 0.0
    provider_usage: list[ProviderUsage] = Field(default_factory=list)
    stage_metrics: list[StageMetric] = Field(default_factory=list)


class WorkflowError(BaseModel):
    stage: str = ""
    timestamp: str = Field(default_factory=_now)
    message: str = ""
    retry_count: int = 0


class ExHackerState(BaseModel):
    metadata: WorkflowMetadata = Field(default_factory=WorkflowMetadata)
    project: Project = Field(default_factory=Project)
    team_profile: TeamProfile | None = None
    challenge_intelligence: ChallengeIntelligence | None = None
    problem_analysis: ProblemAnalysis | None = None
    opportunity_analysis: OpportunityAnalysis | None = None
    generated_ideas: list[Idea] = Field(default_factory=list)
    validation_reports: list[ValidationReport] = Field(default_factory=list)
    selected_idea: Idea | None = None
    tech_stack: TechStack | None = None
    architecture: ArchitecturePackage | None = None
    build_package: BuildPackage | None = None
    prompt_package: PromptPackage | None = None
    presentation: PresentationPackage | None = None
    pitch: PitchPackage | None = None
    exports: ExportPackage | None = None
    execution: ExecutionMetadata | None = None
    errors: list[WorkflowError] = Field(default_factory=list)

    def model_dump_workflow(self) -> dict[str, Any]:
        return self.model_dump(exclude_none=True)
