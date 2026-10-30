"""Exercise ownership, durable jobs and disclosure boundaries with synthetic keys."""

import asyncio
import json
import logging

import httpx
import pytest
from sqlalchemy import select

from app.core.config import settings
from app.core.logging import PrivateFormatter, StructuredFormatter
from app.studio import ai, inference, jobs, pipeline
from app.studio.credentials import leases
from app.studio.models import Artifact, Job, Message, Project
from app.studio.providers import CATALOG
from tests.conftest import drain
from tests.provider_fixtures import respond
from tests.test_transport import mock_clients

KEY = "synthetic-credential-never-real"


async def connect(client, provider="openai", key=KEY):
    model = CATALOG[provider]["models"][0]["id"]
    response = await client.post(
        "/api/v1/ai/leases", json={"provider": provider, "model": model, "key": key}
    )
    assert response.status_code == 201, response.text
    assert key not in response.text
    metadata = response.json()["data"]
    client.headers["X-AI-Lease"] = metadata["id"]
    return metadata


def live(monkeypatch):
    monkeypatch.setattr(settings, "STUDIO_DEMO_MODE", False)
    monkeypatch.setattr(settings, "AI_ACCESS_MODE", "byok")


async def assert_database_has_no_key(factory, keys=(KEY,)):
    async with factory() as db:
        for model in (Project, Job, Artifact, Message):
            rows = await db.scalars(select(model))
            for row in rows:
                text = json.dumps(
                    {c.name: getattr(row, c.name) for c in model.__table__.columns},
                    default=str,
                )
                for key in keys:
                    assert key not in text


async def test_lease_api_isolation_validation_and_revoke(client, monkeypatch):
    live(monkeypatch)
    metadata = await connect(client)
    path = "/api/v1/ai/leases/" + metadata["id"]
    response = await client.post(path + "/renew")
    assert response.status_code == 200
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=__import__("app.main", fromlist=["app"]).app),
        base_url="http://test",
        headers={"Authorization": "Bearer " + "b" * 64},
    ) as other:
        assert (await other.get(path)).status_code == 428
        assert (await other.delete(path)).status_code == 428
        assert (
            await other.post("/api/v1/projects", json={"idea": "secret"})
        ).status_code != 201
    bad = await client.post("/api/v1/ai/leases", json={KEY: KEY, "key": KEY})
    assert bad.status_code == 422
    assert KEY not in bad.text
    assert (await client.delete(path)).status_code == 200
    assert (await client.get(path)).status_code == 428
    assert KEY not in str(leases._entries)


@pytest.mark.parametrize("loss", ["restart", "expiration", "revoke"])
async def test_job_waits_and_resumes_without_operator_fallback(
    client, intake, monkeypatch, isolated_database, loss
):
    live(monkeypatch)
    monkeypatch.setattr(settings, "AI_API_KEY", "operator-must-never-be-used")
    metadata = await connect(client)
    response = await client.post("/api/v1/projects", json=intake)
    assert response.status_code == 201
    project = response.json()["data"]
    path = f"/api/v1/projects/{project['id']}"
    called = []

    async def execute(project, payload, emit):
        called.append(inference.current.get()[1]["model"])
        return {"verified": "original context preserved"}, "ideas_ready"

    monkeypatch.setattr(pipeline, "execute", execute)
    if loss == "restart":
        leases.clear()
    elif loss == "expiration":
        leases._entries[metadata["id"]].deadline = leases.clock() - 1
    else:
        await client.delete("/api/v1/ai/leases/" + metadata["id"])
    await drain()
    assert called == []
    paused = (await client.get(path + "/jobs")).json()["data"]["jobs"][0]
    assert paused["status"] == "credentials_required"
    assert "lease" not in paused["inference"]
    assert metadata["id"] not in json.dumps(paused)
    assert (await client.get(path)).json()["data"]["context"] == {}
    assert await jobs.claim_next() is None
    await connect(client, "groq")
    assert (
        await client.post(f"{path}/jobs/{paused['id']}/resume", json={"revision": 1})
    ).status_code == 409
    await connect(client, "openai", "replacement-synthetic-credential")
    resumed = await client.post(
        f"{path}/jobs/{paused['id']}/resume", json={"revision": 1}
    )
    assert resumed.status_code == 202, resumed.text
    await drain()
    completed = (await client.get(path)).json()["data"]
    assert completed["active_job"] is None
    assert completed["revision"] == 2
    assert called == [metadata["model"]]
    await assert_database_has_no_key(
        isolated_database, (KEY, "replacement-synthetic-credential")
    )


