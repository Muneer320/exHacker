import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Enum, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum(
            "draft",
            "researching",
            "idea_generation",
            "architecture",
            "completed",
            name="project_status",
        ),
        default="draft",
        nullable=False,
    )
    current_stage: Mapped[str] = mapped_column(String(100), default="input", nullable=False)
    team_data: Mapped[dict[str, object] | None] = mapped_column(
        JSONB, nullable=True, default=None
    )
    challenge_data: Mapped[dict[str, object] | None] = mapped_column(
        JSONB, nullable=True, default=None
    )
    resource_data: Mapped[dict[str, object] | None] = mapped_column(
        JSONB, nullable=True, default=None
    )
    state: Mapped[dict[str, object] | None] = mapped_column(
        JSONB, nullable=True, default=None
    )
    completed_agents: Mapped[list[str] | None] = mapped_column(
        JSONB, nullable=True, default=list
    )
    current_agent: Mapped[str | None] = mapped_column(
        String(100), nullable=True, default=None
    )
    agent_logs: Mapped[list[dict[str, Any]] | None] = mapped_column(
        JSONB, nullable=True, default=list
    )
    error_log: Mapped[list[dict[str, str]] | None] = mapped_column(
        JSONB, nullable=True, default=list
    )
    duration_hours: Mapped[int] = mapped_column(Integer, default=24, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name={self.name}, status={self.status})>"
