from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Text, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db import Base


class VisionAnalysisReport(Base):
    __tablename__ = "vision_analysis_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=True)
    idea_id = Column(UUID(as_uuid=True), ForeignKey("product_discovery_ideas.id"), nullable=True)
    file_url = Column(Text, nullable=True)
    analysis_type = Column(String(100), nullable=False)
    provider = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    input_metadata = Column(Text, nullable=True)
    output_json = Column(Text, nullable=True)
    confidence = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="vision_reports")
    idea = relationship("ProductIdea", back_populates="vision_reports")