async def test_switching_keeps_original_job_routing_and_cancel_preserves_work(
    client, intake, monkeypatch
):
    live(monkeypatch)
    original = await connect(client)
    project = (await client.post("/api/v1/projects", json=intake)).json()["data"]
    await connect(client, "groq")
    captured = []

    async def execute(project, payload, emit):
        captured.append(inference.current.get()[1])
        return {"saved": True}, "ideas_ready"

    monkeypatch.setattr(pipeline, "execute", execute)
    await drain()
    assert captured[0]["lease"] == original["id"]
    assert captured[0]["provider"] == "openai"
    path = f"/api/v1/projects/{project['id']}"
    queued = (
        await client.post(path + "/jobs", json={"revision": 2, "kind": "ideas"})
    ).json()["data"]
    cancelled = await client.post(
        path + f"/jobs/{queued['id']}/cancel", json={"revision": 2}
    )
    assert cancelled.status_code == 200
    assert await jobs.claim_next() is None
    assert (await client.get(path)).json()["data"]["context"] == {"saved": True}


async def test_credential_content_never_reaches_database_or_logs(
    client, intake, monkeypatch, isolated_database
):
    live(monkeypatch)
    await connect(client)
    contaminated = {**intake, "constraints": KEY}
    assert (await client.post("/api/v1/projects", json=contaminated)).status_code == 422
    project = (await client.post("/api/v1/projects", json=intake)).json()["data"]

    async def execute(*args):
        # Simulate an unexpected provider failure carrying a request/header.
        raise RuntimeError(KEY)

    monkeypatch.setattr(pipeline, "execute", execute)
    await drain()
    response = await client.get(f"/api/v1/projects/{project['id']}/jobs")
    assert KEY not in response.text
    record = logging.LogRecord(
        "test", logging.ERROR, "test", 1, "accidental %s", (KEY,), None
    )
    assert KEY not in PrivateFormatter().format(record)
    assert KEY not in StructuredFormatter().format(record)
    await assert_database_has_no_key(isolated_database)


async def test_revoke_inflight_pauses_job_and_closes_request(
    client, intake, monkeypatch
):
    live(monkeypatch)
    metadata = await connect(client)
    project = (await client.post("/api/v1/projects", json=intake)).json()["data"]
    started, closed = asyncio.Event(), asyncio.Event()

    async def invoke(spec, secret, messages, max_tokens):
        assert secret == KEY
        try:
            started.set()
            await asyncio.Future()
        finally:
            closed.set()

    async def execute(project, payload, emit):
        await ai.completion(project.id, [{"role": "user", "content": "hello"}])

    monkeypatch.setattr(ai.transport, "invoke", invoke)
    monkeypatch.setattr(pipeline, "execute", execute)
    job = await jobs.claim_next()
    task = asyncio.create_task(jobs.run_job(job))
    await started.wait()
    await client.delete("/api/v1/ai/leases/" + metadata["id"])
    await task
    assert closed.is_set()
    status = (await client.get(f"/api/v1/projects/{project['id']}/jobs")).json()[
        "data"
    ]["jobs"][0]
    assert status["status"] == "credentials_required"
    assert KEY not in str(status)


@pytest.mark.parametrize("provider", CATALOG)
async def test_entire_live_pipeline_on_all_providers(
    client, intake, monkeypatch, isolated_database, provider
):
    live(monkeypatch)
    monkeypatch.setattr(settings, "TAVILY_API_KEY", "synthetic-operator-search-key")
    clients = mock_clients(monkeypatch, respond)
    original = httpx.AsyncClient
    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda **kw: original(**{"trust_env": False, "follow_redirects": False, **kw}),
    )
    metadata = await connect(client, provider)
    project = (await client.post("/api/v1/projects", json=intake)).json()["data"]
    path = f"/api/v1/projects/{project['id']}"
    await drain()
    project = (await client.get(path)).json()["data"]
    assert project["state"] == "ideas_ready", (await client.get(path + "/jobs")).text
    assert len(project["context"]["ideas"]) == 5
    idea = project["context"]["ideas"][0]
    response = await client.post(
        path + f"/ideas/{idea['id']}/confirm", json={"revision": project["revision"]}
    )
    assert response.status_code == 200
    await drain()
    project = (await client.get(path)).json()["data"]
    assert project["state"] == "stack_review", (await client.get(path + "/jobs")).text
    assert (
        await client.post(
            path + "/stack/confirm", json={"revision": project["revision"]}
        )
    ).status_code == 200
    await drain()
    project = (await client.get(path)).json()["data"]
    assert project["context"].get("documents"), (await client.get(path + "/jobs")).text
    before = json.dumps(project["context"]["documents"])
    assert len(project["context"]["documents"]["files"]) == 10
    assert (
        await client.post(
            path + "/chat",
            json={
                "revision": project["revision"],
                "message": "What should we build first?",
            },
        )
    ).status_code == 202
    await drain()
    assert len((await client.get(path + "/chat")).json()["data"]["messages"]) == 2
    assert all(c.is_closed for c in clients)
    leases.clear()
    project = (await client.get(path)).json()["data"]
    assert json.dumps(project["context"]["documents"]) == before
    assert (await client.get(path + "/export")).status_code == 200
    assert metadata["id"] not in json.dumps(project)
    await assert_database_has_no_key(isolated_database)
