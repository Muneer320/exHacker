import pytest

from app.agents.challenge_intelligence import ChallengeIntelligenceAgent
from app.agents.problem_analyst import ProblemAnalystAgent
from app.agents.registry import AgentRegistry
from app.agents.user_profiler import UserProfilerAgent


@pytest.mark.asyncio
async def test_user_profiler_valid_input() -> None:
    agent = UserProfilerAgent()
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
    assert "complexity_budget" in result.output
    assert "execution_capacity_score" in result.output


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
async def test_challenge_intelligence_agent() -> None:
    agent = ChallengeIntelligenceAgent()
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
    assert "themes" in result.output
    assert "evaluation_focus" in result.output


@pytest.mark.asyncio
async def test_agent_registry() -> None:
    AgentRegistry.clear()
    AgentRegistry.register(UserProfilerAgent())
    AgentRegistry.register(ChallengeIntelligenceAgent())
    AgentRegistry.register(ProblemAnalystAgent())

    assert len(AgentRegistry.get_all()) == 3
    assert AgentRegistry.get("user_profiler") is not None
    assert AgentRegistry.get("challenge_intelligence") is not None
    assert AgentRegistry.get("nonexistent") is None

    critical = AgentRegistry.get_critical_agents()
    assert len(critical) == 2
