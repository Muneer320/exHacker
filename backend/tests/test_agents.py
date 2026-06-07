from unittest.mock import AsyncMock

import pytest

from app.agents.challenge_intelligence import ChallengeIntelligenceAgent
from app.agents.opportunity_planner import OpportunityPlannerAgent
from app.agents.problem_analyst import ProblemAnalystAgent
from app.agents.registry import AgentRegistry
from app.agents.user_profiler import UserProfilerAgent


@pytest.fixture
def mock_llm():
    mock = AsyncMock()
    mock.generate.return_value = '{"complexity_budget": "medium", "recommended_scope": "mvp", "risk_tolerance": "medium", "execution_capacity_score": 75.0}'
    return mock


@pytest.fixture
def mock_challenge_llm():
    mock = AsyncMock()
    mock.generate.return_value = '{"themes": ["AI Healthcare"], "opportunities": ["Health monitoring"], "constraints": ["Data privacy"], "resource_opportunities": ["Use health dataset"], "evaluation_focus": ["innovation"]}'
    return mock


@pytest.fixture
def mock_problem_llm():
    mock = AsyncMock()
    mock.generate.return_value = '{"stakeholders": ["Patients", "Doctors"], "pain_points": ["Manual tracking"], "assumptions": ["Data available"], "success_metrics": ["Accuracy > 90%"], "problem_definition": "Improve health monitoring"}'
    return mock


@pytest.fixture
def mock_opportunity_llm():
    mock = AsyncMock()
    mock.generate.return_value = '{"market_gaps": ["No AI solution for X"], "innovation_opportunities": ["Use LLM for Y"], "high_impact_areas": ["Patient outcomes"], "technical_opportunities": ["Real-time processing"]}'
    return mock


@pytest.mark.asyncio
async def test_user_profiler_valid_input(mock_llm) -> None:
    agent = UserProfilerAgent()
    agent._llm = mock_llm
    state = {
        "project": {
            "team_data": {
                "team_size": 4,
                "duration_hours": 24,
                "skills": ["frontend", "backend", "ai"],
                "experience_level": "intermediate",
            }
        }
    }
    result = await agent.run(state)
    assert result.success
    assert result.output is not None
    assert result.output["complexity_budget"] == "medium"
    assert result.output["execution_capacity_score"] == 75.0


@pytest.mark.asyncio
async def test_user_profiler_empty_skills() -> None:
    agent = UserProfilerAgent()
    state = {
        "project": {
            "team_data": {
                "team_size": 1,
                "duration_hours": 12,
                "skills": [],
                "experience_level": "beginner",
            }
        }
    }
    result = await agent.run(state)
    assert not result.success


@pytest.mark.asyncio
async def test_challenge_intelligence_agent(mock_challenge_llm) -> None:
    agent = ChallengeIntelligenceAgent()
    agent._llm = mock_challenge_llm
    state = {
        "project": {
            "challenge_data": {
                "challenge_statements": ["Build AI for healthcare"],
                "evaluation_criteria": ["innovation", "impact"],
            },
            "resource_data": {
                "tracks": ["AI", "Health"],
                "datasets": ["health_data.csv"],
                "apis": ["openai"],
            },
        }
    }
    result = await agent.run(state)
    assert result.success
    assert result.output is not None
    assert "AI Healthcare" in result.output["themes"]


@pytest.mark.asyncio
async def test_problem_analyst_agent(mock_problem_llm) -> None:
    agent = ProblemAnalystAgent()
    agent._llm = mock_problem_llm
    state = {
        "project": {
            "challenge_data": {
                "challenge_statements": ["Build AI for healthcare"],
            }
        },
        "challenge_intelligence": {
            "challenge_statements": ["Build AI for healthcare"],
            "themes": ["AI Healthcare"],
            "opportunities": ["Health monitoring"],
            "evaluation_focus": ["innovation"],
        },
    }
    result = await agent.run(state)
    assert result.success
    assert result.output is not None
    assert "Patients" in result.output["stakeholders"]
    assert result.output["problem_definition"] == "Improve health monitoring"


@pytest.mark.asyncio
async def test_opportunity_planner_agent(mock_opportunity_llm) -> None:
    agent = OpportunityPlannerAgent()
    agent._llm = mock_opportunity_llm
    state = {
        "problem_analysis": {
            "problem_definition": "Improve health monitoring",
            "stakeholders": ["Patients"],
            "pain_points": ["Manual tracking"],
        },
        "challenge_intelligence": {
            "themes": ["AI Healthcare"],
            "opportunities": ["Health monitoring"],
            "constraints": ["Data privacy"],
        },
        "user_profiler": {
            "complexity_budget": "medium",
            "recommended_scope": "mvp",
            "skills": ["frontend", "backend"],
        },
    }
    result = await agent.run(state)
    assert result.success
    assert result.output is not None
    assert "market_gaps" in result.output
    assert "innovation_opportunities" in result.output


@pytest.mark.asyncio
async def test_agent_registry() -> None:
    AgentRegistry.clear()
    AgentRegistry.register(UserProfilerAgent())
    AgentRegistry.register(ChallengeIntelligenceAgent())
    AgentRegistry.register(ProblemAnalystAgent())
    AgentRegistry.register(OpportunityPlannerAgent())

    assert len(AgentRegistry.get_all()) == 4
    assert AgentRegistry.get("user_profiler") is not None
    assert AgentRegistry.get("challenge_intelligence") is not None
    assert AgentRegistry.get("nonexistent") is None

    critical = AgentRegistry.get_critical_agents()
    assert len(critical) == 2


@pytest.mark.asyncio
async def test_challenge_intelligence_no_statements() -> None:
    agent = ChallengeIntelligenceAgent()
    state = {"project": {"challenge_data": {}, "resource_data": {}}}
    result = await agent.run(state)
    assert not result.success
