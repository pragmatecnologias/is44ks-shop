from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.validation_schema import (
    ProductDemandResearchCreate,
    ProductDemandResearchResponse,
    ProductDemandResearchVerifyRequest,
    ProductTrendResearchCreate,
    ProductTrendResearchResponse,
    ProductTrendResearchVerifyRequest,
    ValidationChecklistResponse,
)
from app.services.demand_research_service import DemandResearchService
from app.services.trend_research_service import TrendResearchService
from app.services.validation_checklist_service import ValidationChecklistService

router = APIRouter(prefix="/api/validation", tags=["validation"])


@router.post("/demand", response_model=ProductDemandResearchResponse, status_code=201)
def create_demand_research(data: ProductDemandResearchCreate, db: Session = Depends(get_db)):
    service = DemandResearchService(db)
    return service.to_dict(service.create_research(data))


@router.get("/demand", response_model=list[ProductDemandResearchResponse])
def list_demand_research(
    product_id: uuid.UUID | None = None,
    idea_id: uuid.UUID | None = None,
    campaign_id: uuid.UUID | None = None,
    verification_status: str | None = None,
    db: Session = Depends(get_db),
):
    service = DemandResearchService(db)
    return [service.to_dict(row) for row in service.list_research(product_id=product_id, idea_id=idea_id, campaign_id=campaign_id, verification_status=verification_status)]


@router.patch("/demand/{research_id}/verify", response_model=ProductDemandResearchResponse)
def verify_demand_research(research_id: uuid.UUID, data: ProductDemandResearchVerifyRequest, db: Session = Depends(get_db)):
    service = DemandResearchService(db)
    return service.to_dict(service.verify_research(research_id, data))


@router.post("/trends", response_model=ProductTrendResearchResponse, status_code=201)
def create_trend_research(data: ProductTrendResearchCreate, db: Session = Depends(get_db)):
    service = TrendResearchService(db)
    return service.to_dict(service.create_research(data))


@router.get("/trends", response_model=list[ProductTrendResearchResponse])
def list_trend_research(
    product_id: uuid.UUID | None = None,
    idea_id: uuid.UUID | None = None,
    campaign_id: uuid.UUID | None = None,
    verification_status: str | None = None,
    db: Session = Depends(get_db),
):
    service = TrendResearchService(db)
    return [service.to_dict(row) for row in service.list_research(product_id=product_id, idea_id=idea_id, campaign_id=campaign_id, verification_status=verification_status)]


@router.patch("/trends/{research_id}/verify", response_model=ProductTrendResearchResponse)
def verify_trend_research(research_id: uuid.UUID, data: ProductTrendResearchVerifyRequest, db: Session = Depends(get_db)):
    service = TrendResearchService(db)
    return service.to_dict(service.verify_research(research_id, data))


@router.get("/products/{product_id}/checklist", response_model=ValidationChecklistResponse)
def get_product_validation_checklist(product_id: uuid.UUID, db: Session = Depends(get_db)):
    service = ValidationChecklistService(db)
    return ValidationChecklistResponse.model_validate(service.get_checklist(product_id))


@router.post("/products/{product_id}/run", response_model=ValidationChecklistResponse)
def run_product_validation(product_id: uuid.UUID, db: Session = Depends(get_db)):
    service = ValidationChecklistService(db)
    return ValidationChecklistResponse.model_validate(service.run_validation(product_id))
