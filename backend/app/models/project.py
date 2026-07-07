"""Project model — the primary entity in exHacker.

Bible §8.1 defines 16 fields. This model implements V1 with the most essential fields.
Fields are added incrementally as downstream specialists require them.
"""

import datetime
import uuid
from enum import Enum

from sqlalchemy import Column, DateTime, String, Text

from app.models.base import Base


class ProjectStatus(str, Enum):
    """Project lifecycle states (Bible §9.4 — V1: 7 states)."""
    DRAFT = "draft"
    PROCESSING = "processing"  # Legacy alias for RESEARCHING
    RESEARCHING = "researching"
    IDEAS_READY = "ideas_ready"
    DIRECTION_SELECTED = "direction_selected"
    ARCHITECTING = "architecting"
    READY = "ready"
    EXPORTED = "exported"
    FAILED = "failed"
    ARCHIVED = "archived"


class ProjectModel(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=True, index=True)

    # Core project info
    name = Column(String, nullable=False, default="Untitled Project")
    description = Column(String, nullable=True)
    idea = Column(String, nullable=False)
    status = Column(String, nullable=False, default=ProjectStatus.DRAFT.value)

    # Challenge context (for S1 — Challenge Analyst)
    challenge_statement = Column(Text, nullable=True)
    theme = Column(String, nullable=True)
    organizer = Column(String, nullable=True)
    evaluation_criteria = Column(Text, nullable=True)
    rules = Column(Text, nullable=True)

    # Team context (for planning, feasibility scoring)
    available_hours = Column(String, nullable=True)  # "24h", "36h", "48h", etc.
    team_size = Column(String, nullable=True)        # "1", "2", "3", "4", "5+"
    team_experience = Column(String, nullable=True)  # "beginner", "intermediate", "advanced"
    preferred_languages = Column(String, nullable=True)  # comma-separated
    preferred_frameworks = Column(String, nullable=True) # comma-separated
    target_platform = Column(String, nullable=True)     # "web", "mobile", "desktop", "cli", "iot"
    skills = Column(Text, nullable=True)                 # comma-separated tags
    excluded_technologies = Column(Text, nullable=True)  # comma-separated
    constraints = Column(Text, nullable=True)            # Additional constraints

    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
