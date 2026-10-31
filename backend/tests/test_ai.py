"""Exercise the real provider adapter while keeping paid inference offline."""

import json

import httpx
import pytest

from app.core.config import settings
from app.studio import ai, transport
from app.studio.models import Project
from tests.conftest import create


@pytest.mark.parametrize("finish_reason", ["stop", "length"])
async def test_provider_adapter_reconciles_usage_and_rejects_truncation(
    client, intake, isolated_database, monkeypatch, finish_reason
):
    project = await create(client, intake)
    monkeypatch.setattr(settings, "AI_API_KEY", "adapter-test-key")
    monkeypatch.setattr(settings, "AI_MODEL", "openai/test-model")
    monkeypatch.setattr(settings, "AI_BASE_URL", "https://inference.invalid/v1")
    calls = []

    def respond(request):
        calls.append(request)
        return httpx.Response(
            200,
            json={
                "status": "incomplete" if finish_reason == "length" else "completed",
                "output": [
                    {
                        "type": "message",
                        "content": [
                            {"type": "output_text", "text": "A grounded response."}
                        ],
                    }
                ],
                "usage": {"input_tokens": 100, "output_tokens": 20},
            },
        )

    original_client = httpx.AsyncClient
    monkeypatch.setattr(
        transport.httpx,
        "AsyncClient",
        lambda **kwargs: original_client(
            transport=httpx.MockTransport(respond), **kwargs
        ),
    )
    messages = [
        {"role": "user", "content": "Help our team decide what to build first."}
    ]
    if finish_reason == "length":
        with pytest.raises(ai.StudioError, match="output limit"):
            await ai.completion(project["id"], messages, max_tokens=1000)
    else:
        assert (
            await ai.completion(project["id"], messages, max_tokens=1000)
            == "A grounded response."
        )
    assert len(calls) == 1
    assert calls[0].headers["Authorization"] == "Bearer adapter-test-key"
    assert str(calls[0].url) == "https://inference.invalid/v1/responses"
    body = json.loads(calls[0].content)
    assert body["model"] == "test-model"
    assert body["input"] == messages
    assert body["store"] is False
    expected = (
        100 * settings.AI_INPUT_USD_PER_MILLION
        + 20 * settings.AI_OUTPUT_USD_PER_MILLION
    ) / 1_000_000
    async with isolated_database() as db:
        assert (await db.get(Project, project["id"])).ai_cost == pytest.approx(expected)


async def test_provider_configuration_requires_a_key_for_the_selected_provider(
    monkeypatch,
):
    monkeypatch.setattr(settings, "AI_API_KEY", "")
    monkeypatch.setattr(settings, "AI_MODEL", "anthropic/test-model")
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "other-provider-key")
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "")
    assert ai.configuration()["ai_configured"] is False
    with pytest.raises(ai.StudioError, match="not configured"):
        await ai.completion("unused", [{"role": "user", "content": "Hello"}])
    monkeypatch.setattr(settings, "AI_API_KEY", "explicit-provider-key")
    assert ai.configuration()["ai_configured"] is True


@pytest.mark.parametrize("cooldown,requests,delays", [("2", 2, [2]), ("120", 1, [])])
async def test_provider_cooldown_controls_actual_retries(
    client, intake, monkeypatch, cooldown, requests, delays
):
    from tests.test_transport import mock_clients, provider_response

    project = await create(client, intake)
    monkeypatch.setattr(settings, "AI_API_KEY", "synthetic-cooldown-key")
    monkeypatch.setattr(settings, "AI_MODEL", "openai/gpt-6-luna")
    calls, sleeps = [], []

    def respond(request):
        calls.append(request)
        if len(calls) == 1:
            return httpx.Response(
                429,
                headers={"retry-after": cooldown},
                json={"error": "private provider body"},
            )
        return httpx.Response(200, json=provider_response("openai"))

    async def sleep(seconds):
        sleeps.append(seconds)

    mock_clients(monkeypatch, respond)
    monkeypatch.setattr(ai.asyncio, "sleep", sleep)
    if requests == 1:
        with pytest.raises(transport.TransientProviderError, match="HTTP 429"):
            await ai.completion(project["id"], [{"role": "user", "content": "hello"}])
    else:
        assert (
            await ai.completion(project["id"], [{"role": "user", "content": "hello"}])
            == "A useful response"
        )
    assert len(calls) == requests
    assert sleeps == delays
