"""add validation research tables

Revision ID: 0010_validation_expansion
Revises: 0009_external_research_counts
Create Date: 2026-05-06
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "0010_validation_expansion"
down_revision = "0009_external_research_counts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "product_demand_research",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("product_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=True),
        sa.Column("idea_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("product_discovery_ideas.id"), nullable=True),
        sa.Column("campaign_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("discovery_campaigns.id"), nullable=True),
        sa.Column("task_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("discovery_campaign_tasks.id"), nullable=True),
        sa.Column("keyword", sa.String(length=500), nullable=False),
        sa.Column("source", sa.String(length=80), nullable=False, server_default="MANUAL_CAPTURE"),
        sa.Column("target_country", sa.String(length=8), nullable=False, server_default="US"),
        sa.Column("target_language", sa.String(length=8), nullable=False, server_default="en"),
        sa.Column("monthly_search_volume", sa.Integer(), nullable=True),
        sa.Column("monthly_search_volume_min", sa.Integer(), nullable=True),
        sa.Column("monthly_search_volume_max", sa.Integer(), nullable=True),
        sa.Column("competition_level", sa.String(length=30), nullable=True),
        sa.Column("cpc_low", sa.Numeric(10, 2), nullable=True),
        sa.Column("cpc_high", sa.Numeric(10, 2), nullable=True),
        sa.Column("currency", sa.String(length=8), nullable=False, server_default="USD"),
        sa.Column("buyer_intent_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("keyword_specificity_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("demand_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("related_keywords_json", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column("raw_json", sa.JSON(), nullable=True),
        sa.Column("verification_status", sa.String(length=50), nullable=False, server_default="USER_CAPTURED_UNVERIFIED"),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("screenshot_url", sa.Text(), nullable=True),
        sa.Column("verification_notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_product_demand_research_product_id", "product_demand_research", ["product_id"])
    op.create_index("ix_product_demand_research_idea_id", "product_demand_research", ["idea_id"])
    op.create_index("ix_product_demand_research_campaign_id", "product_demand_research", ["campaign_id"])
    op.create_index("ix_product_demand_research_task_id", "product_demand_research", ["task_id"])

    op.create_table(
        "product_trend_research",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("product_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=True),
        sa.Column("idea_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("product_discovery_ideas.id"), nullable=True),
        sa.Column("campaign_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("discovery_campaigns.id"), nullable=True),
        sa.Column("task_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("discovery_campaign_tasks.id"), nullable=True),
        sa.Column("keyword", sa.String(length=500), nullable=False),
        sa.Column("source", sa.String(length=80), nullable=False, server_default="MANUAL_CAPTURE"),
        sa.Column("geo", sa.String(length=12), nullable=False, server_default="US"),
        sa.Column("timeframe", sa.String(length=80), nullable=False, server_default="past_5_years"),
        sa.Column("trend_direction", sa.String(length=30), nullable=True),
        sa.Column("seasonality_risk", sa.String(length=30), nullable=True),
        sa.Column("evergreen_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("trend_stability_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("spike_risk_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("average_interest", sa.Numeric(10, 2), nullable=True),
        sa.Column("peak_interest", sa.Numeric(10, 2), nullable=True),
        sa.Column("low_interest", sa.Numeric(10, 2), nullable=True),
        sa.Column("trend_points_json", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column("raw_json", sa.JSON(), nullable=True),
        sa.Column("verification_status", sa.String(length=50), nullable=False, server_default="USER_CAPTURED_UNVERIFIED"),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("screenshot_url", sa.Text(), nullable=True),
        sa.Column("verification_notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_product_trend_research_product_id", "product_trend_research", ["product_id"])
    op.create_index("ix_product_trend_research_idea_id", "product_trend_research", ["idea_id"])
    op.create_index("ix_product_trend_research_campaign_id", "product_trend_research", ["campaign_id"])
    op.create_index("ix_product_trend_research_task_id", "product_trend_research", ["task_id"])

    op.create_table(
        "product_validation_summaries",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("product_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=False, unique=True),
        sa.Column("market_presence_status", sa.String(length=30), nullable=True),
        sa.Column("search_demand_status", sa.String(length=30), nullable=True),
        sa.Column("sold_demand_status", sa.String(length=30), nullable=True),
        sa.Column("trend_status", sa.String(length=30), nullable=True),
        sa.Column("supplier_economics_status", sa.String(length=30), nullable=True),
        sa.Column("competition_status", sa.String(length=30), nullable=True),
        sa.Column("risk_status", sa.String(length=30), nullable=True),
        sa.Column("market_presence_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("search_demand_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("sold_demand_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("trend_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("supplier_economics_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("competition_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("risk_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("overall_validation_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("validation_readiness", sa.String(length=40), nullable=False, server_default="INCOMPLETE"),
        sa.Column("main_validation_blocker", sa.Text(), nullable=True),
        sa.Column("next_validation_action", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("product_validation_summaries")
    op.drop_index("ix_product_trend_research_campaign_id", table_name="product_trend_research")
    op.drop_index("ix_product_trend_research_idea_id", table_name="product_trend_research")
    op.drop_index("ix_product_trend_research_product_id", table_name="product_trend_research")
    op.drop_index("ix_product_trend_research_task_id", table_name="product_trend_research")
    op.drop_table("product_trend_research")
    op.drop_index("ix_product_demand_research_campaign_id", table_name="product_demand_research")
    op.drop_index("ix_product_demand_research_idea_id", table_name="product_demand_research")
    op.drop_index("ix_product_demand_research_product_id", table_name="product_demand_research")
    op.drop_index("ix_product_demand_research_task_id", table_name="product_demand_research")
    op.drop_table("product_demand_research")
