from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


ConfidenceLevel = Literal["LOW", "MEDIUM", "HIGH"]
RiskLevel = Literal["LOW", "MEDIUM", "HIGH", "BLOCKED"]
DecisionLevel = Literal["BLOCKED", "SKIP", "WATCHLIST", "BUY_SAMPLE", "BUY_SMALL_BATCH", "REORDER", "SCALE"]


class RiskFlag(BaseModel):
    rule_id: str
    severity: Literal["ALLOW", "LOW", "MEDIUM", "HIGH", "BLOCKED"]
    matched_text: str
    reason: str


class RiskAgentOutput(BaseModel):
    risk_level: RiskLevel = "MEDIUM"
    blocked: bool = False
    risk_flags: list[RiskFlag] = Field(default_factory=list)
    red_flags: list[str] = Field(default_factory=list)
    requires_manual_review: bool = False
    confidence: ConfidenceLevel = "MEDIUM"
    summary: str = ""
    warnings: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)


class MarketplaceInsight(BaseModel):
    marketplace: str | None = None
    active_listing_count: int | None = None
    sold_listing_count: int | None = None
    median_active_price: float | None = None
    median_sold_price: float | None = None


class MarketAgentOutput(BaseModel):
    evidence_quality: Literal["LOW", "MEDIUM", "HIGH"] = "LOW"
    insufficient_data: bool = True
    market_price_missing: bool = True
    supporting_evidence_count: int = 0
    active_listing_count: int = 0
    sold_listing_count: int = 0
    demand_signal: Literal["LOW", "MEDIUM", "HIGH", "UNKNOWN"] = "UNKNOWN"
    competition_level: Literal["LOW", "MEDIUM", "HIGH", "UNKNOWN"] = "UNKNOWN"
    median_active_price: float | None = None
    median_sold_price: float | None = None
    median_active_shipping: float | None = None
    median_sold_shipping: float | None = None
    active_price_range: list[float] = Field(default_factory=list)
    sold_price_range: list[float] = Field(default_factory=list)
    marketplace_coverage: list[str] = Field(default_factory=list)
    sell_through_signal: Literal["LOW", "MEDIUM", "HIGH", "UNKNOWN"] = "UNKNOWN"
    recommended_research_action: str = ""
    required_next_evidence: list[str] = Field(default_factory=list)
    summary: str = ""
    confidence: ConfidenceLevel = "LOW"
    warnings: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)


class CompetitionAgentOutput(BaseModel):
    competition_level: Literal["LOW", "MEDIUM", "HIGH", "UNKNOWN"] = "UNKNOWN"
    listing_gap_score: int = 0
    can_compete: bool = False
    competitor_count: int = 0
    active_competitor_count: int = 0
    sold_competitor_count: int = 0
    median_competitor_price: float | None = None
    avg_photo_score: float | None = None
    avg_title_score: float | None = None
    avg_description_score: float | None = None
    weaknesses: list[str] = Field(default_factory=list)
    recommended_angle: str = ""
    summary: str = ""
    confidence: ConfidenceLevel = "LOW"
    warnings: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)


class ProfitScenario(BaseModel):
    name: str
    sale_price: float
    landed_cost: float
    selling_cost: float
    net_profit: float
    margin_percent: float
    decision: Literal["GOOD", "WEAK", "LOSS"]
    assumptions: list[str] = Field(default_factory=list)
    shipping_revenue: float = 0.0
    shipping_cost: float = 0.0


class ProfitAgentOutput(BaseModel):
    scenarios: list[ProfitScenario] = Field(default_factory=list)
    estimated_net_profit: float = 0.0
    break_even_price: float = 0.0
    minimum_recommended_price: float = 0.0
    target_sale_price: float = 0.0
    market_reference_price: float = 0.0
    best_scenario: str = ""
    summary: str = ""
    confidence: ConfidenceLevel = "LOW"
    warnings: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)


class ReorderAgentOutput(BaseModel):
    reorder_recommendation: Literal["DO_NOT_REORDER", "REORDER_SMALL", "REORDER_MEDIUM", "SCALE", "KILL_PRODUCT"] = "DO_NOT_REORDER"
    current_inventory: int = 0
    quantity_sold: int = 0
    quantity_ordered: int = 0
    quantity_returned: int = 0
    average_daily_sales: float = 0.0
    days_of_cover: float | None = None
    reorder_point: int = 0
    max_reorder_qty: int = 0
    stockout_risk: Literal["LOW", "MEDIUM", "HIGH"] = "LOW"
    return_rate_percent: float = 0.0
    average_landed_cost: float | None = None
    reorder_reason: str = ""
    summary: str = ""
    confidence: ConfidenceLevel = "LOW"
    warnings: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)


class DecisionAgentOutput(BaseModel):
    recommendation: DecisionLevel = "SKIP"
    research_verdict: Literal["REJECT", "WEAK_IDEA", "NEEDS_MORE_RESEARCH", "PROMISING_RESEARCH", "READY_FOR_SAMPLE"] = "NEEDS_MORE_RESEARCH"
    buy_readiness: Literal["NOT_READY", "READY"] = "NOT_READY"
    total_score: int = 0
    confidence: ConfidenceLevel = "LOW"
    reason: str = ""
    next_action: str = ""
    missing_evidence: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    hard_blockers: list[str] = Field(default_factory=list)
    max_quantity_to_buy: int = 0
    max_landed_cost: float = 0.0
    target_sale_price: float = 0.0
    required_before_buying: list[str] = Field(default_factory=list)
    blocked: bool = False
    warnings: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)


class AgentRunResult(BaseModel):
    agent_name: str
    output_json: dict[str, Any]
    summary: str = ""
    confidence: ConfidenceLevel = "LOW"
    warnings: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
