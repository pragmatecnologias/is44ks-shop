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
    InventoryItem,
    MarketplaceEvidence,
    MarketplaceResearch,
    ProfitAnalysis,
    Sale,
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
    inventory_items: list[InventoryItem]
    sales: list[Sale]


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
        inventory_rows = self.db.query(InventoryItem).filter(InventoryItem.product_id == product_id).all()
        sales_rows = self.db.query(Sale).filter(Sale.product_id == product_id).all()
        primary_source = self._primary_source(sources)

        context = ResearchPipelineContext(
            product=product,
            sources=sources,
            marketplace_research=research_rows,
            competitor_listings=competitor_rows,
            marketplace_evidence=evidence_rows,
            inventory_items=inventory_rows,
            sales=sales_rows,
        )

        results: dict[str, dict[str, Any]] = {}

        risk_agent = self.agents.get("risk")
        if risk_agent:
            risk_input = {
                "product": self._serialize_product(product),
                "supplier_title": primary_source.supplier_name if primary_source else None,
                "supplier_notes": primary_source.notes if primary_source else None,
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

        competition_agent = self.agents.get("competition")
        competition_result = None
        if competition_agent:
            competition_input = {
                "product": self._serialize_product(product),
                "market_summary": agent_data(results, "market_agent"),
                "competitor_listings": [self._serialize_competitor(row) for row in competitor_rows],
                "marketplace_evidence": [self._serialize_evidence(row) for row in evidence_rows],
            }
            competition_result = await competition_agent.run(competition_input)
            results["competition_agent"] = competition_result
            self._save_agent_report(product_id, "competition_agent", competition_input, competition_result)

        profit_agent = self.agents.get("profit")
        profit_result = None
        if profit_agent:
            market_data = agent_data(results, "market_agent")
            sale_price = float(market_data.get("median_sold_price") or market_data.get("median_active_price") or 0)

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
                "outbound_shipping": float(settings.DEFAULT_OUTBOUND_SHIPPING),
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
            self._persist_profit_scenarios(product_id, profit_input, profit_result)

        reorder_agent = self.agents.get("reorder")
        reorder_result = None
        if reorder_agent:
            reorder_input = {
                "product": self._serialize_product(product),
                "inventory": [self._serialize_inventory(row) for row in inventory_rows],
                "sales": [self._serialize_sale(row) for row in sales_rows],
                "profit_summary": agent_data(results, "profit_agent"),
                "market_summary": agent_data(results, "market_agent"),
            }
            reorder_result = await reorder_agent.run(reorder_input)
            results["reorder_agent"] = reorder_result
            self._save_agent_report(product_id, "reorder_agent", reorder_input, reorder_result)

        decision_agent = self.agents.get("decision")
        decision_result = None
        if decision_agent:
            decision_input = {
                "product": self._serialize_product(product),
                "supplier_summary": self._serialize_source(primary_source) if primary_source else {},
                "agent_reports": results,
            }
            decision_result = await decision_agent.run(decision_input)
            results["decision_agent"] = decision_result
            self._save_agent_report(product_id, "decision_agent", decision_input, decision_result)

        listing_agent = self.agents.get("listing")
        if listing_agent:
            listing_input = {
                "product": self._serialize_product(product),
                "supplier_summary": self._serialize_source(primary_source) if primary_source else {},
                "market_summary": agent_data(results, "market_agent"),
                "profit_summary": agent_data(results, "profit_agent"),
                "decision_summary": agent_data(results, "decision_agent"),
                "competitor_listings": [self._serialize_competitor(row) for row in competitor_rows],
            }
            listing_result = await listing_agent.run({"listing_input": listing_input})
            results["listing_agent"] = listing_result
            self._save_agent_report(product_id, "listing_agent", listing_input, listing_result)

        if decision_result:
            decision_data = agent_data(results, "decision_agent")
            profit_data = agent_data(results, "profit_agent")
            competition_data = agent_data(results, "competition_agent")
            reorder_data = agent_data(results, "reorder_agent")
            product.final_score = decision_data.get("total_score", 0)
            product.final_decision = decision_data.get("recommendation", "SKIP")
            product.target_sale_price = profit_data.get("target_sale_price") or None
            product.expected_profit = profit_data.get("estimated_net_profit")
            product.risk_level = agent_data(results, "risk_agent").get("risk_level", product.risk_level)

            if product.final_decision == "BUY_SAMPLE":
                product.status = "BUY_SAMPLE"
            elif product.final_decision == "BUY_SMALL_BATCH":
                product.status = "BUY_SMALL_BATCH"
            elif product.final_decision == "WATCHLIST":
                product.status = "WATCHLIST"
            elif product.final_decision == "BLOCKED":
                product.status = "BLOCKED"
            else:
                product.status = "NEEDS_RESEARCH"

            if competition_data.get("can_compete") is False and product.status in {"BUY_SAMPLE", "BUY_SMALL_BATCH"}:
                product.status = "WATCHLIST"

            if reorder_data.get("reorder_recommendation") == "KILL_PRODUCT":
                product.status = "KILL_PRODUCT"
            elif reorder_data.get("reorder_recommendation") in {"REORDER_SMALL", "REORDER_MEDIUM", "SCALE"}:
                if inventory_rows or sales_rows:
                    product.status = "REORDER_CANDIDATE"

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
            "verification_status": row.verification_status,
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
            "verification_status": row.verification_status,
            "raw_text": row.raw_text,
            "confidence": row.confidence,
        }

    def _serialize_inventory(self, row: InventoryItem) -> dict[str, Any]:
        return {
            "quantity_on_hand": row.quantity_on_hand,
            "quantity_ordered": row.quantity_ordered,
            "quantity_sold": row.quantity_sold,
            "quantity_returned": row.quantity_returned,
            "average_landed_cost": float(row.average_landed_cost) if row.average_landed_cost is not None else None,
            "location_code": row.location_code,
            "reorder_point": row.reorder_point,
        }

    def _serialize_sale(self, row: Sale) -> dict[str, Any]:
        return {
            "marketplace": row.marketplace,
            "sale_date": row.sale_date.isoformat() if row.sale_date else None,
            "quantity": row.quantity,
            "sale_price": float(row.sale_price) if row.sale_price is not None else None,
            "marketplace_fee": float(row.marketplace_fee) if row.marketplace_fee is not None else None,
            "shipping_cost": float(row.shipping_cost) if row.shipping_cost is not None else None,
            "packaging_cost": float(row.packaging_cost) if row.packaging_cost is not None else None,
            "net_profit": float(row.net_profit) if row.net_profit is not None else None,
            "buyer_paid_shipping": row.buyer_paid_shipping,
            "returned": row.returned,
            "notes": row.notes,
        }

    def _serialize_source(self, source: ProductSource | None) -> dict[str, Any]:
        if not source:
            return {}
        return {
            "supplier_name": source.supplier_name,
            "supplier_platform": source.supplier_platform,
            "supplier_url": source.supplier_url,
            "unit_cost": float(source.unit_cost) if source.unit_cost is not None else None,
            "domestic_shipping": float(source.domestic_shipping) if source.domestic_shipping is not None else None,
            "international_shipping_estimate": float(source.international_shipping_estimate) if source.international_shipping_estimate is not None else None,
            "estimated_landed_cost": float(source.estimated_landed_cost) if source.estimated_landed_cost is not None else None,
            "moq": source.moq,
            "supplier_rating": source.supplier_rating,
            "notes": source.notes,
            "is_primary": source.is_primary,
            "verification_status": source.verification_status,
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

    def _persist_profit_scenarios(self, product_id: uuid.UUID, profit_input: dict[str, Any], profit_result: dict[str, Any]) -> None:
        self.db.query(ProfitAnalysis).filter(ProfitAnalysis.product_id == product_id).delete(synchronize_session=False)
        self.db.commit()

        profit_data = agent_data({"profit_agent": profit_result}, "profit_agent")
        for scenario in profit_data.get("scenarios", []):
            sale_price = float(scenario.get("sale_price") or 0)
            landed_cost = float(scenario.get("landed_cost") or 0)
            selling_cost = float(scenario.get("selling_cost") or 0)
            net_profit = float(scenario.get("net_profit") or 0)
            margin_percent = float(scenario.get("margin_percent") or 0)
            roi_percent = (net_profit / landed_cost * 100) if landed_cost > 0 else 0
            record = ProfitAnalysis(
                product_id=product_id,
                scenario_name=str(scenario.get("name") or "scenario"),
                expected_sale_price=sale_price,
                product_cost=float(profit_input.get("product_cost") or 0),
                import_shipping_per_unit=float(profit_input.get("china_domestic_shipping") or 0)
                + float(profit_input.get("international_shipping") or 0),
                landed_cost=landed_cost,
                marketplace_fee=max(
                    selling_cost
                    - float(scenario.get("shipping_cost") or 0)
                    - float(profit_input.get("packaging") or 0)
                    - float(profit_input.get("return_allowance") or 0)
                    - float(profit_input.get("ad_cost") or 0),
                    0,
                ),
                us_shipping=float(scenario.get("shipping_cost") or 0),
                packaging_cost=float(profit_input.get("packaging") or 0),
                return_allowance=float(profit_input.get("return_allowance") or 0),
                ad_cost=float(profit_input.get("ad_cost") or 0),
                estimated_net_profit=net_profit,
                margin_percent=margin_percent,
                roi_percent=roi_percent,
                break_even_price=landed_cost + selling_cost,
                verdict=str(scenario.get("decision") or "WEAK"),
            )
            self.db.add(record)

        self.db.commit()


ProductResearchService = ResearchPipelineService
