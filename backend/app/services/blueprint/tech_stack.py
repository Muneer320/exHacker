"""Tech Stack Generator — deterministic decision tree.

SDPD: This is Tier 0. No AI is used.
Every recommendation is computed from rules, not generated.

The decision tree:
  1. Project type (inferred from idea keywords)
  2. Frontend framework
  3. Backend framework
  4. Database
  5. AI provider
  6. Auth provider
  7. Infrastructure

Each decision has an explanation template (written by humans, not AI).
"""

from __future__ import annotations

from typing import Any


def recommend_stack(idea: str) -> dict[str, Any]:
    """Recommend a complete tech stack for a project idea.

    Args:
        idea: The project description.

    Returns:
        Dict with stack choices and explanations.
    """
    idea_lower = idea.lower()
    proj_type = _classify_project(idea_lower)

    stack = {
        "project_type": proj_type,
        "frontend": _recommend_frontend(proj_type),
        "backend": _recommend_backend(proj_type),
        "database": _recommend_database(proj_type, idea_lower),
        "ai": _recommend_ai(idea_lower),
        "auth": _recommend_auth(idea_lower),
        "hosting": _recommend_hosting(proj_type),
        "explanations": {},
    }

    # Add human-written explanations
    stack["explanations"] = _get_explanations(stack)

    return stack


def _classify_project(idea: str) -> str:
    """Classify the project into a type based on keywords."""
    mobile_keywords = ["mobile", "app", "ios", "android", "smartphone", "phone", "tablet"]
    api_keywords = ["api", "backend", "service", "microservice", "serverless", "webhook"]
    cli_keywords = ["cli", "command line", "terminal", "script", "tool"]
    ai_keywords = ["chatbot", "ai", "llm", "gpt", "machine learning", "ml", "recommendation"]

    if any(kw in idea for kw in mobile_keywords):
        return "mobile_app"
    if any(kw in idea for kw in cli_keywords):
        return "cli_tool"
    if any(kw in idea for kw in api_keywords):
        return "api_service"
    if any(kw in idea for kw in ai_keywords):
        return "ai_app"

    return "web_app"  # Default


def _recommend_frontend(proj_type: str) -> dict[str, str]:
    """Recommend frontend framework."""
    defaults = {
        "mobile_app": {"framework": "React Native (Expo)", "language": "TypeScript", "reason": "Cross-platform mobile development with web skills."},
        "web_app": {"framework": "Next.js 16", "language": "TypeScript", "reason": "Full-stack React framework with SSR, routing, and optimal performance."},
        "ai_app": {"framework": "Next.js 16", "language": "TypeScript", "reason": "AI apps need modern React for real-time streaming UI updates."},
        "api_service": {"framework": "None (API only)", "language": "N/A", "reason": "No frontend needed for a pure API service."},
        "cli_tool": {"framework": "None (CLI only)", "language": "N/A", "reason": "Command-line interface, no web frontend needed."},
    }
    return defaults.get(proj_type, defaults["web_app"])


def _recommend_backend(proj_type: str) -> dict[str, str]:
    """Recommend backend framework."""
    defaults = {
        "mobile_app": {"framework": "FastAPI", "language": "Python 3.11+", "reason": "High-performance async API server with auto-generated OpenAPI docs."},
        "web_app": {"framework": "FastAPI", "language": "Python 3.11+", "reason": "Async Python backend with Pydantic validation and auto-docs."},
        "ai_app": {"framework": "FastAPI", "language": "Python 3.11+", "reason": "Python-native async framework ideal for AI/ML integration."},
        "api_service": {"framework": "FastAPI", "language": "Python 3.11+", "reason": "Purpose-built for APIs with automatic OpenAPI documentation."},
        "cli_tool": {"framework": "Typer (CLI)", "language": "Python 3.11+", "reason": "Python CLI framework built on Click, type-safe and auto-documented."},
    }
    return defaults.get(proj_type, defaults["web_app"])


