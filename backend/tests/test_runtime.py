"""HTTP boundaries, approval transactions, and worker lifecycle edges."""

import copy

import pytest
from sqlalchemy import func, select

from app.studio import jobs, routes
from app.studio.ai import StudioError
from app.studio.models import Job, Project
from tests.conftest import create, ready


async def test_readiness_checks_the_isolated_schema(client):
    response = await client.get("/ready")
    assert response.status_code == 200
    assert response.json()["data"]["database"] == "ready"


@pytest.mark.parametrize("chunked", [False, True])
async def test_oversized_requests_are_rejected_before_validation(
    client, isolated_database, chunked
):
    async def body():
        for _ in range(3):
            yield b"x" * 80_000

    response = await client.post(
        "/api/v1/projects", content=body() if chunked else b"x" * 240_000
    )
    assert response.status_code == 413
    assert response.headers["cache-control"] == "private, no-store"
    async with isolated_database() as db:
        assert await db.scalar(select(func.count()).select_from(Project)) == 0


@pytest.mark.parametrize(
    "change", ["duplicate_names", "overbooked", "no_skills", "invalid_hours"]
)
async def test_invalid_team_constraints_do_not_create_projects(
    client, intake, isolated_database, change
):
    data = copy.deepcopy(intake)
    if change == "duplicate_names":
        data["teammates"][1]["name"] = data["teammates"][0]["name"].upper()
    elif change == "overbooked":
        data["teammates"][0]["hours_available"] = 25
    elif change == "no_skills":
        data["teammates"][0]["skills"] = []
    else:
        data["available_hours"] = 0
    assert (await client.post("/api/v1/projects", json=data)).status_code == 422
    async with isolated_database() as db:
        assert await db.scalar(select(func.count()).select_from(Project)) == 0


async def test_only_one_worker_can_claim_a_job(client, intake):
    project = (await client.post("/api/v1/projects", json=intake)).json()["data"]
    first = await jobs.claim_next()
    assert first.project_id == project["id"]
    assert await jobs.claim_next() is None
    await jobs.run_job(first)


async def test_superseded_attempt_cannot_publish_twice(
    client, intake, isolated_database
):
    project = await create(client, intake)
    path = f"/api/v1/projects/{project['id']}"
    async with isolated_database() as db:
        done = await db.scalar(select(Job).where(Job.project_id == project["id"]))
    await jobs.run_job(done)
    saved = (await client.get(path)).json()["data"]
    assert saved["revision"] == project["revision"]
    assert saved["context"] == project["context"]


@pytest.mark.parametrize("approval", ["idea", "stack"])
async def test_approval_and_followup_job_are_one_transaction(
    client, intake, monkeypatch, approval
):
    project = await ready(client, intake)
    path = f"/api/v1/projects/{project['id']}"

    async def unavailable(*_args, **_kwargs):
        raise StudioError("Queue unavailable", 503)

    monkeypatch.setattr(routes, "enqueue", unavailable)
    endpoint = (
        f"{path}/ideas/{project['context']['ideas'][0]['id']}/confirm"
        if approval == "idea"
        else f"{path}/stack/confirm"
    )
    response = await client.post(endpoint, json={"revision": project["revision"]})
    assert response.status_code == 503
    saved = (await client.get(path)).json()["data"]
    assert saved["revision"] == project["revision"]
    assert saved["context"] == project["context"]
