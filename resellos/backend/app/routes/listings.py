from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.db import get_db
from app.schemas.product_schema import ListingGenerateRequest
from app.services.listing_service import ListingService
from app.models.product import Product

router = APIRouter(prefix="/api/listings", tags=["listings"])


@router.get("", response_model=List[dict])
def list_listings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all generated listings across all products."""
    service = ListingService(db)
    return service.get_all_listing_reports(skip, limit)


@router.get("/{product_id}")
def get_listing(product_id: uuid.UUID, db: Session = Depends(get_db)):
    """Get listing generation report for a specific product."""
    service = ListingService(db)
    result = service.get_listing_report(product_id)
    if not result:
        raise HTTPException(status_code=404, detail="No listing found for this product")
    return result


@router.post("/generate")
async def generate_listing(product_id: uuid.UUID, request: ListingGenerateRequest, db: Session = Depends(get_db)):
    """Generate listing content for a product using the ListingAgent."""
    from app.llm import get_llm_provider
    from app.agents import ListingAgent

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    llm = get_llm_provider()
    agent = ListingAgent(llm)

    context = {
        "listing_input": {
            "product_name": product.name,
            "description": product.description or "",
            "marketplace": request.marketplace,
            "features": request.product_features,
            "dimensions": request.dimensions,
            "photos": [],
            "competitor_weaknesses": [],
            "recommended_price": request.target_price,
        }
    }

    result = await agent.run(context)
    output = result.get("output_json", {})

    return {
        "title": output.get("ebay_title", product.name),
        "marketplace": request.marketplace,
        "short_description": output.get("short_description", ""),
        "long_description": output.get("long_description", ""),
        "bullet_points": output.get("bullet_points", []),
        "seo_keywords": output.get("seo_keywords", []),
        "photo_checklist": output.get("photo_checklist", []),
        "bundle_ideas": output.get("bundle_ideas", []),
        "pricing_strategy": output.get("pricing_strategy", ""),
    }