"""Document templates — deterministic markdown generators (Bible §6.2 S13).

SDPD: Tier 0 — all templates are deterministic.
AI is used ONLY for introductions and narrative transitions (Tier 1).
"""

from __future__ import annotations

from typing import Any


def prd(data: dict[str, Any]) -> str:
    i = data.get("idea", {})
    c = data.get("challenge", {})
    return f"""# PRD — Product Requirements Document

> **Status:** Draft v1
> **Version:** 1.0
> **Generated:** {data.get("generated_at", "")}

## 1. Executive Summary

{i.get("elevator_pitch", data.get("pitch", "A hackathon project."))}

## 2. Problem

**Problem Statement:** {i.get("problem_statement", "TBD")}

**Target Users:** {i.get("target_users", "TBD")}

**Why Now:** {i.get("why_now", "TBD")}

## 3. Solution

**Solution Overview:** {i.get("solution", "TBD")}

**Unique Selling Proposition:** {i.get("usp", "TBD")}

## 4. Features

### Core Features
{_feat_list(i.get("core_features", ["TBD"]))}

### Stretch Features
{_feat_list(i.get("stretch_features", []))}

## 5. Success Metrics

| Metric | Target | Measurement |
|---|---|---|
| User engagement | Active daily use | DAU/MAU |
| Time to value | < 2 min | First insight time |
| Demo quality | Judges remember | Pitch feedback |

## 6. Roadmap

{_roadmap(i.get("future_roadmap", []))}
"""


def readme(data: dict[str, Any]) -> str:
    i = data.get("idea", {})
    arch = data.get("architecture", {})
    project = data.get("project", {})
    idea_title = i.get("title", data.get("project_name", "exHacker Project"))
    return f"""# {idea_title}

> {i.get("hook", "A hackathon project.")}

## Overview

{i.get("elevator_pitch", "A project built for a hackathon.")}

## Features

{_feat_list(i.get("core_features", ["Feature 1", "Feature 2"]))}

## Architecture

**Frontend:** {arch.get("frontend", {}).get("framework", "TBD")}
**Backend:** {arch.get("backend", {}).get("framework", "TBD")}
**Database:** {_db_info(arch)}

## Quick Start

```bash
# Clone the repository
git clone https://github.com/your-org/{idea_title.lower().replace(' ', '-')}
cd {idea_title.lower().replace(' ', '-')}

# Install dependencies
npm install
pip install -r requirements.txt

# Start development
npm run dev
```

## Project Structure

```
{_folder_structure(arch)}
```

## Team

{project.get("team_size", "4")} members · {project.get("available_hours", "48")} hours

## License

MIT
"""


def tech_stack(data: dict[str, Any]) -> str:
    arch = data.get("architecture", {})
    tradeoffs = arch.get("tradeoffs", [])
    lines = ["# Tech Stack\n"]
    lines.append("> Every technology chosen with rationale, alternatives, and trade-offs.\n")

    # Frontend
    fe = arch.get("frontend", {})
    lines.append("## Frontend\n")
    lines.append(f"- **Framework:** {fe.get('framework', 'TBD')}")
    if fe.get("state_management"):
        lines.append(f"- **State Management:** {fe['state_management']}")
    lines.append("")

    # Backend
    be = arch.get("backend", {})
    lines.append("## Backend\n")
    lines.append(f"- **Framework:** {be.get('framework', 'TBD')}")
    if be.get("modules"):
        lines.append(f"- **Modules:** {', '.join(be['modules'])}")
    lines.append("")

    # Auth
    auth = arch.get("authentication", {})
    if auth.get("provider"):
        lines.append("## Authentication\n")
        lines.append(f"- **Provider:** {auth['provider']}")
        if auth.get("model"):
            lines.append(f"- **Model:** {auth['model']}")
        lines.append("")

    # Trade-offs
    if tradeoffs:
        lines.append("## Trade-offs\n")
        for t in tradeoffs[:5]:
            lines.append(f"### {t.get('decision', 'Decision')}")
            lines.append(f"**Rationale:** {t.get('rationale', '')}")
            if t.get("alternatives"):
                lines.append(f"**Alternatives considered:** {', '.join(t['alternatives'])}")
            if t.get("pros"):
                lines.append(f"**Pros:** {'; '.join(t['pros'])}")
            if t.get("cons"):
                lines.append(f"**Cons:** {'; '.join(t['cons'])}")
            lines.append("")

    return "\n".join(lines)


