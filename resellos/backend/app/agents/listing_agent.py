from app.agents.base_agent import BaseAgent
from app.llm.base import LLMProvider, Message
from typing import Dict, Any
import json


TRADEMARK_TERMS = {
    "authentic", "genuine", "official", "authorized", "licensed",
    "brand new", "factory sealed", "original", "real", "verified",
}


class ListingAgent(BaseAgent):
    def __init__(self, llm_provider: LLMProvider):
        super().__init__(llm_provider, "listing_agent")

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        template = self._load_prompt("listing_agent.txt")

        listing_input = json.dumps(context.get("listing_input", {}), indent=2)
        prompt = self._format_prompt(template, LISTING_INPUT=listing_input)

        system_msg = Message(
            "system",
            "You are a listing strategy specialist for eBay, Mercari, and Facebook Marketplace. "
            "Return ONLY valid JSON. "
            "IMPORTANT: Do NOT use trademark terms in titles. "
            "eBay titles must be under 80 characters.",
        )
        user_msg = Message("user", prompt)
        result = await self.llm.complete_json([system_msg, user_msg])

        warnings = []
        ebay_title = result.get("ebay_title", "")
        if len(ebay_title) > 80:
            warnings.append(f"eBay title exceeds 80 chars ({len(ebay_title)} chars)")

        for term in TRADEMARK_TERMS:
            if term in ebay_title.lower():
                warnings.append(f"Trademark term in title: '{term}'")

        return {
            "agent_name": "listing_agent",
            "output_json": {
                **result,
                "ebay_title": ebay_title[:80] if len(ebay_title) > 80 else ebay_title,
                "trademark_warnings": warnings,
            },
            "summary": result.get("summary", ""),
            "confidence": result.get("confidence", "MEDIUM"),
            "warnings": warnings,
        }