from __future__ import annotations

from typing import Any, Dict

from app.agents.base_agent import BaseAgent
from app.llm.base import LLMProvider
from app.schemas.agent_schema import DemandAgentOutput
from app.services.demand_research_service import score_buyer_intent, score_keyword_specificity, score_search_volume


def _row_volume(row: dict[str, Any]) -> int | None:
    volume = row.get("monthly_search_volume")
    if volume is not None:
        try:
            return int(volume)
        except Exception:
            return None
    min_volume = row.get("monthly_search_volume_min")
    max_volume = row.get("monthly_search_volume_max")
    try:
        if min_volume is not None and max_volume is not None:
            return int((int(min_volume) + int(max_volume)) / 2)
        if min_volume is not None:
            return int(min_volume)
        if max_volume is not None:
            return int(max_volume)
    except Exception:
        return None
    return None


def _score_row(row: dict[str, Any], product_name: str | None, category: str | None) -> dict[str, Any]:
    keyword = str(row.get("keyword") or "").strip()
    volume = _row_volume(row)
    intent = int(row.get("buyer_intent_score") or score_buyer_intent(keyword, product_name=product_name, category=category))
    specificity = int(row.get("keyword_specificity_score") or score_keyword_specificity(keyword, product_name=product_name, category=category))
    demand_score = int(row.get("demand_score") or score_search_volume(volume) + intent // 4 + specificity // 4)
    competition = str(row.get("competition_level") or "UNKNOWN").upper()
    if competition == "HIGH":
        demand_score -= 5
    elif competition == "LOW":
        demand_score += 5
    if specificity < 35:
        demand_score -= 20
    elif specificity < 55:
        demand_score -= 5
    if intent < 35:
        demand_score -= 10
    return {
        "keyword": keyword,
        "volume": volume,
        "intent": max(0, min(100, intent)),
        "specificity": max(0, min(100, specificity)),
        "demand_score": max(0, min(100, demand_score)),
        "competition_level": competition,
        "verification_status": str(row.get("verification_status") or "").upper(),
        "related_keywords": row.get("related_keywords_json") or row.get("related_keywords") or [],
    }


class DemandAgent(BaseAgent):
    def __init__(self, llm_provider: LLMProvider):
        super().__init__(llm_provider, "demand_agent")

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        product = context.get("product", {}) or {}
        rows = context.get("demand_research", []) or []
        product_name = str(product.get("name") or "").strip() or None
        category = str(product.get("category") or "").strip() or None
        scored_rows = [_score_row(row, product_name, category) for row in rows if isinstance(row, dict)]
        best = max(scored_rows, key=lambda item: (item["demand_score"], item["volume"] or 0, item["specificity"]), default=None)
        all_keywords = []
        for row in scored_rows:
            if row["keyword"] and row["keyword"] not in all_keywords:
                all_keywords.append(row["keyword"])

        if best is None:
            output = DemandAgentOutput.model_validate(
                {
                    "monthly_search_volume": None,
                    "best_keyword": None,
                    "related_keywords": [],
                    "keyword_specificity_score": 0,
                    "buyer_intent_score": 0,
                    "demand_score": 0,
                    "demand_status": "UNKNOWN",
                    "main_demand_blocker": "No keyword demand research captured yet.",
                    "next_action": "Collect keyword demand for this product before promotion.",
                    "confidence": "LOW",
                }
            )
        else:
            volume = best["volume"]
            demand_score = best["demand_score"]
            if volume is None:
                demand_status = "UNKNOWN"
            elif demand_score >= 75 and volume >= 1000 and best["specificity"] >= 55 and best["intent"] >= 35:
                demand_status = "STRONG"
            elif demand_score >= 50 or volume >= 300:
                demand_status = "MODERATE"
            elif demand_score > 0:
                demand_status = "WEAK"
            else:
                demand_status = "UNKNOWN"

            if demand_status == "STRONG":
                blocker = None
                next_action = "Keyword demand looks strong. Validate trend stability and profit economics."
            elif demand_status == "MODERATE":
                blocker = "Keyword demand is promising but not yet strong enough."
                next_action = "Collect a few more keyword demand signals before promotion."
            elif demand_status == "WEAK":
                blocker = "Keyword demand looks weak."
                next_action = "Try more specific keywords or pause this idea."
            else:
                blocker = "No keyword demand volume captured yet."
                next_action = "Capture keyword demand data before promoting the idea."

            output = DemandAgentOutput.model_validate(
                {
                    "monthly_search_volume": volume,
                    "best_keyword": best["keyword"],
                    "related_keywords": [{"keyword": keyword} for keyword in all_keywords],
                    "keyword_specificity_score": best["specificity"],
                    "buyer_intent_score": best["intent"],
                    "demand_score": demand_score,
                    "demand_status": demand_status,
                    "main_demand_blocker": blocker,
                    "next_action": next_action,
                    "confidence": "HIGH" if demand_status == "STRONG" else "MEDIUM" if demand_status == "MODERATE" else "LOW",
                }
            )

        return {
            "agent_name": "demand_agent",
            "output_json": output.model_dump(),
            "summary": output.next_action,
            "confidence": output.confidence,
            "warnings": output.warnings,
            "evidence_refs": output.evidence_refs,
        }
