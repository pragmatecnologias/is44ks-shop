from app.agents.base_agent import BaseAgent
from app.config import settings
from app.llm.base import LLMProvider, Message
from typing import Dict, Any
from app.schemas.agent_schema import DecisionAgentOutput
from app.services.agent_utils import agent_data
import json


class DecisionAgent(BaseAgent):
    def __init__(self, llm_provider: LLMProvider):
        super().__init__(llm_provider, "decision_agent")

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        template = self._load_prompt("decision_agent.txt")

        # Pass all agent reports as context
        reports = context.get("agent_reports", {})
        reports_json = json.dumps(reports, indent=2)
        prompt = self._format_prompt(template, AGENT_REPORTS=reports_json)

        system_msg = Message(
            "system",
            "You are a product sourcing decision specialist. "
            "Combine all agent reports and return ONLY valid JSON with final decision.",
        )
        user_msg = Message("user", prompt)
        try:
            llm_result = await self.llm.complete_json([system_msg, user_msg])
        except Exception:
            llm_result = {}

        risk = agent_data(reports, "risk_agent")
        market = agent_data(reports, "market_agent")
        competition = agent_data(reports, "competition_agent")
        profit = agent_data(reports, "profit_agent")
        product = context.get("product", {})
        supplier_summary = context.get("supplier_summary", {})

        risk_level = str(risk.get("risk_level", "MEDIUM"))
        blocked = bool(risk.get("blocked", False))
        net_profit = float(profit.get("estimated_net_profit", 0) or 0)
        evidence_quality = str(market.get("evidence_quality", "LOW")).upper()
        insufficient_data = bool(market.get("insufficient_data", True))
        sold_listing_count = int(market.get("sold_listing_count", 0) or 0)
        active_listing_count = int(market.get("active_listing_count", 0) or 0)
        competition_level = str(competition.get("competition_level", "UNKNOWN")).upper()
        listing_gap_score = int(competition.get("listing_gap_score", 0) or 0)
        can_compete = bool(competition.get("can_compete", True))
        market_price_missing = bool(
            market.get(
                "market_price_missing",
                float(market.get("median_sold_price") or market.get("median_active_price") or 0) <= 0,
            )
        )
        has_supplier_cost = bool(supplier_summary.get("unit_cost") is not None or supplier_summary.get("estimated_landed_cost") is not None)
        product_cost = float(supplier_summary.get("unit_cost") or 0)
        domestic_shipping = float(supplier_summary.get("domestic_shipping") or 0)
        international_shipping = float(supplier_summary.get("international_shipping_estimate") or 0)
        max_landed_cost = float(supplier_summary.get("estimated_landed_cost") or (product_cost + domestic_shipping + international_shipping))
        target_sale_price = float(profit.get("target_sale_price") or 0)
        research_completeness_score = 0
        research_completeness_score += min(25, sold_listing_count * 5)
        research_completeness_score += min(20, active_listing_count * 2)
        research_completeness_score += 15 if has_supplier_cost else 0
        research_completeness_score += 10 if not market_price_missing else 0
        research_completeness_score += 10 if profit.get("scenarios") else 0
        research_completeness_score += 10 if competition.get("competitor_count", 0) > 0 else 0
        research_completeness_score += 10 if target_sale_price > 0 else 0
        research_completeness_score = max(research_completeness_score, int(market.get("research_completeness_score", 0) or 0))
        research_completeness_score = max(0, min(100, research_completeness_score))
        best_margin = max(
            [float(s.get("margin_percent") or 0) for s in (profit.get("scenarios") or []) if isinstance(s, dict)],
            default=0.0,
        )
        hard_blockers: list[str] = []
        required_before_buying: list[str] = []

        score = 50
        if risk_level == "LOW":
            score += 20
        elif risk_level == "MEDIUM":
            score += 5
        elif risk_level == "HIGH":
            score -= 15
        elif risk_level == "BLOCKED":
            score = 0

        if net_profit >= 15:
            score += 25
        elif net_profit >= 8:
            score += 15
        elif net_profit >= 3:
            score += 5
        else:
            score -= 15

        if evidence_quality == "HIGH":
            score += 20
        elif evidence_quality == "MEDIUM":
            score += 10
        else:
            score -= 10

        if can_compete and listing_gap_score >= 70:
            score += 10
        elif can_compete and listing_gap_score >= 55:
            score += 5
        elif not can_compete or competition_level == "HIGH":
            score -= 10

        score = max(0, min(100, score))

        missing_evidence = []
        if sold_listing_count == 0:
            missing_evidence.append("Sold listings missing")
            required_before_buying.append("Add at least 5 sold listings with prices.")
        if active_listing_count == 0:
            missing_evidence.append("Active listings missing")
            required_before_buying.append("Add active listing evidence for competition checks.")
        if insufficient_data:
            missing_evidence.append("Marketplace evidence quality is low")
            required_before_buying.append("Reach at least medium marketplace evidence quality.")
        if market_price_missing:
            missing_evidence.append("Sold or active market price missing")
            required_before_buying.append("Record a real sold or active market price.")
        if not profit.get("scenarios"):
            missing_evidence.append("Profit scenarios missing")
            required_before_buying.append("Generate profit scenarios before buying.")
        if not has_supplier_cost:
            missing_evidence.append("Supplier cost missing")
            required_before_buying.append("Add supplier unit cost and shipping.")
        if competition.get("competitor_count", 0) == 0:
            missing_evidence.append("Competition listings missing")
            required_before_buying.append("Add competitor listings to understand the market gap.")
        required_before_buying.extend(market.get("required_next_evidence", []))

        assumptions = []
        if net_profit == 0:
            assumptions.append("Profit estimate depends on placeholder costs until supplier data is added.")

        min_profit = float(settings.MIN_ACCEPTABLE_PROFIT)
        min_margin = float(settings.MIN_ACCEPTABLE_MARGIN)
        ready_for_sample = (
            not blocked
            and risk_level != "BLOCKED"
            and sold_listing_count >= 5
            and active_listing_count >= 5
            and has_supplier_cost
            and not market_price_missing
            and target_sale_price > 0
            and net_profit >= min_profit
            and best_margin >= min_margin
            and score >= 70
            and competition.get("can_compete", True)
        )

        if blocked or risk_level == "BLOCKED":
            research_verdict = "REJECT"
            recommendation = "BLOCKED"
            next_action = "Stop research and resolve risk flags before spending money."
            reason = "Risk rules blocked this product."
            hard_blockers.append("Risk rules blocked the product.")
        elif ready_for_sample:
            research_verdict = "READY_FOR_SAMPLE"
            if score >= 85 and net_profit >= max(min_profit * 2, 10) and float(profit.get("minimum_recommended_price") or 0) > 0:
                recommendation = "BUY_SMALL_BATCH"
                next_action = "Order a controlled test batch."
                reason = "Research gates are met and the economics support a small batch."
            else:
                recommendation = "BUY_SAMPLE"
                next_action = "Order a small sample batch."
                reason = "Research gates are met and the idea is ready for sampling."
        elif score >= 70 and not insufficient_data and not market_price_missing:
            research_verdict = "PROMISING_RESEARCH"
            recommendation = "WATCHLIST"
            next_action = "Keep researching until sold evidence, supplier, and competition checks are complete."
            reason = "Promising but not yet ready for sample buying."
        elif score >= 55:
            research_verdict = "NEEDS_MORE_RESEARCH"
            recommendation = "WATCHLIST"
            next_action = "Collect more sold listings, supplier proof, and competitor evidence."
            reason = "The idea is promising, but evidence is still thin."
        elif score >= 35:
            research_verdict = "WEAK_IDEA"
            recommendation = "SKIP"
            next_action = "Skip for now and move on to stronger candidates."
            reason = "Weak economics or too much uncertainty."
        else:
            research_verdict = "REJECT"
            recommendation = "SKIP"
            next_action = "Reject this idea and do not spend more time on it."
            reason = "Insufficient confidence or weak economics."

        if insufficient_data or market_price_missing:
            if recommendation in {"BUY_SAMPLE", "BUY_SMALL_BATCH", "REORDER", "SCALE"}:
                recommendation = "WATCHLIST"
            hard_blockers.append("Market evidence is insufficient for a buy decision.")
            required_before_buying.append("Add real sold listings and a market price.")

        if not can_compete:
            if recommendation in {"BUY_SAMPLE", "BUY_SMALL_BATCH", "REORDER", "SCALE"}:
                recommendation = "WATCHLIST"
            hard_blockers.append("Competition gap is too small to compete reliably.")
            required_before_buying.append("Capture competitor weaknesses and find a clearer angle.")

        if not has_supplier_cost:
            if recommendation in {"BUY_SAMPLE", "BUY_SMALL_BATCH", "REORDER", "SCALE"}:
                recommendation = "WATCHLIST"
            hard_blockers.append("Supplier cost is missing.")
            required_before_buying.append("Add supplier unit cost and shipping.")

        if target_sale_price <= 0:
            required_before_buying.append("Record a real target sale price from market evidence.")

        if ready_for_sample:
            buy_readiness = "READY"
        else:
            buy_readiness = "NOT_READY"

        buy_readiness_status = "READY" if ready_for_sample else "ALMOST_READY" if score >= 60 and not blocked and not market_price_missing else "NOT_READY"

        max_quantity_to_buy = 0
        if recommendation == "BUY_SAMPLE":
            max_quantity_to_buy = 5
        elif recommendation == "BUY_SMALL_BATCH":
            max_quantity_to_buy = 20

        missing_evidence = list(dict.fromkeys(missing_evidence))
        required_before_buying = list(dict.fromkeys(required_before_buying))
        hard_blockers = list(dict.fromkeys(hard_blockers))

        output = DecisionAgentOutput.model_validate(
            {
                "recommendation": recommendation,
                "research_verdict": research_verdict,
                "buy_readiness": buy_readiness,
                "buy_readiness_status": buy_readiness_status,
                "research_completeness_score": research_completeness_score,
                "opportunity_score": score,
                "total_score": score,
                "confidence": "HIGH" if score >= 75 else "MEDIUM" if score >= 55 else "LOW",
                "reason": llm_result.get("reason") or reason,
                "next_action": llm_result.get("next_action") or next_action,
                "missing_evidence": missing_evidence,
                "assumptions": assumptions,
                "hard_blockers": hard_blockers,
                "max_quantity_to_buy": max_quantity_to_buy,
                "max_landed_cost": max_landed_cost,
                "target_sale_price": target_sale_price,
                "required_before_buying": required_before_buying,
                "blocked": blocked,
                "warnings": llm_result.get("warnings", []),
                "evidence_refs": llm_result.get("evidence_refs", []),
            }
        )

        return {
            "agent_name": "decision_agent",
            "output_json": output.model_dump(),
            "summary": output.reason,
            "confidence": output.confidence,
            "warnings": output.warnings,
            "evidence_refs": output.evidence_refs,
        }
