"""Reviewed text-model catalog. Endpoints and authentication are never user supplied."""

from app.studio.errors import StudioError

# USD per million tokens. Use the higher long-context rate for reservations;
# these are safety estimates, not an invoice. Snapshot: 2026-10-31.
CATALOG = {
    "openai": {
        "name": "OpenAI",
        "models": [
            {
                "id": "gpt-6-luna",
                "name": "GPT-6 Luna",
                "context": 1050000,
                "output": 128000,
                "input_rate": 0.20,
                "output_rate": 0.75,
            }
        ],
    },
    "anthropic": {
        "name": "Anthropic (Claude)",
        "models": [
            {
                "id": "claude-haiku-5-5",
                "name": "Claude Haiku 5.5",
                "context": 1000000,
                "output": 128000,
                "input_rate": 0.50,
                "output_rate": 2.50,
            }
        ],
    },
    "gemini": {
        "name": "Google (Gemini)",
        "models": [
            {
                "id": "gemini-3.8-flash",
                "name": "Gemini 3.8 Flash",
                "context": 1048576,
                "output": 65536,
                "input_rate": 0.75,
                "output_rate": 3.75,
            }
        ],
    },
    "xai": {
        "name": "xAI (Grok)",
        "models": [
            {
                "id": "grok-4.7",
                "name": "Grok 4.7",
                "context": 500000,
                "output": 128000,
                "input_rate": 2.0,
                "output_rate": 6.0,
            }
        ],
    },
    "groq": {
        "name": "Groq",
        "note": "Groq's free-plan token limits can be much smaller than the model's context window. Full research reviews, documents and chat may require higher account limits.",
        "models": [
            {
                "id": "openai/gpt-oss-120b",
                "name": "GPT OSS 120B",
                "context": 131072,
                "output": 65536,
                "input_rate": 0.15,
                "output_rate": 0.60,
            },
            {
                "id": "openai/gpt-oss-20b",
                "name": "GPT OSS 20B",
                "context": 131072,
                "output": 65536,
                "input_rate": 0.075,
                "output_rate": 0.30,
            },
        ],
    },
}


def model_spec(provider, model):
    for spec in CATALOG.get(provider, {}).get("models", []):
        if spec["id"] == model:
            return {**spec, "provider": provider, "model": model}
    raise StudioError("Choose a provider and model from the supported catalog.", 422)


def catalog():
    return [{"id": key, **value} for key, value in CATALOG.items()]
