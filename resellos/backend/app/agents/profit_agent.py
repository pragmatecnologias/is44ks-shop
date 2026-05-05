from app.agents.base_agent import BaseAgent
from app.llm.base import LLMProvider, Message
from typing import Dict, Any
import json


class ProfitAgent(BaseAgent):
    def __init__(self, llm_provider: LLMProvider):
        super().__init__(llm_provider, "profit_agent")

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        template = self._load_prompt("profit_agent.txt")

        profit_input = json.dumps(context.get("profit_input", {}), indent=2)
        prompt = self._format_prompt(template, PROFIT_INPUT=profit_input)

        system_msg = Message(
            "system",
            "You are a profit analysis specialist. "
            "Analyze the cost structure and return ONLY valid JSON with profit calculations.",
        )
        user_msg = Message("user", prompt)
        result = await self.llm.complete_json([system_msg, user_msg])

        # Compute structurally to ensure accuracy
        input_data = context.get("profit_input", {})
        sale_price = input_data.get("expected_sale_price", 0)
        product_cost = input_data.get("product_cost", 0)
        import_shipping = input_data.get("import_shipping", 0)
        marketplace_fee_pct = input_data.get("marketplace_fee_pct", 0.13)
        us_shipping = input_data.get("us_shipping", 0)
        packaging = input_data.get("packaging", 0)
        return_allowance = input_data.get("return_allowance", 0)
        ad_cost = input_data.get("ad_cost", 0)

        marketplace_fee = sale_price * marketplace_fee_pct

        landed_cost = product_cost + import_shipping + us_shipping + packaging
        total_cost = landed_cost + marketplace_fee + return_allowance + ad_cost
        net_profit = sale_price - total_cost

        margin = (net_profit / sale_price * 100) if sale_price > 0 else 0
        roi = (net_profit / total_cost * 100) if total_cost > 0 else 0
        break_even = total_cost

        return {
            "agent_name": "profit_agent",
            "output_json": {
                **result,
                "landed_cost": round(landed_cost, 2),
                "total_cost": round(total_cost, 2),
                "estimated_net_profit": round(net_profit, 2),
                "margin_percent": round(margin, 2),
                "roi_percent": round(roi, 2),
                "break_even_price": round(break_even, 2),
                "minimum_recommended_price": round(break_even * 1.1, 2),
                "marketplace_fee_calculated": round(marketplace_fee, 2),
            },
            "summary": result.get("summary", f"Net profit: ${net_profit:.2f}, Margin: {margin:.1f}%"),
            "confidence": result.get("confidence", "MEDIUM"),
            "warnings": result.get("warnings", []),
        }