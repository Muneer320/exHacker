"""Idea Generation model — stores structured product ideas from S5 (Bible §6.2 S5)."""

import datetime
import uuid
from sqlalchemy import Column, String, DateTime, Float, Text, JSON, Integer
from app.models.base import Base


class Idea(Base):
    """A single generated product idea with scoring (Bible §6.2 S5).

    Each idea is a complete product concept with title, hook, elevator pitch,
    solution, features, demo scenario, scoring, and reasoning.
    """
    __tablename__ = "ideas"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, nullable=False, index=True)
    generation_id = Column(String, nullable=False, index=True)  # Groups ideas into a generation batch

    # Core content
    title = Column(String, nullable=False)
    hook = Column(String, nullable=True)       # One-line hook
    elevator_pitch = Column(Text, nullable=True)
    problem_statement = Column(Text, nullable=True)
    solution = Column(Text, nullable=True)
    target_users = Column(String, nullable=True)
    why_now = Column(Text, nullable=True)
    usp = Column(Text, nullable=True)           # Unique selling proposition

    # Strategy
    strategy_label = Column(String, nullable=True)  # e.g. "Most Innovative", "Most Practical"
    strategic_category = Column(String, nullable=True)  # e.g. "innovation", "practical", "judge_favorite"

    # Details
    innovation_summary = Column(Text, nullable=True)
    competitive_differentiation = Column(Text, nullable=True)
    technical_highlights = Column(Text, nullable=True)
    core_features = Column(JSON, nullable=True)
    stretch_features = Column(JSON, nullable=True)
    demo_scenario = Column(Text, nullable=True)
    judge_wow_moment = Column(Text, nullable=True)
    technical_risks = Column(JSON, nullable=True)
    business_potential = Column(Text, nullable=True)

    # Planning
    estimated_build_hours = Column(Integer, nullable=True)
    estimated_difficulty = Column(Float, nullable=True)  # 0-100
    recommended_team_size = Column(String, nullable=True)
    recommended_roles = Column(JSON, nullable=True)
    future_roadmap = Column(JSON, nullable=True)
    target_platform = Column(String, nullable=True)

    # Scoring (Bible §8.4 — 8 dimensions + overall)
    score_innovation = Column(Float, nullable=True)
    score_creativity = Column(Float, nullable=True)
    score_technical_depth = Column(Float, nullable=True)
    score_feasibility = Column(Float, nullable=True)
    score_demo_potential = Column(Float, nullable=True)
    score_judge_appeal = Column(Float, nullable=True)
    score_business_potential = Column(Float, nullable=True)
    score_originality = Column(Float, nullable=True)
    score_confidence = Column(Float, nullable=True)
    score_overall = Column(Float, nullable=True)

    # Reasoning
    why_generated = Column(Text, nullable=True)
    research_references = Column(JSON, nullable=True)
    gap_addressed = Column(String, nullable=True)

    # Comparison tags
    comparison_tags = Column(JSON, nullable=True)  # e.g. ["best_for_beginners", "fastest_to_build"]

    # UI state
    is_selected = Column(String, nullable=True)  # "selected" or None
    is_favorite = Column(String, nullable=True)  # "favorite" or None
    rank = Column(Integer, nullable=True)

    # Metadata
    model_used = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
