from unittest.mock import AsyncMock

import pytest

from app.agents.build_accelerator import BuildAcceleratorAgent
from app.agents.challenge_intelligence import ChallengeIntelligenceAgent
from app.agents.idea_generator import IdeaGeneratorAgent
from app.agents.idea_validator import IdeaValidatorAgent
from app.agents.opportunity_planner import OpportunityPlannerAgent
from app.agents.pitch_coach import PitchCoachAgent
from app.agents.presentation_agent import PresentationAgent
from app.agents.problem_analyst import ProblemAnalystAgent
from app.agents.registry import AgentRegistry
from app.agents.solution_architect import SolutionArchitectAgent
from app.agents.tech_stack_advisor import TechStackAdvisorAgent
from app.agents.user_profiler import UserProfilerAgent


def _make_structured(parsed: dict) -> dict:
    return {"parsed": parsed, "content": str(parsed)}


@pytest.fixture
def mock_llm():
    mock = AsyncMock()
    mock.generate_structured = AsyncMock(return_value=_make_structured({
        "complexity_budget": "medium",
        "recommended_scope": "mvp",
        "risk_tolerance": "medium",
        "execution_capacity_score": 75.0,
    }))
    return mock


@pytest.fixture
def mock_challenge_llm():
    mock = AsyncMock()
    mock.generate_structured = AsyncMock(return_value=_make_structured({
        "themes": ["AI Healthcare"],
        "opportunities": ["Health monitoring"],
        "constraints": ["Data privacy"],
        "resource_opportunities": ["Use health dataset"],
        "evaluation_focus": ["innovation"],
    }))
    return mock


@pytest.fixture
def mock_problem_llm():
    mock = AsyncMock()
    mock.generate_structured = AsyncMock(return_value=_make_structured({
        "stakeholders": ["Patients", "Doctors"],
        "pain_points": ["Manual tracking"],
        "assumptions": ["Data available"],
        "success_metrics": ["Accuracy > 90%"],
        "problem_definition": "Improve health monitoring",
    }))
    return mock


@pytest.fixture
def mock_opportunity_llm():
    mock = AsyncMock()
    mock.generate_structured = AsyncMock(return_value=_make_structured({
        "market_gaps": ["No AI solution for X"],
        "innovation_opportunities": ["Use LLM for Y"],
        "high_impact_areas": ["Patient outcomes"],
        "technical_opportunities": ["Real-time processing"],
    }))
    return mock


@pytest.fixture
def mock_idea_llm():
    mock = AsyncMock()
    mock.generate_structured = AsyncMock(return_value=_make_structured({
        "ideas": [{
            "title": "AI Health Monitor",
            "description": "Monitor patient health with AI",
            "target_users": ["Patients", "Doctors"],
            "key_features": ["Real-time monitoring", "Alerts", "Dashboard"],
            "innovation_score": 85,
        }],
    }))
    return mock


@pytest.fixture
def mock_validator_llm():
    mock = AsyncMock()
    mock.generate_structured = AsyncMock(return_value=_make_structured({
        "innovation": 80,
        "feasibility": 70,
        "hackathon_fit": 90,
        "technical_wow": 85,
        "competitors": [],
        "open_source_projects": [],
        "available_apis": [],
        "strengths": ["Strong impact"],
        "weaknesses": ["Complex"],
        "risks": ["Data privacy"],
    }))
    return mock


@pytest.fixture
def mock_architect_llm():
    mock = AsyncMock()
    mock.generate_structured = AsyncMock(return_value=_make_structured({
        "vision": "AI health platform",
        "product_scope": "MVP",
        "features": [{"title": "Dashboard", "description": "Health dashboard", "priority": "critical"}],
        "user_stories": [{"actor": "Doctor", "goal": "view patient data", "benefit": "better care"}],
        "architecture": {"description": "Web app with API", "components": [], "connections": []},
        "api_design": [{"path": "/api/health", "method": "GET", "description": "Get health data"}],
        "database_schema": {"tables": [], "relationships": []},
        "integrations": [{"name": "OpenAI", "description": "AI analysis", "type": "api"}],
    }))
    return mock


@pytest.fixture
def mock_tech_stack_llm():
    mock = AsyncMock()
    mock.generate_structured = AsyncMock(return_value=_make_structured({
        "frontend": "Next.js",
        "backend": "FastAPI",
        "database": "PostgreSQL",
        "hosting": "Vercel",
        "ai_models": ["GPT-4"],
        "vector_db": "Pinecone",
        "auth_provider": "Clerk",
    }))
    return mock


@pytest.fixture
def mock_build_llm():
    mock = AsyncMock()
    mock.generate_structured = AsyncMock(return_value=_make_structured({
        "frontend_prompts": ["Create Next.js app with Tailwind"],
        "backend_prompts": ["Set up FastAPI with routes"],
        "database_prompts": ["Define SQLAlchemy models"],
        "ai_prompts": ["Integrate OpenAI"],
        "testing_prompts": ["Write pytest tests"],
        "deployment_prompts": ["Deploy to Vercel"],
    }))
    return mock


