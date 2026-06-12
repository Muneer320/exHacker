"""
Challenge Intelligence Agent

Purpose: Deeply understand the hackathon challenge.
Reads:   project.challenge_statements, project.resources
Writes:  challenge_intelligence
"""

import json
from typing import Type, Dict, Any

from app.agents.base import BaseAgent
from app.schemas.state import WorkflowStage, ChallengeIntelligence


class ChallengeIntelligenceAgent(BaseAgent):
    agent_name = "ChallengeIntelligenceAgent"
    stage = WorkflowStage.CHALLENGE_INTELLIGENCE

    @property
    def response_schema(self) -> Type[ChallengeIntelligence]:
        return ChallengeIntelligence

    def build_system_prompt(self, state: Dict[str, Any]) -> str:
        return (
            "You are a specialized AI agent.\n\n"
            "ROLE: Hackathon Challenge Intelligence Analyst\n\n"
            "OBJECTIVE:\n"
            "Deeply analyze the provided hackathon challenge statement(s).\n"
            "Identify themes, constraints, opportunities, and evaluation criteria.\n"
            "Think strategically — what will judges reward?\n\n"
            "RULES:\n"
            "- Focus on UNDERSTANDING, not solutioning.\n"
            "- Be concrete and specific, not vague.\n"
            "- Produce at least 3 items per field.\n"
            "- Return valid JSON only. No markdown. No explanations.\n\n"
            "OUTPUT SCHEMA:\n"
            "{\n"
            '  "themes": ["string"],\n'
            '  "constraints": ["string"],\n'
            '  "opportunities": ["string"],\n'
            '  "evaluation_factors": ["string"],\n'
            '  "technical_opportunities": ["string"]\n'
            "}"
        )

    def build_user_prompt(self, state: Dict[str, Any]) -> str:
        project = state.get("project", {})
        challenge_stmts = project.get("challenge_statements", [])
        resources = project.get("resources", [])
        duration = project.get("duration_hours", 48)

        challenge_text = "\n".join(
            f"- {stmt}" for stmt in challenge_stmts
        ) or "No challenge statement provided."

        resources_text = (
            "\n".join(f"- {r.get('name', '')} ({r.get('url', '')})" for r in resources)
            if resources
            else "No external resources provided."
        )

        return (
            f"HACKATHON CHALLENGE:\n{challenge_text}\n\n"
            f"AVAILABLE RESOURCES:\n{resources_text}\n\n"
            f"DURATION: {duration} hours\n\n"
            "Analyze this challenge thoroughly. "
            "Return the JSON object following the schema exactly."
        )

    def apply_result(self, state: Dict[str, Any], result: ChallengeIntelligence) -> Dict[str, Any]:
        state["challenge_intelligence"] = result.model_dump()
        return state

    def mock_result(self, state: Dict[str, Any]) -> ChallengeIntelligence:
        project = state.get("project", {})
        challenge = (
            project.get("challenge_statements", ["Build an innovative solution"])[0]
        )
        return ChallengeIntelligence(
            themes=[
                "AI-Driven Automation",
                "Human-in-the-Loop Decision Making",
                f"Innovation in: {challenge[:60]}",
            ],
            constraints=[
                f"{project.get('duration_hours', 48)}-hour development window",
                "Must be demo-ready at judging time",
                "Limited team size and resources",
            ],
            opportunities=[
                "Leverage latest LLM APIs for rapid feature delivery",
                "Use pre-built open source frameworks to reduce boilerplate",
                "Focus on a narrow, high-impact MVP scope",
            ],
            evaluation_factors=[
                "Technical complexity and feasibility",
                "Innovation and originality of the idea",
                "Quality and impressiveness of the live demo",
                "Business viability and real-world impact",
            ],
            technical_opportunities=[
                "Multi-provider LLM fallback for 100% uptime",
                "LangGraph for structured multi-step agent workflows",
                "Real-time status visualization via Next.js",
            ],
        )


# Singleton instance
challenge_intelligence_agent = ChallengeIntelligenceAgent()
