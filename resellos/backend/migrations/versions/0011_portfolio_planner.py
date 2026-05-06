"""add shop portfolio planner

Revision ID: 0011_portfolio_planner
Revises: 0010_validation_expansion
Create Date: 2026-05-06
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "0011_portfolio_planner"
down_revision = "0010_validation_expansion"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "shop_concepts",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=300), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("target_customer", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=120), nullable=True),
        sa.Column("price_min", sa.Numeric(10, 2), nullable=True),
        sa.Column("price_max", sa.Numeric(10, 2), nullable=True),
        sa.Column("avoid_list_json", sa.JSON(), nullable=True),
        sa.Column("preferred_attributes_json", sa.JSON(), nullable=True),
        sa.Column("brand_angle", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="DRAFT"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "product_collections",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("shop_concept_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("shop_concepts.id"), nullable=False),
        sa.Column("name", sa.String(length=300), nullable=False),
        sa.Column("theme", sa.Text(), nullable=True),
        sa.Column("target_problem", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="DRAFT"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "portfolio_items",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("shop_concept_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("shop_concepts.id"), nullable=False),
        sa.Column("collection_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("product_collections.id"), nullable=True),
        sa.Column("idea_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("product_discovery_ideas.id"), nullable=True),
        sa.Column("product_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=True),
        sa.Column("role", sa.String(length=30), nullable=False, server_default="CONSIDERING"),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="CONSIDERING"),
        sa.Column("assortment_fit_score", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("bundle_potential_score", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    op.add_column("discovery_campaigns", sa.Column("shop_concept_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("shop_concepts.id"), nullable=True))
    op.add_column("discovery_campaigns", sa.Column("collection_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("product_collections.id"), nullable=True))
    op.add_column("product_discovery_ideas", sa.Column("shop_concept_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("shop_concepts.id"), nullable=True))
    op.add_column("product_discovery_ideas", sa.Column("collection_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("product_collections.id"), nullable=True))
    op.add_column("products", sa.Column("shop_concept_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("shop_concepts.id"), nullable=True))
    op.add_column("products", sa.Column("collection_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("product_collections.id"), nullable=True))

    op.create_index("ix_shop_concepts_status", "shop_concepts", ["status"])
    op.create_index("ix_product_collections_shop_concept_id", "product_collections", ["shop_concept_id"])
    op.create_index("ix_portfolio_items_shop_concept_id", "portfolio_items", ["shop_concept_id"])
    op.create_index("ix_portfolio_items_collection_id", "portfolio_items", ["collection_id"])
    op.create_index("ix_portfolio_items_idea_id", "portfolio_items", ["idea_id"])
    op.create_index("ix_portfolio_items_product_id", "portfolio_items", ["product_id"])


def downgrade() -> None:
    op.drop_index("ix_portfolio_items_product_id", table_name="portfolio_items")
    op.drop_index("ix_portfolio_items_idea_id", table_name="portfolio_items")
    op.drop_index("ix_portfolio_items_collection_id", table_name="portfolio_items")
    op.drop_index("ix_portfolio_items_shop_concept_id", table_name="portfolio_items")
    op.drop_index("ix_product_collections_shop_concept_id", table_name="product_collections")
    op.drop_index("ix_shop_concepts_status", table_name="shop_concepts")
    op.drop_column("products", "collection_id")
    op.drop_column("products", "shop_concept_id")
    op.drop_column("product_discovery_ideas", "collection_id")
    op.drop_column("product_discovery_ideas", "shop_concept_id")
    op.drop_column("discovery_campaigns", "collection_id")
    op.drop_column("discovery_campaigns", "shop_concept_id")
    op.drop_table("portfolio_items")
    op.drop_table("product_collections")
    op.drop_table("shop_concepts")

