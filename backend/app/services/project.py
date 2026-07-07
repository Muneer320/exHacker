"""Project service — CRUD + state machine enforcement.
# pyright: reportAttributeAccessIssue=false
# SQLAlchemy Column descriptors resolve at runtime; Pyright false positive.

The state machine governs valid transitions:

    DRAFT ─────→ PROCESSING ─────→ READY ─────→ ARCHIVED
      ↑               │               │
      └───────────────┴───────────────┘
            (return to DRAFT from any active state)

All business logic lives here. API layer is thin.
"""

import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidStateTransitionError, ProjectNotFoundError
from app.models.project import ProjectModel, ProjectStatus

logger = logging.getLogger(__name__)

# ─── State Machine ───────────────────────────────────────────────────────────

_VALID_TRANSITIONS: dict[ProjectStatus, set[ProjectStatus]] = {
    ProjectStatus.DRAFT: {ProjectStatus.PROCESSING, ProjectStatus.ARCHIVED},
    ProjectStatus.PROCESSING: {ProjectStatus.READY, ProjectStatus.DRAFT},
    ProjectStatus.READY: {ProjectStatus.DRAFT, ProjectStatus.ARCHIVED},
    ProjectStatus.ARCHIVED: set(),  # Terminal state — no transitions out
}


def _validate_transition(current: ProjectStatus, target: ProjectStatus) -> None:
    """Validate a state transition. Raises InvalidStateTransitionError if invalid."""
    allowed = _VALID_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise InvalidStateTransitionError(
            message=f"Cannot transition from '{current.value}' to '{target.value}'.",
            detail={
                "current_state": current.value,
                "requested_state": target.value,
                "allowed_transitions": [s.value for s in allowed],
            },
            suggestion=f"Allowed transitions from '{current.value}': {', '.join(s.value for s in allowed)}",
        )


# ─── Service ─────────────────────────────────────────────────────────────────


async def create_project(
    db: AsyncSession,
    idea: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    challenge_statement: Optional[str] = None,
    theme: Optional[str] = None,
    organizer: Optional[str] = None,
    evaluation_criteria: Optional[str] = None,
    rules: Optional[str] = None,
    available_hours: Optional[str] = None,
    team_size: Optional[str] = None,
    team_experience: Optional[str] = None,
    preferred_languages: Optional[str] = None,
    preferred_frameworks: Optional[str] = None,
    target_platform: Optional[str] = None,
    skills: Optional[str] = None,
    excluded_technologies: Optional[str] = None,
    constraints: Optional[str] = None,
) -> ProjectModel:
    """Create a new project in DRAFT state with all Bible §8.1 fields."""
    project = ProjectModel(
        idea=idea,
        name=name or _generate_name(idea),
        description=description,
        status=ProjectStatus.DRAFT.value,
        challenge_statement=challenge_statement,
        theme=theme,
        organizer=organizer,
        evaluation_criteria=evaluation_criteria,
        rules=rules,
        available_hours=available_hours,
        team_size=team_size,
        team_experience=team_experience,
        preferred_languages=preferred_languages,
        preferred_frameworks=preferred_frameworks,
        target_platform=target_platform,
        skills=skills,
        excluded_technologies=excluded_technologies,
        constraints=constraints,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    logger.info("Created project %s in state %s", project.id, project.status)
    return project


async def get_project(db: AsyncSession, project_id: str) -> ProjectModel:
    """Get a single project by ID."""
    result = await db.execute(select(ProjectModel).where(ProjectModel.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise ProjectNotFoundError(detail={"project_id": project_id})
    return project


async def list_projects(db: AsyncSession) -> list[ProjectModel]:
    """List all projects, newest first."""
    result = await db.execute(
        select(ProjectModel).order_by(ProjectModel.created_at.desc())
    )
    return list(result.scalars().all())


async def update_project(
    db: AsyncSession,
    project_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    idea: Optional[str] = None,
    **kwargs,
) -> ProjectModel:
    """Update project metadata fields. Does not change state."""
    project = await get_project(db, project_id)

    if name is not None:
        project.name = name
    if description is not None:
        project.description = description
    if idea is not None:
        project.idea = idea

    # Update any additional fields passed (challenge context, team context, etc.)
    for key, value in kwargs.items():
        if value is not None and hasattr(project, key):
            setattr(project, key, value)

    await db.commit()
    await db.refresh(project)
    logger.info("Updated project %s", project.id)
    return project


async def delete_project(db: AsyncSession, project_id: str) -> None:
    """Hard-delete a project."""
    project = await get_project(db, project_id)
    await db.delete(project)
    await db.commit()
    logger.info("Deleted project %s", project.id)


async def transition_state(
    db: AsyncSession,
    project_id: str,
    target_status: ProjectStatus,
) -> ProjectModel:
    """Transition a project to a new state with validation."""
    project = await get_project(db, project_id)
    current = ProjectStatus(project.status)

    _validate_transition(current, target_status)

    project.status = target_status.value
    await db.commit()
    await db.refresh(project)

    logger.info(
        "Project %s transitioned: %s → %s",
        project.id,
        current.value,
        target_status.value,
    )
    return project


async def get_projects_by_status(
    db: AsyncSession, status: ProjectStatus
) -> list[ProjectModel]:
    """List projects filtered by status."""
    result = await db.execute(
        select(ProjectModel)
        .where(ProjectModel.status == status.value)
        .order_by(ProjectModel.created_at.desc())
    )
    return list(result.scalars().all())


# ─── Helpers ─────────────────────────────────────────────────────────────────


def _generate_name(idea: str) -> str:
    """Generate a project name from the idea text."""
    # Take the first sentence or first 60 chars
    first_sentence = idea.split(".")[0].strip()
    if len(first_sentence) > 60:
        return first_sentence[:57] + "..."
    return first_sentence or "Untitled Project"
