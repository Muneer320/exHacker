from datetime import UTC, datetime
from typing import Any, cast

import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
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
            # Mark project as failed
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
        if proj:
            proj.status = "completed"
            proj.current_stage = str(final_state.current_stage)
            proj.current_agent = None
            proj.completed_agents = final_state.completed_agents
            proj.state = final_state.model_dump(mode="json")

            logs: list[dict[str, Any]] = cast(
                list[dict[str, Any]], final_state.agent_metadata.get("logs", []),
            )
            proj.agent_logs = logs

            proj.error_log = [e.model_dump() for e in final_state.errors]
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
    if project.status != "draft":
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
