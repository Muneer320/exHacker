from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.services.llm.fallback import generate_with_fallback


class ValidationItem(BaseModel):
    idea_id: str = ""
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    feasibility_score: int = 5
    innovation_score: int = 5
    final_score: float = 5.0


class ValidationListOutput(BaseModel):
    validation_reports: list[ValidationItem] = Field(default_factory=list)


def idea_validator_node(state: dict[str, Any]) -> dict[str, Any]:
    ideas = state.get("generated_ideas", [])
    analysis = state.get("problem_analysis", {})

    prompt = f"""You are exHacker, a hyper-critical hackathon judge and project validator.

Evaluate each idea based on:
1. Technical Wow Factor (30%)
2. Demo Impact / Hackathon Fit (30%)
3. Execution Feasibility (20%)
4. Market Potential / Problem Alignment (20%)

Be specific and brutal. Identify real weaknesses and risks.

Problem Analysis: {analysis}

Ideas: {ideas}
"""

    result = generate_with_fallback(prompt, ValidationListOutput)
    if not isinstance(result, ValidationListOutput):
        return {"validation_reports": []}
    return {"validation_reports": [vr.model_dump() for vr in result.validation_reports]}
