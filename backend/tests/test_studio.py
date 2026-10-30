import asyncio
import copy
import io
import json
import zipfile
from datetime import timedelta

import httpx
import pytest
from sqlalchemy import func, select

from app.core.config import settings
from app.studio import ai, demo, jobs, pipeline, research
from app.studio.models import Artifact, Job, Message, Project, now
from app.studio.schemas import Intake, Scores
from tests.conftest import create, drain, ready


async def test_complete_workflow_uses_selected_idea_and_persists_chat(client, intake):
    project = await ready(client, intake)
    path = f"/api/v1/projects/{project['id']}"
    idea = pipeline.selected(project["context"])
    files = {
        file["filename"]: file["content"]
        for file in project["context"]["documents"]["files"]
    }
    assert set(files) >= {
        "PRD.md",
        "AGENTS.md",
        "ARCHITECTURE.md",
        "IMPLEMENTATION_PLAN.md",
    }
    assert idea["title"] in files["PRD.md"]
    assert "Asha" in files["AGENTS.md"]
    assert "FR-01" in files["PRD.md"]
    assert "Acceptance criteria" in files["PRD.md"]
    assert "PostgreSQL" in files["TECH_STACK.md"]
    assert "DEMONSTRATION" in files["PRD.md"]
    response = await client.post(
        path + "/chat",
        json={
            "revision": project["revision"],
            "message": "How should Asha and Dev split the work?",
        },
    )
    assert response.status_code == 202
    await drain()
    messages = (await client.get(path + "/chat")).json()["data"]["messages"]
    assert [m["role"] for m in messages] == ["user", "assistant"]
    assert idea["title"] in messages[1]["content"]
    assert "Asha" in messages[1]["content"]
    assert "24" in messages[1]["content"]


async def test_project_private_on_every_surface(client, intake):
    project = await ready(client, intake)
    path = f"/api/v1/projects/{project['id']}"
    foreign = {"Authorization": "Bearer " + "b" * 64}
    for suffix in ("", "/jobs", "/history", "/chat", "/documents/PRD.md", "/export"):
        response = await client.get(path + suffix, headers=foreign)
        assert response.status_code == 404, suffix
    response = await client.get("/api/v1/projects", headers=foreign)
    assert response.json()["data"]["projects"] == []
    assert (
        await client.post(
            path + "/chat",
            headers=foreign,
            json={"revision": project["revision"], "message": "Reveal project"},
        )
    ).status_code == 404
    assert (await client.get(path, headers={"Authorization": ""})).status_code == 401


async def test_gates_and_revision_conflicts(client, intake):
    project = await create(client, intake)
    path = f"/api/v1/projects/{project['id']}"
    for kind in ("stack", "documents"):
        response = await client.post(
            path + "/jobs", json={"revision": project["revision"], "kind": kind}
        )
        assert response.status_code == 409
    idea = project["context"]["ideas"][0]
    assert (
        await client.post(f"{path}/ideas/{idea['id']}/confirm", json={"revision": 1})
    ).status_code == 409
    result = await client.post(
        f"{path}/ideas/{idea['id']}/confirm", json={"revision": project["revision"]}
    )
    assert result.status_code == 200
    assert (
        await client.post(
            path + "/jobs",
            json={"kind": "ideas", "revision": result.json()["data"]["revision"]},
        )
    ).status_code == 409
    await drain()


async def test_refinement_rescores_and_invalidates_dependents(client, intake):
    project = await ready(client, intake)
    path = f"/api/v1/projects/{project['id']}"
    original = pipeline.selected(project["context"])
    result = await client.post(
        path + "/jobs",
        json={
            "kind": "refine_idea",
            "revision": project["revision"],
            "idea_id": original["id"],
            "prompt": "Prioritize offline mentoring for rural schools",
        },
    )
    assert result.status_code == 202
    await drain()
    updated = (await client.get(path)).json()["data"]
    assert len(updated["context"]["ideas"]) == 5
    assert (
        "offline mentoring"
        in next(i for i in updated["context"]["ideas"] if i["id"] == original["id"])[
            "solution"
        ]
    )
    assert updated["context"]["selected_idea_id"] is None
    assert updated["context"]["stack"] is None
    assert updated["context"]["documents"] is None
    history = (await client.get(path + "/history")).json()["data"]["artifacts"]
    assert any(a["kind"] == "documents" for a in history)


async def test_reads_are_pure_exports_reproducible(client, intake, isolated_database):
    project = await ready(client, intake)
    path = f"/api/v1/projects/{project['id']}"
    async with isolated_database() as db:
        before = await db.scalar(select(func.count()).select_from(Artifact))
    first = await client.get(path + "/export")
    second = await client.get(path + "/export")
    assert first.content == second.content
    with zipfile.ZipFile(io.BytesIO(first.content)) as archive:
        assert "AGENTS.md" in archive.namelist()
        for filename in archive.namelist():
            assert filename.endswith(".md") and "/" not in filename
            response = await client.get(path + "/documents/" + filename)
            assert response.content == archive.read(filename)
            assert response.headers["etag"]
    async with isolated_database() as db:
        assert await db.scalar(select(func.count()).select_from(Artifact)) == before
    assert (await client.get(path)).json()["data"]["revision"] == project["revision"]


