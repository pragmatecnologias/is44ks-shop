from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db import Base


class DiscoveryCampaign(Base):
    __tablename__ = "discovery_campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(300), nullable=False)
    category = Column(String(120), nullable=True)
    goal = Column(Text, nullable=True)
    constraints_json = Column(JSON, nullable=True)
    budget_limit_usd = Column(Numeric(10, 2), nullable=True)
    max_ideas = Column(Integer, nullable=True)
    max_products_to_promote = Column(Integer, nullable=True)
    status = Column(String(30), default="DRAFT", nullable=False)
    created_by = Column(String(120), nullable=True)
    latest_report_json = Column(JSON, nullable=True)
    report_generated_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    ideas = relationship("ProductIdea", back_populates="campaign", cascade="all, delete-orphan")
    tasks = relationship("DiscoveryCampaignTask", back_populates="campaign", cascade="all, delete-orphan")
    research_jobs = relationship("ExternalResearchJob", back_populates="campaign", cascade="all, delete-orphan")
    evidence_candidates = relationship("EvidenceCandidate", back_populates="campaign", cascade="all, delete-orphan")
    demand_research = relationship("ProductDemandResearch", back_populates="campaign", cascade="all, delete-orphan")
    trend_research = relationship("ProductTrendResearch", back_populates="campaign", cascade="all, delete-orphan")


class DiscoveryCampaignTask(Base):
    __tablename__ = "discovery_campaign_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("discovery_campaigns.id"), nullable=False)
    task_type = Column(String(80), nullable=False)
    status = Column(String(30), default="TODO", nullable=False)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    related_idea_id = Column(UUID(as_uuid=True), ForeignKey("product_discovery_ideas.id"), nullable=True)
    related_product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=True)
    related_candidate_id = Column(UUID(as_uuid=True), ForeignKey("evidence_candidates.id"), nullable=True)
    result_json = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    campaign = relationship("DiscoveryCampaign", back_populates="tasks")
    related_idea = relationship("ProductIdea")
    related_product = relationship("Product")
    related_candidate = relationship("EvidenceCandidate")
