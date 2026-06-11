from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, String, Text

from app.db.base import Base


class ProjectModel(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), default="")
    challenge_statements = Column(JSON, default=list)
    duration_hours = Column(Text, default="48")
    team_profile = Column(JSON, nullable=True)
    status = Column(String(50), default="created")
    workflow_state = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
