from typing import Any

from app.agents.base import AgentResult, BaseAgent
from app.prompts.build_accelerator import BUILD_TEMPLATE, SYSTEM_PROMPT
from app.schemas.prompts import PromptPackage
from app.services.llm import LLMService, llm_service


class BuildAcceleratorAgent(BaseAgent):
    name = "build_accelerator"
    description = "Generates implementation prompts for multiple AI platforms"
    critical = False

    def __init__(self, llm: LLMService | None = None) -> None:
        super().__init__()
        self._llm = llm or llm_service

    async def execute(self, state: dict[str, Any]) -> AgentResult:
        arch = state.get("architecture", {})
        tech = state.get("tech_stack", {})
        project = state.get("project", {})
        challenge = state.get("challenge_intelligence", {})
        team_data = project.get("team_data", {})

        features = arch.get("features", [])
        apis = arch.get("api_design", [])

        user_prompt = BUILD_TEMPLATE.format(
            architecture_summary=(
                f"Vision: {arch.get('vision', '')}\n"
                f"Scope: {arch.get('product_scope', '')}\n"
                f"Features: {', '.join(f.get('title', '') for f in features[:5])}\n"
                f"APIs: {len(apis)} endpoints"
            ),
            tech_stack_summary=(
                f"Frontend: {tech.get('frontend', '')}\n"
                f"Backend: {tech.get('backend', '')}\n"
                f"Database: {tech.get('database', '')}\n"
                f"Hosting: {tech.get('hosting', '')}\n"
                f"AI: {', '.join(tech.get('ai_models', []))}"
            ),
            project_context=(
                f"Duration: {team_data.get('duration_hours', 24)}h\n"
                f"Team: {team_data.get('team_size', 4)} people\n"
                f"Theme: {', '.join(challenge.get('themes', []))}"
            ),
        )

        result = await self._llm.generate_structured(
            SYSTEM_PROMPT, user_prompt, PromptPackage, agent_name=self.name,
        )
        parsed = result.get("parsed", {})

        prompts = PromptPackage(
            frontend_prompts=parsed.get("frontend_prompts", []),
            backend_prompts=parsed.get("backend_prompts", []),
            database_prompts=parsed.get("database_prompts", []),
            ai_prompts=parsed.get("ai_prompts", []),
            testing_prompts=parsed.get("testing_prompts", []),
            deployment_prompts=parsed.get("deployment_prompts", []),
        )

        return AgentResult(success=True, output=prompts.model_dump())
