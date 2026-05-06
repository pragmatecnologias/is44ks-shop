"""add discovery campaigns

Revision ID: 0008_discovery_campaigns
Revises: 0007_evidence_verification
Create Date: 2026-05-06
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "0008_discovery_campaigns"
down_revision = "0007_evidence_verification"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "discovery_campaigns",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=300), nullable=False),
        sa.Column("category", sa.String(length=120), nullable=True),
        sa.Column("goal", sa.Text(), nullable=True),
        sa.Column("constraints_json", sa.JSON(), nullable=True),
        sa.Column("budget_limit_usd", sa.Numeric(10, 2), nullable=True),
        sa.Column("max_ideas", sa.Integer(), nullable=True),
        sa.Column("max_products_to_promote", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="DRAFT"),
        sa.Column("created_by", sa.String(length=120), nullable=True),
        sa.Column("latest_report_json", sa.JSON(), nullable=True),
        sa.Column("report_generated_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "discovery_campaign_tasks",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("campaign_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("discovery_campaigns.id"), nullable=False),
        sa.Column("task_type", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="TODO"),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("related_idea_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("product_discovery_ideas.id"), nullable=True),
        sa.Column("related_product_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=True),
        sa.Column("related_candidate_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("evidence_candidates.id"), nullable=True),
        sa.Column("result_json", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    op.add_column("product_discovery_ideas", sa.Column("campaign_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("discovery_campaigns.id"), nullable=True))
    op.add_column("external_research_jobs", sa.Column("campaign_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("discovery_campaigns.id"), nullable=True))
    op.add_column("evidence_candidates", sa.Column("campaign_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("discovery_campaigns.id"), nullable=True))


def downgrade() -> None:
    op.drop_column("evidence_candidates", "campaign_id")
    op.drop_column("external_research_jobs", "campaign_id")
    op.drop_column("product_discovery_ideas", "campaign_id")
    op.drop_table("discovery_campaign_tasks")
    op.drop_table("discovery_campaigns")
