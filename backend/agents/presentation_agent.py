from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.services.llm.fallback import generate_with_fallback


class SingleSlide(BaseModel):
    slide_number: int = 0
    title: str = ""
    objective: str = ""
    content: list[str] = Field(default_factory=list)
    speaker_notes: str = ""
    visual_suggestion: str = ""


class PresentationOutput(BaseModel):
    slide_order: list[str] = Field(default_factory=list)
    slide_content: list[SingleSlide] = Field(default_factory=list)
    demo_story: str = ""
    business_story: str = ""


def presentation_agent_node(state: Any) -> dict[str, Any]:
    selected_idea = state.get("selected_idea", {})
    architecture = state.get("architecture", {})

    prompt = f"""You are exHacker, an elite Pitch Architect.

Generate a world-class presentation deck for the selected idea and architecture.

Include:
1. Slide order with titles
2. Each slide with content, speaker notes, visual suggestions
3. Demo story
4. Business story

Selected Idea: {selected_idea}
Architecture: {architecture}
"""

    result = generate_with_fallback(prompt, PresentationOutput)
    return {"presentation": result.model_dump()}
