from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.campaign import DiscoveryCampaignTask
from app.models.supplier import AgentReport
from app.models.product_validation import ProductTrendResearch
from app.models.supplier import ProductIdea
from app.schemas.validation_schema import ProductTrendResearchCreate, ProductTrendResearchVerifyRequest


def score_trend_direction(direction: str | None) -> int:
    mapping = {
        "RISING": 90,
        "STABLE": 80,
        "SEASONAL": 55,
        "SPIKY": 35,
        "DECLINING": 20,
        "UNKNOWN": 0,
    }
    return mapping.get(str(direction or "UNKNOWN").upper(), 0)


def score_seasonality_risk(risk: str | None) -> int:
    mapping = {
        "LOW": 90,
        "MEDIUM": 60,
        "HIGH": 25,
        "UNKNOWN": 0,
    }
    return mapping.get(str(risk or "UNKNOWN").upper(), 0)


class TrendResearchService:
    def __init__(self, db: Session):
        self.db = db

    def _resolve_campaign_id(self, *, product_id: uuid.UUID | None, idea_id: uuid.UUID | None, campaign_id: uuid.UUID | None, task_id: uuid.UUID | None) -> uuid.UUID | None:
        if campaign_id is not None:
            return campaign_id
        if idea_id is not None:
            idea = self.db.query(ProductIdea).filter(ProductIdea.id == idea_id).first()
            if idea and idea.campaign_id:
                return idea.campaign_id
        if task_id is not None:
            task = self.db.query(DiscoveryCampaignTask).filter(DiscoveryCampaignTask.id == task_id).first()
            if task and task.related_idea and task.related_idea.campaign_id:
                return task.related_idea.campaign_id
            if task and task.related_product_id:
                return self._resolve_campaign_id(product_id=task.related_product_id, idea_id=None, campaign_id=None, task_id=None)
        if product_id is not None:
            latest_discovery = (
                self.db.query(AgentReport)
                .filter(AgentReport.product_id == product_id, AgentReport.agent_name == "discovery_context")
                .order_by(AgentReport.created_at.desc())
                .first()
            )
            if latest_discovery and latest_discovery.output_json:
                try:
                    raw = json.loads(latest_discovery.output_json) if isinstance(latest_discovery.output_json, str) else latest_discovery.output_json
                except Exception:
                    raw = {}
                idea_id = raw.get("idea_id")
                if idea_id:
                    idea = self.db.query(ProductIdea).filter(ProductIdea.id == uuid.UUID(str(idea_id))).first()
                    if idea and idea.campaign_id:
                        return idea.campaign_id
        return None

    def list_research(
        self,
        *,
        product_id: uuid.UUID | None = None,
        idea_id: uuid.UUID | None = None,
        campaign_id: uuid.UUID | None = None,
        verification_status: str | None = None,
    ) -> list[ProductTrendResearch]:
        query = self.db.query(ProductTrendResearch)
        if product_id is not None:
            query = query.filter(ProductTrendResearch.product_id == product_id)
        if idea_id is not None:
            query = query.filter(ProductTrendResearch.idea_id == idea_id)
        if campaign_id is not None:
            query = query.filter(ProductTrendResearch.campaign_id == campaign_id)
        if verification_status:
            query = query.filter(ProductTrendResearch.verification_status == verification_status)
        return query.order_by(ProductTrendResearch.updated_at.desc(), ProductTrendResearch.created_at.desc()).all()

    def get_research(self, research_id: uuid.UUID) -> ProductTrendResearch | None:
        return self.db.query(ProductTrendResearch).filter(ProductTrendResearch.id == research_id).first()

    def create_research(self, data: ProductTrendResearchCreate) -> ProductTrendResearch:
        campaign_id = self._resolve_campaign_id(product_id=data.product_id, idea_id=data.idea_id, campaign_id=data.campaign_id, task_id=getattr(data, "task_id", None))
        trend_stability = data.trend_stability_score or score_trend_direction(data.trend_direction)
        evergreen_score = data.evergreen_score or max(0, min(100, trend_stability - (data.spike_risk_score or 0) // 2))
        spike_risk = data.spike_risk_score or max(0, min(100, 100 - trend_stability))
        research = ProductTrendResearch(
            product_id=data.product_id,
            idea_id=data.idea_id,
            campaign_id=campaign_id,
            task_id=getattr(data, "task_id", None),
            keyword=data.keyword,
            source=data.source,
            geo=data.geo,
            timeframe=data.timeframe,
            trend_direction=data.trend_direction,
            seasonality_risk=data.seasonality_risk,
            evergreen_score=evergreen_score,
            trend_stability_score=trend_stability,
            spike_risk_score=spike_risk,
            average_interest=data.average_interest,
            peak_interest=data.peak_interest,
            low_interest=data.low_interest,
            trend_points_json=data.trend_points or [],
            raw_json=data.raw_json or None,
            verification_status=data.verification_status or "USER_CAPTURED_UNVERIFIED",
            source_url=data.source_url,
            screenshot_url=data.screenshot_url,
            verification_notes=data.verification_notes,
            created_by=data.created_by,
        )
        self.db.add(research)
        self.db.commit()
        self.db.refresh(research)
        return research

    def verify_research(self, research_id: uuid.UUID, data: ProductTrendResearchVerifyRequest) -> ProductTrendResearch:
        research = self.get_research(research_id)
        if not research:
            raise HTTPException(status_code=404, detail="Trend research record not found")
        if data.verification_status == "USER_VERIFIED" and not (data.source_url or data.screenshot_url or data.verification_notes):
            raise HTTPException(status_code=400, detail="Trend research verification requires proof.")
        research.verification_status = data.verification_status
        if data.source_url is not None:
            research.source_url = data.source_url
        if data.screenshot_url is not None:
            research.screenshot_url = data.screenshot_url
        if data.verification_notes is not None:
            research.verification_notes = data.verification_notes
        research.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(research)
        return research

    def to_dict(self, research: ProductTrendResearch) -> dict[str, Any]:
        return {
            "id": research.id,
            "product_id": research.product_id,
            "idea_id": research.idea_id,
            "campaign_id": research.campaign_id,
            "task_id": research.task_id,
            "keyword": research.keyword,
            "source": research.source,
            "geo": research.geo,
            "timeframe": research.timeframe,
            "trend_direction": research.trend_direction,
            "seasonality_risk": research.seasonality_risk,
            "evergreen_score": research.evergreen_score,
            "trend_stability_score": research.trend_stability_score,
            "spike_risk_score": research.spike_risk_score,
            "average_interest": float(research.average_interest) if research.average_interest is not None else None,
            "peak_interest": float(research.peak_interest) if research.peak_interest is not None else None,
            "low_interest": float(research.low_interest) if research.low_interest is not None else None,
            "trend_points": research.trend_points_json or [],
            "raw_json": research.raw_json or {},
            "verification_status": research.verification_status,
            "source_url": research.source_url,
            "screenshot_url": research.screenshot_url,
            "verification_notes": research.verification_notes,
            "created_by": research.created_by,
            "created_at": research.created_at,
            "updated_at": research.updated_at,
        }
