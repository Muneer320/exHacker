from typing import Any

from app.agents.base import AgentResult, BaseAgent
from app.prompts.pitch_coach import PITCH_TEMPLATE, SYSTEM_PROMPT
from app.schemas.pitch import PitchPackage
from app.services.llm import LLMService, llm_service


class PitchCoachAgent(BaseAgent):
    name = "pitch_coach"
    description = "Prepares pitch materials for hackathon presentations"
    critical = False

    def __init__(self, llm: LLMService | None = None) -> None:
        super().__init__()
        self._llm = llm or llm_service

    async def execute(self, state: dict[str, Any]) -> AgentResult:
        arch = state.get("architecture") or {}
        tech = state.get("tech_stack") or {}
        challenge = state.get("challenge_intelligence") or {}
        ideas = state.get("generated_ideas") or []
        selected = state.get("selected_idea") or (ideas[0] if ideas else {})
        reports = state.get("validation_reports") or []
        report = reports[0] if reports else {}
        project = state.get("project") or {}

        user_prompt = PITCH_TEMPLATE.format(
            project_title=selected.get("title", "Untitled"),
            project_description=selected.get("description", ""),
            architecture_summary=(
                f"Vision: {arch.get('vision', '')}\n"
                f"Features: {len(arch.get('features', []))} features"
            ),
            tech_stack_summary=(
                f"Frontend: {tech.get('frontend', '')}\n"
                f"Backend: {tech.get('backend', '')}\n"
                f"AI: {', '.join(tech.get('ai_models', []))}"
            ),
            validation_context=(
                f"Score: {report.get('final_score', 0)}\n"
                f"Strengths: {', '.join(report.get('strengths', []))}"
            ),
            eval_criteria=", ".join(challenge.get("evaluation_focus", [])),
            duration_minutes=project.get("pitch_duration", 5),
        )

        result = await self._llm.generate_structured(
            SYSTEM_PROMPT, user_prompt, PitchPackage, agent_name=self.name,
        )
        parsed = result.get("parsed", {})

        pitch = PitchPackage(
            pitch_30=parsed.get("pitch_30", ""),
            pitch_120=parsed.get("pitch_120", ""),
            pitch_300=parsed.get("pitch_300", ""),
            qa=parsed.get("qa", []),
            demo_script=parsed.get("demo_script", ""),
        )

        return AgentResult(success=True, output=pitch.model_dump())
