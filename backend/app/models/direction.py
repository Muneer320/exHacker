"""Direction model — stores generated product directions."""

import datetime
import uuid
from sqlalchemy import Column, String, DateTime, Float, Text, Boolean
from app.models.base import Base


class Direction(Base):
    """A generated product direction for a project."""
    __tablename__ = "directions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    tagline = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    innovation_score = Column(Float, nullable=True)
    feasibility_score = Column(Float, nullable=True)
    is_selected = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
