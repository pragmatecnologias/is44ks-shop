"""research search result storage

Revision ID: 0012_research_search
Revises: 0011_portfolio_planner
Create Date: 2026-05-07
"""

from __future__ import annotations

import uuid
from datetime import datetime

import sqlalchemy as sa
from alembic import op

revision = "0012_research_search"
down_revision = "0011_portfolio_planner"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "research_search_results",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("query", sa.Text, nullable=False),
        sa.Column("normalized_query", sa.Text, nullable=True),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("intent", sa.String(50), nullable=False),
        sa.Column("title", sa.Text, nullable=True),
        sa.Column("url", sa.Text, nullable=False),
        sa.Column("normalized_url", sa.Text, nullable=True),
        sa.Column("snippet", sa.Text, nullable=True),
        sa.Column("source_domain", sa.String(255), nullable=True),
        sa.Column("rank", sa.Integer, nullable=True),
        sa.Column("price_text", sa.String(100), nullable=True),
        sa.Column("currency", sa.String(10), nullable=True),
        sa.Column("raw_json", sa.JSON, nullable=True),
        sa.Column("fetched_at", sa.DateTime, nullable=True),
        sa.Column("product_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("idea_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("campaign_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("converted_candidate_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("conversion_status", sa.String(50), nullable=True),
        sa.Column("reject_reason", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, default=datetime.utcnow),
        sa.Column("updated_at", sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
    )

    op.create_index("ix_research_search_url", "research_search_results", ["url"])
    op.create_index("ix_research_search_normalized_url", "research_search_results", ["normalized_url"])
    op.create_index("ix_research_search_query", "research_search_results", ["query"])
    op.create_index("ix_research_search_provider", "research_search_results", ["provider"])
    op.create_index("ix_research_search_intent", "research_search_results", ["intent"])
    op.create_index("ix_research_search_product_id", "research_search_results", ["product_id"])
    op.create_index("ix_research_search_idea_id", "research_search_results", ["idea_id"])
    op.create_index("ix_research_search_campaign_id", "research_search_results", ["campaign_id"])
    op.create_index("ix_research_search_source_domain", "research_search_results", ["source_domain"])
    op.create_index("ix_research_search_fetched_at", "research_search_results", ["fetched_at"])


def downgrade() -> None:
    op.drop_index("ix_research_search_fetched_at", table_name="research_search_results")
    op.drop_index("ix_research_search_source_domain", table_name="research_search_results")
    op.drop_index("ix_research_search_campaign_id", table_name="research_search_results")
    op.drop_index("ix_research_search_idea_id", table_name="research_search_results")
    op.drop_index("ix_research_search_product_id", table_name="research_search_results")
    op.drop_index("ix_research_search_intent", table_name="research_search_results")
    op.drop_index("ix_research_search_provider", table_name="research_search_results")
    op.drop_index("ix_research_search_query", table_name="research_search_results")
    op.drop_index("ix_research_search_normalized_url", table_name="research_search_results")
    op.drop_index("ix_research_search_url", table_name="research_search_results")
    op.drop_table("research_search_results")
