"""Private anonymous workspaces, explicit approvals, jobs, and Markdown exports."""

import copy
import io
import zipfile
from datetime import timedelta

from fastapi import APIRouter, Depends, Header, Query, Response
from pydantic import Field
from sqlalchemy import case, delete, func, select, update

from app.core.config import settings
from app.db.session import get_db
from app.studio import inference
from app.studio.ai import StudioError, configuration
from app.studio.auth import owner_key
from app.studio.credentials import leases
from app.studio.jobs import enqueue, serialize_job
from app.studio.models import Artifact, Job, Message, Project, now
from app.studio.pipeline import selected
from app.studio.schemas import (
    ChatRequest,
    EditStackRequest,
    GenerateRequest,
    Intake,
    Revision,
)

router = APIRouter()


async def owned(db, project_id, owner):
    project = await db.scalar(
        select(Project).where(Project.id == project_id, Project.owner == owner)
    )
    if not project:
        raise StudioError("Project not found in this browser's workspace.", 404)
    return project


def serialize(project):
    return {
        "id": project.id,
        "name": project.name,
        "intake": project.intake,
        "revision": project.revision,
        "state": project.state,
        "context": project.context,
        "active_job": project.active_job,
        "ai_cost": round(project.ai_cost, 6),
        "search_count": project.search_count,
        "created_at": project.created_at.isoformat() + "Z",
        "updated_at": project.updated_at.isoformat() + "Z",
    }


def ok(data):
    return {"success": True, "data": data}


async def mutate(db, project, revision, values, kind, content=None, *, commit=True):
    if content is not None:
        inference.reject_secrets(content)
    inference.reject_secrets(values)
    if project.active_job:
        raise StudioError(
            "Wait for the active operation before changing the project.", 409
        )
    result = await db.execute(
        update(Project)
        .where(
            Project.id == project.id,
            Project.revision == revision,
            Project.active_job.is_(None),
        )
        .values(
            **values,
            revision=Project.revision + 1,
            updated_at=now(),
        )
    )
    if result.rowcount != 1:
        await db.rollback()
        raise StudioError(
            "This project changed in another tab. Reload and try again.", 409
        )
    db.add(
        Artifact(
            project_id=project.id,
            revision=revision + 1,
            kind=kind,
            content=content or values,
        )
    )
    if commit:
        await db.commit()
    else:
        await db.flush()
    await db.refresh(project)
    return project


@router.get("/config")
async def get_config():
    return ok(configuration())


@router.post("/projects", status_code=201)
async def create_project(
    payload: Intake,
    owner=Depends(owner_key),
    db=Depends(get_db),
    ai_lease: str = Header(default="", alias="X-AI-Lease"),
):
    routing = inference.capture(owner, ai_lease)
    inference.reject_secrets(payload.model_dump())
    count = await db.scalar(
        select(func.count()).select_from(Project).where(Project.owner == owner)
    )
    recent = await db.scalar(
        select(func.count())
        .select_from(Project)
        .where(Project.owner == owner, Project.created_at >= now() - timedelta(days=1))
    )
    if (
        count >= settings.MAX_PROJECTS_PER_USER
        or recent >= settings.FREE_TIER_PROJECTS_PER_DAY
    ):
        raise StudioError(
            "Workspace project limit reached. Delete an unused project or try again tomorrow.",
            429,
        )
    project = Project(
        owner=owner,
        name=payload.name or payload.idea[:80],
        intake=payload.model_dump(),
        context={},
    )
    db.add(project)
    await db.flush()
    await enqueue(db, project, "ideas", {}, 1, inference_spec=routing)
    await db.refresh(project)
    return ok(serialize(project))


@router.get("/projects")
async def list_projects(owner=Depends(owner_key), db=Depends(get_db)):
    projects = await db.scalars(
        select(Project)
        .where(Project.owner == owner)
        .order_by(Project.updated_at.desc())
        .limit(settings.MAX_PROJECTS_PER_USER)
    )
    return ok({"projects": [serialize(p) for p in projects]})


@router.get("/projects/{project_id}")
async def get_project(project_id: str, owner=Depends(owner_key), db=Depends(get_db)):
    return ok(serialize(await owned(db, project_id, owner)))


class IntakeUpdate(Revision):
    intake: Intake


