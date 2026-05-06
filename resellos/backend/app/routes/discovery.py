from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.product_schema import (
    OpportunityBoardRow,
    ProductIdeaCreate,
    ProductIdeaResponse,
    ProductIdeaUpdate,
    ProductIdeaQuickScanRequest,
    ProductIdeaQuickScanResponse,
    ResearchTaskResponse,
    ResearchTaskUpdate,
)
from app.services.discovery_service import DiscoveryService

router = APIRouter(prefix="/api/discovery", tags=["discovery"])


@router.get("", response_model=list[ProductIdeaResponse])
def list_ideas(db: Session = Depends(get_db)):
    service = DiscoveryService(db)
    return [service._serialize_idea(idea) for idea in service.list_ideas()]


@router.post("", response_model=ProductIdeaResponse, status_code=201)
def create_idea(data: ProductIdeaCreate, db: Session = Depends(get_db)):
    service = DiscoveryService(db)
    idea = service.create_idea(data)
    return service._serialize_idea(idea)


@router.post("/quick-scan", response_model=ProductIdeaQuickScanResponse)
def quick_scan(data: ProductIdeaQuickScanRequest, db: Session = Depends(get_db)):
    service = DiscoveryService(db)
    return service.quick_scan(data)


@router.post("/{idea_id}/quick-scan", response_model=ProductIdeaQuickScanResponse)
def quick_scan_existing(idea_id: uuid.UUID, db: Session = Depends(get_db)):
    service = DiscoveryService(db)
    try:
        return service.quick_scan_existing(idea_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Discovery idea not found")


@router.get("/opportunity-board", response_model=list[OpportunityBoardRow])
def opportunity_board(db: Session = Depends(get_db)):
    service = DiscoveryService(db)
    return service.opportunity_board()


@router.post("/{idea_id}/tasks/generate", response_model=list[ResearchTaskResponse])
def generate_tasks(idea_id: uuid.UUID, db: Session = Depends(get_db)):
    service = DiscoveryService(db)
    tasks = service.generate_tasks(idea_id)
    if not tasks:
        raise HTTPException(status_code=404, detail="Discovery idea not found")
    return [service._serialize_task(task) for task in tasks]


@router.patch("/tasks/{task_id}", response_model=ResearchTaskResponse)
def update_task(task_id: uuid.UUID, data: ResearchTaskUpdate, db: Session = Depends(get_db)):
    service = DiscoveryService(db)
    task = service.update_task(task_id, data)
    if not task:
        raise HTTPException(status_code=404, detail="Discovery task not found")
    return service._serialize_task(task)


@router.post("/{idea_id}/archive", response_model=ProductIdeaResponse)
def archive_idea(idea_id: uuid.UUID, db: Session = Depends(get_db)):
    service = DiscoveryService(db)
    idea = service.archive_idea(idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Discovery idea not found")
    return service._serialize_idea(idea)


@router.get("/{idea_id}", response_model=ProductIdeaResponse)
def get_idea(idea_id: uuid.UUID, db: Session = Depends(get_db)):
    service = DiscoveryService(db)
    idea = service.get_idea(idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Discovery idea not found")
    return service._serialize_idea(idea)


@router.patch("/{idea_id}", response_model=ProductIdeaResponse)
def update_idea(idea_id: uuid.UUID, data: ProductIdeaUpdate, db: Session = Depends(get_db)):
    service = DiscoveryService(db)
    idea = service.update_idea(idea_id, data)
    if not idea:
        raise HTTPException(status_code=404, detail="Discovery idea not found")
    return service._serialize_idea(idea)


@router.delete("/{idea_id}", status_code=204)
def delete_idea(idea_id: uuid.UUID, db: Session = Depends(get_db)):
    service = DiscoveryService(db)
    if not service.delete_idea(idea_id):
        raise HTTPException(status_code=404, detail="Discovery idea not found")


@router.post("/{idea_id}/promote")
def promote_idea(idea_id: uuid.UUID, db: Session = Depends(get_db)):
    service = DiscoveryService(db)
    product = service.promote_to_product(idea_id)
    if not product:
        raise HTTPException(status_code=404, detail="Discovery idea not found")
    return {"product_id": str(product.id)}
