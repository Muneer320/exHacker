from pydantic import BaseModel, Field


class QuestionAnswer(BaseModel):
    question: str
    answer: str


class PitchPackage(BaseModel):
    pitch_30: str = ""
    pitch_120: str = ""
    pitch_300: str = ""
    qa: list[QuestionAnswer] = Field(default_factory=list)
    demo_script: str = ""
