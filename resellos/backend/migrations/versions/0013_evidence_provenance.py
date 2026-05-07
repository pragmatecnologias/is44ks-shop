"""add evidence provenance fields

Revision ID: 0013_evidence_provenance
Revises: 0012_research_search
Create Date: 2026-05-07
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "0013_evidence_provenance"
down_revision = "0012_research_search"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("marketplace_evidence", sa.Column("discovery_source", sa.String(50), nullable=True))
    op.add_column("marketplace_evidence", sa.Column("proof_level", sa.String(50), nullable=True))
    op.add_column("marketplace_evidence", sa.Column("original_search_intent", sa.String(50), nullable=True))


def downgrade() -> None:
    op.drop_column("marketplace_evidence", "original_search_intent")
    op.drop_column("marketplace_evidence", "proof_level")
    op.drop_column("marketplace_evidence", "discovery_source")