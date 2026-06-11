from __future__ import annotations

import json
from typing import Any


def report_generator_node(state: dict[str, Any]) -> dict[str, Any]:
    selected_idea = state.get("selected_idea", {}) or {}
    architecture = state.get("architecture", {}) or {}
    presentation = state.get("presentation", {}) or {}
    pitch = state.get("pitch", {}) or {}

    title = ""
    if isinstance(selected_idea, dict):
        title = selected_idea.get("title", "") or ""
    description = ""
    if isinstance(selected_idea, dict):
        description = selected_idea.get("description", "") or ""

    readme = f"""# {title}

{description}

## Architecture

{json.dumps(architecture, indent=2) if architecture else "Not generated"}

## Presentation

{presentation.get('demo_story', '') if isinstance(presentation, dict) else ''}

## Pitches

{pitch.get('pitch_30s', '') if isinstance(pitch, dict) else ''}
"""

    architecture_doc = f"""# Architecture Document

{json.dumps(architecture, indent=2) if architecture else "Not generated"}
"""

    presentation_doc = f"""# Presentation

{json.dumps(presentation, indent=2) if presentation else "Not generated"}
"""

    pitch_doc = f"""# Pitch Package

{pitch.get('pitch_30s', '') if isinstance(pitch, dict) else ''}

## 2 Minute Pitch
{pitch.get('pitch_2m', '') if isinstance(pitch, dict) else ''}

## 5 Minute Pitch
{pitch.get('pitch_5m', '') if isinstance(pitch, dict) else ''}
"""

    implementation_guide = f"""# Implementation Guide

Selected Idea: {title}

{json.dumps(architecture, indent=2) if architecture else "Not generated"}
"""

    return {
        "exports": {
            "readme": readme,
            "architecture_doc": architecture_doc,
            "presentation_doc": presentation_doc,
            "pitch_doc": pitch_doc,
            "implementation_guide": implementation_guide,
        }
    }
