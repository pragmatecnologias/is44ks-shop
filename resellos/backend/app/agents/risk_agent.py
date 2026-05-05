from app.agents.base_agent import BaseAgent
from app.llm.base import LLMProvider, Message
from typing import Dict, Any, List
from app.schemas.agent_schema import RiskAgentOutput
from app.services.agent_utils import collect_text_fields
from app.services.risk_rules import evaluate_risk_rules
import json


class RiskAgent(BaseAgent):
    def __init__(self, llm_provider: LLMProvider):
        super().__init__(llm_provider, "risk_agent")

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        template = self._load_prompt("risk_agent.txt")

        product = context.get("product", {})
        product_json = json.dumps(product, indent=2)
        prompt = self._format_prompt(template, PRODUCT_JSON=product_json)

        system_msg = Message(
            "system",
            "You are a product risk assessment specialist for reselling platforms. "
            "Analyze the product and return ONLY valid JSON with risk assessment.",
        )
        user_msg = Message("user", prompt)
        try:
            result = await self.llm.complete_json([system_msg, user_msg])
        except Exception:
            result = {}

        rule_result = evaluate_risk_rules(
            {
                "name": product.get("name"),
                "description": product.get("description"),
                "category": product.get("category"),
                "supplier_title": context.get("supplier_title"),
                "supplier_notes": context.get("supplier_notes"),
                "marketplace_notes": context.get("marketplace_notes"),
                "competitor_text": collect_text_fields(context.get("competitor_text"), context.get("competitor_listings")),
            }
        )

        merged = {
            "risk_level": rule_result["risk_level"],
            "blocked": rule_result["blocked"],
            "risk_flags": rule_result["risk_flags"],
            "red_flags": rule_result["red_flags"],
            "requires_manual_review": rule_result["requires_manual_review"],
            "confidence": "HIGH" if rule_result["risk_flags"] else "MEDIUM",
            "summary": result.get("summary", result.get("reasoning_summary", "")),
            "warnings": result.get("warnings", []),
            "evidence_refs": result.get("evidence_refs", []),
        }

        warnings = list({*merged["warnings"], *merged["red_flags"]})

        output = RiskAgentOutput.model_validate(
            {
                **merged,
                "warnings": warnings,
                "summary": merged["summary"] or "Risk evaluation completed.",
            }
        )

        return {
            "agent_name": "risk_agent",
            "output_json": output.model_dump(),
            "summary": output.summary,
            "confidence": output.confidence,
            "warnings": output.warnings,
            "evidence_refs": output.evidence_refs,
        }
