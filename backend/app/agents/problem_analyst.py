from typing import Any

from app.agents.base import AgentResult, BaseAgent


class ProblemAnalystAgent(BaseAgent):
    name = "problem_analyst"
    description = "Analyzes problem space to identify stakeholders, pain points, and metrics"
    critical = True

    async def execute(self, state: dict[str, Any]) -> AgentResult:
        challenge = state.get("challenge_intelligence", {})
        challenge_statements = challenge.get("challenge_statements", [])
        themes = challenge.get("themes", [])

        if not challenge_statements:
            return AgentResult(
                success=False,
                error="No challenge intelligence available",
            )

        return AgentResult(
            success=True,
            output={
                "stakeholders": [],
                "pain_points": [],
                "assumptions": [],
                "success_metrics": [],
                "problem_definition": challenge_statements[0] if challenge_statements else "",
                "themes": themes,
            },
        )
