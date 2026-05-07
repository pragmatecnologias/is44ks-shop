from sqlalchemy.orm import Session
import uuid
from typing import Optional

from app.models.supplier import MarketplaceResearch, CompetitorListing, MarketplaceEvidence
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

    def delete_competitor_listing(self, competitor_id: uuid.UUID) -> bool:
        listing = self.db.query(CompetitorListing).filter(CompetitorListing.id == competitor_id).first()
        if not listing:
            return False
        self.db.delete(listing)
        self.db.commit()
        return True

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

    def verify_evidence(self, evidence_id: uuid.UUID, status: str, proof: dict | None = None) -> Optional[MarketplaceEvidence]:
        evidence = self.get_evidence_item(evidence_id)
        if not evidence:
            return None

        # Block USER_VERIFIED for SOLD_LISTING from local search without actual proof
        if status == "USER_VERIFIED" and evidence.evidence_type == "SOLD_LISTING":
            discovery_source = (proof or {}).get("discovery_source") or getattr(evidence, "discovery_source", None)
            proof_text = (proof or {}).get("proof_text") or ""
            manual_note = (proof or {}).get("manual_verification_note") or ""
            proof_url = (proof or {}).get("proof_url") or ""
            screenshot_path = (proof or {}).get("proof_screenshot_path") or ""
            original_intent = (proof or {}).get("original_search_intent") or getattr(evidence, "original_search_intent", None)

            is_local_search = discovery_source in ("SEARXNG", "OPENSERP")

            # Rule: ACTIVE_LISTING intent cannot become USER_VERIFIED SOLD_LISTING
            if original_intent == "ACTIVE_LISTING":
                raise ValueError(
                    "Cannot mark ACTIVE_LISTING intent result as USER_VERIFIED SOLD_LISTING. "
                    "This evidence was gathered with ACTIVE_LISTING intent, not sold/completed proof."
                )

            if is_local_search:
                has_proof = bool(proof_text.strip() or manual_note.strip() or proof_url or screenshot_path)
                if not has_proof:
                    raise ValueError(
                        "Cannot mark local-search result as USER_VERIFIED without sold/completed proof. "
                        "Provide proof_text, manual_verification_note, proof_url, or proof_screenshot_path."
                    )

        evidence.verification_status = status
        self.db.commit()
        self.db.refresh(evidence)
        return evidence

    def verify_competitor(self, competitor_id: uuid.UUID, status: str) -> Optional[CompetitorListing]:
        listing = self.db.query(CompetitorListing).filter(CompetitorListing.id == competitor_id).first()
        if not listing:
            return None
        listing.verification_status = status
        self.db.commit()
        self.db.refresh(listing)
        return listing

    def verify_source(self, source_id: uuid.UUID, status: str):
        from app.models.supplier import ProductSource
        source = self.db.query(ProductSource).filter(ProductSource.id == source_id).first()
        if not source:
            return None
        source.verification_status = status
        self.db.commit()
        self.db.refresh(source)
        return source

    def cleanup_evidence(
        self,
        product_id: uuid.UUID | None = None,
        verification_status: str | None = None,
        dry_run: bool = True,
    ) -> dict:
        from app.models.supplier import MarketplaceEvidence, CompetitorListing, ProductSource

        affected: dict[str, int] = {"evidence": 0, "competitors": 0, "sources": 0}
        actions: list[dict] = []

        # Evidence
        q = self.db.query(MarketplaceEvidence)
        if product_id:
            q = q.filter(MarketplaceEvidence.product_id == product_id)
        if verification_status:
            q = q.filter(MarketplaceEvidence.verification_status == verification_status)
        evidence_rows = q.all()
        affected["evidence"] = len(evidence_rows)
        for row in evidence_rows:
            actions.append({"type": "evidence", "id": str(row.id), "marketplace": row.marketplace, "status": row.verification_status})
            if not dry_run:
                self.db.delete(row)

        # Competitors
        qc = self.db.query(CompetitorListing)
        if product_id:
            qc = qc.filter(CompetitorListing.product_id == product_id)
        if verification_status:
            qc = qc.filter(CompetitorListing.verification_status == verification_status)
        comp_rows = qc.all()
        affected["competitors"] = len(comp_rows)
        for row in comp_rows:
            actions.append({"type": "competitor", "id": str(row.id), "marketplace": row.marketplace, "status": row.verification_status})
            if not dry_run:
                self.db.delete(row)

        # Sources
        qs = self.db.query(ProductSource)
        if product_id:
            qs = qs.filter(ProductSource.product_id == product_id)
        if verification_status:
            qs = qs.filter(ProductSource.verification_status == verification_status)
        src_rows = qs.all()
        affected["sources"] = len(src_rows)
        for row in src_rows:
            actions.append({"type": "source", "id": str(row.id), "supplier": row.supplier_name, "status": row.verification_status})
            if not dry_run:
                self.db.delete(row)

        if not dry_run:
            self.db.commit()

        return {"dry_run": dry_run, "affected_counts": affected, "actions": actions}
