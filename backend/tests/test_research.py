import pytest
from typing import Dict, Any

from app.services.research.search import search_client
from app.services.research.service import research_service
from app.agents.idea_validation import idea_validation_agent


@pytest.fixture
def base_state_for_validation() -> Dict[str, Any]:
    """Base workflow state with generated ideas ready for validation."""
    return {
        "metadata": {
            "workflow_id": "test-research-001",
            "project_id": "test-project-001",
            "status": "running",
            "current_stage": "idea_validation",
            "created_at": "2026-06-12T00:00:00Z",
            "updated_at": "2026-06-12T00:00:00Z",
        },
        "project": {
            "id": "test-project-001",
            "name": "Integration Test Project",
            "challenge_statements": ["Build an AI assistant that can generate slide presentations"],
            "duration_hours": 48,
            "resources": [],
        },
        "team_profile": {
            "team_size": 2,
            "experience_level": "advanced",
            "known_technologies": ["Python", "React"],
            "preferred_technologies": ["Next.js"],
        },
        "challenge_intelligence": {
            "themes": ["AI Automation", "Presentations"],
            "constraints": ["48h limit"],
            "opportunities": ["LLM API"],
            "evaluation_factors": ["Originality"],
            "technical_opportunities": ["FastAPI"],
        },
        "problem_analysis": {
            "stakeholders": ["Developers"],
            "pain_points": ["Wasted time"],
            "assumptions": ["API keys are valid"],
            "success_metrics": ["Completes fast"],
            "refined_problem_statement": "Fast mock presentation creator.",
        },
        "opportunity_analysis": {
            "market_gaps": ["No slide generator"],
            "innovation_opportunities": ["Fast multi-stage agent design"],
            "technical_opportunities": ["LangGraph"],
            "impact_opportunities": ["Speed"],
        },
        "generated_ideas": [
            {
                "id": "idea-abc-123",
                "title": "SlideCoach AI",
                "description": "Generates complete visual slides from markdown pitches in real-time.",
                "target_users": ["Hackathon developers", "Indie hackers"],
                "key_features": ["Markdown slides", "Real-time editor", "Groq-speed rendering"],
                "innovation_score": 8.5,
            }
        ],
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


@pytest.mark.asyncio
async def test_search_client_mock():
    """Verify that search client returns mock results."""
    results = await search_client.search("competitors for AI slides generator", max_results=2)
    assert len(results) > 0
    for res in results:
        assert "title" in res
        assert "url" in res
        assert "content" in res
        assert res["url"].startswith("http")


@pytest.mark.asyncio
async def test_research_service_run_mock():
    """Verify that research coordinator runs and generates reports for a list of ideas."""
    ideas = [
        {
            "id": "idea-abc-123",
            "title": "SlideCoach AI",
            "description": "Generates complete visual slides from markdown pitches in real-time.",
            "key_features": ["Markdown slides", "Real-time editor"],
        }
    ]
    report_map = await research_service.run(ideas)
    assert "idea-abc-123" in report_map
    report = report_map["idea-abc-123"]
    assert report.idea_id == "idea-abc-123"
    assert len(report.competitors) >= 2
    assert len(report.open_source_projects) >= 2
    assert len(report.apis) >= 2
    assert report.novelty_score > 0
    assert report.feasibility_score > 0
    assert report.final_score > 0
    assert len(report.recommendations) >= 2


@pytest.mark.asyncio
async def test_idea_validation_agent_with_research(base_state_for_validation):
    """Verify that the validation agent runs the research pipeline and updates state correctly."""
    result_state = await idea_validation_agent.execute(base_state_for_validation)
    
    # Validation reports should be populated
    assert result_state["validation_reports"] is not None
    reports = result_state["validation_reports"]
    assert len(reports) == 1
    
    # Reports should contain competitors and APIs mapped from the search findings
    first_report = reports[0]
    assert first_report["idea_id"] == "idea-abc-123"
    assert len(first_report["competitors"]) >= 2
    assert len(first_report["apis"]) >= 2
    assert first_report["final_score"] > 0
    
    # The temporary _research_reports dict should have been cleaned up
    assert "_research_reports" not in result_state
