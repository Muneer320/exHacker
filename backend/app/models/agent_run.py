import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey
from app.models.base import Base


class AgentRunModel(Base):
    __tablename__ = "agent_runs"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    workflow_id = Column(String, ForeignKey("workflow_states.id"), nullable=False, index=True)
    agent_name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    duration_seconds = Column(Float, nullable=False, default=0.0)
    tokens_used = Column(Integer, nullable=False, default=0)
    cost = Column(Float, nullable=False, default=0.0)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
