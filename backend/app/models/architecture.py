"""Architecture Blueprint model — complete technical specification (Bible §6.2 S7)."""

import datetime
import uuid
from sqlalchemy import Column, String, DateTime, Float, Text, JSON
from app.models.base import Base


class ArchitectureBlueprint(Base):
    """Complete technical architecture for a project (Bible §6.2 S7).

    Stores the full output of the Solution Architect specialist.
    Every downstream engineering specialist depends on this.
    """
    __tablename__ = "architecture_blueprints"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, nullable=False, unique=True, index=True)

    # System overview
    system_overview = Column(Text, nullable=True)
    architecture_rationale = Column(Text, nullable=True)

    # Components
    components = Column(JSON, nullable=True)  # list[{name, description, tech, purpose}]

    # Mermaid diagrams
    mermaid_system = Column(Text, nullable=True)
    mermaid_request_flow = Column(Text, nullable=True)
    mermaid_data_flow = Column(Text, nullable=True)
    mermaid_deployment = Column(Text, nullable=True)

    # Frontend architecture
    frontend_framework = Column(String, nullable=True)
    frontend_folders = Column(JSON, nullable=True)
    frontend_component_hierarchy = Column(JSON, nullable=True)
    frontend_state = Column(Text, nullable=True)
    frontend_routing = Column(JSON, nullable=True)

    # Backend architecture
    backend_framework = Column(String, nullable=True)
    backend_modules = Column(JSON, nullable=True)
    backend_api_organization = Column(JSON, nullable=True)

    # Database
    database_entities = Column(JSON, nullable=True)
    database_relationships = Column(JSON, nullable=True)
    mermaid_er = Column(Text, nullable=True)
    database_notes = Column(Text, nullable=True)

    # API Contracts
    api_contracts = Column(JSON, nullable=True)

    # Authentication
    auth_provider = Column(String, nullable=True)
    auth_model = Column(Text, nullable=True)

    # External services
    external_services = Column(JSON, nullable=True)

    # Scalability
    hackathon_version = Column(Text, nullable=True)
    production_version = Column(Text, nullable=True)
    migration_path = Column(Text, nullable=True)

    # Trade-offs
    tradeoffs = Column(JSON, nullable=True)

    # Architecture review
    weak_points = Column(JSON, nullable=True)
    failure_modes = Column(JSON, nullable=True)

    # Metadata
    model_used = Column(String, nullable=True)
    confidence = Column(Float, nullable=True, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
