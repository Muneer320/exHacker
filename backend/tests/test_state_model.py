from __future__ import annotations

from schemas.state import (
    ArchitecturePackage,
    BuildPackage,
    ChallengeIntelligence,
    ExHackerState,
    ExportPackage,
    Idea,
    OpportunityAnalysis,
    PitchPackage,
    PresentationPackage,
    ProblemAnalysis,
    Project,
    TeamProfile,
    TechStack,
    ValidationReport,
    WorkflowMetadata,
)


def test_exhacker_state_defaults():
    state = ExHackerState()
    assert state.metadata.status == "created"
    assert state.metadata.current_stage == "challenge_intelligence"
    assert isinstance(state.project, Project)
    assert state.team_profile is None
    assert state.challenge_intelligence is None
    assert state.problem_analysis is None
    assert state.opportunity_analysis is None
    assert state.generated_ideas == []
    assert state.validation_reports == []
    assert state.selected_idea is None
    assert state.tech_stack is None
    assert state.architecture is None
    assert state.build_package is None
    assert state.prompt_package is None
    assert state.presentation is None
    assert state.pitch is None
    assert state.exports is None
    assert state.execution is None
    assert state.errors == []


def test_workflow_metadata_defaults():
    meta = WorkflowMetadata()
    assert meta.status == "created"
    assert meta.current_stage == "challenge_intelligence"
    assert meta.project_id == ""
    assert len(meta.workflow_id) > 0


def test_project_defaults():
    project = Project()
    assert project.name == ""
    assert project.challenge_statements == []
    assert project.duration_hours == 48
    assert project.resources is None


def test_team_profile():
    profile = TeamProfile(team_size=3, experience_level="advanced")
    assert profile.team_size == 3
    assert profile.experience_level == "advanced"
    assert profile.known_technologies == []
    assert profile.preferred_technologies == []


def test_challenge_intelligence():
    ci = ChallengeIntelligence(
        themes=["AI", "Healthcare"],
        constraints=["24 hours"],
    )
    assert len(ci.themes) == 2
    assert len(ci.constraints) == 1


def test_problem_analysis():
    pa = ProblemAnalysis(
        stakeholders=["Students", "Teachers"],
        pain_points=["Lack of time"],
        refined_problem_statement="Improve education",
    )
    assert len(pa.stakeholders) == 2
    assert pa.refined_problem_statement == "Improve education"


def test_opportunity_analysis():
    oa = OpportunityAnalysis(
        market_gaps=["No solution for X"],
        innovation_opportunities=["AI-powered Y"],
    )
    assert len(oa.market_gaps) == 1


def test_idea():
    idea = Idea(
        title="AI Tutor",
        description="An AI-powered tutor",
        innovation_score=8,
    )
    assert idea.title == "AI Tutor"
    assert idea.innovation_score == 8


def test_validation_report():
    vr = ValidationReport(
        idea_id="test-id",
        strengths=["Novel approach"],
        weaknesses=["Needs data"],
        feasibility_score=7,
        innovation_score=8,
        final_score=7.5,
    )
    assert vr.final_score == 7.5
    assert isinstance(vr.final_score, float)
    assert len(vr.strengths) == 1


def test_tech_stack():
    ts = TechStack(
        frontend="Next.js",
        backend="FastAPI",
        database="PostgreSQL",
    )
    assert ts.frontend == "Next.js"
    assert ts.database == "PostgreSQL"


def test_architecture_package():
    arch = ArchitecturePackage(system_design="Microservices")
    assert arch.system_design == "Microservices"
    assert arch.components == []


def test_build_package():
    bp = BuildPackage(frontend_tasks=["Create login page"])
    assert len(bp.frontend_tasks) == 1


def test_presentation_package():
    pres = PresentationPackage(demo_story="User logs in and sees dashboard")
    assert "dashboard" in pres.demo_story


def test_pitch_package():
    pitch = PitchPackage(pitch_30s="We solve X")
    assert pitch.pitch_30s == "We solve X"


def test_export_package():
    export = ExportPackage(readme="# Project")
    assert export.readme == "# Project"


def test_exhacker_state_with_data():
    state = ExHackerState(
        project=Project(name="My Hackathon Project"),
        team_profile=TeamProfile(team_size=4),
        challenge_intelligence=ChallengeIntelligence(themes=["AI"]),
        problem_analysis=ProblemAnalysis(pain_points=["Time"]),
        generated_ideas=[Idea(title="Idea 1"), Idea(title="Idea 2")],
        selected_idea=Idea(title="Idea 1"),
        tech_stack=TechStack(frontend="React"),
    )
    assert state.project.name == "My Hackathon Project"
    assert state.team_profile is not None
    assert state.team_profile.team_size == 4
    assert state.challenge_intelligence is not None
    assert len(state.generated_ideas) == 2
    assert state.selected_idea is not None
    assert state.selected_idea.title == "Idea 1"
    assert state.tech_stack is not None
    assert state.tech_stack.frontend == "React"
