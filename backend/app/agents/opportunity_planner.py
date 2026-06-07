from typing import Any

from app.agents.base import AgentResult, BaseAgent
from app.prompts.opportunity_planner import OPPORTUNITY_TEMPLATE, SYSTEM_PROMPT
from app.schemas.opportunity import OpportunityAnalysis
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
        team = state.get("team_profile", {})

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
                f"Complexity Budget: {team.get('complexity_budget', 'medium')}\n"
                f"Scope: {team.get('recommended_scope', 'mvp')}\n"
                f"Skills: {', '.join(team.get('skills', []))}"
            ),
        )

        result = await self._llm.generate_structured(
            SYSTEM_PROMPT, user_prompt, OpportunityAnalysis, agent_name=self.name,
        )
        parsed = result.get("parsed", {})

        analysis = OpportunityAnalysis(
            market_gaps=parsed.get("market_gaps", []),
            innovation_opportunities=parsed.get("innovation_opportunities", []),
            high_impact_areas=parsed.get("high_impact_areas", []),
            technical_opportunities=parsed.get("technical_opportunities", []),
        )

        return AgentResult(success=True, output=analysis.model_dump())
