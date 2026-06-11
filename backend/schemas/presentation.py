from pydantic import BaseModel


class Slide(BaseModel):
    slide_number: int

    title: str

    objective: str

    content: list[str]

    speaker_notes: str

    visual_suggestion: str


class Presentation(BaseModel):
    slides: list[Slide]