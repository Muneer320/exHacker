import uuid
from typing import Any

from app.agents.base import AgentResult, BaseAgent
from app.prompts.idea_generator import IDEA_GENERATION_TEMPLATE, SYSTEM_PROMPT
from app.schemas.idea import Idea
from app.services.llm import LLMService, llm_service


class IdeaGeneratorAgent(BaseAgent):
    name = "idea_generator"
    description = "Generates diverse candidate project ideas from analysis"
    critical = False

    def __init__(self, llm: LLMService | None = None) -> None:
        super().__init__()
        self._llm = llm or llm_service

    async def execute(self, state: dict[str, Any]) -> AgentResult:
        challenge = state.get("challenge_intelligence") or {}
        problem = state.get("problem_analysis") or {}
        opportunity = state.get("opportunity_analysis") or {}
        team = state.get("team_profile") or {}

        challenge_context = (
            f"Themes: {', '.join(challenge.get('themes', []))}\n"
            f"Constraints: {', '.join(challenge.get('constraints', []))}\n"
            f"Eval Focus: {', '.join(challenge.get('evaluation_focus', []))}"
        )

        user_prompt = IDEA_GENERATION_TEMPLATE.format(
            challenge_context=challenge_context,
            problem_analysis=(
                f"Definition: {problem.get('problem_definition', '')}\n"
                f"Pain Points: {', '.join(problem.get('pain_points', []))}\n"
                f"Stakeholders: {', '.join(problem.get('stakeholders', []))}"
            ),
            opportunity_analysis=(
                f"Market Gaps: {', '.join(opportunity.get('market_gaps', []))}\n"
                f"Innovation: {', '.join(opportunity.get('innovation_opportunities', []))}\n"
                f"High Impact: {', '.join(opportunity.get('high_impact_areas', []))}"
            ),
            team_profile=(
                f"Budget: {team.get('complexity_budget', 'medium')}\n"
                f"Scope: {team.get('recommended_scope', 'mvp')}\n"
                f"Skills: {', '.join(team.get('skills', []))}"
            ),
        )

        result = await self._llm.generate_structured(
            SYSTEM_PROMPT, user_prompt, dict, agent_name=self.name,
        )
        parsed = result.get("parsed", {})
        raw_ideas = parsed.get("ideas", [])

        if not raw_ideas:
            return AgentResult(
                success=False,
                error="LLM returned no ideas — check API quota or prompt",
            )

        ideas = []
        for raw in raw_ideas:
            idea = Idea(
                id=str(uuid.uuid4()),
                title=raw.get("title", "Untitled"),
                description=raw.get("description", ""),
                target_users=raw.get("target_users", []),
                key_features=raw.get("key_features", []),
                innovation_score=float(raw.get("innovation_score", 0)),
                final_score=float(raw.get("innovation_score", 0)),
            )
            ideas.append(idea.model_dump())

        return AgentResult(success=True, output={"ideas": ideas})