@router.patch("/projects/{project_id}")
async def update_project(
    project_id: str, payload: IntakeUpdate, owner=Depends(owner_key), db=Depends(get_db)
):
    project = await owned(db, project_id, owner)
    updated = await mutate(
        db,
        project,
        payload.revision,
        {
            "intake": payload.intake.model_dump(),
            "name": payload.intake.name or payload.intake.idea[:80],
            "context": {},
            "state": "intake",
        },
        "intake_changed",
        {
            "previous_context": project.context,
            "previous_intake": project.intake,
            "intake": payload.intake.model_dump(),
        },
    )
    return ok(serialize(updated))


@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: str,
    revision: int = Query(ge=1),
    owner=Depends(owner_key),
    db=Depends(get_db),
):
    project = await owned(db, project_id, owner)
    if project.active_job:
        raise StudioError(
            "Wait for the active operation before deleting this project.", 409
        )
    result = await db.execute(
        delete(Project).where(
            Project.id == project.id,
            Project.revision == revision,
            Project.active_job.is_(None),
        )
    )
    if result.rowcount != 1:
        raise StudioError("The project changed. Reload before deleting.", 409)
    await db.commit()
    return ok(None)


class JobRequest(GenerateRequest):
    kind: str = Field(pattern=r"^(ideas|refine_idea|stack|documents)$")


def check_job(project, kind, payload):
    ctx = project.context
    if kind == "refine_idea":
        if len(payload.get("prompt", "").strip()) < 5:
            raise StudioError(
                "Describe the refinement in at least five characters.", 422
            )
        if not any(i["id"] == payload.get("idea_id") for i in ctx.get("ideas", [])):
            raise StudioError("Choose an idea from this project to refine.", 404)
    if kind == "stack" and not selected(ctx):
        raise StudioError("Confirm an idea before choosing technologies.", 409)
    if kind in ("documents", "chat") and (
        not selected(ctx) or not ctx.get("stack_confirmed")
    ):
        raise StudioError("Confirm the idea and technology stack first.", 409)
    if kind == "chat" and not ctx.get("documents"):
        raise StudioError(
            "Generate the documentation before opening the project assistant.", 409
        )


@router.post("/projects/{project_id}/jobs", status_code=202)
async def start_job(
    project_id: str,
    payload: JobRequest,
    owner=Depends(owner_key),
    db=Depends(get_db),
    ai_lease: str = Header(default="", alias="X-AI-Lease"),
):
    routing = inference.capture(owner, ai_lease)
    project = await owned(db, project_id, owner)
    check_job(project, payload.kind, payload.model_dump())
    job = await enqueue(
        db,
        project,
        payload.kind,
        payload.model_dump(exclude={"revision", "kind"}),
        payload.revision,
        inference_spec=routing,
    )
    return ok(serialize_job(job))


@router.get("/projects/{project_id}/jobs")
async def list_jobs(project_id: str, owner=Depends(owner_key), db=Depends(get_db)):
    await owned(db, project_id, owner)
    jobs = await db.scalars(
        select(Job)
        .where(Job.project_id == project_id)
        .order_by(Job.created_at.desc())
        .limit(30)
    )
    return ok({"jobs": [serialize_job(job) for job in jobs]})


@router.post("/projects/{project_id}/jobs/{job_id}/retry", status_code=202)
async def retry_job(
    project_id: str,
    job_id: str,
    payload: Revision,
    owner=Depends(owner_key),
    db=Depends(get_db),
    ai_lease: str = Header(default="", alias="X-AI-Lease"),
):
    routing = inference.capture(owner, ai_lease)
    project = await owned(db, project_id, owner)
    job = await db.scalar(
        select(Job).where(Job.id == job_id, Job.project_id == project_id)
    )
    if not job or job.status != "failed":
        raise StudioError("Only a failed operation can be retried.", 409)
    if job.input_revision != project.revision:
        raise StudioError(
            "The failed operation used an older revision. Start a new operation with the current project.",
            409,
        )
    check_job(project, job.kind, job.payload)
    return ok(
        serialize_job(
            await enqueue(
                db,
                project,
                job.kind,
                job.payload,
                payload.revision,
                inference_spec=routing,
            )
        )
    )


@router.post("/projects/{project_id}/ideas/{idea_id}/confirm")
async def confirm_idea(
    project_id: str,
    idea_id: str,
    payload: Revision,
    owner=Depends(owner_key),
    db=Depends(get_db),
    ai_lease: str = Header(default="", alias="X-AI-Lease"),
):
    routing = inference.capture(owner, ai_lease)
    project = await owned(db, project_id, owner)
    ctx = copy.deepcopy(project.context)
    if not any(i["id"] == idea_id for i in ctx.get("ideas", [])):
        raise StudioError("Idea not found in this project.", 404)
    ctx.update(
        {
            "selected_idea_id": idea_id,
            "stack": None,
            "stack_confirmed": False,
            "documents": None,
        }
    )
    project = await mutate(
        db,
        project,
        payload.revision,
        {"context": ctx, "state": "idea_selected"},
        "idea_confirmed",
        {"idea_id": idea_id},
        commit=False,
    )
    await enqueue(db, project, "stack", {}, project.revision, inference_spec=routing)
    await db.refresh(project)
    return ok(serialize(project))


