"""Challenge Intelligence model — structured analysis of hackathon challenges (Bible §8.2).

Stores the output of the Challenge Analyst specialist (S1).
Each row is a complete intelligence report for one project.
"""
import datetime
import uuid
from sqlalchemy import Column, String, DateTime, Float, Text, JSON
from app.models.base import Base


class ChallengeIntelligence(Base):
    """Structured understanding of a hackathon challenge (Bible §8.2, §6.2 S1)."""
    __tablename__ = "challenge_intelligence"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, nullable=False, unique=True, index=True)

    # Executive summary — one-paragraph interpretation
    executive_summary = Column(Text, nullable=True)

    # Core problem analysis
    core_problem = Column(Text, nullable=True)
    who_experiences = Column(String, nullable=True)
    why_important = Column(Text, nullable=True)

    # Hidden problems (things implied but not stated)
    hidden_problems = Column(JSON, nullable=True)  # list[str]

    # Stakeholders
    stakeholders = Column(JSON, nullable=True)  # list[{role, description}]

    # Constraints — all types unified
    constraints = Column(JSON, nullable=True)  # list[{type, description}]

    # Success criteria with inferred weights
    success_criteria = Column(JSON, nullable=True)  # list[{criterion, weight, description}]

    # Opportunity spaces (not final ideas)
    opportunity_areas = Column(JSON, nullable=True)  # list[str]

    # Innovation opportunities likely to impress judges
    innovation_opportunities = Column(JSON, nullable=True)  # list[{area, description}]

    # Risk areas — common mistakes
    risk_areas = Column(JSON, nullable=True)  # list[{area, severity, description}]

    # Difficulty assessment (0-100 scale)
    difficulty_technical = Column(Float, nullable=True)
    difficulty_research = Column(Float, nullable=True)
    difficulty_demo = Column(Float, nullable=True)
    difficulty_judge = Column(Float, nullable=True)
    difficulty_overall = Column(Float, nullable=True)

    # Recommended strategy (mentor-style advice)
    recommended_strategy = Column(Text, nullable=True)

    # Themes extracted from challenge
    themes = Column(JSON, nullable=True)  # list[str]
    keywords = Column(JSON, nullable=True)  # list[str]

    # Metadata
    confidence = Column(Float, nullable=True, default=0.0)
    model_used = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
