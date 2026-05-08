from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db import Base


class ShopConcept(Base):
    __tablename__ = "shop_concepts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    target_customer = Column(Text, nullable=True)
    category = Column(String(120), nullable=True)
    price_min = Column(Numeric(10, 2), nullable=True)
    price_max = Column(Numeric(10, 2), nullable=True)
    avoid_list_json = Column(JSON, nullable=True)
    preferred_attributes_json = Column(JSON, nullable=True)
    brand_angle = Column(Text, nullable=True)
    status = Column(String(30), default="DRAFT", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    campaigns = relationship("DiscoveryCampaign", back_populates="shop_concept")
    collections = relationship("ProductCollection", back_populates="shop_concept", cascade="all, delete-orphan")
    ideas = relationship("ProductIdea", back_populates="shop_concept")
    products = relationship("Product", back_populates="shop_concept")
    portfolio_items = relationship("PortfolioItem", back_populates="shop_concept", cascade="all, delete-orphan")
    production_campaigns = relationship("ProductionCampaign", back_populates="shop_concept")


class ProductCollection(Base):
    __tablename__ = "product_collections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_concept_id = Column(UUID(as_uuid=True), ForeignKey("shop_concepts.id"), nullable=False)
    name = Column(String(300), nullable=False)
    theme = Column(Text, nullable=True)
    target_problem = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    status = Column(String(30), default="DRAFT", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    shop_concept = relationship("ShopConcept", back_populates="collections")
    campaigns = relationship("DiscoveryCampaign", back_populates="collection")
    ideas = relationship("ProductIdea", back_populates="collection")
    products = relationship("Product", back_populates="collection")
    portfolio_items = relationship("PortfolioItem", back_populates="collection", cascade="all, delete-orphan")


class PortfolioItem(Base):
    __tablename__ = "portfolio_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_concept_id = Column(UUID(as_uuid=True), ForeignKey("shop_concepts.id"), nullable=False)
    collection_id = Column(UUID(as_uuid=True), ForeignKey("product_collections.id"), nullable=True)
    idea_id = Column(UUID(as_uuid=True), ForeignKey("product_discovery_ideas.id"), nullable=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=True)
    role = Column(String(30), default="CONSIDERING", nullable=False)
    status = Column(String(30), default="CONSIDERING", nullable=False)
    assortment_fit_score = Column(Integer, default=0)
    bundle_potential_score = Column(Integer, default=0)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    shop_concept = relationship("ShopConcept", back_populates="portfolio_items")
    collection = relationship("ProductCollection", back_populates="portfolio_items")
    idea = relationship("ProductIdea", back_populates="portfolio_items")
    product = relationship("Product", back_populates="portfolio_items")
