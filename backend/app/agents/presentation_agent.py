import json
from typing import Any

from app.agents.base import AgentResult, BaseAgent
from app.prompts.presentation_agent import PRESENTATION_TEMPLATE, SYSTEM_PROMPT
from app.services.llm import LLMService, llm_service


class PresentationAgent(BaseAgent):
    name = "presentation_agent"
    description = "Generates hackathon presentation materials"
    critical = False

    def __init__(self, llm: LLMService | None = None) -> None:
        super().__init__()
        self._llm = llm or llm_service

    async def execute(self, state: dict[str, Any]) -> AgentResult:
        arch = state.get("solution_architect", {})
        validated = state.get("idea_validator", {})
        ideas = state.get("idea_generator", {}).get("ideas", [])
        selected = state.get("selected_idea", ideas[0] if ideas else {})

        features = arch.get("features", [])
        reports = validated.get("validation_reports", [])
        report = reports[0] if reports else {}

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

        result_text = await self._llm.generate(SYSTEM_PROMPT, user_prompt)

        try:
            pres = json.loads(result_text)
        except json.JSONDecodeError:
            pres = {}

        return AgentResult(
            success=True,
            output={
                "slides": [
                    {"title": s.get("title", ""), "content": s.get("content", ""),
                     "type": s.get("type", "slide")}
                    for s in pres.get("slides", [])
                ],
                "diagrams": [
                    {"title": d.get("title", ""), "description": d.get("description", ""),
                     "diagram_type": d.get("diagram_type", "architecture"),
                     "content": d.get("content", "")}
                    for d in pres.get("diagrams", [])
                ],
                "demo_story": pres.get("demo_story", ""),
            },
        )
