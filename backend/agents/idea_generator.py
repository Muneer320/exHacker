import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from schemas.idea import IdeaList

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY3")
)


def idea_generator_node(state):

    analysis = state["problem_analysis"]

    opportunities = state["opportunity_analysis"]

    prompt = f"""
You are exHacker, an elite hackathon veteran and Idea Generator Agent who has won multiple tier-1 hackathons. Your expertise lies in finding the perfect intersection of technical "wow-factor," real-world utility, and 24-to-48-hour feasibility.

Your goal is to generate exactly 10 highly competitive hackathon project ideas based on the provided problem and opportunity analyses. 

### Constraints & Guidelines:
1. Feasibility: Ideas must be buildable for an MVP within 24-48 hours. Explicitly state what should be built vs. what should be mocked/hardcoded for the demo.
2. Demo Potential: The idea must have a highly visual or interactive component. Avoid backend-heavy ideas that are hard to show off in a 2-minute pitch.
3. AI Integration: Use AI to solve the core logic or create a magical user experience, not just as a basic chat wrapper.
4. "Wow" Factor: Each idea must have a specific hook that makes judges sit up and pay attention.

### Input Data:
Problem Analysis:
{analysis}

Opportunity Analysis:
{opportunities}

### Output Format:
Return a valid JSON list of 10 objects with the following keys:
{{
  "name": "Idea Title (Max 5 words)",
  "tagline": "One-sentence hook",
  "category": "e.g., AI, Web3, DevOps, Creator Tools",
  "demo_hook": "The specific interactive moment or visual result that wins the demo",
  "why_now": "Why this is relevant to the hackathon theme/current trends",
  "feasibility_plan": "Short plan (2-3 sentences) of what to build vs. mock"
}}
"""

    result = llm.with_structured_output(
        IdeaList
    ).invoke(prompt)

    return {
        "ideas": [
            idea.model_dump()
            for idea in result.ideas
        ]
    }
    
