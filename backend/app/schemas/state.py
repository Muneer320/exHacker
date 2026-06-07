from enum import StrEnum

from pydantic import BaseModel, Field

from app.schemas.architecture import ArchitecturePackage
from app.schemas.challenge import ChallengeIntelligence
from app.schemas.idea import Idea, ValidationReport
from app.schemas.opportunity import OpportunityAnalysis
from app.schemas.pitch import PitchPackage
from app.schemas.presentation import PresentationPackage
from app.schemas.problem import ProblemAnalysis
from app.schemas.project import ProjectResponse
from app.schemas.prompts import PromptPackage
from app.schemas.team import TeamProfile
from app.schemas.tech_stack import TechStack


class WorkflowStage(StrEnum):
    INPUT = "input"
    CHALLENGE_INTELLIGENCE = "challenge_intelligence"
    PROBLEM_ANALYSIS = "problem_analysis"
    OPPORTUNITY_ANALYSIS = "opportunity_analysis"
    IDEA_GENERATION = "idea_generation"
    IDEA_VALIDATION = "idea_validation"
    IDEA_SELECTION = "idea_selection"
    ARCHITECTURE = "architecture"
    TECH_STACK = "tech_stack"
    BUILD_ACCELERATION = "build_acceleration"
    PRESENTATION = "presentation"
    PITCH = "pitch"
    COMPLETED = "completed"


class AgentErrorSeverity(StrEnum):
    WARNING = "warning"
    CRITICAL = "critical"


class AgentError(BaseModel):
    agent_name: str
    timestamp: str
    message: str
    severity: AgentErrorSeverity = AgentErrorSeverity.WARNING


class ExHackerState(BaseModel):
    project: ProjectResponse
    team_profile: TeamProfile | None = None
    challenge_intelligence: ChallengeIntelligence | None = None
    problem_analysis: ProblemAnalysis | None = None
    opportunity_analysis: OpportunityAnalysis | None = None
    generated_ideas: list[Idea] = Field(default_factory=list)
    validation_reports: list[ValidationReport] = Field(default_factory=list)
    selected_idea: Idea | None = None
    architecture: ArchitecturePackage | None = None
    tech_stack: TechStack | None = None
    prompts: PromptPackage | None = None
    presentation: PresentationPackage | None = None
    pitch: PitchPackage | None = None
    current_stage: WorkflowStage = WorkflowStage.INPUT
    completed_agents: list[str] = Field(default_factory=list)
    errors: list[AgentError] = Field(default_factory=list)
