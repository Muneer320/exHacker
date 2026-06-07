import structlog
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.project import Project
from app.services.llm import llm_service

logger = structlog.get_logger()
router = APIRouter(prefix="/debug", tags=["debug"])


@router.get("/costs")
async def get_cost_summary() -> dict[str, object]:
    summary = llm_service.summary()
    return {
        "total_cost": summary["total_cost"],
        "total_tokens": summary["total_tokens"],
        "total_calls": summary["total_calls"],
        "by_provider": summary["by_provider"],
    }


@router.get("/providers")
async def get_providers() -> list[dict[str, str]]:
    providers = llm_service.get_providers()
    return [
        {
            "name": p.name,
            "model": p.config.model,
        }
        for p in providers
    ]


@router.post("/costs/reset")
async def reset_costs() -> dict[str, str]:
    llm_service.reset()
    return {"status": "reset"}


@router.get("/workflow/{project_id}")
async def get_workflow_debug(
    project_id: str,
    session: AsyncSession = Depends(get_session),
) -> dict[str, object]:
    result = await session.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        return {"error": "Project not found"}

    return {
        "project_id": project.id,
        "status": project.status,
        "current_stage": project.current_stage,
        "completed_agents": project.completed_agents,
        "error_count": len(project.error_log or []),
        "has_state": project.state is not None,
    }
