from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.db import get_db
from app.schemas.product_schema import (
    ProductCreate, ProductResponse, ProductUpdate,
    SupplierCreate, SupplierResponse,
)
from app.services.product_service import ProductService
from app.services.supplier_service import SupplierService

router = APIRouter(prefix="/api/products", tags=["products"])


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    service = ProductService(db)
    return service.create_product(db, product)


@router.get("", response_model=List[ProductResponse])
def list_products(skip: int = 0, limit: int = 100, status: str = None, db: Session = Depends(get_db)):
    service = ProductService(db)
    if status:
        return service.get_products_by_status(db, status)
    return service.get_products(db, skip, limit)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: uuid.UUID, db: Session = Depends(get_db)):
    service = ProductService(db)
    product = service.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(product_id: uuid.UUID, data: ProductUpdate, db: Session = Depends(get_db)):
    service = ProductService(db)
    product = service.update_product(db, product_id, data)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: uuid.UUID, db: Session = Depends(get_db)):
    service = ProductService(db)
    if not service.delete_product(db, product_id):
        raise HTTPException(status_code=404, detail="Product not found")


# --- Product Sources (Suppliers) ---
supplier_router = APIRouter(prefix="/api/products/{product_id}/sources", tags=["suppliers"])


@supplier_router.post("", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
def create_source(product_id: uuid.UUID, data: SupplierCreate, db: Session = Depends(get_db)):
    service = SupplierService(db)
    return service.create_source(product_id, data)


@supplier_router.get("", response_model=List[SupplierResponse])
def list_sources(product_id: uuid.UUID, db: Session = Depends(get_db)):
    service = SupplierService(db)
    return service.get_sources(product_id)


@supplier_router.patch("/{source_id}", response_model=SupplierResponse)
def update_source(product_id: uuid.UUID, source_id: uuid.UUID, data: SupplierCreate, db: Session = Depends(get_db)):
    service = SupplierService(db)
    result = service.update_source(source_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Source not found")
    return result


@supplier_router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_source(product_id: uuid.UUID, source_id: uuid.UUID, db: Session = Depends(get_db)):
    service = SupplierService(db)
    if not service.delete_source(source_id):
        raise HTTPException(status_code=404, detail="Source not found")