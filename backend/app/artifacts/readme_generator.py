from __future__ import annotations

import json
from typing import Any

from app.artifacts.base import ArtifactGenerator


class ReadmeGenerator(ArtifactGenerator):
    @property
    def name(self) -> str:
        return "readme"

    def generate(self, state: dict[str, Any]) -> str:
        selected_idea = state.get("selected_idea", {}) or {}
        architecture = state.get("architecture", {}) or {}
        tech_stack = state.get("tech_stack", {}) or {}
        challenge = state.get("challenge_statement", "")

        title = ""
        if isinstance(selected_idea, dict):
            title = selected_idea.get("title", "exHacker Project")
        description = ""
        if isinstance(selected_idea, dict):
            description = selected_idea.get("description", "")

        frontend = tech_stack.get("frontend", "TBD") if isinstance(tech_stack, dict) else "TBD"
        backend = tech_stack.get("backend", "TBD") if isinstance(tech_stack, dict) else "TBD"
        database = tech_stack.get("database", "TBD") if isinstance(tech_stack, dict) else "TBD"

        return f"""# {title}

{description}

## Challenge

{challenge}

## Tech Stack

- **Frontend:** {frontend}
- **Backend:** {backend}
- **Database:** {database}

## Architecture Overview

{json.dumps(architecture, indent=2) if architecture else "TBD"}

## Getting Started

1. Clone the repository
2. Install dependencies
3. Set up environment variables
4. Run the application

## Features

- Feature 1
- Feature 2
- Feature 3

## Team

Built with ❤️ during a hackathon.
"""
