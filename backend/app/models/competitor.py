"""Competitor Intelligence model — stores structured competitive analysis (Bible §6.2 S3)."""

import datetime
import uuid
from sqlalchemy import Column, String, DateTime, Float, Text, JSON
from app.models.base import Base


class CompetitorIntelligence(Base):
    """Structured competitive analysis report for a project (Bible §6.2 S3).

    Stores the output of the Competitor Analyst specialist.
    Contains competitor profiles, comparison matrix, gap analysis,
    differentiation opportunities, innovation scores, and warnings.
    """
    __tablename__ = "competitor_intelligence"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, nullable=False, unique=True, index=True)

    # Executive summary
    summary = Column(Text, nullable=True)
    landscape_summary = Column(Text, nullable=True)

    # Individual competitor profiles (JSON)
    competitors = Column(JSON, nullable=True)

    # Comparison matrix across dimensions
    comparison_matrix = Column(JSON, nullable=True)

    # Gap analysis
    gap_analysis = Column(JSON, nullable=True)

    # Differentiation opportunities
    quick_wins = Column(JSON, nullable=True)
    medium_innovations = Column(JSON, nullable=True)
    moonshots = Column(JSON, nullable=True)

    # Innovation score
    innovation_score = Column(Float, nullable=True)
    innovation_breakdown = Column(JSON, nullable=True)

    # Warnings
    warnings = Column(JSON, nullable=True)

    # Keywords extracted
    keywords = Column(JSON, nullable=True)
    themes = Column(JSON, nullable=True)

    # Metadata
    model_used = Column(String, nullable=True)
    confidence = Column(Float, nullable=True, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
