from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.schemas.external_research_schema import EvidenceCandidateResponse


CampaignStatus = str
CampaignTaskStatus = str


class DiscoveryCampaignCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=300)
    shop_concept_id: Optional[uuid.UUID] = None
    collection_id: Optional[uuid.UUID] = None
    category: Optional[str] = None
    goal: Optional[str] = None
    constraints_json: dict[str, Any] = Field(default_factory=dict)
    budget_limit_usd: float = 25.0
    max_ideas: int = 10
    max_products_to_promote: int = 3
    status: CampaignStatus = "DRAFT"
    created_by: Optional[str] = None


class DiscoveryCampaignUpdate(BaseModel):
    name: Optional[str] = None
    shop_concept_id: Optional[uuid.UUID] = None
    collection_id: Optional[uuid.UUID] = None
    category: Optional[str] = None
    goal: Optional[str] = None
    constraints_json: Optional[dict[str, Any]] = None
    budget_limit_usd: Optional[float] = None
    max_ideas: Optional[int] = None
    max_products_to_promote: Optional[int] = None
    status: Optional[CampaignStatus] = None
    created_by: Optional[str] = None


class DiscoveryCampaignResponse(BaseModel):
    id: uuid.UUID
    name: str
    shop_concept_id: Optional[uuid.UUID] = None
    collection_id: Optional[uuid.UUID] = None
    category: Optional[str] = None
    goal: Optional[str] = None
    constraints_json: dict[str, Any] = Field(default_factory=dict)
    budget_limit_usd: float = 0.0
    max_ideas: int = 0
    max_products_to_promote: int = 0
    status: CampaignStatus
    created_by: Optional[str] = None
    shop_concept_name: Optional[str] = None
    collection_name: Optional[str] = None
    report_generated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    idea_count: int = 0
    rejected_idea_count: int = 0
    promising_idea_count: int = 0
    promoted_product_count: int = 0
    dataforseo_spend_estimate: float = 0.0

    class Config:
        from_attributes = True


class DiscoveryCampaignTaskCreate(BaseModel):
    task_type: str = Field(..., min_length=1, max_length=80)
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    status: CampaignTaskStatus = "TODO"
    related_idea_id: Optional[uuid.UUID] = None
    related_product_id: Optional[uuid.UUID] = None
    related_candidate_id: Optional[uuid.UUID] = None
    result_json: Optional[dict[str, Any]] = None
    error_message: Optional[str] = None


class DiscoveryCampaignTaskUpdate(BaseModel):
    task_type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[CampaignTaskStatus] = None
    related_idea_id: Optional[uuid.UUID] = None
    related_product_id: Optional[uuid.UUID] = None
    related_candidate_id: Optional[uuid.UUID] = None
    result_json: Optional[dict[str, Any]] = None
    error_message: Optional[str] = None


class DiscoveryCampaignTaskResponse(BaseModel):
    id: uuid.UUID
    campaign_id: uuid.UUID
    task_type: str
    status: CampaignTaskStatus
    title: str
    description: Optional[str] = None
    related_idea_id: Optional[uuid.UUID] = None
    related_product_id: Optional[uuid.UUID] = None
    related_candidate_id: Optional[uuid.UUID] = None
    result_json: dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DiscoveryCampaignIdeaSummary(BaseModel):
    id: uuid.UUID
    idea_name: str
    category: Optional[str] = None
    shop_concept_id: Optional[uuid.UUID] = None
    collection_id: Optional[uuid.UUID] = None
    status: str
    quick_scan_verdict: Optional[str] = None
    buy_readiness_status: str = "NOT_READY"
    scout_status: Optional[str] = None
    scout_score: Optional[int] = None
    scout_confidence: Optional[str] = None
    scout_reason: Optional[str] = None
    scout_next_step: Optional[str] = None
    scout_metrics: Optional[object] = None
    opportunity_score: int = 0
    research_completeness_score: int = 0
    promoted_product_id: Optional[uuid.UUID] = None
    required_next_evidence: Optional[object] = None


class DiscoveryCampaignProductSummary(BaseModel):
    id: uuid.UUID
    name: str
    category: Optional[str] = None
    shop_concept_id: Optional[uuid.UUID] = None
    collection_id: Optional[uuid.UUID] = None
    status: str
    research_verdict: Optional[str] = None
    buy_readiness_status: Optional[str] = None
    final_decision: Optional[str] = None
    research_completeness_score: int = 0
    opportunity_score: int = 0
    next_action: Optional[str] = None
    main_blocker: Optional[str] = None


class DiscoveryCampaignReportResponse(BaseModel):
    campaign_id: uuid.UUID
    shop_concept_id: Optional[uuid.UUID] = None
    shop_concept_name: Optional[str] = None
    collection_id: Optional[uuid.UUID] = None
    collection_name: Optional[str] = None
    total_ideas: int
    rejected_ideas: int
    promising_ideas: int
    promoted_products: int
    dataforseo_spend_estimate: float
    budget_limit_usd: float
    spend_remaining: float | None = None
    budget_used_percent: float = 0.0
    ideas_by_verdict: dict[str, int] = Field(default_factory=dict)
    products_by_decision: dict[str, int] = Field(default_factory=dict)
    candidate_count_by_status: dict[str, int] = Field(default_factory=dict)
    ideas_with_keyword_demand: int = 0
    ideas_with_trend_research: int = 0
    products_with_keyword_demand: int = 0
    products_with_trend_research: int = 0
    products_with_evergreen_trend: int = 0
    products_with_weak_landed_cost_ratio: int = 0
    portfolio_items_total: int = 0
    portfolio_items_by_role: dict[str, int] = Field(default_factory=dict)
    portfolio_items_by_status: dict[str, int] = Field(default_factory=dict)
    portfolio_collection_gaps: list[str] = Field(default_factory=list)
    external_jobs_total: int = 0
    external_jobs_pending_count: int = 0
    external_jobs_imported_count: int = 0
    external_jobs_failed_count: int = 0
    latest_pending_job_id: str | None = None
    latest_pending_job_query: str | None = None
    latest_pending_job_status: str | None = None
    external_research_next_action: str | None = None
    watchlist_products: list[DiscoveryCampaignProductSummary] = Field(default_factory=list)
    skip_products: list[DiscoveryCampaignProductSummary] = Field(default_factory=list)
    ready_for_sample_products: list[DiscoveryCampaignProductSummary] = Field(default_factory=list)
    next_best_task: str | None = None
    top_ranked_ideas: list[DiscoveryCampaignIdeaSummary] = Field(default_factory=list)
    top_products: list[DiscoveryCampaignProductSummary] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)


class DiscoveryCampaignDetailResponse(BaseModel):
    campaign: DiscoveryCampaignResponse
    ideas: list[DiscoveryCampaignIdeaSummary] = Field(default_factory=list)
    tasks: list[DiscoveryCampaignTaskResponse] = Field(default_factory=list)
    report: DiscoveryCampaignReportResponse
    products: list[DiscoveryCampaignProductSummary] = Field(default_factory=list)
    evidence_candidates: list[EvidenceCandidateResponse] = Field(default_factory=list)
    tasks_by_status: dict[str, int] = Field(default_factory=dict)
