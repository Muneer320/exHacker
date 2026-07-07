"""Direction model — stores generated product directions with 8-dimension scoring."""

import datetime
import uuid
from sqlalchemy import Column, String, DateTime, Float, Text, Boolean, JSON
from app.models.base import Base


class Direction(Base):
    """A generated product direction for a project.

    Each direction has 8 score dimensions (Bible §5.5):
      1. Innovation — How novel is this idea?
      2. Creativity — How creative is the approach?
      3. Technical Depth — Does it demonstrate skill?
      4. Feasibility — Can it be built in the available time?
      5. Demo Potential — How impressive will the demo be?
      6. Judge Appeal — How well does it match judging criteria?
      7. Business Potential — Could this become a real product?
      8. Overall Confidence — How confident is the system?
    """
    __tablename__ = "directions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    tagline = Column(String, nullable=False)

    # Content
    elevator_pitch = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    problem_statement = Column(Text, nullable=True)
    solution = Column(Text, nullable=True)
    differentiation = Column(Text, nullable=True)
    core_features = Column(JSON, nullable=True)    # list[str]
    stretch_features = Column(JSON, nullable=True)  # list[str]
    risks = Column(JSON, nullable=True)             # list[{title, severity, mitigation}]

    # 8-dimension scoring (Bible §5.5)
    innovation_score = Column(Float, nullable=True)
    creativity_score = Column(Float, nullable=True)
    technical_depth_score = Column(Float, nullable=True)
    feasibility_score = Column(Float, nullable=True)
    demo_potential_score = Column(Float, nullable=True)
    judge_appeal_score = Column(Float, nullable=True)
    business_potential_score = Column(Float, nullable=True)
    overall_score = Column(Float, nullable=True)

    # Estimated effort
    estimated_effort_hours = Column(Float, nullable=True)

    # Selection state
    is_selected = Column(Boolean, nullable=False, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
