from app.agents.base_agent import BaseAgent
from app.llm.base import LLMProvider, Message
from typing import Dict, Any, List


COUNTERFEIT_BRANDS = {
    "nike", "apple", "rolex", "gucci", "chanel", "louis vuitton", "lv",
    "adidas", "hermes", "prada", "dior", "versace", "burberry", "cartier",
    "samsung", "sony", "microsoft", "beats", "uggs", "north face", "patagonia",
    "coach", "michael kors", "kate spade", "fendi", "balenciaga", "givenchy",
    "armani", "ralph lauren", "polo ralph lauren", "tommy hilfiger",
}

UNSAFE_CATEGORIES = {
    "battery", "lithium", "batteries", "cell", "power bank",
    "medical", "healthcare", "medical device", "diagnostic",
    "cosmetic", "skincare", "beauty", "makeup", "personal care",
    "supplement", "vitamin", "nutraceutical", "dietary supplement",
    "pharmaceutical", "drug", "medication", "rx", "prescription",
    "children toy", "kids toy", "childcare", "infant",
    "food", "edible", "consumable",
    "firearm", "weapon", "ammunition", "explosive",
    "animal", "pet", "livestock",
    "pornography", "adult", "mature",
    "cannabis", "thc", "cbd", "marijuana", "hemp",
    "alcohol", "tobacco", "vape", "e-cigarette",
}


class RiskAgent(BaseAgent):
    def __init__(self, llm_provider: LLMProvider):
        super().__init__(llm_provider, "risk_agent")

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        template = self._load_prompt("risk_agent.txt")

        import json
        product_json = json.dumps(context.get("product", {}), indent=2)
        prompt = self._format_prompt(template, PRODUCT_JSON=product_json)

        system_msg = Message(
            "system",
            "You are a product risk assessment specialist for reselling platforms. "
            "Analyze the product and return ONLY valid JSON with risk assessment.",
        )
        user_msg = Message("user", prompt)
        result = await self.llm.complete_json([system_msg, user_msg])

        risk_level = result.get("risk_level", "MEDIUM")
        blocked = result.get("blocked", False)
        warnings = []

        # Rule-based overrides
        product_name = context.get("product", {}).get("name", "").lower()
        category = context.get("product", {}).get("category", "").lower()

        for brand in COUNTERFEIT_BRANDS:
            if brand in product_name:
                blocked = True
                risk_level = "BLOCKED"
                warnings.append(f"Counterfeit/trademark brand detected: {brand}")

        for unsafe in UNSAFE_CATEGORIES:
            if unsafe in category:
                blocked = True
                risk_level = "BLOCKED"
                warnings.append(f"Unsafe category detected: {unsafe}")

        # Merge red flags
        existing_flags = result.get("red_flags", [])
        if isinstance(existing_flags, list):
            warnings = warnings + [w for w in existing_flags if w not in warnings]

        return {
            "agent_name": "risk_agent",
            "output_json": {
                **result,
                "blocked": blocked,
                "risk_level": risk_level,
                "red_flags": warnings,
            },
            "summary": result.get("reasoning_summary", ""),
            "confidence": result.get("confidence", "MEDIUM"),
            "warnings": warnings,
        }