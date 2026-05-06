"""add evidence verification status

Revision ID: 0007_evidence_verification
Revises: 0006_model_drift_fixes
Create Date: 2026-05-05
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "0007_evidence_verification"
down_revision = "0006_model_drift_fixes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add verification_status column to all three evidence tables
    op.add_column("marketplace_evidence", sa.Column("verification_status", sa.String(50), nullable=True))
    op.add_column("competitor_listings", sa.Column("verification_status", sa.String(50), nullable=True))
    op.add_column("product_sources", sa.Column("verification_status", sa.String(50), nullable=True))

    # Classify existing marketplace_evidence rows
    op.execute("""
        UPDATE marketplace_evidence
        SET verification_status = 'API_IMPORTED'
        WHERE source_method = 'DATAFORSEO'
    """)
    op.execute("""
        UPDATE marketplace_evidence
        SET verification_status = 'USER_CAPTURED_UNVERIFIED'
        WHERE source_method IN ('MANUAL_CAPTURE', 'VISION')
          AND verification_status IS NULL
    """)
    op.execute("""
        UPDATE marketplace_evidence
        SET verification_status = 'TEST_DATA'
        WHERE verification_status IS NULL
          AND created_at >= NOW() - INTERVAL '48 hours'
    """)
    op.execute("""
        UPDATE marketplace_evidence
        SET verification_status = 'AI_EXTRACTED_UNVERIFIED'
        WHERE verification_status IS NULL
    """)

    # Classify existing competitor_listings rows (no source_method column, use created_at heuristic)
    op.execute("""
        UPDATE competitor_listings
        SET verification_status = 'TEST_DATA'
        WHERE created_at >= NOW() - INTERVAL '48 hours'
    """)
    op.execute("""
        UPDATE competitor_listings
        SET verification_status = 'AI_EXTRACTED_UNVERIFIED'
        WHERE verification_status IS NULL
    """)

    # Classify existing product_sources rows
    op.execute("""
        UPDATE product_sources
        SET verification_status = 'TEST_DATA'
        WHERE created_at >= NOW() - INTERVAL '48 hours'
    """)
    op.execute("""
        UPDATE product_sources
        SET verification_status = 'AI_EXTRACTED_UNVERIFIED'
        WHERE verification_status IS NULL
    """)


def downgrade() -> None:
    op.drop_column("product_sources", "verification_status")
    op.drop_column("competitor_listings", "verification_status")
    op.drop_column("marketplace_evidence", "verification_status")
