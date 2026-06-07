from unittest.mock import AsyncMock

import pytest

from app.agents.challenge_intelligence import ChallengeIntelligenceAgent
from app.agents.idea_generator import IdeaGeneratorAgent
from app.agents.idea_validator import IdeaValidatorAgent
from app.agents.opportunity_planner import OpportunityPlannerAgent
from app.agents.problem_analyst import ProblemAnalystAgent
from app.agents.registry import AgentRegistry
from app.agents.solution_architect import SolutionArchitectAgent
from app.agents.tech_stack_advisor import TechStackAdvisorAgent
from app.agents.user_profiler import UserProfilerAgent


@pytest.fixture
def mock_llm():
    mock = AsyncMock()
    mock.generate.return_value = (
        '{"complexity_budget": "medium", "recommended_scope": "mvp", '
        '"risk_tolerance": "medium", "execution_capacity_score": 75.0}'
    )
    return mock


@pytest.fixture
def mock_challenge_llm():
    mock = AsyncMock()
    mock.generate.return_value = (
        '{"themes": ["AI Healthcare"], "opportunities": ["Health monitoring"], '
        '"constraints": ["Data privacy"], "resource_opportunities": ["Use health dataset"], '
        '"evaluation_focus": ["innovation"]}'
    )
    return mock


@pytest.fixture
def mock_problem_llm():
    mock = AsyncMock()
    mock.generate.return_value = (
        '{"stakeholders": ["Patients", "Doctors"], "pain_points": ["Manual tracking"], '
        '"assumptions": ["Data available"], "success_metrics": ["Accuracy > 90%"], '
        '"problem_definition": "Improve health monitoring"}'
    )
    return mock


@pytest.fixture
def mock_opportunity_llm():
    mock = AsyncMock()
    mock.generate.return_value = (
        '{"market_gaps": ["No AI solution for X"], '
        '"innovation_opportunities": ["Use LLM for Y"], '
        '"high_impact_areas": ["Patient outcomes"], '
        '"technical_opportunities": ["Real-time processing"]}'
    )
    return mock


@pytest.fixture
def mock_idea_llm():
    mock = AsyncMock()
    mock.generate.return_value = (
        '{"ideas": [{"title": "AI Health Monitor", '
        '"description": "Monitor patient health with AI", '
        '"target_users": ["Patients", "Doctors"], '
        '"key_features": ["Real-time monitoring", "Alerts", "Dashboard"], '
        '"innovation_score": 85}]}'
    )
    return mock


@pytest.fixture
def mock_validator_llm():
    mock = AsyncMock()
    mock.generate.return_value = (
        '{"innovation": 80, "feasibility": 70, "hackathon_fit": 90, '
        '"technical_wow": 85, "competitors": [], '
        '"open_source_projects": [], "available_apis": [], '
        '"strengths": ["Strong impact"], "weaknesses": ["Complex"], '
        '"risks": ["Data privacy"]}'
    )
    return mock


@pytest.mark.asyncio
async def test_user_profiler_valid_input(mock_llm) -> None:
    agent = UserProfilerAgent(llm=mock_llm)
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
    agent = ChallengeIntelligenceAgent(llm=mock_challenge_llm)
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
    agent = ProblemAnalystAgent(llm=mock_problem_llm)
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


@pytest.mark.asyncio
async def test_opportunity_planner_agent(mock_opportunity_llm) -> None:
    agent = OpportunityPlannerAgent(llm=mock_opportunity_llm)
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


