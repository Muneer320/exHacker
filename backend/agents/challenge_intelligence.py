from __future__ import annotations

from typing import Any

from app.services.llm.fallback import generate_with_fallback
from schemas.state import ChallengeIntelligence


def challenge_intelligence_node(state: dict[str, Any]) -> dict[str, Any]:
    challenge = state.get("challenge_statement", "")
    resources = state.get("project", {}).get("resources") if isinstance(state.get("project"), dict) else None

    prompt = f"""You are the Challenge Intelligence Agent of exHacker.

Your ONLY responsibility is to deeply understand the challenge.

Identify:
1. Themes - major topics and domains
2. Constraints - limitations and boundaries
3. Opportunities - areas of potential
4. Evaluation factors - what judges will care about
5. Technical opportunities - technology areas to explore

Challenge Statement: {challenge}
Resources: {resources}
"""

    result = generate_with_fallback(prompt, ChallengeIntelligence)
    return {"challenge_intelligence": result.model_dump()}
