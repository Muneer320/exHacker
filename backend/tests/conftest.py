"""Every test owns a temporary database. Never touch configured application data."""

import copy
import os
import uuid

import httpx
import pytest
import pytest_asyncio
from sqlalchemy import event, text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app import main
from app.core.config import settings
from app.db import session
from app.main import app
from app.studio import ai, jobs, pipeline, research
from app.studio.credentials import leases
from app.studio.models import StudioBase


@pytest.fixture
def intake():
    return {
        "idea": "Help rural students find STEM mentors despite unreliable internet",
        "available_hours": 24,
        "teammates": [
            {
                "name": "Asha",
                "role": "Frontend",
                "skills": [{"technology": "React", "proficiency": "advanced"}],
            },
            {
                "name": "Dev",
                "role": "Backend",
                "skills": [{"technology": "Python", "proficiency": "intermediate"}],
                "hours_available": 16,
            },
        ],
        "judging_criteria": "Accessibility, demonstrable impact, and feasibility",
        "required_technologies": "Open-source tools",
    }


@pytest_asyncio.fixture(autouse=True)
async def isolated_database(tmp_path, monkeypatch):
    test_url = os.environ.get("TEST_DATABASE_URL")
    schema = f"test_{uuid.uuid4().hex}"
    admin = None
    if test_url:
        # Never run destructive fixture setup against an application database.
        url = make_url(test_url)
        if url.drivername != "postgresql+asyncpg" or not (url.database or "").endswith(
            "_verification"
        ):
            raise RuntimeError(
                "TEST_DATABASE_URL must point to a dedicated PostgreSQL *_verification database."
            )
        admin = create_async_engine(test_url)
        async with admin.begin() as connection:
            await connection.execute(text(f'CREATE SCHEMA "{schema}"'))
        engine = create_async_engine(
            test_url, connect_args={"server_settings": {"search_path": schema}}
        )
    else:
        engine = create_async_engine(
            f"sqlite+aiosqlite:///{(tmp_path / 'test.db').as_posix()}"
        )

        @event.listens_for(engine.sync_engine, "connect")
        def foreign_keys(connection, _record):
            connection.execute("PRAGMA foreign_keys=ON")
            connection.execute("PRAGMA busy_timeout=10000")

    factory = async_sessionmaker(engine, expire_on_commit=False)
    monkeypatch.setattr(session, "engine", engine)
    monkeypatch.setattr(main, "engine", engine)
    monkeypatch.setattr(session, "AsyncSessionLocal", factory)
    for module in (ai, jobs, pipeline, research):
        monkeypatch.setattr(module, "AsyncSessionLocal", factory)
    leases.clear()
    monkeypatch.setattr(settings, "AI_ACCESS_MODE", "operator")
    monkeypatch.setattr(settings, "STUDIO_DEMO_MODE", True)
    monkeypatch.setattr(settings, "STUDIO_WORKER_ENABLED", False)
    monkeypatch.setattr(settings, "FREE_TIER_PROJECTS_PER_DAY", 50)
    async with engine.begin() as connection:
        await connection.run_sync(StudioBase.metadata.create_all)
    yield factory
    leases.clear()
    await engine.dispose()
    if admin:
        async with admin.begin() as connection:
            await connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        await admin.dispose()


@pytest_asyncio.fixture
async def client():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
        headers={"Authorization": "Bearer " + "a" * 64},
    ) as client:
        yield client


async def drain():
    for _ in range(10):
        job = await jobs.claim_next()
        if job is None:
            return
        await jobs.run_job(job)
    raise AssertionError("Unexpected unbounded job cycle")


async def create(client, intake):
    response = await client.post("/api/v1/projects", json=copy.deepcopy(intake))
    assert response.status_code == 201, response.text
    project = response.json()["data"]
    await drain()
    return (await client.get(f"/api/v1/projects/{project['id']}")).json()["data"]


async def ready(client, intake):
    project = await create(client, intake)
    path = f"/api/v1/projects/{project['id']}"
    selected = project["context"]["ideas"][2]["id"]
    response = await client.post(
        f"{path}/ideas/{selected}/confirm", json={"revision": project["revision"]}
    )
    assert response.status_code == 200, response.text
    await drain()
    project = (await client.get(path)).json()["data"]
    response = await client.post(
        f"{path}/stack/confirm", json={"revision": project["revision"]}
    )
    assert response.status_code == 200, response.text
    await drain()
    project = (await client.get(path)).json()["data"]
    assert project["state"] == "ready", (await client.get(path + "/jobs")).json()
    return project