@pytest.mark.asyncio
async def test_idea_generator_agent(mock_idea_llm) -> None:
    agent = IdeaGeneratorAgent(llm=mock_idea_llm)
    state = {
        "challenge_intelligence": {
            "themes": ["AI Healthcare"],
            "constraints": ["Privacy"],
            "evaluation_focus": ["Innovation"],
        },
        "problem_analysis": {
            "problem_definition": "Improve health",
            "pain_points": ["Manual"],
            "stakeholders": ["Patients"],
        },
        "opportunity_analysis": {
            "market_gaps": ["No AI"],
            "innovation_opportunities": ["LLM"],
            "high_impact_areas": ["Health"],
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
    assert len(result.output["ideas"]) > 0
    assert result.output["ideas"][0]["title"] == "AI Health Monitor"


@pytest.mark.asyncio
async def test_idea_validator_agent(mock_validator_llm, mock_idea_llm) -> None:
    gen_agent = IdeaGeneratorAgent(llm=mock_idea_llm)
    gen_state = {
        "challenge_intelligence": {"themes": ["AI"], "constraints": [], "evaluation_focus": []},
        "problem_analysis": {"problem_definition": "", "pain_points": [], "stakeholders": []},
        "opportunity_analysis": {
            "market_gaps": [], "innovation_opportunities": [], "high_impact_areas": []
        },
        "user_profiler": {"complexity_budget": "medium", "recommended_scope": "mvp", "skills": []},
    }
    gen_result = await gen_agent.run(gen_state)

    agent = IdeaValidatorAgent(llm=mock_validator_llm)
    state = {
        "idea_generator": gen_result.output,
        "challenge_intelligence": {
            "themes": ["AI Healthcare"],
            "evaluation_focus": ["Innovation"],
        },
    }
    result = await agent.run(state)
    assert result.success
    assert result.output is not None
    assert "validation_reports" in result.output
    assert len(result.output["validation_reports"]) > 0
    assert result.output["validation_reports"][0]["innovation"] == 80.0


@pytest.mark.asyncio
async def test_agent_registry() -> None:
    AgentRegistry.clear()
    AgentRegistry.register(UserProfilerAgent())
    AgentRegistry.register(ChallengeIntelligenceAgent())
    AgentRegistry.register(ProblemAnalystAgent())
    AgentRegistry.register(OpportunityPlannerAgent())
    AgentRegistry.register(IdeaGeneratorAgent())
    AgentRegistry.register(IdeaValidatorAgent())

    assert len(AgentRegistry.get_all()) == 6
    assert AgentRegistry.get("idea_generator") is not None
    assert AgentRegistry.get("nonexistent") is None

    critical = AgentRegistry.get_critical_agents()
    assert len(critical) == 2


@pytest.mark.asyncio
async def test_challenge_intelligence_no_statements() -> None:
    agent = ChallengeIntelligenceAgent()
    state = {"project": {"challenge_data": {}, "resource_data": {}}}
    result = await agent.run(state)
    assert not result.success


@pytest.fixture
def mock_architect_llm():
    mock = AsyncMock()
    mock.generate.return_value = (
        '{"vision": "AI health platform", "product_scope": "MVP", '
        '"features": [{"title": "Dashboard", "description": "Health dashboard", '
        '"priority": "critical"}], '
        '"user_stories": [{"actor": "Doctor", "goal": "view patient data", '
        '"benefit": "better care"}], '
        '"architecture": {"description": "Web app with API", '
        '"components": [], "connections": []}, '
        '"api_design": [{"path": "/api/health", "method": "GET", '
        '"description": "Get health data"}], '
        '"database_schema": {"tables": [], "relationships": []}, '
        '"integrations": [{"name": "OpenAI", '
        '"description": "AI analysis", "type": "api"}]}'
    )
    return mock


@pytest.fixture
def mock_tech_stack_llm():
    mock = AsyncMock()
    mock.generate.return_value = (
        '{"frontend": "Next.js", "backend": "FastAPI", "database": "PostgreSQL", '
        '"hosting": "Vercel", "ai_models": ["GPT-4"], '
        '"vector_db": "Pinecone", "auth_provider": "Clerk"}'
    )
    return mock


@pytest.mark.asyncio
async def test_solution_architect_agent(mock_architect_llm) -> None:
    agent = SolutionArchitectAgent(llm=mock_architect_llm)
    state = {
        "selected_idea": {
            "id": "test-1",
            "title": "AI Health Monitor",
            "description": "Monitor health with AI",
            "target_users": ["Patients", "Doctors"],
            "key_features": ["Monitoring", "Alerts"],
            "innovation_score": 85,
            "feasibility_score": 70,
        },
        "user_profiler": {
            "complexity_budget": "medium",
            "recommended_scope": "mvp",
            "skills": ["frontend", "backend"],
        },
        "project": {
            "team_data": {
                "team_size": 4,
                "duration_hours": 24,
                "skills": ["frontend", "backend"],
            }
        },
    }
    result = await agent.run(state)
    assert result.success
    assert result.output is not None
    assert "vision" in result.output
    assert len(result.output["features"]) > 0


@pytest.mark.asyncio
async def test_tech_stack_advisor_agent(mock_tech_stack_llm) -> None:
    agent = TechStackAdvisorAgent(llm=mock_tech_stack_llm)
    state = {
        "solution_architect": {
            "features": [{"title": "Dashboard", "priority": "critical"}],
            "api_design": [{"path": "/api/health", "method": "GET"}],
            "integrations": [{"name": "OpenAI", "type": "api"}],
        },
        "user_profiler": {
            "complexity_budget": "medium",
            "skills": ["frontend", "backend"],
        },
        "challenge_intelligence": {
            "themes": ["AI Healthcare"],
            "evaluation_focus": ["Innovation"],
        },
        "project": {
            "team_data": {
                "team_size": 4,
                "duration_hours": 24,
                "skills": ["frontend", "backend"],
                "experience_level": "intermediate",
            }
        },
    }
    result = await agent.run(state)
    assert result.success
    assert result.output is not None
    assert result.output["frontend"] == "Next.js"
    assert result.output["backend"] == "FastAPI"


@pytest.mark.asyncio
async def test_solution_architect_no_idea() -> None:
    agent = SolutionArchitectAgent()
    state = {
        "selected_idea": {},
        "idea_generator": {"ideas": []},
        "project": {"team_data": {}},
    }
    result = await agent.run(state)
    assert not result.success


@pytest.mark.asyncio
async def test_agent_registry_full() -> None:
    AgentRegistry.clear()
    AgentRegistry.register(UserProfilerAgent())
    AgentRegistry.register(ChallengeIntelligenceAgent())
    AgentRegistry.register(ProblemAnalystAgent())
    AgentRegistry.register(OpportunityPlannerAgent())
    AgentRegistry.register(IdeaGeneratorAgent())
    AgentRegistry.register(IdeaValidatorAgent())
    AgentRegistry.register(SolutionArchitectAgent())
    AgentRegistry.register(TechStackAdvisorAgent())

    assert len(AgentRegistry.get_all()) == 8
    assert AgentRegistry.get("solution_architect") is not None
    assert AgentRegistry.get("tech_stack_advisor") is not None

    critical = AgentRegistry.get_critical_agents()
    assert len(critical) == 3