@pytest.fixture
def mock_presentation_llm():
    mock = AsyncMock()
    mock.generate_structured = AsyncMock(return_value=_make_structured({
        "slides": [{"title": "Problem", "content": "Health data is siloed", "type": "slide"}],
        "diagrams": [{"title": "Architecture", "description": "System diagram",
                       "diagram_type": "architecture", "content": "Web -> API -> DB"}],
        "demo_story": "Start with problem, show solution, end with impact",
    }))
    return mock


@pytest.fixture
def mock_pitch_llm():
    mock = AsyncMock()
    mock.generate_structured = AsyncMock(return_value=_make_structured({
        "pitch_30": "We solve health data silos with AI",
        "pitch_120": "Our platform connects health data",
        "pitch_300": "Full pitch with demo",
        "qa": [{"question": "How is this different?", "answer": "AI-first approach"}],
        "demo_script": "1. Open app, 2. Upload data, 3. See insights",
    }))
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
        "team_profile": {
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
        "team_profile": {
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
        "opportunity_analysis": {"market_gaps": [], "innovation_opportunities": [], "high_impact_areas": []},
        "team_profile": {"complexity_budget": "medium", "recommended_scope": "mvp", "skills": []},
    }
    gen_result = await gen_agent.run(gen_state)

    agent = IdeaValidatorAgent(llm=mock_validator_llm)
    state = {
        "generated_ideas": gen_result.output["ideas"],
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
    assert result.output["validation_reports"][0]["final_score"] == 80.0


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
        "team_profile": {
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
        "architecture": {
            "features": [{"title": "Dashboard", "priority": "critical"}],
            "api_design": [{"path": "/api/health", "method": "GET"}],
            "integrations": [{"name": "OpenAI", "type": "api"}],
        },
        "team_profile": {
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
        "generated_ideas": [],
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


@pytest.mark.asyncio
async def test_build_accelerator_agent(mock_build_llm) -> None:
    agent = BuildAcceleratorAgent(llm=mock_build_llm)
    state = {
        "architecture": {
            "vision": "Health platform",
            "product_scope": "MVP",
            "features": [{"title": "Dashboard", "priority": "critical"}],
            "api_design": [{"path": "/api/health", "method": "GET"}],
        },
        "tech_stack": {
            "frontend": "Next.js", "backend": "FastAPI",
            "database": "PostgreSQL", "hosting": "Vercel",
            "ai_models": ["GPT-4"],
        },
        "project": {"team_data": {"duration_hours": 24, "team_size": 4}},
        "challenge_intelligence": {"themes": ["AI Healthcare"]},
    }
    result = await agent.run(state)
    assert result.success
    assert result.output is not None
    assert len(result.output["frontend_prompts"]) > 0


@pytest.mark.asyncio
async def test_presentation_agent(mock_presentation_llm) -> None:
    agent = PresentationAgent(llm=mock_presentation_llm)
    state = {
        "architecture": {
            "vision": "Health platform",
            "features": [{"title": "Dashboard", "priority": "critical"}],
        },
        "generated_ideas": [{"title": "AI Health", "description": "Health AI"}],
        "selected_idea": {"title": "AI Health", "description": "Health AI"},
        "validation_reports": [{
            "final_score": 85,
            "strengths": ["AI powered"],
            "risks": ["Data privacy"],
        }],
    }
    result = await agent.run(state)
    assert result.success
    assert result.output is not None
    assert len(result.output["slides"]) > 0


@pytest.mark.asyncio
async def test_pitch_coach_agent(mock_pitch_llm) -> None:
    agent = PitchCoachAgent(llm=mock_pitch_llm)
    state = {
        "architecture": {
            "vision": "Health platform",
            "features": [{"title": "Dashboard"}],
        },
        "tech_stack": {
            "frontend": "Next.js", "backend": "FastAPI",
            "ai_models": ["GPT-4"],
        },
        "generated_ideas": [{"title": "AI Health", "description": "Health AI"}],
        "selected_idea": {"title": "AI Health", "description": "Health AI"},
        "validation_reports": [{
            "final_score": 85,
            "strengths": ["AI powered"],
        }],
        "challenge_intelligence": {"evaluation_focus": ["Innovation"]},
        "project": {"pitch_duration": 5},
    }
    result = await agent.run(state)
    assert result.success
    assert result.output is not None
    assert "pitch_30" in result.output
    assert len(result.output["qa"]) > 0


@pytest.mark.asyncio
async def test_registry_all_agents() -> None:
    AgentRegistry.clear()
    AgentRegistry.register(UserProfilerAgent())
    AgentRegistry.register(ChallengeIntelligenceAgent())
    AgentRegistry.register(ProblemAnalystAgent())
    AgentRegistry.register(OpportunityPlannerAgent())
    AgentRegistry.register(IdeaGeneratorAgent())
    AgentRegistry.register(IdeaValidatorAgent())
    AgentRegistry.register(SolutionArchitectAgent())
    AgentRegistry.register(TechStackAdvisorAgent())
    AgentRegistry.register(BuildAcceleratorAgent())
    AgentRegistry.register(PresentationAgent())
    AgentRegistry.register(PitchCoachAgent())

    assert len(AgentRegistry.get_all()) == 11
    assert AgentRegistry.get("build_accelerator") is not None
    assert AgentRegistry.get("presentation_agent") is not None
    assert AgentRegistry.get("pitch_coach") is not None
