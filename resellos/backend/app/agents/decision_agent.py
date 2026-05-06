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
        current_net_profit = float(profit.get("current_net_profit", net_profit) or net_profit)
        target_net_profit_threshold = float(profit.get("target_net_profit_threshold", 8.0) or 8.0)
        profit_gap_to_buy_sample = float(
            profit.get("profit_gap_to_buy_sample", max(0.0, target_net_profit_threshold - current_net_profit)) or 0
        )
        current_landed_cost = float(profit.get("current_landed_cost", profit.get("break_even_price", 0)) or 0)
        max_landed_cost_for_target_profit = float(profit.get("max_landed_cost_for_target_profit", 0) or 0)
        evidence_quality = str(market.get("evidence_quality", "LOW")).upper()
        insufficient_data = bool(market.get("insufficient_data", True))
        sold_listing_count = int(market.get("sold_listing_count", 0) or 0)
        active_listing_count = int(market.get("active_listing_count", 0) or 0)
        verified_sold = int(market.get("verified_sold_listing_count", 0) or 0)
        verified_active = int(market.get("verified_active_listing_count", 0) or 0)
        test_data_count = int(market.get("test_data_evidence_count", 0) or 0)
        competition_level = str(competition.get("competition_level", "UNKNOWN")).upper()
        listing_gap_score = int(competition.get("listing_gap_score", 0) or 0)
        can_compete = bool(competition.get("can_compete", True))
        verified_competitor_count = int(competition.get("verified_competitor_count", 0) or 0)
        market_price_missing = bool(
            market.get(
                "market_price_missing",
                float(market.get("median_sold_price") or market.get("median_active_price") or 0) <= 0,
            )
        )
        verification_coverage = float(market.get("verification_coverage", 0) or 0)
        verified_evidence_count = int(market.get("verified_evidence_count", 0) or 0)
        unverified_evidence_count = int(market.get("unverified_evidence_count", 0) or 0)
        has_supplier_cost = bool(supplier_summary.get("unit_cost") is not None or supplier_summary.get("estimated_landed_cost") is not None)
        supplier_verification_status = str(supplier_summary.get("verification_status") or "").upper()
        supplier_verified = supplier_verification_status == "USER_VERIFIED"
        product_cost = float(supplier_summary.get("unit_cost") or 0)
        domestic_shipping = float(supplier_summary.get("domestic_shipping") or 0)
        international_shipping = float(supplier_summary.get("international_shipping_estimate") or 0)
        max_landed_cost = float(supplier_summary.get("estimated_landed_cost") or (product_cost + domestic_shipping + international_shipping))
        target_sale_price = float(profit.get("target_sale_price") or 0)
        current_target_sale_price = float(profit.get("current_target_sale_price", target_sale_price) or target_sale_price)
        required_sale_price_for_target_profit = float(profit.get("required_sale_price_for_target_profit", 0) or 0)
        research_completeness_score = 0
        research_completeness_score += min(25, verified_sold * 5)
        research_completeness_score += min(20, verified_active * 2)
        research_completeness_score += 15 if has_supplier_cost else 0
        research_completeness_score += 10 if supplier_verified else 0
        research_completeness_score += 10 if not market_price_missing else 0
        research_completeness_score += 10 if profit.get("scenarios") else 0
        research_completeness_score += 10 if competition.get("competitor_count", 0) > 0 else 0
        research_completeness_score += 10 if target_sale_price > 0 else 0
        if supplier_verified and verified_competitor_count >= 3 and verification_coverage >= 1.0:
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
        if verified_sold == 0:
            missing_evidence.append("Verified sold listings missing")
            required_before_buying.append("Add at least 5 verified sold listings with prices.")
        if verified_active == 0:
            missing_evidence.append("Verified active listings missing")
            required_before_buying.append("Add verified active listing evidence for competition checks.")
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
        if verified_competitor_count < 3:
            missing_evidence.append("Verified competitor evidence missing")
            required_before_buying.append("Add at least 3 verified competitor listings before buying.")
        if not supplier_verified:
            missing_evidence.append("Verified supplier source missing")
            required_before_buying.append("Verify supplier source before buying.")
        required_before_buying.extend(market.get("required_next_evidence", []))

        assumptions = []
        if net_profit == 0:
            assumptions.append("Profit estimate depends on placeholder costs until supplier data is added.")

        min_profit = float(settings.MIN_ACCEPTABLE_PROFIT)
        min_margin = float(settings.MIN_ACCEPTABLE_MARGIN)
        ready_for_sample = (
            not blocked
            and risk_level != "BLOCKED"
            and verified_sold >= 5
            and verified_active >= 5
            and unverified_evidence_count == 0
            and test_data_count == 0
            and verification_coverage >= 1.0
            and has_supplier_cost
            and supplier_verified
            and not market_price_missing
            and target_sale_price > 0
            and net_profit >= min_profit
            and best_margin >= min_margin
            and score >= 70
            and competition.get("can_compete", True)
            and verified_competitor_count >= 3
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
            if research_verdict == "READY_FOR_SAMPLE":
                research_verdict = "NEEDS_MORE_RESEARCH"

        if test_data_count > 0:
            if recommendation in {"BUY_SAMPLE", "BUY_SMALL_BATCH", "REORDER", "SCALE"}:
                recommendation = "WATCHLIST"
            hard_blockers.append(f"{test_data_count} evidence items are test data — not real market evidence.")
            required_before_buying.append("Replace test/synthetic evidence with real verified data.")
            if research_verdict == "READY_FOR_SAMPLE":
                research_verdict = "NEEDS_MORE_RESEARCH"

        if not can_compete:
            if recommendation in {"BUY_SAMPLE", "BUY_SMALL_BATCH", "REORDER", "SCALE"}:
                recommendation = "WATCHLIST"
            hard_blockers.append("Competition gap is too small to compete reliably.")
            required_before_buying.append("Capture competitor weaknesses and find a clearer angle.")
            if research_verdict == "READY_FOR_SAMPLE":
                research_verdict = "PROMISING_RESEARCH"

        if not has_supplier_cost:
            if recommendation in {"BUY_SAMPLE", "BUY_SMALL_BATCH", "REORDER", "SCALE"}:
                recommendation = "WATCHLIST"
            hard_blockers.append("Supplier cost is missing.")
            required_before_buying.append("Add supplier unit cost and shipping.")
            if research_verdict == "READY_FOR_SAMPLE":
                research_verdict = "NEEDS_MORE_RESEARCH"

        if not supplier_verified:
            if recommendation in {"BUY_SAMPLE", "BUY_SMALL_BATCH", "REORDER", "SCALE"}:
                recommendation = "WATCHLIST"
            hard_blockers.append("Supplier cost is not verified.")
            required_before_buying.append("Verify supplier URL, screenshot, unit cost, shipping, and landed cost.")
            if research_verdict == "READY_FOR_SAMPLE":
                research_verdict = "NEEDS_MORE_RESEARCH"

        if unverified_evidence_count > 0 or test_data_count > 0 or verification_coverage < 1.0:
            verification_blocker = "Evidence is not verified."
            if verification_blocker not in hard_blockers:
                hard_blockers.append(verification_blocker)
            required_before_buying.append("Verify evidence before sample buying.")
            if recommendation in {"BUY_SAMPLE", "BUY_SMALL_BATCH", "REORDER", "SCALE"}:
                recommendation = "WATCHLIST"
            if research_verdict == "READY_FOR_SAMPLE":
                research_verdict = "NEEDS_MORE_RESEARCH"
        else:
            verification_blocker = ""

        if target_sale_price <= 0:
            required_before_buying.append("Record a real target sale price from market evidence.")

        if ready_for_sample:
            buy_readiness = "READY"
        else:
            buy_readiness = "NOT_READY"

        buy_readiness_status = (
            "READY"
            if ready_for_sample
            else "ALMOST_READY"
            if score >= 60
            and not blocked
            and not market_price_missing
            and not verification_blocker
            and supplier_verified
            and verified_competitor_count >= 3
            and test_data_count == 0
            and verification_coverage >= 1.0
            else "NOT_READY"
        )

        evidence_gates_complete = (
            verified_sold >= 5
            and verified_active >= 5
            and test_data_count == 0
            and unverified_evidence_count == 0
            and verification_coverage >= 1.0
            and has_supplier_cost
            and supplier_verified
            and verified_competitor_count >= 3
            and not market_price_missing
        )

        if buy_readiness_status != "READY" and score < 70:
            if evidence_gates_complete:
                required_before_buying.append("Improve supplier landed cost, validate the active price signal, and sharpen the competitor angle before sample buying.")
            else:
                required_before_buying.append("Improve economics or competition enough to reach the sample-buy threshold.")

        max_quantity_to_buy = 0
        if recommendation == "BUY_SAMPLE":
            max_quantity_to_buy = 5
        elif recommendation == "BUY_SMALL_BATCH":
            max_quantity_to_buy = 20

        missing_evidence = list(dict.fromkeys(missing_evidence))
        required_before_buying = list(dict.fromkeys(required_before_buying))
        hard_blockers = list(dict.fromkeys(hard_blockers))

        if evidence_gates_complete:
            def _is_evidence_request(item: str) -> bool:
                lowered = item.lower()
                return any(
                    phrase in lowered
                    for phrase in [
                        "verified sold listings",
                        "verified active listings",
                        "verified competitor listings",
                        "supplier source before buying",
                        "supplier unit cost and shipping",
                        "verify evidence before sample buying",
                        "real sold listings",
                        "market price",
                        "competition checks",
                        "market gap",
                    ]
                )

            required_before_buying = [item for item in required_before_buying if not _is_evidence_request(item)]
            if current_net_profit < target_net_profit_threshold:
                required_before_buying.append(
                    f"Reduce landed cost to approximately ${max_landed_cost_for_target_profit:.2f} or prove a higher sustainable sale price above ${required_sale_price_for_target_profit:.2f}."
                )

        if evidence_gates_complete and not blocked and buy_readiness_status != "READY":
            if current_net_profit < target_net_profit_threshold:
                next_action = (
                    f"Verified evidence gates are complete. Reduce landed cost to about ${max_landed_cost_for_target_profit:.2f} "
                    f"or validate sale prices above ${required_sale_price_for_target_profit:.2f} before sample buying."
                )
            elif research_verdict in {"NEEDS_MORE_RESEARCH", "PROMISING_RESEARCH"}:
                next_action = "Verified evidence gates are complete. Improve supplier landed cost, validate the active price signal, and sharpen the competitor angle before sample buying."
            elif research_verdict in {"WEAK_IDEA", "REJECT"}:
                next_action = "Verified evidence is complete, but the economics are too weak. Pause or look for a better supplier and stronger market gap."

        final_next_action = llm_result.get("next_action") or next_action
        if evidence_gates_complete and not blocked and buy_readiness_status != "READY":
            final_next_action = next_action

        if verification_blocker:
            main_blocker = verification_blocker
        elif hard_blockers:
            main_blocker = hard_blockers[0]
        elif missing_evidence:
            main_blocker = missing_evidence[0]
        elif buy_readiness_status != "READY":
            if research_verdict in {"WEAK_IDEA", "REJECT"}:
                main_blocker = "Weak economics or too much uncertainty."
            elif evidence_gates_complete and current_net_profit < target_net_profit_threshold:
                main_blocker = "Verified evidence is complete, but profit is below the sample-buy threshold."
            elif research_verdict == "NEEDS_MORE_RESEARCH":
                main_blocker = "Verified evidence is complete, but the opportunity score is still below the sample-buy threshold."
            elif not supplier_verified:
                main_blocker = "Supplier cost is not verified."
            elif verified_competitor_count < 3:
                main_blocker = "Verify at least 3 competitor listings."
            elif market_price_missing:
                main_blocker = "Market price is missing."
            elif score < 70:
                main_blocker = "Opportunity score is still below the sample-buy threshold."
            else:
                main_blocker = reason or "Product is not ready for sample buying yet."
        else:
            main_blocker = "None"

        if main_blocker in {None, "", "None"} and buy_readiness_status != "READY":
            main_blocker = reason or "Product is not ready for sample buying yet."

        output = DecisionAgentOutput.model_validate(
            {
                "recommendation": recommendation,
                "research_verdict": research_verdict,
                "buy_readiness": buy_readiness,
                "buy_readiness_status": buy_readiness_status,
                "research_completeness_score": research_completeness_score,
                "opportunity_score": score,
                "total_score": score,
                "main_blocker": main_blocker,
                "confidence": "HIGH" if score >= 75 else "MEDIUM" if score >= 55 else "LOW",
                "reason": llm_result.get("reason") or reason,
                "next_action": final_next_action,
                "missing_evidence": missing_evidence,
                "assumptions": assumptions,
                "hard_blockers": hard_blockers,
                "max_quantity_to_buy": max_quantity_to_buy,
                "max_landed_cost": max_landed_cost,
                "target_sale_price": target_sale_price,
                "current_net_profit": current_net_profit,
                "target_net_profit_threshold": target_net_profit_threshold,
                "profit_gap_to_buy_sample": profit_gap_to_buy_sample,
                "current_landed_cost": current_landed_cost,
                "max_landed_cost_for_target_profit": max_landed_cost_for_target_profit,
                "current_target_sale_price": current_target_sale_price,
                "required_sale_price_for_target_profit": required_sale_price_for_target_profit,
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
