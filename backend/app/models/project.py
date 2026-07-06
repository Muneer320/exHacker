"""Project model."""

import datetime
import uuid
from enum import Enum
from sqlalchemy import Column, String, DateTime
from app.models.base import Base


class ProjectStatus(str, Enum):
    DRAFT = "draft"
    RESEARCHING = "researching"
    DIRECTIONS_READY = "directions_ready"
    BLUEPRINTING = "blueprinting"
    READY = "ready"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    CANCELLED = "cancelled"


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

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "description": self.description,
            "idea": self.idea,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
