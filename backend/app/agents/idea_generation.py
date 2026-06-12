"""
Idea Generation Agent

Purpose: Generate 5 distinct, viable project ideas.
Reads:   challenge_intelligence, problem_analysis, opportunity_analysis, team_profile
Writes:  generated_ideas
"""

import uuid
from typing import Type, Dict, Any, List

from pydantic import BaseModel, Field

from app.agents.base import BaseAgent
from app.schemas.state import WorkflowStage, Idea


class IdeaList(BaseModel):
    """Wrapper so LLM returns a list of ideas as a JSON object."""
    ideas: List[Idea] = Field(default_factory=list)


class IdeaGenerationAgent(BaseAgent):
    agent_name = "IdeaGenerationAgent"
    stage = WorkflowStage.IDEA_GENERATION

    @property
    def response_schema(self) -> Type[IdeaList]:
        return IdeaList

    def build_system_prompt(self, state: Dict[str, Any]) -> str:
        return (
            "You are a specialized AI agent.\n\n"
            "ROLE: Creative Innovation Director\n\n"
            "OBJECTIVE:\n"
            "Generate 5 diverse, compelling project ideas for a hackathon.\n"
            "Each idea should be:\n"
            "- Feasible within the time constraint\n"
            "- Innovative and differentiated\n"
            "- Targeted at real users with real problems\n"
            "- Demo-friendly (can be shown in 3 minutes)\n\n"
            "RULES:\n"
            "- Diverge — generate radically different directions, not variations.\n"
            "- Never stop at the first good idea.\n"
            "- innovation_score is 0.0-10.0 — be honest, not optimistic.\n"
            "- Each idea MUST have a unique UUID for 'id' field.\n"
            "- Return valid JSON only. No markdown. No explanations.\n\n"
            "OUTPUT SCHEMA:\n"
            "{\n"
            '  "ideas": [\n'
            "    {\n"
            '      "id": "uuid-string",\n'
            '      "title": "string",\n'
            '      "description": "string (2-3 sentences)",\n'
            '      "target_users": ["string"],\n'
            '      "key_features": ["string (min 3)"],\n'
            '      "innovation_score": 0.0\n'
            "    }\n"
            "  ]\n"
            "}"
        )

    def build_user_prompt(self, state: Dict[str, Any]) -> str:
        ci = state.get("challenge_intelligence") or {}
        pa = state.get("problem_analysis") or {}
        oa = state.get("opportunity_analysis") or {}
        team = state.get("team_profile") or {}
        project = state.get("project") or {}

        return (
            f"PROJECT NAME: {project.get('name', 'Hackathon Project')}\n"
            f"DURATION: {project.get('duration_hours', 48)} hours\n\n"
            f"REFINED PROBLEM: {pa.get('refined_problem_statement', 'No problem defined.')}\n\n"
            f"KEY THEMES: {', '.join(ci.get('themes', []))}\n\n"
            f"MARKET GAPS:\n"
            + "\n".join(f"- {g}" for g in oa.get("market_gaps", []))
            + "\n\nINNOVATION OPPORTUNITIES:\n"
            + "\n".join(f"- {o}" for o in oa.get("innovation_opportunities", []))
            + "\n\nTEAM KNOWN TECH: "
            + ", ".join(team.get("known_technologies", []) if team else ["General"])
            + "\n\n"
            "Generate exactly 5 ideas. Make each idea distinctly different. "
            "Return the JSON object following the schema exactly."
        )

    def apply_result(self, state: Dict[str, Any], result: IdeaList) -> Dict[str, Any]:
        # Ensure all ideas have valid UUIDs
        ideas = []
        for idea in result.ideas:
            idea_dict = idea.model_dump()
            if not idea_dict.get("id") or len(idea_dict["id"]) < 10:
                idea_dict["id"] = str(uuid.uuid4())
            ideas.append(idea_dict)
        state["generated_ideas"] = ideas
        return state

    def mock_result(self, state: Dict[str, Any]) -> IdeaList:
        project = state.get("project", {})
        name = project.get("name", "HackProject")
        return IdeaList(
            ideas=[
                Idea(
                    id=str(uuid.uuid4()),
                    title=f"{name} Sentinel",
                    description=(
                        "An autonomous monitoring agent that watches running AI pipelines "
                        "and auto-recovers failures via dynamic LLM key rotation, ensuring "
                        "100% uptime for production and live demo scenarios."
                    ),
                    target_users=["Hackathon Teams", "Indie Developers", "AI Product Teams"],
                    key_features=[
                        "Groq → Gemini → OpenAI automatic provider fallback",
                        "Real-time error log dashboard",
                        "Configurable retry policies",
                    ],
                    innovation_score=8.5,
                ),
                Idea(
                    id=str(uuid.uuid4()),
                    title=f"{name} Blueprint",
                    description=(
                        "An interactive canvas that generates complete project blueprints "
                        "— including database schema, API contracts, and frontend component "
                        "maps — from a single challenge description input."
                    ),
                    target_users=["Software Architects", "Prototypers", "Backend Developers"],
                    key_features=[
                        "LLM-powered SQL schema generator",
                        "REST API contract designer",
                        "ZIP downloadable project scaffold",
                    ],
                    innovation_score=9.2,
                ),
                Idea(
                    id=str(uuid.uuid4()),
                    title=f"{name} PitchMaster",
                    description=(
                        "Analyzes your product idea and auto-generates judge-ready presentation "
                        "slides, an elevator pitch script, and anticipated Q&A answers — all in "
                        "under 60 seconds."
                    ),
                    target_users=["Team Leaders", "Product Managers", "First-time Founders"],
                    key_features=[
                        "Markdown slide deck generator",
                        "30s / 2m / 5m pitch scripts",
                        "Judge Q&A simulator with answers",
                    ],
                    innovation_score=8.8,
                ),
                Idea(
                    id=str(uuid.uuid4()),
                    title=f"{name} CodeSprint",
                    description=(
                        "AI-powered development task planner that breaks an architecture doc "
                        "into an ordered, assigned sprint board with AI-generated implementation "
                        "prompts for each task."
                    ),
                    target_users=["Development Teams", "Scrum Masters", "Solo Hackers"],
                    key_features=[
                        "Architecture-to-task decomposer",
                        "Role-based task assignment",
                        "Copy-ready LLM code prompts per task",
                    ],
                    innovation_score=8.0,
                ),
                Idea(
                    id=str(uuid.uuid4()),
                    title=f"{name} Validator",
                    description=(
                        "Automatically validates hackathon project ideas against live market data "
                        "— surfacing real competitors, GitHub open source alternatives, and "
                        "feasibility scores before you invest hours building."
                    ),
                    target_users=["Entrepreneurs", "Hackathon Strategists", "Researchers"],
                    key_features=[
                        "Competitor discovery engine",
                        "Open source alternative finder",
                        "Feasibility + innovation scoring",
                    ],
                    innovation_score=8.3,
                ),
            ]
        )


# Singleton instance
idea_generation_agent = IdeaGenerationAgent()
