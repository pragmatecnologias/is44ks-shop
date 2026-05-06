from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db import Base


class ProductDemandResearch(Base):
    __tablename__ = "product_demand_research"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=True)
    idea_id = Column(UUID(as_uuid=True), ForeignKey("product_discovery_ideas.id"), nullable=True)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("discovery_campaigns.id"), nullable=True)
    task_id = Column(UUID(as_uuid=True), ForeignKey("discovery_campaign_tasks.id"), nullable=True)
    keyword = Column(String(500), nullable=False)
    source = Column(String(80), nullable=False, default="MANUAL_CAPTURE")
    target_country = Column(String(8), nullable=False, default="US")
    target_language = Column(String(8), nullable=False, default="en")
    monthly_search_volume = Column(Integer, nullable=True)
    monthly_search_volume_min = Column(Integer, nullable=True)
    monthly_search_volume_max = Column(Integer, nullable=True)
    competition_level = Column(String(30), nullable=True)
    cpc_low = Column(Numeric(10, 2), nullable=True)
    cpc_high = Column(Numeric(10, 2), nullable=True)
    currency = Column(String(8), nullable=False, default="USD")
    buyer_intent_score = Column(Integer, nullable=False, default=0)
    keyword_specificity_score = Column(Integer, nullable=False, default=0)
    demand_score = Column(Integer, nullable=False, default=0)
    related_keywords_json = Column(JSON, nullable=False, default=list)
    raw_json = Column(JSON, nullable=True)
    verification_status = Column(String(50), nullable=False, default="USER_CAPTURED_UNVERIFIED")
    source_url = Column(Text, nullable=True)
    screenshot_url = Column(Text, nullable=True)
    verification_notes = Column(Text, nullable=True)
    created_by = Column(String(120), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = relationship("Product", back_populates="demand_research")
    idea = relationship("ProductIdea")
    campaign = relationship("DiscoveryCampaign", back_populates="demand_research")


class ProductTrendResearch(Base):
    __tablename__ = "product_trend_research"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=True)
    idea_id = Column(UUID(as_uuid=True), ForeignKey("product_discovery_ideas.id"), nullable=True)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("discovery_campaigns.id"), nullable=True)
    task_id = Column(UUID(as_uuid=True), ForeignKey("discovery_campaign_tasks.id"), nullable=True)
    keyword = Column(String(500), nullable=False)
    source = Column(String(80), nullable=False, default="MANUAL_CAPTURE")
    geo = Column(String(12), nullable=False, default="US")
    timeframe = Column(String(80), nullable=False, default="past_5_years")
    trend_direction = Column(String(30), nullable=True)
    seasonality_risk = Column(String(30), nullable=True)
    evergreen_score = Column(Integer, nullable=False, default=0)
    trend_stability_score = Column(Integer, nullable=False, default=0)
    spike_risk_score = Column(Integer, nullable=False, default=0)
    average_interest = Column(Numeric(10, 2), nullable=True)
    peak_interest = Column(Numeric(10, 2), nullable=True)
    low_interest = Column(Numeric(10, 2), nullable=True)
    trend_points_json = Column(JSON, nullable=False, default=list)
    raw_json = Column(JSON, nullable=True)
    verification_status = Column(String(50), nullable=False, default="USER_CAPTURED_UNVERIFIED")
    source_url = Column(Text, nullable=True)
    screenshot_url = Column(Text, nullable=True)
    verification_notes = Column(Text, nullable=True)
    created_by = Column(String(120), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = relationship("Product", back_populates="trend_research")
    idea = relationship("ProductIdea")
    campaign = relationship("DiscoveryCampaign", back_populates="trend_research")


class ProductValidationSummary(Base):
    __tablename__ = "product_validation_summaries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, unique=True)
    market_presence_status = Column(String(30), nullable=True)
    search_demand_status = Column(String(30), nullable=True)
    sold_demand_status = Column(String(30), nullable=True)
    trend_status = Column(String(30), nullable=True)
    supplier_economics_status = Column(String(30), nullable=True)
    competition_status = Column(String(30), nullable=True)
    risk_status = Column(String(30), nullable=True)
    market_presence_score = Column(Integer, nullable=False, default=0)
    search_demand_score = Column(Integer, nullable=False, default=0)
    sold_demand_score = Column(Integer, nullable=False, default=0)
    trend_score = Column(Integer, nullable=False, default=0)
    supplier_economics_score = Column(Integer, nullable=False, default=0)
    competition_score = Column(Integer, nullable=False, default=0)
    risk_score = Column(Integer, nullable=False, default=0)
    overall_validation_score = Column(Integer, nullable=False, default=0)
    validation_readiness = Column(String(40), nullable=False, default="INCOMPLETE")
    main_validation_blocker = Column(Text, nullable=True)
    next_validation_action = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = relationship("Product", back_populates="validation_summary")
