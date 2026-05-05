from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict

from app.agents.base_agent import BaseAgent
from app.llm.base import LLMProvider, Message
from app.schemas.agent_schema import ReorderAgentOutput


def _days_between(start: datetime | None, end: datetime | None = None) -> float:
    if not start:
        return 0.0
    end = end or datetime.now(timezone.utc)
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    return max((end - start).total_seconds() / 86400.0, 1.0)


class ReorderAgent(BaseAgent):
    def __init__(self, llm_provider: LLMProvider):
        super().__init__(llm_provider, "reorder_agent")

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        template = self._load_prompt("reorder_agent.txt")

        product = context.get("product", {})
        inventory = context.get("inventory", [])
        sales = context.get("sales", [])
        profit_summary = context.get("profit_summary", {})

        prompt = self._format_prompt(
            template,
            PRODUCT_JSON=json.dumps(product, indent=2),
            INVENTORY_JSON=json.dumps(inventory, indent=2),
            SALES_JSON=json.dumps(sales, indent=2),
            PROFIT_SUMMARY_JSON=json.dumps(profit_summary, indent=2),
        )

        system_msg = Message(
            "system",
            "You are a reorder intelligence specialist. "
            "Return ONLY valid JSON. "
            "Judge whether the product should be reordered, scaled, killed, or left alone.",
        )
        user_msg = Message("user", prompt)
        try:
            result = await self.llm.complete_json([system_msg, user_msg])
        except Exception:
            result = {}

        inventory_rows = inventory if isinstance(inventory, list) else []
        sales_rows = sales if isinstance(sales, list) else []

        current_inventory = sum(int(row.get("quantity_on_hand") or 0) for row in inventory_rows)
        quantity_ordered = sum(int(row.get("quantity_ordered") or 0) for row in inventory_rows)
        quantity_sold = sum(int(row.get("quantity_sold") or 0) for row in inventory_rows)
        quantity_returned = sum(int(row.get("quantity_returned") or 0) for row in inventory_rows)

        if quantity_sold == 0 and sales_rows:
            quantity_sold = sum(int(row.get("quantity") or 1) for row in sales_rows)
        if quantity_returned == 0 and sales_rows:
            quantity_returned = sum(int(row.get("quantity") or 1) for row in sales_rows if row.get("returned"))

        reorder_point = max((int(row.get("reorder_point") or 0) for row in inventory_rows), default=0)
        average_landed_cost = next((float(row.get("average_landed_cost")) for row in inventory_rows if row.get("average_landed_cost") is not None), None)

        product_created_at = product.get("created_at")
        created_dt = None
        if isinstance(product_created_at, str):
            try:
                created_dt = datetime.fromisoformat(product_created_at.replace("Z", "+00:00"))
            except ValueError:
                created_dt = None

        date_values = []
        for row in sales_rows:
            sale_date = row.get("sale_date")
            if isinstance(sale_date, str):
                try:
                    date_values.append(datetime.fromisoformat(sale_date.replace("Z", "+00:00")))
                except ValueError:
                    continue

        active_days = _days_between(min(date_values) if date_values else created_dt)
        average_daily_sales = round(quantity_sold / active_days, 2) if active_days > 0 else 0.0
        days_of_cover = round(current_inventory / average_daily_sales, 1) if average_daily_sales > 0 else float("inf")
        return_rate = round((quantity_returned / quantity_sold) * 100, 2) if quantity_sold > 0 else 0.0

        if return_rate >= 20:
            recommendation = "KILL_PRODUCT"
        elif quantity_sold <= 0 and current_inventory <= 0:
            recommendation = "DO_NOT_REORDER"
        elif average_daily_sales >= 1.0 and current_inventory <= reorder_point:
            recommendation = "SCALE" if quantity_sold >= 20 else "REORDER_MEDIUM"
        elif average_daily_sales > 0 and days_of_cover <= 14:
            recommendation = "REORDER_SMALL"
        elif average_daily_sales > 0 and days_of_cover <= 30:
            recommendation = "REORDER_SMALL"
        else:
            recommendation = "DO_NOT_REORDER"

        if current_inventory > reorder_point and days_of_cover > 45 and recommendation != "KILL_PRODUCT":
            recommendation = "DO_NOT_REORDER"

        stockout_risk = "HIGH" if average_daily_sales > 0 and days_of_cover <= 14 else "MEDIUM" if average_daily_sales > 0 and days_of_cover <= 30 else "LOW"
        max_reorder_qty = 0
        if recommendation == "REORDER_SMALL":
            max_reorder_qty = max(reorder_point or 5, 5)
        elif recommendation == "REORDER_MEDIUM":
            max_reorder_qty = max(reorder_point * 2 if reorder_point else 20, 20)
        elif recommendation == "SCALE":
            max_reorder_qty = max(reorder_point * 3 if reorder_point else 40, 40)

        if recommendation == "KILL_PRODUCT":
            reason = "Return rate is too high to justify replenishment."
        elif recommendation == "SCALE":
            reason = "Sell-through is strong and on-hand inventory is tight."
        elif recommendation == "REORDER_MEDIUM":
            reason = "Demand is present and inventory cover is short."
        elif recommendation == "REORDER_SMALL":
            reason = "Product is moving and should be topped up carefully."
        else:
            reason = "Current sell-through does not justify replenishment."

        output = ReorderAgentOutput.model_validate(
            {
                "reorder_recommendation": recommendation,
                "current_inventory": current_inventory,
                "quantity_sold": quantity_sold,
                "quantity_ordered": quantity_ordered,
                "quantity_returned": quantity_returned,
                "average_daily_sales": average_daily_sales,
                "days_of_cover": days_of_cover if days_of_cover != float("inf") else None,
                "reorder_point": reorder_point,
                "max_reorder_qty": max_reorder_qty,
                "stockout_risk": stockout_risk,
                "return_rate_percent": return_rate,
                "average_landed_cost": average_landed_cost,
                "reorder_reason": result.get("reorder_reason", reason),
                "summary": result.get(
                    "summary",
                    f"Reorder recommendation: {recommendation} based on {quantity_sold} sold and {current_inventory} on hand.",
                ),
                "confidence": "HIGH" if quantity_sold >= 10 else "MEDIUM" if quantity_sold > 0 else "LOW",
                "warnings": result.get("warnings", []),
                "evidence_refs": result.get("evidence_refs", []),
            }
        )

        return {
            "agent_name": "reorder_agent",
            "output_json": output.model_dump(),
            "summary": output.summary,
            "confidence": output.confidence,
            "warnings": output.warnings,
            "evidence_refs": output.evidence_refs,
        }
