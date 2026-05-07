from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


SearchProvider = Literal["SEARXNG", "OPENSERP", "PLAYWRIGHT", "DATAFORSEO", "MANUAL"]
SearchIntent = Literal[
    "SOLD_EVIDENCE",
    "ACTIVE_LISTING",
    "SUPPLIER",
    "COMPETITOR",
    "COMPLAINT_RESEARCH",
    "KEYWORD_DEMAND",
    "GENERAL_RESEARCH",
]
ConversionStatus = Literal["NOT_CONVERTED", "CONVERTED_TO_CANDIDATE", "REJECTED"]
CandidateType = Literal["SOLD_LISTING", "ACTIVE_LISTING", "SUPPLIER_SOURCE", "COMPETITOR_LISTING", "COMPLAINT_NOTE", "KEYWORD_DEMAND_NOTE"]
ProviderStatusCode = Literal["OK", "ERROR", "DISABLED", "TIMEOUT"]


class ProviderStatus(BaseModel):
    provider: SearchProvider
    status: ProviderStatusCode
    message: str | None = None
    result_count: int = 0


class ResearchSearchRequest(BaseModel):
    query: str
    intent: SearchIntent
    providers: list[SearchProvider] = Field(default_factory=lambda: ["SEARXNG", "OPENSERP"])
    max_results: int = Field(default=10, ge=1, le=25)
    product_id: uuid.UUID | None = None
    idea_id: uuid.UUID | None = None
    campaign_id: uuid.UUID | None = None
    store_results: bool = True


class ResearchSearchResultResponse(BaseModel):
    id: uuid.UUID
    query: str
    provider: SearchProvider
    intent: SearchIntent
    title: str | None = None
    url: str
    snippet: str | None = None
    source_domain: str | None = None
    rank: int | None = None
    price_text: str | None = None
    currency: str | None = None
    fetched_at: datetime | None = None
    product_id: uuid.UUID | None = None
    idea_id: uuid.UUID | None = None
    campaign_id: uuid.UUID | None = None
    conversion_status: ConversionStatus | None = None
    converted_candidate_id: uuid.UUID | None = None

    class Config:
        from_attributes = True


class ResearchSearchResponse(BaseModel):
    query: str
    intent: SearchIntent
    requested_providers: list[SearchProvider]
    provider_statuses: list[ProviderStatus]
    result_count: int
    stored_count: int
    deduped_count: int
    results: list[ResearchSearchResultResponse]


class ConvertSearchResultToCandidateRequest(BaseModel):
    candidate_type: CandidateType
    product_id: uuid.UUID | None = None
    idea_id: uuid.UUID | None = None
    campaign_id: uuid.UUID | None = None
    notes: str | None = None
    price: float | None = None
    title_override: str | None = None


class ConvertSearchResultToCandidateResponse(BaseModel):
    search_result_id: uuid.UUID
    candidate_id: uuid.UUID
    verification_status: str
    status: str


class RejectSearchResultRequest(BaseModel):
    reject_reason: str


class RejectSearchResultResponse(BaseModel):
    id: uuid.UUID
    conversion_status: Literal["REJECTED"]
    reject_reason: str
