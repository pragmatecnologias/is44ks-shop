from __future__ import annotations

import json
from statistics import median
from typing import Any, Dict

from app.agents.base_agent import BaseAgent
from app.llm.base import LLMProvider, Message
from app.schemas.agent_schema import CompetitionAgentOutput


def _avg(values: list[float]) -> float | None:
    if not values:
        return None
    return round(sum(values) / len(values), 2)


class CompetitionAgent(BaseAgent):
    def __init__(self, llm_provider: LLMProvider):
        super().__init__(llm_provider, "competition_agent")

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        template = self._load_prompt("competition_agent.txt")

        product = context.get("product", {})
        competitor_listings = context.get("competitor_listings", [])
        market_summary = context.get("market_summary", {})

        prompt = self._format_prompt(
            template,
            PRODUCT_JSON=json.dumps(product, indent=2),
            COMPETITOR_LISTINGS_JSON=json.dumps(competitor_listings, indent=2),
            MARKET_SUMMARY_JSON=json.dumps(market_summary, indent=2),
        )

        system_msg = Message(
            "system",
            "You are a competition analysis specialist for resale products. "
            "Return ONLY valid JSON. Do not invent evidence. "
            "Focus on whether a new seller can beat the current listings.",
        )
        user_msg = Message("user", prompt)
        try:
            result = await self.llm.complete_json([system_msg, user_msg])
        except Exception:
            result = {}

        listings = competitor_listings if isinstance(competitor_listings, list) else []
        VERIFIED = {"USER_VERIFIED", "API_IMPORTED"}

        def _status(row: dict[str, Any]) -> str:
            return str(row.get("verification_status") or "").upper()

        verified_listings = [row for row in listings if _status(row) in VERIFIED]
        unverified_listings = [row for row in listings if row not in verified_listings]
        verified_prices = [float(row.get("price")) for row in verified_listings if row.get("price") is not None]
        verified_photo_scores = [float(row.get("photo_score")) for row in verified_listings if row.get("photo_score") is not None]
        verified_title_scores = [float(row.get("title_score")) for row in verified_listings if row.get("title_score") is not None]
        verified_description_scores = [float(row.get("description_score")) for row in verified_listings if row.get("description_score") is not None]
        verified_sold_count = sum(1 for row in verified_listings if bool(row.get("sold")))
        verified_active_count = len(verified_listings) - verified_sold_count
        sold_count = sum(1 for row in listings if bool(row.get("sold")))
        active_count = len(listings) - sold_count

        avg_photo_score = _avg(verified_photo_scores)
        avg_title_score = _avg(verified_title_scores)
        avg_description_score = _avg(verified_description_scores)
        median_price = round(median(verified_prices), 2) if verified_prices else None
        verification_coverage = (len(verified_listings) / len(listings)) if listings else 0.0

        weakness_list: list[str] = []
        gap_score = 50

        if not listings:
            weakness_list.append("No competitor listings captured yet.")
            gap_score = 30
        elif not verified_listings:
            weakness_list.append("Competitor listings are not verified yet.")
            gap_score = 25
        else:
            if verified_active_count >= 10:
                gap_score -= 15
            elif verified_active_count >= 5:
                gap_score -= 8
            elif verified_active_count == 0:
                gap_score += 8

            if verified_sold_count > verified_active_count:
                gap_score += 10
            elif verified_active_count > verified_sold_count * 2 and verified_active_count >= 5:
                weakness_list.append("Many active listings but fewer sold comps, suggesting tough sell-through.")
                gap_score -= 8

            if avg_photo_score is not None and avg_photo_score < 60:
                weakness_list.append("Competitor photos look weak enough to beat with real photos.")
                gap_score += 10
            elif avg_photo_score is not None and avg_photo_score >= 80:
                weakness_list.append("Competitor photos are already strong.")
                gap_score -= 8

            if avg_title_score is not None and avg_title_score < 60:
                weakness_list.append("Competitor titles are not well optimized.")
                gap_score += 8

            if avg_description_score is not None and avg_description_score < 55:
                weakness_list.append("Competitor descriptions are thin or incomplete.")
                gap_score += 6

            if median_price is not None and float(market_summary.get("median_sold_price") or 0) > 0:
                market_price = float(market_summary.get("median_sold_price") or market_summary.get("median_active_price") or 0)
                if market_price > 0 and median_price <= market_price * 0.9:
                    gap_score += 8
                    weakness_list.append("Competitors are priced below the median market signal.")
                elif market_price > 0 and median_price >= market_price * 1.1:
                    gap_score += 5
                    weakness_list.append("Competitors are priced above the median market signal.")

        gap_score = max(0, min(100, gap_score))

        competition_level = "HIGH" if verified_active_count >= 10 else "MEDIUM" if verified_active_count >= 4 else "LOW"
        can_compete = gap_score >= 55 and bool(verified_listings)

        category = str(product.get("category", "")).lower()
        if "car" in category:
            recommended_angle = "Use real photos, dimensions, and fitment clarity."
        elif "pet" in category:
            recommended_angle = "Lead with usefulness, safety, and a simple problem-solving angle."
        elif "home" in category or "organization" in category:
            recommended_angle = "Show neatness, bundle value, and before/after clarity."
        else:
            recommended_angle = "Use real photos, a clear bundle angle, and concise benefit-driven copy."

        output = CompetitionAgentOutput.model_validate(
            {
                "competition_level": competition_level,
                "listing_gap_score": gap_score,
                "can_compete": can_compete,
                "competitor_count": len(listings),
                "verified_competitor_count": len(verified_listings),
                "unverified_competitor_count": len(unverified_listings),
                "active_competitor_count": active_count,
                "sold_competitor_count": sold_count,
                "verified_active_competitor_count": verified_active_count,
                "verified_sold_competitor_count": verified_sold_count,
                "median_competitor_price": median_price,
                "avg_photo_score": avg_photo_score,
                "avg_title_score": avg_title_score,
                "avg_description_score": avg_description_score,
                "verification_coverage": round(verification_coverage, 2),
                "weaknesses": weakness_list or ["No obvious weakness captured yet."],
                "recommended_angle": result.get("recommended_angle", recommended_angle),
                "summary": result.get(
                    "summary",
                    "Competition analysis completed from captured competitor listings.",
                ),
                "confidence": "HIGH" if verified_listings and gap_score >= 55 else "MEDIUM" if verified_listings else "LOW",
                "warnings": result.get("warnings", []),
                "evidence_refs": result.get("evidence_refs", []),
            }
        )

        return {
            "agent_name": "competition_agent",
            "output_json": output.model_dump(),
            "summary": output.summary,
            "confidence": output.confidence,
            "warnings": output.warnings,
            "evidence_refs": output.evidence_refs,
        }
