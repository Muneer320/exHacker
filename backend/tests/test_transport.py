"""Verify real wire adapters and failure boundaries with offline HTTP transports."""

import json

import httpx
import pytest

from app.studio import transport
from app.studio.errors import CredentialsRequiredError, StudioError
from app.studio.providers import CATALOG, model_spec

SECRET = "fixture-provider-credential"


def provider_response(provider, text="A useful response"):
    if provider in ("openai", "xai"):
        return {
            "status": "completed",
            "output": [
                {"type": "message", "content": [{"type": "output_text", "text": text}]}
            ],
            "usage": {"input_tokens": 100, "output_tokens": 20},
        }
    if provider == "anthropic":
        return {
            "content": [{"type": "text", "text": text}],
            "stop_reason": "end_turn",
            "usage": {"input_tokens": 100, "output_tokens": 20},
        }
    if provider == "gemini":
        return {
            "candidates": [
                {"content": {"parts": [{"text": text}]}, "finishReason": "STOP"}
            ],
            "usageMetadata": {
                "promptTokenCount": 100,
                "candidatesTokenCount": 18,
                "thoughtsTokenCount": 2,
            },
        }
    return {
        "choices": [{"message": {"content": text}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 100, "completion_tokens": 20},
    }


def mock_clients(monkeypatch, handler):
    original = httpx.AsyncClient
    clients = []

    def factory(**kwargs):
        assert kwargs["trust_env"] is False
        assert kwargs["follow_redirects"] is False
        client = original(transport=httpx.MockTransport(handler), **kwargs)
        clients.append(client)
        return client

    monkeypatch.setattr(transport.httpx, "AsyncClient", factory)
    return clients


@pytest.mark.parametrize("provider", CATALOG)
async def test_five_provider_protocols_and_client_cleanup(monkeypatch, provider):
    spec = {
        **model_spec(provider, CATALOG[provider]["models"][0]["id"]),
        "source": "byok",
    }
    messages = [
        {"role": "system", "content": "system rules"},
        {"role": "user", "content": "first question"},
        {"role": "assistant", "content": "previous answer"},
        {"role": "user", "content": "follow-up"},
    ]
    calls = []

    def respond(request):
        calls.append(request)
        assert request.method == "POST"
        assert request.url.scheme == "https"
        assert not request.url.query
        body = json.loads(request.content)
        assert SECRET not in request.content.decode()
        if provider == "gemini":
            assert request.headers["x-goog-api-key"] == SECRET
            assert "authorization" not in request.headers
            assert body["contents"][1]["role"] == "model"
            assert body["systemInstruction"]["parts"][0]["text"] == "system rules"
        else:
            assert request.headers["Authorization"] == f"Bearer {SECRET}"
            assert body["model"] == spec["model"]
        if provider in ("openai", "xai"):
            assert body["store"] is False
            assert body["max_output_tokens"] == 1234
        if provider == "anthropic":
            assert request.headers["anthropic-version"] == "2026-10-21"
            assert body["system"] == "system rules"
            assert all(m["role"] != "system" for m in body["messages"])
        return httpx.Response(200, json=provider_response(provider))

    clients = mock_clients(monkeypatch, respond)
    result = await transport.invoke(spec, SECRET, messages, 1234)
    assert result == transport.Result("A useful response", 100, 20)
    assert len(calls) == len(clients) == 1
    assert clients[0].is_closed


@pytest.mark.parametrize("status", [302, 400, 401, 403, 429, 500, 200])
async def test_failure_bodies_are_never_exposed(monkeypatch, status, caplog):
    spec = {"source": "byok", "provider": "openai", "model": "gpt-6-luna"}
    clients = mock_clients(
        monkeypatch,
        lambda _: httpx.Response(
            status,
            headers={"Location": "https://evil.invalid/"},
            json=provider_response("openai", SECRET)
            if status == 200
            else {"error": SECRET},
        ),
    )
    with pytest.raises(StudioError) as error:
        await transport.invoke(
            spec, SECRET, [{"role": "user", "content": "hello"}], 100
        )
    assert SECRET not in str(error.value)
    assert SECRET not in caplog.text
    assert all(c.is_closed for c in clients)
    if status in (401, 403):
        assert isinstance(error.value, CredentialsRequiredError)


async def test_response_size_and_malformed_json_fail_closed(monkeypatch):
    spec = {"source": "byok", "provider": "groq", "model": "openai/gpt-oss-120b"}
    for body in (b"a" * 2_000_001, b"{invalid", b"{}"):
        clients = mock_clients(
            monkeypatch, lambda _, payload=body: httpx.Response(200, content=payload)
        )
        with pytest.raises(StudioError):
            await transport.invoke(
                spec, SECRET, [{"role": "user", "content": "hello"}], 100
            )
        assert clients[0].is_closed
        monkeypatch.undo()


async def test_request_limit_is_actionable_without_exposing_provider_details(
    monkeypatch, caplog
):
    spec = {"source": "byok", "provider": "groq", "model": "openai/gpt-oss-120b"}
    clients = mock_clients(
        monkeypatch,
        lambda _: httpx.Response(
            413,
            json={
                "error": {
                    "message": f"Request too large for organization private-account: {SECRET}"
                }
            },
        ),
    )
    with pytest.raises(StudioError) as caught:
        await transport.invoke(
            spec, SECRET, [{"role": "user", "content": "review"}], 11000
        )
    assert "Groq" in str(caught.value)
    assert "HTTP 413" in str(caught.value)
    assert "account" in str(caught.value)
    assert "private-account" not in str(caught.value) + caplog.text
    assert SECRET not in str(caught.value) + caplog.text
    assert "HTTP 413" in caplog.text
    assert clients[0].is_closed


@pytest.mark.parametrize(
    "header,expected",
    [("7.5", 7.5), ("0", 1), (None, 1), ("bad", 1), ("120", None), ("nan", None)],
)
def test_provider_cooldowns_are_bounded_without_retrying_too_early(header, expected):
    assert transport.retry_delay(header) == expected
