from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from app.db import get_db
from app.schemas.product_schema import ResearchRunResponse
from app.services.research_pipeline_service import ProductResearchService
from app.llm import get_llm_provider
from app.agents import RiskAgent, MarketAgent, ProfitAgent, ListingAgent, DecisionAgent


router = APIRouter(prefix="/api/products", tags=["research"])


def _get_agents() -> dict:
    """Get all available agents with LLM provider."""
    llm = get_llm_provider()
    return {
        "risk": RiskAgent(llm),
        "market": MarketAgent(llm),
        "profit": ProfitAgent(llm),
        "listing": ListingAgent(llm),
        "decision": DecisionAgent(llm),
    }


@router.post("/{product_id}/research/run", response_model=ResearchRunResponse)
async def run_research(product_id: uuid.UUID, db: Session = Depends(get_db)):
    """Run the full research pipeline for a product."""
    from app.models.product import Product

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    agents = _get_agents()
    service = ProductResearchService(db, agents)

    # Convert agents to sync-friendly wrapper
    class SyncAgentWrapper:
        def __init__(self, async_agent):
            self._agent = async_agent

        def run(self, input_data: dict):
            import asyncio
            return asyncio.run(self._agent.run(input_data))

    sync_agents = {k: SyncAgentWrapper(v) for k, v in agents.items()}
    service.agents = sync_agents

    result = service.run_research_pipeline(product_id)

    reports = []
    for name, report in result.get("reports", {}).items():
        reports.append({
            "id": uuid.uuid4(),
            "product_id": product_id,
            "agent_name": name,
            "report_type": name,
            "summary": report.get("summary", ""),
            "confidence": report.get("confidence"),
            "created_at": report.get("created_at", ""),
        })

    return ResearchRunResponse(
        product_id=product_id,
        status=result.get("status", product.status),
        final_decision=result.get("final_decision"),
        final_score=float(result.get("final_score")) if result.get("final_score") else None,
        reports=reports,
    )