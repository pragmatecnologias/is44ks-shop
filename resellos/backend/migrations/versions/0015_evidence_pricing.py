"""add marketplace evidence pricing fields

Revision ID: 0015_evidence_pricing
Revises: 0014_supplier_economics
Create Date: 2026-05-07
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "0015_evidence_pricing"
down_revision = "0014_supplier_economics"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("marketplace_evidence", sa.Column("price_currency", sa.String(10), nullable=True))
    op.add_column("marketplace_evidence", sa.Column("price_quantity_basis", sa.Text, nullable=True))
    op.add_column("marketplace_evidence", sa.Column("price_total_price", sa.Numeric(10, 2), nullable=True))
    op.add_column("marketplace_evidence", sa.Column("price_proof_text", sa.Text, nullable=True))
    op.add_column("marketplace_evidence", sa.Column("price_manual_verification_note", sa.Text, nullable=True))
    op.add_column("marketplace_evidence", sa.Column("price_proof_screenshot_path", sa.Text, nullable=True))
    op.add_column("marketplace_evidence", sa.Column("price_verified", sa.Boolean, nullable=True))
    op.add_column("marketplace_evidence", sa.Column("price_verified_at", sa.DateTime, nullable=True))
    op.add_column("marketplace_evidence", sa.Column("price_verified_by_source", sa.String(50), nullable=True))
    op.add_column("marketplace_evidence", sa.Column("price_confidence_level", sa.String(20), nullable=True))


def downgrade() -> None:
    op.drop_column("marketplace_evidence", "price_confidence_level")
    op.drop_column("marketplace_evidence", "price_verified_by_source")
    op.drop_column("marketplace_evidence", "price_verified_at")
    op.drop_column("marketplace_evidence", "price_verified")
    op.drop_column("marketplace_evidence", "price_proof_screenshot_path")
    op.drop_column("marketplace_evidence", "price_manual_verification_note")
    op.drop_column("marketplace_evidence", "price_proof_text")
    op.drop_column("marketplace_evidence", "price_total_price")
    op.drop_column("marketplace_evidence", "price_quantity_basis")
    op.drop_column("marketplace_evidence", "price_currency")