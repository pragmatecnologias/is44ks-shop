from app.agents.base_agent import BaseAgent
from app.llm.base import LLMProvider, Message
from typing import Dict, Any
from app.schemas.agent_schema import DecisionAgentOutput
from app.services.agent_utils import agent_data
import json


class DecisionAgent(BaseAgent):
    def __init__(self, llm_provider: LLMProvider):
        super().__init__(llm_provider, "decision_agent")

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        template = self._load_prompt("decision_agent.txt")

        # Pass all agent reports as context
        reports = context.get("agent_reports", {})
        reports_json = json.dumps(reports, indent=2)
        prompt = self._format_prompt(template, AGENT_REPORTS=reports_json)

        system_msg = Message(
            "system",
            "You are a product sourcing decision specialist. "
            "Combine all agent reports and return ONLY valid JSON with final decision.",
        )
        user_msg = Message("user", prompt)
        try:
            llm_result = await self.llm.complete_json([system_msg, user_msg])
        except Exception:
            llm_result = {}

        risk = agent_data(reports, "risk_agent")
        market = agent_data(reports, "market_agent")
        profit = agent_data(reports, "profit_agent")

        risk_level = str(risk.get("risk_level", "MEDIUM"))
        blocked = bool(risk.get("blocked", False))
        net_profit = float(profit.get("estimated_net_profit", 0) or 0)
        evidence_quality = str(market.get("evidence_quality", "LOW")).upper()
        insufficient_data = bool(market.get("insufficient_data", True))
        sold_listing_count = int(market.get("sold_listing_count", 0) or 0)
        active_listing_count = int(market.get("active_listing_count", 0) or 0)
        market_price_missing = float(market.get("median_sold_price") or market.get("median_active_price") or 0) <= 0

        score = 50
        if risk_level == "LOW":
            score += 20
        elif risk_level == "MEDIUM":
            score += 5
        elif risk_level == "HIGH":
            score -= 15
        elif risk_level == "BLOCKED":
            score = 0

        if net_profit >= 15:
            score += 25
        elif net_profit >= 8:
            score += 15
        elif net_profit >= 3:
            score += 5
        else:
            score -= 15

        if evidence_quality == "HIGH":
            score += 20
        elif evidence_quality == "MEDIUM":
            score += 10
        else:
            score -= 10

        score = max(0, min(100, score))

        missing_evidence = []
        if sold_listing_count == 0:
            missing_evidence.append("Sold listings missing")
        if active_listing_count == 0:
            missing_evidence.append("Active listings missing")
        if insufficient_data:
            missing_evidence.append("Marketplace evidence quality is low")
        if market_price_missing:
            missing_evidence.append("Sold or active market price missing")
        if not profit.get("scenarios"):
            missing_evidence.append("Profit scenarios missing")

        assumptions = []
        if net_profit == 0:
            assumptions.append("Profit estimate depends on placeholder costs until supplier data is added.")

        if blocked or risk_level == "BLOCKED":
            recommendation = "BLOCKED"
            next_action = "Stop research and resolve risk flags before spending money."
            reason = "Risk rules blocked this product."
        elif score >= 85 and net_profit >= 10 and evidence_quality == "HIGH":
            recommendation = "BUY_SMALL_BATCH"
            next_action = "Order a small test batch if supplier terms are acceptable."
            reason = "Strong evidence, healthy margin, and acceptable risk."
        elif score >= 70 and net_profit >= 3:
            recommendation = "BUY_SAMPLE"
            next_action = "Buy a sample only after filling the missing evidence gaps."
            reason = "Promising product with enough margin to justify sample testing."
        elif score >= 55:
            recommendation = "WATCHLIST"
            next_action = "Collect more sold listings and supplier proof before ordering."
            reason = "The idea is promising, but evidence is still thin."
        else:
            recommendation = "SKIP"
            next_action = "Skip for now and move on to stronger candidates."
            reason = "Insufficient confidence or weak economics."

        if insufficient_data or market_price_missing:
            if recommendation in {"BUY_SAMPLE", "BUY_SMALL_BATCH"}:
                recommendation = "WATCHLIST"
                next_action = "Add sold listings and a real market price before ordering."
                reason = "Market evidence is too thin for a sample order."

        output = DecisionAgentOutput.model_validate(
            {
                "recommendation": recommendation,
                "total_score": score,
                "confidence": "HIGH" if score >= 75 else "MEDIUM" if score >= 55 else "LOW",
                "reason": llm_result.get("reason", reason),
                "next_action": llm_result.get("next_action", next_action),
                "missing_evidence": missing_evidence,
                "assumptions": assumptions,
                "blocked": blocked,
                "warnings": llm_result.get("warnings", []),
                "evidence_refs": llm_result.get("evidence_refs", []),
            }
        )

        return {
            "agent_name": "decision_agent",
            "output_json": output.model_dump(),
            "summary": output.reason,
            "confidence": output.confidence,
            "warnings": output.warnings,
            "evidence_refs": output.evidence_refs,
        }
