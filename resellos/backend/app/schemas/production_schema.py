from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# ProductionCampaign
# ---------------------------------------------------------------------------


class ProductionCampaignCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=300)
    shop_concept_id: Optional[uuid.UUID] = None
    goal: Optional[str] = None
    workspace_type: Optional[str] = None
    workspace_dimensions_json: Optional[dict[str, Any]] = None
    power_constraints_json: Optional[dict[str, Any]] = None
    safety_requirements_json: Optional[dict[str, Any]] = None
    budget_limit_usd: Optional[float] = None
    status: str = "DRAFT"
    created_by: Optional[str] = None


class ProductionCampaignUpdate(BaseModel):
    name: Optional[str] = None
    shop_concept_id: Optional[uuid.UUID] = None
    goal: Optional[str] = None
    workspace_type: Optional[str] = None
    workspace_dimensions_json: Optional[dict[str, Any]] = None
    power_constraints_json: Optional[dict[str, Any]] = None
    safety_requirements_json: Optional[dict[str, Any]] = None
    budget_limit_usd: Optional[float] = None
    status: Optional[str] = None
    created_by: Optional[str] = None


class ProductionCampaignResponse(BaseModel):
    id: uuid.UUID
    name: str
    shop_concept_id: Optional[uuid.UUID] = None
    mode: str = "PRODUCTION"
    goal: Optional[str] = None
    workspace_type: Optional[str] = None
    workspace_dimensions_json: Optional[dict[str, Any]] = None
    power_constraints_json: Optional[dict[str, Any]] = None
    safety_requirements_json: Optional[dict[str, Any]] = None
    budget_limit_usd: Optional[float] = None
    status: str
    created_by: Optional[str] = None
    machine_count: int = 0
    shortlisted_count: int = 0
    decided_count: int = 0
    report_generated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# ProductionCapability
# ---------------------------------------------------------------------------


class ProductionCapabilityCreate(BaseModel):
    campaign_id: uuid.UUID
    name: str = Field(..., min_length=1, max_length=200)
    category: Optional[str] = None
    description: Optional[str] = None
    materials: Optional[list[str]] = None
    typical_products: Optional[list[str]] = None
    entry_cost_range_json: Optional[dict[str, Any]] = None
    skill_level: Optional[str] = None
    workspace_footprint: Optional[str] = None


class ProductionCapabilityResponse(BaseModel):
    id: uuid.UUID
    campaign_id: uuid.UUID
    name: str
    category: Optional[str] = None
    description: Optional[str] = None
    materials: Optional[list[str]] = None
    typical_products: Optional[list[str]] = None
    entry_cost_range_json: Optional[dict[str, Any]] = None
    skill_level: Optional[str] = None
    workspace_footprint: Optional[str] = None
    machine_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# MachineCandidate
# ---------------------------------------------------------------------------


class MachineCandidateCreate(BaseModel):
    campaign_id: uuid.UUID
    name: str = Field(..., min_length=1, max_length=300)
    brand: Optional[str] = None
    model: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    price_new: Optional[float] = None
    price_used_range_json: Optional[dict[str, Any]] = None
    condition: Optional[str] = None
    power_requirements: Optional[str] = None
    workspace_needed: Optional[str] = None
    safety_notes: Optional[str] = None
    capability_ids: Optional[list[uuid.UUID]] = None


class MachineCandidateUpdate(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    price_new: Optional[float] = None
    price_used_range_json: Optional[dict[str, Any]] = None
    condition: Optional[str] = None
    power_requirements: Optional[str] = None
    workspace_needed: Optional[str] = None
    safety_notes: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    capability_ids: Optional[list[uuid.UUID]] = None


class MachineCandidateResponse(BaseModel):
    id: uuid.UUID
    campaign_id: uuid.UUID
    name: str
    brand: Optional[str] = None
    model: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    price_new: Optional[float] = None
    price_used_range_json: Optional[dict[str, Any]] = None
    condition: Optional[str] = None
    power_requirements: Optional[str] = None
    workspace_needed: Optional[str] = None
    safety_notes: Optional[str] = None
    status: str
    decision_recommendation: Optional[str] = None
    decision_reason: Optional[str] = None
    decided_at: Optional[datetime] = None
    notes: Optional[str] = None
    evidence_count: int = 0
    product_family_count: int = 0
    cost_scenario_count: int = 0
    has_decision: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# MachineEvidence
# ---------------------------------------------------------------------------


class MachineEvidenceCreate(BaseModel):
    evidence_type: str = Field(..., min_length=1, max_length=50)
    title: Optional[str] = None
    url: Optional[str] = None
    price: Optional[float] = None
    source: Optional[str] = None
    seller: Optional[str] = None
    condition: Optional[str] = None
    specs_json: Optional[dict[str, Any]] = None
    pros: Optional[str] = None
    cons: Optional[str] = None
    confidence: str = "MEDIUM"
    raw_text: Optional[str] = None
    screenshot_url: Optional[str] = None
    notes: Optional[str] = None


class MachineEvidenceResponse(BaseModel):
    id: uuid.UUID
    machine_id: uuid.UUID
    evidence_type: str
    title: Optional[str] = None
    url: Optional[str] = None
    price: Optional[float] = None
    source: Optional[str] = None
    seller: Optional[str] = None
    condition: Optional[str] = None
    specs_json: Optional[dict[str, Any]] = None
    pros: Optional[str] = None
    cons: Optional[str] = None
    verification_status: str
    confidence: str
    raw_text: Optional[str] = None
    screenshot_url: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# MachineProductFamily
# ---------------------------------------------------------------------------


class MachineProductFamilyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=300)
    description: Optional[str] = None
    material_cost_per_unit: Optional[float] = None
    estimated_sale_price: Optional[float] = None
    estimated_demand: Optional[str] = None
    market_evidence_summary: Optional[str] = None
    notes: Optional[str] = None


class MachineProductFamilyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    material_cost_per_unit: Optional[float] = None
    estimated_sale_price: Optional[float] = None
    estimated_demand: Optional[str] = None
    market_evidence_summary: Optional[str] = None
    has_market_evidence: Optional[bool] = None
    market_evidence_count: Optional[int] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class MachineProductFamilyResponse(BaseModel):
    id: uuid.UUID
    machine_id: uuid.UUID
    name: str
    description: Optional[str] = None
    material_cost_per_unit: Optional[float] = None
    estimated_sale_price: Optional[float] = None
    estimated_demand: Optional[str] = None
    market_evidence_summary: Optional[str] = None
    market_evidence_count: int = 0
    has_market_evidence: bool = False
    status: str
    promoted_product_id: Optional[uuid.UUID] = None
    promoted_idea_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None
    cost_scenario_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# ProductionCostScenario
# ---------------------------------------------------------------------------


class ProductionCostScenarioCreate(BaseModel):
    product_family_id: Optional[uuid.UUID] = None
    scenario_name: str = Field(..., min_length=1, max_length=200)
    material_cost: Optional[float] = None
    labor_cost: Optional[float] = None
    machine_time_cost: Optional[float] = None
    consumables_cost: Optional[float] = None
    marketplace_fee: Optional[float] = None
    shipping_cost: Optional[float] = None
    packaging_cost: Optional[float] = None
    other_costs: Optional[float] = None
    total_cost_per_unit: Optional[float] = None
    sale_price: Optional[float] = None
    net_profit_per_unit: Optional[float] = None
    margin_percent: Optional[float] = None
    machine_purchase_price: Optional[float] = None
    units_per_month: Optional[int] = None
    monthly_profit: Optional[float] = None
    payback_months: Optional[float] = None
    notes: Optional[str] = None


class ProductionCostScenarioUpdate(BaseModel):
    scenario_name: Optional[str] = None
    material_cost: Optional[float] = None
    labor_cost: Optional[float] = None
    machine_time_cost: Optional[float] = None
    consumables_cost: Optional[float] = None
    marketplace_fee: Optional[float] = None
    shipping_cost: Optional[float] = None
    packaging_cost: Optional[float] = None
    other_costs: Optional[float] = None
    total_cost_per_unit: Optional[float] = None
    sale_price: Optional[float] = None
    net_profit_per_unit: Optional[float] = None
    margin_percent: Optional[float] = None
    machine_purchase_price: Optional[float] = None
    units_per_month: Optional[int] = None
    monthly_profit: Optional[float] = None
    payback_months: Optional[float] = None
    notes: Optional[str] = None


class ProductionCostScenarioResponse(BaseModel):
    id: uuid.UUID
    machine_id: uuid.UUID
    product_family_id: Optional[uuid.UUID] = None
    scenario_name: str
    material_cost: Optional[float] = None
    labor_cost: Optional[float] = None
    machine_time_cost: Optional[float] = None
    consumables_cost: Optional[float] = None
    marketplace_fee: Optional[float] = None
    shipping_cost: Optional[float] = None
    packaging_cost: Optional[float] = None
    other_costs: Optional[float] = None
    total_cost_per_unit: Optional[float] = None
    sale_price: Optional[float] = None
    net_profit_per_unit: Optional[float] = None
    margin_percent: Optional[float] = None
    machine_purchase_price: Optional[float] = None
    units_per_month: Optional[int] = None
    monthly_profit: Optional[float] = None
    payback_months: Optional[float] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# MachineDecision
# ---------------------------------------------------------------------------


class MachineDecisionResponse(BaseModel):
    id: uuid.UUID
    machine_id: uuid.UUID
    recommendation: str
    reason: Optional[str] = None
    confidence: str
    evidence_count: int = 0
    product_family_count: int = 0
    families_with_market_evidence: int = 0
    has_cost_scenario: bool = False
    payback_calculated: bool = False
    workspace_fit: Optional[str] = None
    safety_fit: Optional[str] = None
    budget_fit: Optional[str] = None
    hard_blockers: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Composite / Detail responses
# ---------------------------------------------------------------------------


class ProductionCampaignDetailResponse(BaseModel):
    campaign: ProductionCampaignResponse
    capabilities: list[ProductionCapabilityResponse] = Field(default_factory=list)
    machines: list[MachineCandidateResponse] = Field(default_factory=list)


class MachineCockpitResponse(BaseModel):
    machine: MachineCandidateResponse
    capabilities: list[ProductionCapabilityResponse] = Field(default_factory=list)
    evidence: list[MachineEvidenceResponse] = Field(default_factory=list)
    product_families: list[MachineProductFamilyResponse] = Field(default_factory=list)
    cost_scenarios: list[ProductionCostScenarioResponse] = Field(default_factory=list)
    decision: Optional[MachineDecisionResponse] = None
    next_action: Optional[dict[str, Any]] = None