def architecture_doc(data: dict[str, Any]) -> str:
    arch = data.get("architecture", {})
    lines = ["# Architecture\n"]
    lines.append(f"> {arch.get('system_overview', 'Architecture overview')}\n")

    if arch.get("architecture_rationale"):
        lines.append("## Rationale\n")
        lines.append(f"{arch['architecture_rationale']}\n")

    if arch.get("components"):
        lines.append("## Components\n")
        for comp in arch["components"]:
            lines.append(f"### {comp.get('name', 'Component')}")
            lines.append(f"- **Tech:** {comp.get('tech', '')}")
            lines.append(f"- **Purpose:** {comp.get('purpose', '')}")
            lines.append(f"- **Description:** {comp.get('description', '')}")
            lines.append("")

    if arch.get("mermaid_system"):
        lines.append("## System Diagram\n")
        lines.append("```mermaid")
        lines.append(arch["mermaid_system"])
        lines.append("```\n")

    if arch.get("mermaid_data_flow"):
        lines.append("## Data Flow\n")
        lines.append("```mermaid")
        lines.append(arch["mermaid_data_flow"])
        lines.append("```\n")

    review = arch.get("review", {})
    if review.get("weak_points"):
        lines.append("## Architecture Review\n")
        lines.append("### Weak Points\n")
        for w in review["weak_points"]:
            lines.append(f"- {w}")
        lines.append("")
    if review.get("failure_modes"):
        lines.append("### Failure Modes\n")
        for f in review["failure_modes"]:
            lines.append(f"- {f}")
        lines.append("")

    return "\n".join(lines)


def api_doc(data: dict[str, Any]) -> str:
    arch = data.get("architecture", {})
    contracts = arch.get("api_contracts", [])
    lines = ["# API Documentation\n"]

    auth = arch.get("authentication", {})
    if auth.get("model"):
        lines.append(f"## Authentication\n{auth['model']}\n")

    lines.append("## Endpoints\n")
    for ep in contracts:
        lines.append(f"### `{ep.get('method', 'GET')} {ep.get('path', '/')}`")
        if ep.get("description"):
            lines.append(f"_{ep['description']}_\n")
        if ep.get("request"):
            lines.append("**Request:**")
            lines.append(f"```json\n{_json(ep['request'])}\n```")
        if ep.get("response"):
            lines.append("**Response:**")
            lines.append(f"```json\n{_json(ep['response'])}\n```")
        if ep.get("errors"):
            lines.append(f"**Errors:** {', '.join(ep['errors'])}")
        lines.append("")

    return "\n".join(lines)


def database_doc(data: dict[str, Any]) -> str:
    arch = data.get("architecture", {})
    db = arch.get("database", {})
    entities = db.get("entities", [])
    relationships = db.get("relationships", [])
    lines = ["# Database Design\n"]

    if db.get("notes"):
        lines.append(f"> {db['notes']}\n")

    if db.get("mermaid_er"):
        lines.append("## Entity Relationship Diagram\n")
        lines.append("```mermaid")
        lines.append(db["mermaid_er"])
        lines.append("```\n")

    lines.append("## Entities\n")
    for ent in entities:
        lines.append(f"### {ent.get('name', 'Entity')}")
        fields = ent.get("fields", [])
        if fields:
            lines.append("| Field | Type | Constraints |")
            lines.append("|---|---|---|")
            for f in fields:
                pk = "PK" if f.get("pk") else ""
                unique = "UNIQUE" if f.get("unique") else ""
                constraints = " | ".join(filter(None, [pk, unique]))
                lines.append(f"| {f.get('name', '')} | {f.get('type', '')} | {constraints} |")
        lines.append("")

    if relationships:
        lines.append("## Relationships\n")
        lines.append("| From | To | Type |")
        lines.append("|---|---|---|")
        for r in relationships:
            lines.append(f"| {r.get('from', '')} | {r.get('to', '')} | {r.get('type', '')} |")
        lines.append("")

    return "\n".join(lines)


