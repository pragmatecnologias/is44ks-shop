"""model-migration drift fixes

Revision ID: 0006_model_drift_fixes
Revises: 0005_external_research
Create Date: 2026-05-05
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "0006_model_drift_fixes"
down_revision = "0005_external_research"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("profit_analyses", sa.Column("return_allowance", sa.Numeric(10, 2), nullable=True))
    op.add_column("profit_analyses", sa.Column("ad_cost", sa.Numeric(10, 2), nullable=True))
    op.add_column("external_research_jobs", sa.Column("updated_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("external_research_jobs", "updated_at")
    op.drop_column("profit_analyses", "ad_cost")
    op.drop_column("profit_analyses", "return_allowance")
