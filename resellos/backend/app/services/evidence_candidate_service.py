from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.external_research import EvidenceCandidate
from app.models.product import Product
from app.models.supplier import CompetitorListing, DiscoveryTask, MarketplaceEvidence, ProductSource
from app.schemas.external_research_schema import (
    EvidenceCandidateRejectRequest,
    EvidenceCandidateReviewRequest,
    EvidenceCandidateReviewResponse,
)


def _json_load(value: Any, default: Any) -> Any:
    if value is None:
        return default
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return default
    return default


def _candidate_payload(candidate: EvidenceCandidate) -> dict[str, Any]:
    raw_json = _json_load(candidate.raw_json, {})
    return {
        "id": candidate.id,
        "job_id": candidate.job_id,
        "idea_id": candidate.idea_id,
        "product_id": candidate.product_id,
        "source": candidate.source,
        "candidate_type": candidate.candidate_type,
        "marketplace": candidate.marketplace,
        "evidence_type": candidate.evidence_type,
        "title": candidate.title,
        "url": candidate.url,
        "price": float(candidate.price) if candidate.price is not None else None,
        "shipping_price": float(candidate.shipping_price) if candidate.shipping_price is not None else None,
        "seller": candidate.seller,
        "rating": float(candidate.rating) if candidate.rating is not None else None,
        "review_count": candidate.review_count,
        "image_url": candidate.image_url,
        "confidence": candidate.confidence,
        "review_status": candidate.review_status,
        "raw_json": raw_json,
        "created_at": candidate.created_at or datetime.utcnow(),
    }


