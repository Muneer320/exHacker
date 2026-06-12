"""
Opportunity Discovery Agent

Purpose: Identify market gaps and innovation opportunities.
Reads:   challenge_intelligence, problem_analysis
Writes:  opportunity_analysis
"""

from typing import Type, Dict, Any

from app.agents.base import BaseAgent
from app.schemas.state import WorkflowStage, OpportunityAnalysis


class OpportunityDiscoveryAgent(BaseAgent):
    agent_name = "OpportunityDiscoveryAgent"
    stage = WorkflowStage.OPPORTUNITY_DISCOVERY

    @property
    def response_schema(self) -> Type[OpportunityAnalysis]:
        return OpportunityAnalysis

    def build_system_prompt(self, state: Dict[str, Any]) -> str:
        return (
            "You are a specialized AI agent.\n\n"
            "ROLE: Market Opportunity Intelligence Analyst\n\n"
            "OBJECTIVE:\n"
            "Identify valuable, actionable opportunities from the problem analysis.\n"
            "Focus on WHERE innovation can create outsized impact.\n"
            "Think: market gaps, technical angles, and real-world leverage points.\n\n"
            "RULES:\n"
            "- Focus on OPPORTUNITY DISCOVERY, not implementation.\n"
            "- Be concrete — avoid generic platitudes.\n"
            "- Each field must have at least 3 items.\n"
            "- Return valid JSON only. No markdown. No explanations.\n\n"
            "OUTPUT SCHEMA:\n"
            "{\n"
            '  "market_gaps": ["string"],\n'
            '  "innovation_opportunities": ["string"],\n'
            '  "technical_opportunities": ["string"],\n'
            '  "impact_opportunities": ["string"]\n'
            "}"
        )

    def build_user_prompt(self, state: Dict[str, Any]) -> str:
        ci = state.get("challenge_intelligence") or {}
        pa = state.get("problem_analysis") or {}

        pain_points = "\n".join(f"- {p}" for p in pa.get("pain_points", [])) or "None"
        success_metrics = "\n".join(f"- {m}" for m in pa.get("success_metrics", [])) or "None"
        refined_statement = pa.get("refined_problem_statement", "Unknown problem.")
        tech_opps = "\n".join(f"- {t}" for t in ci.get("technical_opportunities", [])) or "None"

        return (
            f"REFINED PROBLEM STATEMENT:\n{refined_statement}\n\n"
            f"KEY PAIN POINTS:\n{pain_points}\n\n"
            f"SUCCESS METRICS:\n{success_metrics}\n\n"
            f"KNOWN TECHNICAL OPPORTUNITIES:\n{tech_opps}\n\n"
            "Identify opportunities to address this problem space at scale. "
            "Return the JSON object following the schema exactly."
        )

    def apply_result(self, state: Dict[str, Any], result: OpportunityAnalysis) -> Dict[str, Any]:
        state["opportunity_analysis"] = result.model_dump()
        return state

    def mock_result(self, state: Dict[str, Any]) -> OpportunityAnalysis:
        return OpportunityAnalysis(
            market_gaps=[
                "Existing agent frameworks are either too simplistic or too complex for hackathon time constraints",
                "No tool provides a live visual dashboard specifically for multi-agent workflow observability",
                "Most tools lack automatic LLM provider fallback — teams lose time debugging rate limits during demos",
            ],
            innovation_opportunities=[
                "Combine LangGraph orchestration with real-time database state snapshots for full audit trails",
                "Build a Human-in-the-Loop checkpoint UI that lets teams steer AI direction mid-workflow",
                "Create a pitch-ready export package that generates markdown slides automatically",
            ],
            technical_opportunities=[
                "Use Groq's ultra-low latency API as primary inference with Gemini as a hot standby",
                "SQLite + aiosqlite for zero-setup local persistence with async session management",
                "LangGraph conditional edges for clean Human-in-the-Loop pause and resume logic",
            ],
            impact_opportunities=[
                "Reduce hackathon project setup time from hours to under 5 minutes",
                "Demonstrate live AI resilience — automatic fallback during judging is a wow moment",
                "Enable non-technical team members to steer project direction at the idea selection step",
            ],
        )


# Singleton instance
opportunity_discovery_agent = OpportunityDiscoveryAgent()
