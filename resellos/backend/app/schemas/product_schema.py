from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=500)
    category: Optional[str] = None
    subcategory: Optional[str] = None
    description: Optional[str] = None
    supplier_url: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    risk_level: Optional[str] = None
    final_score: Optional[float] = None
    final_decision: Optional[str] = None
    target_sale_price: Optional[float] = None
    expected_profit: Optional[float] = None


class ProductResponse(BaseModel):
    id: uuid.UUID
    sku: str
    name: str
    category: Optional[str] = None
    subcategory: Optional[str] = None
    description: Optional[str] = None
    status: str
    risk_level: Optional[str] = None
    final_score: Optional[float] = None
    final_decision: Optional[str] = None
    target_sale_price: Optional[float] = None
    expected_profit: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SupplierCreate(BaseModel):
    supplier_name: Optional[str] = None
    supplier_platform: Optional[str] = None
    supplier_url: Optional[str] = None
    unit_cost: Optional[float] = None
    domestic_shipping: Optional[float] = None
    international_shipping_estimate: Optional[float] = None
    estimated_landed_cost: Optional[float] = None
    moq: Optional[int] = None
    supplier_rating: Optional[str] = None
    notes: Optional[str] = None
    is_primary: bool = False


class SupplierResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    supplier_name: Optional[str] = None
    supplier_platform: Optional[str] = None
    supplier_url: Optional[str] = None
    unit_cost: Optional[float] = None
    domestic_shipping: Optional[float] = None
    international_shipping_estimate: Optional[float] = None
    estimated_landed_cost: Optional[float] = None
    moq: Optional[int] = None
    supplier_rating: Optional[str] = None
    notes: Optional[str] = None
    is_primary: bool
    created_at: datetime

    class Config:
        from_attributes = True


class MarketplaceResearchCreate(BaseModel):
    marketplace: str
    keyword: Optional[str] = None
    search_url: Optional[str] = None
    active_listing_count: Optional[int] = None
    sold_listing_count: Optional[int] = None
    min_active_price: Optional[float] = None
    median_active_price: Optional[float] = None
    max_active_price: Optional[float] = None
    min_sold_price: Optional[float] = None
    median_sold_price: Optional[float] = None
    max_sold_price: Optional[float] = None
    shipping_min: Optional[float] = None
    shipping_median: Optional[float] = None
    shipping_max: Optional[float] = None
    competition_level: Optional[str] = None
    demand_signal: Optional[str] = None
    evidence_quality: Optional[str] = None
    notes: Optional[str] = None


class MarketplaceEvidenceCreate(BaseModel):
    marketplace: str
    evidence_type: str
    title: Optional[str] = None
    url: Optional[str] = None
    price: Optional[float] = None
    shipping_price: Optional[float] = None
    sold_date: Optional[datetime] = None
    condition: Optional[str] = None
    seller_name: Optional[str] = None
    source_method: Optional[str] = None
    raw_text: Optional[str] = None
    screenshot_url: Optional[str] = None
    confidence: Optional[str] = None
    notes: Optional[str] = None


class MarketplaceEvidenceUpdate(BaseModel):
    marketplace: Optional[str] = None
    evidence_type: Optional[str] = None
    title: Optional[str] = None
    url: Optional[str] = None
    price: Optional[float] = None
    shipping_price: Optional[float] = None
    sold_date: Optional[datetime] = None
    condition: Optional[str] = None
    seller_name: Optional[str] = None
    source_method: Optional[str] = None
    raw_text: Optional[str] = None
    screenshot_url: Optional[str] = None
    confidence: Optional[str] = None
    notes: Optional[str] = None


class ProfitAnalysisCreate(BaseModel):
    scenario_name: Optional[str] = "default"
    expected_sale_price: float
    product_cost: float
    import_shipping_per_unit: float = 0
    us_shipping: float = 0
    marketplace_fee: float = 0
    packaging_cost: float = 0.50
    return_allowance: float = 0.50
    ad_cost: float = 0


