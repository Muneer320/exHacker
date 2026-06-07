from pydantic import BaseModel, Field


class Slide(BaseModel):
    title: str
    content: str
    type: str = "slide"


class Diagram(BaseModel):
    title: str
    description: str
    diagram_type: str = "architecture"
    content: str = ""


class PresentationPackage(BaseModel):
    slides: list[Slide] = Field(default_factory=list)
    diagrams: list[Diagram] = Field(default_factory=list)
    demo_story: str = ""
