"""Exercise the real provider adapter while keeping paid inference offline."""

import litellm
import pytest

from app.core.config import settings
from app.studio import ai
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

    async def respond(**kwargs):
        calls.append(kwargs)
        return litellm.ModelResponse(
            choices=[
                {
                    "message": {"role": "assistant", "content": "A grounded response."},
                    "finish_reason": finish_reason,
                }
            ],
            usage={"prompt_tokens": 100, "completion_tokens": 20, "total_tokens": 120},
        )

    monkeypatch.setattr(litellm, "acompletion", respond)
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
    assert calls[0]["api_key"] == "adapter-test-key"
    assert calls[0]["model"] == "openai/test-model"
    assert calls[0]["api_base"] == "https://inference.invalid/v1"
    assert calls[0]["messages"] == messages
    assert calls[0]["num_retries"] == 0
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
