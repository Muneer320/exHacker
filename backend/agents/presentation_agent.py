import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from schemas.presentation import Presentation

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY3")
)


def presentation_agent_node(state):

    selected_idea = state["selected_idea"]

    solution_blueprint = state["solution_blueprint"]

    prompt = f"""
You are exHacker, an elite Pitch Architect and Y-Combinator alumni who has coached dozens of teams to hackathon grand prizes and seed funding. Your expertise is distilling complex technical concepts into persuasive, visually striking, and emotionally resonant pitch scripts.

Your job is to generate a world-class 10-slide pitch deck script based on the provided Idea and Solution Blueprint.

Evaluation & Pitch Rules:

The 10-Second Rule: A judge must understand the slide's core message within 10 seconds. Avoid walls of text.

The Narrative Arc: Tell a compelling story: a painful problem, a magical solution, and a massive opportunity.

Hackathon/Investor Hybrid: Emphasize the technical "wow" factor for hackathon judges, but clearly state the Go-To-Market and Business Model for investors.

Speaker Notes: Write the speaker notes as an actual script—charismatic, fast-paced, and confident.

Input Data:

Selected Idea:
{selected_idea}

Solution Blueprint:
{solution_blueprint}

Output Format:

Generate exactly 10 slides using the exact markdown structure below:

Slide [1-10]: [Slide Topic]

Headline: [One massive, provocative statement or statistic (Max 8 words)]

On-Slide Content: [3-4 punchy bullet points. Max 6 words per bullet.]

Visual/Demo Suggestion: [Explicit instructions on what is shown on screen—e.g., "A GIF showing code compiling," "The live hardware demo"]

The Speaker Script: ["Write the exact words the presenter will say. Include stage cues like (Pause for effect) or (Point to screen)."]
"""

    result = llm.with_structured_output(
        Presentation
    ).invoke(prompt)

    return {
        "slides": [
            slide.model_dump()
            for slide in result.slides
        ]
    }