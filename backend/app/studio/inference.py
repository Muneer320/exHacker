"""Capture routing at enqueue time; resolve RAM credentials afresh for each call."""

from contextvars import ContextVar

from app.core.config import settings
from app.studio.credentials import leases
from app.studio.errors import StudioError
from app.studio.providers import model_spec

current: ContextVar[tuple[str, dict] | None] = ContextVar("inference", default=None)
current_job: ContextVar[tuple[str, int] | None] = ContextVar(
    "job_attempt", default=None
)


def operator_spec():
    provider, separator, model = settings.AI_MODEL.partition("/")
    if not separator:
        provider, model = "openai", provider
    if provider not in ("openai", "anthropic", "gemini", "xai", "groq"):
        raise StudioError(
            "The operator model must use a supported provider prefix.", 503
        )
    return {
        "source": "operator",
        "provider": provider,
        "model": model,
        "input_rate": settings.AI_INPUT_USD_PER_MILLION,
        "output_rate": settings.AI_OUTPUT_USD_PER_MILLION,
        "output": settings.AI_MAX_OUTPUT_TOKENS,
        "context": 1000000,
    }


def capture(owner, handle=""):
    if settings.STUDIO_DEMO_MODE:
        return {"source": "demo", "provider": "demo", "model": "offline-fixtures"}
    if settings.AI_ACCESS_MODE == "operator":
        return operator_spec()
    entry = leases.get(owner, handle)
    return {
        **model_spec(entry.provider, entry.model),
        "source": "byok",
        "lease": handle,
    }


def ensure(owner, spec):
    if spec.get("source") == "byok":
        entry = leases.get(owner, spec.get("lease", ""))
        if (entry.provider, entry.model) != (spec["provider"], spec["model"]):
            raise StudioError("The AI session does not match this operation.", 409)


def public(spec):
    return {key: spec[key] for key in ("source", "provider", "model") if key in spec}


def reject_secrets(value):
    import json
    import re

    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    if leases.contains_secret(text) or re.search(
        r"\b(?:sk-(?:ant-|proj-)?[A-Za-z0-9_-]{20,}|gsk_[A-Za-z0-9]{20,}|xai-[A-Za-z0-9_-]{20,}|AIza[A-Za-z0-9_-]{30,})",
        text,
    ):
        raise StudioError(
            "Credential-like content was blocked. Enter API keys only in AI session settings.",
            422,
        )
