"""add opportunity scout fields to discovery ideas

Revision ID: 0017_opportunity_scout
Revises: 0016_price_estimate_guardrail
Create Date: 2026-05-07
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "0017_opportunity_scout"
down_revision = "0016_price_estimate_guardrail"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("product_discovery_ideas", sa.Column("scout_status", sa.String(length=50), nullable=True))
    op.add_column("product_discovery_ideas", sa.Column("scout_score", sa.Integer(), nullable=True))
    op.add_column("product_discovery_ideas", sa.Column("scout_confidence", sa.String(length=20), nullable=True))
    op.add_column("product_discovery_ideas", sa.Column("scout_reason", sa.Text(), nullable=True))
    op.add_column("product_discovery_ideas", sa.Column("scout_next_step", sa.Text(), nullable=True))
    op.add_column("product_discovery_ideas", sa.Column("scout_metrics_json", sa.Text(), nullable=True))
    op.add_column("product_discovery_ideas", sa.Column("scout_updated_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("product_discovery_ideas", "scout_updated_at")
    op.drop_column("product_discovery_ideas", "scout_metrics_json")
    op.drop_column("product_discovery_ideas", "scout_next_step")
    op.drop_column("product_discovery_ideas", "scout_reason")
    op.drop_column("product_discovery_ideas", "scout_confidence")
    op.drop_column("product_discovery_ideas", "scout_score")
    op.drop_column("product_discovery_ideas", "scout_status")
