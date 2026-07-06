"""Data Model Generator — deterministic entity templates.

SDPD: Tier 0 (deterministic). No AI is used.
Entities are generated from templates based on the project type and idea keywords.
Custom entity detection uses keyword matching, not AI.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Common entities with their fields
ENTITY_TEMPLATES: dict[str, list[dict[str, str]]] = {
    "user": [
        {"name": "id", "type": "UUID", "description": "Primary key"},
        {"name": "email", "type": "string", "description": "User email address"},
        {"name": "name", "type": "string", "description": "Display name"},
        {"name": "avatar_url", "type": "string?", "description": "Profile picture URL"},
        {"name": "created_at", "type": "timestamp", "description": "Account creation date"},
    ],
    "project": [
        {"name": "id", "type": "UUID", "description": "Primary key"},
        {"name": "user_id", "type": "UUID", "description": "Owner reference"},
        {"name": "name", "type": "string", "description": "Project name"},
        {"name": "description", "type": "text?", "description": "Detailed description"},
        {"name": "status", "type": "enum", "description": "Current state"},
        {"name": "created_at", "type": "timestamp", "description": "Creation date"},
    ],
    "task": [
        {"name": "id", "type": "UUID", "description": "Primary key"},
        {"name": "project_id", "type": "UUID", "description": "Parent project"},
        {"name": "title", "type": "string", "description": "Task title"},
        {"name": "status", "type": "enum", "description": "todo/in_progress/done"},
        {"name": "priority", "type": "enum", "description": "low/medium/high"},
        {"name": "due_date", "type": "timestamp?", "description": "Deadline"},
    ],
    "transaction": [
        {"name": "id", "type": "UUID", "description": "Primary key"},
        {"name": "user_id", "type": "UUID", "description": "User reference"},
        {"name": "amount", "type": "decimal", "description": "Transaction amount"},
        {"name": "category", "type": "string", "description": "Spending category"},
        {"name": "description", "type": "text?", "description": "Transaction note"},
        {"name": "date", "type": "timestamp", "description": "Transaction date"},
    ],
    "budget": [
        {"name": "id", "type": "UUID", "description": "Primary key"},
        {"name": "user_id", "type": "UUID", "description": "User reference"},
        {"name": "category", "type": "string", "description": "Budget category"},
        {"name": "limit", "type": "decimal", "description": "Monthly spending limit"},
        {"name": "spent", "type": "decimal", "description": "Current month spending"},
        {"name": "period", "type": "string", "description": "Budget period (monthly/yearly)"},
    ],
    "goal": [
        {"name": "id", "type": "UUID", "description": "Primary key"},
        {"name": "user_id", "type": "UUID", "description": "User reference"},
        {"name": "title", "type": "string", "description": "Goal name"},
        {"name": "target_amount", "type": "decimal", "description": "Target amount"},
        {"name": "current_amount", "type": "decimal", "description": "Saved so far"},
        {"name": "deadline", "type": "timestamp?", "description": "Target date"},
    ],
    "conversation": [
        {"name": "id", "type": "UUID", "description": "Primary key"},
        {"name": "user_id", "type": "UUID", "description": "User reference"},
        {"name": "title", "type": "string", "description": "Conversation title"},
        {"name": "model", "type": "string", "description": "AI model used"},
        {"name": "created_at", "type": "timestamp", "description": "Start time"},
    ],
    "message": [
        {"name": "id", "type": "UUID", "description": "Primary key"},
        {"name": "conversation_id", "type": "UUID", "description": "Parent conversation"},
        {"name": "role", "type": "enum", "description": "user/assistant/system"},
        {"name": "content", "type": "text", "description": "Message content"},
        {"name": "created_at", "type": "timestamp", "description": "Send time"},
    ],
    "product": [
        {"name": "id", "type": "UUID", "description": "Primary key"},
        {"name": "name", "type": "string", "description": "Product name"},
        {"name": "description", "type": "text", "description": "Product description"},
        {"name": "price", "type": "decimal", "description": "Unit price"},
        {"name": "category", "type": "string", "description": "Product category"},
        {"name": "stock", "type": "integer", "description": "Inventory count"},
    ],
    "order": [
        {"name": "id", "type": "UUID", "description": "Primary key"},
        {"name": "user_id", "type": "UUID", "description": "Customer reference"},
        {"name": "status", "type": "enum", "description": "pending/paid/shipped/delivered"},
        {"name": "total", "type": "decimal", "description": "Order total"},
        {"name": "items", "type": "json", "description": "Line items array"},
        {"name": "created_at", "type": "timestamp", "description": "Order date"},
    ],
}

# Keyword → entity mappings
KEYWORD_ENTITIES: list[tuple[list[str], str]] = [
    (["user", "account", "profile", "login", "signup", "auth", "member"], "user"),
    (["project", "workspace", "repository", "app"], "project"),
    (["task", "todo", "issue", "ticket", "chore", "assignment"], "task"),
    (["transaction", "payment", "purchase", "spending", "expense", "income"], "transaction"),
    (["budget", "saving", "financial", "finance", "money"], "budget"),
    (["goal", "target", "milestone", "objective", "habit"], "goal"),
    (["chat", "message", "conversation", "dialog", "ai", "bot"], "conversation"),
    (["product", "item", "catalog", "inventory", "listing"], "product"),
    (["order", "cart", "checkout", "invoice", "purchase"], "order"),
]

RELATIONSHIP_KEYWORDS: dict[str, list[tuple[str, str, str]]] = {
    "user": [
        ("project", "1:N", "user has many projects"),
        ("task", "1:N", "user has many tasks"),
        ("transaction", "1:N", "user has many transactions"),
        ("budget", "1:N", "user has many budgets"),
        ("goal", "1:N", "user has many goals"),
        ("conversation", "1:N", "user has many conversations"),
        ("order", "1:N", "user has many orders"),
    ],
    "project": [
        ("task", "1:N", "project has many tasks"),
    ],
    "conversation": [
        ("message", "1:N", "conversation has many messages"),
    ],
    "order": [
        ("product", "N:M", "order contains many products"),
    ],
}


def generate_data_model(idea: str) -> dict[str, Any]:
    """Generate a data model from a project idea.

    Uses keyword matching to detect relevant entities.
    No AI is involved.

    Args:
        idea: The project idea text.

    Returns:
        Data model with entities, relationships, and notes.
    """
    idea_lower = idea.lower()

    # Detect relevant entities
    detected_entities: list[str] = []
    for keywords, entity_name in KEYWORD_ENTITIES:
        if any(kw in idea_lower for kw in keywords):
            if entity_name not in detected_entities:
                detected_entities.append(entity_name)

    # Always include User if any entity needs user reference
    if any(e in detected_entities for e in ["project", "task", "transaction", "budget", "goal", "conversation", "order"]):
        if "user" not in detected_entities:
            detected_entities.insert(0, "user")

    # Build entity definitions
    entities = []
    for name in detected_entities:
        template = ENTITY_TEMPLATES.get(name)
        if template:
            entities.append({
                "name": name,
                "fields": template,
            })

    # Build relationships
    relationships = []
    known = set(detected_entities)
    for source_name in detected_entities:
        source_rels = RELATIONSHIP_KEYWORDS.get(source_name, [])
        for target_name, rel_type, description in source_rels:
            if target_name in known:
                relationships.append({
                    "from": source_name,
                    "to": target_name,
                    "type": rel_type,
                    "description": description,
                })

    return {
        "entities": entities,
        "relationships": relationships,
        "notes": _generate_data_notes(entities, idea),
    }


def _generate_data_notes(entities: list[dict[str, Any]], idea: str) -> list[str]:
    """Generate helpful notes about the data model."""
    notes = []
    if not entities:
        notes.append("No specific entities detected. Consider starting with a simple data structure.")
    else:
        entity_names = [e["name"] for e in entities]
        notes.append(f"Core entities: {', '.join(entity_names)}.")
        total_fields = sum(len(e["fields"]) for e in entities)
        notes.append(f"Total fields across all entities: {total_fields}.")

    notes.append("Data model can be extended as requirements evolve.")
    return notes
