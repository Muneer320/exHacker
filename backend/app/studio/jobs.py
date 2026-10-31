"""Database-backed job claiming, leases, recovery, and atomic publication."""

import asyncio
import contextlib
import logging
from datetime import timedelta

from sqlalchemy import or_, select, update

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.studio import inference
from app.studio.errors import CredentialsRequiredError, StudioError
from app.studio.models import Artifact, Job, Message, Project, now

logger = logging.getLogger(__name__)


def serialize_job(job):
    return {
        "id": job.id,
        "kind": job.kind,
        "status": job.status,
        "events": job.events,
        "error": job.error,
        "attempts": job.attempts,
        "inference": inference.public(job.inference or {"source": "operator"}),
        "created_at": job.created_at.isoformat() + "Z",
        "updated_at": job.updated_at.isoformat() + "Z",
    }


async def enqueue(db, project, kind, payload, revision, *, inference_spec=None):
    inference.reject_secrets(payload)
    if revision != project.revision:
        raise StudioError(
            "This project changed in another tab. Reload before submitting.", 409
        )
    if project.active_job:
        raise StudioError(
            "A project operation is already in progress. Wait for it to finish.", 409
        )
    job = Job(
        project_id=project.id,
        kind=kind,
        payload={**payload, "kind": kind},
        input_revision=revision,
        inference=inference_spec,
    )
    db.add(job)
    await db.flush()
    claimed = await db.execute(
        update(Project)
        .where(
            Project.id == project.id,
            Project.active_job.is_(None),
            Project.revision == revision,
        )
        .values(active_job=job.id)
    )
    if claimed.rowcount != 1:
        await db.rollback()
        raise StudioError("Another operation started first. Reload the project.", 409)
    await db.commit()
    return job


async def claim_next():
    async with AsyncSessionLocal() as db:
        eligible = or_(
            Job.status == "queued",
            (Job.status == "running") & (Job.lease_until < now()),
        )
        job = await db.scalar(
            select(Job).where(eligible).order_by(Job.created_at).limit(1)
        )
        if not job:
            return None
        claimed = await db.execute(
            update(Job)
            .where(Job.id == job.id, eligible)
            .values(
                status="running",
                attempts=Job.attempts + 1,
                lease_until=now()
                + timedelta(seconds=settings.STUDIO_JOB_LEASE_SECONDS),
                updated_at=now(),
            )
        )
        if claimed.rowcount != 1:
            await db.rollback()
            return None
        await db.commit()
        await db.refresh(job)
        return job


