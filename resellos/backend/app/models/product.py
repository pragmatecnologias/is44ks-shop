import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sku = Column(String(100), unique=True, nullable=False)
    name = Column(Text, nullable=False)
    category = Column(String(100))
    subcategory = Column(String(100))
    description = Column(Text)
    status = Column(String(50), nullable=False, default="NEW")
    risk_level = Column(String(50))
    final_score = Column(Numeric(5, 2))
    final_decision = Column(String(50))
    target_sale_price = Column(Numeric(10, 2))
    expected_profit = Column(Numeric(10, 2))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    sources = relationship("ProductSource", back_populates="product", cascade="all, delete-orphan")
    marketplace_research = relationship("MarketplaceResearch", back_populates="product", cascade="all, delete-orphan")
    competitor_listings = relationship("CompetitorListing", back_populates="product", cascade="all, delete-orphan")
    profit_analyses = relationship("ProfitAnalysis", back_populates="product", cascade="all, delete-orphan")
    agent_reports = relationship("AgentReport", back_populates="product", cascade="all, delete-orphan")
    marketplace_evidence = relationship("MarketplaceEvidence", back_populates="product", cascade="all, delete-orphan")
    inventory = relationship("InventoryItem", back_populates="product", cascade="all, delete-orphan")
    sales = relationship("Sale", back_populates="product", cascade="all, delete-orphan")
    files = relationship("ProductFile", back_populates="product", cascade="all, delete-orphan")
    vision_reports = relationship("VisionAnalysisReport", back_populates="product", cascade="all, delete-orphan")
