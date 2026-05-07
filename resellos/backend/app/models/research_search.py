from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID

from app.db import Base


class ResearchSearchResult(Base):
    __tablename__ = "research_search_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query = Column(Text, nullable=False)
    normalized_query = Column(Text, nullable=True)
    provider = Column(String(50), nullable=False)
    intent = Column(String(50), nullable=False)
    title = Column(Text, nullable=True)
    url = Column(Text, nullable=False)
    snippet = Column(Text, nullable=True)
    source_domain = Column(String(255), nullable=True)
    rank = Column(Integer, nullable=True)
    price_text = Column(String(100), nullable=True)
    currency = Column(String(10), nullable=True)
    raw_json = Column(JSON, nullable=True)
    fetched_at = Column(DateTime, nullable=True)
    product_id = Column(UUID(as_uuid=True), nullable=True)
    idea_id = Column(UUID(as_uuid=True), nullable=True)
    campaign_id = Column(UUID(as_uuid=True), nullable=True)
    converted_candidate_id = Column(UUID(as_uuid=True), nullable=True)
    conversion_status = Column(String(50), nullable=True)
    reject_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)