"""
Agent Tests — Milestone 3

Tests all 10 agent mock_result() and execute() methods in isolation.
Uses mock fallback execution (no real LLM calls needed).
"""

import pytest
import asyncio
from typing import Dict, Any

# Agents
from app.agents.challenge_intelligence import challenge_intelligence_agent
from app.agents.problem_analysis import problem_analysis_agent
from app.agents.opportunity_discovery import opportunity_discovery_agent
from app.agents.idea_generation import idea_generation_agent
from app.agents.idea_validation import idea_validation_agent
from app.agents.tech_stack import tech_stack_advisor_agent
from app.agents.architecture import solution_architect_agent
from app.agents.build_accelerator import build_accelerator_agent
from app.agents.presentation import presentation_agent
from app.agents.pitch import pitch_coach_agent

# Schemas for type validation
from app.schemas.state import (
    ChallengeIntelligence,
    ProblemAnalysis,
    OpportunityAnalysis,
    TechStack,
    ArchitecturePackage,
    PresentationPackage,
    PitchPackage,
)


# ---------------------------------------------------------------------------
# Shared fixture: a minimal complete workflow state
# ---------------------------------------------------------------------------

@pytest.fixture
def base_state() -> Dict[str, Any]:
    """Minimal workflow state with enough context for all agents."""
    return {
        "metadata": {
            "workflow_id": "test-workflow-001",
            "project_id": "test-project-001",
            "status": "running",
            "current_stage": "challenge_intelligence",
            "created_at": "2026-06-12T00:00:00Z",
            "updated_at": "2026-06-12T00:00:00Z",
        },
        "project": {
            "id": "test-project-001",
            "name": "exHacker Test",
            "challenge_statements": [
                "Build an AI tool that helps hackathon teams go from challenge to MVP in under 5 minutes."
            ],
            "duration_hours": 48,
            "resources": [],
            "created_at": "2026-06-12T00:00:00Z",
        },
        "team_profile": {
            "team_size": 3,
            "experience_level": "Mid-level",
            "known_technologies": ["Python", "React", "FastAPI"],
            "preferred_technologies": ["Next.js", "Tailwind CSS"],
        },
        "challenge_intelligence": None,
        "problem_analysis": None,
        "opportunity_analysis": None,
        "generated_ideas": None,
        "validation_reports": None,
        "selected_idea": None,
        "tech_stack": None,
        "architecture": None,
        "build_package": None,
        "prompt_package": None,
        "presentation": None,
        "pitch": None,
        "exports": None,
        "execution": {
            "total_duration_seconds": 0.0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "provider_usage": [],
            "stage_metrics": [],
        },
        "errors": [],
    }


