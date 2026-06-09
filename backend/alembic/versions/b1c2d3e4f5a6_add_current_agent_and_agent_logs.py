"""add current_agent and agent_logs to projects

Revision ID: b1c2d3e4f5a6
Revises: 40bc39e8570f
Create Date: 2026-06-08 12:00:00.000000
"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = 'b1c2d3e4f5a6'
down_revision: str | None = '40bc39e8570f'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        'projects',
        sa.Column('current_agent', sa.String(length=100), nullable=True),
    )
    op.add_column(
        'projects',
        sa.Column(
            'agent_logs',
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column('projects', 'agent_logs')
    op.drop_column('projects', 'current_agent')
