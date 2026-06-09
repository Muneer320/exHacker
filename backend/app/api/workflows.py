from datetime import UTC, datetime
from typing import Any, cast

import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from langgraph.types import Command
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.registry import AgentRegistry
from app.db.session import get_session
from app.models.project import Project
from app.schemas.project import ProjectResponse
from app.schemas.state import ExHackerState, WorkflowStage
from app.workflows.orchestrator import AGENT_SEQUENCE, get_orchestrator

logger = structlog.get_logger()
router = APIRouter(prefix="/workflows", tags=["workflows"])


# ─────────────────────────────────────────────────────────────────────────────
# Background task: runs the full workflow and writes results back to DB
# ─────────────────────────────────────────────────────────────────────────────

async def _run_workflow_background(project_id: str) -> None:
    """
    Runs in the background after the HTTP response has been returned.
    Opens its own DB session, executes the full LangGraph workflow, and
    persists progress + final state back to the projects table.
    """
    from app.db.session import AsyncSessionLocal  # local import to avoid circular dep

    logger.info(
        "background_workflow_starting",
        project_id=project_id,
        agent_sequence=AGENT_SEQUENCE,
    )

    async with AsyncSessionLocal() as session:
        # ── Load project ──────────────────────────────────────────────────────
        result = await session.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()
        if not project:
            logger.error("background_workflow_project_not_found", project_id=project_id)
            return

        # ── Build initial workflow state ──────────────────────────────────────
        initial_state = ExHackerState(
            project=ProjectResponse.model_validate(project),
            current_stage=WorkflowStage.INPUT,
        )

        # Log available LLM providers before starting
        from app.services.llm import llm_service
        available = llm_service.get_providers()
        logger.info(
            "available_llm_providers",
            project_id=project_id,
            count=len(available),
            names=[p.name for p in available],
        )

        orchestrator = get_orchestrator()

        # ── Progress callback: called after every agent ───────────────────────
        async def _on_agent_progress(
            proj_id: str,
            current_agent: str,
            completed: list[str],
            agent_logs: list[dict[str, Any]],
            errors: list[dict[str, Any]],
        ) -> None:
            try:
                async with AsyncSessionLocal() as prog_session:
                    prog_result = await prog_session.execute(
                        select(Project).where(Project.id == proj_id)
                    )
                    proj = prog_result.scalar_one_or_none()
                    if proj:
                        proj.current_agent = current_agent or None
                        proj.completed_agents = completed
                        proj.agent_logs = agent_logs
                        proj.error_log = errors
                        await prog_session.commit()
                        logger.info(
                            "progress_persisted",
                            project_id=proj_id,
                            current_agent=current_agent,
                            completed_count=len(completed),
                        )
            except Exception as exc:
                logger.error("progress_persist_error", project_id=proj_id, error=str(exc))

        orchestrator.set_progress_callback(_on_agent_progress)

        # ── Execute the full workflow ──────────────────────────────────────────
        try:
            final_state = await orchestrator.run_workflow(initial_state)
        except Exception as exc:
            logger.exception("background_workflow_failed", project_id=project_id, error=str(exc))
            result2 = await session.execute(select(Project).where(Project.id == project_id))
            proj = result2.scalar_one_or_none()
            if proj:
                proj.status = "failed"
                proj.current_agent = None
                err_entry: dict[str, Any] = {
                    "agent_name": "orchestrator",
                    "timestamp": datetime.now(UTC).isoformat(),
                    "message": str(exc),
                    "severity": "critical",
                }
                existing = list(proj.error_log or [])
                existing.append(err_entry)
                proj.error_log = existing
                await session.commit()
            return

        # ── Persist final state ───────────────────────────────────────────────
        result3 = await session.execute(select(Project).where(Project.id == project_id))
        proj = result3.scalar_one_or_none()
        if not proj:
            return

        thread_id = cast(str, final_state.agent_metadata.get("thread_id", ""))
        is_interrupted = cast(bool, final_state.agent_metadata.get("interrupted", False))

        proj.thread_id = thread_id or None
        proj.current_agent = None
        proj.completed_agents = final_state.completed_agents
        proj.state = cast("dict[str, object]", final_state.model_dump(mode="json"))

        logs = cast(list[dict[str, Any]], final_state.agent_metadata.get("logs", []))
        proj.agent_logs = logs
        proj.error_log = [e.model_dump() for e in final_state.errors]

        if is_interrupted:
            checkpoint_stage = cast(str, final_state.agent_metadata.get("checkpoint_stage", "idea_selection"))
            proj.status = "idea_selection"
            proj.current_stage = checkpoint_stage
            await session.commit()
            logger.info(
                "background_workflow_interrupted",
                project_id=project_id,
                thread_id=thread_id,
                checkpoint=checkpoint_stage,
                completed_agents=final_state.completed_agents,
            )
        else:
            proj.status = "completed"
            proj.current_stage = str(final_state.current_stage)
            await session.commit()
            logger.info(
                "background_workflow_completed",
                project_id=project_id,
                agents_done=final_state.completed_agents,
            )


