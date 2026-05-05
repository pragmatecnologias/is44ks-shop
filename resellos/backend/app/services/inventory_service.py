from sqlalchemy.orm import Session
import uuid
from typing import Optional

from app.models.supplier import InventoryItem
from app.schemas.product_schema import InventoryItemCreate, InventoryItemUpdate


class InventoryService:
    def __init__(self, db: Session):
        self.db = db

    def create_item(self, product_id: uuid.UUID, data: InventoryItemCreate) -> InventoryItem:
        item = InventoryItem(
            product_id=product_id,
            quantity_on_hand=data.quantity_on_hand,
            quantity_ordered=data.quantity_ordered,
            average_landed_cost=data.average_landed_cost,
            location_code=data.location_code,
            reorder_point=data.reorder_point,
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def get_item(self, product_id: uuid.UUID) -> Optional[InventoryItem]:
        return self.db.query(InventoryItem).filter(InventoryItem.product_id == product_id).first()

    def update_item(self, product_id: uuid.UUID, data: InventoryItemUpdate) -> Optional[InventoryItem]:
        item = self.get_item(product_id)
        if not item:
            return None
        update = data.model_dump(exclude_unset=True)
        for key, value in update.items():
            setattr(item, key, value)
        self.db.commit()
        self.db.refresh(item)
        return item

    def adjust_quantity(self, product_id: uuid.UUID, sold: int = 0, returned: int = 0, ordered: int = 0) -> Optional[InventoryItem]:
        item = self.get_item(product_id)
        if not item:
            return None
        if sold:
            item.quantity_on_hand = max(0, item.quantity_on_hand - sold)
            item.quantity_sold = item.quantity_sold + sold
        if returned:
            item.quantity_on_hand = item.quantity_on_hand + returned
            item.quantity_returned = item.quantity_returned + returned
        if ordered:
            item.quantity_ordered = item.quantity_ordered + ordered
        self.db.commit()
        self.db.refresh(item)
        return item