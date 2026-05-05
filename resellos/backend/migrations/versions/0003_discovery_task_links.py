"""discovery task links

Revision ID: 0003_discovery_task_links
Revises: 0002_discovery
Create Date: 2026-05-05
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision = "0003_discovery_task_links"
down_revision = "0002_discovery"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("discovery_tasks", sa.Column("linked_evidence_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("discovery_tasks", sa.Column("linked_source_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("discovery_tasks", sa.Column("linked_competitor_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("discovery_tasks", sa.Column("linked_product_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        "fk_discovery_tasks_linked_evidence_id_marketplace_evidence",
        "discovery_tasks",
        "marketplace_evidence",
        ["linked_evidence_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_discovery_tasks_linked_source_id_product_sources",
        "discovery_tasks",
        "product_sources",
        ["linked_source_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_discovery_tasks_linked_competitor_id_competitor_listings",
        "discovery_tasks",
        "competitor_listings",
        ["linked_competitor_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_discovery_tasks_linked_product_id_products",
        "discovery_tasks",
        "products",
        ["linked_product_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_discovery_tasks_linked_product_id_products", "discovery_tasks", type_="foreignkey")
    op.drop_constraint("fk_discovery_tasks_linked_competitor_id_competitor_listings", "discovery_tasks", type_="foreignkey")
    op.drop_constraint("fk_discovery_tasks_linked_source_id_product_sources", "discovery_tasks", type_="foreignkey")
    op.drop_constraint("fk_discovery_tasks_linked_evidence_id_marketplace_evidence", "discovery_tasks", type_="foreignkey")
    op.drop_column("discovery_tasks", "linked_product_id")
    op.drop_column("discovery_tasks", "linked_competitor_id")
    op.drop_column("discovery_tasks", "linked_source_id")
    op.drop_column("discovery_tasks", "linked_evidence_id")
