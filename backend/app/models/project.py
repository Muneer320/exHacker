import datetime
from sqlalchemy import Column, String, Integer, JSON, DateTime
from app.models.base import Base


class ProjectModel(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    challenge_statements = Column(JSON, nullable=False)
    duration_hours = Column(Integer, nullable=False)
    team_profile = Column(JSON, nullable=True)  # Stores serialized TeamProfile Pydantic model
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
