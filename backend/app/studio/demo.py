"""Explicit offline fixtures, never a fallback for live-provider failures."""

from app.studio.schemas import Idea, Scores, Specification, Stack


def ideas(intake, prompt=""):
    topic = " ".join(intake["idea"].split()[:6])
    capacity = sum(
        m.get("hours_available") or intake["available_hours"]
        for m in intake["teammates"]
    )
    result = []
    for i, (angle, feature) in enumerate(
        [
            ("Offline-first", "Capture inputs locally and synchronize when connected"),
            ("Explainable", "Show evidence and reasoning beside each recommendation"),
            ("Collaborative", "Share progress with a small accountability group"),
            (
                "Accessible",
                "Provide a guided low-bandwidth interface with keyboard support",
            ),
            (
                "Decision support",
                "Compare alternatives against explicit user constraints",
            ),
        ]
    ):
        result.append(
            Idea(
                title=f"{angle}: {topic}"[:160],
                hook=f"A focused {angle.lower()} approach to the challenge.",
                problem=f"The team wants to address: {intake['idea']}",
                solution=f"Build a focused workflow for {intake['idea']}. {feature}. "
                + (
                    f"Requested refinement: {prompt}"
                    if prompt
                    else "Keep the demonstration centered on one complete journey."
                ),
                target_users="People directly affected by the stated challenge; validate with interviews.",
                differentiation=f"Explore a {angle.lower()} interaction model. Originality is unverified because this is an offline demonstration.",
                core_features=[
                    feature,
                    "Guide the user through one complete workflow",
                    "Persist results and provide a clear recovery path",
                ],
                stretch_features=[
                    "Additional personalization after the core journey works"
                ],
                non_goals=["Large-scale integrations before the MVP is validated"],
                demo_scenario=f"Start with a realistic input for {topic}, complete the core workflow, show its saved outcome, and demonstrate recovery from an invalid input.",
                effort_hours=max(0.25, round(capacity * (0.4 + i * 0.03), 1)),
                risks=[
                    {
                        "risk": "The target problem has not been validated",
                        "severity": "high",
                        "mitigation": "Interview target users and run live competitor research before committing.",
                    }
                ],
                assumptions=[
                    "This is demonstration data; all market and feasibility judgments need validation."
                ],
                scores=Scores(
                    **{
                        key: {
                            "value": 35 if key == "originality" else 60 + i,
                            "rationale": "Illustrative demonstration score; not based on research or model evaluation.",
                        }
                        for key in Scores.model_fields
                    }
                ),
                evidence_ids=[],
                critique=[
                    "This offline concept has not been compared with live competitors."
                ],
                changes_made=[
                    "Kept scope to one journey and reserved integration time."
                ],
            )
        )
    return result


def stack(intake):
    choices = [
        (
            "Frontend",
            "Next.js + TypeScript",
            "Accessible web interface and route-based user journeys",
        ),
        (
            "Backend",
            "FastAPI + Python",
            "Validate requests and implement the domain workflow",
        ),
        ("Database", "PostgreSQL", "Store domain records with transactional integrity"),
        (
            "Testing",
            "pytest + Playwright",
            "Verify backend behavior and the primary browser journey",
        ),
    ]
    return Stack(
        summary="Demonstration architecture for a small, maintainable application. Edit these choices to match your actual team's capabilities before confirmation.",
        choices=[
            {
                "category": c,
                "technology": t,
                "purpose": p,
                "rationale": "Illustrative baseline; verify against the team's skills and constraints.",
                "alternatives": ["Use the team's strongest familiar alternative"],
                "tradeoffs": ["Introducing a new technology consumes hackathon time."],
            }
            for c, t, p in choices
        ],
        components=[
            {
                "name": "Web interface",
                "responsibility": "Present the core workflow with validation, loading, and error states.",
                "technology": choices[0][1],
                "depends_on": ["Domain service"],
            },
            {
                "name": "Domain service",
                "responsibility": "Enforce business rules and persist authorized project data.",
                "technology": choices[1][1],
                "depends_on": [],
            },
        ],
        data_flow=[
            "User submits a validated input to the domain service.",
            "The service authorizes, persists, and returns the result to the interface.",
        ],
        compatibility_notes=[
            "This offline stack has not been checked against live provider documentation."
        ],
        risks=[
            {
                "risk": "The team may be unfamiliar with this stack",
                "severity": "medium",
                "mitigation": "Replace choices with technologies the team knows before confirming.",
            }
        ],
        setup_steps=[
            "Create the frontend and domain service using the confirmed frameworks.",
            "Configure a development database and server-side environment variables.",
            "Implement and test one vertical slice before expanding scope.",
        ],
    )


