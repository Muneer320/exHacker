from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.services.llm.fallback import generate_with_fallback


class IdeaItem(BaseModel):
    title: str = ""
    description: str = ""
    target_users: list[str] = Field(default_factory=list)
    key_features: list[str] = Field(default_factory=list)
    innovation_score: int = 5


class IdeaListOutput(BaseModel):
    ideas: list[IdeaItem] = Field(default_factory=list)


def idea_generator_node(state: dict[str, Any]) -> dict[str, Any]:
    analysis = state.get("problem_analysis", {})
    opportunities = state.get("opportunity_analysis", {})
    challenge = state.get("challenge_statement", "")

    prompt = f"""You are exHacker, an elite hackathon veteran and Idea Generator Agent.

Generate exactly 5 highly competitive hackathon project ideas.

Constraints:
1. Feasibility: Buildable MVP within 24-48 hours
2. Demo Potential: Highly visual or interactive
3. AI Integration: AI solves core logic
4. "Wow" Factor: Judges will be impressed

Challenge: {challenge}

Problem Analysis: {analysis}

Opportunity Analysis: {opportunities}
"""

    result = generate_with_fallback(prompt, IdeaListOutput)
    if not isinstance(result, IdeaListOutput):
        return {"generated_ideas": []}
    return {"generated_ideas": [idea.model_dump() for idea in result.ideas]}
