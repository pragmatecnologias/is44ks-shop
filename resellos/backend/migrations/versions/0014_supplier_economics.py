"""add supplier economics fields

Revision ID: 0014_supplier_economics
Revises: 0013_evidence_provenance
Create Date: 2026-05-07
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "0014_supplier_economics"
down_revision = "0013_evidence_provenance"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("product_sources", sa.Column("currency", sa.String(10), nullable=True))
    op.add_column("product_sources", sa.Column("quantity_basis", sa.Text, nullable=True))
    op.add_column("product_sources", sa.Column("proof_text", sa.Text, nullable=True))
    op.add_column("product_sources", sa.Column("manual_verification_note", sa.Text, nullable=True))
    op.add_column("product_sources", sa.Column("confidence_level", sa.String(20), nullable=True))
    op.add_column("product_sources", sa.Column("economics_verified", sa.Boolean, nullable=True))
    op.execute("UPDATE product_sources SET economics_verified = FALSE WHERE economics_verified IS NULL")
    op.alter_column("product_sources", "economics_verified", nullable=False, server_default=False)
    op.add_column("product_sources", sa.Column("verified_at", sa.DateTime, nullable=True))
    op.add_column("product_sources", sa.Column("verified_by_source", sa.String(50), nullable=True))


def downgrade() -> None:
    op.drop_column("product_sources", "verified_by_source")
    op.drop_column("product_sources", "verified_at")
    op.drop_column("product_sources", "economics_verified")
    op.drop_column("product_sources", "confidence_level")
    op.drop_column("product_sources", "manual_verification_note")
    op.drop_column("product_sources", "proof_text")
    op.drop_column("product_sources", "quantity_basis")
    op.drop_column("product_sources", "currency")