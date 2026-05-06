from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional, Literal

from pydantic import BaseModel, Field


PortfolioRole = Literal["CONSIDERING", "HERO", "ADD_ON", "BUNDLE_SUPPORT", "TRAFFIC", "PROFIT", "TEST", "REJECTED"]
PortfolioItemStatus = Literal["CONSIDERING", "RESEARCHING", "SAMPLE_READY", "SAMPLED", "REJECTED"]
ShopConceptStatus = Literal["DRAFT", "ACTIVE", "PAUSED"]
CollectionStatus = Literal["DRAFT", "ACTIVE", "PAUSED"]


class ShopConceptCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=300)
    description: Optional[str] = None
    target_customer: Optional[str] = None
    category: Optional[str] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    avoid_list_json: dict[str, Any] = Field(default_factory=dict)
    preferred_attributes_json: dict[str, Any] = Field(default_factory=dict)
    brand_angle: Optional[str] = None
    status: ShopConceptStatus = "DRAFT"


class ShopConceptUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    target_customer: Optional[str] = None
    category: Optional[str] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    avoid_list_json: Optional[dict[str, Any]] = None
    preferred_attributes_json: Optional[dict[str, Any]] = None
    brand_angle: Optional[str] = None
    status: Optional[ShopConceptStatus] = None


class ShopConceptResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    target_customer: Optional[str] = None
    category: Optional[str] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    avoid_list_json: dict[str, Any] = Field(default_factory=dict)
    preferred_attributes_json: dict[str, Any] = Field(default_factory=dict)
    brand_angle: Optional[str] = None
    status: ShopConceptStatus
    created_at: datetime
    updated_at: datetime
    campaign_count: int = 0
    collection_count: int = 0
    idea_count: int = 0
    product_count: int = 0
    portfolio_item_count: int = 0

    class Config:
        from_attributes = True


class ProductCollectionCreate(BaseModel):
    shop_concept_id: Optional[uuid.UUID] = None
    name: str = Field(..., min_length=1, max_length=300)
    theme: Optional[str] = None
    target_problem: Optional[str] = None
    description: Optional[str] = None
    status: CollectionStatus = "DRAFT"


class ProductCollectionUpdate(BaseModel):
    shop_concept_id: Optional[uuid.UUID] = None
    name: Optional[str] = None
    theme: Optional[str] = None
    target_problem: Optional[str] = None
    description: Optional[str] = None
    status: Optional[CollectionStatus] = None


class ProductCollectionResponse(BaseModel):
    id: uuid.UUID
    shop_concept_id: uuid.UUID
    shop_concept_name: Optional[str] = None
    name: str
    theme: Optional[str] = None
    target_problem: Optional[str] = None
    description: Optional[str] = None
    status: CollectionStatus
    created_at: datetime
    updated_at: datetime
    portfolio_item_count: int = 0
    idea_count: int = 0
    product_count: int = 0

    class Config:
        from_attributes = True


class PortfolioItemCreate(BaseModel):
    shop_concept_id: Optional[uuid.UUID] = None
    collection_id: Optional[uuid.UUID] = None
    idea_id: Optional[uuid.UUID] = None
    product_id: Optional[uuid.UUID] = None
    role: PortfolioRole = "CONSIDERING"
    status: PortfolioItemStatus = "CONSIDERING"
    assortment_fit_score: int = 0
    bundle_potential_score: int = 0
    notes: Optional[str] = None


class PortfolioItemUpdate(BaseModel):
    shop_concept_id: Optional[uuid.UUID] = None
    collection_id: Optional[uuid.UUID] = None
    idea_id: Optional[uuid.UUID] = None
    product_id: Optional[uuid.UUID] = None
    role: Optional[PortfolioRole] = None
    status: Optional[PortfolioItemStatus] = None
    assortment_fit_score: Optional[int] = None
    bundle_potential_score: Optional[int] = None
    notes: Optional[str] = None


class PortfolioItemResponse(BaseModel):
    id: uuid.UUID
    shop_concept_id: uuid.UUID
    shop_concept_name: Optional[str] = None
    collection_id: Optional[uuid.UUID] = None
    collection_name: Optional[str] = None
    idea_id: Optional[uuid.UUID] = None
    idea_name: Optional[str] = None
    product_id: Optional[uuid.UUID] = None
    product_name: Optional[str] = None
    role: PortfolioRole
    status: PortfolioItemStatus
    assortment_fit_score: int = 0
    bundle_potential_score: int = 0
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ShopPortfolioReportResponse(BaseModel):
    shop_concept_id: uuid.UUID
    shop_concept_name: str
    collections: list[ProductCollectionResponse] = Field(default_factory=list)
    portfolio_items: list[PortfolioItemResponse] = Field(default_factory=list)
    total_items: int = 0
    items_by_role: dict[str, int] = Field(default_factory=dict)
    items_by_status: dict[str, int] = Field(default_factory=dict)
    products_by_decision: dict[str, int] = Field(default_factory=dict)
    watchlist_products: list[dict[str, Any]] = Field(default_factory=list)
    skip_products: list[dict[str, Any]] = Field(default_factory=list)
    ready_for_sample_products: list[dict[str, Any]] = Field(default_factory=list)
    ideas_still_under_research: list[dict[str, Any]] = Field(default_factory=list)
    collection_gaps: list[str] = Field(default_factory=list)
    next_recommended_campaign: Optional[str] = None
    next_action: Optional[str] = None


class ShopConceptDetailResponse(BaseModel):
    shop_concept: ShopConceptResponse
    collections: list[ProductCollectionResponse] = Field(default_factory=list)
    portfolio_items: list[PortfolioItemResponse] = Field(default_factory=list)
    report: ShopPortfolioReportResponse

