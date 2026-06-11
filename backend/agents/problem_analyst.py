from __future__ import annotations

from typing import Any

from app.services.llm.fallback import generate_with_fallback
from schemas.state import ProblemAnalysis


def problem_analyst_node(state: dict[str, Any]) -> dict[str, Any]:
    challenge = state.get("challenge_statement", "")

    prompt = f"""You are the Problem Analysis Agent of exHacker.

Your ONLY responsibility is to deeply analyze the challenge.

Do NOT generate project ideas.
Do NOT generate architecture.
Do NOT recommend technologies.
Do NOT create implementation plans.

Analyze the challenge and extract:
1. Core problem statement
2. Pain points
3. Stakeholders
4. Constraints
5. Assumptions
6. Success metrics
7. Opportunities
8. AI opportunities

Challenge: {challenge}
"""

    result = generate_with_fallback(prompt, ProblemAnalysis)
    return {"problem_analysis": result.model_dump()}
