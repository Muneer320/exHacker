from __future__ import annotations

from typing import Any


def idea_selector_node(state: dict[str, Any]) -> dict[str, Any]:
    reports = state.get("validation_reports", [])
    ideas = state.get("generated_ideas", [])

    if not reports or not ideas:
        if ideas:
            return {"selected_idea": ideas[0]}
        return {"selected_idea": {}}

    best_report = max(reports, key=lambda r: r.get("final_score", 0) if isinstance(r, dict) else 0)
    best_id = best_report.get("idea_id", "") if isinstance(best_report, dict) else ""

    selected = None
    for idea in ideas:
        iid = idea.get("id", "") if isinstance(idea, dict) else ""
        if iid == best_id:
            selected = idea
            break

    if not selected:
        selected = ideas[0] if ideas else {}

    return {"selected_idea": selected}
