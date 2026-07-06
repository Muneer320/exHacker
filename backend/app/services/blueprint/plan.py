"""Plan Generator — deterministic task generation from architecture components.

SDPD: Tier 0 (deterministic). Tasks are generated from component definitions.
No AI is used — each component produces known, repeatable tasks.
"""

from __future__ import annotations

from typing import Any


def generate_plan(architecture: dict[str, Any]) -> dict[str, Any]:
    """Generate an implementation plan from architecture components.

    Each component produces setup, implementation, and integration tasks.
    Tasks are grouped into phases by dependency order.

    Args:
        architecture: Architecture dict with components.

    Returns:
        Plan with phases, tasks, and estimated effort.
    """
    components = architecture.get("components", [])
    if not components:
        return {"phases": [], "total_tasks": 0, "estimated_hours": 0}

    phases = []
    total_tasks = 0
    total_hours = 0

    # Phase 1: Foundation (always first)
    phase1_tasks = _phase1_tasks(components)
    phase1_hours = sum(t["estimated_hours"] for t in phase1_tasks)
    phases.append({
        "name": "Foundation",
        "description": "Project setup, core infrastructure, and shared dependencies.",
        "tasks": phase1_tasks,
        "estimated_hours": phase1_hours,
    })
    total_hours += phase1_hours
    total_tasks += len(phase1_tasks)

    # Phase 2: Core features (one task per main component)
    for component in components:
        comp_tasks = _component_tasks(component)
        if comp_tasks:
            comp_hours = sum(t["estimated_hours"] for t in comp_tasks)
            phases.append({
                "name": component["name"],
                "description": component.get("description", ""),
                "tasks": comp_tasks,
                "estimated_hours": comp_hours,
            })
            total_hours += comp_hours
            total_tasks += len(comp_tasks)

    # Phase 3: Integration & Polish
    phase3_tasks = _phase3_tasks()
    phase3_hours = sum(t["estimated_hours"] for t in phase3_tasks)
    phases.append({
        "name": "Integration & Polish",
        "description": "API integration, error handling, testing, and deployment.",
        "tasks": phase3_tasks,
        "estimated_hours": phase3_hours,
    })
    total_hours += phase3_hours
    total_tasks += len(phase3_tasks)

    return {
        "phases": phases,
        "total_tasks": total_tasks,
        "estimated_hours": total_hours,
    }


def _phase1_tasks(components: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Generate foundation tasks that apply to every project."""
    tasks = [
        {"title": "Initialize project repository", "description": "Set up version control with Git, create project structure.", "estimated_hours": 1},
        {"title": "Configure development environment", "description": "Set up linting, formatting, type checking, and dev scripts.", "estimated_hours": 1},
        {"title": "Set up database and ORM", "description": "Initialize database, create initial schema migrations.", "estimated_hours": 2},
        {"title": "Implement authentication", "description": "Set up user registration, login, JWT token management.", "estimated_hours": 4},
        {"title": "Set up CI/CD pipeline", "description": "Configure automated testing, building, and deployment.", "estimated_hours": 2},
    ]
    return tasks


def _component_tasks(component: dict[str, Any]) -> list[dict[str, Any]]:
    """Generate tasks for a single architecture component."""
    name = component.get("name", "")
    sub_components = component.get("sub_components", [])
    tech = component.get("tech", "")

    tasks = [
        {"title": f"Set up {name}", "description": f"Initialize {name} using {tech} with project conventions.", "estimated_hours": 2},
    ]

    for sub in sub_components[:4]:  # Max 4 sub-component tasks
        tasks.append({
            "title": f"Implement {sub}",
            "description": f"Build and integrate {sub} within {name}.",
            "estimated_hours": 3,
        })

    tasks.append({
        "title": f"Test {name}",
        "description": f"Write unit and integration tests for {name}.",
        "estimated_hours": 2,
    })

    return tasks


def _phase3_tasks() -> list[dict[str, Any]]:
    """Generate final integration and polish tasks."""
    return [
        {"title": "End-to-end testing", "description": "Write and run end-to-end tests covering the main user flows.", "estimated_hours": 3},
        {"title": "Error handling and edge cases", "description": "Add error boundaries, loading states, and fallback UIs.", "estimated_hours": 2},
        {"title": "Performance optimization", "description": "Profile and optimize database queries, bundle size, and rendering.", "estimated_hours": 2},
        {"title": "Deploy to production", "description": "Configure production environment, domain, SSL, and monitoring.", "estimated_hours": 2},
        {"title": "Write documentation", "description": "Create README, API docs, and setup guide for contributors.", "estimated_hours": 1},
    ]
