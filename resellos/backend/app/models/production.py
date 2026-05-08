from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    Numeric,
    String,
    Table,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db import Base

# Association table for many-to-many machine <-> capability
machine_capabilities = Table(
    "machine_capabilities",
    Base.metadata,
    Column(
        "machine_id",
        UUID(as_uuid=True),
        ForeignKey("machine_candidates.id"),
        primary_key=True,
    ),
    Column(
        "capability_id",
        UUID(as_uuid=True),
        ForeignKey("production_capabilities.id"),
        primary_key=True,
    ),
)


class ProductionCampaign(Base):
    __tablename__ = "production_campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(300), nullable=False)
    shop_concept_id = Column(
        UUID(as_uuid=True), ForeignKey("shop_concepts.id"), nullable=True
    )
    mode = Column(String(30), default="PRODUCTION", nullable=False)
    goal = Column(Text, nullable=True)
    workspace_type = Column(String(100), nullable=True)
    workspace_dimensions_json = Column(JSON, nullable=True)
    power_constraints_json = Column(JSON, nullable=True)
    safety_requirements_json = Column(JSON, nullable=True)
    budget_limit_usd = Column(Numeric(10, 2), nullable=True)
    status = Column(String(30), default="DRAFT", nullable=False)
    created_by = Column(String(120), nullable=True)
    latest_report_json = Column(JSON, nullable=True)
    report_generated_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    shop_concept = relationship("ShopConcept", back_populates="production_campaigns")
    capabilities = relationship(
        "ProductionCapability",
        back_populates="campaign",
        cascade="all, delete-orphan",
    )
    machines = relationship(
        "MachineCandidate",
        back_populates="campaign",
        cascade="all, delete-orphan",
    )


class ProductionCapability(Base):
    __tablename__ = "production_capabilities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(
        UUID(as_uuid=True),
        ForeignKey("production_campaigns.id"),
        nullable=False,
    )
    name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    materials = Column(JSON, nullable=True)
    typical_products = Column(JSON, nullable=True)
    entry_cost_range_json = Column(JSON, nullable=True)
    skill_level = Column(String(30), nullable=True)
    workspace_footprint = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    campaign = relationship("ProductionCampaign", back_populates="capabilities")
    machines = relationship(
        "MachineCandidate",
        secondary="machine_capabilities",
        back_populates="capabilities",
    )


class MachineCandidate(Base):
    __tablename__ = "machine_candidates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(
        UUID(as_uuid=True),
        ForeignKey("production_campaigns.id"),
        nullable=False,
    )
    name = Column(String(300), nullable=False)
    brand = Column(String(200), nullable=True)
    model = Column(String(200), nullable=True)
    category = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    url = Column(Text, nullable=True)
    price_new = Column(Numeric(10, 2), nullable=True)
    price_used_range_json = Column(JSON, nullable=True)
    condition = Column(String(50), nullable=True)
    power_requirements = Column(String(100), nullable=True)
    workspace_needed = Column(String(100), nullable=True)
    safety_notes = Column(Text, nullable=True)
    status = Column(String(50), default="SUGGESTED", nullable=False)
    decision_recommendation = Column(String(50), nullable=True)
    decision_reason = Column(Text, nullable=True)
    decided_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    campaign = relationship("ProductionCampaign", back_populates="machines")
    capabilities = relationship(
        "ProductionCapability",
        secondary="machine_capabilities",
        back_populates="machines",
    )
    evidence = relationship(
        "MachineEvidence",
        back_populates="machine",
        cascade="all, delete-orphan",
    )
    product_families = relationship(
        "MachineProductFamily",
        back_populates="machine",
        cascade="all, delete-orphan",
    )
    cost_scenarios = relationship(
        "ProductionCostScenario",
        back_populates="machine",
        cascade="all, delete-orphan",
    )
    decision = relationship(
        "MachineDecision",
        back_populates="machine",
        uselist=False,
        cascade="all, delete-orphan",
    )


class MachineEvidence(Base):
    __tablename__ = "machine_evidence"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    machine_id = Column(
        UUID(as_uuid=True),
        ForeignKey("machine_candidates.id"),
        nullable=False,
    )
    evidence_type = Column(String(50), nullable=False)
    title = Column(String(500), nullable=True)
    url = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=True)
    source = Column(String(100), nullable=True)
    seller = Column(String(200), nullable=True)
    condition = Column(String(50), nullable=True)
    specs_json = Column(JSON, nullable=True)
    pros = Column(Text, nullable=True)
    cons = Column(Text, nullable=True)
    verification_status = Column(String(50), default="PENDING")
    confidence = Column(String(20), default="MEDIUM")
    raw_text = Column(Text, nullable=True)
    screenshot_url = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    machine = relationship("MachineCandidate", back_populates="evidence")


