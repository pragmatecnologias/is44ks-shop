from sqlalchemy.orm import Session
import uuid
from typing import Optional

from app.models.product import Product
from app.models.supplier import ProductSource, MarketplaceResearch, CompetitorListing, ProfitAnalysis, AgentReport
from app.config import settings


class ProductResearchService:
    """Orchestrates the full research pipeline for a product."""

    def __init__(self, db: Session, agents: dict):
        self.db = db
        self.agents = agents

    def run_research_pipeline(self, product_id: uuid.UUID) -> dict:
        """Run the full research pipeline for a product."""
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return {"error": "Product not found"}

        # Update status to researching
        product.status = "RESEARCHING"
        self.db.commit()

        results = {}

        # 1. Run RiskAgent
        risk_agent = self.agents.get("risk")
        if risk_agent:
            risk_input = {
                "product_name": product.name,
                "description": product.description,
                "supplier_url": None,
                "category": product.category,
            }
            risk_result = risk_agent.run(risk_input)
            self._save_agent_report(product_id, "risk", risk_input, risk_result)
            results["risk"] = risk_result

            if risk_result.output_json.get("blocked", False):
                product.status = "BLOCKED"
                product.risk_level = risk_result.output_json.get("risk_level", "BLOCKED")
                self.db.commit()
                return {
                    "status": "blocked",
                    "decision": "BLOCKED",
                    "reason": risk_result.output_json.get("reasoning_summary", "Risk agent blocked this product"),
                    "reports": [risk_result],
                }

        # 2. Run MarketAgent
        market_agent = self.agents.get("market")
        if market_agent:
            market_input = {
                "product_name": product.name,
                "marketplace_data": [],
                "competitor_listings": [],
            }
            market_result = market_agent.run(market_input)
            self._save_agent_report(product_id, "market", market_input, market_result)
            results["market"] = market_result

        # 3. Run SupplierAgent (placeholder - uses ProductSource data)
        supplier_agent = self.agents.get("supplier")
        if supplier_agent:
            sources = self.db.query(ProductSource).filter(ProductSource.product_id == product_id).all()
            supplier_input = {
                "product_name": product.name,
                "sources": [
                    {"name": s.supplier_name, "cost": s.unit_cost, "platform": s.supplier_platform}
                    for s in sources
                ],
            }
            supplier_result = supplier_agent.run(supplier_input)
            self._save_agent_report(product_id, "supplier", supplier_input, supplier_result)
            results["supplier"] = supplier_result

        # 4. Run ProfitAgent
        profit_agent = self.agents.get("profit")
        if profit_agent:
            sources = self.db.query(ProductSource).filter(ProductSource.product_id == product_id).all()
            primary_source = next((s for s in sources if s.is_primary), sources[0] if sources else None)
            sale_price = market_result.output_json.get("realistic_sale_price", 50) if "market" in results else 50
            buy_cost = float(primary_source.unit_cost) if primary_source else 10
            import_shipping = float(primary_source.international_shipping_estimate or 5) if primary_source else 5

            profit_input = {
                "expected_sale_price": sale_price,
                "product_cost": buy_cost,
                "import_shipping": import_shipping,
                "marketplace_fee": sale_price * (settings.DEFAULT_MARKETPLACE_FEE_PERCENT / 100),
                "us_shipping": 8,
                "packaging_cost": settings.DEFAULT_PACKAGING_COST,
                "return_allowance": settings.DEFAULT_RETURN_ALLOWANCE,
                "ad_cost": 0,
            }
            profit_result = profit_agent.run(profit_input)
            self._save_agent_report(product_id, "profit", profit_input, profit_result)
            results["profit"] = profit_result

        # 5. Run CompetitionAgent
        competition_agent = self.agents.get("competition")
        if competition_agent:
            comp_input = {
                "product_name": product.name,
                "competitor_listings": [],
            }
            competition_result = competition_agent.run(comp_input)
            self._save_agent_report(product_id, "competition", comp_input, competition_result)
            results["competition"] = competition_result

        # 6. Run ListingAgent
        listing_agent = self.agents.get("listing")
        if listing_agent:
            listing_input = {
                "product_name": product.name,
                "features": [],
                "dimensions": {},
                "photos": [],
                "competitor_weaknesses": [],
                "recommended_price": sale_price if "market" in results else None,
                "marketplace": "ebay",
            }
            listing_result = listing_agent.run(listing_input)
            self._save_agent_report(product_id, "listing", listing_input, listing_result)
            results["listing"] = listing_result

        # 7. Run DecisionAgent with all reports
        decision_agent = self.agents.get("decision")
        decision_result = None
        if decision_agent:
            decision_input = {
                "product_name": product.name,
                "reports": {k: v.output_json for k, v in results.items()},
            }
            decision_result = decision_agent.run(decision_input)
            self._save_agent_report(product_id, "decision", decision_input, decision_result)

        # 8. Update product with final score and decision
        if decision_result:
            output = decision_result.output_json
            score = output.get("final_score", 0)
            decision = output.get("final_decision", "SKIP")

            product.final_score = score
            product.final_decision = decision
            product.target_sale_price = output.get("recommended_price")
            product.expected_profit = output.get("expected_profit")

            if decision in ("BUY_SMALL_BATCH", "BUY_SAMPLE"):
                product.status = "APPROVED"
            elif decision == "WATCHLIST":
                product.status = "NEW"
            else:
                product.status = "SKIPPED"

            self.db.commit()

        # 9. Return final decision report
        return {
            "product_id": product_id,
            "status": product.status,
            "final_decision": product.final_decision,
            "final_score": float(product.final_score) if product.final_score else None,
            "reports": results,
        }

    def _save_agent_report(self, product_id: uuid.UUID, agent_type: str, input_data: dict, result) -> AgentReport:
        import json
        report = AgentReport(
            product_id=product_id,
            agent_name=agent_type,
            report_type=agent_type,
            input_json=json.dumps(input_data),
            output_json=json.dumps(result.output_json),
            summary=result.summary,
            confidence=str(result.confidence) if result.confidence else None,
        )
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report