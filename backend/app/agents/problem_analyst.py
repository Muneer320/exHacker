from typing import Any

from app.agents.base import AgentResult, BaseAgent
from app.prompts.problem_analyst import PROBLEM_ANALYSIS_TEMPLATE, SYSTEM_PROMPT
from app.schemas.problem import ProblemAnalysis
from app.services.llm import LLMService, llm_service


class ProblemAnalystAgent(BaseAgent):
    name = "problem_analyst"
    description = "Analyzes problem space to identify stakeholders, pain points, metrics"
    critical = True

    def __init__(self, llm: LLMService | None = None) -> None:
        super().__init__()
        self._llm = llm or llm_service

    async def execute(self, state: dict[str, Any]) -> AgentResult:
        challenge_intel = state.get("challenge_intelligence", {})
        project = state.get("project", {})
        challenge_data = project.get("challenge_data", {})

        challenge_statements = challenge_intel.get("challenge_statements", [])
        themes = challenge_intel.get("themes", [])
        opportunities = challenge_intel.get("opportunities", [])
        evaluation_focus = challenge_intel.get("evaluation_focus", [])

        if not challenge_statements and not challenge_data.get("challenge_statements"):
            return AgentResult(
                success=False,
                error="No challenge intelligence available",
            )

        statements = challenge_statements or challenge_data.get("challenge_statements", [])
        context = "\n".join(statements)

        user_prompt = PROBLEM_ANALYSIS_TEMPLATE.format(
            challenge_context=context,
            challenge_intelligence=(
                f"Themes: {', '.join(themes)}\n"
                f"Opportunities: {', '.join(opportunities)}\n"
                f"Evaluation Focus: {', '.join(evaluation_focus)}"
            ),
        )

        result = await self._llm.generate_structured(
            SYSTEM_PROMPT, user_prompt, ProblemAnalysis, agent_name=self.name,
        )
        parsed = result.get("parsed", {})

        analysis = ProblemAnalysis(
            stakeholders=parsed.get("stakeholders", []),
            pain_points=parsed.get("pain_points", []),
            assumptions=parsed.get("assumptions", []),
            success_metrics=parsed.get("success_metrics", []),
            problem_definition=parsed.get("problem_definition", statements[0] if statements else ""),
        )

        return AgentResult(success=True, output=analysis.model_dump())