@router.put("/projects/{project_id}/stack", status_code=202)
async def edit_stack(
    project_id: str,
    payload: EditStackRequest,
    owner=Depends(owner_key),
    db=Depends(get_db),
    ai_lease: str = Header(default="", alias="X-AI-Lease"),
):
    routing = inference.capture(owner, ai_lease)
    project = await owned(db, project_id, owner)
    check_job(project, "stack", {})
    job = await enqueue(
        db,
        project,
        "stack",
        {"requested_stack": payload.stack.model_dump()},
        payload.revision,
        inference_spec=routing,
    )
    return ok(serialize_job(job))


@router.post("/projects/{project_id}/stack/confirm")
async def confirm_stack(
    project_id: str,
    payload: Revision,
    owner=Depends(owner_key),
    db=Depends(get_db),
    ai_lease: str = Header(default="", alias="X-AI-Lease"),
):
    routing = inference.capture(owner, ai_lease)
    project = await owned(db, project_id, owner)
    ctx = copy.deepcopy(project.context)
    if not selected(ctx) or not ctx.get("stack"):
        raise StudioError(
            "Generate and review a stack for the confirmed idea first.", 409
        )
    ctx.update({"stack_confirmed": True, "documents": None})
    project = await mutate(
        db,
        project,
        payload.revision,
        {"context": ctx, "state": "stack_confirmed"},
        "stack_confirmed",
        {"stack": ctx["stack"]},
        commit=False,
    )
    await enqueue(
        db, project, "documents", {}, project.revision, inference_spec=routing
    )
    await db.refresh(project)
    return ok(serialize(project))


@router.post("/projects/{project_id}/jobs/{job_id}/resume", status_code=202)
async def resume_job(
    project_id: str,
    job_id: str,
    payload: Revision,
    owner=Depends(owner_key),
    db=Depends(get_db),
    ai_lease: str = Header(default="", alias="X-AI-Lease"),
):
    project = await owned(db, project_id, owner)
    job = await db.get(Job, job_id)
    if (
        not job
        or job.project_id != project_id
        or project.active_job != job_id
        or job.status != "credentials_required"
        or payload.revision != project.revision
        or job.input_revision != project.revision
    ):
        raise StudioError(
            "Only the current operation waiting for credentials can be resumed.", 409
        )
    original = job.inference or {}
    if original.get("source") != "byok":
        raise StudioError("This operation does not use a user AI session.", 409)
    entry = leases.get(owner, ai_lease)
    if (entry.provider, entry.model) != (
        original.get("provider"),
        original.get("model"),
    ):
        raise StudioError(
            "Reconnect the original provider and model shown on the operation, or cancel it and start a new one.",
            409,
        )
    result = await db.execute(
        update(Job)
        .where(
            Job.id == job_id,
            Job.status == "credentials_required",
            Job.attempts == job.attempts,
        )
        .values(
            status="queued",
            error=None,
            # Attempt numbers fence stale workers and must never be reused.
            # Explicit resume resets the interruption allowance separately.
            inference={**original, "lease": ai_lease, "recovery_base": job.attempts},
            updated_at=now(),
            events=[
                *job.events,
                {
                    "message": "Resuming from saved inputs; interrupted provider work may be billed again.",
                    "at": now().isoformat() + "Z",
                },
            ][-60:],
        )
    )
    if result.rowcount != 1:
        raise StudioError("The operation changed. Reload before resuming.", 409)
    await db.commit()
    await db.refresh(job)
    return ok(serialize_job(job))


