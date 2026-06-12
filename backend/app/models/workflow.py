import datetime
from sqlalchemy import Column, String, JSON, DateTime, ForeignKey
from app.models.base import Base


class WorkflowStateModel(Base):
    __tablename__ = "workflow_states"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    status = Column(String, nullable=False, default="created")
    current_stage = Column(String, nullable=False, default="challenge_intelligence")
    state_json = Column(JSON, nullable=False)  # Stores serialized ExHackerStateSchema
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
