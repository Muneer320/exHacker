from __future__ import annotations

from pydantic import BaseModel, Field


class Slide(BaseModel):
    slide_number: int = 0
    title: str = ""
    objective: str = ""
    content: list[str] = Field(default_factory=list)
    speaker_notes: str = ""
    visual_suggestion: str = ""


class Presentation(BaseModel):
    slides: list[Slide] = Field(default_factory=list)
