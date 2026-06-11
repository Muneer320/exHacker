from __future__ import annotations

import json
from typing import Any

from app.artifacts.base import ArtifactGenerator


class ArchitectureGenerator(ArtifactGenerator):
    @property
    def name(self) -> str:
        return "architecture"

    def generate(self, state: dict[str, Any]) -> str:
        architecture = state.get("architecture", {}) or {}
        tech_stack = state.get("tech_stack", {}) or {}

        system_design = architecture.get("system_design", "") if isinstance(architecture, dict) else ""
        components = architecture.get("components", []) if isinstance(architecture, dict) else []
        api_design = architecture.get("api_design", []) if isinstance(architecture, dict) else []

        lines = [
            "# Architecture Document",
            "",
            "## System Design",
            "",
            system_design or "TBD",
            "",
            "## Components",
            "",
        ]

        for comp in components:
            if isinstance(comp, dict):
                lines.append(f"- **{comp.get('name', '')}**: {comp.get('description', '')} ({comp.get('technology', '')})")
            else:
                lines.append(f"- {comp}")

        lines.extend([
            "",
            "## API Design",
            "",
        ])

        for api in api_design:
            if isinstance(api, dict):
                lines.append(f"### `{api.get('method', 'GET')} {api.get('endpoint', '/')}`")
                lines.append(f"{api.get('description', '')}")
                lines.append("")
            else:
                lines.append(f"- {api}")

        lines.extend([
            "## Tech Stack",
            "",
            "```json",
            json.dumps(tech_stack, indent=2) if tech_stack else "{}",
            "```",
        ])

        return "\n".join(lines)
