"""discovery queue

Revision ID: 0002_discovery
Revises: 0001_initial
Create Date: 2026-05-05
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision = "0002_discovery"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "product_discovery_ideas",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("idea_name", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=120), nullable=True),
        sa.Column("source_platform", sa.String(length=100), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("rough_supplier_cost", sa.Numeric(10, 2), nullable=True),
        sa.Column("estimated_landed_cost", sa.Numeric(10, 2), nullable=True),
        sa.Column("why_interesting", sa.Text(), nullable=True),
        sa.Column("risk_flags", sa.Text(), nullable=True),
        sa.Column("quick_market_signal", sa.Text(), nullable=True),
        sa.Column("quick_profit_signal", sa.Text(), nullable=True),
        sa.Column("research_priority", sa.String(length=50), nullable=True, server_default="MEDIUM"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=True, server_default="IDEA"),
        sa.Column("quick_scan_verdict", sa.String(length=50), nullable=True),
        sa.Column("quick_scan_reason", sa.Text(), nullable=True),
        sa.Column("suggested_keywords", sa.Text(), nullable=True),
        sa.Column("required_next_evidence", sa.Text(), nullable=True),
        sa.Column("promoted_product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "discovery_tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("idea_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("product_discovery_ideas.id"), nullable=False),
        sa.Column("task_type", sa.String(length=80), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=True, server_default="TODO"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("discovery_tasks")
    op.drop_table("product_discovery_ideas")
