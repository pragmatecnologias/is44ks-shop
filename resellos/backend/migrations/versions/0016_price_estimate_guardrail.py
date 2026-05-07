"""add estimated market price fields and downgrade derived sold prices

Revision ID: 0016_price_estimate_guardrail
Revises: 0015_evidence_pricing
Create Date: 2026-05-07
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "0016_price_estimate_guardrail"
down_revision = "0015_evidence_pricing"
branch_labels = None
depends_on = None


DOOR_HINGE_PRODUCT_ID = "ee638c1a-8ad3-4a91-a506-80cff34a1f7c"
ESTIMATE_NOTE = "Price estimate derived from active-market comparable, not actual completed-sale proof."


def upgrade() -> None:
    op.add_column("marketplace_evidence", sa.Column("estimated_market_price", sa.Numeric(10, 2), nullable=True))
    op.add_column("marketplace_evidence", sa.Column("price_estimation_method", sa.String(50), nullable=True))

    connection = op.get_bind()
    connection.execute(
        sa.text(
            """
            UPDATE marketplace_evidence
            SET estimated_market_price = COALESCE(price_total_price, price),
                price_estimation_method = 'ACTIVE_MARKET_COMPARABLE',
                price_verified = FALSE,
                price_verified_at = NULL,
                price_verified_by_source = NULL,
                price_confidence_level = CASE
                    WHEN price_confidence_level IS NULL OR TRIM(price_confidence_level) = '' THEN 'LOW'
                    ELSE price_confidence_level
                END,
                price_manual_verification_note = CASE
                    WHEN price_manual_verification_note IS NULL OR TRIM(price_manual_verification_note) = '' THEN :estimate_note
                    WHEN LOWER(price_manual_verification_note) LIKE '%' || LOWER(:estimate_note) || '%' THEN price_manual_verification_note
                    ELSE price_manual_verification_note || ' ' || :estimate_note
                END,
                notes = CASE
                    WHEN notes IS NULL OR TRIM(notes) = '' THEN :estimate_note
                    WHEN LOWER(notes) LIKE '%' || LOWER(:estimate_note) || '%' THEN notes
                    ELSE notes || ' ' || :estimate_note
                END
            WHERE product_id = :product_id
              AND evidence_type = 'SOLD_LISTING'
              AND price_verified IS TRUE
              AND (
                    lower(COALESCE(price_proof_text, '')) LIKE '%active-market%'
                 OR lower(COALESCE(price_manual_verification_note, '')) LIKE '%active-market%'
                 OR lower(COALESCE(notes, '')) LIKE '%active-market%'
                 OR lower(COALESCE(price_proof_text, '')) LIKE '%active market%'
                 OR lower(COALESCE(price_manual_verification_note, '')) LIKE '%active market%'
                 OR lower(COALESCE(notes, '')) LIKE '%active market%'
                 OR lower(COALESCE(price_proof_text, '')) LIKE '%comparable%'
                 OR lower(COALESCE(price_manual_verification_note, '')) LIKE '%comparable%'
                 OR lower(COALESCE(notes, '')) LIKE '%comparable%'
                 OR lower(COALESCE(price_proof_text, '')) LIKE '%estimate%'
                 OR lower(COALESCE(price_manual_verification_note, '')) LIKE '%estimate%'
                 OR lower(COALESCE(notes, '')) LIKE '%estimate%'
                 OR lower(COALESCE(price_proof_text, '')) LIKE '%same product%'
                 OR lower(COALESCE(price_manual_verification_note, '')) LIKE '%same product%'
                 OR lower(COALESCE(notes, '')) LIKE '%same product%'
                 OR lower(COALESCE(price_proof_text, '')) LIKE '%same product category%'
                 OR lower(COALESCE(price_manual_verification_note, '')) LIKE '%same product category%'
                 OR lower(COALESCE(notes, '')) LIKE '%same product category%'
                 OR lower(COALESCE(price_proof_text, '')) LIKE '%based on market active prices%'
                 OR lower(COALESCE(price_manual_verification_note, '')) LIKE '%based on market active prices%'
                 OR lower(COALESCE(notes, '')) LIKE '%based on market active prices%'
                 OR lower(COALESCE(price_proof_text, '')) LIKE '%based on active market%'
                 OR lower(COALESCE(price_manual_verification_note, '')) LIKE '%based on active market%'
                 OR lower(COALESCE(notes, '')) LIKE '%based on active market%'
                 OR lower(COALESCE(price_proof_text, '')) LIKE '%verified active%'
                 OR lower(COALESCE(price_manual_verification_note, '')) LIKE '%verified active%'
                 OR lower(COALESCE(notes, '')) LIKE '%verified active%'
              )
            """
        ),
        {"product_id": DOOR_HINGE_PRODUCT_ID, "estimate_note": ESTIMATE_NOTE},
    )


def downgrade() -> None:
    op.drop_column("marketplace_evidence", "price_estimation_method")
    op.drop_column("marketplace_evidence", "estimated_market_price")