def _recommend_database(proj_type: str, idea: str) -> dict[str, str]:
    """Recommend database based on project type and keywords."""
    realtime_keywords = ["realtime", "real-time", "live", "chat", "notification", "websocket"]
    document_keywords = ["content", "blog", "cms", "catalog", "product"]
    relational_keywords = ["payment", "transaction", "order", "account", "user", "inventory"]

    if any(kw in idea for kw in realtime_keywords):
        return {"database": "Supabase (PostgreSQL + Realtime)", "type": "relational+realtime", "reason": "PostgreSQL with built-in realtime subscriptions for live data sync."}
    if any(kw in idea for kw in document_keywords):
        return {"database": "MongoDB / PostgreSQL", "type": "document", "reason": "Flexible document model for content-heavy applications."}
    if any(kw in idea for kw in relational_keywords):
        return {"database": "PostgreSQL", "type": "relational", "reason": "ACID-compliant relational database with strong data integrity."}

    # Default by project type
    if proj_type == "mobile_app":
        return {"database": "Supabase (PostgreSQL)", "type": "relational", "reason": "Managed PostgreSQL with realtime sync for mobile backends."}
    if proj_type == "cli_tool":
        return {"database": "SQLite", "type": "embedded", "reason": "Zero-config, file-based database perfect for CLI tools."}

    return {"database": "PostgreSQL", "type": "relational", "reason": "Reliable, scalable, and widely-supported relational database."}


def _recommend_ai(idea: str) -> dict[str, str]:
    """Recommend AI provider if needed."""
    ai_keywords = ["ai", "llm", "gpt", "chatbot", "smart", "recommend", "personaliz", "predict",
                   "analyze", "insight", "automat", "intelligent", "learn", "ml"]

    if any(kw in idea for kw in ai_keywords):
        return {
            "provider": "opencode-go (GLM / DeepSeek)",
            "model": "glm-5.2 (reasoning), deepseek-v4-flash (cheap tasks)",
            "reason": "Cost-effective AI inference with OpenRouter-style routing and fallback.",
        }

    return {"provider": "None required", "model": "", "reason": "Project doesn't require AI features."}


def _recommend_auth(idea: str) -> dict[str, str]:
    """Recommend auth approach."""
    auth_keywords = ["user", "account", "login", "signup", "auth", "profile", "personaliz"]

    if any(kw in idea for kw in auth_keywords):
        return {"provider": "NextAuth.js / OAuth", "type": "OAuth + JWT", "reason": "Easy OAuth integration with Google, GitHub, and email magic links."}

    return {"provider": "None required", "type": "", "reason": "No user accounts needed for this project."}


def _recommend_hosting(proj_type: str) -> dict[str, str]:
    """Recommend hosting platform."""
    defaults = {
        "mobile_app": {"platform": "Vercel (frontend) + Railway (backend)", "reason": "Separate hosting for mobile API backend and any web dashboard."},
        "web_app": {"platform": "Vercel", "reason": "Optimal for Next.js with global CDN, automatic HTTPS, and zero-config deploys."},
        "ai_app": {"platform": "Vercel + Modal (GPU)", "reason": "Vercel for the frontend, Modal for GPU-accelerated AI inference tasks."},
        "api_service": {"platform": "Railway / Fly.io", "reason": "Simple API-focused hosting with fast cold starts and global regions."},
        "cli_tool": {"platform": "PyPI (pip install)", "reason": "Distributed as a Python package, no server hosting needed."},
    }
    return defaults.get(proj_type, defaults["web_app"])


def _get_explanations(stack: dict[str, Any]) -> dict[str, str]:
    """Return human-written explanations for each stack choice."""
    return {
        "frontend": (
            f"We recommend {stack['frontend']['framework']} ({stack['frontend']['language']}) "
            f"for the frontend. {stack['frontend']['reason']}"
        ),
        "backend": (
            f"For the backend, {stack['backend']['framework']} ({stack['backend']['language']}) "
            f"is the best choice. {stack['backend']['reason']}"
        ),
        "database": (
            f"Data should be stored in {stack['database']['database']}. "
            f"{stack['database']['reason']}"
        ),
        "ai": (
            f"{stack['ai']['provider']} handles AI inference. "
            f"{stack['ai']['reason']}"
        ),
        "auth": (
            f"{stack['auth']['provider']} handles authentication. "
            f"{stack['auth']['reason']}"
        ),
        "hosting": (
            f"Deploy on {stack['hosting']['platform']}. "
            f"{stack['hosting']['reason']}"
        ),
    }
