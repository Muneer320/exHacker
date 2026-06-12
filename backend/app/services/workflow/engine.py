"""
exHacker Workflow Engine (Agent-Wired)

Orchestrates the full multi-agent workflow via LangGraph.
Each node delegates execution to its corresponding agent class.
Agents include automatic retry + mock fallback via BaseAgent.
"""

import uuid
import datetime
import logging
from typing import TypedDict, List, Optional, Any, Dict

from langgraph.graph import StateGraph, END

from app.schemas.state import WorkflowStatus, WorkflowStage
from app.agents.challenge_intelligence import challenge_intelligence_agent
from app.agents.problem_analysis import problem_analysis_agent
from app.agents.opportunity_discovery import opportunity_discovery_agent
from app.agents.idea_generation import idea_generation_agent
from app.agents.idea_validation import idea_validation_agent
from app.agents.tech_stack import tech_stack_advisor_agent
from app.agents.architecture import solution_architect_agent
from app.agents.build_accelerator import build_accelerator_agent
from app.agents.presentation import presentation_agent
from app.agents.pitch import pitch_coach_agent

logger = logging.getLogger(__name__)


class ExHackerState(TypedDict):
    metadata: Dict[str, Any]
    project: Dict[str, Any]
    team_profile: Optional[Dict[str, Any]]
    challenge_intelligence: Optional[Dict[str, Any]]
    problem_analysis: Optional[Dict[str, Any]]
    opportunity_analysis: Optional[Dict[str, Any]]
    generated_ideas: Optional[List[Dict[str, Any]]]
    validation_reports: Optional[List[Dict[str, Any]]]
    selected_idea: Optional[Dict[str, Any]]
    tech_stack: Optional[Dict[str, Any]]
    architecture: Optional[Dict[str, Any]]
    build_package: Optional[Dict[str, Any]]
    prompt_package: Optional[Dict[str, Any]]
    presentation: Optional[Dict[str, Any]]
    pitch: Optional[Dict[str, Any]]
    exports: Optional[Dict[str, Any]]
    execution: Dict[str, Any]
    errors: List[Dict[str, Any]]
    logs: List[Dict[str, Any]]


def utc_now_str() -> str:
    return datetime.datetime.utcnow().isoformat() + "Z"


# ---------------------------------------------------------------------------
# Node wrappers: update metadata stage, skip if already populated, delegate
# ---------------------------------------------------------------------------

def add_state_log(state: ExHackerState, stage: str, message: str):
    if "logs" not in state or state["logs"] is None:
        state["logs"] = []
    state["logs"].append({
        "stage": stage,
        "message": message,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    })

async def challenge_intelligence_node(state: ExHackerState) -> ExHackerState:
    state["metadata"]["current_stage"] = WorkflowStage.CHALLENGE_INTELLIGENCE.value
    state["metadata"]["status"] = WorkflowStatus.RUNNING.value
    state["metadata"]["updated_at"] = utc_now_str()
    add_state_log(state, "challenge_intelligence", "Challenge Intelligence agent starting requirements analysis...")
    if state.get("challenge_intelligence"):
        add_state_log(state, "challenge_intelligence", "Challenge analysis cached, skipping.")
        return state
    res = await challenge_intelligence_agent.execute(state)
    add_state_log(res, "challenge_intelligence", "Challenge Intelligence analysis complete. Constraints and opportunities extracted.")
    return res


async def problem_analysis_node(state: ExHackerState) -> ExHackerState:
    state["metadata"]["current_stage"] = WorkflowStage.PROBLEM_ANALYSIS.value
    state["metadata"]["updated_at"] = utc_now_str()
    add_state_log(state, "problem_analysis", "Problem Analyst agent mapping stakeholders and pain points...")
    if state.get("problem_analysis"):
        add_state_log(state, "problem_analysis", "Problem analysis cached, skipping.")
        return state
    res = await problem_analysis_agent.execute(state)
    add_state_log(res, "problem_analysis", "Problem analysis complete. Refined problem statement and success metrics defined.")
    return res


