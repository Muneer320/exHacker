import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.registry import AgentRegistry
from app.db.session import get_session
from app.models.project import Project
from app.schemas.project import ProjectResponse
from app.schemas.state import ExHackerState, WorkflowStage
from app.workflows.orchestrator import WorkflowOrchestrator

logger = structlog.get_logger()
router = APIRouter(prefix="/workflows", tags=["workflows"])

_orchestrator: WorkflowOrchestrator | None = None


def get_orchestrator() -> WorkflowOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = WorkflowOrchestrator()
    return _orchestrator


@router.post("/{project_id}/start")
async def start_workflow(
    project_id: str,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    result = await session.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )

    project.status = "researching"
    project.current_stage = WorkflowStage.CHALLENGE_INTELLIGENCE
    await session.flush()
    await session.refresh(project)

    logger.info("workflow_started", project_id=project_id)
    return {"status": "started", "project_id": project_id}


@router.post("/{project_id}/run-agent/{agent_name}")
async def run_single_agent(
    project_id: str,
    agent_name: str,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    result = await session.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    agent = AgentRegistry.get(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_name} not found")

    orchestrator = get_orchestrator()
    state = ExHackerState(
        project=ProjectResponse.model_validate(project),
    )
    updated = await orchestrator.run_agent_single(state, agent_name)

    project.state = updated.model_dump()
    project.completed_agents = updated.completed_agents
    project.error_log = [e.model_dump() for e in updated.errors]
    if updated.current_stage:
        project.current_stage = updated.current_stage

    await session.flush()
    logger.info("agent_run_completed", project_id=project_id, agent=agent_name)
    return {"status": "completed", "agent": agent_name}


@router.get("/{project_id}/state", response_model=ExHackerState)
async def get_workflow_state(
    project_id: str,
    session: AsyncSession = Depends(get_session),
) -> ExHackerState:
    result = await session.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    stage = WorkflowStage.INPUT
    if project.current_stage:
        stage = WorkflowStage(project.current_stage)
    return ExHackerState(
        project=ProjectResponse.model_validate(project),
        current_stage=stage,
    )
