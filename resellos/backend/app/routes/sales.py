from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.db import get_db
from app.schemas.product_schema import SaleCreate
from app.services.sale_service import SaleService
from app.models.product import Product

router = APIRouter(prefix="/api/sales", tags=["sales"])


@router.post("/{product_id}", status_code=201)
def create_sale(product_id: uuid.UUID, data: SaleCreate, db: Session = Depends(get_db)):
    service = SaleService(db)
    return service.create_sale(product_id, data)


@router.get("", response_model=List[dict])
def list_sales(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = SaleService(db)
    return service.get_all_sales(skip, limit)


@router.get("/{sale_id}", response_model=dict)
def get_sale(sale_id: uuid.UUID, db: Session = Depends(get_db)):
    service = SaleService(db)
    result = service.get_sale(sale_id)
    if not result:
        raise HTTPException(status_code=404, detail="Sale not found")
    return result


@router.get("/product/{product_id}", response_model=List[dict])
def get_product_sales(product_id: uuid.UUID, db: Session = Depends(get_db)):
    service = SaleService(db)
    return service.get_sales(product_id)