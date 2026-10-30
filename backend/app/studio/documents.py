"""Reproducible Markdown compiled from the confirmed project snapshot."""

import hashlib
import json

from app.studio.schemas import Specification, Stack


def bullets(items):
    return "\n".join(f"- {item}" for item in items) or "- None recorded."


def section(title, text):
    return f"\n## {title}\n\n{text}\n"


def team_text(intake):
    return bullets(
        [
            f"{m['name']} — {m.get('role') or 'Builder'}; "
            + ", ".join(f"{s['technology']} ({s['proficiency']})" for s in m["skills"])
            + f"; capacity: {m.get('hours_available') or intake['available_hours']}h"
            for m in intake["teammates"]
        ]
    )


def compile_documents(
    intake: dict,
    idea: dict,
    stack: Stack,
    spec: Specification,
    revision: int,
    generated_at: str,
    research: dict,
    demo: bool,
) -> dict:
    title = idea["title"]
    header = f"> Project revision: {revision} · Generated: {generated_at}\n"
    if demo:
        header += "> DEMONSTRATION: sample planning content; no live research or AI validation.\n"
    stack_text = "\n".join(
        f"### {c.category}: {c.technology}\n\n**Used for:** {c.purpose}\n\n**Why:** {c.rationale}\n\n"
        + "**Alternatives:** "
        + ", ".join(c.alternatives)
        + "\n\n"
        + bullets(c.tradeoffs)
        + "\n"
        for c in stack.choices
    )
    constraints = bullets(
        [
            f"Time limit: {intake['available_hours']} hours; reserve 20% for integration and rehearsal.",
            f"Hackathon: {intake.get('hackathon') or 'Not specified'}",
            f"Platform: {intake['target_platform']}",
            f"Judging rubric: {intake.get('judging_criteria') or 'Not supplied; judging scores are estimates.'}",
            f"Rules: {intake.get('rules') or 'No additional rules supplied'}",
            f"Required technologies: {intake.get('required_technologies') or 'None specified'}",
            f"Excluded technologies: {intake.get('excluded_technologies') or 'None specified'}",
            f"Budget: {intake.get('budget') or 'Not specified; verify service pricing before committing.'}",
            f"Other constraints: {intake.get('constraints') or 'None supplied'}",
        ]
    )
    requirements = "\n".join(
        f"### {r.id}: {r.title} ({r.priority})\n\n{r.user_story}\n\n{r.behavior}\n\n"
        + "**Acceptance criteria**\n\n"
        + bullets(r.acceptance_criteria)
        + "\n\n**Edge cases and failure behavior**\n\n"
        + bullets(r.edge_cases)
        + "\n"
        for r in spec.requirements
    )
    entities = "\n".join(
        f"### {e.name}\n\n**Fields and types**\n\n{bullets(e.fields)}\n\n"
        f"**Relationships**\n\n{bullets(e.relationships)}\n\n**Validation and integrity**\n\n{bullets(e.validation)}\n"
        for e in spec.entities
    )
    endpoints = "\n".join(
        f"### {ep.method} `{ep.path}`\n\n{ep.purpose}\n\n**Request:** {ep.request}\n\n"
        f"**Response:** {ep.response}\n\n**Authorization:** {ep.authorization}\n\n**Errors**\n\n{bullets(ep.errors)}\n"
        for ep in spec.endpoints
    )
    tasks = "\n".join(
        f"### {t.id}: {t.title}\n\n- Owner: {t.owner}\n- Effort: {t.hours} person-hours\n"
        f"- Dependencies: {', '.join(t.depends_on) or 'None'}\n- Deliverable: {t.deliverable}\n"
        for t in spec.tasks
    )
    components = "\n".join(
        f"### {c.name}\n\n{c.responsibility}\n\n- Technology: {c.technology}\n"
        f"- Depends on: {', '.join(c.depends_on) or 'None'}\n"
        for c in stack.components
    )
    risks = "\n".join(
        f"- **{r['severity'].upper()}: {r['risk']}** — {r['mitigation']}"
        for r in idea["risks"]
    )
    sources = "\n".join(
        f"- [{s['id']}] [{s['title']}]({s['url']}) — retrieved {s['retrieved_at']}\n  {s['snippet']}"
        for s in research.get("sources", [])
    )
    sources = (
        sources
        or "No live evidence is available. Treat novelty and market claims as unverified."
    )
    prd = f"# {title} — Product Requirements Document\n\n{header}"
    for heading, text in [
        ("1. Executive summary", spec.executive_summary),
        (
            "2. Problem, audience, and intended outcome",
            f"{idea['problem']}\n\n**Audience:** {idea['target_users']}\n\n{idea['solution']}",
        ),
        ("3. Hackathon constraints and team", constraints + "\n\n" + team_text(intake)),
        ("4. Differentiation and evidence", idea["differentiation"] + "\n\n" + sources),
        ("5. MVP scope", bullets(idea["core_features"])),
        (
            "6. Stretch scope and explicit non-goals",
            "### Stretch\n\n"
            + bullets(idea["stretch_features"])
            + "\n\n### Non-goals\n\n"
            + bullets(idea["non_goals"]),
        ),
        ("7. End-to-end user journeys", bullets(spec.user_journeys)),
        ("8. Functional requirements", requirements),
        ("9. Screens and interaction states", bullets(spec.pages)),
        ("10. Confirmed technical decisions", stack.summary + "\n\n" + stack_text),
        (
            "11. System architecture and data flow",
            components + "\n\n" + bullets(stack.data_flow),
        ),
        ("12. Data model and integrity", entities),
        ("13. API and integration contracts", endpoints),
        ("14. Security and privacy", bullets(spec.security)),
        ("15. Accessibility and usability", bullets(spec.accessibility)),
        ("16. Reliability, errors, and recovery", bullets(spec.reliability)),
        ("17. Implementation plan and dependencies", tasks),
        (
            "18. Verification and definition of done",
            bullets(spec.test_plan)
            + "\n\nEvery must-have requirement must pass its acceptance criteria before the demo.",
        ),
        ("19. Success metrics", bullets(spec.success_metrics)),
        (
            "20. Risks, assumptions, and unresolved questions",
            risks
            + "\n\n### Assumptions\n\n"
            + bullets(idea["assumptions"])
            + "\n\n### Open questions\n\n"
            + bullets(spec.open_questions),
        ),
        ("21. Demo journey", idea["demo_scenario"]),
    ]:
        prd += section(heading, text)

    agents = (
        f"# Agent instructions — {title}\n\n{header}"
        + section(
            "Read first",
            (
                "Read PRD.md, ARCHITECTURE.md, and IMPLEMENTATION_PLAN.md before editing. "
                "PRD.md defines the approved product; TECH_STACK.md records confirmed technologies. "
                "These files describe a planned project, not proof that code or infrastructure already exists."
            ),
        )
        + section(
            "Product boundaries",
            bullets(idea["core_features"])
            + "\n\n**Do not expand into:**\n\n"
            + bullets(idea["non_goals"]),
        )
    )
    agents += section("Confirmed technologies", stack_text)
    agents += section(
        "Team and delivery constraints", constraints + "\n\n" + team_text(intake)
    )
    agents += section(
        "Project-specific implementation instructions", bullets(spec.agent_instructions)
    )
    agents += section(
        "Working rules",
        bullets(
            [
                "Trace implementation to requirement IDs and satisfy their acceptance criteria.",
                "Respect task dependencies. Ask before replacing a confirmed technology or expanding scope.",
                "Inspect the actual repository before assuming filenames, commands, or existing infrastructure.",
                "Keep credentials on the server and out of committed files, browser bundles, logs, and exports.",
                "Validate input, enforce authorization at resource boundaries, and preserve data on failed operations.",
                "Use honest loading, empty, error, and retry states. Never pass off sample data as successful functionality.",
                "Write and run meaningful tests for critical user journeys, integrations, and failure cases.",
                "Verify current provider documentation and pricing; research snippets are evidence leads, not guarantees.",
                "Record unresolved assumptions. Report exactly what was tested and what remains unverified.",
            ]
        ),
    )
    agents += section("Definition of done", bullets(spec.test_plan))

    docs = {
        "PRD.md": prd,
        "AGENTS.md": agents,
        "README.md": f"# {title}\n\n{header}\n{idea['hook']}\n\n{spec.executive_summary}"
        + section(
            "Start here",
            "1. Read PRD.md for the approved scope.\n2. Read TECH_STACK.md and SETUP.md.\n3. Follow IMPLEMENTATION_PLAN.md.\n4. Run the acceptance checks in PRD.md.\n\nThis is a planning handoff. Setup steps must be verified against the repository you build.",
        )
        + section("Core features", bullets(idea["core_features"])),
        "TECH_STACK.md": f"# Confirmed technology stack\n\n{header}\n{stack.summary}\n\n{stack_text}"
        + section("Compatibility review", bullets(stack.compatibility_notes)),
        "ARCHITECTURE.md": f"# Architecture — {title}\n\n{header}\n{stack.summary}\n\n{components}"
        + section("Data flow", bullets(stack.data_flow))
        + section(
            "Compatibility and risks",
            bullets(stack.compatibility_notes)
            + "\n\n"
            + bullets([f"{r.risk}: {r.mitigation}" for r in stack.risks]),
        ),
        "DATABASE.md": f"# Data model\n\n{header}\n{entities}",
        "API.md": f"# API contracts\n\n{header}\n{endpoints}",
        "SETUP.md": f"# Setup plan\n\n{header}\nThese are proposed setup steps for the confirmed stack. Verify commands and service requirements against official documentation.\n"
        + section("Environment and services", stack_text)
        + section("Steps", bullets(stack.setup_steps))
        + section(
            "Configuration safety",
            "Create a .env.example with names and descriptions only. Keep actual secrets outside version control. Verify permissions, quotas, cost, and local service availability before integration.",
        ),
        "IMPLEMENTATION_PLAN.md": f"# Implementation plan\n\n{header}\nTime limit: {intake['available_hours']}h. Total planned effort: {sum(t.hours for t in spec.tasks):g} person-hours.\n\n{team_text(intake)}\n\n{tasks}"
        + section("Acceptance and testing", bullets(spec.test_plan)),
        "RESEARCH.md": f"# Research and decision evidence\n\n{header}\n{sources}"
        + section(
            "Research limitations",
            bullets(research.get("warnings", []))
            + "\n\nSearch coverage is incomplete; finding no exact competitor does not establish originality. Scores are advisory estimates, not predictions of winning.",
        )
        + section("Idea critique", bullets(idea["critique"]))
        + section("Revisions made", bullets(idea["changes_made"])),
    }
    return {
        "revision": revision,
        "generated_at": generated_at,
        "files": [
            {
                "filename": filename,
                "content": content.rstrip() + "\n",
                "sha256": hashlib.sha256(
                    (content.rstrip() + "\n").encode()
                ).hexdigest(),
            }
            for filename, content in docs.items()
        ],
        "specification": spec.model_dump(),
        "input_digest": hashlib.sha256(
            json.dumps(
                {"intake": intake, "idea": idea, "stack": stack.model_dump()},
                sort_keys=True,
            ).encode()
        ).hexdigest(),
    }
