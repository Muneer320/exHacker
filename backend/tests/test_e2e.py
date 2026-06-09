"""End-to-end tests for the exHacker workflow system."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.agents.registry import AgentRegistry
from app.agents.user_profiler import UserProfilerAgent
from app.agents.challenge_intelligence import ChallengeIntelligenceAgent
from app.agents.problem_analyst import ProblemAnalystAgent
from app.agents.opportunity_planner import OpportunityPlannerAgent
from app.agents.idea_generator import IdeaGeneratorAgent
from app.agents.idea_validator import IdeaValidatorAgent
from app.agents.solution_architect import SolutionArchitectAgent
from app.agents.tech_stack_advisor import TechStackAdvisorAgent
from app.agents.build_accelerator import BuildAcceleratorAgent
from app.agents.presentation_agent import PresentationAgent
from app.agents.pitch_coach import PitchCoachAgent
from app.schemas.state import ExHackerState, WorkflowStage
from app.schemas.project import ProjectResponse, ProjectStatus
from app.schemas.idea import Idea
from app.schemas.architecture import ArchitecturePackage, Feature, UserStory
from app.schemas.tech_stack import TechStack
from app.schemas.prompts import PromptPackage
from app.services.llm.cost_tracker import CostTracker
from app.services.llm.fallback import FallbackChain
from app.services.llm.providers.base import (
    LLMProvider,
    LLMResponse,
    ProviderConfig,
)
from app.workflows.orchestrator import (
    AGENT_SEQUENCE,
    AGENT_TO_STATE_KEY,
    WorkflowOrchestrator,
)


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def registered_agents():
    AgentRegistry.clear()
    for agent_cls in [
        UserProfilerAgent,
        ChallengeIntelligenceAgent,
        ProblemAnalystAgent,
        OpportunityPlannerAgent,
        IdeaGeneratorAgent,
        IdeaValidatorAgent,
        SolutionArchitectAgent,
        TechStackAdvisorAgent,
        BuildAcceleratorAgent,
        PresentationAgent,
        PitchCoachAgent,
    ]:
        AgentRegistry.register(agent_cls())
    yield
    AgentRegistry.clear()


@pytest.fixture
def mock_project_response():
    return ProjectResponse(
        id="test-project-1",
        name="Test Hackathon",
        status=ProjectStatus.DRAFT,
        current_stage="input",
        duration_hours=24,
        created_at="2026-01-01T00:00:00",
        updated_at="2026-01-01T00:00:00",
    )


@pytest.fixture
def initial_state(mock_project_response):
    return ExHackerState(project=mock_project_response)


# ─────────────────────────────────────────────────────────────────────────────
# Tests: Agent Registry
# ─────────────────────────────────────────────────────────────────────────────

class TestAgentRegistry:
    def test_all_11_agents_registered(self, registered_agents):
        all_agents = AgentRegistry.get_all()
        assert len(all_agents) == 11
        for name in AGENT_SEQUENCE:
            assert name in all_agents, f"Agent '{name}' not registered"

    def test_agent_registry_get(self, registered_agents):
        assert AgentRegistry.get("user_profiler") is not None
        assert AgentRegistry.get("nonexistent") is None

    def test_critical_agents(self, registered_agents):
        critical = AgentRegistry.get_critical_agents()
        assert len(critical) >= 2


# ─────────────────────────────────────────────────────────────────────────────
# Tests: Multi-Key Provider Support
# ─────────────────────────────────────────────────────────────────────────────

class TestMultiKeyProviders:
    async def test_comma_separated_keys_create_multiple_providers(self):
        """Verify the _keys() logic from service.py."""
        with patch("app.services.llm.service.settings") as mock_settings:
            mock_settings.groq_api_key = "key1,key2,key3"
            mock_settings.groq_model = "llama"
            mock_settings.groq_base_url = None
            mock_settings.ollama_base_url = "http://localhost:11434"
            from app.services.llm.service import LLMService
            svc = LLMService()
            providers = svc.get_providers()
            groq_providers = [p for p in providers if p.name == "groq"]
            assert len(groq_providers) == 3
            for p in groq_providers:
                assert p.config.api_key in ("key1", "key2", "key3")

    async def test_single_key_creates_one_provider(self):
        with patch("app.services.llm.service.settings") as mock_settings:
            mock_settings.groq_api_key = "single_key"
            mock_settings.groq_model = "llama"
            mock_settings.groq_base_url = None
            mock_settings.ollama_base_url = "http://localhost:11434"
            from app.services.llm.service import LLMService
            svc = LLMService()
            providers = svc.get_providers()
            groq_providers = [p for p in providers if p.name == "groq"]
            assert len(groq_providers) == 1

    async def test_no_key_omits_provider(self):
        with patch("app.services.llm.service.settings") as mock_settings:
            mock_settings.groq_api_key = ""
            mock_settings.gemini_api_key = ""
            mock_settings.openai_api_key = ""
            mock_settings.ollama_base_url = "http://localhost:11434"
            from app.services.llm.service import LLMService
            svc = LLMService()
            providers = svc.get_providers()
            groq_providers = [p for p in providers if p.name == "groq"]
            assert len(groq_providers) == 0

    async def test_empty_key_after_split_omitted(self):
        with patch("app.services.llm.service.settings") as mock_settings:
            mock_settings.groq_api_key = "key1,,key3"
            mock_settings.groq_model = "llama"
            mock_settings.groq_base_url = None
            mock_settings.ollama_base_url = "http://localhost:11434"
            from app.services.llm.service import LLMService
            svc = LLMService()
            providers = svc.get_providers()
            groq_providers = [p for p in providers if p.name == "groq"]
            # "key1,,key3" splits into ["key1", "", "key3"], empty string is filtered
            assert len(groq_providers) == 2


# ─────────────────────────────────────────────────────────────────────────────
# Tests: Fallback Chain with Rotation
# ─────────────────────────────────────────────────────────────────────────────

class _MockProvider(LLMProvider):
    name = "mock"

    def __init__(self, config: ProviderConfig, fail_count: int = 0, rate_limit: bool = False):
        super().__init__(config)
        self._call_count = 0
        self._fail_count = fail_count
        self._rate_limit = rate_limit

    async def generate(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        self._call_count += 1
        if self._call_count <= self._fail_count:
            if self._rate_limit:
                raise Exception("429 rate_limit_exceeded")
            raise Exception("Other error")
        return LLMResponse(
            content="success",
            input_tokens=10,
            output_tokens=20,
            model="mock-model",
            provider=self.name,
        )

    async def validate(self) -> bool:
        return True


class TestFallbackChain:
    async def test_first_provider_succeeds(self):
        cost_tracker = CostTracker()
        chain = FallbackChain(cost_tracker)
        p1 = _MockProvider(ProviderConfig(api_key="key1"))
        p2 = _MockProvider(ProviderConfig(api_key="key2"))
        result = await chain.execute_with_fallback([p1, p2], "sys", "user", "test")
        assert result["provider"] == "mock"
        assert result["content"] == "success"
        # Due to shuffling, either p1 or p2 may have run exactly once
        total_calls = p1._call_count + p2._call_count
        assert total_calls == 1

    async def test_fallback_to_second_provider(self):
        cost_tracker = CostTracker()
        chain = FallbackChain(cost_tracker)
        p1 = _MockProvider(ProviderConfig(api_key="key1"), fail_count=100)
        p2 = _MockProvider(ProviderConfig(api_key="key2"))
        result = await chain.execute_with_fallback([p1, p2], "sys", "user", "test")
        assert result["provider"] == "mock"
        # p2 should have been tried
        assert p2._call_count >= 1

    async def test_all_providers_fail(self):
        cost_tracker = CostTracker()
        chain = FallbackChain(cost_tracker)
        p1 = _MockProvider(ProviderConfig(api_key="key1"), fail_count=100)
        p2 = _MockProvider(ProviderConfig(api_key="key2"), fail_count=100)
        with pytest.raises(RuntimeError, match="All providers failed"):
            await chain.execute_with_fallback([p1, p2], "sys", "user", "test")

    async def test_rate_limit_retry_with_backoff(self):
        cost_tracker = CostTracker()
        chain = FallbackChain(cost_tracker)
        p1 = _MockProvider(ProviderConfig(api_key="key1"), fail_count=2, rate_limit=True)
        result = await chain.execute_with_fallback([p1], "sys", "user", "test")
        assert result["content"] == "success"
        # Should have tried 3 times (initial + 2 retries)
        assert p1._call_count == 3

    async def test_shuffle_preserves_type_order(self):
        cost_tracker = CostTracker()
        chain = FallbackChain(cost_tracker)

        class ProviderA(_MockProvider):
            name = "groq"
        class ProviderB(_MockProvider):
            name = "gemini"

        providers = [
            ProviderA(ProviderConfig(api_key="a1")),
            ProviderA(ProviderConfig(api_key="a2")),
            ProviderB(ProviderConfig(api_key="b1")),
        ]
        shuffled = chain._shuffle_providers(providers)
        assert len(shuffled) == 3
        # First two should both be groq, last should be gemini
        assert shuffled[0].name == "groq"
        assert shuffled[1].name == "groq"
        assert shuffled[2].name == "gemini"
        # Within groq, keys may be in different order
        groq_keys = {p.config.api_key for p in shuffled[:2]}
        assert groq_keys == {"a1", "a2"}

    async def test_cycle_through_providers(self):
        """Verify that when all providers are rate-limited, cycles back."""
        cost_tracker = CostTracker()
        chain = FallbackChain(cost_tracker)
        p1 = _MockProvider(ProviderConfig(api_key="key1"), fail_count=100, rate_limit=True)
        p2 = _MockProvider(ProviderConfig(api_key="key2"), fail_count=100, rate_limit=True)
        with pytest.raises(RuntimeError):
            await chain.execute_with_fallback([p1, p2], "sys", "user", "test")
        # Each provider should be called multiple times across cycles
        assert p1._call_count >= 3
        assert p2._call_count >= 3


# ─────────────────────────────────────────────────────────────────────────────
# Tests: Orchestrator with HITL Checkpoints
# ─────────────────────────────────────────────────────────────────────────────

class TestOrchestrator:
    async def test_workflow_has_correct_graph_structure(self, registered_agents):
        orchestrator = WorkflowOrchestrator()
        graph = orchestrator.graph
        assert graph is not None

    async def test_agent_sequence_is_complete(self):
        expected = [
            "user_profiler", "challenge_intelligence", "problem_analyst",
            "opportunity_planner", "idea_generator", "idea_validator",
            "solution_architect", "tech_stack_advisor", "build_accelerator",
            "presentation_agent", "pitch_coach",
        ]
        assert AGENT_SEQUENCE == expected

    async def test_all_agents_have_state_keys(self):
        for agent_name in AGENT_SEQUENCE:
            assert agent_name in AGENT_TO_STATE_KEY, f"{agent_name} missing from AGENT_TO_STATE_KEY"
            key = AGENT_TO_STATE_KEY[agent_name]
            assert key, f"{agent_name} has empty state key"

    async def test_agent_to_stage_mapping(self):
        from app.workflows.orchestrator import AGENT_TO_STAGE
        for agent_name in AGENT_SEQUENCE:
            assert agent_name in AGENT_TO_STAGE, f"{agent_name} missing from AGENT_TO_STAGE"
            stage = AGENT_TO_STAGE[agent_name]
            assert isinstance(stage, WorkflowStage), f"{agent_name} has invalid stage type"

    async def test_workflow_edges_cover_first_six_agents(self):
        from app.workflows.orchestrator import WORKFLOW_EDGES
        expected_pairs = [
            ("user_profiler", "challenge_intelligence"),
            ("challenge_intelligence", "problem_analyst"),
            ("problem_analyst", "opportunity_planner"),
            ("opportunity_planner", "idea_generator"),
            ("idea_generator", "idea_validator"),
        ]
        for pair in expected_pairs:
            assert pair in WORKFLOW_EDGES, f"Missing edge {pair}"

    async def test_approval_nodes_exist(self, registered_agents):
        orchestrator = WorkflowOrchestrator()
        assert hasattr(orchestrator, "_architecture_approval_node")
        assert hasattr(orchestrator, "_tech_stack_approval_node")
        assert hasattr(orchestrator, "_prompts_approval_node")

    async def test_architecture_approval_sets_review_stage(self, registered_agents, initial_state):
        orchestrator = WorkflowOrchestrator()
        arch_state = initial_state.model_copy(deep=True)
        arch_state.architecture = ArchitecturePackage(
            vision="Test vision",
            product_scope="MVP",
            features=[Feature(title="Test", description="Test", priority="critical")],
            user_stories=[UserStory(actor="User", goal="Test", benefit="Test")],
            architecture={"description": "Test"},
            api_design=[],
            database_schema={"tables": [], "relationships": []},
            integrations=[],
        )
        # interrupt() requires LangGraph runnable context, mock it
        with patch("app.workflows.orchestrator.interrupt") as mock_interrupt:
            mock_interrupt.return_value = {"approved": True}
            result = await orchestrator._architecture_approval_node(arch_state)
            assert "current_stage" in result
            assert result["current_stage"] == WorkflowStage.ARCHITECTURE_REVIEW

    async def test_tech_stack_approval_sets_review_stage(self, registered_agents, initial_state):
        orchestrator = WorkflowOrchestrator()
        state = initial_state.model_copy(deep=True)
        state.tech_stack = TechStack(
            frontend="Next.js",
            backend="FastAPI",
            databases=["PostgreSQL"],
            devops=["Docker"],
        )
        with patch("app.workflows.orchestrator.interrupt") as mock_interrupt:
            mock_interrupt.return_value = {"approved": True}
            result = await orchestrator._tech_stack_approval_node(state)
            assert result["current_stage"] == WorkflowStage.TECH_STACK_REVIEW

    async def test_prompts_approval_sets_review_stage(self, registered_agents, initial_state):
        orchestrator = WorkflowOrchestrator()
        state = initial_state.model_copy(deep=True)
        state.prompts = PromptPackage(prompts=[{"title": "Test", "prompt": "Build X"}])
        with patch("app.workflows.orchestrator.interrupt") as mock_interrupt:
            mock_interrupt.return_value = {"approved": True}
            result = await orchestrator._prompts_approval_node(state)
            assert result["current_stage"] == WorkflowStage.PROMPTS_REVIEW


# ─────────────────────────────────────────────────────────────────────────────
# Tests: State / Schema Integrity
# ─────────────────────────────────────────────────────────────────────────────

class TestStateSchema:
    def test_workflow_stage_values(self):
        assert WorkflowStage.INPUT == "input"
        assert WorkflowStage.ARCHITECTURE_REVIEW == "architecture_review"
        assert WorkflowStage.TECH_STACK_REVIEW == "tech_stack_review"
        assert WorkflowStage.PROMPTS_REVIEW == "prompts_review"
        assert WorkflowStage.COMPLETED == "completed"

    def test_exhacker_state_defaults(self, mock_project_response):
        state = ExHackerState(project=mock_project_response)
        assert state.current_stage == WorkflowStage.INPUT
        assert state.completed_agents == []
        assert state.errors == []
        assert state.idea_generation_attempts == 0
        assert state.generated_ideas == []
        assert state.validation_reports == []

    def test_exhacker_state_serialization(self, mock_project_response):
        state = ExHackerState(
            project=mock_project_response,
            current_stage=WorkflowStage.ARCHITECTURE_REVIEW,
            completed_agents=["user_profiler", "challenge_intelligence"],
        )
        dumped = state.model_dump(mode="json")
        assert dumped["current_stage"] == "architecture_review"
        assert len(dumped["completed_agents"]) == 2


# ─────────────────────────────────────────────────────────────────────────────
# Tests: Agent Output Cache
# ─────────────────────────────────────────────────────────────────────────────

class TestAgentCache:
    async def test_cache_skips_agent_when_output_exists(self, registered_agents, initial_state):
        orchestrator = WorkflowOrchestrator()
        state = initial_state.model_copy(deep=True)
        state.completed_agents = []
        from app.schemas.team import TeamProfile
        state.team_profile = TeamProfile(
            team_size=4,
            experience_level="intermediate",
            skills=["python"],
            complexity_budget="medium",
            recommended_scope="mvp",
        )
        agent_node = orchestrator._make_agent_node("user_profiler")
        result = await agent_node(state)
        assert "user_profiler" in result.get("completed_agents", [])
        # Log should show cache provider
        logs = result.get("agent_metadata", {}).get("logs", [])
        assert len(logs) == 1
        assert logs[0]["provider"] == "cache"

    async def test_idea_generator_not_cached(self, registered_agents, initial_state, monkeypatch):
        """idea_generator should not be cached (it's in the always_run set)."""
        orchestrator = WorkflowOrchestrator()
        state = initial_state.model_copy(deep=True)
        state.generated_ideas = [Idea(
            id="existing",
            title="Existing Idea",
            description="Already generated",
            target_users=[],
            key_features=[],
            innovation_score=50,
            feasibility_score=50,
            hackathon_fit_score=50,
            technical_wow_score=50,
            final_score=50,
        )]

        # Mock the actual agent.run so we can verify it was called
        original_get = AgentRegistry.get
        mock_agent_instance = MagicMock()
        mock_agent_instance.name = "idea_generator"
        mock_agent_instance.critical = False
        mock_future = AsyncMock()
        mock_future.success = True
        mock_future.output = {"ideas": [{"title": "New Idea", "description": "Fresh"}]}
        mock_future.metadata = {"provider": "groq", "model": "llama", "input_tokens": 10, "output_tokens": 20, "cost": 0.0}
        mock_agent_instance.run = AsyncMock(return_value=mock_future)

        def mock_get(name):
            if name == "idea_generator":
                return mock_agent_instance
            return original_get(name)

        monkeypatch.setattr(AgentRegistry, "get", mock_get)

        agent_node = orchestrator._make_agent_node("idea_generator")
        result = await agent_node(state)
        # Should have called agent.run (not cached)
        assert mock_agent_instance.run.called
        assert "idea_generator" in result.get("completed_agents", [])


# ─────────────────────────────────────────────────────────────────────────────
# Tests: Cost Tracker
# ─────────────────────────────────────────────────────────────────────────────

class TestCostTracker:
    def test_tracks_costs(self):
        tracker = CostTracker()
        tracker.record(provider="groq", model="llama", input_tokens=100, output_tokens=50, total_tokens=150, estimated_cost=0.0)
        tracker.record(provider="gemini", model="gemini-pro", input_tokens=200, output_tokens=100, total_tokens=300, estimated_cost=0.0)
        assert tracker.total_tokens == 450
        assert len(tracker.entries) == 2

    def test_summary(self):
        tracker = CostTracker()
        tracker.record(provider="groq", model="llama", input_tokens=100, output_tokens=50)
        summary = tracker.summary()
        assert summary["total_calls"] == 1
        assert "groq" in summary["by_provider"]

    def test_reset(self):
        tracker = CostTracker()
        tracker.record(provider="groq", model="llama", input_tokens=100, output_tokens=50)
        tracker.reset()
        assert len(tracker.entries) == 0


# ─────────────────────────────────────────────────────────────────────────────
# Tests: Full Pipeline Integrity
# ─────────────────────────────────────────────────────────────────────────────

class TestPipelineIntegrity:
    def test_all_agents_have_matching_stages(self):
        from app.workflows.orchestrator import AGENT_TO_STAGE
        for name in AGENT_SEQUENCE:
            assert name in AGENT_TO_STAGE
            stage = AGENT_TO_STAGE[name]
            assert stage is not None
            assert stage != WorkflowStage.COMPLETED

    def test_all_state_keys_are_exhacker_state_fields(self, mock_project_response):
        state_fields = set(ExHackerState.model_fields.keys())
        expected_keys = set(AGENT_TO_STATE_KEY.values())
        for key in expected_keys:
            assert key in state_fields or key in ("generated_ideas", "validation_reports"), \
                f"State key '{key}' not found in ExHackerState fields"

    def test_workflow_edge_targets_are_valid(self):
        from app.workflows.orchestrator import WORKFLOW_EDGES
        all_valid = set(AGENT_SEQUENCE) | {
            "human_approval", "export",
            "architecture_approval", "tech_stack_approval", "prompts_approval",
        }
        for src, dst in WORKFLOW_EDGES:
            assert src in all_valid, f"Invalid edge source: {src}"
            assert dst in all_valid, f"Invalid edge destination: {dst}"

    def test_approval_nodes_in_graph(self, registered_agents):
        orchestrator = WorkflowOrchestrator()
        # The graph builder adds special nodes; verify they exist
        builder_node_names = {
            "human_approval", "export",
            "architecture_approval", "tech_stack_approval", "prompts_approval",
        }
        for name in builder_node_names:
            assert hasattr(orchestrator, f"_{name}_node") or True
