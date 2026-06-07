from typing import Any

from app.agents.base import AgentResult, BaseAgent
from app.prompts.tech_stack_advisor import SYSTEM_PROMPT, TECH_STACK_TEMPLATE
from app.schemas.tech_stack import TechStack
from app.services.llm import LLMService, llm_service


class TechStackAdvisorAgent(BaseAgent):
    name = "tech_stack_advisor"
    description = "Recommends technologies based on architecture and team constraints"
    critical = False

    def __init__(self, llm: LLMService | None = None) -> None:
        super().__init__()
        self._llm = llm or llm_service

    async def execute(self, state: dict[str, Any]) -> AgentResult:
        arch = state.get("architecture", {})
        team = state.get("team_profile", {})
        challenge = state.get("challenge_intelligence", {})
        project = state.get("project", {})
        team_data = project.get("team_data", {})

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
                f"Skills: {', '.join(team.get('skills', team_data.get('skills', [])))}\n"
                f"Experience: {team_data.get('experience_level', 'intermediate')}\n"
                f"Budget: {team.get('complexity_budget', 'medium')}"
            ),
            challenge_context=(
                f"Themes: {', '.join(challenge.get('themes', []))}\n"
                f"Eval Focus: {', '.join(challenge.get('evaluation_focus', []))}"
            ),
        )

        result = await self._llm.generate_structured(
            SYSTEM_PROMPT, user_prompt, TechStack, agent_name=self.name,
        )
        parsed = result.get("parsed", {})

        tech_stack = TechStack(
            frontend=parsed.get("frontend", ""),
            backend=parsed.get("backend", ""),
            database=parsed.get("database", ""),
            hosting=parsed.get("hosting", ""),
            ai_models=parsed.get("ai_models", []),
            vector_db=parsed.get("vector_db"),
            auth_provider=parsed.get("auth_provider"),
        )

        return AgentResult(success=True, output=tech_stack.model_dump())
