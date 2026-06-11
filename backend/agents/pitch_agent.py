from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.services.llm.fallback import generate_with_fallback


class QA(BaseModel):
    question: str = ""
    answer: str = ""


class PitchOutput(BaseModel):
    pitch_30s: str = ""
    pitch_2m: str = ""
    pitch_5m: str = ""
    judge_questions: list[QA] = Field(default_factory=list)
    demo_script: str = ""


def pitch_agent_node(state: Any) -> dict[str, Any]:
    selected_idea = state.get("selected_idea", {})
    presentation = state.get("presentation", {})
    validation_reports = state.get("validation_reports", [])

    prompt = f"""You are an elite startup founder and pitch coach.

Using the selected idea, presentation, and validation results, create:

1. A 30-second elevator pitch
2. A 2-minute hackathon pitch
3. A 5-minute investor pitch
4. Judge Q&A preparation
5. Demo script

Requirements:
- Tell a compelling story
- Explain the problem
- Explain the solution
- Explain why now
- Be memorable

Selected Idea: {selected_idea}
Presentation: {presentation}
Validation: {validation_reports}
"""

    result = generate_with_fallback(prompt, PitchOutput)
    return {"pitch": result.model_dump()}
