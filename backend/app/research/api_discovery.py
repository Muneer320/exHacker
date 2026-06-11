from __future__ import annotations

from typing import Any

from app.research.base import ResearchSource


class ApiDiscovery(ResearchSource):
    @property
    def name(self) -> str:
        return "api_discovery"

    def search(self, query: str, **kwargs: Any) -> list[dict[str, Any]]:  # noqa: ARG002
        results: list[dict[str, Any]] = []

        known_apis: list[dict[str, Any]] = [
            {"name": "OpenAI API", "provider": "OpenAI", "description": "GPT models, embeddings, DALL-E", "pricing": "Pay-per-token", "integration_effort": "low"},
            {"name": "Gemini API", "provider": "Google", "description": "Multimodal AI models", "pricing": "Free tier available", "integration_effort": "low"},
            {"name": "Supabase", "provider": "Supabase", "description": "PostgreSQL, auth, realtime, storage", "pricing": "Free tier available", "integration_effort": "low"},
            {"name": "Twilio", "provider": "Twilio", "description": "SMS, email, voice, video APIs", "pricing": "Pay-per-use", "integration_effort": "medium"},
            {"name": "Stripe", "provider": "Stripe", "description": "Payment processing, billing", "pricing": "2.9% + $0.30 per transaction", "integration_effort": "medium"},
            {"name": "Mapbox", "provider": "Mapbox", "description": "Maps, geocoding, navigation", "pricing": "Free tier available", "integration_effort": "medium"},
            {"name": "Resend", "provider": "Resend", "description": "Email API for developers", "pricing": "Free tier available", "integration_effort": "low"},
            {"name": "Clerk", "provider": "Clerk", "description": "Authentication and user management", "pricing": "Free tier available", "integration_effort": "low"},
        ]

        query_lower = query.lower()
        for api in known_apis:
            if any(word in api["name"].lower() for word in query_lower.split()) or \
               any(word in api["description"].lower() for word in query_lower.split()):
                results.append(api)

        return results[:5]
