"""API Contract Generator — deterministic endpoint templates.

SDPD: Tier 0 (deterministic). CRUD endpoints follow patterns.
Custom endpoints added via keyword detection, not AI.
"""

from __future__ import annotations

from typing import Any


def generate_api_contracts(data_model: dict[str, Any]) -> dict[str, Any]:
    """Generate API contracts from a data model.

    Each entity gets standard CRUD endpoints.
    Custom endpoints are added based on entity type.

    Args:
        data_model: The data model with entities and relationships.

    Returns:
        API contracts with endpoints grouped by entity.
    """
    endpoints = []

    for entity in data_model.get("entities", []):
        name = entity["name"]
        endpoints.extend(_crud_endpoints(name))

        # Custom endpoints per entity type
        custom = _custom_endpoints(name)
        endpoints.extend(custom)

    return {
        "endpoints": endpoints,
        "format": "REST/JSON",
        "base_url": "/api/v1",
        "auth": "Bearer JWT token in Authorization header",
    }


def _crud_endpoints(entity: str) -> list[dict[str, str]]:
    """Generate standard CRUD endpoints for an entity."""
    base_path = f"/{entity}s"
    return [
        {
            "method": "GET",
            "path": base_path,
            "description": f"List all {entity}s",
            "auth": "Required",
        },
        {
            "method": "POST",
            "path": base_path,
            "description": f"Create a new {entity}",
            "auth": "Required",
        },
        {
            "method": "GET",
            "path": f"{base_path}/{{id}}",
            "description": f"Get a single {entity} by ID",
            "auth": "Required",
        },
        {
            "method": "PATCH",
            "path": f"{base_path}/{{id}}",
            "description": f"Update a {entity}",
            "auth": "Required",
        },
        {
            "method": "DELETE",
            "path": f"{base_path}/{{id}}",
            "description": f"Delete a {entity}",
            "auth": "Required",
        },
    ]


def _custom_endpoints(entity: str) -> list[dict[str, str]]:
    """Return custom endpoints for specific entity types."""
    custom_map = {
        "user": [
            {"method": "POST", "path": "/auth/register", "description": "Register a new user", "auth": "None"},
            {"method": "POST", "path": "/auth/login", "description": "Login and receive JWT", "auth": "None"},
            {"method": "POST", "path": "/auth/refresh", "description": "Refresh access token", "auth": "Required"},
            {"method": "GET", "path": "/me", "description": "Get current user profile", "auth": "Required"},
        ],
        "transaction": [
            {"method": "GET", "path": "/transactions/summary", "description": "Get spending summary by category", "auth": "Required"},
            {"method": "GET", "path": "/transactions/recent", "description": "Get recent transactions", "auth": "Required"},
        ],
        "budget": [
            {"method": "GET", "path": "/budgets/summary", "description": "Get budget overview with spending vs limits", "auth": "Required"},
        ],
        "conversation": [
            {"method": "POST", "path": "/conversations/{id}/messages", "description": "Send a message in a conversation", "auth": "Required"},
            {"method": "GET", "path": "/conversations/{id}/messages", "description": "Get messages for a conversation", "auth": "Required"},
        ],
        "project": [
            {"method": "PATCH", "path": "/projects/{id}/status", "description": "Update project status", "auth": "Required"},
        ],
        "order": [
            {"method": "POST", "path": "/orders/{id}/checkout", "description": "Complete checkout for an order", "auth": "Required"},
        ],
    }
    return custom_map.get(entity, [])
