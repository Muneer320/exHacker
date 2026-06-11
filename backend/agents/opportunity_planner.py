from __future__ import annotations

from typing import Any

from app.services.llm.fallback import generate_with_fallback
from schemas.state import OpportunityAnalysis


def opportunity_planner_node(state: dict[str, Any]) -> dict[str, Any]:
    analysis = state.get("problem_analysis", {})

    prompt = f"""You are exHacker's Opportunity Planner, an elite product strategist.

Your goal is to dissect the provided Problem Analysis and extract specific, actionable opportunities.

Find:
1. Market gaps - what is underserved
2. Innovation opportunities - where can we break new ground
3. Technical opportunities - what technologies can we leverage
4. Impact opportunities - where can we make the biggest difference

Problem Analysis: {analysis}
"""

    result = generate_with_fallback(prompt, OpportunityAnalysis)
    return {"opportunity_analysis": result.model_dump()}
