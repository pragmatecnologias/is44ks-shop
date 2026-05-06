from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.campaign_schema import (
    DiscoveryCampaignCreate,
    DiscoveryCampaignDetailResponse,
    DiscoveryCampaignReportResponse,
    DiscoveryCampaignResponse,
    DiscoveryCampaignUpdate,
    DiscoveryCampaignTaskCreate,
    DiscoveryCampaignTaskResponse,
    DiscoveryCampaignTaskUpdate,
)
from app.schemas.product_schema import ProductIdeaCreate, ProductIdeaResponse
from app.services.campaign_service import CampaignService

router = APIRouter(prefix="/api/discovery/campaigns", tags=["discovery-campaigns"])


@router.post("", response_model=DiscoveryCampaignResponse, status_code=201)
def create_campaign(data: DiscoveryCampaignCreate, db: Session = Depends(get_db)):
    service = CampaignService(db)
    campaign = service.create_campaign(data)
    return service._serialize_campaign(campaign)


@router.get("", response_model=list[DiscoveryCampaignResponse])
def list_campaigns(db: Session = Depends(get_db)):
    service = CampaignService(db)
    return [service._serialize_campaign(campaign) for campaign in service.list_campaigns()]


@router.patch("/{campaign_id}", response_model=DiscoveryCampaignResponse)
def update_campaign(campaign_id: uuid.UUID, data: DiscoveryCampaignUpdate, db: Session = Depends(get_db)):
    service = CampaignService(db)
    campaign = service.update_campaign(campaign_id, data.model_dump(exclude_unset=True))
    if not campaign:
        raise HTTPException(status_code=404, detail="Discovery campaign not found")
    return service._serialize_campaign(campaign)


@router.get("/{campaign_id}", response_model=DiscoveryCampaignDetailResponse)
def get_campaign(campaign_id: uuid.UUID, db: Session = Depends(get_db)):
    service = CampaignService(db)
    return service.get_detail(campaign_id)


@router.post("/{campaign_id}/ideas", response_model=ProductIdeaResponse, status_code=201)
def add_idea_to_campaign(campaign_id: uuid.UUID, data: ProductIdeaCreate, db: Session = Depends(get_db)):
    service = CampaignService(db)
    if data.campaign_id and data.campaign_id != campaign_id:
        raise HTTPException(status_code=400, detail="campaign_id mismatch.")
    payload = data.model_dump()
    payload["campaign_id"] = campaign_id
    idea = service.add_idea_to_campaign(campaign_id, ProductIdeaCreate(**payload))
    return service.discovery._serialize_idea(idea)


@router.post("/{campaign_id}/tasks", response_model=DiscoveryCampaignTaskResponse, status_code=201)
def create_task(campaign_id: uuid.UUID, data: DiscoveryCampaignTaskCreate, db: Session = Depends(get_db)):
    service = CampaignService(db)
    task = service.create_task(campaign_id, data)
    return service._serialize_task(task)


@router.patch("/{campaign_id}/tasks/{task_id}", response_model=DiscoveryCampaignTaskResponse)
def update_task(campaign_id: uuid.UUID, task_id: uuid.UUID, data: DiscoveryCampaignTaskUpdate, db: Session = Depends(get_db)):
    service = CampaignService(db)
    task = service.update_task(campaign_id, task_id, data)
    if not task:
        raise HTTPException(status_code=404, detail="Discovery campaign task not found")
    return service._serialize_task(task)


@router.get("/{campaign_id}/report", response_model=DiscoveryCampaignReportResponse)
def get_report(campaign_id: uuid.UUID, db: Session = Depends(get_db)):
    service = CampaignService(db)
    return service.get_report(campaign_id)


@router.post("/{campaign_id}/generate-next-tasks", response_model=list[DiscoveryCampaignTaskResponse])
def generate_next_tasks(campaign_id: uuid.UUID, db: Session = Depends(get_db)):
    service = CampaignService(db)
    tasks = service.generate_next_tasks(campaign_id)
    return [service._serialize_task(task) for task in tasks]


@router.get("/{campaign_id}/next-task")
def get_next_task(campaign_id: uuid.UUID, db: Session = Depends(get_db)):
    service = CampaignService(db)
    task = service.get_next_task(campaign_id)
    if not task:
        return {"message": "No campaign tasks pending."}
    return service._serialize_task(task)
