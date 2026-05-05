import re
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.supplier import ProductSource
from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductResponse


def generate_sku(name: str, existing_count: int = 0) -> str:
    """Generate SKU from product name per spec section 13.1"""
    # Remove special chars, convert to uppercase, hyphenate words
    words = re.findall(r'[A-Za-z0-9]+', name)
    base = '-'.join(w.upper()[:8] for w in words[:4])
    count = existing_count + 1
    return f"{base}-{count:03d}"


class ProductService:
    def __init__(self, db: Session):
        self.db = db

    def create_product(self, product_data: ProductCreate) -> Product:
        existing_count = self.db.query(Product).count()
        sku = generate_sku(product_data.name, existing_count)

        product = Product(
            id=uuid.uuid4(),
            sku=sku,
            name=product_data.name,
            category=product_data.category,
            subcategory=product_data.subcategory,
            description=product_data.description,
            status='NEW',
        )
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def get_product(self, db: Session, product_id: uuid.UUID) -> Optional[Product]:
        return db.query(Product).filter(Product.id == product_id).first()

    def get_products(self, db: Session, skip: int = 0, limit: int = 100) -> List[Product]:
        return db.query(Product).offset(skip).limit(limit).all()

    def get_products_by_status(self, db: Session, status: str) -> List[Product]:
        return db.query(Product).filter(Product.status == status).all()

    def update_product(self, db: Session, product_id: uuid.UUID, data: ProductUpdate) -> Optional[Product]:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)
        product.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(product)
        return product

    def delete_product(self, db: Session, product_id: uuid.UUID) -> bool:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return False
        db.delete(product)
        db.commit()
        return True

    def get_product_sources(self, db: Session, product_id: uuid.UUID) -> List[ProductSource]:
        return db.query(ProductSource).filter(ProductSource.product_id == product_id).all()