def frontend_doc(data: dict[str, Any]) -> str:
    arch = data.get("architecture", {})
    fe = arch.get("frontend", {})
    lines = ["# Frontend Architecture\n"]
    lines.append(f"**Framework:** {fe.get('framework', 'TBD')}\n")

    if fe.get("folder_structure"):
        lines.append("## Folder Structure\n")
        lines.append("```")
        for folder in fe["folder_structure"]:
            lines.append(folder)
        lines.append("```\n")

    if fe.get("component_hierarchy"):
        lines.append("## Component Hierarchy\n")
        for c in fe["component_hierarchy"]:
            lines.append(f"- {c}")
        lines.append("")

    if fe.get("state_management"):
        lines.append(f"**State Management:** {fe['state_management']}\n")

    if fe.get("routing"):
        lines.append("## Routing\n")
        lines.append("| Path | Component | Auth Required |")
        lines.append("|---|---|---|")
        for r in fe["routing"]:
            auth = "✓" if r.get("auth") else ""
            lines.append(f"| {r.get('path', '')} | {r.get('component', '')} | {auth} |")
        lines.append("")

    return "\n".join(lines)


def backend_doc(data: dict[str, Any]) -> str:
    arch = data.get("architecture", {})
    be = arch.get("backend", {})
    lines = ["# Backend Architecture\n"]
    lines.append(f"**Framework:** {be.get('framework', 'TBD')}\n")

    if be.get("modules"):
        lines.append("## Modules\n")
        for m in be["modules"]:
            lines.append(f"- {m}")
        lines.append("")

    if be.get("api_organization"):
        lines.append("## API Organization\n")
        for org in be["api_organization"]:
            lines.append(f"- `{org.get('prefix', '')}` — {org.get('description', '')}")
        lines.append("")

    return "\n".join(lines)


def implementation_plan(data: dict[str, Any]) -> str:
    idea = data.get("idea", {})
    arch = data.get("architecture", {})
    sc = arch.get("scalability", {})
    hours = idea.get("estimated_build_hours", 48)
    difficulty = idea.get("estimated_difficulty", 50)
    roles = idea.get("recommended_roles", ["Frontend", "Backend", "Designer", "PM"])
    team_size = data.get("project", {}).get("team_size", "4")
    available = data.get("project", {}).get("available_hours", "48")

    lines = ["# Implementation Plan\n"]

    lines.append("## Overview\n")
    lines.append(f"- **Estimated effort:** {hours} hours\n- **Difficulty:** {difficulty}/100\n- **Team:** {team_size} members\n- **Available:** {available}\n")

    lines.append("## Team Roles\n")
    for role in roles[:6]:
        lines.append(f"- {role}")
    lines.append("")

    roadmap = idea.get("future_roadmap", [])
    if roadmap:
        lines.append("## Milestones\n")
        for i, rm in enumerate(roadmap):
            lines.append(f"### Phase {i + 1}")
            lines.append(f"- {rm}")
            lines.append(f"  - Estimated: ~{hours // max(len(roadmap), 1)}h")
            lines.append(f"  - Parallel: {'✓' if i > 0 else ''}")
            lines.append("")

    if sc.get("hackathon_version"):
        lines.append("## Hackathon Version\n")
        lines.append(f"{sc['hackathon_version']}\n")

    if sc.get("production_version"):
        lines.append("## Production Path\n")
        lines.append(f"{sc['production_version']}\n")

    return "\n".join(lines)


