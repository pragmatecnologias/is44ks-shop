from app.agents.base_agent import BaseAgent
from app.llm.base import LLMProvider, Message
from typing import Dict, Any
import json


class DecisionAgent(BaseAgent):
    def __init__(self, llm_provider: LLMProvider):
        super().__init__(llm_provider, "decision_agent")

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        template = self._load_prompt("decision_agent.txt")

        # Pass all agent reports as context
        reports_json = json.dumps(context.get("agent_reports", {}), indent=2)
        prompt = self._format_prompt(template, AGENT_REPORTS=reports_json)

        system_msg = Message(
            "system",
            "You are a product sourcing decision specialist. "
            "Combine all agent reports and return ONLY valid JSON with final decision.",
        )
        user_msg = Message("user", prompt)
        result = await self.llm.complete_json([system_msg, user_msg])

        # Apply decision rules
        reports = context.get("agent_reports", {})
        risk_level = reports.get("risk_agent", {}).get("risk_level", "MEDIUM")
        score = result.get("total_score", 0)
        net_profit = reports.get("profit_agent", {}).get("estimated_net_profit", 0)
        evidence_quality = reports.get("market_agent", {}).get("evidence_quality", "unknown")

        recommendation = result.get("recommendation", "SKIP")

        # Override rules
        if risk_level == "BLOCKED" or result.get("blocked", False):
            recommendation = "BLOCKED"
        elif net_profit < 3:
            if recommendation in ("BUY_SMALL_BATCH", "BUY_SAMPLE"):
                recommendation = "WATCHLIST"
        elif evidence_quality not in ("strong", "moderate"):
            if recommendation in ("BUY_SMALL_BATCH", "BUY_SAMPLE"):
                recommendation = "WATCHLIST"
        elif score >= 85:
            recommendation = "BUY_SMALL_BATCH"
        elif 70 <= score < 85:
            recommendation = "BUY_SAMPLE"
        elif 55 <= score < 70:
            recommendation = "WATCHLIST"
        else:
            recommendation = "SKIP"

        return {
            "agent_name": "decision_agent",
            "output_json": {
                **result,
                "recommendation": recommendation,
                "total_score": score,
            },
            "summary": result.get("reasoning", ""),
            "confidence": result.get("confidence", "MEDIUM"),
            "warnings": result.get("warnings", []),
        }