from typing import Any

from app.agents.base import AgentResult, BaseAgent
from app.prompts.solution_architect import ARCHITECTURE_TEMPLATE, SYSTEM_PROMPT
from app.schemas.architecture import ArchitecturePackage
from app.services.llm import LLMService, llm_service


class SolutionArchitectAgent(BaseAgent):
    name = "solution_architect"
    description = "Designs complete project blueprint from selected idea"
    critical = True

    def __init__(self, llm: LLMService | None = None) -> None:
        super().__init__()
        self._llm = llm or llm_service

    async def execute(self, state: dict[str, Any]) -> AgentResult:
        selected = state.get("selected_idea") or {}
        team = state.get("team_profile") or {}
        project = state.get("project", {})

        if not selected or not selected.get("id"):
            ideas = state.get("generated_ideas") or []
            selected = ideas[0] if ideas else {}
            if not selected:
                return AgentResult(
                    success=False,
                    error="No selected idea available",
                )

        team_data = project.get("team_data", {})

        user_prompt = ARCHITECTURE_TEMPLATE.format(
            idea_title=selected.get("title", "Untitled"),
            idea_description=selected.get("description", ""),
            target_users=", ".join(selected.get("target_users", [])),
            key_features=", ".join(selected.get("key_features", [])),
            innovation=selected.get("innovation_score", 0),
            feasibility=selected.get("feasibility_score", 0),
            team_size=team_data.get("team_size", 4),
            duration_hours=team_data.get("duration_hours", 24),
            skills=", ".join(team.get("skills", team_data.get("skills", []))),
            complexity_budget=team.get("complexity_budget", "medium"),
            recommended_scope=team.get("recommended_scope", "mvp"),
        )

        result = await self._llm.generate_structured(
            SYSTEM_PROMPT, user_prompt, ArchitecturePackage, agent_name=self.name,
        )
        parsed = result.get("parsed", {})

        arch = ArchitecturePackage(
            vision=parsed.get("vision", selected.get("description", "")),
            product_scope=parsed.get("product_scope", "MVP"),
            features=parsed.get("features", []),
            user_stories=parsed.get("user_stories", []),
            architecture=parsed.get("architecture", {}),
            api_design=parsed.get("api_design", []),
            database_schema=parsed.get("database_schema", {}),
            integrations=parsed.get("integrations", []),
        )

        return AgentResult(success=True, output=arch.model_dump())
