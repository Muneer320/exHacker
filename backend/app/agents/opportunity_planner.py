from typing import Any

from app.agents.base import AgentResult, BaseAgent
from app.prompts.opportunity_planner import OPPORTUNITY_TEMPLATE, SYSTEM_PROMPT
from app.services.llm import LLMService, llm_service


class OpportunityPlannerAgent(BaseAgent):
    name = "opportunity_planner"
    description = "Discovers high-value opportunities within the problem space"
    critical = False

    def __init__(self, llm: LLMService | None = None) -> None:
        super().__init__()
        self._llm = llm or llm_service

    async def execute(self, state: dict[str, Any]) -> AgentResult:
        problem = state.get("problem_analysis", {})
        challenge = state.get("challenge_intelligence", {})
        profiler = state.get("user_profiler", {})

        user_prompt = OPPORTUNITY_TEMPLATE.format(
            problem_analysis=(
                f"Problem: {problem.get('problem_definition', 'Not defined')}\n"
                f"Stakeholders: {', '.join(problem.get('stakeholders', []))}\n"
                f"Pain Points: {', '.join(problem.get('pain_points', []))}"
            ),
            challenge_intelligence=(
                f"Themes: {', '.join(challenge.get('themes', []))}\n"
                f"Opportunities: {', '.join(challenge.get('opportunities', []))}\n"
                f"Constraints: {', '.join(challenge.get('constraints', []))}"
            ),
            team_profile=(
                f"Complexity Budget: {profiler.get('complexity_budget', 'medium')}\n"
                f"Scope: {profiler.get('recommended_scope', 'mvp')}\n"
                f"Skills: {', '.join(profiler.get('skills', []))}"
            ),
        )

        result_text = await self._llm.generate(SYSTEM_PROMPT, user_prompt)

        try:
            import json
            analysis = json.loads(result_text)
        except json.JSONDecodeError:
            analysis = {
                "market_gaps": [],
                "innovation_opportunities": [],
                "high_impact_areas": [],
                "technical_opportunities": [],
            }

        return AgentResult(
            success=True,
            output={
                "market_gaps": analysis.get("market_gaps", []),
                "innovation_opportunities": analysis.get("innovation_opportunities", []),
                "high_impact_areas": analysis.get("high_impact_areas", []),
                "technical_opportunities": analysis.get("technical_opportunities", []),
            },
        )
