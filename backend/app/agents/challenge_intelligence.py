from typing import Any

from app.agents.base import AgentResult, BaseAgent


class ChallengeIntelligenceAgent(BaseAgent):
    name = "challenge_intelligence"
    description = "Analyzes challenge statements to extract themes, opportunities, and constraints"
    critical = True

    async def execute(self, state: dict[str, Any]) -> AgentResult:
        project = state.get("project", {})
        challenge_data = project.get("challenge_data", {})
        challenge_statements = challenge_data.get("challenge_statements", [])
        resource_data = project.get("resource_data", {})

        if not challenge_statements:
            return AgentResult(
                success=False,
                error="No challenge statements provided",
            )

        tracks = resource_data.get("tracks", [])
        evaluation_criteria = challenge_data.get("evaluation_criteria", [])
        datasets = resource_data.get("datasets", [])
        apis = resource_data.get("apis", [])

        return AgentResult(
            success=True,
            output={
                "themes": [f"Theme extracted from: {s[:100]}" for s in challenge_statements],
                "opportunities": [],
                "constraints": [],
                "resource_opportunities": [
                    *[f"Dataset available: {d}" for d in datasets],
                    *[f"API available: {a}" for a in apis],
                ],
                "evaluation_focus": evaluation_criteria or [],
                "challenge_statements": challenge_statements,
                "tracks": tracks,
            },
        )

    def validate_inputs(self, state: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        project = state.get("project", {})
        challenge_data = project.get("challenge_data", {})
        if not challenge_data.get("challenge_statements"):
            errors.append("No challenge statements in state")
        return errors
