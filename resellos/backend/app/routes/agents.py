from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid
import json

from app.db import get_db
from app.services.agent_service import AgentService
from app.models.product import Product

router = APIRouter(prefix="/api/agents", tags=["agents"])


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
    from app.llm import get_llm_provider
    from app.agents import RiskAgent, MarketAgent, CompetitionAgent, ProfitAgent, ReorderAgent, ListingAgent, DecisionAgent

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    llm = get_llm_provider()

    agent_map = {
        "risk": RiskAgent,
        "market": MarketAgent,
        "competition": CompetitionAgent,
        "profit": ProfitAgent,
        "reorder": ReorderAgent,
        "listing": ListingAgent,
        "decision": DecisionAgent,
    }

    agent_cls = agent_map.get(agent_type)
    if not agent_cls:
        raise HTTPException(status_code=400, detail=f"Unknown agent type: {agent_type}")

    agent = agent_cls(llm)

    if agent_type == "risk":
        context = {"product": {"name": product.name, "category": product.category, "description": product.description}}
    elif agent_type == "market":
        context = {"product": {"name": product.name, "category": product.category}}
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
