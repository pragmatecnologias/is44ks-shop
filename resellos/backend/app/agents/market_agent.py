from app.agents.base_agent import BaseAgent
from app.llm.base import LLMProvider, Message
from typing import Dict, Any
import json


class MarketAgent(BaseAgent):
    def __init__(self, llm_provider: LLMProvider):
        super().__init__(llm_provider, "market_agent")

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        template = self._load_prompt("market_agent.txt")

        product_json = json.dumps(context.get("product", {}), indent=2)
        marketplace_json = json.dumps(context.get("marketplace_research", {}), indent=2)
        competitor_json = json.dumps(context.get("competitor_listings", []), indent=2)

        prompt = self._format_prompt(
            template,
            PRODUCT_JSON=product_json,
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
        result = await self.llm.complete_json([system_msg, user_msg])

        return {
            "agent_name": "market_agent",
            "output_json": result,
            "summary": result.get("summary", ""),
            "confidence": result.get("confidence", "MEDIUM"),
            "warnings": result.get("warnings", []),
        }