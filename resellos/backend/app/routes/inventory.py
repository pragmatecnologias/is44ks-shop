from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from app.db import get_db
from app.schemas.product_schema import InventoryCreate
from app.services.inventory_service import InventoryService

router = APIRouter(prefix="/api/inventory", tags=["inventory"])


@router.post("/{product_id}", status_code=201)
def create_inventory_item(product_id: uuid.UUID, data: InventoryCreate, db: Session = Depends(get_db)):
    service = InventoryService(db)
    return service.create_item(product_id, data)


@router.get("/{product_id}")
def get_inventory(product_id: uuid.UUID, db: Session = Depends(get_db)):
    service = InventoryService(db)
    result = service.get_item(product_id)
    if not result:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return result


@router.patch("/{product_id}")
def update_inventory(product_id: uuid.UUID, data: InventoryCreate, db: Session = Depends(get_db)):
    service = InventoryService(db)
    result = service.update_item(product_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return result


@router.post("/{product_id}/adjust")
def adjust_inventory(product_id: uuid.UUID, sold: int = 0, returned: int = 0, ordered: int = 0, db: Session = Depends(get_db)):
    service = InventoryService(db)
    result = service.adjust_quantity(product_id, sold, returned, ordered)
    if not result:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return result