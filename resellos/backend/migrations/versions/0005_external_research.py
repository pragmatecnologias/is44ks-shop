"""external research jobs and evidence candidates

Revision ID: 0005_external_research
Revises: 0004_vision_analysis_reports
Create Date: 2026-05-05
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision = "0005_external_research"
down_revision = "0004_vision_analysis_reports"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "external_research_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("idea_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("product_discovery_ideas.id"), nullable=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=True),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("api_area", sa.String(length=100), nullable=False),
        sa.Column("query", sa.String(length=500), nullable=False),
        sa.Column("queue", sa.String(length=50), nullable=True, server_default="standard"),
        sa.Column("status", sa.String(length=30), nullable=True, server_default="QUEUED"),
        sa.Column("provider_task_id", sa.String(length=120), nullable=True),
        sa.Column("cost_estimate", sa.Numeric(10, 4), nullable=True),
        sa.Column("result_count", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("raw_request", sa.JSON(), nullable=True),
        sa.Column("raw_response", sa.JSON(), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "evidence_candidates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("external_research_jobs.id"), nullable=True),
        sa.Column("idea_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("product_discovery_ideas.id"), nullable=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=True),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("candidate_type", sa.String(length=50), nullable=False),
        sa.Column("marketplace", sa.String(length=120), nullable=True),
        sa.Column("evidence_type", sa.String(length=50), nullable=True),
        sa.Column("title", sa.String(length=500), nullable=True),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("price", sa.Numeric(10, 2), nullable=True),
        sa.Column("shipping_price", sa.Numeric(10, 2), nullable=True),
        sa.Column("seller", sa.String(length=200), nullable=True),
        sa.Column("rating", sa.Numeric(5, 2), nullable=True),
        sa.Column("review_count", sa.Integer(), nullable=True),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("confidence", sa.String(length=50), nullable=True, server_default="MEDIUM"),
        sa.Column("review_status", sa.String(length=30), nullable=True, server_default="PENDING"),
        sa.Column("raw_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("evidence_candidates")
    op.drop_table("external_research_jobs")