@pytest.fixture
def full_state(base_state) -> Dict[str, Any]:
    """State with all early-stage outputs filled in (for late-stage agent tests)."""
    import uuid

    idea_id = str(uuid.uuid4())

    base_state["challenge_intelligence"] = {
        "themes": ["AI Automation", "Human Collaboration"],
        "constraints": ["48-hour limit", "Must demo live"],
        "opportunities": ["LLM APIs", "Visual dashboards"],
        "evaluation_factors": ["Innovation", "Feasibility"],
        "technical_opportunities": ["LangGraph", "FastAPI"],
    }
    base_state["problem_analysis"] = {
        "stakeholders": ["Hackathon teams", "Judges"],
        "pain_points": ["Setup time", "Demo crashes"],
        "assumptions": ["API keys available"],
        "success_metrics": ["Under 5 minutes"],
        "refined_problem_statement": "Teams waste time on setup instead of building.",
    }
    base_state["opportunity_analysis"] = {
        "market_gaps": ["No integrated tool"],
        "innovation_opportunities": ["Multi-agent pipeline"],
        "technical_opportunities": ["LangGraph"],
        "impact_opportunities": ["10x faster delivery"],
    }
    base_state["generated_ideas"] = [
        {
            "id": idea_id,
            "title": "exHacker Sentinel",
            "description": "AI workflow engine for hackathons.",
            "target_users": ["Developers"],
            "key_features": ["LLM fallback", "State persistence", "Live dashboard"],
            "innovation_score": 9.0,
        }
    ]
    base_state["validation_reports"] = [
        {
            "idea_id": idea_id,
            "competitors": [{"name": "LangSmith", "description": "LLM monitoring", "url": ""}],
            "open_source_projects": [{"name": "langgraph", "description": "Orchestration", "url": "", "stars": 3400}],
            "apis": [{"name": "Groq API", "description": "Inference", "url": ""}],
            "strengths": ["Demo-friendly"],
            "weaknesses": ["Depends on LLMs"],
            "risks": ["Rate limits"],
            "feasibility_score": 9.0,
            "innovation_score": 9.0,
            "final_score": 9.0,
        }
    ]
    base_state["selected_idea"] = base_state["generated_ideas"][0]
    base_state["tech_stack"] = {
        "frontend": "Next.js 15",
        "backend": "FastAPI",
        "database": "SQLite",
        "ai_stack": ["Groq", "Gemini"],
        "deployment": ["Vercel", "Railway"],
        "reasoning": ["Fast", "Simple"],
    }
    base_state["architecture"] = {
        "system_design": "Clean separation of concerns.",
        "components": [{"name": "API", "description": "FastAPI", "responsibilities": ["Handle requests"]}],
        "modules": [],
        "api_design": [],
        "database_design": {"tables": [], "relationships": []},
        "integrations": [],
        "mvp_scope": ["Create project", "Run workflow", "Export artifacts"],
        "future_scope": ["WebSocket streaming"],
    }
    base_state["build_package"] = {
        "frontend_tasks": ["Build dashboard"],
        "backend_tasks": ["Build API"],
        "database_tasks": ["Create tables"],
        "testing_tasks": ["Write tests"],
        "deployment_tasks": ["Dockerize"],
    }
    base_state["presentation"] = {
        "slide_order": ["Slide 1: Problem"],
        "slide_content": [{"title": "The Problem", "content": ["Demo crashes"], "visual_notes": "Dark red"}],
        "demo_story": "We open the dashboard...",
        "business_story": "500K hackathon developers...",
    }

    return base_state


# ---------------------------------------------------------------------------
# Unit tests: mock_result() for each agent
# ---------------------------------------------------------------------------

def test_challenge_intelligence_mock(base_state):
    result = challenge_intelligence_agent.mock_result(base_state)
    assert isinstance(result, ChallengeIntelligence)
    assert len(result.themes) >= 3
    assert len(result.constraints) >= 3
    assert len(result.opportunities) >= 3
    assert len(result.evaluation_factors) >= 3
    assert len(result.technical_opportunities) >= 3


def test_problem_analysis_mock(base_state):
    result = problem_analysis_agent.mock_result(base_state)
    assert isinstance(result, ProblemAnalysis)
    assert len(result.stakeholders) >= 3
    assert len(result.pain_points) >= 3
    assert len(result.success_metrics) >= 3
    assert result.refined_problem_statement != ""


def test_opportunity_discovery_mock(base_state):
    result = opportunity_discovery_agent.mock_result(base_state)
    assert isinstance(result, OpportunityAnalysis)
    assert len(result.market_gaps) >= 3
    assert len(result.innovation_opportunities) >= 3
    assert len(result.technical_opportunities) >= 3


def test_idea_generation_mock(base_state):
    from app.agents.idea_generation import IdeaList
    result = idea_generation_agent.mock_result(base_state)
    assert isinstance(result, IdeaList)
    assert len(result.ideas) == 5
    for idea in result.ideas:
        assert idea.id != ""
        assert idea.title != ""
        assert idea.innovation_score >= 0.0


def test_idea_validation_mock(full_state):
    from app.agents.idea_validation import ValidationReportList
    result = idea_validation_agent.mock_result(full_state)
    assert isinstance(result, ValidationReportList)
    assert len(result.reports) == len(full_state["generated_ideas"])
    for report in result.reports:
        assert report.feasibility_score >= 0.0
        assert report.final_score >= 0.0
        assert len(report.strengths) >= 2


def test_tech_stack_mock(full_state):
    result = tech_stack_advisor_agent.mock_result(full_state)
    assert isinstance(result, TechStack)
    assert result.frontend != ""
    assert result.backend != ""
    assert result.database != ""
    assert len(result.ai_stack) >= 2
    assert len(result.reasoning) >= 3


def test_solution_architect_mock(full_state):
    result = solution_architect_agent.mock_result(full_state)
    assert isinstance(result, ArchitecturePackage)
    assert result.system_design != ""
    assert len(result.components) >= 2
    assert len(result.mvp_scope) >= 4
    assert len(result.api_design) >= 3


