import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Numeric, ForeignKey, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db import Base


class ProductSource(Base):
    __tablename__ = "product_sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    supplier_name = Column(Text)
    supplier_platform = Column(String(100))
    supplier_url = Column(Text)
    unit_cost = Column(Numeric(10, 2))
    domestic_shipping = Column(Numeric(10, 2))
    international_shipping_estimate = Column(Numeric(10, 2))
    estimated_landed_cost = Column(Numeric(10, 2))
    moq = Column(Integer)
    supplier_rating = Column(String(50))
    notes = Column(Text)
    is_primary = Column(Boolean, default=False)
    verification_status = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="sources")


class MarketplaceResearch(Base):
    __tablename__ = "marketplace_research"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    marketplace = Column(String(100), nullable=False)
    keyword = Column(Text)
    search_url = Column(Text)
    active_listing_count = Column(Integer)
    sold_listing_count = Column(Integer)
    min_active_price = Column(Numeric(10, 2))
    median_active_price = Column(Numeric(10, 2))
    max_active_price = Column(Numeric(10, 2))
    min_sold_price = Column(Numeric(10, 2))
    median_sold_price = Column(Numeric(10, 2))
    max_sold_price = Column(Numeric(10, 2))
    shipping_min = Column(Numeric(10, 2))
    shipping_median = Column(Numeric(10, 2))
    shipping_max = Column(Numeric(10, 2))
    competition_level = Column(String(50))
    demand_signal = Column(String(50))
    evidence_quality = Column(String(50))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="marketplace_research")


class CompetitorListing(Base):
    __tablename__ = "competitor_listings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    marketplace = Column(String(100))
    title = Column(Text)
    url = Column(Text)
    price = Column(Numeric(10, 2))
    shipping_price = Column(Numeric(10, 2))
    condition = Column(String(50))
    seller_name = Column(String(200))
    sold = Column(Boolean, default=False)
    verification_status = Column(String(50))
    photo_score = Column(Numeric(5, 2))
    title_score = Column(Numeric(5, 2))
    description_score = Column(Numeric(5, 2))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="competitor_listings")


class ProfitAnalysis(Base):
    __tablename__ = "profit_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    scenario_name = Column(String(100))
    expected_sale_price = Column(Numeric(10, 2))
    product_cost = Column(Numeric(10, 2))
    import_shipping_per_unit = Column(Numeric(10, 2))
    landed_cost = Column(Numeric(10, 2))
    marketplace_fee = Column(Numeric(10, 2))
    us_shipping = Column(Numeric(10, 2))
    packaging_cost = Column(Numeric(10, 2))
    return_allowance = Column(Numeric(10, 2))
    ad_cost = Column(Numeric(10, 2))
    estimated_net_profit = Column(Numeric(10, 2))
    margin_percent = Column(Numeric(8, 2))
    roi_percent = Column(Numeric(8, 2))
    break_even_price = Column(Numeric(10, 2))
    verdict = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="profit_analyses")


class AgentReport(Base):
    __tablename__ = "agent_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"))
    agent_name = Column(String(100), nullable=False)
    report_type = Column(String(100))
    input_json = Column(Text)
    output_json = Column(Text)
    summary = Column(Text)
    confidence = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="agent_reports")


class MarketplaceEvidence(Base):
    __tablename__ = "marketplace_evidence"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    marketplace = Column(Text, nullable=False)
    evidence_type = Column(String(50), nullable=False)
    title = Column(Text)
    url = Column(Text)
    price = Column(Numeric(10, 2))
    shipping_price = Column(Numeric(10, 2))
    sold_date = Column(DateTime)
    condition = Column(String(100))
    seller_name = Column(String(200))
    source_method = Column(String(50))
    verification_status = Column(String(50))
    raw_text = Column(Text)
    screenshot_url = Column(Text)
    confidence = Column(String(50))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="marketplace_evidence")


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    quantity_on_hand = Column(Integer, default=0)
    quantity_ordered = Column(Integer, default=0)
    quantity_sold = Column(Integer, default=0)
    quantity_returned = Column(Integer, default=0)
    average_landed_cost = Column(Numeric(10, 2))
    location_code = Column(String(100))
    reorder_point = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = relationship("Product", back_populates="inventory")


class Sale(Base):
    __tablename__ = "sales"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    marketplace = Column(String(100))
    sale_date = Column(DateTime)
    quantity = Column(Integer)
    sale_price = Column(Numeric(10, 2))
    marketplace_fee = Column(Numeric(10, 2))
    shipping_cost = Column(Numeric(10, 2))
    packaging_cost = Column(Numeric(10, 2))
    net_profit = Column(Numeric(10, 2))
    buyer_paid_shipping = Column(Boolean, default=False)
    returned = Column(Boolean, default=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="sales")


class ProductFile(Base):
    __tablename__ = "product_files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    file_type = Column(String(100))
    file_url = Column(Text)
    original_filename = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="files")


class ProductIdea(Base):
    __tablename__ = "product_discovery_ideas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    idea_name = Column(Text, nullable=False)
    category = Column(String(120))
    source_platform = Column(String(100))
    source_url = Column(Text)
    rough_supplier_cost = Column(Numeric(10, 2))
    estimated_landed_cost = Column(Numeric(10, 2))
    why_interesting = Column(Text)
    risk_flags = Column(Text)
    quick_market_signal = Column(Text)
    quick_profit_signal = Column(Text)
    research_priority = Column(String(50), default="MEDIUM")
    notes = Column(Text)
    status = Column(String(50), default="IDEA")
    quick_scan_verdict = Column(String(50))
    quick_scan_reason = Column(Text)
    suggested_keywords = Column(Text)
    required_next_evidence = Column(Text)
    promoted_product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    promoted_product = relationship("Product", foreign_keys=[promoted_product_id])
    vision_reports = relationship("VisionAnalysisReport", back_populates="idea", cascade="all, delete-orphan")
    external_research_jobs = relationship("ExternalResearchJob", back_populates="idea", cascade="all, delete-orphan")


class DiscoveryTask(Base):
    __tablename__ = "discovery_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    idea_id = Column(UUID(as_uuid=True), ForeignKey("product_discovery_ideas.id"), nullable=False)
    task_type = Column(String(80), nullable=False)
    title = Column(Text, nullable=False)
    status = Column(String(30), default="TODO")
    notes = Column(Text)
    sort_order = Column(Integer, default=0)
    linked_evidence_id = Column(UUID(as_uuid=True), ForeignKey("marketplace_evidence.id"))
    linked_source_id = Column(UUID(as_uuid=True), ForeignKey("product_sources.id"))
    linked_competitor_id = Column(UUID(as_uuid=True), ForeignKey("competitor_listings.id"))
    linked_product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    idea = relationship("ProductIdea", back_populates="tasks")


ProductIdea.tasks = relationship(
    "DiscoveryTask",
    back_populates="idea",
    cascade="all, delete-orphan",
)


# Backwards-compatible aliases for the older discovery naming.
ProductDiscoveryIdea = ProductIdea
