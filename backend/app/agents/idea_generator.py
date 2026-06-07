import json
import uuid
from typing import Any

from app.agents.base import AgentResult, BaseAgent
from app.prompts.idea_generator import IDEA_GENERATION_TEMPLATE, SYSTEM_PROMPT
from app.services.llm import LLMService, llm_service


class IdeaGeneratorAgent(BaseAgent):
    name = "idea_generator"
    description = "Generates diverse candidate project ideas from analysis"
    critical = False

    def __init__(self, llm: LLMService | None = None) -> None:
        super().__init__()
        self._llm = llm or llm_service

    async def execute(self, state: dict[str, Any]) -> AgentResult:
        challenge = state.get("challenge_intelligence", {})
        problem = state.get("problem_analysis", {})
        opportunity = state.get("opportunity_analysis", {})
        profiler = state.get("user_profiler", {})

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
                f"Budget: {profiler.get('complexity_budget', 'medium')}\n"
                f"Scope: {profiler.get('recommended_scope', 'mvp')}\n"
                f"Skills: {', '.join(profiler.get('skills', []))}"
            ),
        )

        result_text = await self._llm.generate(SYSTEM_PROMPT, user_prompt)

        try:
            data = json.loads(result_text)
            raw_ideas = data.get("ideas", [])
        except json.JSONDecodeError:
            raw_ideas = []

        ideas = []
        for raw in raw_ideas:
            ideas.append({
                "id": str(uuid.uuid4()),
                "title": raw.get("title", "Untitled"),
                "description": raw.get("description", ""),
                "target_users": raw.get("target_users", []),
                "key_features": raw.get("key_features", []),
                "innovation_score": float(raw.get("innovation_score", 0)),
                "feasibility_score": 0.0,
                "hackathon_fit_score": 0.0,
                "technical_wow_score": 0.0,
                "final_score": float(raw.get("innovation_score", 0)),
            })

        return AgentResult(
            success=True,
            output={
                "ideas": ideas,
            },
        )
