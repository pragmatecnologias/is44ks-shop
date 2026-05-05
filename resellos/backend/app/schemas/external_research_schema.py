from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


EvidenceCandidateSource = Literal["DATAFORSEO", "MANUAL_CAPTURE", "VISION"]
EvidenceCandidateType = Literal["MARKETPLACE_EVIDENCE", "COMPETITOR_LISTING", "SUPPLIER_SOURCE", "RISK_FLAG"]
EvidenceReviewStatus = Literal["PENDING", "APPROVED", "REJECTED", "IGNORED"]
EvidenceApproveAs = Literal["MARKETPLACE_EVIDENCE", "COMPETITOR_LISTING", "SUPPLIER_SOURCE"]
ExternalResearchQueue = Literal["standard", "priority"]
ExternalResearchStatus = Literal["QUEUED", "SUBMITTED", "READY", "FAILED", "IMPORTED"]


class ExternalResearchRunRequest(BaseModel):
    idea_id: uuid.UUID | None = None
    product_id: uuid.UUID | None = None
    queries: list[str] = Field(default_factory=list)
    max_results: int = 20
    queue: ExternalResearchQueue = "standard"
    budget_override: bool = False


class ExternalResearchJobResponse(BaseModel):
    id: uuid.UUID
    idea_id: uuid.UUID | None = None
    product_id: uuid.UUID | None = None
    provider: str
    api_area: str
    query: str
    queue: ExternalResearchQueue
    status: ExternalResearchStatus
    provider_task_id: str | None = None
    cost_estimate: float | None = None
    result_count: int = 0
    raw_request: dict[str, Any] = Field(default_factory=dict)
    raw_response: dict[str, Any] = Field(default_factory=dict)
    last_error: str | None = None
    candidate_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EvidenceCandidateResponse(BaseModel):
    id: uuid.UUID
    job_id: uuid.UUID | None = None
    idea_id: uuid.UUID | None = None
    product_id: uuid.UUID | None = None
    source: EvidenceCandidateSource
    candidate_type: EvidenceCandidateType
    marketplace: str | None = None
    evidence_type: str | None = None
    title: str | None = None
    url: str | None = None
    price: float | None = None
    shipping_price: float | None = None
    seller: str | None = None
    rating: float | None = None
    review_count: int | None = None
    image_url: str | None = None
    confidence: str = "MEDIUM"
    review_status: EvidenceReviewStatus = "PENDING"
    raw_json: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

    class Config:
        from_attributes = True


class EvidenceCandidateReviewRequest(BaseModel):
    approve_as: EvidenceApproveAs | None = None
    task_id: uuid.UUID | None = None
    product_id: uuid.UUID | None = None
    notes: str | None = None


class EvidenceCandidateRejectRequest(BaseModel):
    notes: str | None = None


class EvidenceCandidateReviewResponse(BaseModel):
    candidate: EvidenceCandidateResponse
    created_object_type: str | None = None
    created_object_id: uuid.UUID | None = None
    linked_task_id: uuid.UUID | None = None


class ManualCaptureResponse(BaseModel):
    candidate: EvidenceCandidateResponse
    vision_report_id: uuid.UUID | None = None


class ExternalResearchRunResponse(BaseModel):
    jobs: list[ExternalResearchJobResponse] = Field(default_factory=list)
    estimated_cost: float = 0.0
    budget_warning: str | None = None


class ExternalResearchJobDetailResponse(BaseModel):
    job: ExternalResearchJobResponse
    candidates: list[EvidenceCandidateResponse] = Field(default_factory=list)