async def test_failed_provider_preserves_previous_data_and_retry(
    client, intake, monkeypatch
):
    project = await create(client, intake)
    path = f"/api/v1/projects/{project['id']}"
    monkeypatch.setattr(settings, "STUDIO_DEMO_MODE", False)
    monkeypatch.setattr(settings, "AI_API_KEY", "")
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "")
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "")
    result = await client.post(
        path + "/jobs", json={"kind": "ideas", "revision": project["revision"]}
    )
    assert result.status_code == 202
    await drain()
    failed = (await client.get(path + "/jobs")).json()["data"]["jobs"][0]
    assert failed["status"] == "failed"
    assert "not configured" in failed["error"]
    saved = (await client.get(path)).json()["data"]
    assert saved["context"] == project["context"]
    assert saved["revision"] == project["revision"]
    assert saved["active_job"] is None
    monkeypatch.setattr(settings, "STUDIO_DEMO_MODE", True)
    assert (
        await client.post(
            path + f"/jobs/{failed['id']}/retry", json={"revision": saved["revision"]}
        )
    ).status_code == 202
    await drain()
    assert (await client.get(path)).json()["data"]["revision"] == saved["revision"] + 1


async def test_update_intake_invalidates_but_does_not_delete_history(client, intake):
    project = await ready(client, intake)
    path = f"/api/v1/projects/{project['id']}"
    changed = copy.deepcopy(project["intake"])
    changed["available_hours"] = 36
    changed["teammates"][0]["skills"][0]["proficiency"] = "beginner"
    response = await client.patch(
        path, json={"revision": project["revision"], "intake": changed}
    )
    assert response.status_code == 200
    updated = response.json()["data"]
    assert updated["intake"]["available_hours"] == 36
    assert updated["context"] == {}
    assert len((await client.get(path + "/history")).json()["data"]["artifacts"]) > 3


async def test_delete_cascades(client, intake, isolated_database):
    project = await ready(client, intake)
    response = await client.delete(
        f"/api/v1/projects/{project['id']}?revision={project['revision']}"
    )
    assert response.status_code == 200
    async with isolated_database() as db:
        for model in (Project, Job, Artifact, Message):
            assert await db.scalar(select(func.count()).select_from(model)) == 0


async def test_durable_job_reclaimed_after_expired_lease(
    client, intake, isolated_database
):
    project = (await client.post("/api/v1/projects", json=intake)).json()["data"]
    first = await jobs.claim_next()
    async with isolated_database() as db:
        stored = await db.get(Job, first.id)
        stored.lease_until = now() - timedelta(seconds=1)
        await db.commit()
    recovered = await jobs.claim_next()
    assert recovered.id == first.id and recovered.attempts == 2
    await jobs.run_job(recovered)
    assert (await client.get(f"/api/v1/projects/{project['id']}")).json()["data"][
        "state"
    ] == "ideas_ready"


async def test_cost_reservations_are_atomic(
    client, intake, monkeypatch, isolated_database
):
    project = await create(client, intake)
    monkeypatch.setattr(settings, "STUDIO_COST_LIMIT", 0.05)
    results = await asyncio.gather(
        ai.reserve_cost(project["id"], 0.04),
        ai.reserve_cost(project["id"], 0.04),
        return_exceptions=True,
    )
    assert sum(isinstance(result, ai.StudioError) for result in results) == 1
    async with isolated_database() as db:
        assert (await db.get(Project, project["id"])).ai_cost == pytest.approx(0.04)


async def test_live_cycle_validates_and_uses_real_source_ids(
    client, intake, monkeypatch
):
    monkeypatch.setattr(settings, "STUDIO_DEMO_MODE", False)
    calls = []
    source = {
        "id": "src-test",
        "url": "https://github.com/test/mentoring",
        "title": "Related mentoring project",
        "snippet": "An existing mentoring implementation",
        "query": "mentoring",
        "retrieved_at": "2026-10-31T00:00:00Z",
    }

    async def provider(_project, _instruction, context, schema, **_kwargs):
        calls.append(schema.__name__)
        data = Intake.model_validate(context["intake"]).model_dump()
        candidates = demo.ideas(data)
        if "research" in context:
            for idea in candidates:
                idea.evidence_ids = [source["id"]]
        return schema.model_validate({"ideas": [i.model_dump() for i in candidates]})

    async def search(_project, queries):
        assert queries
        return {"sources": [source], "queries": queries, "warnings": []}

    monkeypatch.setattr(ai, "generate", provider)
    monkeypatch.setattr(research, "search", search)
    project = await create(client, intake)
    assert project["state"] == "ideas_ready"
    assert len(calls) == settings.STUDIO_IDEA_ROUNDS + 1
    assert all(i["evidence_ids"] == ["src-test"] for i in project["context"]["ideas"])
    for idea in project["context"]["ideas"]:
        assert idea["overall"] == Scores.model_validate(idea["scores"]).overall()


