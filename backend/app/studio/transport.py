"""Request-scoped HTTPX adapters: no SDK caches, redirects, proxies or response storage."""

from dataclasses import dataclass

import httpx

from app.core.config import settings
from app.studio.errors import CredentialsRequiredError, StudioError

ENDPOINTS = {
    "openai": "https://api.openai.com/v1/responses",
    "anthropic": "https://api.anthropic.com/v1/messages",
    "gemini": "https://generativelanguage.googleapis.com/v1beta/models/",
    "xai": "https://api.x.ai/v1/responses",
    "groq": "https://api.groq.com/openai/v1/chat/completions",
}


class TransientProviderError(StudioError):
    def __init__(self):
        super().__init__(
            "The provider is temporarily unavailable or rate limited. Retry shortly.",
            502,
        )


@dataclass
class Result:
    text: str
    input_tokens: int | None
    output_tokens: int | None
    truncated: bool = False


def request(spec, key, messages, max_tokens):
    provider, model = spec["provider"], spec["model"]
    url = ENDPOINTS[provider]
    headers = {"Authorization": f"Bearer {key}"}
    system = "\n\n".join(m["content"] for m in messages if m["role"] == "system")
    turns = [m for m in messages if m["role"] != "system"]
    if provider in ("openai", "xai"):
        body = {
            "model": model,
            "input": messages,
            "store": False,
            "max_output_tokens": max_tokens,
        }
        if model.startswith(("gpt-6", "grok-4.7")):
            body["reasoning"] = {"effort": "low"}
    elif provider == "anthropic":
        headers["anthropic-version"] = "2026-10-21"
        body = {
            "model": model,
            "system": system,
            "messages": turns,
            "max_tokens": max_tokens,
            "stream": False,
        }
    elif provider == "gemini":
        headers = {"x-goog-api-key": key}
        url += model + ":generateContent"
        body = {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [
                {
                    "role": "model" if m["role"] == "assistant" else "user",
                    "parts": [{"text": m["content"]}],
                }
                for m in turns
            ],
            "generationConfig": {"maxOutputTokens": max_tokens},
        }
    else:
        body = {
            "model": model,
            "messages": messages,
            "max_completion_tokens": max_tokens,
        }
        if model.startswith("openai/gpt-oss"):
            body["reasoning_effort"] = "low"
    if spec["source"] == "operator" and settings.AI_BASE_URL:
        if provider != "openai":
            raise StudioError(
                "AI_BASE_URL is supported only for operator OpenAI Responses endpoints.",
                503,
            )
        url = settings.AI_BASE_URL.rstrip("/") + "/responses"
    return url, headers, body


def parse(provider, data):
    if provider in ("openai", "xai"):
        text = "".join(
            c.get("text", "")
            for item in data.get("output", [])
            if item.get("type") == "message"
            for c in item.get("content", [])
            if c.get("type") == "output_text"
        )
        usage = data.get("usage") or {}
        incomplete = data.get("status") != "completed"
        return Result(
            text, usage.get("input_tokens"), usage.get("output_tokens"), incomplete
        )
    if provider == "anthropic":
        text = "".join(
            c.get("text", "")
            for c in data.get("content", [])
            if c.get("type") == "text"
        )
        usage = data.get("usage") or {}
        return Result(
            text,
            usage.get("input_tokens"),
            usage.get("output_tokens"),
            data.get("stop_reason") == "max_tokens",
        )
    if provider == "gemini":
        candidate = data.get("candidates", [{}])[0]
        text = "".join(
            p.get("text", "")
            for p in candidate.get("content", {}).get("parts", [])
            if not p.get("thought")
        )
        usage = data.get("usageMetadata") or {}
        output = usage.get("candidatesTokenCount")
        if output is not None:
            output += usage.get("thoughtsTokenCount", 0)
        return Result(
            text,
            usage.get("promptTokenCount"),
            output,
            candidate.get("finishReason") == "MAX_TOKENS",
        )
    choice = data["choices"][0]
    usage = data.get("usage") or {}
    return Result(
        choice["message"].get("content") or "",
        usage.get("prompt_tokens"),
        usage.get("completion_tokens"),
        choice.get("finish_reason") == "length",
    )


async def invoke(spec, key, messages, max_tokens):
    url, headers, body = request(spec, key, messages, max_tokens)
    try:
        async with (
            httpx.AsyncClient(
                timeout=settings.AI_TIMEOUT_SECONDS,
                trust_env=False,
                follow_redirects=False,
            ) as client,
            client.stream("POST", url, headers=headers, json=body) as response,
        ):
            if response.status_code in (401, 403):
                if spec["source"] == "byok":
                    raise CredentialsRequiredError()
                raise StudioError(
                    "The operator's provider credentials were rejected.", 502
                )
            if response.status_code == 429 or response.status_code >= 500:
                raise TransientProviderError()
            if response.status_code != 200:
                raise StudioError(
                    "The provider rejected the request. Check model access, quotas and provider limits.",
                    502,
                )
            buffer = bytearray()
            async for chunk in response.aiter_bytes():
                buffer.extend(chunk)
                if len(buffer) > 2_000_000:
                    raise StudioError(
                        "The provider response exceeded the safety limit.", 502
                    )
            import json

            result = parse(spec["provider"], json.loads(buffer))
            if key in result.text:
                raise StudioError(
                    "The provider returned credential-like content; the result was discarded.",
                    502,
                )
            return result
    except StudioError:
        raise
    except (httpx.TimeoutException, httpx.NetworkError):
        raise TransientProviderError() from None
    except Exception:
        raise StudioError(
            "The provider returned an invalid response. Retry this step.", 502
        ) from None
    finally:
        # Drop application references as soon as the closed request completes.
        headers.clear()
        key = ""
