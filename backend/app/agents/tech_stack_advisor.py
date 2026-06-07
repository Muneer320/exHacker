import json
from typing import Any

from app.agents.base import AgentResult, BaseAgent
from app.prompts.tech_stack_advisor import SYSTEM_PROMPT, TECH_STACK_TEMPLATE
from app.services.llm import LLMService, llm_service


class TechStackAdvisorAgent(BaseAgent):
    name = "tech_stack_advisor"
    description = "Recommends technologies based on architecture and team constraints"
    critical = False

    def __init__(self, llm: LLMService | None = None) -> None:
        super().__init__()
        self._llm = llm or llm_service

    async def execute(self, state: dict[str, Any]) -> AgentResult:
        arch = state.get("solution_architect", {})
        profiler = state.get("user_profiler", {})
        challenge = state.get("challenge_intelligence", {})
        project = state.get("project", {})
        team_data = project.get("team_data", {})

        # If no architecture from agent, use selected idea
        if not arch.get("features"):
            arch = state.get("architecture", {})

        features = arch.get("features", [])
        apis = arch.get("api_design", [])
        integrations = arch.get("integrations", [])

        user_prompt = TECH_STACK_TEMPLATE.format(
            architecture_summary=(
                f"Features: {', '.join(f.get('title', '') for f in features)}\n"
                f"APIs: {len(apis)} endpoints\n"
                f"Integrations: {', '.join(i.get('name', '') for i in integrations)}"
            ),
            team_profile=(
                f"Size: {team_data.get('team_size', 4)}\n"
                f"Duration: {team_data.get('duration_hours', 24)}h\n"
                f"Skills: {', '.join(profiler.get('skills', team_data.get('skills', [])))}\n"
                f"Experience: {team_data.get('experience_level', 'intermediate')}\n"
                f"Budget: {profiler.get('complexity_budget', 'medium')}"
            ),
            challenge_context=(
                f"Themes: {', '.join(challenge.get('themes', []))}\n"
                f"Eval Focus: {', '.join(challenge.get('evaluation_focus', []))}"
            ),
        )

        result_text = await self._llm.generate(SYSTEM_PROMPT, user_prompt)

        try:
            tech = json.loads(result_text)
        except json.JSONDecodeError:
            tech = {}

        return AgentResult(
            success=True,
            output={
                "frontend": tech.get("frontend", ""),
                "backend": tech.get("backend", ""),
                "database": tech.get("database", ""),
                "hosting": tech.get("hosting", ""),
                "ai_models": tech.get("ai_models", []),
                "vector_db": tech.get("vector_db"),
                "auth_provider": tech.get("auth_provider"),
            },
        )
