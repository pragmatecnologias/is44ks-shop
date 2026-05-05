"""vision analysis reports

Revision ID: 0004_vision_analysis_reports
Revises: 0003_discovery_task_links
Create Date: 2026-05-05
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision = "0004_vision_analysis_reports"
down_revision = "0003_discovery_task_links"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "vision_analysis_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=True),
        sa.Column("idea_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("product_discovery_ideas.id"), nullable=True),
        sa.Column("file_url", sa.Text(), nullable=True),
        sa.Column("analysis_type", sa.String(length=100), nullable=False),
        sa.Column("provider", sa.String(length=100), nullable=False),
        sa.Column("model", sa.String(length=100), nullable=False),
        sa.Column("input_metadata", sa.Text(), nullable=True),
        sa.Column("output_json", sa.Text(), nullable=True),
        sa.Column("confidence", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("vision_analysis_reports")