class ProfitAnalysisUpdate(BaseModel):
    scenario_name: Optional[str] = None
    expected_sale_price: Optional[float] = None
    product_cost: Optional[float] = None
    import_shipping_per_unit: Optional[float] = None
    landed_cost: Optional[float] = None
    marketplace_fee: Optional[float] = None
    us_shipping: Optional[float] = None
    packaging_cost: Optional[float] = None
    return_allowance: Optional[float] = None
    ad_cost: Optional[float] = None


class CompetitorListingCreate(BaseModel):
    marketplace: Optional[str] = None
    title: Optional[str] = None
    url: Optional[str] = None
    price: Optional[float] = None
    shipping_price: Optional[float] = None
    condition: Optional[str] = None
    seller_name: Optional[str] = None
    sold: bool = False
    photo_score: Optional[float] = None
    title_score: Optional[float] = None
    description_score: Optional[float] = None
    notes: Optional[str] = None


class InventoryCreate(BaseModel):
    quantity_on_hand: int = 0
    quantity_ordered: int = 0
    average_landed_cost: Optional[float] = None
    location_code: Optional[str] = None
    reorder_point: Optional[int] = None


class SaleCreate(BaseModel):
    marketplace: Optional[str] = None
    sale_date: Optional[datetime] = None
    quantity: int = 1
    sale_price: float
    marketplace_fee: float = 0
    shipping_cost: float = 0
    packaging_cost: float = 0.50
    net_profit: Optional[float] = None
    buyer_paid_shipping: bool = False
    returned: bool = False
    notes: Optional[str] = None


class ResearchPipelineResponse(BaseModel):
    product_id: str
    status: str
    final_score: float
    final_decision: str
    next_action: str


class ResearchRunResponse(BaseModel):
    product_id: uuid.UUID
    status: str
    final_decision: Optional[str] = None
    final_score: Optional[float] = None
    decision: Optional[dict] = None
    reports: list[dict] = Field(default_factory=list)


class ResearchCockpitResponse(BaseModel):
    product: ProductResponse
    sources: list[SupplierResponse] = Field(default_factory=list)
    marketplace_research: list[dict] = Field(default_factory=list)
    marketplace_evidence: list[dict] = Field(default_factory=list)
    competitor_listings: list[dict] = Field(default_factory=list)
    profit_analyses: list[dict] = Field(default_factory=list)
    agent_reports: list[dict] = Field(default_factory=list)
    decision: Optional[dict] = None
    competition: Optional[dict] = None
    reorder: Optional[dict] = None
    buy_readiness: dict = Field(default_factory=dict)
    hard_blockers: list[str] = Field(default_factory=list)
    inventory: list[dict] = Field(default_factory=list)
    sales: list[dict] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    next_action: Optional[str] = None
    confidence: Optional[str] = None
    current_status: Optional[str] = None
    discovery_context: Optional[dict] = None


class ListingGenerateRequest(BaseModel):
    marketplace: str = "ebay"
    product_features: Optional[str] = None
    dimensions: Optional[str] = None
    target_price: Optional[float] = None
    shipping_policy: Optional[str] = None
    bundle_option: bool = False


class ProductIdeaCreate(BaseModel):
    idea_name: str = Field(..., min_length=1, max_length=300)
    category: Optional[str] = None
    source_platform: Optional[str] = None
    source_url: Optional[str] = None
    rough_supplier_cost: Optional[float] = None
    estimated_landed_cost: Optional[float] = None
    why_interesting: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    marketplace_observation: Optional[str] = None


class ProductIdeaUpdate(BaseModel):
    idea_name: Optional[str] = None
    category: Optional[str] = None
    source_platform: Optional[str] = None
    source_url: Optional[str] = None
    rough_supplier_cost: Optional[float] = None
    estimated_landed_cost: Optional[float] = None
    why_interesting: Optional[str] = None
    risk_flags: Optional[str] = None
    quick_market_signal: Optional[str] = None
    quick_profit_signal: Optional[str] = None
    research_priority: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    quick_scan_verdict: Optional[str] = None
    quick_scan_reason: Optional[str] = None
    suggested_keywords: Optional[str] = None
    required_next_evidence: Optional[str] = None
    promoted_product_id: Optional[uuid.UUID] = None


