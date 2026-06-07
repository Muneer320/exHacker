from typing import Any

from app.agents.base import AgentResult, BaseAgent
from app.prompts.challenge_intelligence import CHALLENGE_TEMPLATE, SYSTEM_PROMPT
from app.services.llm import LLMService, llm_service


class ChallengeIntelligenceAgent(BaseAgent):
    name = "challenge_intelligence"
    description = "Analyzes challenge statements to extract themes, opportunities, constraints"
    critical = True

    def __init__(self, llm: LLMService | None = None) -> None:
        super().__init__()
        self._llm = llm or llm_service

    async def execute(self, state: dict[str, Any]) -> AgentResult:
        project = state.get("project", {})
        challenge_data = project.get("challenge_data", {})
        resource_data = project.get("resource_data", {})

        challenge_statements = challenge_data.get("challenge_statements", [])
        tracks = resource_data.get("tracks", [])
        evaluation_criteria = challenge_data.get("evaluation_criteria", [])
        datasets = resource_data.get("datasets", [])
        apis = resource_data.get("apis", [])

        if not challenge_statements:
            return AgentResult(
                success=False,
                error="No challenge statements provided",
            )

        user_prompt = CHALLENGE_TEMPLATE.format(
            challenge_statements="\n".join(challenge_statements),
            tracks=", ".join(tracks) if tracks else "None specified",
            resources=(
                f"Datasets: {', '.join(datasets) if datasets else 'None'}, "
                f"APIs: {', '.join(apis) if apis else 'None'}"
            ),
            criteria=", ".join(evaluation_criteria) if evaluation_criteria else "Not specified",
        )

        result_text = await self._llm.generate(SYSTEM_PROMPT, user_prompt)

        try:
            import json
            analysis = json.loads(result_text)
        except json.JSONDecodeError:
            analysis = {
                "themes": [s[:100] for s in challenge_statements],
                "opportunities": [],
                "constraints": [],
                "resource_opportunities": [
                    *[f"Dataset: {d}" for d in datasets],
                    *[f"API: {a}" for a in apis],
                ],
                "evaluation_focus": evaluation_criteria,
            }

        return AgentResult(
            success=True,
            output={
                "themes": analysis.get("themes", []),
                "opportunities": analysis.get("opportunities", []),
                "constraints": analysis.get("constraints", []),
                "resource_opportunities": analysis.get("resource_opportunities", []),
                "evaluation_focus": analysis.get("evaluation_focus", evaluation_criteria),
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
