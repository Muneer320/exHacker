from __future__ import annotations

from typing import Any

from app.services.llm.fallback import generate_with_fallback
from schemas.state import ArchitecturePackage


def solution_architect_node(state: Any) -> dict[str, Any]:
    selected_idea = state.get("selected_idea", {})
    analysis = state.get("problem_analysis", {})
    tech_stack = state.get("tech_stack", {})

    prompt = f"""You are exHacker, an elite Technical Lead and Solution Architect.

Generate a complete solution architecture for the selected idea.

Include:
1. System design overview
2. Components and modules
3. API design
4. Database design
5. Integrations
6. MVP scope
7. Future scope

Selected Idea: {selected_idea}
Problem Analysis: {analysis}
Tech Stack: {tech_stack}
"""

    result = generate_with_fallback(prompt, ArchitecturePackage)
    return {"architecture": result.model_dump()}
