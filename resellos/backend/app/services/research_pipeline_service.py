from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from app.config import settings
from app.models.product import Product
from app.models.supplier import (
    AgentReport,
    CompetitorListing,
    MarketplaceEvidence,
    MarketplaceResearch,
    ProductSource,
)
from app.services.agent_utils import agent_data


@dataclass
class ResearchPipelineContext:
    product: Product
    sources: list[ProductSource]
    marketplace_research: list[MarketplaceResearch]
    competitor_listings: list[CompetitorListing]
    marketplace_evidence: list[MarketplaceEvidence]


class ResearchPipelineService:
    """Runs the product research loop in a deterministic order."""

    def __init__(self, db: Session, agents: dict[str, Any]):
        self.db = db
        self.agents = agents

    async def run_research_pipeline(self, product_id: uuid.UUID) -> dict[str, Any]:
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return {"error": "Product not found"}

        product.status = "RESEARCHING"
        self.db.commit()

        sources = self.db.query(ProductSource).filter(ProductSource.product_id == product_id).all()
        research_rows = self.db.query(MarketplaceResearch).filter(MarketplaceResearch.product_id == product_id).all()
        competitor_rows = self.db.query(CompetitorListing).filter(CompetitorListing.product_id == product_id).all()
        evidence_rows = self.db.query(MarketplaceEvidence).filter(MarketplaceEvidence.product_id == product_id).all()

        context = ResearchPipelineContext(
            product=product,
            sources=sources,
            marketplace_research=research_rows,
            competitor_listings=competitor_rows,
            marketplace_evidence=evidence_rows,
        )

        results: dict[str, dict[str, Any]] = {}

        risk_agent = self.agents.get("risk")
        if risk_agent:
            risk_input = {
                "product": self._serialize_product(product),
                "supplier_title": self._primary_source(sources).supplier_name if sources else None,
                "supplier_notes": self._primary_source(sources).notes if sources else None,
                "marketplace_notes": self._marketplace_notes(research_rows, evidence_rows),
                "competitor_listings": [self._serialize_competitor(row) for row in competitor_rows],
            }
            risk_result = await risk_agent.run(risk_input)
            results["risk_agent"] = risk_result
            self._save_agent_report(product_id, "risk_agent", risk_input, risk_result)

            risk_data = agent_data(results, "risk_agent")
            if risk_data.get("blocked", False):
                product.status = "BLOCKED"
                product.risk_level = risk_data.get("risk_level", "BLOCKED")
                product.final_decision = "BLOCKED"
                product.final_score = 0
                product.expected_profit = 0
                self.db.commit()
                return {
                    "status": "blocked",
                    "decision": "BLOCKED",
                    "final_decision": "BLOCKED",
                    "final_score": 0,
                    "reports": results,
                    "next_action": "Resolve risk flags before moving forward.",
                }

        market_agent = self.agents.get("market")
        market_result = None
        if market_agent:
            market_input = {
                "product": self._serialize_product(product),
                "marketplace_research": [self._serialize_market_research(row) for row in research_rows],
                "competitor_listings": [self._serialize_competitor(row) for row in competitor_rows],
                "marketplace_evidence": [self._serialize_evidence(row) for row in evidence_rows],
            }
            market_result = await market_agent.run(market_input)
            results["market_agent"] = market_result
            self._save_agent_report(product_id, "market_agent", market_input, market_result)

        profit_agent = self.agents.get("profit")
        profit_result = None
        if profit_agent:
            primary_source = self._primary_source(sources)
            market_data = agent_data(results, "market_agent")
            sale_price = float(market_data.get("median_sold_price") or market_data.get("median_active_price") or 0)
            if sale_price <= 0:
                sale_price = 29.99

            profit_input = {
                "expected_sale_price": sale_price,
                "product_cost": float(primary_source.unit_cost or 0) if primary_source else 0,
                "china_domestic_shipping": float(primary_source.domestic_shipping or 0) if primary_source else 0,
                "international_shipping": float(primary_source.international_shipping_estimate or 0) if primary_source else 0,
                "duties": 0,
                "inspection_cost": 0,
                "platform_fee_percent": settings.DEFAULT_MARKETPLACE_FEE_PERCENT / 100,
                "platform_fee_fixed": 0,
                "payment_fee": 0,
                "outbound_shipping": float(settings.DEFAULT_PACKAGING_COST),
                "packaging": float(settings.DEFAULT_PACKAGING_COST),
                "return_allowance": float(settings.DEFAULT_RETURN_ALLOWANCE),
                "ad_cost": 0,
                "buyer_paid_shipping": False,
                "free_shipping": True,
                "bundle_quantity": 2,
                "quantity_ordered": 1,
                "damaged_unit_allowance": 0,
            }
            profit_result = await profit_agent.run({"profit_input": profit_input})
            results["profit_agent"] = profit_result
            self._save_agent_report(product_id, "profit_agent", profit_input, profit_result)

        decision_agent = self.agents.get("decision")
        decision_result = None
        if decision_agent:
            decision_input = {
                "product": self._serialize_product(product),
                "agent_reports": results,
            }
            decision_result = await decision_agent.run(decision_input)
            results["decision_agent"] = decision_result
            self._save_agent_report(product_id, "decision_agent", decision_input, decision_result)

        if decision_result:
            decision_data = agent_data(results, "decision_agent")
            profit_data = agent_data(results, "profit_agent")
            product.final_score = decision_data.get("total_score", 0)
            product.final_decision = decision_data.get("recommendation", "SKIP")
            product.target_sale_price = profit_data.get("break_even_price")
            product.expected_profit = profit_data.get("estimated_net_profit")
            product.risk_level = agent_data(results, "risk_agent").get("risk_level", product.risk_level)

            if product.final_decision in {"BUY_SAMPLE", "BUY_SMALL_BATCH"}:
                product.status = "BUY_SAMPLE"
            elif product.final_decision == "WATCHLIST":
                product.status = "WATCHLIST"
            elif product.final_decision == "BLOCKED":
                product.status = "BLOCKED"
            else:
                product.status = "NEEDS_RESEARCH"

            self.db.commit()

        return {
            "product_id": product_id,
            "status": product.status,
            "final_decision": product.final_decision,
            "final_score": float(product.final_score) if product.final_score is not None else None,
            "reports": results,
        }

    def _serialize_product(self, product: Product) -> dict[str, Any]:
        return {
            "id": str(product.id),
            "name": product.name,
            "category": product.category,
            "subcategory": product.subcategory,
            "description": product.description,
        }

    def _serialize_market_research(self, row: MarketplaceResearch) -> dict[str, Any]:
        return {
            "marketplace": row.marketplace,
            "active_listing_count": row.active_listing_count or 0,
            "sold_listing_count": row.sold_listing_count or 0,
            "median_active_price": float(row.median_active_price) if row.median_active_price is not None else None,
            "median_sold_price": float(row.median_sold_price) if row.median_sold_price is not None else None,
            "evidence_quality": row.evidence_quality,
        }

    def _serialize_competitor(self, row: CompetitorListing) -> dict[str, Any]:
        return {
            "marketplace": row.marketplace,
            "title": row.title,
            "price": float(row.price) if row.price is not None else None,
            "shipping_price": float(row.shipping_price) if row.shipping_price is not None else None,
            "sold": row.sold,
            "notes": row.notes,
        }

    def _serialize_evidence(self, row: MarketplaceEvidence) -> dict[str, Any]:
        return {
            "marketplace": row.marketplace,
            "evidence_type": row.evidence_type,
            "title": row.title,
            "url": row.url,
            "price": float(row.price) if row.price is not None else None,
            "shipping_price": float(row.shipping_price) if row.shipping_price is not None else None,
            "source_method": row.source_method,
            "raw_text": row.raw_text,
            "confidence": row.confidence,
        }

    def _primary_source(self, sources: list[ProductSource]) -> ProductSource | None:
        if not sources:
            return None
        return next((source for source in sources if source.is_primary), sources[0])

    def _marketplace_notes(self, research_rows: list[MarketplaceResearch], evidence_rows: list[MarketplaceEvidence]) -> str:
        notes = [row.notes for row in research_rows if row.notes]
        notes.extend(row.notes for row in evidence_rows if row.notes)
        notes.extend(row.raw_text for row in evidence_rows if row.raw_text)
        return "\n".join(notes)

    def _save_agent_report(self, product_id: uuid.UUID, agent_type: str, input_data: dict[str, Any], result: dict[str, Any]) -> AgentReport:
        report = AgentReport(
            product_id=product_id,
            agent_name=agent_type,
            report_type=agent_type,
            input_json=json.dumps(input_data, default=str),
            output_json=json.dumps(result.get("output_json", {}), default=str),
            summary=result.get("summary", ""),
            confidence=str(result.get("confidence", "")) if result.get("confidence") else None,
        )
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report


ProductResearchService = ResearchPipelineService
