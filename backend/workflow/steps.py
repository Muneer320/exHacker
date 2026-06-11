from __future__ import annotations

from typing import Any

STEPS: list[dict[str, Any]] = [
    {
        "key": "challenge_intelligence",
        "label": "Challenge Intelligence",
        "description": "Understanding the challenge themes, constraints, and opportunities",
        "output_key": "challenge_intelligence",
        "is_select_step": False,
        "symbol": "◈",
    },
    {
        "key": "problem_analyst",
        "label": "Problem Analyst",
        "description": "Deep analysis of the challenge, pain points, and opportunities",
        "output_key": "problem_analysis",
        "is_select_step": False,
        "symbol": "◈",
    },
    {
        "key": "opportunity_planner",
        "label": "Opportunity Planner",
        "description": "Market gaps, AI arbitrage, and monetisation hooks",
        "output_key": "opportunity_analysis",
        "is_select_step": False,
        "symbol": "◉",
    },
    {
        "key": "idea_generator",
        "label": "Idea Generator",
        "description": "Generate competitive hackathon project ideas",
        "output_key": "generated_ideas",
        "is_select_step": False,
        "symbol": "◆",
    },
    {
        "key": "idea_validator",
        "label": "Idea Validator",
        "description": "Validate and score ideas across multiple dimensions",
        "output_key": "validation_reports",
        "is_select_step": False,
        "symbol": "⚖",
    },
    {
        "key": "select_idea",
        "label": "Idea Selection",
        "description": "Choose your winning idea from the validated list",
        "output_key": "selected_idea",
        "is_select_step": True,
        "symbol": "✦",
    },
    {
        "key": "solution_architect",
        "label": "Solution Architect",
        "description": "Complete technical blueprint and implementation roadmap",
        "output_key": "architecture",
        "is_select_step": False,
        "symbol": "◉",
    },
    {
        "key": "presentation_agent",
        "label": "Presentation Agent",
        "description": "Generate presentation deck with speaker notes",
        "output_key": "presentation",
        "is_select_step": False,
        "symbol": "▣",
    },
    {
        "key": "pitch_agent",
        "label": "Pitch Agent",
        "description": "Generate elevator pitch, hackathon pitch, and investor pitch",
        "output_key": "pitch",
        "is_select_step": False,
        "symbol": "◎",
    },
    {
        "key": "report_generator",
        "label": "Report Generator",
        "description": "Generate final execution report and documentation",
        "output_key": "exports",
        "is_select_step": False,
        "symbol": "▤",
    },
]

STEP_KEYS: list[str] = [s["key"] for s in STEPS]


def get_step(key: str | None) -> dict[str, Any] | None:
    if not key:
        return None
    for s in STEPS:
        if s["key"] == key:
            return s
    return None


def get_next_step(current_key: str) -> str | None:
    try:
        idx = STEP_KEYS.index(current_key)
        return STEP_KEYS[idx + 1] if idx + 1 < len(STEP_KEYS) else None
    except ValueError:
        return None
