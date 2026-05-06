from app.agents.base_agent import BaseAgent
from app.llm.base import LLMProvider, Message
from typing import Dict, Any
from app.schemas.agent_schema import ProfitAgentOutput, ProfitScenario
import json


class ProfitAgent(BaseAgent):
    def __init__(self, llm_provider: LLMProvider):
        super().__init__(llm_provider, "profit_agent")

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        template = self._load_prompt("profit_agent.txt")

        profit_input = context.get("profit_input", {})
        profit_input_json = json.dumps(profit_input, indent=2)
        prompt = self._format_prompt(template, PROFIT_INPUT=profit_input_json)

        system_msg = Message(
            "system",
            "You are a profit analysis specialist. "
            "Analyze the cost structure and return ONLY valid JSON with profit calculations.",
        )
        user_msg = Message("user", prompt)
        try:
            result = await self.llm.complete_json([system_msg, user_msg])
        except Exception:
            result = {}

        input_data = profit_input
        sale_price = float(input_data.get("expected_sale_price", 0) or 0)
        product_cost = float(input_data.get("product_cost", 0) or 0)
        china_domestic_shipping = float(input_data.get("china_domestic_shipping", input_data.get("supplier_domestic_shipping", 0)) or 0)
        international_shipping = float(input_data.get("international_shipping", input_data.get("import_shipping", 0)) or 0)
        duties = float(input_data.get("duties", 0) or 0)
        inspection_cost = float(input_data.get("inspection_cost", 0) or 0)
        marketplace_fee_fixed = float(input_data.get("platform_fee_fixed", 0) or 0)
        platform_fee_percent = float(input_data.get("platform_fee_percent", input_data.get("marketplace_fee_pct", 0.13)) or 0)
        payment_fee = float(input_data.get("payment_fee", 0) or 0)
        outbound_shipping = float(input_data.get("outbound_shipping") or input_data.get("us_shipping") or 0)
        packaging = float(input_data.get("packaging") or input_data.get("packaging_cost") or 0)
        return_allowance = float(input_data.get("return_allowance", 0) or 0)
        ad_cost = float(input_data.get("ad_cost", 0) or 0)
        buyer_paid_shipping = bool(input_data.get("buyer_paid_shipping", False))
        bundle_quantity = max(int(input_data.get("bundle_quantity", 1) or 1), 1)
        quantity_ordered = max(int(input_data.get("quantity_ordered", 1) or 1), 1)
        damaged_unit_allowance = float(input_data.get("damaged_unit_allowance", 0) or 0)
        shipping_revenue = float(input_data.get("buyer_paid_shipping_amount", outbound_shipping if buyer_paid_shipping else 0) or 0)

        def scenario(
            name: str,
            scenario_sale_price: float,
            shipping_cost: float,
            shipping_revenue_value: float = 0.0,
            bundle_multiplier: int = 1,
            assumptions: list[str] | None = None,
        ) -> dict[str, float | str]:
            unit_product_cost = product_cost * bundle_multiplier
            unit_china_domestic = china_domestic_shipping * bundle_multiplier
            unit_international = international_shipping * bundle_multiplier
            unit_duties = duties * bundle_multiplier
            unit_inspection = inspection_cost * bundle_multiplier
            landed_cost = unit_product_cost + unit_china_domestic + unit_international + unit_duties + unit_inspection + damaged_unit_allowance
            fee_base = scenario_sale_price + shipping_revenue_value
            platform_fee = fee_base * platform_fee_percent + marketplace_fee_fixed
            selling_cost = platform_fee + payment_fee + shipping_cost + packaging + return_allowance + ad_cost
            net_profit = scenario_sale_price + shipping_revenue_value - landed_cost - selling_cost
            margin = (net_profit / scenario_sale_price * 100) if scenario_sale_price > 0 else 0
            decision = "GOOD" if net_profit >= 8 and margin >= 20 else "WEAK" if net_profit > 0 else "LOSS"
            return {
                "name": name,
                "sale_price": round(scenario_sale_price, 2),
                "landed_cost": round(landed_cost, 2),
                "selling_cost": round(selling_cost, 2),
                "net_profit": round(net_profit, 2),
                "margin_percent": round(margin, 2),
                "decision": decision,
                "assumptions": assumptions or ([ "Bundle ships in one package" ] if bundle_multiplier > 1 else [ "Standard parcel shipping" ]),
                "shipping_revenue": round(shipping_revenue_value, 2),
                "shipping_cost": round(shipping_cost, 2),
            }

        buyer_paid = scenario(
            "eBay buyer-paid shipping",
            sale_price,
            outbound_shipping,
            shipping_revenue_value=outbound_shipping,
            bundle_multiplier=1,
            assumptions=[
                "Marketplace fee calculated on item price plus buyer-paid shipping",
                "Shipping charge is shown to the buyer separately",
            ],
        )
        free_ship = scenario(
            "eBay free shipping",
            sale_price,
            outbound_shipping,
            shipping_revenue_value=0,
            bundle_multiplier=1,
            assumptions=[
                "Buyer sees a single all-in price",
                "Outbound shipping is paid by the seller",
            ],
        )
        bundle = scenario(
            f"{bundle_quantity}-pack bundle",
            sale_price * bundle_quantity,
            outbound_shipping,
            shipping_revenue_value=outbound_shipping,
            bundle_multiplier=bundle_quantity,
            assumptions=[
                "Bundle ships in one package",
                "Marketplace fee estimated on the combined item value",
                "Outbound shipping does not scale linearly with quantity",
            ],
        )

        scenarios = [buyer_paid, free_ship, bundle]
        # Prefer single-unit scenarios for the primary estimated_net_profit.
        # Bundle scenarios inflate profit because shipping doesn't scale.
        single_unit_scenarios = [s for s in scenarios if "bundle" not in s["name"].lower()]
        best = max(single_unit_scenarios or scenarios, key=lambda item: float(item["net_profit"]))
        target_net_profit_threshold = 8.0
        break_even = float(best["landed_cost"]) + float(best["selling_cost"])
        minimum_recommended_price = round(break_even * 1.1, 2)
        market_reference_price = sale_price if sale_price > 0 else 0
        target_sale_price = sale_price if sale_price > 0 else 0
        current_net_profit = float(best["net_profit"])
        current_landed_cost = float(best["landed_cost"])
        landed_cost_ratio = round(current_landed_cost / target_sale_price, 4) if target_sale_price > 0 else None
        if landed_cost_ratio is None:
            landed_cost_ratio_status = "UNKNOWN"
        elif landed_cost_ratio <= 0.25:
            landed_cost_ratio_status = "EXCELLENT"
        elif landed_cost_ratio <= 0.40:
            landed_cost_ratio_status = "GOOD"
        elif landed_cost_ratio <= 0.60:
            landed_cost_ratio_status = "WEAK"
        else:
            landed_cost_ratio_status = "BAD"
        gross_margin_percent = round(((target_sale_price - current_landed_cost) / target_sale_price) * 100, 2) if target_sale_price > 0 else None
        if gross_margin_percent is None:
            gross_margin_status = "UNKNOWN"
        elif gross_margin_percent >= 60:
            gross_margin_status = "EXCELLENT"
        elif gross_margin_percent >= 40:
            gross_margin_status = "GOOD"
        elif gross_margin_percent >= 25:
            gross_margin_status = "WEAK"
        else:
            gross_margin_status = "BAD"
        max_landed_cost_for_target_profit_raw = round(
            float(best["sale_price"]) + float(best["shipping_revenue"]) - float(best["selling_cost"]) - target_net_profit_threshold,
            2,
        )
        max_landed_cost_for_target_profit = max(0.0, max_landed_cost_for_target_profit_raw)
        target_profit_feasible = max_landed_cost_for_target_profit_raw > 0
        required_sale_price_for_target_profit = max(
            0.0,
            round(float(best["landed_cost"]) + float(best["selling_cost"]) + target_net_profit_threshold - float(best["shipping_revenue"]), 2),
        )
        profit_gap_to_buy_sample = round(max(0.0, target_net_profit_threshold - current_net_profit), 2)

        output = ProfitAgentOutput.model_validate(
            {
                "scenarios": [ProfitScenario.model_validate(item).model_dump() for item in scenarios],
                "estimated_net_profit": current_net_profit,
                "current_net_profit": current_net_profit,
                "target_net_profit_threshold": target_net_profit_threshold,
                "profit_gap_to_buy_sample": profit_gap_to_buy_sample,
                "current_landed_cost": current_landed_cost,
                "max_landed_cost_for_target_profit": max_landed_cost_for_target_profit,
                "max_landed_cost_for_target_profit_raw": max_landed_cost_for_target_profit_raw,
                "target_profit_feasible": target_profit_feasible,
                "current_target_sale_price": round(target_sale_price, 2),
                "required_sale_price_for_target_profit": required_sale_price_for_target_profit,
                "landed_cost_ratio": landed_cost_ratio,
                "landed_cost_ratio_status": landed_cost_ratio_status,
                "gross_margin_percent": gross_margin_percent,
                "gross_margin_status": gross_margin_status,
                "break_even_price": round(break_even, 2),
                "minimum_recommended_price": minimum_recommended_price,
                "target_sale_price": round(target_sale_price, 2),
                "market_reference_price": round(market_reference_price, 2),
                "best_scenario": str(best["name"]),
                "summary": result.get(
                    "summary",
                    f"Best scenario: {best['name']} with net profit ${best['net_profit']:.2f}.",
                ),
                "confidence": "MEDIUM" if best["net_profit"] > 0 else "LOW",
                "warnings": result.get("warnings", []),
                "evidence_refs": result.get("evidence_refs", []),
            }
        )

        return {
            "agent_name": "profit_agent",
            "output_json": output.model_dump(),
            "summary": output.summary,
            "confidence": output.confidence,
            "warnings": output.warnings,
            "evidence_refs": output.evidence_refs,
        }
