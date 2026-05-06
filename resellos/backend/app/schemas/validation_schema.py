from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
import uuid

from pydantic import BaseModel, Field


ValidationStatus = Literal["PASS", "FAIL", "WARNING", "UNKNOWN"]
ValidationReadiness = Literal["INCOMPLETE", "WEAK", "WATCHLIST", "READY_FOR_SAMPLE"]


class ValidationCheck(BaseModel):
    status: ValidationStatus = "UNKNOWN"
    score: int = 0
    summary: str = ""
    next_action: str | None = None


class ProductDemandResearchCreate(BaseModel):
    product_id: uuid.UUID | None = None
    idea_id: uuid.UUID | None = None
    campaign_id: uuid.UUID | None = None
    task_id: uuid.UUID | None = None
    keyword: str
    source: str = "MANUAL_CAPTURE"
    target_country: str = "US"
    target_language: str = "en"
    monthly_search_volume: int | None = None
    monthly_search_volume_min: int | None = None
    monthly_search_volume_max: int | None = None
    competition_level: str | None = None
    cpc_low: float | None = None
    cpc_high: float | None = None
    currency: str = "USD"
    buyer_intent_score: int = 0
    keyword_specificity_score: int = 0
    demand_score: int = 0
    related_keywords: list[dict[str, Any]] = Field(default_factory=list)
    raw_json: dict[str, Any] = Field(default_factory=dict)
    verification_status: str = "USER_CAPTURED_UNVERIFIED"
    source_url: str | None = None
    screenshot_url: str | None = None
    verification_notes: str | None = None
    created_by: str | None = None


class ProductDemandResearchVerifyRequest(BaseModel):
    verification_status: Literal["USER_VERIFIED", "USER_CAPTURED_UNVERIFIED"] = "USER_VERIFIED"
    source_url: str | None = None
    screenshot_url: str | None = None
    verification_notes: str | None = None
    confirm: bool | None = None


class ProductDemandResearchResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID | None = None
    idea_id: uuid.UUID | None = None
    campaign_id: uuid.UUID | None = None
    task_id: uuid.UUID | None = None
    keyword: str
    source: str
    target_country: str
    target_language: str
    monthly_search_volume: int | None = None
    monthly_search_volume_min: int | None = None
    monthly_search_volume_max: int | None = None
    competition_level: str | None = None
    cpc_low: float | None = None
    cpc_high: float | None = None
    currency: str
    buyer_intent_score: int
    keyword_specificity_score: int
    demand_score: int
    related_keywords: list[dict[str, Any]] = Field(default_factory=list)
    raw_json: dict[str, Any] = Field(default_factory=dict)
    verification_status: str
    source_url: str | None = None
    screenshot_url: str | None = None
    verification_notes: str | None = None
    created_by: str | None = None
    created_at: datetime
    updated_at: datetime


class ProductTrendResearchCreate(BaseModel):
    product_id: uuid.UUID | None = None
    idea_id: uuid.UUID | None = None
    campaign_id: uuid.UUID | None = None
    task_id: uuid.UUID | None = None
    keyword: str
    source: str = "MANUAL_CAPTURE"
    geo: str = "US"
    timeframe: str = "past_5_years"
    trend_direction: str | None = None
    seasonality_risk: str | None = None
    evergreen_score: int = 0
    trend_stability_score: int = 0
    spike_risk_score: int = 0
    average_interest: float | None = None
    peak_interest: float | None = None
    low_interest: float | None = None
    trend_points: list[dict[str, Any]] = Field(default_factory=list)
    raw_json: dict[str, Any] = Field(default_factory=dict)
    verification_status: str = "USER_CAPTURED_UNVERIFIED"
    source_url: str | None = None
    screenshot_url: str | None = None
    verification_notes: str | None = None
    created_by: str | None = None


class ProductTrendResearchVerifyRequest(BaseModel):
    verification_status: Literal["USER_VERIFIED", "USER_CAPTURED_UNVERIFIED"] = "USER_VERIFIED"
    source_url: str | None = None
    screenshot_url: str | None = None
    verification_notes: str | None = None
    confirm: bool | None = None


class ProductTrendResearchResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID | None = None
    idea_id: uuid.UUID | None = None
    campaign_id: uuid.UUID | None = None
    task_id: uuid.UUID | None = None
    keyword: str
    source: str
    geo: str
    timeframe: str
    trend_direction: str | None = None
    seasonality_risk: str | None = None
    evergreen_score: int
    trend_stability_score: int
    spike_risk_score: int
    average_interest: float | None = None
    peak_interest: float | None = None
    low_interest: float | None = None
    trend_points: list[dict[str, Any]] = Field(default_factory=list)
    raw_json: dict[str, Any] = Field(default_factory=dict)
    verification_status: str
    source_url: str | None = None
    screenshot_url: str | None = None
    verification_notes: str | None = None
    created_by: str | None = None
    created_at: datetime
    updated_at: datetime


class ProductValidationSummaryResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    market_presence_status: str | None = None
    search_demand_status: str | None = None
    sold_demand_status: str | None = None
    trend_status: str | None = None
    supplier_economics_status: str | None = None
    competition_status: str | None = None
    risk_status: str | None = None
    market_presence_score: int = 0
    search_demand_score: int = 0
    sold_demand_score: int = 0
    trend_score: int = 0
    supplier_economics_score: int = 0
    competition_score: int = 0
    risk_score: int = 0
    overall_validation_score: int = 0
    validation_readiness: ValidationReadiness = "INCOMPLETE"
    main_validation_blocker: str | None = None
    next_validation_action: str | None = None
    created_at: datetime
    updated_at: datetime


class ValidationChecklistResponse(BaseModel):
    product_id: uuid.UUID
    market_presence: ValidationCheck = Field(default_factory=ValidationCheck)
    search_demand: ValidationCheck = Field(default_factory=ValidationCheck)
    sold_demand: ValidationCheck = Field(default_factory=ValidationCheck)
    trend_stability: ValidationCheck = Field(default_factory=ValidationCheck)
    supplier_economics: ValidationCheck = Field(default_factory=ValidationCheck)
    competition_gap: ValidationCheck = Field(default_factory=ValidationCheck)
    risk: ValidationCheck = Field(default_factory=ValidationCheck)
    final_readiness: ValidationReadiness = "INCOMPLETE"
    main_blocker: str | None = None
    next_action: str | None = None
    overall_validation_score: int = 0
