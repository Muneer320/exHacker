"""Research data models — expanded for S2 Research Specialist (Bible §6.2 S2)."""

import datetime
import uuid
from enum import Enum
from sqlalchemy import Column, String, DateTime, Float, Text, JSON, Boolean
from app.models.base import Base


class ResearchResultType(str, Enum):
    """Expanded research categories (10 categories per Bible)."""
    PRODUCT = "product"
    STARTUP = "startup"
    OSS = "oss"
    GITHUB = "github"
    PAPER = "paper"
    API = "api"
    FRAMEWORK = "framework"
    HACKATHON_WINNER = "hackathon_winner"
    TREND = "trend"
    INSIGHT = "insight"


class ResearchResult(Base):
    """Stores a single research result from any category."""
    __tablename__ = "research_results"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, nullable=False, index=True)
    report_id = Column(String, nullable=True, index=True)  # Groups results into a report
    query = Column(String, nullable=False)
    source = Column(String, nullable=False, default="tavily")
    result_type = Column(String, nullable=False, default=ResearchResultType.PRODUCT.value)

    # Core fields
    title = Column(String, nullable=False)
    url = Column(String, nullable=True)
    snippet = Column(Text, nullable=True)

    # Intelligence metadata
    relevance = Column(String, nullable=True)  # "high", "medium", "low"
    confidence = Column(Float, nullable=True)
    freshness = Column(String, nullable=True)  # "days", "weeks", "months", "years"
    why_relevant = Column(Text, nullable=True)  # Why this matters for the project

    # Categorization
    category = Column(String, nullable=True)  # Specific subcategory
    tags = Column(JSON, nullable=True)

    # Scoring
    relevance_score = Column(Float, nullable=True)
    extra_data = Column(JSON, nullable=True)

    # Caching
    cached_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Synthesis (for report-level data)
    is_synthesis = Column(Boolean, default=False, nullable=False)
