import json
from typing import Any

from app.agents.base import AgentResult, BaseAgent
from app.prompts.pitch_coach import PITCH_TEMPLATE, SYSTEM_PROMPT
from app.services.llm import LLMService, llm_service


class PitchCoachAgent(BaseAgent):
    name = "pitch_coach"
    description = "Prepares pitch materials for hackathon presentations"
    critical = False

    def __init__(self, llm: LLMService | None = None) -> None:
        super().__init__()
        self._llm = llm or llm_service

    async def execute(self, state: dict[str, Any]) -> AgentResult:
        arch = state.get("solution_architect", {})
        tech = state.get("tech_stack_advisor", {})
        validated = state.get("idea_validator", {})
        challenge = state.get("challenge_intelligence", {})
        ideas = state.get("idea_generator", {}).get("ideas", [])
        selected = state.get("selected_idea", ideas[0] if ideas else {})
        project = state.get("project", {})

        reports = validated.get("validation_reports", [])
        report = reports[0] if reports else {}

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

        result_text = await self._llm.generate(SYSTEM_PROMPT, user_prompt)

        try:
            pitch = json.loads(result_text)
        except json.JSONDecodeError:
            pitch = {}

        return AgentResult(
            success=True,
            output={
                "pitch_30": pitch.get("pitch_30", ""),
                "pitch_120": pitch.get("pitch_120", ""),
                "pitch_300": pitch.get("pitch_300", ""),
                "qa": [
                    {"question": q.get("question", ""), "answer": q.get("answer", "")}
                    for q in pitch.get("qa", [])
                ],
                "demo_script": pitch.get("demo_script", ""),
            },
        )
