"""
Idea Validation Agent

Purpose: Critically evaluate each generated idea for feasibility and innovation.
Reads:   generated_ideas
Writes:  validation_reports
"""

import logging
from typing import Type, Dict, Any, List

from pydantic import BaseModel, Field

from app.agents.base import BaseAgent
from app.schemas.state import WorkflowStage, ValidationReport, Competitor, OpenSourceProject, ApiResource

logger = logging.getLogger(__name__)


class ValidationReportList(BaseModel):
    """Wrapper so LLM returns a list of validation reports as a JSON object."""
    reports: List[ValidationReport] = Field(default_factory=list)


class IdeaValidationAgent(BaseAgent):
    agent_name = "IdeaValidationAgent"
    stage = WorkflowStage.IDEA_VALIDATION

    @property
    def response_schema(self) -> Type[ValidationReportList]:
        return ValidationReportList

    def build_system_prompt(self, state: Dict[str, Any]) -> str:
        return (
            "You are a specialized AI agent.\n\n"
            "ROLE: Critical Idea Validator and Market Analyst\n\n"
            "OBJECTIVE:\n"
            "Critically evaluate each project idea against real-world criteria.\n"
            "You are a skeptic — attempt to break each idea before approving it.\n"
            "Identify competitors, open source alternatives, and APIs that already exist.\n\n"
            "SCORING:\n"
            "- feasibility_score: Can this be built in the hackathon timeframe? (0.0-10.0)\n"
            "- innovation_score: How original and differentiated is this? (0.0-10.0)\n"
            "- final_score: Weighted average. Innovation matters more than feasibility.\n\n"
            "RULES:\n"
            "- Prefer skepticism over optimism.\n"
            "- Produce at least 2 competitors per idea.\n"
            "- Produce at least 2 open source alternatives per idea.\n"
            "- Produce at least 2 relevant APIs per idea.\n"
            "- Return valid JSON only. No markdown. No explanations.\n\n"
            "OUTPUT SCHEMA:\n"
            "{\n"
            '  "reports": [\n'
            "    {\n"
            '      "idea_id": "string",\n'
            '      "competitors": [{"name":"string","description":"string","url":"string"}],\n'
            '      "open_source_projects": [{"name":"string","description":"string","url":"string","stars":0}],\n'
            '      "apis": [{"name":"string","description":"string","url":"string"}],\n'
            '      "strengths": ["string"],\n'
            '      "weaknesses": ["string"],\n'
            '      "risks": ["string"],\n'
            '      "feasibility_score": 0.0,\n'
            '      "innovation_score": 0.0,\n'
            '      "final_score": 0.0\n'
            "    }\n"
            "  ]\n"
            "}"
        )

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        from app.services.research.service import research_service
        ideas = state.get("generated_ideas") or []
        
        try:
            logger.info(f"[{self.agent_name}] Triggering research pipeline for {len(ideas)} ideas.")
            reports = await research_service.run(ideas)
            state["_research_reports"] = {k: v.model_dump() for k, v in reports.items()}
        except Exception as e:
            logger.error(f"[{self.agent_name}] Research pipeline failed: {e}")
            state["_research_reports"] = {}

        result_state = await super().execute(state)

        # Cleanup temp state data
        if "_research_reports" in result_state:
            del result_state["_research_reports"]

        return result_state

    def build_user_prompt(self, state: Dict[str, Any]) -> str:
        ideas = state.get("generated_ideas") or []
        research_reports = state.get("_research_reports") or {}
        ideas_text = ""
        for i, idea in enumerate(ideas, 1):
            idea_id = idea.get("id")
            report = research_reports.get(idea_id) or {}
            
            # Format competitors
            comps = report.get("competitors", [])
            comps_text = "\n".join(
                f"    * Competitor: {c.get('name')} - {c.get('description')} ({c.get('url')})" 
                for c in comps
            ) or "    * None found."
            
            # Format OS projects
            os_projs = report.get("open_source_projects", [])
            os_text = "\n".join(
                f"    * OS Library: {o.get('name')} - {o.get('description')} ({o.get('url')} - Stars: {o.get('stars')})" 
                for o in os_projs
            ) or "    * None found."
            
            # Format APIs
            apis = report.get("apis", [])
            api_text = "\n".join(
                f"    * API: {a.get('name')} - {a.get('description')} ({a.get('url')})" 
                for a in apis
            ) or "    * None found."

            ideas_text += (
                f"\nIDEA {i}:\n"
                f"  id: {idea_id}\n"
                f"  title: {idea.get('title')}\n"
                f"  description: {idea.get('description')}\n"
                f"  key_features: {', '.join(idea.get('key_features', []))}\n"
                f"  target_users: {', '.join(idea.get('target_users', []))}\n"
                f"  EVIDENCE & WEB RESEARCH FINDINGS:\n"
                f"    Competitors:\n{comps_text}\n"
                f"    Open Source Projects:\n{os_text}\n"
                f"    APIs & SDKs:\n{api_text}\n"
            )

        return (
            f"HACKATHON IDEAS TO VALIDATE:\n{ideas_text}\n\n"
            "Critically validate each idea using the web research findings provided. Produce one report per idea. "
            "Ensure the strengths, weaknesses, and risks reflect the real competitors and APIs found. "
            "The 'idea_id' field in each report must match the exact 'id' of the corresponding idea. "
            "Return the JSON object following the schema exactly."
        )

    def apply_result(self, state: Dict[str, Any], result: ValidationReportList) -> Dict[str, Any]:
        state["validation_reports"] = [r.model_dump() for r in result.reports]
        return state

    def mock_result(self, state: Dict[str, Any]) -> ValidationReportList:
        ideas = state.get("generated_ideas") or []
        research_reports = state.get("_research_reports") or {}
        reports = []
        for idea in ideas:
            idea_id = idea.get("id", "unknown")
            title = idea.get("title", "Idea")
            
            report_data = research_reports.get(idea_id) or {}
            
            # Map search findings if available
            comps = [Competitor(**c) for c in report_data.get("competitors", [])]
            os_projs = [OpenSourceProject(**o) for o in report_data.get("open_source_projects", [])]
            apis = [ApiResource(**a) for a in report_data.get("apis", [])]
            
            feas_score = report_data.get("feasibility_score", 8.5)
            inno_score = report_data.get("novelty_score", idea.get("innovation_score", 8.0))
            final_score = report_data.get("final_score", round((feas_score + inno_score) / 2, 2))
            
            if not comps:
                comps = [
                    Competitor(
                        name="LangSmith",
                        description="Observability and monitoring platform for LLM apps",
                        url="https://smith.langchain.com",
                    ),
                    Competitor(
                        name="Helicone",
                        description="Open source LLM monitoring and proxy tool",
                        url="https://helicone.ai",
                    ),
                ]
            if not os_projs:
                os_projs = [
                    OpenSourceProject(
                        name="langgraph",
                        description="LangChain's graph-based agent orchestration library",
                        url="https://github.com/langchain-ai/langgraph",
                        stars=3400,
                    ),
                    OpenSourceProject(
                        name="fastapi",
                        description="High-performance async Python web framework",
                        url="https://github.com/fastapi/fastapi",
                        stars=68000,
                    ),
                ]
            if not apis:
                apis = [
                    ApiResource(
                        name="Groq Cloud API",
                        description="Ultra-fast Llama-3 inference endpoint",
                        url="https://groq.com",
                    ),
                    ApiResource(
                        name="Google Gemini API",
                        description="Multimodal AI inference — flash and pro tiers",
                        url="https://ai.google.dev",
                    ),
                ]

            reports.append(
                ValidationReport(
                    idea_id=idea_id,
                    competitors=comps,
                    open_source_projects=os_projs,
                    apis=apis,
                    strengths=[
                        f"{title} addresses a real, felt pain point for hackathon developers",
                        "Extremely demo-friendly — visible outputs within seconds of starting",
                        "SQLite + local runtime means zero infrastructure setup during judging",
                    ],
                    weaknesses=[
                        "Heavily dependent on external LLM provider reliability",
                        "State serialization adds complexity to async execution model",
                    ],
                    risks=[
                        "LLM rate limits or outages during live judging session",
                        "Concurrent database writes if multiple workflow triggers overlap",
                    ],
                    feasibility_score=feas_score,
                    innovation_score=inno_score,
                    final_score=final_score,
                )
            )
        return ValidationReportList(reports=reports)


# Singleton instance
idea_validation_agent = IdeaValidationAgent()
