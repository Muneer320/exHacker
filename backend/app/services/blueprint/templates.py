"""Architecture templates — component layouts for common project types.

SDPD: Tier 0 (deterministic). These are pre-designed templates, not AI-generated.
AI enrichment (Tier 2) is used only to customize components for the specific idea.
"""

from __future__ import annotations

from typing import Any


WEB_APP: list[dict[str, Any]] = [
    {
        "name": "Frontend (Next.js)",
        "description": "React-based web application with server-side rendering",
        "responsibilities": [
            "User interface and interactions",
            "Client-side routing and state management",
            "Server-side rendering for SEO and performance",
            "API client for backend communication",
        ],
        "tech": "Next.js 16 + React 19",
        "sub_components": ["Pages/Routes", "Shared Components", "State Management (Zustand)", "API Client Layer"],
    },
    {
        "name": "Backend API (FastAPI)",
        "description": "Async Python API server handling business logic",
        "responsibilities": [
            "REST/JSON API endpoint implementation",
            "Business logic and data validation",
            "Authentication and authorization",
            "Background task processing",
        ],
        "tech": "FastAPI + Python 3.11+",
        "sub_components": ["API Routes", "Service Layer", "Middleware", "Background Workers"],
    },
    {
        "name": "Database (PostgreSQL)",
        "description": "Relational data storage with ACID compliance",
        "responsibilities": [
            "Persistent data storage",
            "Data integrity and relationships",
            "Query optimization and indexing",
            "Migration management",
        ],
        "tech": "PostgreSQL + SQLAlchemy",
        "sub_components": ["Schema/Migrations", "Query Layer", "Connection Pool"],
    },
    {
        "name": "Authentication Service",
        "description": "User identity and access management",
        "responsibilities": [
            "User registration and login",
            "OAuth provider integration",
            "Session management and JWT tokens",
            "Role-based access control",
        ],
        "tech": "NextAuth.js / OAuth 2.0",
        "sub_components": ["Auth Providers", "Session Store", "Permission Guards"],
    },
]

MOBILE_APP: list[dict[str, Any]] = [
    {
        "name": "Mobile App (React Native)",
        "description": "Cross-platform mobile application",
        "responsibilities": [
            "Mobile UI with native components",
            "Offline data and local storage",
            "Push notifications",
            "Camera/location/device API integration",
        ],
        "tech": "React Native (Expo)",
        "sub_components": ["Screens", "Navigation", "Native Modules", "Offline Cache"],
    },
    {
        "name": "Backend API (FastAPI)",
        "description": "Mobile app backend server",
        "responsibilities": [
            "Mobile API endpoints",
            "Data sync and conflict resolution",
            "Push notification dispatch",
            "File/media upload handling",
        ],
        "tech": "FastAPI + Python 3.11+",
        "sub_components": ["API Routes", "Push Service", "File Storage", "Sync Engine"],
    },
    {
        "name": "Database (Supabase)",
        "description": "Managed PostgreSQL with realtime capabilities",
        "responsibilities": [
            "User data storage",
            "Real-time data sync to mobile devices",
            "Row-level security policies",
        ],
        "tech": "Supabase (PostgreSQL)",
        "sub_components": ["Tables", "Realtime Subscriptions", "RLS Policies"],
    },
    {
        "name": "Authentication",
        "description": "Mobile-friendly authentication",
        "responsibilities": [
            "Social login (Google, Apple)",
            "Session management on device",
            "Biometric authentication support",
        ],
        "tech": "Supabase Auth / NextAuth.js",
        "sub_components": ["OAuth Flows", "Token Refresh", "Biometric Auth"],
    },
]

AI_APP: list[dict[str, Any]] = [
    {
        "name": "Frontend (Next.js)",
        "description": "Web UI with streaming AI response support",
        "responsibilities": [
            "Real-time AI response streaming UI",
            "Prompt input and conversation management",
            "Loading states and progress indicators",
        ],
        "tech": "Next.js 16 + Server-Sent Events",
        "sub_components": ["Chat/Stream UI", "Prompt Input", "Response Renderer"],
    },
    {
        "name": "AI Gateway Service",
        "description": "LLM provider routing and prompt management",
        "responsibilities": [
            "Multi-provider AI calls with fallback",
            "Prompt engineering and templating",
            "Cost tracking and rate limiting",
            "Streaming response handling",
        ],
        "tech": "FastAPI + LiteLLM",
        "sub_components": ["Model Router", "Prompt Manager", "Cost Tracker", "Stream Handler"],
    },
    {
        "name": "Backend API (FastAPI)",
        "description": "Application server and data management",
        "responsibilities": [
            "Business logic and data API",
            "Conversation/session storage",
            "Usage analytics",
        ],
        "tech": "FastAPI + Python 3.11+",
        "sub_components": ["API Routes", "Session Store", "Analytics"],
    },
    {
        "name": "Database (PostgreSQL)",
        "description": "Persistent storage for user data and AI interactions",
        "responsibilities": [
            "User accounts and preferences",
            "Conversation history",
            "Usage and billing data",
        ],
        "tech": "PostgreSQL + pgvector",
        "sub_components": ["Tables", "Vector Storage", "Migrations"],
    },
]

API_SERVICE: list[dict[str, Any]] = [
    {
        "name": "API Gateway",
        "description": "Entry point for all API requests",
        "responsibilities": [
            "Request routing and load balancing",
            "Rate limiting and authentication",
            "API versioning",
            "Request/response logging",
        ],
        "tech": "FastAPI + API Key Auth",
        "sub_components": ["Routes", "Middleware", "Rate Limiter"],
    },
    {
        "name": "Service Layer",
        "description": "Business logic and data processing",
        "responsibilities": [
            "Core business logic",
            "External service integration",
            "Data transformation and validation",
        ],
        "tech": "Python 3.11+",
        "sub_components": ["Services", "Integrations", "Validators"],
    },
    {
        "name": "Database (PostgreSQL)",
        "description": "Data persistence layer",
        "responsibilities": [
            "Structured data storage",
            "Query performance and indexing",
        ],
        "tech": "PostgreSQL + SQLAlchemy",
        "sub_components": ["Tables", "Migrations", "Query Layer"],
    },
]

CLI_TOOL: list[dict[str, Any]] = [
    {
        "name": "CLI Entry Point",
        "description": "Command-line interface with subcommands",
        "responsibilities": [
            "Command parsing and dispatch",
            "Help text and auto-completion",
            "Configuration file management",
        ],
        "tech": "Typer (Python)",
        "sub_components": ["Commands", "Arguments", "Config"],
    },
    {
        "name": "Core Logic",
        "description": "Tool functionality implementation",
        "responsibilities": [
            "Core algorithm/transformation logic",
            "File I/O and data processing",
        ],
        "tech": "Python 3.11+",
        "sub_components": ["Processors", "Utilities"],
    },
]

TEMPLATES: dict[str, list[dict[str, Any]]] = {
    "web_app": WEB_APP,
    "mobile_app": MOBILE_APP,
    "ai_app": AI_APP,
    "api_service": API_SERVICE,
    "cli_tool": CLI_TOOL,
}


def get_template(project_type: str) -> list[dict[str, Any]]:
    """Get the architecture template for a project type."""
    return TEMPLATES.get(project_type, TEMPLATES["web_app"])


def list_templates() -> list[str]:
    """List available architecture template types."""
    return list(TEMPLATES.keys())