def specification(intake, idea):
    members = intake["teammates"]
    tasks = []
    for i in range(3):
        member = members[i % len(members)]
        tasks.append(
            {
                "id": f"T-{i + 1:02}",
                "title": [
                    "Prepare the development environment",
                    "Implement the core vertical slice",
                    "Verify integration and rehearse the demo",
                ][i],
                "owner": member["name"],
                "hours": round(
                    min(
                        intake["available_hours"],
                        member.get("hours_available") or intake["available_hours"],
                    )
                    * 0.15,
                    3,
                ),
                "depends_on": [f"T-{i:02}"] if i else [],
                "deliverable": "A verified, reproducible increment with documented checks and known limitations.",
            }
        )
    return Specification(
        executive_summary=f"{idea['solution']} The team will validate this concept through one complete user journey, persistent results, and recoverable errors. This document is an offline demonstration template; its product details require review before implementation.",
        user_journeys=[
            "A new user enters a realistic challenge input, resolves validation errors, and receives a meaningful result.",
            "A returning user retrieves a previously saved result and safely retries an interrupted action.",
        ],
        requirements=[
            {
                "id": f"FR-{i + 1:02}",
                "title": feature[:200],
                "user_story": f"As a target user, I want to {feature.lower()} so I can complete the core workflow.",
                "behavior": f"The application must support: {feature}. Validate inputs, authorize access, persist successful changes, and preserve previous data on failure.",
                "acceptance_criteria": [
                    "A valid input produces a persisted outcome visible after a page reload.",
                    "An invalid input shows a specific error without creating or overwriting data.",
                ],
                "edge_cases": [
                    "An interrupted request can be retried without duplicating the operation."
                ],
                "priority": "must",
            }
            for i, feature in enumerate(idea["core_features"][:3])
        ],
        pages=[
            "Entry screen: empty, editing, invalid, submitting, success, and retry states.",
            "Result screen: saved data, not found, unauthorized, loading, and recovery states.",
        ],
        entities=[
            {
                "name": "Record",
                "fields": [
                    "id: unique identifier",
                    "owner_id: authenticated owner",
                    "content: validated domain payload",
                    "created_at: server timestamp",
                ],
                "relationships": ["Each record belongs to one owner."],
                "validation": [
                    "Validate the domain payload and enforce ownership on every access."
                ],
            }
        ],
        endpoints=[
            {
                "method": "POST",
                "path": "/records",
                "purpose": "Create an authorized domain record",
                "request": "Validated domain payload",
                "response": "Saved record with identifier",
                "authorization": "Require the current user's authenticated identity",
                "errors": [
                    "422 invalid input",
                    "401 unauthenticated",
                    "409 duplicate operation",
                ],
            }
        ],
        tasks=tasks,
        security=[
            "Enforce record ownership on the server.",
            "Store secrets outside committed files and browser bundles.",
            "Validate input sizes and types before processing.",
        ],
        accessibility=[
            "Support keyboard navigation with visible focus states.",
            "Associate labels and errors with form controls.",
        ],
        reliability=[
            "Preserve saved data when an operation fails.",
            "Make retries idempotent.",
            "Expose actionable errors and operational health checks.",
        ],
        test_plan=[
            "Complete the main user journey and verify persistence after reload.",
            "Verify unauthorized users cannot retrieve another user's data.",
            "Simulate provider failures and ensure existing data remains intact.",
        ],
        success_metrics=[
            "The primary journey completes within the demo time window.",
            "Every must-have acceptance criterion passes before the presentation.",
        ],
        open_questions=[
            "Run live competitor research and validate assumptions with target users."
        ],
        agent_instructions=[
            "Use the confirmed technology stack and inspect the repository before editing.",
            "Implement the core journey before stretch features.",
            "Keep demonstration data visibly labeled and outside production paths.",
        ],
    )
