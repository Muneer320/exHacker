from __future__ import annotations

from typing import Any

from app.artifacts.base import ArtifactGenerator


class ImplementationGuideGenerator(ArtifactGenerator):
    @property
    def name(self) -> str:
        return "implementation_guide"

    def generate(self, state: dict[str, Any]) -> str:
        architecture = state.get("architecture", {}) or {}
        build_package = state.get("build_package", {}) or {}
        selected_idea = state.get("selected_idea", {}) or {}

        title = selected_idea.get("title", "Project") if isinstance(selected_idea, dict) else "Project"
        mvp_scope = architecture.get("mvp_scope", []) if isinstance(architecture, dict) else []
        impl_steps = architecture.get("implementation_steps", []) if isinstance(architecture, dict) else []
        frontend_tasks = build_package.get("frontend_tasks", []) if isinstance(build_package, dict) else []
        backend_tasks = build_package.get("backend_tasks", []) if isinstance(build_package, dict) else []

        lines = [
            "# Implementation Guide",
            "",
            f"## {title}",
            "",
            "## MVP Scope",
            "",
        ]

        for item in mvp_scope:
            lines.append(f"- {item}")

        lines.extend(["", "## Implementation Steps", ""])

        for i, step in enumerate(impl_steps, 1):
            lines.append(f"{i}. {step}")

        if frontend_tasks:
            lines.extend(["", "### Frontend Tasks", ""])
            for t in frontend_tasks:
                lines.append(f"- {t}")

        if backend_tasks:
            lines.extend(["", "### Backend Tasks", ""])
            for t in backend_tasks:
                lines.append(f"- {t}")

        return "\n".join(lines)
