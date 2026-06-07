import json
from typing import Any

from app.agents.base import AgentResult, BaseAgent
from app.prompts.build_accelerator import BUILD_TEMPLATE, SYSTEM_PROMPT
from app.services.llm import LLMService, llm_service


class BuildAcceleratorAgent(BaseAgent):
    name = "build_accelerator"
    description = "Generates implementation prompts for multiple AI platforms"
    critical = False

    def __init__(self, llm: LLMService | None = None) -> None:
        super().__init__()
        self._llm = llm or llm_service

    async def execute(self, state: dict[str, Any]) -> AgentResult:
        arch = state.get("solution_architect", {})
        tech = state.get("tech_stack_advisor", {})
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

        result_text = await self._llm.generate(SYSTEM_PROMPT, user_prompt)

        try:
            prompts = json.loads(result_text)
        except json.JSONDecodeError:
            prompts = {}

        return AgentResult(
            success=True,
            output={
                "frontend_prompts": prompts.get("frontend_prompts", []),
                "backend_prompts": prompts.get("backend_prompts", []),
                "database_prompts": prompts.get("database_prompts", []),
                "ai_prompts": prompts.get("ai_prompts", []),
                "testing_prompts": prompts.get("testing_prompts", []),
                "deployment_prompts": prompts.get("deployment_prompts", []),
            },
        )
