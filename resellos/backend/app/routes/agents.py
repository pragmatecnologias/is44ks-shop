from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid
import json

from app.db import get_db
from app.services.agent_service import AgentService
from app.models.product import Product
from app.models.product_validation import ProductDemandResearch, ProductTrendResearch
from app.models.supplier import MarketplaceEvidence
from app.services.agent_factory import build_agents

router = APIRouter(prefix="/api/agents", tags=["agents"])


def _serialize_row(row):
    return {column: getattr(row, column) for column in row.__table__.columns.keys()}


@router.get("/reports/{product_id}")
def get_reports(product_id: uuid.UUID, db: Session = Depends(get_db)):
    service = AgentService(db)
    return service.get_reports(product_id)


@router.get("/reports/detail/{report_id}")
def get_report(report_id: uuid.UUID, db: Session = Depends(get_db)):
    service = AgentService(db)
    result = service.get_report(report_id)
    if not result:
        raise HTTPException(status_code=404, detail="Report not found")
    return result


@router.post("/run/{product_id}")
async def run_agent(product_id: uuid.UUID, agent_type: str, db: Session = Depends(get_db)):
    """Run a specific agent for a product and return results."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    agent_map = build_agents()

    agent = agent_map.get(agent_type)
    if not agent:
        raise HTTPException(status_code=400, detail=f"Unknown agent type: {agent_type}")

    if agent_type == "risk":
        context = {"product": {"name": product.name, "category": product.category, "description": product.description}}
    elif agent_type == "market":
        evidence_rows = db.query(MarketplaceEvidence).filter(MarketplaceEvidence.product_id == product_id).all()
        context = {
            "product": {"name": product.name, "category": product.category},
            "marketplace_evidence": [_serialize_row(row) for row in evidence_rows],
        }
    elif agent_type == "demand":
        demand_rows = db.query(ProductDemandResearch).filter(ProductDemandResearch.product_id == product_id).all()
        context = {
            "product": {"name": product.name, "category": product.category},
            "demand_research": [_serialize_row(row) for row in demand_rows],
        }
    elif agent_type == "trend":
        trend_rows = db.query(ProductTrendResearch).filter(ProductTrendResearch.product_id == product_id).all()
        context = {
            "product": {"name": product.name, "category": product.category},
            "trend_research": [_serialize_row(row) for row in trend_rows],
        }
    elif agent_type == "competition":
        context = {"product": {"name": product.name, "category": product.category}, "competitor_listings": []}
    elif agent_type == "profit":
        context = {"profit_input": {"expected_sale_price": 50, "product_cost": 10}}
    elif agent_type == "reorder":
        context = {"product": {"name": product.name}, "inventory": [], "sales": []}
    elif agent_type == "listing":
        context = {"listing_input": {"product_name": product.name, "marketplace": "ebay"}}
    else:
        context = {}

    result = await agent.run(context)

    service = AgentService(db)
    service.save_report(
        product_id=product_id,
        agent_name=agent_type,
        report_type=agent_type,
        input_json=json.dumps(context),
        output_json=json.dumps(result.get("output_json", {})),
        summary=result.get("summary", ""),
        confidence=result.get("confidence"),
    )

    return result
