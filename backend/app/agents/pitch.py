"""
Pitch Coach Agent

Purpose: Prepare team for delivering the final pitch to judges.
Reads:   selected_idea, presentation, validation_reports
Writes:  pitch
"""

from typing import Type, Dict, Any

from app.agents.base import BaseAgent
from app.schemas.state import WorkflowStage, PitchPackage


class PitchCoachAgent(BaseAgent):
    agent_name = "PitchCoachAgent"
    stage = WorkflowStage.PITCH

    @property
    def response_schema(self) -> Type[PitchPackage]:
        return PitchPackage

    def build_system_prompt(self, state: Dict[str, Any]) -> str:
        return (
            "You are a specialized AI agent.\n\n"
            "ROLE: Hackathon Pitch Coach\n\n"
            "OBJECTIVE:\n"
            "Prepare the team to deliver a memorable, winning pitch to judges.\n"
            "Focus on COMMUNICATION and PERSUASION — not technical depth.\n"
            "Think: what is the one thing judges will remember after 50 pitches?\n\n"
            "RULES:\n"
            "- pitch_30s should be exactly 50-60 words — timed for 30 seconds.\n"
            "- pitch_2m should be exactly 150-200 words.\n"
            "- pitch_5m should be exactly 400-500 words.\n"
            "- judge_questions must include at least 5 realistic questions with answers.\n"
            "- demo_script should be step-by-step with 5-7 specific actions.\n"
            "- Return valid JSON only. No markdown. No explanations.\n\n"
            "OUTPUT SCHEMA:\n"
            "{\n"
            '  "pitch_30s": "string",\n'
            '  "pitch_2m": "string",\n'
            '  "pitch_5m": "string",\n'
            '  "judge_questions": [{"question":"string","answer":"string"}],\n'
            '  "demo_script": "string"\n'
            "}"
        )

    def build_user_prompt(self, state: Dict[str, Any]) -> str:
        idea = state.get("selected_idea") or {}
        presentation = state.get("presentation") or {}
        reports = state.get("validation_reports") or []

        selected_report = {}
        if reports and idea.get("id"):
            for r in reports:
                if r.get("idea_id") == idea.get("id"):
                    selected_report = r
                    break

        risks = "\n".join(f"- {r}" for r in selected_report.get("risks", []))
        weaknesses = "\n".join(f"- {w}" for w in selected_report.get("weaknesses", []))

        return (
            f"IDEA: {idea.get('title', 'Unknown')}\n"
            f"DESCRIPTION: {idea.get('description', 'No description.')}\n"
            f"KEY FEATURES: {', '.join(idea.get('key_features', []))}\n\n"
            f"DEMO STORY: {presentation.get('demo_story', 'Not available.')}\n"
            f"BUSINESS STORY: {presentation.get('business_story', 'Not available.')}\n\n"
            f"KNOWN RISKS (prepare answers for these):\n{risks or 'None identified.'}\n\n"
            f"KNOWN WEAKNESSES (prepare answers for these):\n{weaknesses or 'None identified.'}\n\n"
            "Create a complete pitch coaching package. "
            "Return the JSON object following the schema exactly."
        )

    def apply_result(self, state: Dict[str, Any], result: PitchPackage) -> Dict[str, Any]:
        state["pitch"] = result.model_dump()
        return state

    def mock_result(self, state: Dict[str, Any]) -> PitchPackage:
        idea = state.get("selected_idea") or {}
        title = idea.get("title", "Our Solution")

        return PitchPackage(
            pitch_30s=(
                f"Meet {title}. We built a resilient, AI-orchestrated workflow engine that takes "
                f"a hackathon challenge and delivers a complete pitch-ready project in under 5 minutes — "
                f"with automatic LLM fallback that guarantees your demo never crashes during judging."
            ),
            pitch_2m=(
                f"Every hackathon team knows the moment: your demo crashes in front of the judges "
                f"because of an API rate limit. We built {title} to make that moment impossible.\n\n"
                f"{title} is a state-persisted, multi-agent AI workflow engine. You paste in your "
                f"challenge statement and 10 specialized AI agents execute in sequence — analyzing your "
                f"challenge, generating ideas, validating them against real market data, and producing a "
                f"complete technical architecture and pitch package.\n\n"
                f"When Groq hits its rate limit, Gemini takes over in milliseconds. Every agent output "
                f"is stored in SQLite — so if anything fails, we resume from exactly where we stopped. "
                f"Our dashboard gives judges a real-time view of every agent executing live.\n\n"
                f"We built {title} using our own tool — in 48 hours. It's live right now."
            ),
            pitch_5m=(
                f"Good afternoon, judges. I want to start with a question: how many hackathon demos have "
                f"you seen crash in the last 24 hours? [Pause for effect.]\n\n"
                f"We built {title} specifically to eliminate that problem forever.\n\n"
                f"THE PROBLEM: Hackathon teams spend 30-40% of their time wrestling with infrastructure. "
                f"They build fragile, one-shot LLM pipelines that die under rate limits. "
                f"They have no visibility into what's happening inside their AI workflows. "
                f"And they spend precious hours setting up boilerplate that adds zero business value.\n\n"
                f"THE SOLUTION: {title} is a state-persisted, multi-agent workflow engine. "
                f"Paste in your challenge statement. 10 specialized AI agents execute in sequence, "
                f"each one reading structured output from the previous. Challenge Intelligence analyzes "
                f"your challenge. Problem Analysis identifies stakeholders and pain points. "
                f"Opportunity Discovery finds market gaps. Idea Generation produces 5 diverse concepts. "
                f"Idea Validation critiques each one against real competitors. Then you choose your "
                f"direction. From there: Tech Stack Advisor, Solution Architect, Build Accelerator, "
                f"Presentation Agent, and Pitch Coach produce everything you need.\n\n"
                f"THE TECHNICAL MOAT: We use LangGraph for clean conditional routing with a "
                f"human-in-the-loop checkpoint. Groq is our primary inference provider — ultra-fast "
                f"Llama-3.3-70B. If Groq rate-limits, Gemini takes over in milliseconds. "
                f"Zero downtime. Every state transition is serialized to SQLite — so we can resume "
                f"from any failure point without losing progress.\n\n"
                f"THE DEMO: [Navigate to dashboard] Watch a real challenge execute live. "
                f"[Point to agent steps] Each card lights up as the agent completes. "
                f"[Pull Groq key] Now watch the fallback. [Show Gemini taking over] Zero interruption. "
                f"[Select idea] The workflow resumes. [Show final output] Here's the complete package.\n\n"
                f"THE MARKET: 500,000+ hackathon participants globally. Our beachhead. "
                f"The expansion path is indie builders, then enterprise workflow teams. "
                f"Any team that orchestrates AI needs what we built.\n\n"
                f"We built {title} using {title} itself — in 48 hours. That's the point. Thank you."
            ),
            judge_questions=[
                {
                    "question": "How does this scale beyond hackathons?",
                    "answer": (
                        "The core engine — state-persisted multi-agent workflows with LLM fallback — "
                        "is domain-agnostic. Hackathons are our beachhead because the pain is acute and "
                        "measurable. Expansion paths include indie developer workflow automation, "
                        "enterprise AI pipeline monitoring, and custom agent marketplaces."
                    ),
                },
                {
                    "question": "What happens if ALL LLM providers fail simultaneously?",
                    "answer": (
                        "The system writes a WORKFLOW_FAILED error to SQLite with the exact failure "
                        "stage and error details. The workflow state is preserved, so teams can either "
                        "retry later or debug the specific agent that failed. In practice, "
                        "Groq + Gemini + OpenAI failing simultaneously has a near-zero probability."
                    ),
                },
                {
                    "question": "How is this different from LangChain or CrewAI?",
                    "answer": (
                        "LangChain and CrewAI require significant engineering to build and configure. "
                        "We are a purpose-built, opinionated workflow for the hackathon context, "
                        "with a UI, database persistence, human checkpoints, and a complete output "
                        "package built in. You don't configure us — you just paste your challenge."
                    ),
                },
                {
                    "question": "Can teams customize the agent workflow?",
                    "answer": (
                        "In the current MVP, the workflow is fixed at 10 stages optimized for hackathons. "
                        "Post-hackathon, we plan a plugin architecture where teams can inject custom "
                        "agents or reorder stages. The LangGraph foundation already supports this."
                    ),
                },
                {
                    "question": "How much does this cost to run?",
                    "answer": (
                        "A full workflow end-to-end costs approximately $0.01-0.03 in LLM tokens "
                        "on Groq's free tier. For a hackathon team, a day of development costs less "
                        "than a coffee. We plan a freemium model with 10 free workflows per month "
                        "and $9/month for unlimited."
                    ),
                },
            ],
            demo_script=(
                f"Step 1: Open the {title} dashboard — show the clean, minimal project creation form.\n"
                f"Step 2: Paste the hackathon challenge statement and click 'Run Workflow'.\n"
                f"Step 3: Point to the live agent progress stepper — explain what each card means.\n"
                f"Step 4: Pull the GROQ_API_KEY from the environment — watch the fallback indicator appear.\n"
                f"Step 5: Show Gemini taking over — zero interruption, workflow continues.\n"
                f"Step 6: Reach the 'Idea Selection' checkpoint — let an audience member choose.\n"
                f"Step 7: Show the complete output package — architecture, pitch, build tasks.\n"
                f"Close: 'This is what we built in 48 hours — using this exact tool.'"
            ),
        )


# Singleton instance
pitch_coach_agent = PitchCoachAgent()