class ResearchTaskResponse(BaseModel):
    id: uuid.UUID
    idea_id: uuid.UUID
    task_type: str
    title: str
    status: str
    notes: Optional[str] = None
    sort_order: int
    linked_evidence_id: Optional[uuid.UUID] = None
    linked_source_id: Optional[uuid.UUID] = None
    linked_competitor_id: Optional[uuid.UUID] = None
    linked_product_id: Optional[uuid.UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ResearchTaskUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    linked_evidence_id: Optional[uuid.UUID] = None
    linked_source_id: Optional[uuid.UUID] = None
    linked_competitor_id: Optional[uuid.UUID] = None
    linked_product_id: Optional[uuid.UUID] = None


class ProductIdeaResponse(BaseModel):
    id: uuid.UUID
    idea_name: str
    category: Optional[str] = None
    source_platform: Optional[str] = None
    source_url: Optional[str] = None
    rough_supplier_cost: Optional[float] = None
    estimated_landed_cost: Optional[float] = None
    why_interesting: Optional[str] = None
    risk_flags: Optional[object] = None
    quick_market_signal: Optional[str] = None
    quick_profit_signal: Optional[str] = None
    research_priority: Optional[str] = None
    notes: Optional[str] = None
    status: str
    quick_scan_verdict: Optional[str] = None
    quick_scan_reason: Optional[str] = None
    research_completeness_score: int = 0
    discovery_completeness_score: int = 0
    opportunity_score: int = 0
    buy_readiness_status: str = "NOT_READY"
    suggested_keywords: Optional[object] = None
    required_next_evidence: Optional[object] = None
    promoted_product_id: Optional[uuid.UUID] = None
    tasks: list[ResearchTaskResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductIdeaQuickScanRequest(BaseModel):
    idea_name: str = Field(..., min_length=1, max_length=300)
    category: Optional[str] = None
    source_platform: Optional[str] = None
    source_url: Optional[str] = None
    rough_supplier_cost: Optional[float] = None
    estimated_landed_cost: Optional[float] = None
    why_interesting: Optional[str] = None
    notes: Optional[str] = None
    marketplace_observation: Optional[str] = None


class ProductIdeaQuickScanResponse(BaseModel):
    idea: ProductIdeaResponse
    quick_scan_verdict: str
    quick_scan_reason: str
    research_priority: str
    research_completeness_score: int = 0
    discovery_completeness_score: int = 0
    opportunity_score: int = 0
    buy_readiness_status: str = "NOT_READY"
    required_next_evidence: object = Field(default_factory=list)
    suggested_keywords: object = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)
    tasks: list[ResearchTaskResponse] = Field(default_factory=list)


class OpportunityBoardRow(BaseModel):
    id: str
    entity_type: str
    title: str
    category: Optional[str] = None
    discovery_completeness_score: int = 0
    research_completeness_score: int = 0
    research_verdict: Optional[str] = None
    buy_readiness_status: Optional[str] = None
    risk_level: Optional[str] = None
    sold_evidence_count: int = 0
    active_evidence_count: int = 0
    median_sold_price: Optional[float] = None
    median_active_price: Optional[float] = None
    median_sold_shipping: Optional[float] = None
    median_active_shipping: Optional[float] = None
    median_shipping: Optional[float] = None
    best_landed_cost: Optional[float] = None
    best_profit_scenario: Optional[str] = None
    competition_gap_score: Optional[int] = None
    supplier_confidence: Optional[str] = None
    next_action: Optional[str] = None
    source_platform: Optional[str] = None
    status: Optional[str] = None


# Backwards-compatible aliases for older discovery naming.
DiscoveryIdeaCreate = ProductIdeaCreate
DiscoveryIdeaUpdate = ProductIdeaUpdate
DiscoveryTaskResponse = ResearchTaskResponse
DiscoveryTaskUpdate = ResearchTaskUpdate
DiscoveryIdeaResponse = ProductIdeaResponse
DiscoveryQuickScanRequest = ProductIdeaQuickScanRequest
DiscoveryQuickScanResponse = ProductIdeaQuickScanResponse
