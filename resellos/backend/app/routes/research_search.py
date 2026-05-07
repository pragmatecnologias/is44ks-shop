from __future__ import annotations

import uuid
from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.research_search_schema import (
    ConvertSearchResultToCandidateRequest,
    ConvertSearchResultToCandidateResponse,
    RejectSearchResultRequest,
    RejectSearchResultResponse,
    ResearchSearchRequest,
    ResearchSearchResponse,
    ResearchSearchResultResponse,
)
from app.services.research_search_broker import ResearchSearchBroker

router = APIRouter(prefix="/api/research", tags=["research-search"])


@router.post("/search", response_model=ResearchSearchResponse)
def search(
    request: ResearchSearchRequest,
    db: Session = Depends(get_db),
):
    broker = ResearchSearchBroker(db)
    return broker.search(request)


@router.get("/search-results", response_model=list[ResearchSearchResultResponse])
def list_search_results(
    product_id: uuid.UUID | None = None,
    idea_id: uuid.UUID | None = None,
    campaign_id: uuid.UUID | None = None,
    intent: str | None = Query(default=None),
    provider: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    broker = ResearchSearchBroker(db)
    results = broker.list_results(
        product_id=product_id,
        idea_id=idea_id,
        campaign_id=campaign_id,
        intent=intent,
        provider=provider,
        limit=limit,
        offset=offset,
    )
    return [
        ResearchSearchResultResponse(
            id=r.id,
            query=r.query,
            provider=r.provider,
            intent=r.intent,
            title=r.title,
            url=r.url,
            snippet=r.snippet,
            source_domain=r.source_domain,
            rank=r.rank,
            price_text=r.price_text,
            currency=r.currency,
            fetched_at=r.fetched_at,
            product_id=r.product_id,
            idea_id=r.idea_id,
            campaign_id=r.campaign_id,
            conversion_status=r.conversion_status,
            converted_candidate_id=r.converted_candidate_id,
        )
        for r in results
    ]


@router.post("/search-results/{result_id}/candidate", response_model=ConvertSearchResultToCandidateResponse)
def convert_search_result_to_candidate(
    result_id: uuid.UUID,
    request: ConvertSearchResultToCandidateRequest,
    db: Session = Depends(get_db),
):
    broker = ResearchSearchBroker(db)
    result = broker.convert_to_candidate(result_id, request)
    if not result:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Search result not found")
    return result


@router.patch("/search-results/{result_id}/reject", response_model=RejectSearchResultResponse)
def reject_search_result(
    result_id: uuid.UUID,
    request: RejectSearchResultRequest,
    db: Session = Depends(get_db),
):
    broker = ResearchSearchBroker(db)
    result = broker.reject_result(result_id, request.reject_reason)
    if not result:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Search result not found")
    return RejectSearchResultResponse(
        id=result.id,
        conversion_status="REJECTED",
        reject_reason=result.reject_reason or "",
    )