async def opportunity_discovery_node(state: ExHackerState) -> ExHackerState:
    state["metadata"]["current_stage"] = WorkflowStage.OPPORTUNITY_DISCOVERY.value
    state["metadata"]["updated_at"] = utc_now_str()
    add_state_log(state, "opportunity_discovery", "Opportunity Planner agent scanning market gaps and existing APIs...")
    if state.get("opportunity_analysis"):
        add_state_log(state, "opportunity_discovery", "Research findings cached, skipping.")
        return state
    res = await opportunity_discovery_agent.execute(state)
    add_state_log(res, "opportunity_discovery", "Research complete. Identified competitors, open-source libraries, and key integrations.")
    return res


async def idea_generation_node(state: ExHackerState) -> ExHackerState:
    state["metadata"]["current_stage"] = WorkflowStage.IDEA_GENERATION.value
    state["metadata"]["updated_at"] = utc_now_str()
    add_state_log(state, "idea_generation", "Idea Generator agent brainstorming 5 distinct project concepts...")
    if state.get("generated_ideas"):
        add_state_log(state, "idea_generation", "Ideas cached, skipping.")
        return state
    res = await idea_generation_agent.execute(state)
    add_state_log(res, "idea_generation", "Idea generation complete. Created 5 distinct concepts tailored to constraints.")
    return res


async def idea_validation_node(state: ExHackerState) -> ExHackerState:
    state["metadata"]["current_stage"] = WorkflowStage.IDEA_VALIDATION.value
    state["metadata"]["updated_at"] = utc_now_str()
    add_state_log(state, "idea_validation", "Idea Validator agent scoring concepts for feasibility and novelty...")
    if state.get("validation_reports"):
        add_state_log(state, "idea_validation", "Validation reports cached, skipping.")
        return state
    res = await idea_validation_agent.execute(state)
    add_state_log(res, "idea_validation", "Validation complete. Ideas scored and ready for human selection.")
    return res


async def pause_for_selection_node(state: ExHackerState) -> ExHackerState:
    """Pauses workflow at human checkpoint — waits for idea selection via API."""
    state["metadata"]["current_stage"] = WorkflowStage.HUMAN_SELECTION.value
    state["metadata"]["status"] = WorkflowStatus.WAITING_FOR_USER.value
    state["metadata"]["updated_at"] = utc_now_str()
    add_state_log(state, "human_selection", "Workflow paused at Idea Selection checkpoint. Awaiting user choice...")
    logger.info("Workflow paused at HUMAN_SELECTION checkpoint.")
    return state


async def tech_stack_node(state: ExHackerState) -> ExHackerState:
    state["metadata"]["current_stage"] = WorkflowStage.TECH_STACK.value
    state["metadata"]["updated_at"] = utc_now_str()
    add_state_log(state, "tech_stack", "Tech Stack Advisor agent designing optimal software stack...")
    if state.get("tech_stack"):
        add_state_log(state, "tech_stack", "Tech stack cached, skipping.")
        return state
    res = await tech_stack_advisor_agent.execute(state)
    add_state_log(res, "tech_stack", "Tech stack recommended. Aligned with team skills and constraints.")
    return res


async def architecture_node(state: ExHackerState) -> ExHackerState:
    state["metadata"]["current_stage"] = WorkflowStage.ARCHITECTURE.value
    state["metadata"]["updated_at"] = utc_now_str()
    add_state_log(state, "architecture", "Solution Architect agent designing system components and database tables...")
    if state.get("architecture"):
        add_state_log(state, "architecture", "Architecture package cached, skipping.")
        return state
    res = await solution_architect_agent.execute(state)
    add_state_log(res, "architecture", "Architecture design complete. Generated component list, API design, and Mermaid data flows.")
    return res


async def build_accelerator_node(state: ExHackerState) -> ExHackerState:
    state["metadata"]["current_stage"] = WorkflowStage.BUILD_ACCELERATOR.value
    state["metadata"]["updated_at"] = utc_now_str()
    add_state_log(state, "build_plan", "Build Accelerator agent compiling roadmap milestones and tasks...")
    if state.get("build_package") and state.get("prompt_package"):
        add_state_log(state, "build_plan", "Build plan cached, skipping.")
        return state
    res = await build_accelerator_agent.execute(state)
    add_state_log(res, "build_plan", "Build plan ready. Compiled milestones, frontend/backend task lists, and developer prompts.")
    return res


