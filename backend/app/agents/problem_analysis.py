"""
Problem Analysis Agent

Purpose: Convert challenge intelligence into a structured problem definition.
Reads:   challenge_intelligence, team_profile
Writes:  problem_analysis
"""

from typing import Type, Dict, Any

from app.agents.base import BaseAgent
from app.schemas.state import WorkflowStage, ProblemAnalysis


class ProblemAnalysisAgent(BaseAgent):
    agent_name = "ProblemAnalysisAgent"
    stage = WorkflowStage.PROBLEM_ANALYSIS

    @property
    def response_schema(self) -> Type[ProblemAnalysis]:
        return ProblemAnalysis

    def build_system_prompt(self, state: Dict[str, Any]) -> str:
        return (
            "You are a specialized AI agent.\n\n"
            "ROLE: Problem Analysis Specialist\n\n"
            "OBJECTIVE:\n"
            "Convert challenge intelligence into a crystal-clear, structured problem definition.\n"
            "Focus on WHO suffers, WHY they suffer, and WHAT outcome matters.\n"
            "Do NOT suggest solutions — only define the problem space.\n\n"
            "RULES:\n"
            "- Be specific and measurable.\n"
            "- Identify real human pain points — not technical issues.\n"
            "- Produce at least 3 items per list field.\n"
            "- The refined_problem_statement must be 1-2 concise sentences.\n"
            "- Return valid JSON only. No markdown. No explanations.\n\n"
            "OUTPUT SCHEMA:\n"
            "{\n"
            '  "stakeholders": ["string"],\n'
            '  "pain_points": ["string"],\n'
            '  "assumptions": ["string"],\n'
            '  "success_metrics": ["string"],\n'
            '  "refined_problem_statement": "string"\n'
            "}"
        )

    def build_user_prompt(self, state: Dict[str, Any]) -> str:
        ci = state.get("challenge_intelligence") or {}
        team = state.get("team_profile") or {}

        themes_text = "\n".join(f"- {t}" for t in ci.get("themes", [])) or "Unknown"
        constraints_text = "\n".join(f"- {c}" for c in ci.get("constraints", [])) or "Unknown"
        opps_text = "\n".join(f"- {o}" for o in ci.get("opportunities", [])) or "Unknown"

        team_text = (
            f"Team Size: {team.get('team_size', 'Unknown')}\n"
            f"Experience Level: {team.get('experience_level', 'Unknown')}\n"
            f"Known Technologies: {', '.join(team.get('known_technologies', []) or ['Unknown'])}"
            if team
            else "No team profile provided."
        )

        return (
            f"CHALLENGE THEMES:\n{themes_text}\n\n"
            f"CONSTRAINTS:\n{constraints_text}\n\n"
            f"OPPORTUNITIES:\n{opps_text}\n\n"
            f"TEAM PROFILE:\n{team_text}\n\n"
            "Based on this, produce a structured problem analysis. "
            "Return the JSON object following the schema exactly."
        )

    def apply_result(self, state: Dict[str, Any], result: ProblemAnalysis) -> Dict[str, Any]:
        state["problem_analysis"] = result.model_dump()
        return state

    def mock_result(self, state: Dict[str, Any]) -> ProblemAnalysis:
        project = state.get("project", {})
        proj_name = project.get("name", "the project")
        return ProblemAnalysis(
            stakeholders=[
                "Hackathon participants and developers",
                "Hackathon judges and evaluators",
                "Product teams and startup founders",
            ],
            pain_points=[
                "High cognitive load when setting up multi-agent AI workflows from scratch",
                "Brittle LLM pipelines crash during high-stakes live demos due to rate limits",
                "No unified dashboard to visualize agent execution progress in real time",
            ],
            assumptions=[
                "Users have valid API credentials for at least one LLM provider",
                "The runtime environment supports Python 3.10+ and Node.js 18+",
                "Internet connectivity is available during workflow execution",
            ],
            success_metrics=[
                "Project generation completes in under 5 minutes end-to-end",
                "Zero demo crashes during live judging via automatic fallback",
                "Judges understand workflow status within 3 seconds of viewing the dashboard",
            ],
            refined_problem_statement=(
                f"Hackathon developers struggle to orchestrate resilient, multi-stage AI "
                f"workflows under extreme time pressure. {proj_name} eliminates this friction "
                f"by providing a fault-tolerant, state-persisted execution engine with a "
                f"real-time visual dashboard."
            ),
        )


# Singleton instance
problem_analysis_agent = ProblemAnalysisAgent()
