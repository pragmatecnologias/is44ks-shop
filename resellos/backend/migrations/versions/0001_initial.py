"""initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2026-05-05
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("sku", sa.String(length=100), nullable=False, unique=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("subcategory", sa.String(length=100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="NEW"),
        sa.Column("risk_level", sa.String(length=50), nullable=True),
        sa.Column("final_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("final_decision", sa.String(length=50), nullable=True),
        sa.Column("target_sale_price", sa.Numeric(10, 2), nullable=True),
        sa.Column("expected_profit", sa.Numeric(10, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "product_sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("supplier_name", sa.Text(), nullable=True),
        sa.Column("supplier_platform", sa.String(length=100), nullable=True),
        sa.Column("supplier_url", sa.Text(), nullable=True),
        sa.Column("unit_cost", sa.Numeric(10, 2), nullable=True),
        sa.Column("domestic_shipping", sa.Numeric(10, 2), nullable=True),
        sa.Column("international_shipping_estimate", sa.Numeric(10, 2), nullable=True),
        sa.Column("estimated_landed_cost", sa.Numeric(10, 2), nullable=True),
        sa.Column("moq", sa.Integer(), nullable=True),
        sa.Column("supplier_rating", sa.String(length=50), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_primary", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "marketplace_research",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("marketplace", sa.String(length=100), nullable=False),
        sa.Column("keyword", sa.Text(), nullable=True),
        sa.Column("search_url", sa.Text(), nullable=True),
        sa.Column("active_listing_count", sa.Integer(), nullable=True),
        sa.Column("sold_listing_count", sa.Integer(), nullable=True),
        sa.Column("min_active_price", sa.Numeric(10, 2), nullable=True),
        sa.Column("median_active_price", sa.Numeric(10, 2), nullable=True),
        sa.Column("max_active_price", sa.Numeric(10, 2), nullable=True),
        sa.Column("min_sold_price", sa.Numeric(10, 2), nullable=True),
        sa.Column("median_sold_price", sa.Numeric(10, 2), nullable=True),
        sa.Column("max_sold_price", sa.Numeric(10, 2), nullable=True),
        sa.Column("shipping_min", sa.Numeric(10, 2), nullable=True),
        sa.Column("shipping_median", sa.Numeric(10, 2), nullable=True),
        sa.Column("shipping_max", sa.Numeric(10, 2), nullable=True),
        sa.Column("competition_level", sa.String(length=50), nullable=True),
        sa.Column("demand_signal", sa.String(length=50), nullable=True),
        sa.Column("evidence_quality", sa.String(length=50), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "competitor_listings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("marketplace", sa.String(length=100), nullable=True),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("price", sa.Numeric(10, 2), nullable=True),
        sa.Column("shipping_price", sa.Numeric(10, 2), nullable=True),
        sa.Column("condition", sa.String(length=50), nullable=True),
        sa.Column("seller_name", sa.String(length=200), nullable=True),
        sa.Column("sold", sa.Boolean(), nullable=True),
        sa.Column("photo_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("title_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("description_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "marketplace_evidence",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("marketplace", sa.Text(), nullable=False),
        sa.Column("evidence_type", sa.String(length=50), nullable=False),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("price", sa.Numeric(10, 2), nullable=True),
        sa.Column("shipping_price", sa.Numeric(10, 2), nullable=True),
        sa.Column("sold_date", sa.DateTime(), nullable=True),
        sa.Column("condition", sa.String(length=100), nullable=True),
        sa.Column("seller_name", sa.String(length=200), nullable=True),
        sa.Column("source_method", sa.String(length=50), nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.Column("screenshot_url", sa.Text(), nullable=True),
        sa.Column("confidence", sa.String(length=50), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "profit_analyses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("scenario_name", sa.String(length=100), nullable=True),
        sa.Column("expected_sale_price", sa.Numeric(10, 2), nullable=True),
        sa.Column("product_cost", sa.Numeric(10, 2), nullable=True),
        sa.Column("import_shipping_per_unit", sa.Numeric(10, 2), nullable=True),
        sa.Column("landed_cost", sa.Numeric(10, 2), nullable=True),
        sa.Column("marketplace_fee", sa.Numeric(10, 2), nullable=True),
        sa.Column("us_shipping", sa.Numeric(10, 2), nullable=True),
        sa.Column("packaging_cost", sa.Numeric(10, 2), nullable=True),
        sa.Column("estimated_net_profit", sa.Numeric(10, 2), nullable=True),
        sa.Column("margin_percent", sa.Numeric(8, 2), nullable=True),
        sa.Column("roi_percent", sa.Numeric(8, 2), nullable=True),
        sa.Column("break_even_price", sa.Numeric(10, 2), nullable=True),
        sa.Column("verdict", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "agent_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=True),
        sa.Column("agent_name", sa.String(length=100), nullable=False),
        sa.Column("report_type", sa.String(length=100), nullable=True),
        sa.Column("input_json", sa.Text(), nullable=True),
        sa.Column("output_json", sa.Text(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("confidence", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "inventory_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("quantity_on_hand", sa.Integer(), nullable=True),
        sa.Column("quantity_ordered", sa.Integer(), nullable=True),
        sa.Column("quantity_sold", sa.Integer(), nullable=True),
        sa.Column("quantity_returned", sa.Integer(), nullable=True),
        sa.Column("average_landed_cost", sa.Numeric(10, 2), nullable=True),
        sa.Column("location_code", sa.String(length=100), nullable=True),
        sa.Column("reorder_point", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "sales",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("marketplace", sa.String(length=100), nullable=True),
        sa.Column("sale_date", sa.DateTime(), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=True),
        sa.Column("sale_price", sa.Numeric(10, 2), nullable=True),
        sa.Column("marketplace_fee", sa.Numeric(10, 2), nullable=True),
        sa.Column("shipping_cost", sa.Numeric(10, 2), nullable=True),
        sa.Column("packaging_cost", sa.Numeric(10, 2), nullable=True),
        sa.Column("net_profit", sa.Numeric(10, 2), nullable=True),
        sa.Column("buyer_paid_shipping", sa.Boolean(), nullable=True),
        sa.Column("returned", sa.Boolean(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "product_files",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("file_type", sa.String(length=100), nullable=True),
        sa.Column("file_url", sa.Text(), nullable=True),
        sa.Column("original_filename", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("product_files")
    op.drop_table("sales")
    op.drop_table("inventory_items")
    op.drop_table("agent_reports")
    op.drop_table("profit_analyses")
    op.drop_table("marketplace_evidence")
    op.drop_table("competitor_listings")
    op.drop_table("marketplace_research")
    op.drop_table("product_sources")
    op.drop_table("products")