async def presentation_node(state: ExHackerState) -> ExHackerState:
    state["metadata"]["current_stage"] = WorkflowStage.PRESENTATION.value
    state["metadata"]["updated_at"] = utc_now_str()
    add_state_log(state, "presentation", "Presentation agent structuring slides and pitch narratives...")
    if state.get("presentation"):
        add_state_log(state, "presentation", "Presentation slides cached, skipping.")
        return state
    res = await presentation_agent.execute(state)
    add_state_log(res, "presentation", "Slide deck structure complete. Structured slide titles, content lists, and visual notes.")
    return res


async def pitch_node(state: ExHackerState) -> ExHackerState:
    state["metadata"]["current_stage"] = WorkflowStage.PITCH.value
    state["metadata"]["updated_at"] = utc_now_str()
    add_state_log(state, "pitch", "Pitch Coach agent writing elevator pitches and Q&A prep...")
    if state.get("pitch"):
        add_state_log(state, "pitch", "Pitch coach plan cached, skipping.")
        return state
    res = await pitch_coach_agent.execute(state)
    add_state_log(res, "pitch", "Pitch prep complete. Elevator pitch scripts and simulated Q&As ready.")
    return res


async def export_node(state: ExHackerState) -> ExHackerState:
    """Final node: assembles export package from completed outputs."""
    state["metadata"]["current_stage"] = WorkflowStage.EXPORT.value
    state["metadata"]["updated_at"] = utc_now_str()
    add_state_log(state, "export", "Export agent compiling downloadable markdown packages...")
    if state.get("exports"):
        add_state_log(state, "export", "Exports cached, skipping.")
        return state

    idea = state.get("selected_idea", {})
    title = idea.get("title", "Selected Solution")
    pitch = state.get("pitch", {})
    presentation = state.get("presentation", {})
    arch = state.get("architecture", {})
    build = state.get("build_package", {})

    state["exports"] = {
        "readme": (
            f"# {title}\n\n"
            f"{idea.get('description', '')}\n\n"
            f"## Key Features\n"
            + "\n".join(f"- {f}" for f in idea.get("key_features", []))
            + "\n\n## Get Started\n\n```bash\nnpm install && npm run dev\n```"
        ),
        "architecture_doc": (
            f"# Architecture — {title}\n\n"
            f"{arch.get('system_design', '')}\n\n"
            f"## MVP Scope\n"
            + "\n".join(f"- {s}" for s in arch.get("mvp_scope", []))
        ),
        "presentation_doc": (
            f"# Presentation Slides — {title}\n\n"
            + "\n".join(
                f"## {slide.get('title', '')}\n"
                + "\n".join(f"- {c}" for c in slide.get("content", []))
                for slide in presentation.get("slide_content", [])
            )
        ),
        "pitch_doc": (
            f"# Pitch Guide — {title}\n\n"
            f"## 30-Second Pitch\n{pitch.get('pitch_30s', '')}\n\n"
            f"## 2-Minute Pitch\n{pitch.get('pitch_2m', '')}\n\n"
            f"## 5-Minute Pitch\n{pitch.get('pitch_5m', '')}\n\n"
            f"## Demo Script\n{pitch.get('demo_script', '')}\n\n"
            f"## Anticipated Judge Questions\n"
            + "\n".join(
                f"**Q: {qa.get('question', '')}**\nA: {qa.get('answer', '')}\n"
                for qa in pitch.get("judge_questions", [])
            )
        ),
        "implementation_guide": (
            f"# Implementation Guide — {title}\n\n"
            f"## Frontend Tasks\n"
            + "\n".join(f"- {t}" for t in build.get("frontend_tasks", []))
            + "\n\n## Backend Tasks\n"
            + "\n".join(f"- {t}" for t in build.get("backend_tasks", []))
            + "\n\n## Database Tasks\n"
            + "\n".join(f"- {t}" for t in build.get("database_tasks", []))
        ),
    }

    state["metadata"]["status"] = WorkflowStatus.COMPLETED.value
    add_state_log(state, "export", "Export packages ready. Workflow completed successfully.")
    logger.info("Workflow COMPLETED. Export package assembled.")
    return state


# ---------------------------------------------------------------------------
# Conditional routing
# ---------------------------------------------------------------------------

def route_after_validation(state: ExHackerState) -> str:
    """Route to tech_stack if idea selected, otherwise pause for human."""
    if state.get("selected_idea") is not None:
        return "tech_stack"
    return "pause_for_selection"


# ---------------------------------------------------------------------------
# Build and compile graph
# ---------------------------------------------------------------------------

