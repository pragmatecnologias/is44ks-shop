from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.campaign import DiscoveryCampaignTask
from app.models.supplier import AgentReport
from app.models.product_validation import ProductDemandResearch
from app.models.supplier import ProductIdea
from app.schemas.validation_schema import ProductDemandResearchCreate, ProductDemandResearchVerifyRequest


def score_search_volume(volume: int | None) -> int:
    if volume is None:
        return 0
    if volume >= 5000:
        return 100
    if volume >= 1000:
        return 80
    if volume >= 300:
        return 60
    if volume >= 100:
        return 35
    return 10


def score_keyword_specificity(keyword: str, *, product_name: str | None = None, category: str | None = None) -> int:
    text = keyword.lower().strip()
    product = (product_name or "").lower().strip()
    category_text = (category or "").lower().strip()
    score = 20
    if product and product in text:
        score += 50
    if category_text and category_text in text:
        score += 20
    if any(token in text for token in ["for dogs", "for cats", "pet hair remover", "cat litter", "waste bag", "feeding mat", "travel bottle"]):
        score += 20
    if len(text.split()) >= 3:
        score += 10
    return max(0, min(100, score))


def score_buyer_intent(keyword: str, *, product_name: str | None = None, category: str | None = None) -> int:
    text = keyword.lower().strip()
    score = 20
    if product_name and product_name.lower().strip() in text:
        score += 45
    if category and category.lower().strip() in text:
        score += 15
    if any(token in text for token in ["buy", "best", "review", "cheap", "replacement", "for dogs", "for cats"]):
        score += 10
    if "pet" in text:
        score += 10
    return max(0, min(100, score))


class DemandResearchService:
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
    ) -> list[ProductDemandResearch]:
        query = self.db.query(ProductDemandResearch)
        if product_id is not None:
            query = query.filter(ProductDemandResearch.product_id == product_id)
        if idea_id is not None:
            query = query.filter(ProductDemandResearch.idea_id == idea_id)
        if campaign_id is not None:
            query = query.filter(ProductDemandResearch.campaign_id == campaign_id)
        if verification_status:
            query = query.filter(ProductDemandResearch.verification_status == verification_status)
        return query.order_by(ProductDemandResearch.updated_at.desc(), ProductDemandResearch.created_at.desc()).all()

    def get_research(self, research_id: uuid.UUID) -> ProductDemandResearch | None:
        return self.db.query(ProductDemandResearch).filter(ProductDemandResearch.id == research_id).first()

    def create_research(self, data: ProductDemandResearchCreate) -> ProductDemandResearch:
        product_name = None
        product_category = None
        if data.product_id:
            from app.models.product import Product

            product_obj = self.db.query(Product).filter(Product.id == data.product_id).first()
            product_name = product_obj.name if product_obj else None
            product_category = product_obj.category if product_obj else None
        if data.demand_score and data.demand_score > 0:
            demand_score = int(data.demand_score)
        else:
            demand_score = min(
                100,
                score_search_volume(data.monthly_search_volume)
                + score_buyer_intent(data.keyword, product_name=product_name, category=None) // 3
                + score_keyword_specificity(data.keyword, product_name=product_name, category=None) // 3,
            )
        campaign_id = self._resolve_campaign_id(
            product_id=data.product_id,
            idea_id=data.idea_id,
            campaign_id=data.campaign_id,
            task_id=getattr(data, "task_id", None),
        )
        research = ProductDemandResearch(
            product_id=data.product_id,
            idea_id=data.idea_id,
            campaign_id=campaign_id,
            task_id=getattr(data, "task_id", None),
            keyword=data.keyword,
            source=data.source,
            target_country=data.target_country,
            target_language=data.target_language,
            monthly_search_volume=data.monthly_search_volume,
            monthly_search_volume_min=data.monthly_search_volume_min,
            monthly_search_volume_max=data.monthly_search_volume_max,
            competition_level=data.competition_level,
            cpc_low=data.cpc_low,
            cpc_high=data.cpc_high,
            currency=data.currency,
            buyer_intent_score=data.buyer_intent_score or score_buyer_intent(data.keyword, product_name=product_name, category=product_category),
            keyword_specificity_score=data.keyword_specificity_score or score_keyword_specificity(data.keyword, product_name=product_name, category=product_category),
            demand_score=demand_score,
            related_keywords_json=data.related_keywords or [],
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

    def verify_research(self, research_id: uuid.UUID, data: ProductDemandResearchVerifyRequest) -> ProductDemandResearch:
        research = self.get_research(research_id)
        if not research:
            raise HTTPException(status_code=404, detail="Keyword demand record not found")
        if data.verification_status == "USER_VERIFIED" and not (data.source_url or data.screenshot_url or data.verification_notes):
            raise HTTPException(status_code=400, detail="Keyword demand verification requires proof.")
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

    def to_dict(self, research: ProductDemandResearch) -> dict[str, Any]:
        return {
            "id": research.id,
            "product_id": research.product_id,
            "idea_id": research.idea_id,
            "campaign_id": research.campaign_id,
            "task_id": research.task_id,
            "keyword": research.keyword,
            "source": research.source,
            "target_country": research.target_country,
            "target_language": research.target_language,
            "monthly_search_volume": research.monthly_search_volume,
            "monthly_search_volume_min": research.monthly_search_volume_min,
            "monthly_search_volume_max": research.monthly_search_volume_max,
            "competition_level": research.competition_level,
            "cpc_low": float(research.cpc_low) if research.cpc_low is not None else None,
            "cpc_high": float(research.cpc_high) if research.cpc_high is not None else None,
            "currency": research.currency,
            "buyer_intent_score": research.buyer_intent_score,
            "keyword_specificity_score": research.keyword_specificity_score,
            "demand_score": research.demand_score,
            "related_keywords": research.related_keywords_json or [],
            "raw_json": research.raw_json or {},
            "verification_status": research.verification_status,
            "source_url": research.source_url,
            "screenshot_url": research.screenshot_url,
            "verification_notes": research.verification_notes,
            "created_by": research.created_by,
            "created_at": research.created_at,
            "updated_at": research.updated_at,
        }