class EvidenceCandidateService:
    def __init__(self, db: Session):
        self.db = db

    def list_candidates(
        self,
        *,
        idea_id: uuid.UUID | None = None,
        product_id: uuid.UUID | None = None,
        job_id: uuid.UUID | None = None,
        review_status: str | None = None,
    ) -> list[EvidenceCandidate]:
        query = self.db.query(EvidenceCandidate)
        if idea_id is not None:
            query = query.filter(EvidenceCandidate.idea_id == idea_id)
        if product_id is not None:
            query = query.filter(EvidenceCandidate.product_id == product_id)
        if job_id is not None:
            query = query.filter(EvidenceCandidate.job_id == job_id)
        if review_status:
            query = query.filter(EvidenceCandidate.review_status == review_status)
        return query.order_by(EvidenceCandidate.created_at.desc()).all()

    def get_candidate(self, candidate_id: uuid.UUID) -> EvidenceCandidate | None:
        return self.db.query(EvidenceCandidate).filter(EvidenceCandidate.id == candidate_id).first()

    def serialize_candidate(self, candidate: EvidenceCandidate) -> dict[str, Any]:
        return _candidate_payload(candidate)

    def reject_candidate(
        self,
        candidate_id: uuid.UUID,
        data: EvidenceCandidateRejectRequest | None = None,
    ) -> EvidenceCandidate:
        candidate = self.get_candidate(candidate_id)
        if not candidate:
            raise HTTPException(status_code=404, detail="Evidence candidate not found")
        candidate.review_status = "REJECTED"
        raw_json = _json_load(candidate.raw_json, {})
        raw_json["review_notes"] = data.notes if data and data.notes else raw_json.get("review_notes")
        candidate.raw_json = raw_json
        self.db.commit()
        self.db.refresh(candidate)
        return candidate

    def approve_candidate(
        self,
        candidate_id: uuid.UUID,
        data: EvidenceCandidateReviewRequest,
    ) -> EvidenceCandidateReviewResponse:
        candidate = self.get_candidate(candidate_id)
        if not candidate:
            raise HTTPException(status_code=404, detail="Evidence candidate not found")

        product_id = data.product_id or candidate.product_id or self._resolve_product_from_idea(candidate.idea_id)
        if not product_id:
            raise HTTPException(
                status_code=400,
                detail="A promoted product is required before approving this candidate.",
            )

        created_object_type: str | None = None
        created_object_id: uuid.UUID | None = None

        # Map candidate source to initial verification status
        _source = str(candidate.source or "").upper()
        if _source == "DATAFORSEO":
            initial_verification = "API_IMPORTED"
        elif _source in {"MANUAL_CAPTURE", "VISION"}:
            initial_verification = "USER_CAPTURED_UNVERIFIED"
        else:
            initial_verification = "AI_EXTRACTED_UNVERIFIED"

        if data.approve_as == "MARKETPLACE_EVIDENCE":
            created = MarketplaceEvidence(
                product_id=product_id,
                marketplace=candidate.marketplace or "Google Shopping",
                evidence_type=candidate.evidence_type or "ACTIVE_LISTING",
                title=candidate.title,
                url=candidate.url,
                price=candidate.price,
                shipping_price=candidate.shipping_price,
                condition=_json_load(candidate.raw_json, {}).get("condition"),
                seller_name=candidate.seller,
                source_method=candidate.source,
                verification_status=initial_verification,
                raw_text=json.dumps(_json_load(candidate.raw_json, {}), ensure_ascii=False, default=str),
                screenshot_url=candidate.image_url,
                confidence=candidate.confidence,
                notes=data.notes,
            )
            self.db.add(created)
            self.db.flush()
            created_object_type = "marketplace_evidence"
            created_object_id = created.id
        elif data.approve_as == "COMPETITOR_LISTING":
            created = CompetitorListing(
                product_id=product_id,
                marketplace=candidate.marketplace or "Google Shopping",
                title=candidate.title,
                url=candidate.url,
                price=candidate.price,
                shipping_price=candidate.shipping_price,
                condition=_json_load(candidate.raw_json, {}).get("condition"),
                seller_name=candidate.seller,
                sold=candidate.evidence_type == "SOLD_LISTING",
                verification_status=initial_verification,
                notes=data.notes or candidate.source,
            )
            self.db.add(created)
            self.db.flush()
            created_object_type = "competitor_listing"
            created_object_id = created.id
        elif data.approve_as == "SUPPLIER_SOURCE":
            raw = _json_load(candidate.raw_json, {})
            created = ProductSource(
                product_id=product_id,
                supplier_name=raw.get("supplier_name") or candidate.seller or candidate.marketplace,
                supplier_platform=raw.get("supplier_platform") or candidate.marketplace or candidate.source,
                supplier_url=candidate.url,
                unit_cost=candidate.price,
                estimated_landed_cost=raw.get("estimated_landed_cost"),
                moq=raw.get("moq"),
                verification_status=initial_verification,
                notes=data.notes or raw.get("shipping_notes"),
                is_primary=False,
            )
            self.db.add(created)
            self.db.flush()
            created_object_type = "supplier_source"
            created_object_id = created.id
        else:
            raise HTTPException(status_code=400, detail="Unsupported approval target")

        candidate.review_status = "APPROVED"
        candidate.product_id = product_id
        raw_json = _json_load(candidate.raw_json, {})
        raw_json["approval"] = {
            "approve_as": data.approve_as,
            "created_object_type": created_object_type,
            "created_object_id": str(created_object_id) if created_object_id else None,
            "notes": data.notes,
        }
        candidate.raw_json = raw_json

        if data.task_id:
            task = self.db.query(DiscoveryTask).filter(DiscoveryTask.id == data.task_id).first()
            if task:
                task.linked_evidence_id = created_object_id if data.approve_as == "MARKETPLACE_EVIDENCE" else None
                task.linked_source_id = created_object_id if data.approve_as == "SUPPLIER_SOURCE" else None
                task.linked_competitor_id = created_object_id if data.approve_as == "COMPETITOR_LISTING" else None
                task.linked_product_id = product_id

        self.db.commit()
        self.db.refresh(candidate)
        return EvidenceCandidateReviewResponse(
            candidate=_candidate_payload(candidate),
            created_object_type=created_object_type,
            created_object_id=created_object_id,
            linked_task_id=data.task_id,
        )

    def _resolve_product_from_idea(self, idea_id: uuid.UUID | None) -> uuid.UUID | None:
        if not idea_id:
            return None
        from app.models.supplier import ProductIdea

        idea = self.db.query(ProductIdea).filter(ProductIdea.id == idea_id).first()
        if not idea:
            return None
        return idea.promoted_product_id
