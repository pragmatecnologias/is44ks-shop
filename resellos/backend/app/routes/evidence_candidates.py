from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.external_research_schema import (
    EvidenceCandidateRejectRequest,
    EvidenceCandidateResponse,
    EvidenceCandidateReviewRequest,
    EvidenceCandidateReviewResponse,
)
from app.services.evidence_candidate_service import EvidenceCandidateService

router = APIRouter(prefix="/api/evidence-candidates", tags=["evidence-candidates"])


@router.get("", response_model=list[EvidenceCandidateResponse])
def list_candidates(
    idea_id: uuid.UUID | None = None,
    product_id: uuid.UUID | None = None,
    job_id: uuid.UUID | None = None,
    review_status: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    service = EvidenceCandidateService(db)
    return [EvidenceCandidateResponse.model_validate(service.serialize_candidate(candidate)) for candidate in service.list_candidates(idea_id=idea_id, product_id=product_id, job_id=job_id, review_status=review_status)]


@router.post("/{candidate_id}/approve", response_model=EvidenceCandidateReviewResponse)
def approve_candidate(candidate_id: uuid.UUID, request: EvidenceCandidateReviewRequest, db: Session = Depends(get_db)):
    service = EvidenceCandidateService(db)
    if not request.approve_as:
        raise HTTPException(status_code=400, detail="approve_as is required")
    return service.approve_candidate(candidate_id, request)


@router.post("/{candidate_id}/reject", response_model=EvidenceCandidateResponse)
def reject_candidate(candidate_id: uuid.UUID, request: EvidenceCandidateRejectRequest, db: Session = Depends(get_db)):
    service = EvidenceCandidateService(db)
    candidate = service.reject_candidate(candidate_id, request)
    return EvidenceCandidateResponse.model_validate(service.serialize_candidate(candidate))

