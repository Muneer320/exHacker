"""Synthetic external services; never imported by application code."""

import json

import httpx

from app.studio import demo
from tests.test_transport import provider_response


def respond(request):
    body = json.loads(request.content)
    if request.url.host == "api.tavily.com":
        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "url": "https://github.com/test-fixtures/offline-evidence",
                        "title": "Synthetic test evidence",
                        "content": "Test fixture, not market validation.",
                        "score": 0.8,
                    }
                ]
            },
        )
    provider = {
        "api.openai.com": "openai",
        "api.anthropic.com": "anthropic",
        "generativelanguage.googleapis.com": "gemini",
        "api.x.ai": "xai",
        "api.groq.com": "groq",
    }[request.url.host]
    if provider in ("openai", "xai"):
        messages = body["input"]
    elif provider == "anthropic":
        messages = [{"role": "system", "content": body["system"]}, *body["messages"]]
    elif provider == "gemini":
        messages = [
            {
                "role": "system",
                "content": body["systemInstruction"]["parts"][0]["text"],
            },
            *[
                {"role": "user", "content": m["parts"][0]["text"]}
                for m in body["contents"]
            ],
        ]
    else:
        messages = body["messages"]
    system = messages[0]["content"]
    marker = "JSON SCHEMA:" + chr(10)
    if marker not in system:
        return httpx.Response(
            200,
            json=provider_response(
                provider,
                "Integration fixture: build the smallest approved workflow first. Your confirmed stack and team deadline remain the constraints.",
            ),
        )
    schema = json.loads(system.split(marker, 1)[1])
    context = json.loads(messages[1]["content"])
    intake = context["intake"]
    title = schema["title"]
    if title in ("CandidateBatch", "RefinedIdea"):
        ideas = [
            i.model_dump() for i in demo.ideas(intake, context.get("feedback", ""))
        ]
        if context.get("research", {}).get("sources"):
            for idea in ideas:
                idea["evidence_ids"] = [context["research"]["sources"][0]["id"]]
        result = {"idea": ideas[0]} if title == "RefinedIdea" else {"ideas": ideas}
    elif title == "Stack":
        result = (
            context.get("requested_stack_choices_to_preserve")
            or demo.stack(intake).model_dump()
        )
    elif title == "Specification":
        result = demo.specification(intake, context["confirmed_idea"]).model_dump()
    else:
        raise AssertionError(f"Unhandled test schema {title}")
    return httpx.Response(200, json=provider_response(provider, json.dumps(result)))