class MachineProductFamily(Base):
    __tablename__ = "machine_product_families"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    machine_id = Column(
        UUID(as_uuid=True),
        ForeignKey("machine_candidates.id"),
        nullable=False,
    )
    name = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    material_cost_per_unit = Column(Numeric(10, 2), nullable=True)
    estimated_sale_price = Column(Numeric(10, 2), nullable=True)
    estimated_demand = Column(String(30), nullable=True)
    market_evidence_summary = Column(Text, nullable=True)
    market_evidence_count = Column(Integer, default=0)
    has_market_evidence = Column(Boolean, default=False)
    status = Column(String(50), default="SUGGESTED", nullable=False)
    promoted_product_id = Column(
        UUID(as_uuid=True), ForeignKey("products.id"), nullable=True
    )
    promoted_idea_id = Column(
        UUID(as_uuid=True),
        ForeignKey("product_discovery_ideas.id"),
        nullable=True,
    )
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    machine = relationship("MachineCandidate", back_populates="product_families")
    promoted_product = relationship("Product", foreign_keys=[promoted_product_id])
    promoted_idea = relationship("ProductIdea", foreign_keys=[promoted_idea_id])
    cost_scenarios = relationship(
        "ProductionCostScenario",
        back_populates="product_family",
        cascade="all, delete-orphan",
    )


class ProductionCostScenario(Base):
    __tablename__ = "production_cost_scenarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    machine_id = Column(
        UUID(as_uuid=True),
        ForeignKey("machine_candidates.id"),
        nullable=False,
    )
    product_family_id = Column(
        UUID(as_uuid=True),
        ForeignKey("machine_product_families.id"),
        nullable=True,
    )
    scenario_name = Column(String(200), nullable=False)
    material_cost = Column(Numeric(10, 2), nullable=True)
    labor_cost = Column(Numeric(10, 2), nullable=True)
    machine_time_cost = Column(Numeric(10, 2), nullable=True)
    consumables_cost = Column(Numeric(10, 2), nullable=True)
    marketplace_fee = Column(Numeric(10, 2), nullable=True)
    shipping_cost = Column(Numeric(10, 2), nullable=True)
    packaging_cost = Column(Numeric(10, 2), nullable=True)
    other_costs = Column(Numeric(10, 2), nullable=True)
    total_cost_per_unit = Column(Numeric(10, 2), nullable=True)
    sale_price = Column(Numeric(10, 2), nullable=True)
    net_profit_per_unit = Column(Numeric(10, 2), nullable=True)
    margin_percent = Column(Numeric(8, 2), nullable=True)
    machine_purchase_price = Column(Numeric(10, 2), nullable=True)
    units_per_month = Column(Integer, nullable=True)
    monthly_profit = Column(Numeric(10, 2), nullable=True)
    payback_months = Column(Numeric(8, 1), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    machine = relationship("MachineCandidate", back_populates="cost_scenarios")
    product_family = relationship(
        "MachineProductFamily", back_populates="cost_scenarios"
    )


class MachineDecision(Base):
    __tablename__ = "machine_decisions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    machine_id = Column(
        UUID(as_uuid=True),
        ForeignKey("machine_candidates.id"),
        nullable=False,
        unique=True,
    )
    recommendation = Column(String(50), nullable=False)
    reason = Column(Text, nullable=True)
    confidence = Column(String(20), default="MEDIUM")
    evidence_count = Column(Integer, default=0)
    product_family_count = Column(Integer, default=0)
    families_with_market_evidence = Column(Integer, default=0)
    has_cost_scenario = Column(Boolean, default=False)
    payback_calculated = Column(Boolean, default=False)
    workspace_fit = Column(String(20), nullable=True)
    safety_fit = Column(String(20), nullable=True)
    budget_fit = Column(String(20), nullable=True)
    hard_blockers_json = Column(JSON, nullable=True)
    warnings_json = Column(JSON, nullable=True)
    agent_output_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    machine = relationship("MachineCandidate", back_populates="decision")