def test_build_accelerator_mock(full_state):
    from app.agents.build_accelerator import BuildAcceleratorOutput
    result = build_accelerator_agent.mock_result(full_state)
    assert isinstance(result, BuildAcceleratorOutput)
    assert len(result.build_package.frontend_tasks) >= 4
    assert len(result.build_package.backend_tasks) >= 4
    assert len(result.prompt_package.frontend_prompts) >= 1
    assert len(result.prompt_package.backend_prompts) >= 1


def test_presentation_mock(full_state):
    result = presentation_agent.mock_result(full_state)
    assert isinstance(result, PresentationPackage)
    assert len(result.slide_order) >= 5
    assert len(result.slide_content) == len(result.slide_order)
    assert result.demo_story != ""
    assert result.business_story != ""


def test_pitch_mock(full_state):
    result = pitch_coach_agent.mock_result(full_state)
    assert isinstance(result, PitchPackage)
    assert len(result.pitch_30s.split()) <= 80  # roughly 30 seconds
    assert len(result.judge_questions) >= 5
    assert result.demo_script != ""


# ---------------------------------------------------------------------------
# Integration tests: execute() with mock fallback (no real LLM)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_challenge_intelligence_execute_mock(base_state):
    """Agent execute() uses mock when no LLM is configured."""
    result_state = await challenge_intelligence_agent.execute(base_state)
    assert result_state["challenge_intelligence"] is not None
    ci = result_state["challenge_intelligence"]
    assert "themes" in ci
    assert len(ci["themes"]) >= 3
    # Metrics should be recorded
    assert result_state["execution"]["total_tokens"] > 0


@pytest.mark.asyncio
async def test_problem_analysis_execute_mock(base_state):
    result_state = await problem_analysis_agent.execute(base_state)
    assert result_state["problem_analysis"] is not None
    pa = result_state["problem_analysis"]
    assert "refined_problem_statement" in pa
    assert pa["refined_problem_statement"] != ""


@pytest.mark.asyncio
async def test_opportunity_discovery_execute_mock(base_state):
    result_state = await opportunity_discovery_agent.execute(base_state)
    assert result_state["opportunity_analysis"] is not None
    oa = result_state["opportunity_analysis"]
    assert "market_gaps" in oa


@pytest.mark.asyncio
async def test_idea_generation_execute_mock(full_state):
    full_state["generated_ideas"] = None  # Reset so agent runs
    result_state = await idea_generation_agent.execute(full_state)
    assert result_state["generated_ideas"] is not None
    assert len(result_state["generated_ideas"]) == 5


@pytest.mark.asyncio
async def test_idea_validation_execute_mock(full_state):
    full_state["validation_reports"] = None  # Reset so agent runs
    result_state = await idea_validation_agent.execute(full_state)
    assert result_state["validation_reports"] is not None
    assert len(result_state["validation_reports"]) > 0


@pytest.mark.asyncio
async def test_tech_stack_execute_mock(full_state):
    full_state["tech_stack"] = None  # Reset
    result_state = await tech_stack_advisor_agent.execute(full_state)
    assert result_state["tech_stack"] is not None
    ts = result_state["tech_stack"]
    assert "frontend" in ts
    assert "backend" in ts


@pytest.mark.asyncio
async def test_architecture_execute_mock(full_state):
    full_state["architecture"] = None  # Reset
    result_state = await solution_architect_agent.execute(full_state)
    assert result_state["architecture"] is not None
    arch = result_state["architecture"]
    assert "system_design" in arch
    assert "mvp_scope" in arch


@pytest.mark.asyncio
async def test_build_accelerator_execute_mock(full_state):
    full_state["build_package"] = None
    full_state["prompt_package"] = None
    result_state = await build_accelerator_agent.execute(full_state)
    assert result_state["build_package"] is not None
    assert result_state["prompt_package"] is not None


@pytest.mark.asyncio
async def test_presentation_execute_mock(full_state):
    full_state["presentation"] = None
    result_state = await presentation_agent.execute(full_state)
    assert result_state["presentation"] is not None
    p = result_state["presentation"]
    assert "slide_order" in p
    assert "demo_story" in p


@pytest.mark.asyncio
async def test_pitch_execute_mock(full_state):
    full_state["pitch"] = None
    result_state = await pitch_coach_agent.execute(full_state)
    assert result_state["pitch"] is not None
    pitch = result_state["pitch"]
    assert "pitch_30s" in pitch
    assert "judge_questions" in pitch
    assert len(pitch["judge_questions"]) >= 5
