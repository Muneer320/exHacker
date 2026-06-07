from typing import Any

from app.agents.base import AgentResult, BaseAgent
from app.prompts.idea_validator import SYSTEM_PROMPT, VALIDATION_TEMPLATE
from app.schemas.idea import Idea, ValidationReport
from app.services.llm import LLMService, llm_service


class IdeaValidatorAgent(BaseAgent):
    name = "idea_validator"
    description = "Researches and scores generated ideas against multiple criteria"
    critical = False

    def __init__(self, llm: LLMService | None = None) -> None:
        super().__init__()
        self._llm = llm or llm_service

    async def execute(self, state: dict[str, Any]) -> AgentResult:
        ideas = state.get("generated_ideas", [])
        challenge = state.get("challenge_intelligence", {})

        if not ideas:
            return AgentResult(
                success=False,
                error="No ideas to validate",
            )

        challenge_context = (
            f"Themes: {', '.join(challenge.get('themes', []))}\n"
            f"Eval Focus: {', '.join(challenge.get('evaluation_focus', []))}"
        )

        validated_ideas: list[dict[str, Any]] = []
        reports: list[dict[str, Any]] = []
        for idea in ideas:
            user_prompt = VALIDATION_TEMPLATE.format(
                idea_title=idea.get("title", "Untitled"),
                idea_description=idea.get("description", ""),
                features=", ".join(idea.get("key_features", [])),
                users=", ".join(idea.get("target_users", [])),
                challenge_context=challenge_context,
            )

            result = await self._llm.generate_structured(
                SYSTEM_PROMPT, user_prompt, dict, agent_name=self.name,
            )
            analysis = result.get("parsed", {})

            innovation = float(analysis.get("innovation", 0))
            feasibility = float(analysis.get("feasibility", 0))
            hackathon_fit = float(analysis.get("hackathon_fit", 0))
            tech_wow = float(analysis.get("technical_wow", 0))
            final_score = (
                innovation * 0.3 + feasibility * 0.3
                + hackathon_fit * 0.2 + tech_wow * 0.2
            )

            report = ValidationReport(
                idea_id=idea["id"],
                competitors=analysis.get("competitors", []),
                open_source_projects=analysis.get("open_source_projects", []),
                available_apis=analysis.get("available_apis", []),
                strengths=analysis.get("strengths", []),
                weaknesses=analysis.get("weaknesses", []),
                risks=analysis.get("risks", []),
                final_score=round(final_score, 1),
            )

            updated_idea = Idea(
                id=idea["id"],
                title=idea.get("title", "Untitled"),
                description=idea.get("description", ""),
                target_users=idea.get("target_users", []),
                key_features=idea.get("key_features", []),
                innovation_score=round(innovation, 1),
                feasibility_score=round(feasibility, 1),
                hackathon_fit_score=round(hackathon_fit, 1),
                technical_wow_score=round(tech_wow, 1),
                final_score=round(final_score, 1),
            )

            validated_ideas.append(updated_idea.model_dump())
            reports.append(report.model_dump())

        return AgentResult(
            success=True,
            output={
                "ideas": validated_ideas,
                "validation_reports": reports,
            },
        )
