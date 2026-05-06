"""add result_count_raw and candidate_count to external_research_jobs

Revision ID: 0009_external_research_counts
Revises: 0008_discovery_campaigns
Create Date: 2026-05-06
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "0009_external_research_counts"
down_revision = "0008_discovery_campaigns"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("external_research_jobs", sa.Column("result_count_raw", sa.Integer(), nullable=True, server_default="0"))
    op.add_column("external_research_jobs", sa.Column("candidate_count", sa.Integer(), nullable=True, server_default="0"))


def downgrade() -> None:
    op.drop_column("external_research_jobs", "candidate_count")
    op.drop_column("external_research_jobs", "result_count_raw")
