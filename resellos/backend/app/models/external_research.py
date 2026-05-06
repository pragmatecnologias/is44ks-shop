from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db import Base


class ExternalResearchJob(Base):
    __tablename__ = "external_research_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    idea_id = Column(UUID(as_uuid=True), ForeignKey("product_discovery_ideas.id"), nullable=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=True)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("discovery_campaigns.id"), nullable=True)
    provider = Column(String(50), nullable=False)
    api_area = Column(String(100), nullable=False)
    query = Column(String(500), nullable=False)
    queue = Column(String(50), default="standard")
    status = Column(String(30), default="QUEUED")
    provider_task_id = Column(String(120), nullable=True)
    cost_estimate = Column(Numeric(10, 4), nullable=True)
    result_count = Column(Integer, default=0)
    result_count_raw = Column(Integer, default=0)
    candidate_count = Column(Integer, default=0)
    raw_request = Column(JSON, nullable=True)
    raw_response = Column(JSON, nullable=True)
    last_error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    idea = relationship("ProductIdea", back_populates="external_research_jobs")
    product = relationship("Product", back_populates="external_research_jobs")
    campaign = relationship("DiscoveryCampaign", back_populates="research_jobs")
    candidates = relationship("EvidenceCandidate", back_populates="job", cascade="all, delete-orphan")


class EvidenceCandidate(Base):
    __tablename__ = "evidence_candidates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("external_research_jobs.id"), nullable=True)
    idea_id = Column(UUID(as_uuid=True), ForeignKey("product_discovery_ideas.id"), nullable=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=True)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("discovery_campaigns.id"), nullable=True)
    source = Column(String(50), nullable=False)
    candidate_type = Column(String(50), nullable=False)
    marketplace = Column(String(120), nullable=True)
    evidence_type = Column(String(50), nullable=True)
    title = Column(String(500), nullable=True)
    url = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=True)
    shipping_price = Column(Numeric(10, 2), nullable=True)
    seller = Column(String(200), nullable=True)
    rating = Column(Numeric(5, 2), nullable=True)
    review_count = Column(Integer, nullable=True)
    image_url = Column(Text, nullable=True)
    confidence = Column(String(50), default="MEDIUM")
    review_status = Column(String(30), default="PENDING")
    raw_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("ExternalResearchJob", back_populates="candidates")
    idea = relationship("ProductIdea")
    product = relationship("Product")
    campaign = relationship("DiscoveryCampaign", back_populates="evidence_candidates")
