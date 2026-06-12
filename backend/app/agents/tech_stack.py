"""
Tech Stack Advisor Agent

Purpose: Recommend practical, demo-ready technology stack.
Reads:   selected_idea, team_profile, project.duration_hours
Writes:  tech_stack
"""

from typing import Type, Dict, Any

from app.agents.base import BaseAgent
from app.schemas.state import WorkflowStage, TechStack


class TechStackAdvisorAgent(BaseAgent):
    agent_name = "TechStackAdvisorAgent"
    stage = WorkflowStage.TECH_STACK

    @property
    def response_schema(self) -> Type[TechStack]:
        return TechStack

    def build_system_prompt(self, state: Dict[str, Any]) -> str:
        return (
            "You are a specialized AI agent.\n\n"
            "ROLE: Hackathon Technology Stack Advisor\n\n"
            "OBJECTIVE:\n"
            "Recommend a practical, battle-tested technology stack for a hackathon project.\n"
            "The team must be able to:\n"
            "1. Build it within the time limit.\n"
            "2. Deploy it before judging.\n"
            "3. Demo it live without it crashing.\n\n"
            "RULES:\n"
            "- Prefer BORING technologies over cutting-edge ones.\n"
            "- Hackathons reward execution, not novelty.\n"
            "- Align stack with the team's known technologies when possible.\n"
            "- The ai_stack should include at least 2 providers/tools.\n"
            "- Each reasoning entry should be 1 sentence explaining the WHY.\n"
            "- Return valid JSON only. No markdown. No explanations.\n\n"
            "OUTPUT SCHEMA:\n"
            "{\n"
            '  "frontend": "string",\n'
            '  "backend": "string",\n'
            '  "database": "string",\n'
            '  "ai_stack": ["string"],\n'
            '  "deployment": ["string"],\n'
            '  "reasoning": ["string"]\n'
            "}"
        )

    def build_user_prompt(self, state: Dict[str, Any]) -> str:
        idea = state.get("selected_idea") or {}
        team = state.get("team_profile") or {}
        project = state.get("project") or {}

        known_tech = ", ".join(team.get("known_technologies", []) if team else []) or "General purpose"
        preferred_tech = ", ".join(team.get("preferred_technologies", []) if team else []) or "None"
        experience = team.get("experience_level", "Mid-level") if team else "Mid-level"

        return (
            f"SELECTED IDEA: {idea.get('title', 'Unknown')}\n"
            f"DESCRIPTION: {idea.get('description', 'No description.')}\n"
            f"KEY FEATURES: {', '.join(idea.get('key_features', []))}\n\n"
            f"TEAM PROFILE:\n"
            f"  Experience: {experience}\n"
            f"  Known Tech: {known_tech}\n"
            f"  Preferred Tech: {preferred_tech}\n\n"
            f"DURATION: {project.get('duration_hours', 48)} hours\n\n"
            "Recommend a pragmatic, deployable technology stack. "
            "Return the JSON object following the schema exactly."
        )

    def apply_result(self, state: Dict[str, Any], result: TechStack) -> Dict[str, Any]:
        state["tech_stack"] = result.model_dump()
        return state

    def mock_result(self, state: Dict[str, Any]) -> TechStack:
        return TechStack(
            frontend="Next.js 15 (React 19, TypeScript, Tailwind CSS, Lucide React)",
            backend="FastAPI (Python 3.12, Uvicorn, LangGraph, Pydantic v2, SQLAlchemy)",
            database="SQLite (aiosqlite async driver, zero-setup local persistence)",
            ai_stack=[
                "Groq Cloud API — ultra-fast Llama-3.3-70B for primary inference",
                "Google Gemini 1.5 Flash — cost-efficient fallback inference",
                "LangGraph — structured multi-agent workflow orchestration",
            ],
            deployment=[
                "Vercel — frontend static deployment with automatic preview URLs",
                "Railway / Render — FastAPI app server with one-click deploy",
            ],
            reasoning=[
                "Next.js is the industry standard for fast, responsive web UIs with minimal setup.",
                "FastAPI provides type-safe, auto-documented APIs that align perfectly with our Pydantic schemas.",
                "SQLite eliminates infrastructure complexity — no Docker containers or cloud DB credentials needed.",
                "Groq + Gemini fallback ensures 100% uptime during live judging even if one provider rate-limits.",
                "LangGraph enables clean state-machine orchestration with built-in conditional routing.",
            ],
        )


# Singleton instance
tech_stack_advisor_agent = TechStackAdvisorAgent()
