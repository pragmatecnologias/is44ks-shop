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
    active_listing_count: int = 0
    sold_listing_count: int = 0
    demand_signal: Literal["LOW", "MEDIUM", "HIGH", "UNKNOWN"] = "UNKNOWN"
    competition_level: Literal["LOW", "MEDIUM", "HIGH", "UNKNOWN"] = "UNKNOWN"
    median_active_price: float | None = None
    median_sold_price: float | None = None
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


class ProfitAgentOutput(BaseModel):
    scenarios: list[ProfitScenario] = Field(default_factory=list)
    estimated_net_profit: float = 0.0
    break_even_price: float = 0.0
    minimum_recommended_price: float = 0.0
    summary: str = ""
    confidence: ConfidenceLevel = "LOW"
    warnings: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)


class DecisionAgentOutput(BaseModel):
    recommendation: DecisionLevel = "SKIP"
    total_score: int = 0
    confidence: ConfidenceLevel = "LOW"
    reason: str = ""
    next_action: str = ""
    missing_evidence: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
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

