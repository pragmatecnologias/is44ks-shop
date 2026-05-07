from datetime import datetime
from sqlalchemy.orm import Session
import uuid
from typing import Optional

from app.models.product import Product
from app.models.supplier import ProductSource
from app.schemas.product_schema import SupplierCreate, SupplierEconomicsUpdate


class SupplierService:
    def __init__(self, db: Session):
        self.db = db

    def create_source(self, product_id: uuid.UUID, data: SupplierCreate) -> ProductSource:
        source = ProductSource(
            product_id=product_id,
            supplier_name=data.supplier_name,
            supplier_platform=data.supplier_platform,
            supplier_url=data.supplier_url,
            unit_cost=data.unit_cost,
            domestic_shipping=data.domestic_shipping,
            international_shipping_estimate=data.international_shipping_estimate,
            estimated_landed_cost=data.estimated_landed_cost,
            moq=data.moq,
            supplier_rating=data.supplier_rating,
            notes=data.notes,
            is_primary=data.is_primary,
        )
        self.db.add(source)
        self.db.commit()
        self.db.refresh(source)
        return source

    def get_sources(self, product_id: uuid.UUID) -> list[ProductSource]:
        return self.db.query(ProductSource).filter(ProductSource.product_id == product_id).all()

    def get_source(self, source_id: uuid.UUID) -> Optional[ProductSource]:
        return self.db.query(ProductSource).filter(ProductSource.id == source_id).first()

    def update_source(self, source_id: uuid.UUID, data: SupplierCreate) -> Optional[ProductSource]:
        source = self.get_source(source_id)
        if not source:
            return None
        update = data.model_dump(exclude_unset=True)
        for key, value in update.items():
            setattr(source, key, value)
        self.db.commit()
        self.db.refresh(source)
        return source

    def delete_source(self, source_id: uuid.UUID) -> bool:
        source = self.get_source(source_id)
        if not source:
            return False
        self.db.delete(source)
        self.db.commit()
        return True

    def update_economics(self, source_id: uuid.UUID, data: SupplierEconomicsUpdate) -> Optional[ProductSource]:
        source = self.get_source(source_id)
        if not source:
            return None
        source.unit_cost = data.unit_cost
        source.currency = data.currency
        source.moq = data.moq
        source.domestic_shipping = data.shipping_cost
        source.estimated_landed_cost = data.estimated_landed_cost
        source.quantity_basis = data.quantity_basis
        source.proof_text = data.proof_text
        source.manual_verification_note = data.manual_verification_note
        source.confidence_level = data.confidence_level
        source.verified_by_source = data.verified_by_source
        source.economics_verified = True
        source.verified_at = datetime.utcnow()
        source.verification_status = "USER_VERIFIED"
        self.db.commit()
        self.db.refresh(source)
        return source

    def update_economics_for_product(
        self, product_id: uuid.UUID, source_id: uuid.UUID, data: SupplierEconomicsUpdate
    ) -> Optional[ProductSource]:
        """Update economics only if source belongs to the given product_id."""
        source = self.get_source(source_id)
        if not source:
            return None
        if source.product_id != product_id:
            return None
        source.unit_cost = data.unit_cost
        source.currency = data.currency
        source.moq = data.moq
        source.domestic_shipping = data.shipping_cost
        source.estimated_landed_cost = data.estimated_landed_cost
        source.quantity_basis = data.quantity_basis
        source.proof_text = data.proof_text
        source.manual_verification_note = data.manual_verification_note
        source.confidence_level = data.confidence_level
        source.verified_by_source = data.verified_by_source
        source.economics_verified = True
        source.verified_at = datetime.utcnow()
        source.verification_status = "USER_VERIFIED"
        self.db.commit()
        self.db.refresh(source)
        return source