from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.external_research_schema import (
    ExternalResearchJobDetailResponse,
    ExternalResearchJobResponse,
    ExternalResearchRunRequest,
    ExternalResearchRunResponse,
)
from app.services.external_research_service import ExternalResearchService

router = APIRouter(prefix="/api/external-research", tags=["external-research"])


@router.post("/google-shopping", response_model=ExternalResearchRunResponse)
@router.post("/dataforseo/google-shopping", response_model=ExternalResearchRunResponse)
def run_google_shopping(request: ExternalResearchRunRequest, db: Session = Depends(get_db)):
    service = ExternalResearchService(db)
    if request.idea_id:
        return service.run_google_shopping_for_idea(request)
    if request.product_id:
        return service.run_google_shopping_for_product(request)
    raise HTTPException(status_code=400, detail="Provide either idea_id or product_id.")


@router.get("/jobs", response_model=list[ExternalResearchJobResponse])
def list_jobs(
    idea_id: uuid.UUID | None = None,
    product_id: uuid.UUID | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    service = ExternalResearchService(db)
    return [ExternalResearchJobResponse.model_validate(service._serialize_job(job)) for job in service.list_jobs(idea_id=idea_id, product_id=product_id, status=status)]


@router.get("/jobs/{job_id}", response_model=ExternalResearchJobDetailResponse)
def get_job(job_id: uuid.UUID, db: Session = Depends(get_db)):
    service = ExternalResearchService(db)
    job = service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="External research job not found")
    return ExternalResearchJobDetailResponse(
        job=ExternalResearchJobResponse.model_validate(service._serialize_job(job)),
        candidates=[service._serialize_candidate(candidate) for candidate in service.list_candidates(job_id=job_id)],
    )


@router.post("/jobs/{job_id}/poll", response_model=ExternalResearchJobDetailResponse)
def poll_job(job_id: uuid.UUID, db: Session = Depends(get_db)):
    service = ExternalResearchService(db)
    job = service.poll_job(job_id)
    return ExternalResearchJobDetailResponse(
        job=ExternalResearchJobResponse.model_validate(service._serialize_job(job)),
        candidates=[service._serialize_candidate(candidate) for candidate in service.list_candidates(job_id=job_id)],
    )

