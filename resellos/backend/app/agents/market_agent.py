from app.agents.base_agent import BaseAgent
from app.llm.base import LLMProvider, Message
from typing import Dict, Any
from app.schemas.agent_schema import MarketAgentOutput
import json


class MarketAgent(BaseAgent):
    def __init__(self, llm_provider: LLMProvider):
        super().__init__(llm_provider, "market_agent")

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        template = self._load_prompt("market_agent.txt")

        product = context.get("product", {})
        marketplace_json = json.dumps(context.get("marketplace_research", []), indent=2)
        competitor_json = json.dumps(context.get("competitor_listings", []), indent=2)
        evidence = context.get("marketplace_evidence", [])
        evidence_count = len(evidence) if isinstance(evidence, list) else 0

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

        active_listing_count = 0
        sold_listing_count = 0
        median_active_price = None
        median_sold_price = None
        evidence_quality = "LOW"
        insufficient_data = True

        if isinstance(context.get("marketplace_research"), list):
            research_rows = context["marketplace_research"]
            active_listing_count = sum(int(row.get("active_listing_count") or 0) for row in research_rows)
            sold_listing_count = sum(int(row.get("sold_listing_count") or 0) for row in research_rows)
            active_prices = [float(row.get("median_active_price")) for row in research_rows if row.get("median_active_price") is not None]
            sold_prices = [float(row.get("median_sold_price")) for row in research_rows if row.get("median_sold_price") is not None]
            if active_prices:
                median_active_price = round(sorted(active_prices)[len(active_prices) // 2], 2)
            if sold_prices:
                median_sold_price = round(sorted(sold_prices)[len(sold_prices) // 2], 2)

        if sold_listing_count >= 10 and active_listing_count >= 10 and median_sold_price is not None:
            evidence_quality = "HIGH"
            insufficient_data = False
        elif sold_listing_count > 0 or active_listing_count > 0 or evidence_count > 0:
            evidence_quality = "MEDIUM"
            insufficient_data = sold_listing_count == 0

        output = MarketAgentOutput.model_validate(
            {
                "evidence_quality": evidence_quality,
                "insufficient_data": insufficient_data,
                "active_listing_count": active_listing_count,
                "sold_listing_count": sold_listing_count,
                "demand_signal": result.get("demand_signal", "UNKNOWN"),
                "competition_level": result.get("competition_level", "UNKNOWN"),
                "median_active_price": median_active_price,
                "median_sold_price": median_sold_price,
                "summary": result.get("summary", "Marketplace evidence analyzed."),
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
