from sqlalchemy.orm import Session
import uuid
from typing import Optional

from app.models.marketplace import MarketplaceResearch, CompetitorListing, MarketplaceEvidence
from app.schemas.product_schema import MarketplaceResearchCreate, MarketplaceEvidenceCreate, MarketplaceEvidenceUpdate


class MarketplaceService:
    def __init__(self, db: Session):
        self.db = db

    def create_research(self, product_id: uuid.UUID, data: MarketplaceResearchCreate) -> MarketplaceResearch:
        research = MarketplaceResearch(
            product_id=product_id,
            marketplace=data.marketplace,
            keyword=data.keyword,
            search_url=data.search_url,
            active_listing_count=data.active_listing_count,
            sold_listing_count=data.sold_listing_count,
            min_active_price=data.min_active_price,
            median_active_price=data.median_active_price,
            max_active_price=data.max_active_price,
            min_sold_price=data.min_sold_price,
            median_sold_price=data.median_sold_price,
            max_sold_price=data.max_sold_price,
            shipping_min=data.shipping_min,
            shipping_median=data.shipping_median,
            shipping_max=data.shipping_max,
            competition_level=data.competition_level,
            demand_signal=data.demand_signal,
            evidence_quality=data.evidence_quality,
            notes=data.notes,
        )
        self.db.add(research)
        self.db.commit()
        self.db.refresh(research)
        return research

    def get_research(self, product_id: uuid.UUID) -> list[MarketplaceResearch]:
        return self.db.query(MarketplaceResearch).filter(MarketplaceResearch.product_id == product_id).all()

    def update_research(self, research_id: uuid.UUID, data: MarketplaceResearchCreate) -> Optional[MarketplaceResearch]:
        research = self.db.query(MarketplaceResearch).filter(MarketplaceResearch.id == research_id).first()
        if not research:
            return None
        update = data.model_dump(exclude_unset=True)
        for key, value in update.items():
            setattr(research, key, value)
        self.db.commit()
        self.db.refresh(research)
        return research

    def delete_research(self, research_id: uuid.UUID) -> bool:
        research = self.db.query(MarketplaceResearch).filter(MarketplaceResearch.id == research_id).first()
        if not research:
            return False
        self.db.delete(research)
        self.db.commit()
        return True

    def create_competitor_listing(self, product_id: uuid.UUID, data) -> CompetitorListing:
        listing = CompetitorListing(
            product_id=product_id,
            marketplace=data.marketplace,
            title=data.title,
            url=data.url,
            price=data.price,
            shipping_price=data.shipping_price,
            condition=data.condition,
            seller_name=data.seller_name,
            sold=data.sold,
            photo_score=data.photo_score,
            title_score=data.title_score,
            description_score=data.description_score,
            notes=data.notes,
        )
        self.db.add(listing)
        self.db.commit()
        self.db.refresh(listing)
        return listing

    def get_competitor_listings(self, product_id: uuid.UUID) -> list[CompetitorListing]:
        return self.db.query(CompetitorListing).filter(CompetitorListing.product_id == product_id).all()

    def create_evidence(self, product_id: uuid.UUID, data: MarketplaceEvidenceCreate) -> MarketplaceEvidence:
        evidence = MarketplaceEvidence(
            product_id=product_id,
            marketplace=data.marketplace,
            evidence_type=data.evidence_type,
            title=data.title,
            url=data.url,
            price=data.price,
            shipping_price=data.shipping_price,
            sold_date=data.sold_date,
            condition=data.condition,
            seller_name=data.seller_name,
            source_method=data.source_method,
            raw_text=data.raw_text,
            screenshot_url=data.screenshot_url,
            confidence=data.confidence,
            notes=data.notes,
        )
        self.db.add(evidence)
        self.db.commit()
        self.db.refresh(evidence)
        return evidence

    def get_evidence(self, product_id: uuid.UUID) -> list[MarketplaceEvidence]:
        return self.db.query(MarketplaceEvidence).filter(MarketplaceEvidence.product_id == product_id).all()

    def get_evidence_item(self, evidence_id: uuid.UUID) -> Optional[MarketplaceEvidence]:
        return self.db.query(MarketplaceEvidence).filter(MarketplaceEvidence.id == evidence_id).first()

    def update_evidence(self, evidence_id: uuid.UUID, data: MarketplaceEvidenceUpdate) -> Optional[MarketplaceEvidence]:
        evidence = self.get_evidence_item(evidence_id)
        if not evidence:
            return None
        update = data.model_dump(exclude_unset=True)
        for key, value in update.items():
            setattr(evidence, key, value)
        self.db.commit()
        self.db.refresh(evidence)
        return evidence

    def delete_evidence(self, evidence_id: uuid.UUID) -> bool:
        evidence = self.get_evidence_item(evidence_id)
        if not evidence:
            return False
        self.db.delete(evidence)
        self.db.commit()
        return True
