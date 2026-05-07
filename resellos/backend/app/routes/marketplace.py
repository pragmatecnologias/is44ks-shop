from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.db import get_db
from app.schemas.product_schema import MarketplaceResearchCreate, CompetitorListingCreate, MarketplaceEvidenceCreate, MarketplaceEvidenceUpdate, EvidenceVerificationRequest, CleanupRequest
from app.services.marketplace_service import MarketplaceService

router = APIRouter(prefix="/api/marketplace", tags=["marketplace"])


@router.post("/research/{product_id}", status_code=201)
def create_research(product_id: uuid.UUID, data: MarketplaceResearchCreate, db: Session = Depends(get_db)):
    service = MarketplaceService(db)
    return service.create_research(product_id, data)


@router.get("/research/{product_id}")
def get_research(product_id: uuid.UUID, db: Session = Depends(get_db)):
    service = MarketplaceService(db)
    return service.get_research(product_id)


@router.patch("/research/detail/{research_id}")
def update_research(research_id: uuid.UUID, data: MarketplaceResearchCreate, db: Session = Depends(get_db)):
    service = MarketplaceService(db)
    result = service.update_research(research_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Research not found")
    return result


@router.delete("/research/detail/{research_id}", status_code=204)
def delete_research(research_id: uuid.UUID, db: Session = Depends(get_db)):
    service = MarketplaceService(db)
    if not service.delete_research(research_id):
        raise HTTPException(status_code=404, detail="Research not found")


@router.post("/competitors/{product_id}", status_code=201)
def create_competitor(product_id: uuid.UUID, data: CompetitorListingCreate, db: Session = Depends(get_db)):
    service = MarketplaceService(db)
    return service.create_competitor_listing(product_id, data)


@router.get("/competitors/{product_id}")
def get_competitors(product_id: uuid.UUID, db: Session = Depends(get_db)):
    service = MarketplaceService(db)
    return service.get_competitor_listings(product_id)


@router.delete("/competitors/detail/{competitor_id}", status_code=204)
def delete_competitor(competitor_id: uuid.UUID, db: Session = Depends(get_db)):
    service = MarketplaceService(db)
    if not service.delete_competitor_listing(competitor_id):
        raise HTTPException(status_code=404, detail="Competitor not found")


@router.post("/evidence/cleanup")
def cleanup_evidence(data: CleanupRequest, db: Session = Depends(get_db)):
    service = MarketplaceService(db)
    return service.cleanup_evidence(
        product_id=data.product_id,
        verification_status=data.verification_status,
        dry_run=data.dry_run,
    )


@router.post("/evidence/{product_id}", status_code=201)
def create_evidence(product_id: uuid.UUID, data: MarketplaceEvidenceCreate, db: Session = Depends(get_db)):
    service = MarketplaceService(db)
    return service.create_evidence(product_id, data)


@router.get("/evidence/{product_id}")
def get_evidence(product_id: uuid.UUID, db: Session = Depends(get_db)):
    service = MarketplaceService(db)
    return service.get_evidence(product_id)


@router.patch("/evidence/detail/{evidence_id}")
def update_evidence(evidence_id: uuid.UUID, data: MarketplaceEvidenceUpdate, db: Session = Depends(get_db)):
    service = MarketplaceService(db)
    result = service.update_evidence(evidence_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return result


@router.delete("/evidence/detail/{evidence_id}", status_code=204)
def delete_evidence(evidence_id: uuid.UUID, db: Session = Depends(get_db)):
    service = MarketplaceService(db)
    if not service.delete_evidence(evidence_id):
        raise HTTPException(status_code=404, detail="Evidence not found")


@router.patch("/evidence/detail/{evidence_id}/verify")
def verify_evidence(evidence_id: uuid.UUID, data: EvidenceVerificationRequest, db: Session = Depends(get_db)):
    service = MarketplaceService(db)
    try:
        result = service.verify_evidence(evidence_id, data.verification_status, proof=data.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not result:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return result


@router.patch("/competitors/detail/{competitor_id}/verify")
def verify_competitor(competitor_id: uuid.UUID, data: EvidenceVerificationRequest, db: Session = Depends(get_db)):
    service = MarketplaceService(db)
    result = service.verify_competitor(competitor_id, data.verification_status)
    if not result:
        raise HTTPException(status_code=404, detail="Competitor not found")
    return result


@router.patch("/sources/detail/{source_id}/verify")
def verify_source(source_id: uuid.UUID, data: EvidenceVerificationRequest, db: Session = Depends(get_db)):
    service = MarketplaceService(db)
    result = service.verify_source(source_id, data.verification_status)
    if not result:
        raise HTTPException(status_code=404, detail="Source not found")
    return result
