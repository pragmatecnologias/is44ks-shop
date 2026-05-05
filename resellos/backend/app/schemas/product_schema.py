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
    reports: list[dict] = Field(default_factory=list)


class ListingGenerateRequest(BaseModel):
    marketplace: str = "ebay"
    product_features: Optional[str] = None
    dimensions: Optional[str] = None
    target_price: Optional[float] = None
    shipping_policy: Optional[str] = None
    bundle_option: bool = False
