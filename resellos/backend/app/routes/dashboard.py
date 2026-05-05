from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.product import Product
from app.models.supplier import MarketplaceResearch, CompetitorListing, MarketplaceEvidence, AgentReport

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    categories = (
        db.query(Product.category, func.count(Product.id))
        .group_by(Product.category)
        .order_by(func.count(Product.id).desc())
        .limit(5)
        .all()
    )

    total_products = len(products)
    blocked_count = sum(1 for product in products if product.status == "BLOCKED")
    watchlist_count = sum(1 for product in products if product.status == "WATCHLIST")
    buy_sample_candidates = sum(1 for product in products if product.status in {"BUY_SAMPLE", "BUY_SMALL_BATCH"})
    products_ordered = sum(1 for product in products if product.status in {"SAMPLE_ORDERED", "SAMPLE_RECEIVED", "APPROVED_TO_LIST", "LISTED", "SELLING"})
    products_listed = sum(1 for product in products if product.status in {"APPROVED_TO_LIST", "LISTED", "SELLING", "SLOW_MOVING", "REORDER_CANDIDATE", "REORDERED"})

    recent_products = [_serialize_product(product) for product in sorted(products, key=lambda item: item.updated_at or item.created_at, reverse=True)[:5]]
    reorder_recommendations = [_serialize_product(product) for product in products if product.status == "REORDER_CANDIDATE"][:5]

    agent_activity_rows = (
        db.query(AgentReport)
        .order_by(AgentReport.created_at.desc())
        .limit(8)
        .all()
    )

    return {
        "total_products": total_products,
        "blocked_count": blocked_count,
        "watchlist_count": watchlist_count,
        "buy_sample_candidates": buy_sample_candidates,
        "products_ordered": products_ordered,
        "products_listed": products_listed,
        "top_categories": [
            {"category": category or "Uncategorized", "count": count}
            for category, count in categories
        ],
        "recent_products": recent_products,
        "reorder_recommendations": reorder_recommendations,
        "agent_activity": [
            {
                "agent_type": report.agent_name.replace("_agent", ""),
                "status": "completed",
                "summary": report.summary,
                "confidence": report.confidence,
                "started_at": report.created_at,
                "completed_at": report.created_at,
            }
            for report in agent_activity_rows
        ],
    }


def _serialize_product(product: Product) -> dict:
    return {
        "id": str(product.id),
        "sku": product.sku,
        "name": product.name,
        "category": product.category,
        "subcategory": product.subcategory,
        "description": product.description,
        "status": product.status,
        "risk_level": product.risk_level,
        "final_score": float(product.final_score) if product.final_score is not None else None,
        "final_decision": product.final_decision,
        "target_sale_price": float(product.target_sale_price) if product.target_sale_price is not None else None,
        "expected_profit": float(product.expected_profit) if product.expected_profit is not None else None,
        "created_at": product.created_at,
        "updated_at": product.updated_at,
    }