# ─────────────────────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/{project_id}/start")
async def start_workflow(
    project_id: str,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    """Mark the project as started and kick off the full workflow in the background."""
    result = await session.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )
    if project.status not in ("draft", "idea_selection", "failed"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Project is already in status '{project.status}'. Cannot restart.",
        )

    # Mark as running immediately so the UI reacts
    project.status = "researching"
    project.current_stage = WorkflowStage.INPUT
    project.current_agent = "user_profiler"  # first agent about to run
    project.completed_agents = []
    project.agent_logs = []
    project.error_log = []
    await session.commit()
    await session.refresh(project)

    logger.info(
        "workflow_start_requested",
        project_id=project_id,
        name=project.name,
    )

    # ▶ Actually run the workflow in the background
    background_tasks.add_task(_run_workflow_background, project_id)

    return {"status": "started", "project_id": project_id}


@router.get("/{project_id}/progress")
async def get_workflow_progress(
    project_id: str,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """
    Returns lightweight real-time progress info:
    current agent, completed agents, agent logs, and errors.
    Polled by the frontend every 2 seconds.
    """
    result = await session.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return {
        "project_id": project_id,
        "status": project.status,
        "current_stage": project.current_stage,
        "current_agent": project.current_agent,
        "completed_agents": project.completed_agents or [],
        "agent_logs": project.agent_logs or [],
        "error_log": project.error_log or [],
        "updated_at": project.updated_at.isoformat() if project.updated_at else None,
    }


class SelectIdeaRequest(BaseModel):
    selected_idea_id: str


class ApproveCheckpointRequest(BaseModel):
    approved: bool = True


@router.post("/{project_id}/approve")
async def approve_checkpoint(
    project_id: str,
    body: ApproveCheckpointRequest,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    """Approve any checkpoint (architecture, tech stack, prompts) and resume workflow."""
    result = await session.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.status != "idea_selection":
        raise HTTPException(status_code=409, detail=f"Project is in status '{project.status}', not 'idea_selection'")

    thread_id = project.thread_id
    if not thread_id:
        raise HTTPException(status_code=409, detail="No thread_id found — workflow may not have been started")

    orchestrator = get_orchestrator()
    try:
        config = {"configurable": {"thread_id": thread_id}}
        async for _ in orchestrator.graph.astream(
            Command(resume={"approved": body.approved}),
            config=config,
        ):
            pass

        snapshot = await orchestrator.graph.aget_state(config)
        final_state = ExHackerState.model_validate(snapshot.values)

        project.thread_id = None
        project.current_agent = None
        project.completed_agents = final_state.completed_agents
        project.state = final_state.model_dump(mode="json")

        logs = cast(list[dict[str, Any]], final_state.agent_metadata.get("logs", []))
        project.agent_logs = logs
        project.error_log = [e.model_dump() for e in final_state.errors]

        if snapshot.tasks:
            checkpoint_stage = "idea_selection"
            try:
                if snapshot.tasks[0].interrupts:
                    iv = snapshot.tasks[0].interrupts[0].value
                    if isinstance(iv, dict):
                        checkpoint_stage = iv.get("stage", "idea_selection")
            except Exception:
                pass
            project.status = "idea_selection"
            project.current_stage = checkpoint_stage
            project.thread_id = thread_id
        else:
            project.status = "completed"
            project.current_stage = str(final_state.current_stage)

        await session.flush()
        logger.info("checkpoint_approved", project_id=project_id, current_stage=project.current_stage)
    except Exception as exc:
        logger.exception("checkpoint_approve_failed", project_id=project_id, error=str(exc))
        raise HTTPException(status_code=500, detail=f"Failed to approve checkpoint: {exc}")

    return {"status": "resumed", "project_id": project_id}


@router.post("/{project_id}/select-idea")
async def select_idea(
    project_id: str,
    body: SelectIdeaRequest,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    """Resume workflow after human-in-the-loop idea selection."""
    result = await session.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.status != "idea_selection":
        raise HTTPException(status_code=409, detail=f"Project is in status '{project.status}', not 'idea_selection'")

    thread_id = project.thread_id
    if not thread_id:
        raise HTTPException(status_code=409, detail="No thread_id found — workflow may not have been started")

    orchestrator = get_orchestrator()
    try:
        config = {"configurable": {"thread_id": thread_id}}
        async for _ in orchestrator.graph.astream(
            Command(resume={"selected_idea_id": body.selected_idea_id}),
            config=config,
        ):
            pass

        snapshot = await orchestrator.graph.aget_state(config)
        final_state = ExHackerState.model_validate(snapshot.values)

        project.thread_id = None
        project.current_agent = None
        project.completed_agents = final_state.completed_agents
        project.state = final_state.model_dump(mode="json")

        logs = cast(list[dict[str, Any]], final_state.agent_metadata.get("logs", []))
        project.agent_logs = logs
        project.error_log = [e.model_dump() for e in final_state.errors]

        # Check if interrupted again
        if snapshot.tasks:
            project.status = "idea_selection"
            project.current_stage = "idea_selection"
            project.thread_id = thread_id
        else:
            project.status = "completed"
            project.current_stage = str(final_state.current_stage)

        await session.flush()
        logger.info("workflow_resumed_after_selection", project_id=project_id, idea_id=body.selected_idea_id)
    except Exception as exc:
        logger.exception("workflow_resume_failed", project_id=project_id, error=str(exc))
        raise HTTPException(status_code=500, detail=f"Failed to resume workflow: {exc}")

    return {"status": "resumed", "project_id": project_id}


@router.post("/{project_id}/regenerate-ideas")
async def regenerate_ideas(
    project_id: str,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    """Re-run idea_generator and idea_validator for the project."""
    result = await session.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project.thread_id = None
    project.status = "researching"
    project.current_stage = "idea_generation"

    raw_state = (project.state or {})
    raw_state["project"] = ProjectResponse.model_validate(project).model_dump(mode="json")
    state = ExHackerState.model_validate(raw_state)

    orchestrator = get_orchestrator()
    try:
        state = await orchestrator.run_agent_single(state, "idea_generator")
        state = await orchestrator.run_agent_single(state, "idea_validator")

        project.current_agent = None
        project.completed_agents = state.completed_agents
        project.state = state.model_dump(mode="json")

        logs = cast(list[dict[str, Any]], state.agent_metadata.get("logs", []))
        project.agent_logs = logs
        project.error_log = [e.model_dump() for e in state.errors]

        ideas = state.generated_ideas or []
        if ideas:
            project.status = "idea_selection"
            project.current_stage = "idea_selection"
        else:
            project.status = "completed"
            project.current_stage = str(state.current_stage)

        await session.flush()
        logger.info("ideas_regenerated", project_id=project_id, count=len(ideas))
    except Exception as exc:
        logger.exception("regenerate_ideas_failed", project_id=project_id, error=str(exc))
        raise HTTPException(status_code=500, detail=f"Failed to regenerate ideas: {exc}")

    return {"status": "regenerated", "project_id": project_id}


@router.post("/{project_id}/run-agent/{agent_name}")
async def run_single_agent(
    project_id: str,
    agent_name: str,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    """Run a single named agent against the current project state (debug/manual mode)."""
    result = await session.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    agent = AgentRegistry.get(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")

    orchestrator = get_orchestrator()
    state = ExHackerState(
        project=ProjectResponse.model_validate(project),
    )
    updated = await orchestrator.run_agent_single(state, agent_name)

    project.state = updated.model_dump(mode="json")
    project.completed_agents = updated.completed_agents
    project.current_stage = str(updated.current_stage)
    project.error_log = [e.model_dump() for e in updated.errors]

    await session.flush()
    logger.info("manual_agent_run_completed", project_id=project_id, agent=agent_name)
    return {"status": "completed", "agent": agent_name}


@router.get("/{project_id}/state", response_model=ExHackerState)
async def get_workflow_state(
    project_id: str,
    session: AsyncSession = Depends(get_session),
) -> ExHackerState:
    result = await session.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    stage = WorkflowStage.INPUT
    if project.current_stage:
        try:
            stage = WorkflowStage(project.current_stage)
        except ValueError:
            stage = WorkflowStage.INPUT

    return ExHackerState(
        project=ProjectResponse.model_validate(project),
        current_stage=stage,
    )
