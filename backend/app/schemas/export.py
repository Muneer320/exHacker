from pydantic import BaseModel, Field

from app.schemas.architecture import ArchitecturePackage
from app.schemas.challenge import ChallengeIntelligence
from app.schemas.idea import Idea
from app.schemas.opportunity import OpportunityAnalysis
from app.schemas.pitch import PitchPackage
from app.schemas.presentation import PresentationPackage
from app.schemas.problem import ProblemAnalysis
from app.schemas.prompts import PromptPackage
from app.schemas.tech_stack import TechStack


class ExportPackage(BaseModel):
    project_id: str
    project_name: str
    challenge_statements: list[str] = Field(default_factory=list)
    intelligence: ChallengeIntelligence | None = None
    problem_analysis: ProblemAnalysis | None = None
    opportunities: OpportunityAnalysis | None = None
    selected_idea: Idea | None = None
    architecture: ArchitecturePackage | None = None
    tech_stack: TechStack | None = None
    prompts: PromptPackage | None = None
    presentation: PresentationPackage | None = None
    pitch: PitchPackage | None = None