def build_workflow_graph() -> StateGraph:
    builder = StateGraph(ExHackerState)

    builder.add_node("challenge_intelligence", challenge_intelligence_node)
    builder.add_node("problem_analysis", problem_analysis_node)
    builder.add_node("opportunity_discovery", opportunity_discovery_node)
    builder.add_node("idea_generation", idea_generation_node)
    builder.add_node("idea_validation", idea_validation_node)
    builder.add_node("pause_for_selection", pause_for_selection_node)
    builder.add_node("tech_stack", tech_stack_node)
    builder.add_node("architecture", architecture_node)
    builder.add_node("build_accelerator", build_accelerator_node)
    builder.add_node("presentation", presentation_node)
    builder.add_node("pitch", pitch_node)
    builder.add_node("export", export_node)

    builder.set_entry_point("challenge_intelligence")
    builder.add_edge("challenge_intelligence", "problem_analysis")
    builder.add_edge("problem_analysis", "opportunity_discovery")
    builder.add_edge("opportunity_discovery", "idea_generation")
    builder.add_edge("idea_generation", "idea_validation")

    builder.add_conditional_edges(
        "idea_validation",
        route_after_validation,
        {
            "tech_stack": "tech_stack",
            "pause_for_selection": "pause_for_selection",
        },
    )

    builder.add_edge("pause_for_selection", END)
    builder.add_edge("tech_stack", "architecture")
    builder.add_edge("architecture", "build_accelerator")
    builder.add_edge("build_accelerator", "presentation")
    builder.add_edge("presentation", "pitch")
    builder.add_edge("pitch", "export")
    builder.add_edge("export", END)

    return builder.compile()


# Compiled graph — singleton
workflow_graph = build_workflow_graph()


# ---------------------------------------------------------------------------
# Execution orchestrator
# ---------------------------------------------------------------------------

async def run_workflow(initial_state: ExHackerState) -> ExHackerState:
    """
    Execute the workflow graph from the given initial state.
    Returns the final state after execution completes or pauses at human checkpoint.
    """
    current_state = initial_state

    async for event in workflow_graph.astream(current_state):
        for node_name, state_update in event.items():
            current_state.update(state_update)
            logger.debug(f"Node '{node_name}' completed. Stage: {current_state['metadata'].get('current_stage')}")

    return current_state


async def run_workflow_background(workflow_id: str):
    """
    Runs graph execution in a new DB session context, committing the state
    and logs incrementally to the database after each agent node finishes.
    """
    from app.db.session import SessionLocal
    from app.models.workflow import WorkflowStateModel
    from sqlalchemy.future import select
    from sqlalchemy.orm.attributes import flag_modified

    logger.info(f"[Background Workflow] Starting worker for workflow {workflow_id}")
    async with SessionLocal() as db:
        result = await db.execute(select(WorkflowStateModel).where(WorkflowStateModel.id == workflow_id))
        wf = result.scalar_one_or_none()
        if not wf:
            logger.error(f"[Background Workflow] Workflow {workflow_id} not found.")
            return

        state = wf.state_json
        current_state = state

        try:
            async for event in workflow_graph.astream(current_state):
                for node_name, state_update in event.items():
                    current_state.update(state_update)
                    stage = current_state["metadata"].get("current_stage")
                    status = current_state["metadata"].get("status")
                    logger.info(f"[Background Workflow] Stage {stage} completed with status {status}")

                    # Incremental database update
                    wf.state_json = current_state
                    wf.current_stage = stage
                    wf.status = status
                    flag_modified(wf, "state_json")
                    db.add(wf)
                    await db.commit()
                    await db.refresh(wf)
                    
        except Exception as e:
            logger.error(f"[Background Workflow] Exception in background graph run: {e}", exc_info=True)
            wf.status = WorkflowStatus.FAILED.value
            wf.current_stage = current_state["metadata"].get("current_stage", WorkflowStage.CHALLENGE_INTELLIGENCE.value)
            
            if "errors" not in current_state or current_state["errors"] is None:
                current_state["errors"] = []
            
            current_state["errors"].append({
                "stage": wf.current_stage,
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "message": f"Background error: {str(e)}",
                "retry_count": 0
            })
            current_state["metadata"]["status"] = WorkflowStatus.FAILED.value
            
            wf.state_json = current_state
            flag_modified(wf, "state_json")
            db.add(wf)
            await db.commit()
