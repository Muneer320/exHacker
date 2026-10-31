"""A failed critique must not throw away successful candidate/search work."""

import copy
from datetime import timedelta

import pytest
from sqlalchemy import func, select, update

from app.core.config import settings
from app.studio import demo, inference, jobs, pipeline
from app.studio.errors import StudioError
from app.studio.models import Artifact, Job, now
from app.studio.schemas import CandidateBatch
from tests.conftest import create, drain


def live_boundaries(monkeypatch, *, fail="critique_1"):
    monkeypatch.setattr(settings, "STUDIO_DEMO_MODE", False)
    monkeypatch.setattr(settings, "STUDIO_IDEA_ROUNDS", 2)
    state = {"initial": 0, "search": [], "critiques": [], "fail": fail, "models": []}

    async def generate(project_id, instruction, context, schema, **kwargs):
        values = demo.ideas(context["intake"])
        if "candidates" not in context:
            state["initial"] += 1
        else:
            round_number = context["round"]
            state["critiques"].append(round_number)
            state["models"].append(inference.current.get()[1]["model"])
            if state["fail"] == f"critique_{round_number}":
                state["fail"] = None
                raise StudioError("Synthetic provider request limit (HTTP 413).", 502)
            for idea in values:
                idea.evidence_ids = ["fixture-source"]
        return CandidateBatch(ideas=values)

    async def search(project_id, queries):
        state["search"].append(queries)
        if state["fail"] == "research":
            state["fail"] = None
            raise StudioError("Synthetic search outage", 502)
        return {
            "sources": [
                {
                    "id": "fixture-source",
                    "title": "Synthetic evidence",
                    "url": "https://github.com/test-fixtures/evidence",
                    "snippet": "Test source",
                }
            ],
            "queries": queries,
            "warnings": [],
        }

    monkeypatch.setattr(pipeline.ai, "generate", generate)
    monkeypatch.setattr(pipeline.research, "search", search)
    return state


async def start(client, path, revision):
    response = await client.post(
        path + "/jobs", json={"revision": revision, "kind": "ideas"}
    )
    assert response.status_code == 202, response.text
    await drain()
    return (await client.get(path + "/jobs")).json()["data"]["jobs"][0]


async def retry(client, path, job, revision):
    response = await client.post(
        path + f"/jobs/{job['id']}/retry", json={"revision": revision}
    )
    assert response.status_code == 202, response.text
    await drain()
    return (await client.get(path + "/jobs")).json()["data"]["jobs"][0]


@pytest.mark.parametrize("failure", ["research", "critique_1", "critique_2"])
async def test_retry_reuses_completed_work_and_preserves_previous_context(
    client, intake, monkeypatch, failure
):
    project = await create(client, intake)
    path = f"/api/v1/projects/{project['id']}"
    state = live_boundaries(monkeypatch, fail=failure)
    failed = await start(client, path, project["revision"])
    assert failed["status"] == "failed"
    assert (await client.get(path)).json()["data"]["context"] == project["context"]
    # A retry can use a different selected provider without paying to explore
    # and research the same saved candidates again.
    monkeypatch.setattr(settings, "AI_MODEL", "gemini/gemini-3.8-flash")
    completed = await retry(client, path, failed, project["revision"])
    assert completed["status"] == "completed", completed
    assert state["initial"] == 1
    assert len(state["search"]) == (3 if failure == "research" else 2)
    assert state["critiques"] == (
        [1, 2, 2]
        if failure == "critique_2"
        else [1, 1, 2]
        if failure == "critique_1"
        else [1, 2]
    )
    assert state["models"][-1] == "gemini-3.8-flash"
    saved = (await client.get(path)).json()["data"]
    assert len(saved["context"]["ideas"]) == 5
    assert saved["context"]["demo"] is False
    assert saved["revision"] == project["revision"] + 1
    assert any("Reusing saved" in event["message"] for event in completed["events"])


@pytest.mark.parametrize("change", ["brief", "expired", "other_project"])
async def test_progress_never_crosses_input_revision_expiry_or_project(
    client, intake, monkeypatch, isolated_database, change
):
    project = await create(client, intake)
    second = await create(client, intake) if change == "other_project" else None
    path = f"/api/v1/projects/{project['id']}"
    state = live_boundaries(monkeypatch)
    failed = await start(client, path, project["revision"])
    assert failed["status"] == "failed"
    if change == "brief":
        edited = copy.deepcopy(project["intake"])
        edited["idea"] += " with a different target audience"
        updated = await client.patch(
            path, json={"revision": project["revision"], "intake": edited}
        )
        assert updated.status_code == 200
        result = await start(client, path, updated.json()["data"]["revision"])
    elif change == "expired":
        async with isolated_database() as db:
            rows = await db.scalars(
                select(Artifact).where(
                    Artifact.project_id == project["id"],
                    Artifact.kind == "idea_progress",
                )
            )
            for row in rows:
                row.created_at = now() - timedelta(hours=25)
            await db.commit()
        result = await retry(client, path, failed, project["revision"])
    else:
        result = await start(
            client, f"/api/v1/projects/{second['id']}", second["revision"]
        )
    assert result["status"] == "completed", result
    assert state["initial"] == 2


async def test_superseded_attempt_cannot_write_progress(
    client, intake, isolated_database
):
    project = (await client.post("/api/v1/projects", json=intake)).json()["data"]
    stale = await jobs.claim_next()
    async with isolated_database() as db:
        await db.execute(
            update(Job).where(Job.id == stale.id).values(attempts=stale.attempts + 1)
        )
        await db.commit()
    token = inference.current_job.set((stale.id, stale.attempts))
    try:
        with pytest.raises(StudioError, match="superseded"):
            await pipeline.checkpoint(
                project["id"], 1, "idea_progress", {"key": "stale"}
            )
    finally:
        inference.current_job.reset(token)
    async with isolated_database() as db:
        assert await db.scalar(select(func.count()).select_from(Artifact)) == 0
