"""Project model."""

import datetime
import uuid
from enum import Enum

from sqlalchemy import Column, DateTime, String

from app.models.base import Base


class ProjectStatus(str, Enum):
    """Approved 4-state lifecycle for V1.

    DRAFT → PROCESSING → READY → ARCHIVED
    """
    DRAFT = "draft"
    PROCESSING = "processing"
    READY = "ready"
    ARCHIVED = "archived"


class ProjectModel(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=True, index=True)
    name = Column(String, nullable=False, default="Untitled Project")
    description = Column(String, nullable=True)
    idea = Column(String, nullable=False)
    status = Column(String, nullable=False, default=ProjectStatus.DRAFT.value)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
