from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from app.db import get_db
from app.schemas.product_schema import ResearchRunResponse, ResearchCockpitResponse
from app.services.research_pipeline_service import ProductResearchService
from app.llm import get_llm_provider
from app.agents import RiskAgent, MarketAgent, ProfitAgent, ListingAgent, DecisionAgent
from app.models.supplier import MarketplaceResearch, CompetitorListing, MarketplaceEvidence, ProductSource, ProfitAnalysis, AgentReport


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

    result = await service.run_research_pipeline(product_id)
    reports = []
    for name, report in result.get("reports", {}).items():
        reports.append(
            {
                "id": uuid.uuid4(),
                "product_id": product_id,
                "agent_name": name,
                "report_type": name,
                "summary": report.get("summary", ""),
                "confidence": report.get("confidence"),
                "created_at": report.get("created_at", ""),
            }
        )

    return ResearchRunResponse(
        product_id=product_id,
        status=result.get("status", product.status),
        final_decision=result.get("final_decision"),
        final_score=float(result.get("final_score")) if result.get("final_score") is not None else None,
        decision=result.get("reports", {}).get("decision_agent", {}).get("output_json"),
        reports=reports,
    )


@router.get("/{product_id}/research/cockpit", response_model=ResearchCockpitResponse)
def get_research_cockpit(product_id: uuid.UUID, db: Session = Depends(get_db)):
    from app.models.product import Product

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    sources = db.query(ProductSource).filter(ProductSource.product_id == product_id).all()
    research_rows = db.query(MarketplaceResearch).filter(MarketplaceResearch.product_id == product_id).all()
    evidence_rows = db.query(MarketplaceEvidence).filter(MarketplaceEvidence.product_id == product_id).all()
    competitor_rows = db.query(CompetitorListing).filter(CompetitorListing.product_id == product_id).all()
    profit_rows = db.query(ProfitAnalysis).filter(ProfitAnalysis.product_id == product_id).all()
    agent_rows = db.query(AgentReport).filter(AgentReport.product_id == product_id).all()

    decision = next((row for row in agent_rows if row.agent_name == "decision_agent"), None)
    decision_output = None
    if decision and decision.output_json:
        import json

        decision_output = json.loads(decision.output_json)

    missing_evidence = []
    if not any(row.evidence_type == "SOLD_LISTING" for row in evidence_rows):
        missing_evidence.append("Sold listings missing")
    if not any(row.evidence_type == "ACTIVE_LISTING" for row in evidence_rows):
        missing_evidence.append("Active listings missing")
    if not sources:
        missing_evidence.append("Supplier comparison missing")
    if not profit_rows:
        missing_evidence.append("Profit scenarios missing")

    return ResearchCockpitResponse(
        product=product,
        sources=sources,
        marketplace_research=[_serialize_model(row) for row in research_rows],
        marketplace_evidence=[_serialize_model(row) for row in evidence_rows],
        competitor_listings=[_serialize_model(row) for row in competitor_rows],
        profit_analyses=[_serialize_model(row) for row in profit_rows],
        agent_reports=[_serialize_model(row) for row in agent_rows],
        decision=decision_output,
        missing_evidence=missing_evidence,
        next_action=(decision_output or {}).get("next_action") if decision_output else None,
        confidence=(decision_output or {}).get("confidence") if decision_output else None,
        current_status=product.status,
    )


def _serialize_model(row):
    if hasattr(row, "model_dump"):
        data = row.model_dump()
    else:
        data = {}
        for key in dir(row):
            if key.startswith("_"):
                continue
    # SQLAlchemy + Pydantic compatibility shim
    if data:
        return data
    out = {}
    for key in row.__table__.columns.keys():
        value = getattr(row, key)
        try:
            import uuid as _uuid
            if isinstance(value, _uuid.UUID):
                out[key] = str(value)
            else:
                out[key] = value
        except Exception:
            out[key] = value
    return out
