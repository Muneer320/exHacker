from typing import Any

from app.agents.base import AgentResult, BaseAgent
from app.prompts.user_profiler import SYSTEM_PROMPT, USER_PROFILE_TEMPLATE
from app.services.llm import LLMService, llm_service


class UserProfilerAgent(BaseAgent):
    name = "user_profiler"
    description = "Analyzes team constraints and establishes project scope boundaries"
    critical = False

    def __init__(self, llm: LLMService | None = None) -> None:
        super().__init__()
        self._llm = llm or llm_service

    async def execute(self, state: dict[str, Any]) -> AgentResult:
        project = state.get("project", {})
        team_data = project.get("team_data", {})

        team_size = team_data.get("team_size", 4)
        duration_hours = team_data.get("duration_hours", 24)
        experience_level = team_data.get("experience_level", "intermediate")
        skills = team_data.get("skills", [])

        if not skills:
            return AgentResult(
                success=False,
                error="Team skills list is empty",
            )

        user_prompt = USER_PROFILE_TEMPLATE.format(
            team_size=team_size,
            duration_hours=duration_hours,
            experience_level=experience_level,
            skills=", ".join(skills),
        )

        result_text = await self._llm.generate(SYSTEM_PROMPT, user_prompt)

        try:
            import json
            analysis = json.loads(result_text)
        except json.JSONDecodeError:
            analysis = {
                "complexity_budget": "medium",
                "recommended_scope": "mvp",
                "risk_tolerance": "medium",
                "execution_capacity_score": 70.0,
            }

        return AgentResult(
            success=True,
            output={
                "complexity_budget": analysis.get("complexity_budget", "medium"),
                "recommended_scope": analysis.get("recommended_scope", "mvp"),
                "risk_tolerance": analysis.get("risk_tolerance", "medium"),
                "execution_capacity_score": analysis.get("execution_capacity_score", 70.0),
                "team_size": team_size,
                "duration_hours": duration_hours,
                "skills": skills,
                "experience_level": experience_level,
            },
        )
