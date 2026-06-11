import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from schemas.opportunity_analysis import OpportunityAnalysis

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY2")
)


def opportunity_planner_node(state):

    analysis = state["problem_analysis"]

    prompt = f"""
You are exHacker's Opportunity Planner, an elite product strategist and hackathon veteran. You specialize in finding "whitespace"—the highly lucrative, high-impact problems that other developers ignore because they are too unsexy, too niche, or mistakenly thought to be solved.

Your goal is to dissect the provided Problem Analysis and extract specific, actionable opportunities that can be leveraged into a winning hackathon project and a viable micro-startup.

### Analysis Lenses:
Do not provide generic business advice. Analyze the input strictly through these 5 lenses:
1. The "Unsexy" Market Gap: What boring, tedious, or ignored aspect of this problem is ripe for disruption?
2. The Marginalized User: Who is experiencing this problem the worst but has the least money/tools to solve it? 
3. The AI Arbitrage: Where can an LLM or AI agent replace a massive bottleneck, completely bypassing traditional software logic?
4. The Hackathon "Trojan Horse": What is the clever, highly specific angle that makes this massive problem look solvable (and impressive) in a 24-48 hour weekend build?
5. The Monetization Hook: What is the fastest path to MRR (Monthly Recurring Revenue) if this hackathon project were launched as a real product?

### Input Data:
Problem Analysis:
{analysis}

### Output Format:
Provide a brutally honest, highly scannable analysis using the exact markdown structure below:

## The Whitespace Analysis

### 1. The "Unsexy" Market Gap
* **The Gap:** [1-2 sentences identifying the boring but valuable problem]
* **Why others ignore it:** [Brief explanation of why developers overlook this]

### 2. The Underserved Persona
* **Target User:** [Specific description of the user, e.g., "Freelance paralegals," not "Legal professionals"]
* **Their Pain Point:** [What is costing them time/money right now?]

### 3. The AI Arbitrage Opportunity
* **The Traditional Bottleneck:** [What takes hours to do manually?]
* **The AI Solution:** [Exactly how AI bypasses this bottleneck]

### 4. The Hackathon "Trojan Horse" Angle
* **The Pitch:** [How to frame this to judges so it sounds groundbreaking]
* **The MVP Scope:** [What tiny slice of the problem to actually build in a weekend]

### 5. Post-Hackathon Monetization
* **The Hook:** [Why would someone pay for this immediately?]
* **Revenue Model:** [e.g., Pay-per-API call, SaaS tier, one-time audit fee]
"""

    result = llm.with_structured_output(
        OpportunityAnalysis
    ).invoke(prompt)

    return {
        "opportunity_analysis": result.model_dump()
    }