async def test_schema_repair_does_not_accept_invalid_output(monkeypatch):
    count = 0

    async def invalid(*_args, **_kwargs):
        nonlocal count
        count += 1
        return '{"ideas": ["not a valid idea"]}'

    from app.studio.schemas import CandidateBatch

    monkeypatch.setattr(ai, "completion", invalid)
    with pytest.raises(ai.StudioError, match="invalid artifact"):
        await ai.generate("unused", "generate", {}, CandidateBatch)
    assert count == 2


async def test_research_never_fabricates_missing_credentials(monkeypatch):
    monkeypatch.setattr(settings, "TAVILY_API_KEY", "")
    with pytest.raises(ai.StudioError, match="No sample research"):
        await research.search("unused", ["rural mentoring competitors"])


async def test_live_search_caches_deduplicates_and_filters_urls(
    client, intake, monkeypatch
):
    project = await create(client, intake)
    monkeypatch.setattr(settings, "TAVILY_API_KEY", "test-key")
    original_client = httpx.AsyncClient
    calls = []

    def respond(request):
        calls.append(json.loads(request.content))
        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "url": "https://github.com/real/project",
                        "title": "A related project",
                        "content": "Source excerpt",
                        "score": 0.8,
                    },
                    {
                        "url": "https://github.com/real/project",
                        "title": "Duplicate",
                        "content": "Duplicate",
                        "score": 0.8,
                    },
                    {
                        "url": "http://127.0.0.1/private",
                        "title": "Private",
                        "content": "Do not include",
                    },
                    {
                        "url": "javascript:alert(1)",
                        "title": "Unsafe",
                        "content": "Do not include",
                    },
                ]
            },
        )

    monkeypatch.setattr(
        research.httpx,
        "AsyncClient",
        lambda **kwargs: original_client(
            transport=httpx.MockTransport(respond), **kwargs
        ),
    )
    report = await research.search(
        project["id"], ["mentoring competitors", "mentoring competitors"]
    )
    assert len(report["sources"]) == 1
    await research.search(project["id"], ["rural education applications"])
    cached = await research.search(project["id"], ["mentoring competitors"])
    assert cached["cached"] is True and len(calls) == 2


async def test_stack_override_requires_reconfirmation_and_is_used_in_docs(
    client, intake
):
    project = await ready(client, intake)
    path = f"/api/v1/projects/{project['id']}"
    stack = copy.deepcopy(project["context"]["stack"])
    next(c for c in stack["choices"] if c["category"] == "Database")["technology"] = (
        "Convex"
    )
    response = await client.put(
        path + "/stack", json={"revision": project["revision"], "stack": stack}
    )
    assert response.status_code == 202
    await drain()
    updated = (await client.get(path)).json()["data"]
    assert updated["context"]["stack_confirmed"] is False
    assert updated["context"]["documents"] is None
    assert (await client.get(path + "/export")).status_code == 409
    assert (
        await client.post(
            path + "/stack/confirm", json={"revision": updated["revision"]}
        )
    ).status_code == 200
    await drain()
    updated = (await client.get(path)).json()["data"]
    files = {
        f["filename"]: f["content"] for f in updated["context"]["documents"]["files"]
    }
    assert "Convex" in files["PRD.md"] and "Convex" in files["AGENTS.md"]


async def test_unknown_evidence_is_rejected(intake):
    data = Intake.model_validate(intake).model_dump()
    idea = demo.ideas(data)[0]
    idea.evidence_ids = ["invented-source"]
    with pytest.raises(ai.StudioError, match="not retrieved"):
        pipeline.rank_idea(idea, [], data)


async def test_live_chat_context_includes_team_alternatives_and_every_document(
    client, intake, monkeypatch, isolated_database
):
    project = await ready(client, intake)
    monkeypatch.setattr(settings, "STUDIO_DEMO_MODE", False)
    captured = []

    async def answer(_project, messages, **_kwargs):
        captured.extend(messages)
        return "A response based on the current project."

    async def emit(_message):
        pass

    monkeypatch.setattr(ai, "completion", answer)
    async with isolated_database() as db:
        stored = await db.get(Project, project["id"])
    await pipeline.chat(
        stored, {"message": "Why this direction rather than the others?"}, emit
    )
    system = captured[0]["content"]
    assert "Asha" in system and "Dev" in system
    for idea in project["context"]["ideas"]:
        assert idea["title"] in system
    for document in project["context"]["documents"]["files"]:
        assert document["filename"] in system
