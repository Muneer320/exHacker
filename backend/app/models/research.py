"""Research data models."""

import datetime
import uuid
from enum import Enum
from sqlalchemy import Column, String, DateTime, Float, Text, JSON
from app.models.base import Base


class ResearchResultType(str, Enum):
    COMPETITOR = "competitor"
    API = "api"
    OSS = "oss"
    INSIGHT = "insight"


class ResearchResult(Base):
    """Stores a single research result (competitor, API, or OSS project)."""
    __tablename__ = "research_results"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, nullable=False, index=True)
    query = Column(String, nullable=False)
    source = Column(String, nullable=False, default="tavily")
    result_type = Column(String, nullable=False, default=ResearchResultType.COMPETITOR.value)
    title = Column(String, nullable=False)
    url = Column(String, nullable=True)
    snippet = Column(Text, nullable=True)
    relevance_score = Column(Float, nullable=True)
    extra_data = Column(JSON, nullable=True)  # Extra data like stars, pricing, etc.
    cached_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
