"""Shared Intelligence models — the shared context layer for all specialists.

Bible §7: Shared Intelligence Model
  - Shared Project Memory (§7.4)
  - Decision Journal (§7.5)
  - Specialist References (§7.6)
  - Confidence Tracking (§7.7)
  - Review Workflow (§7.8)
"""

import datetime
import uuid
from sqlalchemy import Column, String, DateTime, Float, Text, JSON, Integer, Boolean
from app.models.base import Base


class SharedMemory(Base):
    """Structured project memory — outputs from every specialist (Bible §7.4).

    Append-oriented: new entries are added, existing ones are never modified.
    Specialists read the latest entry for their category by created_at DESC.
    """
    __tablename__ = "shared_memory"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, nullable=False, index=True)

    # Which specialist produced this
    specialist = Column(String, nullable=False, index=True)  # e.g. "challenge_analyst", "research_specialist"
    memory_type = Column(String, nullable=False, index=True)  # e.g. "challenge_intelligence", "research_report"

    # Version tracking (append-only, version increments per write)
    version = Column(Integer, nullable=False, default=1)

    # Structured content — the specialist's output, always typed
    content = Column(JSON, nullable=False)

    # Confidence from the originating specialist
    confidence = Column(Float, nullable=True, default=0.0)

    # References to other memory entries that this entry depends on (Bible §7.6)
    references = Column(JSON, nullable=True)  # list of memory IDs

    # Attribution
    model_used = Column(String, nullable=True)
    token_count = Column(Integer, nullable=True)

    # Metadata
    is_active = Column(Boolean, default=True, nullable=False)  # Soft-invalidation for review overrides
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class DecisionJournal(Base):
    """Immutable, append-only record of every significant product decision (Bible §7.5).

    Never rewritten. Never deleted. New entries supersede old ones.
    """
    __tablename__ = "decision_journal"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, nullable=False, index=True)

    # Sequential entry number within the project (for display/reference)
    entry_number = Column(Integer, nullable=False)

    # Human-readable title
    title = Column(String, nullable=False)

    # Category classification
    category = Column(String, nullable=False, index=True)
    # Categories: opportunity_selected, direction_rejected, tech_chosen,
    #            architecture_tradeoff, research_finding, risk_accepted,
    #            feature_scoped, specialist_review, direction_generated

    # The decision itself
    description = Column(Text, nullable=False)
    rationale = Column(Text, nullable=True)
    alternatives_considered = Column(JSON, nullable=True)

    # Confidence and attribution
    confidence = Column(Float, nullable=True)
    originating_specialist = Column(String, nullable=False)

    # References to shared_memory entries that informed this decision
    references = Column(JSON, nullable=True)  # list of memory IDs

    # Status — decisions are immutable but their status can be updated
    # (this is the ONE mutable field, for review workflows)
    status = Column(String, nullable=False, default="accepted")
    # Statuses: proposed, accepted, rejected, superseded, needs_review

    # When this decision was superseded (if status = superseded)
    superseded_by = Column(String, nullable=True)  # decision ID

    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)


class ReviewRecord(Base):
    """Review workflow infrastructure — for future Critic/Fact Checker specialists (Bible §7.8).

    Prepared but not wired into any specialist yet.
    """
    __tablename__ = "review_records"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, nullable=False, index=True)

    # Target of the review — a memory entry or decision
    target_type = Column(String, nullable=False)  # "memory" or "decision"
    target_id = Column(String, nullable=False)

    # Reviewer
    reviewer_specialist = Column(String, nullable=False)

    # Review outcome
    status = Column(String, nullable=False, default="pending")
    # Statuses: pending, approved, rejected, needs_revision

    # Findings
    findings = Column(JSON, nullable=True)
    confidence_adjustment = Column(Float, nullable=True)  # How much to adjust the original confidence
    rationale = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
