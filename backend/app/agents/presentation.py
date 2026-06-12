"""
Presentation Agent

Purpose: Generate hackathon-winning presentation materials.
Reads:   selected_idea, architecture, validation_reports
Writes:  presentation
"""

from typing import Type, Dict, Any

from app.agents.base import BaseAgent
from app.schemas.state import WorkflowStage, PresentationPackage


class PresentationAgent(BaseAgent):
    agent_name = "PresentationAgent"
    stage = WorkflowStage.PRESENTATION

    @property
    def response_schema(self) -> Type[PresentationPackage]:
        return PresentationPackage

    def build_system_prompt(self, state: Dict[str, Any]) -> str:
        return (
            "You are a specialized AI agent.\n\n"
            "ROLE: Hackathon Presentation Strategist\n\n"
            "OBJECTIVE:\n"
            "Create a complete, judge-ready presentation package for a hackathon project.\n"
            "Focus on storytelling, clarity, and emotional impact.\n"
            "Think: why should the judges care? What is memorable?\n\n"
            "RULES:\n"
            "- slide_order should list exactly 5-7 slide titles.\n"
            "- slide_content must match slide_order (same count).\n"
            "- Each slide must have 3-5 content bullet points.\n"
            "- demo_story should be a 3-sentence narrative arc for the live demo.\n"
            "- business_story should explain the market opportunity in 2-3 sentences.\n"
            "- Return valid JSON only. No markdown. No explanations.\n\n"
            "OUTPUT SCHEMA:\n"
            "{\n"
            '  "slide_order": ["string"],\n'
            '  "slide_content": [\n'
            '    {"title":"string","content":["string"],"visual_notes":"string"}\n'
            "  ],\n"
            '  "demo_story": "string",\n'
            '  "business_story": "string"\n'
            "}"
        )

    def build_user_prompt(self, state: Dict[str, Any]) -> str:
        idea = state.get("selected_idea") or {}
        arch = state.get("architecture") or {}
        reports = state.get("validation_reports") or []

        # Find validation report for selected idea
        selected_report = {}
        if reports and idea.get("id"):
            for r in reports:
                if r.get("idea_id") == idea.get("id"):
                    selected_report = r
                    break

        strengths = "\n".join(f"- {s}" for s in selected_report.get("strengths", []))
        mvp_scope = "\n".join(f"- {s}" for s in arch.get("mvp_scope", []))

        return (
            f"IDEA: {idea.get('title', 'Unknown')}\n"
            f"DESCRIPTION: {idea.get('description', 'No description.')}\n"
            f"KEY FEATURES: {', '.join(idea.get('key_features', []))}\n"
            f"TARGET USERS: {', '.join(idea.get('target_users', []))}\n\n"
            f"VALIDATED STRENGTHS:\n{strengths or 'Not available.'}\n\n"
            f"MVP DELIVERABLES:\n{mvp_scope or 'Not available.'}\n\n"
            "Create a compelling, judge-winning presentation package. "
            "Return the JSON object following the schema exactly."
        )

    def apply_result(self, state: Dict[str, Any], result: PresentationPackage) -> Dict[str, Any]:
        state["presentation"] = result.model_dump()
        return state

    def mock_result(self, state: Dict[str, Any]) -> PresentationPackage:
        idea = state.get("selected_idea") or {}
        title = idea.get("title", "Our Solution")
        features = idea.get("key_features", ["Feature 1", "Feature 2", "Feature 3"])

        return PresentationPackage(
            slide_order=[
                "Slide 1: The Problem",
                "Slide 2: Our Solution",
                "Slide 3: Live Demo",
                "Slide 4: Technical Architecture",
                "Slide 5: Market Opportunity",
                "Slide 6: Team & Execution",
            ],
            slide_content=[
                {
                    "title": "The Problem",
                    "content": [
                        "Hackathon teams lose hours building fragile, one-shot AI pipelines",
                        "Live demos crash due to LLM rate limits at the worst possible moment",
                        "No unified tool to go from 'challenge statement' to 'judging-ready project'",
                        "Teams waste 30-40% of hackathon time on infrastructure, not innovation",
                    ],
                    "visual_notes": "Dark red background, bold warning icon, stark statistics overlay",
                },
                {
                    "title": f"Introducing {title}",
                    "content": [
                        f"A resilient, AI-orchestrated workflow engine purpose-built for hackathons",
                        f"{features[0] if features else 'Multi-provider LLM fallback for 100% uptime'}",
                        f"{features[1] if len(features) > 1 else 'State-persisted workflow execution'}",
                        f"{features[2] if len(features) > 2 else 'Real-time visual progress dashboard'}",
                        "From challenge input to pitch-ready output in under 5 minutes",
                    ],
                    "visual_notes": "Deep purple gradient, glowing dashboard screenshot, animated checkmarks",
                },
                {
                    "title": "Live Demo",
                    "content": [
                        "Watch: paste challenge statement → agents execute sequentially",
                        "Watch: Groq API key pulled → seamless Gemini fallback in milliseconds",
                        "Watch: Select your idea → workflow resumes automatically",
                        "Watch: Architecture, pitch, and build plan generated in one click",
                    ],
                    "visual_notes": "Screen recording showing real-time agent execution on dashboard",
                },
                {
                    "title": "Technical Architecture",
                    "content": [
                        "LangGraph state machine — 10 specialized AI agents in sequence",
                        "FastAPI backend + SQLite persistence — zero infrastructure setup",
                        "Groq primary → Gemini fallback → automatic failover",
                        "Next.js dashboard with live status polling every 2 seconds",
                    ],
                    "visual_notes": "Clean system diagram showing agent flow with arrows and component boxes",
                },
                {
                    "title": "Market Opportunity",
                    "content": [
                        "500,000+ hackathon participants globally every year",
                        "Every team wastes 30-40% of time on workflow setup and debugging",
                        "Entry point: hackathons → expansion: indie builders → enterprise workflow teams",
                        "Monetization: SaaS subscriptions + premium LLM credit bundles",
                    ],
                    "visual_notes": "Market funnel diagram with TAM/SAM/SOM breakdown",
                },
                {
                    "title": "Team & Execution",
                    "content": [
                        "Built in 48 hours using our own tool — dogfooding from day one",
                        "Full-stack implementation: FastAPI, LangGraph, Next.js, SQLite",
                        "Live today: clone the repo, set API key, and run in under 2 minutes",
                    ],
                    "visual_notes": "Team photo + GitHub repo QR code + live URL on screen",
                },
            ],
            demo_story=(
                f"We open the {title} dashboard and paste in our hackathon challenge statement — "
                f"in under 30 seconds, 10 AI agents begin analyzing, generating, and validating ideas. "
                f"We then pull the Groq API key to simulate a failure — the dashboard shows a "
                f"seamless Gemini fallback with zero interruption, before we select our final idea "
                f"and receive a complete pitch package ready for judges."
            ),
            business_story=(
                f"Every hackathon team faces the same infrastructure bottleneck — {title} eliminates it. "
                f"Our beachhead market of 500,000+ annual hackathon participants grows to indie developers "
                f"and enterprise workflow teams who need resilient, observable AI pipelines without the "
                f"LangChain complexity tax."
            ),
        )


# Singleton instance
presentation_agent = PresentationAgent()
