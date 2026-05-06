from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.portfolio_schema import (
    PortfolioItemCreate,
    PortfolioItemResponse,
    PortfolioItemUpdate,
    ProductCollectionCreate,
    ProductCollectionResponse,
    ProductCollectionUpdate,
    ShopConceptCreate,
    ShopConceptDetailResponse,
    ShopConceptResponse,
    ShopConceptUpdate,
    ShopPortfolioReportResponse,
)
from app.services.portfolio_service import PortfolioService

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])


@router.post("/shops", response_model=ShopConceptResponse, status_code=201)
def create_shop_concept(data: ShopConceptCreate, db: Session = Depends(get_db)):
    service = PortfolioService(db)
    return ShopConceptResponse.model_validate(service._serialize_shop(service.create_shop_concept(data)))


@router.get("/shops", response_model=list[ShopConceptResponse])
def list_shop_concepts(db: Session = Depends(get_db)):
    service = PortfolioService(db)
    return [ShopConceptResponse.model_validate(service._serialize_shop(shop)) for shop in service.list_shop_concepts()]


@router.get("/shops/{shop_id}", response_model=ShopConceptDetailResponse)
def get_shop_concept(shop_id: uuid.UUID, db: Session = Depends(get_db)):
    service = PortfolioService(db)
    return service.get_shop_detail(shop_id)


@router.patch("/shops/{shop_id}", response_model=ShopConceptResponse)
def update_shop_concept(shop_id: uuid.UUID, data: ShopConceptUpdate, db: Session = Depends(get_db)):
    service = PortfolioService(db)
    shop = service.update_shop_concept(shop_id, data)
    if not shop:
        raise HTTPException(status_code=404, detail="Shop concept not found")
    return ShopConceptResponse.model_validate(service._serialize_shop(shop))


@router.post("/shops/{shop_id}/collections", response_model=ProductCollectionResponse, status_code=201)
def create_collection(shop_id: uuid.UUID, data: ProductCollectionCreate, db: Session = Depends(get_db)):
    service = PortfolioService(db)
    collection = service.create_collection(shop_id, data)
    return ProductCollectionResponse.model_validate(service._serialize_collection(collection))


@router.patch("/collections/{collection_id}", response_model=ProductCollectionResponse)
def update_collection(collection_id: uuid.UUID, data: ProductCollectionUpdate, db: Session = Depends(get_db)):
    service = PortfolioService(db)
    collection = service.update_collection(collection_id, data)
    if not collection:
        raise HTTPException(status_code=404, detail="Product collection not found")
    return ProductCollectionResponse.model_validate(service._serialize_collection(collection))


@router.post("/shops/{shop_id}/items", response_model=PortfolioItemResponse, status_code=201)
def create_portfolio_item(shop_id: uuid.UUID, data: PortfolioItemCreate, db: Session = Depends(get_db)):
    service = PortfolioService(db)
    item = service.add_portfolio_item(shop_id, data)
    return PortfolioItemResponse.model_validate(service._serialize_item(item))


@router.patch("/items/{item_id}", response_model=PortfolioItemResponse)
def update_portfolio_item(item_id: uuid.UUID, data: PortfolioItemUpdate, db: Session = Depends(get_db)):
    service = PortfolioService(db)
    item = service.update_portfolio_item(item_id, data)
    if not item:
        raise HTTPException(status_code=404, detail="Portfolio item not found")
    return PortfolioItemResponse.model_validate(service._serialize_item(item))


@router.get("/shops/{shop_id}/report", response_model=ShopPortfolioReportResponse)
def get_shop_portfolio_report(shop_id: uuid.UUID, db: Session = Depends(get_db)):
    service = PortfolioService(db)
    return ShopPortfolioReportResponse.model_validate(service.get_shop_report(shop_id))

