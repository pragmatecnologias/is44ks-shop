from __future__ import annotations

import asyncio
import unittest

from app.agents.decision_agent import DecisionAgent
from app.agents.profit_agent import ProfitAgent
from app.agents.risk_agent import RiskAgent
from app.llm.base import LLMProvider, Message
from app.services.agent_utils import agent_data
from app.services.risk_rules import evaluate_risk_rules


class FakeLLMProvider(LLMProvider):
    async def complete(self, messages: list[Message], **kwargs) -> str:
        return ""

    async def complete_json(self, messages: list[Message], **kwargs):
        return {}


class AgentContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.llm = FakeLLMProvider()

    def test_agent_data_reads_nested_output_json(self) -> None:
        reports = {
            "risk_agent": {"output_json": {"risk_level": "LOW", "blocked": False}},
            "profit_agent": {"output_json": {"estimated_net_profit": 7.42}},
            "market_agent": {"output_json": {"evidence_quality": "MEDIUM"}},
        }

        self.assertEqual(agent_data(reports, "risk_agent")["risk_level"], "LOW")
        self.assertEqual(agent_data(reports, "profit_agent")["estimated_net_profit"], 7.42)
        self.assertEqual(agent_data(reports, "market_agent")["evidence_quality"], "MEDIUM")

    def test_risk_rules_allow_generic_pet_accessory(self) -> None:
        result = evaluate_risk_rules(
            {
                "name": "Pet hair remover",
                "description": "Reusable generic pet accessory",
                "category": "pet accessory",
                "supplier_title": "Generic pet grooming tool",
            }
        )

        self.assertEqual(result["risk_level"], "LOW")
        self.assertFalse(result["blocked"])
        self.assertTrue(any(flag["rule_id"] == "pet_accessory" for flag in result["risk_flags"]))

    def test_decision_agent_uses_nested_reports(self) -> None:
        agent = DecisionAgent(self.llm)
        result = asyncio.run(
            agent.run(
                {
                    "agent_reports": {
                        "risk_agent": {"output_json": {"risk_level": "LOW", "blocked": False}},
                        "market_agent": {
                            "output_json": {
                                "evidence_quality": "MEDIUM",
                                "sold_listing_count": 4,
                                "active_listing_count": 12,
                                "insufficient_data": False,
                            }
                        },
                        "profit_agent": {"output_json": {"estimated_net_profit": 7.42, "scenarios": [{}]}},
                    }
                }
            )
        )

        self.assertEqual(result["output_json"]["recommendation"], "BUY_SAMPLE")
        self.assertGreater(result["output_json"]["total_score"], 0)

    def test_profit_agent_outputs_three_scenarios(self) -> None:
        agent = ProfitAgent(self.llm)
        result = asyncio.run(
            agent.run(
                {
                    "profit_input": {
                        "expected_sale_price": 18.99,
                        "product_cost": 4.15,
                        "china_domestic_shipping": 0.35,
                        "international_shipping": 1.2,
                        "duties": 0,
                        "inspection_cost": 0,
                        "platform_fee_percent": 0.13,
                        "platform_fee_fixed": 0,
                        "payment_fee": 0,
                        "outbound_shipping": 4.0,
                        "packaging": 0.4,
                        "return_allowance": 0.5,
                        "ad_cost": 0,
                        "buyer_paid_shipping": True,
                        "bundle_quantity": 2,
                    }
                }
            )
        )

        scenarios = result["output_json"]["scenarios"]
        self.assertEqual(len(scenarios), 3)
        self.assertGreater(result["output_json"]["estimated_net_profit"], 0)


if __name__ == "__main__":
    unittest.main()
