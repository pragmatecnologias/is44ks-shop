from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.db import get_db
from app.schemas.product_schema import ProfitAnalysisCreate
from app.services.profit_service import ProfitService

router = APIRouter(prefix="/api/profit", tags=["profit"])


@router.post("/analyses/{product_id}", status_code=201)
def create_analysis(product_id: uuid.UUID, data: ProfitAnalysisCreate, db: Session = Depends(get_db)):
    service = ProfitService(db)
    return service.create_analysis(product_id, data)


@router.get("/analyses/{product_id}")
def get_analyses(product_id: uuid.UUID, db: Session = Depends(get_db)):
    service = ProfitService(db)
    return service.get_analyses(product_id)


@router.get("/analyses/detail/{analysis_id}")
def get_analysis(analysis_id: uuid.UUID, db: Session = Depends(get_db)):
    service = ProfitService(db)
    result = service.get_analysis(analysis_id)
    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return result


@router.patch("/analyses/detail/{analysis_id}")
def update_analysis(analysis_id: uuid.UUID, data: ProfitAnalysisCreate, db: Session = Depends(get_db)):
    service = ProfitService(db)
    result = service.update_analysis(analysis_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return result


@router.delete("/analyses/detail/{analysis_id}", status_code=204)
def delete_analysis(analysis_id: uuid.UUID, db: Session = Depends(get_db)):
    service = ProfitService(db)
    if not service.delete_analysis(analysis_id):
        raise HTTPException(status_code=404, detail="Analysis not found")