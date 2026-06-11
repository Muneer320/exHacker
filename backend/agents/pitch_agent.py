import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from schemas.pitch import PitchPackage

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY1")
)


def pitch_agent_node(state):

    selected_idea = state["selected_idea"]

    slides = state["slides"]

    prompt = f"""
You are an elite startup founder, YC mentor,
TED speaker, investor, and hackathon winner.

Using the selected idea and presentation slides,
create:

1. A 30-second elevator pitch

2. A 2-minute hackathon pitch

3. A 5-minute investor pitch

Requirements:

- Tell a compelling story
- Explain the problem
- Explain the solution
- Explain why now
- Explain market opportunity
- Explain impact
- Be memorable
- Be persuasive
- Sound natural when spoken

Selected Idea:

{selected_idea}

Presentation Slides:

{slides}
"""

    result = llm.with_structured_output(
        PitchPackage
    ).invoke(prompt)

    return {
    "pitch_30s": result.pitch_30s,
    "pitch_2min": result.pitch_2min,
    "pitch_5min": result.pitch_5min
}