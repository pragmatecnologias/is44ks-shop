"""add production capability discovery tables

Revision ID: 0018_production_capability
Revises: 0017_opportunity_scout
Create Date: 2026-05-08
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0018_production_capability"
down_revision = "0017_opportunity_scout"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "production_campaigns",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(300), nullable=False),
        sa.Column("shop_concept_id", sa.String(36), nullable=True),
        sa.Column("mode", sa.String(30), server_default="PRODUCTION", nullable=False),
        sa.Column("goal", sa.Text, nullable=True),
        sa.Column("workspace_type", sa.String(100), nullable=True),
        sa.Column("workspace_dimensions_json", sa.JSON, nullable=True),
        sa.Column("power_constraints_json", sa.JSON, nullable=True),
        sa.Column("safety_requirements_json", sa.JSON, nullable=True),
        sa.Column("budget_limit_usd", sa.Numeric(10, 2), nullable=True),
        sa.Column("status", sa.String(30), server_default="DRAFT", nullable=False),
        sa.Column("created_by", sa.String(120), nullable=True),
        sa.Column("latest_report_json", sa.JSON, nullable=True),
        sa.Column("report_generated_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "production_capabilities",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("campaign_id", sa.String(36), sa.ForeignKey("production_campaigns.id"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("materials", sa.JSON, nullable=True),
        sa.Column("typical_products", sa.JSON, nullable=True),
        sa.Column("entry_cost_range_json", sa.JSON, nullable=True),
        sa.Column("skill_level", sa.String(30), nullable=True),
        sa.Column("workspace_footprint", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "machine_candidates",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("campaign_id", sa.String(36), sa.ForeignKey("production_campaigns.id"), nullable=False),
        sa.Column("name", sa.String(300), nullable=False),
        sa.Column("brand", sa.String(200), nullable=True),
        sa.Column("model", sa.String(200), nullable=True),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("url", sa.Text, nullable=True),
        sa.Column("price_new", sa.Numeric(10, 2), nullable=True),
        sa.Column("price_used_range_json", sa.JSON, nullable=True),
        sa.Column("condition", sa.String(50), nullable=True),
        sa.Column("power_requirements", sa.String(100), nullable=True),
        sa.Column("workspace_needed", sa.String(100), nullable=True),
        sa.Column("safety_notes", sa.Text, nullable=True),
        sa.Column("status", sa.String(50), server_default="SUGGESTED", nullable=False),
        sa.Column("decision_recommendation", sa.String(50), nullable=True),
        sa.Column("decision_reason", sa.Text, nullable=True),
        sa.Column("decided_at", sa.DateTime, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "machine_capabilities",
        sa.Column("machine_id", sa.String(36), sa.ForeignKey("machine_candidates.id"), primary_key=True),
        sa.Column("capability_id", sa.String(36), sa.ForeignKey("production_capabilities.id"), primary_key=True),
    )

    op.create_table(
        "machine_evidence",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("machine_id", sa.String(36), sa.ForeignKey("machine_candidates.id"), nullable=False),
        sa.Column("evidence_type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(500), nullable=True),
        sa.Column("url", sa.Text, nullable=True),
        sa.Column("price", sa.Numeric(10, 2), nullable=True),
        sa.Column("source", sa.String(100), nullable=True),
        sa.Column("seller", sa.String(200), nullable=True),
        sa.Column("condition", sa.String(50), nullable=True),
        sa.Column("specs_json", sa.JSON, nullable=True),
        sa.Column("pros", sa.Text, nullable=True),
        sa.Column("cons", sa.Text, nullable=True),
        sa.Column("verification_status", sa.String(50), server_default="PENDING"),
        sa.Column("confidence", sa.String(20), server_default="MEDIUM"),
        sa.Column("raw_text", sa.Text, nullable=True),
        sa.Column("screenshot_url", sa.Text, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "machine_product_families",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("machine_id", sa.String(36), sa.ForeignKey("machine_candidates.id"), nullable=False),
        sa.Column("name", sa.String(300), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("material_cost_per_unit", sa.Numeric(10, 2), nullable=True),
        sa.Column("estimated_sale_price", sa.Numeric(10, 2), nullable=True),
        sa.Column("estimated_demand", sa.String(30), nullable=True),
        sa.Column("market_evidence_summary", sa.Text, nullable=True),
        sa.Column("market_evidence_count", sa.Integer, server_default="0"),
        sa.Column("has_market_evidence", sa.Boolean, server_default="0"),
        sa.Column("status", sa.String(50), server_default="SUGGESTED", nullable=False),
        sa.Column("promoted_product_id", sa.String(36), nullable=True),
        sa.Column("promoted_idea_id", sa.String(36), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "production_cost_scenarios",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("machine_id", sa.String(36), sa.ForeignKey("machine_candidates.id"), nullable=False),
        sa.Column("product_family_id", sa.String(36), sa.ForeignKey("machine_product_families.id"), nullable=True),
        sa.Column("scenario_name", sa.String(200), nullable=False),
        sa.Column("material_cost", sa.Numeric(10, 2), nullable=True),
        sa.Column("labor_cost", sa.Numeric(10, 2), nullable=True),
        sa.Column("machine_time_cost", sa.Numeric(10, 2), nullable=True),
        sa.Column("consumables_cost", sa.Numeric(10, 2), nullable=True),
        sa.Column("marketplace_fee", sa.Numeric(10, 2), nullable=True),
        sa.Column("shipping_cost", sa.Numeric(10, 2), nullable=True),
        sa.Column("packaging_cost", sa.Numeric(10, 2), nullable=True),
        sa.Column("other_costs", sa.Numeric(10, 2), nullable=True),
        sa.Column("total_cost_per_unit", sa.Numeric(10, 2), nullable=True),
        sa.Column("sale_price", sa.Numeric(10, 2), nullable=True),
        sa.Column("net_profit_per_unit", sa.Numeric(10, 2), nullable=True),
        sa.Column("margin_percent", sa.Numeric(8, 2), nullable=True),
        sa.Column("machine_purchase_price", sa.Numeric(10, 2), nullable=True),
        sa.Column("units_per_month", sa.Integer, nullable=True),
        sa.Column("monthly_profit", sa.Numeric(10, 2), nullable=True),
        sa.Column("payback_months", sa.Numeric(8, 1), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "machine_decisions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("machine_id", sa.String(36), sa.ForeignKey("machine_candidates.id"), nullable=False, unique=True),
        sa.Column("recommendation", sa.String(50), nullable=False),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column("confidence", sa.String(20), server_default="MEDIUM"),
        sa.Column("evidence_count", sa.Integer, server_default="0"),
        sa.Column("product_family_count", sa.Integer, server_default="0"),
        sa.Column("families_with_market_evidence", sa.Integer, server_default="0"),
        sa.Column("has_cost_scenario", sa.Boolean, server_default="0"),
        sa.Column("payback_calculated", sa.Boolean, server_default="0"),
        sa.Column("workspace_fit", sa.String(20), nullable=True),
        sa.Column("safety_fit", sa.String(20), nullable=True),
        sa.Column("budget_fit", sa.String(20), nullable=True),
        sa.Column("hard_blockers_json", sa.JSON, nullable=True),
        sa.Column("warnings_json", sa.JSON, nullable=True),
        sa.Column("agent_output_json", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("machine_decisions")
    op.drop_table("production_cost_scenarios")
    op.drop_table("machine_product_families")
    op.drop_table("machine_evidence")
    op.drop_table("machine_capabilities")
    op.drop_table("machine_candidates")
    op.drop_table("production_capabilities")
    op.drop_table("production_campaigns")