async def heartbeat(job):
    while True:
        await asyncio.sleep(max(1, settings.STUDIO_JOB_LEASE_SECONDS // 3))
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                update(Job)
                .where(
                    Job.id == job.id,
                    Job.attempts == job.attempts,
                    Job.status == "running",
                )
                .values(
                    lease_until=now()
                    + timedelta(seconds=settings.STUDIO_JOB_LEASE_SECONDS)
                )
            )
            await db.commit()
            if result.rowcount != 1:
                return


async def run_job(job):
    from app.studio.pipeline import execute

    token = None
    job_token = None
    owner = ""
    spec = job.inference or {}

    async def emit(message):
        inference.ensure(owner, spec)
        async with AsyncSessionLocal() as db:
            current = await db.get(Job, job.id)
            if (
                not current
                or current.attempts != job.attempts
                or current.status != "running"
            ):
                raise StudioError(
                    "The job lease has changed; this attempt was superseded.", 409
                )
            current.events = [
                *current.events,
                {"message": message, "at": now().isoformat() + "Z"},
            ][-60:]
            current.updated_at = now()
            await db.commit()

    beat = asyncio.create_task(heartbeat(job))
    try:
        spec = spec or inference.operator_spec()
        async with AsyncSessionLocal() as db:
            project = await db.get(Project, job.project_id)
            if (
                not project
                or project.active_job != job.id
                or project.revision != job.input_revision
            ):
                raise StudioError(
                    "The job belongs to an outdated project revision.", 409
                )
        owner = project.owner
        inference.ensure(owner, spec)
        token = inference.current.set((owner, spec))
        job_token = inference.current_job.set((job.id, job.attempts))
        if job.attempts - spec.get("recovery_base", 0) > 3:
            raise StudioError(
                "This operation was interrupted repeatedly. Review the saved project and retry manually.",
                409,
            )
        await emit(
            "Started operation."
            if job.attempts == 1
            else "Recovering an interrupted operation from its saved inputs."
        )
        result = await execute(project, job.payload, emit)
        inference.ensure(owner, spec)
        inference.reject_secrets(result)
        context, state = result[:2]
        async with AsyncSessionLocal() as db:
            owned = await db.execute(
                update(Job)
                .where(
                    Job.id == job.id,
                    Job.attempts == job.attempts,
                    Job.status == "running",
                )
                .values(status="completed", lease_until=None, updated_at=now())
            )
            published = await db.execute(
                update(Project)
                .where(
                    Project.id == project.id,
                    Project.active_job == job.id,
                    Project.revision == job.input_revision,
                )
                .values(
                    context=context,
                    state=state,
                    revision=Project.revision + 1,
                    active_job=None,
                    updated_at=now(),
                )
            )
            if owned.rowcount != 1 or published.rowcount != 1:
                await db.rollback()
                raise StudioError(
                    "The result was superseded and was not published.", 409
                )
            db.add(
                Artifact(
                    project_id=project.id,
                    revision=project.revision + 1,
                    kind=job.kind,
                    content={
                        "context": context,
                        "input": job.payload,
                        "inference": inference.public(spec),
                    },
                )
            )
            if job.kind == "chat":
                db.add(
                    Message(
                        project_id=project.id,
                        role="user",
                        content=job.payload["message"],
                        context_revision=project.revision,
                    )
                )
                db.add(
                    Message(
                        project_id=project.id,
                        role="assistant",
                        content=result[2],
                        context_revision=project.revision,
                    )
                )
            await db.commit()
    except CredentialsRequiredError as exc:
        async with AsyncSessionLocal() as db:
            await db.execute(
                update(Job)
                .where(
                    Job.id == job.id,
                    Job.attempts == job.attempts,
                    Job.status == "running",
                )
                .values(
                    status="credentials_required",
                    error=str(exc),
                    lease_until=None,
                    updated_at=now(),
                )
            )
            await db.commit()
    except asyncio.CancelledError:
        async with AsyncSessionLocal() as db:
            await db.execute(
                update(Job)
                .where(
                    Job.id == job.id,
                    Job.attempts == job.attempts,
                    Job.status == "running",
                )
                .values(status="queued", lease_until=None, updated_at=now())
            )
            await db.commit()
        raise
    except Exception as exc:
        logger.warning("Studio job %s failed (%s)", job.id, type(exc).__name__)
        message = (
            str(exc)
            if isinstance(exc, StudioError)
            else "The operation failed unexpectedly. Saved project data was preserved. Retry or inspect server logs."
        )
        async with AsyncSessionLocal() as db:
            owned = await db.execute(
                update(Job)
                .where(
                    Job.id == job.id,
                    Job.attempts == job.attempts,
                    Job.status == "running",
                )
                .values(
                    status="failed", error=message, lease_until=None, updated_at=now()
                )
            )
            if owned.rowcount == 1:
                await db.execute(
                    update(Project)
                    .where(Project.id == job.project_id, Project.active_job == job.id)
                    .values(active_job=None, updated_at=now())
                )
            await db.commit()
    finally:
        if job_token is not None:
            inference.current_job.reset(job_token)
        if token is not None:
            inference.current.reset(token)
        beat.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await beat


async def worker():
    while True:
        try:
            job = await claim_next()
            if job:
                await run_job(job)
            else:
                await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.error("Studio worker encountered an error (%s)", type(exc).__name__)
            await asyncio.sleep(2)
