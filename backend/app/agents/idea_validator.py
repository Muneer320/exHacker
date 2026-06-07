import json
from typing import Any

from app.agents.base import AgentResult, BaseAgent
from app.prompts.idea_validator import SYSTEM_PROMPT, VALIDATION_TEMPLATE
from app.services.llm import LLMService, llm_service


class IdeaValidatorAgent(BaseAgent):
    name = "idea_validator"
    description = "Researches and scores generated ideas against multiple criteria"
    critical = False

    def __init__(self, llm: LLMService | None = None) -> None:
        super().__init__()
        self._llm = llm or llm_service

    async def execute(self, state: dict[str, Any]) -> AgentResult:
        ideas = state.get("idea_generator", {}).get("ideas", [])
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

        validated: list[dict[str, Any]] = []
        for idea in ideas:
            user_prompt = VALIDATION_TEMPLATE.format(
                idea_title=idea.get("title", "Untitled"),
                idea_description=idea.get("description", ""),
                features=", ".join(idea.get("key_features", [])),
                users=", ".join(idea.get("target_users", [])),
                challenge_context=challenge_context,
            )

            result_text = await self._llm.generate(SYSTEM_PROMPT, user_prompt)

            try:
                analysis = json.loads(result_text)
            except json.JSONDecodeError:
                analysis = {}

            innovation = float(analysis.get("innovation", 0))
            feasibility = float(analysis.get("feasibility", 0))
            hackathon_fit = float(analysis.get("hackathon_fit", 0))
            tech_wow = float(analysis.get("technical_wow", 0))
            final_score = (
                innovation * 0.3 + feasibility * 0.3
                + hackathon_fit * 0.2 + tech_wow * 0.2
            )

            validated.append({
                "idea_id": idea["id"],
                "competitors": [
                    {"name": c.get("name", ""), "description": c.get("description", ""),
                     "strengths": c.get("strengths", []), "weaknesses": c.get("weaknesses", [])}
                    for c in analysis.get("competitors", [])
                ],
                "open_source_projects": [
                    {"name": o.get("name", ""), "description": o.get("description", ""),
                     "url": o.get("url", "")}
                    for o in analysis.get("open_source_projects", [])
                ],
                "available_apis": [
                    {"name": a.get("name", ""), "description": a.get("description", ""),
                     "url": a.get("url", "")}
                    for a in analysis.get("available_apis", [])
                ],
                "strengths": analysis.get("strengths", []),
                "weaknesses": analysis.get("weaknesses", []),
                "risks": analysis.get("risks", []),
                "final_score": round(final_score, 1),
                "innovation": round(innovation, 1),
                "feasibility": round(feasibility, 1),
                "hackathon_fit": round(hackathon_fit, 1),
                "technical_wow": round(tech_wow, 1),
            })

            # Update idea scores from validation
            idea["innovation_score"] = round(innovation, 1)
            idea["feasibility_score"] = round(feasibility, 1)
            idea["hackathon_fit_score"] = round(hackathon_fit, 1)
            idea["technical_wow_score"] = round(tech_wow, 1)
            idea["final_score"] = round(final_score, 1)

        return AgentResult(
            success=True,
            output={
                "ideas": ideas,
                "validation_reports": validated,
            },
        )
