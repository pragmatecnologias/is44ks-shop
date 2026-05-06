from app.agents.base_agent import BaseAgent
from app.llm.base import LLMProvider, Message
from typing import Dict, Any
from app.schemas.agent_schema import MarketAgentOutput
import json


def _median(values: list[float]) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return round(ordered[middle], 2)
    return round((ordered[middle - 1] + ordered[middle]) / 2, 2)


class MarketAgent(BaseAgent):
    def __init__(self, llm_provider: LLMProvider):
        super().__init__(llm_provider, "market_agent")

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        template = self._load_prompt("market_agent.txt")

        product = context.get("product", {})
        marketplace_research = context.get("marketplace_research", [])
        competitor_listings = context.get("competitor_listings", [])
        evidence = context.get("marketplace_evidence", [])

        marketplace_json = json.dumps(marketplace_research, indent=2)
        competitor_json = json.dumps(competitor_listings, indent=2)

        prompt = self._format_prompt(
            template,
            PRODUCT_JSON=json.dumps(product, indent=2),
            MARKETPLACE_RESEARCH_JSON=marketplace_json,
            COMPETITOR_LISTINGS_JSON=competitor_json,
        )

        system_msg = Message(
            "system",
            "You are a market research specialist for resale platforms. "
            "Analyze the market data and return ONLY valid JSON. "
            "IMPORTANT: Do NOT invent prices. If insufficient data exists, "
            "clearly indicate 'insufficient_data': true and state why.",
        )
        user_msg = Message("user", prompt)
        try:
            result = await self.llm.complete_json([system_msg, user_msg])
        except Exception:
            result = {}

        evidence_rows = evidence if isinstance(evidence, list) else []
        active_rows = [row for row in evidence_rows if str(row.get("evidence_type", "")).upper() == "ACTIVE_LISTING"]
        sold_rows = [row for row in evidence_rows if str(row.get("evidence_type", "")).upper() == "SOLD_LISTING"]
        supporting_rows = [row for row in evidence_rows if str(row.get("evidence_type", "")).upper() in {"SCREENSHOT", "MANUAL_NOTE"}]

        # Verification-aware filtering
        VERIFIED = {"USER_VERIFIED", "API_IMPORTED"}
        TEST = {"TEST_DATA", "REJECTED"}

        def _status(row: dict) -> str:
            return str(row.get("verification_status") or "").upper()

        verified_sold_rows = [row for row in sold_rows if _status(row) in VERIFIED]
        verified_active_rows = [row for row in active_rows if _status(row) in VERIFIED]
        test_data_count = sum(1 for row in evidence_rows if _status(row) == "TEST_DATA")
        verified_evidence_count = sum(1 for row in evidence_rows if _status(row) in VERIFIED)
        unverified_evidence_count = sum(1 for row in evidence_rows if _status(row) not in VERIFIED and _status(row) not in TEST and _status(row) != "")

        active_prices = [float(row.get("price")) for row in active_rows if row.get("price") is not None]
        sold_prices = [float(row.get("price")) for row in sold_rows if row.get("price") is not None]
        active_shipping_prices = [float(row.get("shipping_price")) for row in active_rows if row.get("shipping_price") is not None]
        sold_shipping_prices = [float(row.get("shipping_price")) for row in sold_rows if row.get("shipping_price") is not None]

        if not active_prices and isinstance(marketplace_research, list):
            active_prices = [float(row.get("median_active_price")) for row in marketplace_research if row.get("median_active_price") is not None]
        if not sold_prices and isinstance(marketplace_research, list):
            sold_prices = [float(row.get("median_sold_price")) for row in marketplace_research if row.get("median_sold_price") is not None]
        if not active_shipping_prices and isinstance(marketplace_research, list):
            active_shipping_prices = [float(row.get("shipping_median")) for row in marketplace_research if row.get("shipping_median") is not None]
        if not sold_shipping_prices and isinstance(marketplace_research, list):
            sold_shipping_prices = [float(row.get("shipping_median")) for row in marketplace_research if row.get("shipping_median") is not None]

        active_listing_count = len(active_rows)
        sold_listing_count = len(sold_rows)
        verified_sold_count = len(verified_sold_rows)
        verified_active_count = len(verified_active_rows)

        active_price_range = [round(min(active_prices), 2), round(max(active_prices), 2)] if active_prices else []
        sold_price_range = [round(min(sold_prices), 2), round(max(sold_prices), 2)] if sold_prices else []
        median_active_price = _median(active_prices)
        median_sold_price = _median(sold_prices)
        median_active_shipping = _median(active_shipping_prices)
        median_sold_shipping = _median(sold_shipping_prices)
        shipping_values = [value for value in [median_active_shipping, median_sold_shipping] if value is not None]
        median_shipping = _median([float(value) for value in shipping_values]) if shipping_values else None
        marketplace_coverage = sorted(
            {
                str(row.get("marketplace")).strip()
                for row in (evidence if isinstance(evidence, list) else []) + (marketplace_research if isinstance(marketplace_research, list) else [])
                if row.get("marketplace")
            }
        )

        market_price_missing = median_sold_price is None and median_active_price is None
        supporting_evidence_count = len(supporting_rows)
        verification_coverage = (verified_evidence_count / len(evidence_rows)) if evidence_rows else 0.0
        insufficient_data = verified_sold_count < 5 or market_price_missing

        if verified_sold_count >= 10 and verified_active_count >= 10 and median_sold_price is not None:
            evidence_quality = "HIGH"
        elif verified_sold_count >= 5 and median_sold_price is not None:
            evidence_quality = "MEDIUM"
        elif verified_active_count >= 5 or marketplace_coverage:
            evidence_quality = "LOW"
        else:
            evidence_quality = "LOW"

        if verified_sold_count >= 10:
            sell_through_signal = "HIGH"
        elif verified_sold_count >= 5:
            sell_through_signal = "MEDIUM"
        elif verified_sold_count > 0:
            sell_through_signal = "LOW"
        else:
            sell_through_signal = "UNKNOWN"

        required_next_evidence = []
        if verified_sold_count < 5:
            required_next_evidence.append(f"Add at least 5 verified sold listings (currently {verified_sold_count} verified of {sold_listing_count} total).")
        if verified_active_count < 5:
            required_next_evidence.append(f"Add at least 5 verified active listings (currently {verified_active_count} verified of {active_listing_count} total).")
        if median_active_shipping is None and median_sold_shipping is None:
            required_next_evidence.append("Capture shipping examples.")
        if supporting_evidence_count == 0:
            required_next_evidence.append("Add screenshots or manual notes for support.")
        if test_data_count > 0:
            required_next_evidence.append(f"Replace {test_data_count} test/synthetic evidence items with real verified data.")
        if unverified_evidence_count > 0:
            required_next_evidence.append(f"Verify {unverified_evidence_count} unverified evidence items.")

        demand_evidence_quality = "HIGH" if verified_sold_count >= 10 else "MEDIUM" if verified_sold_count >= 5 else "LOW"
        market_presence_quality = "HIGH" if verified_active_count >= 10 else "MEDIUM" if verified_active_count >= 5 else "LOW"
        research_completeness_score = 0
        research_completeness_score += min(30, verified_sold_count * 4)
        research_completeness_score += min(20, verified_active_count * 2)
        research_completeness_score += 15 if median_sold_price is not None else 0
        research_completeness_score += 10 if median_active_price is not None else 0
        research_completeness_score += 10 if median_shipping is not None else 0
        research_completeness_score += min(15, supporting_evidence_count * 5)
        research_completeness_score += 10 if marketplace_coverage else 0
        research_completeness_score = max(0, min(100, research_completeness_score))

        if evidence_quality == "HIGH":
            recommended_research_action = "Proceed to profit and competition analysis."
        elif verified_sold_count < 5:
            recommended_research_action = f"Add {5 - verified_sold_count} more verified sold listings to improve confidence."
        elif verified_active_count < 5:
            recommended_research_action = f"Add {5 - verified_active_count} more verified active listings to compare competition."
        else:
            recommended_research_action = "Collect a few more evidence points before buying."

        output = MarketAgentOutput.model_validate(
            {
                "evidence_quality": evidence_quality,
                "insufficient_data": insufficient_data,
                "market_price_missing": market_price_missing,
                "supporting_evidence_count": supporting_evidence_count,
                "active_listing_count": active_listing_count,
                "sold_listing_count": sold_listing_count,
                "verified_sold_listing_count": verified_sold_count,
                "verified_active_listing_count": verified_active_count,
                "total_evidence_count": len(evidence_rows),
                "verified_evidence_count": verified_evidence_count,
                "unverified_evidence_count": unverified_evidence_count,
                "test_data_evidence_count": test_data_count,
                "verification_coverage": round(verification_coverage, 2),
                "research_completeness_score": research_completeness_score,
                "demand_signal": "HIGH" if verified_sold_count >= 10 else "MEDIUM" if verified_sold_count > 0 else "UNKNOWN",
                "demand_evidence_quality": demand_evidence_quality,
                "market_presence_quality": market_presence_quality,
                "competition_level": "HIGH" if verified_active_count >= 10 else "MEDIUM" if verified_active_count > 0 else "UNKNOWN",
                "median_active_price": median_active_price,
                "median_sold_price": median_sold_price,
                "median_active_shipping": median_active_shipping,
                "median_sold_shipping": median_sold_shipping,
                "median_shipping": median_shipping,
                "active_price_range": active_price_range,
                "sold_price_range": sold_price_range,
                "marketplace_coverage": marketplace_coverage,
                "sell_through_signal": sell_through_signal,
                "recommended_research_action": recommended_research_action,
                "required_next_evidence": required_next_evidence,
                "summary": result.get("summary", f"Marketplace evidence analyzed from {len(marketplace_coverage)} marketplaces."),
                "confidence": "LOW" if insufficient_data else "MEDIUM",
                "warnings": result.get("warnings", []),
                "evidence_refs": result.get("evidence_refs", []),
            }
        )

        return {
            "agent_name": "market_agent",
            "output_json": output.model_dump(),
            "summary": output.summary,
            "confidence": output.confidence,
            "warnings": output.warnings,
            "evidence_refs": output.evidence_refs,
        }
