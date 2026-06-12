"""
Idea Validation Agent

Purpose: Critically evaluate each generated idea for feasibility and innovation.
Reads:   generated_ideas
Writes:  validation_reports
"""

from typing import Type, Dict, Any, List

from pydantic import BaseModel, Field

from app.agents.base import BaseAgent
from app.schemas.state import WorkflowStage, ValidationReport, Competitor, OpenSourceProject, ApiResource


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

    def build_user_prompt(self, state: Dict[str, Any]) -> str:
        ideas = state.get("generated_ideas") or []
        ideas_text = ""
        for i, idea in enumerate(ideas, 1):
            ideas_text += (
                f"\nIDEA {i}:\n"
                f"  id: {idea.get('id')}\n"
                f"  title: {idea.get('title')}\n"
                f"  description: {idea.get('description')}\n"
                f"  key_features: {', '.join(idea.get('key_features', []))}\n"
                f"  target_users: {', '.join(idea.get('target_users', []))}\n"
            )

        return (
            f"HACKATHON IDEAS TO VALIDATE:\n{ideas_text}\n\n"
            "Critically validate each idea. Produce one report per idea. "
            "The 'idea_id' field in each report must match the exact 'id' of the corresponding idea. "
            "Return the JSON object following the schema exactly."
        )

    def apply_result(self, state: Dict[str, Any], result: ValidationReportList) -> Dict[str, Any]:
        state["validation_reports"] = [r.model_dump() for r in result.reports]
        return state

    def mock_result(self, state: Dict[str, Any]) -> ValidationReportList:
        ideas = state.get("generated_ideas") or []
        reports = []
        for idea in ideas:
            idea_id = idea.get("id", "unknown")
            title = idea.get("title", "Idea")
            inno_score = idea.get("innovation_score", 8.0)
            feas_score = 8.5
            reports.append(
                ValidationReport(
                    idea_id=idea_id,
                    competitors=[
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
                    ],
                    open_source_projects=[
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
                    ],
                    apis=[
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
                    ],
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
                    final_score=round((feas_score + inno_score) / 2, 2),
                )
            )
        return ValidationReportList(reports=reports)


# Singleton instance
idea_validation_agent = IdeaValidationAgent()
