"""Validated inputs and generated artifacts. Provider output is always untrusted."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Skill(Model):
    technology: str = Field(min_length=1, max_length=80)
    proficiency: Literal["beginner", "intermediate", "advanced"]


class Teammate(Model):
    name: str = Field(min_length=1, max_length=80)
    skills: list[Skill] = Field(min_length=1, max_length=20)
    role: str = Field(default="", max_length=120)
    hours_available: float | None = Field(default=None, gt=0, le=720)


class Intake(Model):
    idea: str = Field(min_length=10, max_length=6000)
    available_hours: float = Field(ge=1, le=720)
    teammates: list[Teammate] = Field(min_length=1, max_length=12)
    name: str = Field(default="", max_length=160)
    hackathon: str = Field(default="", max_length=200)
    judging_criteria: str = Field(default="", max_length=4000)
    rules: str = Field(default="", max_length=4000)
    required_technologies: str = Field(default="", max_length=1000)
    preferred_technologies: str = Field(default="", max_length=1000)
    excluded_technologies: str = Field(default="", max_length=1000)
    target_platform: str = Field(default="web", min_length=1, max_length=120)
    budget: str = Field(default="", max_length=300)
    constraints: str = Field(default="", max_length=4000)

    @model_validator(mode="after")
    def check_members(self):
        names = [member.name.casefold() for member in self.teammates]
        if len(names) != len(set(names)):
            raise ValueError("Give each teammate a different name.")
        if any(
            m.hours_available and m.hours_available > self.available_hours
            for m in self.teammates
        ):
            raise ValueError(
                "A teammate's available hours cannot exceed the project time."
            )
        return self


class Revision(Model):
    revision: int = Field(ge=1)


class GenerateRequest(Revision):
    prompt: str = Field(default="", max_length=4000)
    idea_id: str | None = Field(default=None, max_length=80)


class RefineRequest(GenerateRequest):
    prompt: str = Field(min_length=5, max_length=4000)


class Risk(Model):
    risk: str = Field(min_length=1, max_length=800)
    severity: Literal["low", "medium", "high"]
    mitigation: str = Field(min_length=1, max_length=1000)


SCORE_WEIGHTS = {
    "originality": 0.15,
    "problem_fit": 0.15,
    "feasibility": 0.20,
    "team_fit": 0.15,
    "technical_depth": 0.10,
    "demo_potential": 0.10,
    "judge_appeal": 0.10,
    "impact": 0.05,
}


class Score(Model):
    value: int = Field(ge=0, le=100)
    rationale: str = Field(min_length=10, max_length=1000)


class Scores(Model):
    originality: Score
    problem_fit: Score
    feasibility: Score
    team_fit: Score
    technical_depth: Score
    demo_potential: Score
    judge_appeal: Score
    impact: Score

    def overall(self) -> float:
        return round(
            sum(
                getattr(self, key).value * weight
                for key, weight in SCORE_WEIGHTS.items()
            ),
            1,
        )


class Idea(Model):
    title: str = Field(min_length=3, max_length=160)
    hook: str = Field(min_length=5, max_length=300)
    problem: str = Field(min_length=20, max_length=2000)
    solution: str = Field(min_length=30, max_length=3000)
    target_users: str = Field(min_length=5, max_length=600)
    differentiation: str = Field(min_length=20, max_length=1800)
    core_features: list[str] = Field(min_length=3, max_length=8)
    stretch_features: list[str] = Field(default_factory=list, max_length=5)
    non_goals: list[str] = Field(min_length=1, max_length=10)
    demo_scenario: str = Field(min_length=20, max_length=2000)
    effort_hours: float = Field(gt=0, le=8640)
    risks: list[Risk] = Field(min_length=1, max_length=8)
    assumptions: list[str] = Field(min_length=1, max_length=12)
    scores: Scores
    evidence_ids: list[str] = Field(default_factory=list, max_length=20)
    critique: list[str] = Field(min_length=1, max_length=10)
    changes_made: list[str] = Field(min_length=1, max_length=10)

    @field_validator(
        "core_features",
        "stretch_features",
        "non_goals",
        "assumptions",
        "critique",
        "changes_made",
    )
    @classmethod
    def bounded_items(cls, value):
        if any(not item.strip() or len(item) > 2000 for item in value):
            raise ValueError("List entries must be nonempty and under 2000 characters.")
        return value


class CandidateBatch(Model):
    ideas: list[Idea] = Field(min_length=5, max_length=8)


class RefinedIdea(Model):
    idea: Idea


class StackChoice(Model):
    category: str = Field(min_length=2, max_length=100)
    technology: str = Field(min_length=2, max_length=200)
    purpose: str = Field(min_length=10, max_length=1500)
    rationale: str = Field(min_length=10, max_length=1500)
    alternatives: list[str] = Field(min_length=1, max_length=5)
    tradeoffs: list[str] = Field(min_length=1, max_length=6)


class Component(Model):
    name: str = Field(min_length=2, max_length=120)
    responsibility: str = Field(min_length=10, max_length=1500)
    technology: str = Field(min_length=2, max_length=200)
    depends_on: list[str] = Field(default_factory=list, max_length=12)


class Stack(Model):
    summary: str = Field(min_length=30, max_length=3000)
    choices: list[StackChoice] = Field(min_length=2, max_length=12)
    components: list[Component] = Field(min_length=2, max_length=15)
    data_flow: list[str] = Field(min_length=2, max_length=15)
    compatibility_notes: list[str] = Field(min_length=1, max_length=12)
    risks: list[Risk] = Field(min_length=1, max_length=8)
    setup_steps: list[str] = Field(min_length=2, max_length=20)

    @model_validator(mode="after")
    def distinct_choices(self):
        categories = [choice.category.casefold() for choice in self.choices]
        if len(categories) != len(set(categories)):
            raise ValueError("Each stack category must appear once.")
        return self


class EditStackRequest(Revision):
    stack: Stack


class Requirement(Model):
    id: str = Field(pattern=r"^FR-\d{2,3}$")
    title: str = Field(min_length=3, max_length=200)
    user_story: str = Field(min_length=20, max_length=2000)
    behavior: str = Field(min_length=40, max_length=4000)
    acceptance_criteria: list[str] = Field(min_length=2, max_length=10)
    edge_cases: list[str] = Field(min_length=1, max_length=10)
    priority: Literal["must", "should", "could"]


class Entity(Model):
    name: str = Field(min_length=2, max_length=100)
    fields: list[str] = Field(min_length=2, max_length=25)
    relationships: list[str] = Field(default_factory=list, max_length=10)
    validation: list[str] = Field(min_length=1, max_length=10)


class Endpoint(Model):
    method: Literal[
        "GET", "POST", "PUT", "PATCH", "DELETE", "SUBSCRIBE", "QUERY", "MUTATION"
    ]
    path: str = Field(min_length=1, max_length=200)
    purpose: str = Field(min_length=10, max_length=1000)
    request: str = Field(min_length=2, max_length=2000)
    response: str = Field(min_length=2, max_length=2000)
    authorization: str = Field(min_length=5, max_length=1000)
    errors: list[str] = Field(min_length=1, max_length=10)


class Task(Model):
    id: str = Field(pattern=r"^T-\d{2,3}$")
    title: str = Field(min_length=5, max_length=200)
    owner: str = Field(min_length=1, max_length=80)
    hours: float = Field(gt=0, le=720)
    depends_on: list[str] = Field(default_factory=list, max_length=15)
    deliverable: str = Field(min_length=10, max_length=1500)


class Specification(Model):
    executive_summary: str = Field(min_length=100, max_length=6000)
    user_journeys: list[str] = Field(min_length=2, max_length=10)
    requirements: list[Requirement] = Field(min_length=3, max_length=15)
    pages: list[str] = Field(min_length=1, max_length=20)
    entities: list[Entity] = Field(min_length=1, max_length=12)
    endpoints: list[Endpoint] = Field(min_length=1, max_length=20)
    tasks: list[Task] = Field(min_length=3, max_length=30)
    security: list[str] = Field(min_length=3, max_length=15)
    accessibility: list[str] = Field(min_length=2, max_length=10)
    reliability: list[str] = Field(min_length=3, max_length=15)
    test_plan: list[str] = Field(min_length=3, max_length=20)
    success_metrics: list[str] = Field(min_length=2, max_length=10)
    open_questions: list[str] = Field(default_factory=list, max_length=15)
    agent_instructions: list[str] = Field(min_length=3, max_length=15)

    @model_validator(mode="after")
    def coherent_plan(self):
        ids = [task.id for task in self.tasks]
        if len(ids) != len(set(ids)):
            raise ValueError("Task identifiers must be unique.")
        requirements = [r.id for r in self.requirements]
        if len(requirements) != len(set(requirements)):
            raise ValueError("Requirement identifiers must be unique.")
        known = set(ids)
        completed = set()
        while len(completed) < len(known):
            available = {t.id for t in self.tasks if set(t.depends_on) <= completed}
            if not available - completed:
                raise ValueError(
                    "Task dependencies contain a cycle or an unknown task."
                )
            completed |= available
        return self


class ChatRequest(Revision):
    message: str = Field(min_length=1, max_length=6000)
