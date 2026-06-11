from __future__ import annotations

import json
from typing import Any

from app.artifacts.base import ArtifactGenerator


class PRDGenerator(ArtifactGenerator):
    @property
    def name(self) -> str:
        return "prd"

    def generate(self, state: dict[str, Any]) -> str:
        selected_idea = state.get("selected_idea", {}) or {}
        problem_analysis = state.get("problem_analysis", {}) or {}
        architecture = state.get("architecture", {}) or {}

        title = selected_idea.get("title", "Untitled Project") if isinstance(selected_idea, dict) else "Untitled Project"
        description = selected_idea.get("description", "") if isinstance(selected_idea, dict) else ""
        stakeholders = problem_analysis.get("stakeholders", []) if isinstance(problem_analysis, dict) else []
        pain_points = problem_analysis.get("pain_points", []) if isinstance(problem_analysis, dict) else []
        success_metrics = problem_analysis.get("success_metrics", []) if isinstance(problem_analysis, dict) else []

        lines = [
            "# Product Requirements Document",
            "",
            f"## {title}",
            "",
            f"{description}",
            "",
            "## Problem Statement",
            "",
            f"{problem_analysis.get('refined_problem_statement', problem_analysis.get('problem_statement', '')) if isinstance(problem_analysis, dict) else ''}",
            "",
            "## Stakeholders",
            "",
        ]

        for s in stakeholders:
            lines.append(f"- {s}")

        lines.extend(["", "## Pain Points", ""])
        for p in pain_points:
            lines.append(f"- {p}")

        lines.extend(["", "## Success Metrics", ""])
        for m in success_metrics:
            lines.append(f"- {m}")

        lines.extend([
            "",
            "## Architecture",
            "",
            "```json",
            json.dumps(architecture, indent=2) if architecture else "{}",
            "```",
        ])

        return "\n".join(lines)
