from typing import Any

from app.agents.base import AgentResult, BaseAgent
from app.prompts.presentation_agent import PRESENTATION_TEMPLATE, SYSTEM_PROMPT
from app.schemas.presentation import PresentationPackage
from app.services.llm import LLMService, llm_service


class PresentationAgent(BaseAgent):
    name = "presentation_agent"
    description = "Generates hackathon presentation materials"
    critical = False

    def __init__(self, llm: LLMService | None = None) -> None:
        super().__init__()
        self._llm = llm or llm_service

    async def execute(self, state: dict[str, Any]) -> AgentResult:
        arch = state.get("architecture") or {}
        ideas = state.get("generated_ideas") or []
        selected = state.get("selected_idea") or (ideas[0] if ideas else {})
        reports = state.get("validation_reports") or []
        report = reports[0] if reports else {}

        features = arch.get("features", [])

        user_prompt = PRESENTATION_TEMPLATE.format(
            project_title=selected.get("title", "Untitled"),
            project_description=selected.get("description", ""),
            features=", ".join(f.get("title", "") for f in features[:5]),
            validation_context=(
                f"Score: {report.get('final_score', 0)}\n"
                f"Strengths: {', '.join(report.get('strengths', []))}\n"
                f"Risks: {', '.join(report.get('risks', []))}"
            ),
            architecture_summary=(
                f"Vision: {arch.get('vision', '')}\n"
                f"Scope: {arch.get('product_scope', '')}"
            ),
        )

        result = await self._llm.generate_structured(
            SYSTEM_PROMPT, user_prompt, PresentationPackage, agent_name=self.name,
        )
        parsed = result.get("parsed", {})

        presentation = PresentationPackage(
            slides=parsed.get("slides", []),
            diagrams=parsed.get("diagrams", []),
            demo_story=parsed.get("demo_story", ""),
        )

        return AgentResult(success=True, output=presentation.model_dump())