@router.post("/projects/{project_id}/jobs/{job_id}/cancel")
async def cancel_job(
    project_id: str,
    job_id: str,
    payload: Revision,
    owner=Depends(owner_key),
    db=Depends(get_db),
):
    project = await owned(db, project_id, owner)
    if project.active_job != job_id or project.revision != payload.revision:
        raise StudioError("The project changed. Reload before cancelling.", 409)
    result = await db.execute(
        update(Job)
        .where(
            Job.id == job_id,
            Job.project_id == project_id,
            Job.status.in_(["queued", "credentials_required"]),
        )
        .values(status="cancelled", error=None, lease_until=None, updated_at=now())
    )
    if result.rowcount != 1:
        raise StudioError(
            "Remove the active AI session first and wait for the running operation to pause.",
            409,
        )
    released = await db.execute(
        update(Project)
        .where(
            Project.id == project_id,
            Project.active_job == job_id,
            Project.revision == payload.revision,
        )
        .values(active_job=None, updated_at=now())
    )
    if released.rowcount != 1:
        await db.rollback()
        raise StudioError("The project changed. Reload before cancelling.", 409)
    await db.commit()
    return ok(None)


@router.get("/projects/{project_id}/history")
async def history(project_id: str, owner=Depends(owner_key), db=Depends(get_db)):
    await owned(db, project_id, owner)
    rows = await db.scalars(
        select(Artifact)
        .where(Artifact.project_id == project_id, Artifact.kind != "search_cache")
        .order_by(Artifact.created_at.desc())
        .limit(60)
    )
    return ok(
        {
            "artifacts": [
                {
                    "id": a.id,
                    "kind": a.kind,
                    "revision": a.revision,
                    "created_at": a.created_at.isoformat() + "Z",
                }
                for a in rows
            ]
        }
    )


@router.get("/projects/{project_id}/history/{artifact_id}")
async def artifact(
    project_id: str, artifact_id: str, owner=Depends(owner_key), db=Depends(get_db)
):
    await owned(db, project_id, owner)
    row = await db.scalar(
        select(Artifact).where(
            Artifact.project_id == project_id, Artifact.id == artifact_id
        )
    )
    if not row:
        raise StudioError("Artifact not found.", 404)
    return ok({"content": row.content, "revision": row.revision, "kind": row.kind})


@router.get("/projects/{project_id}/chat")
async def get_chat(project_id: str, owner=Depends(owner_key), db=Depends(get_db)):
    await owned(db, project_id, owner)
    rows = await db.scalars(
        select(Message)
        .where(Message.project_id == project_id)
        .order_by(
            Message.context_revision,
            case((Message.role == "user", 0), else_=1),
            Message.created_at,
            Message.id,
        )
    )
    return ok(
        {
            "messages": [
                {
                    "id": m.id,
                    "role": m.role,
                    "content": m.content,
                    "context_revision": m.context_revision,
                    "created_at": m.created_at.isoformat() + "Z",
                }
                for m in rows
            ]
        }
    )


@router.post("/projects/{project_id}/chat", status_code=202)
async def send_chat(
    project_id: str,
    payload: ChatRequest,
    owner=Depends(owner_key),
    db=Depends(get_db),
    ai_lease: str = Header(default="", alias="X-AI-Lease"),
):
    routing = inference.capture(owner, ai_lease)
    project = await owned(db, project_id, owner)
    check_job(project, "chat", {})
    return ok(
        serialize_job(
            await enqueue(
                db,
                project,
                "chat",
                {"message": payload.message},
                payload.revision,
                inference_spec=routing,
            )
        )
    )


def documents(project):
    package = project.context.get("documents")
    if not package or not project.context.get("stack_confirmed"):
        raise StudioError("Generate documentation for the confirmed stack first.", 409)
    return package


@router.get("/projects/{project_id}/documents/{filename}")
async def download_document(
    project_id: str, filename: str, owner=Depends(owner_key), db=Depends(get_db)
):
    project = await owned(db, project_id, owner)
    file = next(
        (f for f in documents(project)["files"] if f["filename"] == filename), None
    )
    if not file:
        raise StudioError("Document not found.", 404)
    return Response(
        file["content"],
        media_type="text/markdown",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "ETag": f'"{file["sha256"]}"',
            "Cache-Control": "private, no-store",
        },
    )


@router.get("/projects/{project_id}/export")
async def export_documents(
    project_id: str, owner=Depends(owner_key), db=Depends(get_db)
):
    project = await owned(db, project_id, owner)
    package = documents(project)
    buffer = io.BytesIO()
    # Fixed timestamps make the same stored revision byte-for-byte reproducible.
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file in package["files"]:
            archive.writestr(
                zipfile.ZipInfo(file["filename"], date_time=(2020, 1, 1, 0, 0, 0)),
                file["content"].encode(),
            )
    return Response(
        buffer.getvalue(),
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="exhacker-{project.id[:8]}-r{package["revision"]}.zip"',
            "Cache-Control": "private, no-store",
        },
    )
