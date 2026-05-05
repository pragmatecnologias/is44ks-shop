from sqlalchemy.orm import Session
import uuid
from typing import Optional

from app.models.sale import Sale
from app.schemas.product_schema import SaleCreate


class SaleService:
    def __init__(self, db: Session):
        self.db = db

    def create_sale(self, product_id: uuid.UUID, data: SaleCreate) -> Sale:
        sale = Sale(
            product_id=product_id,
            marketplace=data.marketplace,
            sale_date=data.sale_date,
            quantity=data.quantity,
            sale_price=data.sale_price,
            marketplace_fee=data.marketplace_fee,
            shipping_cost=data.shipping_cost,
            packaging_cost=data.packaging_cost,
            net_profit=data.net_profit,
            buyer_paid_shipping=data.buyer_paid_shipping,
            returned=data.returned,
            notes=data.notes,
        )
        self.db.add(sale)
        self.db.commit()
        self.db.refresh(sale)
        return sale

    def get_sales(self, product_id: uuid.UUID) -> list[Sale]:
        return self.db.query(Sale).filter(Sale.product_id == product_id).all()

    def get_all_sales(self, skip: int = 0, limit: int = 100) -> list[Sale]:
        return self.db.query(Sale).offset(skip).limit(limit).all()

    def get_sale(self, sale_id: uuid.UUID) -> Optional[Sale]:
        return self.db.query(Sale).filter(Sale.id == sale_id).first()