def pitch_doc(data: dict[str, Any]) -> str:
    i = data.get("idea", {})
    c = data.get("challenge", {})
    lines = ["# Pitch Guide\n"]

    lines.append("## Problem\n")
    lines.append(f"{i.get('problem_statement', 'TBD')}\n")

    lines.append("## Solution\n")
    lines.append(f"{i.get('solution', 'TBD')}\n")

    lines.append(f"**Hook:** {i.get('hook', '')}\n")

    lines.append("## Innovation\n")
    lines.append(f"{i.get('innovation_summary', '')}\n")

    lines.append("## Demo Order\n")
    fallback_demo = "1. Open app\\n2. Show key feature\\n3. Deliver wow moment"
    lines.append(f"{i.get('demo_scenario', fallback_demo)}\\n")

    lines.append("## Judge Wow Moment\n")
    lines.append(f"{i.get('judge_wow_moment', 'TBD')}\n")

    if i.get("usp"):
        lines.append("## What Makes This Different\n")
        lines.append(f"{i['usp']}\n")

    opportunity_areas = c.get("opportunity_areas", [])
    if opportunity_areas:
        lines.append("## Relevant Themes\n")
        for oa in opportunity_areas[:5]:
            lines.append(f"- {oa}")
        lines.append("")

    return "\n".join(lines)


# ─── Helpers ─────────────────────────────────────────────────────────────


def _feat_list(features: list[str]) -> str:
    if not features:
        return ""
    return "\n".join(f"- {f}" for f in features)


def _roadmap(steps: list[str]) -> str:
    if not steps:
        return "TBD"
    return "\n".join(f"{i + 1}. {s}" for i, s in enumerate(steps))


def _db_info(arch: dict[str, Any]) -> str:
    db = arch.get("database", {})
    entities = db.get("entities", [])
    names = [e.get("name", "") for e in entities]
    return ", ".join(names) if names else "TBD"


def _folder_structure(arch: dict[str, Any]) -> str:
    fe = arch.get("frontend", {})
    be = arch.get("backend", {})
    lines = []
    if fe.get("folder_structure"):
        for f in fe["folder_structure"]:
            lines.append(f"├── frontend/{f}/")
    if be.get("modules"):
        for m in be["modules"]:
            lines.append(f"├── backend/{m}/")
    return "\n".join(lines) if lines else "├── src/\n├── docs/\n└── tests/"


def _json(obj: Any) -> str:
    import json
    return json.dumps(obj, indent=2)


# ─── Document Registry ───────────────────────────────────────────────────

DOCUMENTS = {
    "README.md": {"title": "README", "description": "Project overview and quick start", "generator": readme},
    "PRD.md": {"title": "Product Requirements Document", "description": "Problem, solution, features, success metrics", "generator": prd},
    "TECH_STACK.md": {"title": "Technology Stack", "description": "Every technology with rationale and trade-offs", "generator": tech_stack},
    "ARCHITECTURE.md": {"title": "Architecture", "description": "System architecture, components, and diagrams", "generator": architecture_doc},
    "API.md": {"title": "API Documentation", "description": "All endpoints, schemas, and authentication", "generator": api_doc},
    "DATABASE.md": {"title": "Database Design", "description": "Entities, relationships, and ER diagrams", "generator": database_doc},
    "FRONTEND.md": {"title": "Frontend Architecture", "description": "Pages, components, state, and routing", "generator": frontend_doc},
    "BACKEND.md": {"title": "Backend Architecture", "description": "Modules, services, and folder structure", "generator": backend_doc},
    "IMPLEMENTATION_PLAN.md": {"title": "Implementation Plan", "description": "Milestones, priorities, and parallel work", "generator": implementation_plan},
    "PITCH.md": {"title": "Pitch Guide", "description": "Problem, solution, innovation, demo order", "generator": pitch_doc},
}
