from __future__ import annotations

import asyncio
import unittest

from app.agents.decision_agent import DecisionAgent
from app.agents.competition_agent import CompetitionAgent
from app.agents.market_agent import MarketAgent
from app.agents.profit_agent import ProfitAgent
from app.agents.reorder_agent import ReorderAgent
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
                    "supplier_summary": {"unit_cost": 4.15, "international_shipping_estimate": 1.2},
                    "agent_reports": {
                        "risk_agent": {"output_json": {"risk_level": "LOW", "blocked": False}},
                        "market_agent": {
                            "output_json": {
                                "evidence_quality": "MEDIUM",
                                "sold_listing_count": 4,
                                "active_listing_count": 12,
                                "insufficient_data": False,
                                "median_sold_price": 18.99,
                                "median_active_price": 21.99,
                            }
                        },
                        "profit_agent": {"output_json": {"estimated_net_profit": 7.42, "scenarios": [{}]}},
                    }
                }
            )
        )

        self.assertEqual(result["output_json"]["recommendation"], "BUY_SAMPLE")
        self.assertGreater(result["output_json"]["total_score"], 0)

    def test_decision_agent_caps_buy_when_market_data_is_thin(self) -> None:
        agent = DecisionAgent(self.llm)
        result = asyncio.run(
            agent.run(
                {
                    "product": {"name": "Test product"},
                    "supplier_summary": {"unit_cost": 4.15, "international_shipping_estimate": 1.2},
                    "agent_reports": {
                        "risk_agent": {"output_json": {"risk_level": "LOW", "blocked": False}},
                        "market_agent": {
                            "output_json": {
                                "evidence_quality": "LOW",
                                "sold_listing_count": 0,
                                "active_listing_count": 12,
                                "insufficient_data": True,
                                "market_price_missing": True,
                            }
                        },
                        "profit_agent": {"output_json": {"estimated_net_profit": 12.0, "scenarios": [{}]}},
                    },
                }
            )
        )

        self.assertEqual(result["output_json"]["recommendation"], "WATCHLIST")
        self.assertTrue(result["output_json"]["hard_blockers"])

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

    def test_market_agent_uses_evidence_rows(self) -> None:
        agent = MarketAgent(self.llm)
        result = asyncio.run(
            agent.run(
                {
                    "product": {"name": "Test product"},
                    "marketplace_evidence": [
                        {"marketplace": "eBay", "evidence_type": "SOLD_LISTING", "price": 10.0, "shipping_price": 2.0},
                        {"marketplace": "eBay", "evidence_type": "SOLD_LISTING", "price": 12.0, "shipping_price": 2.5},
                        {"marketplace": "eBay", "evidence_type": "SOLD_LISTING", "price": 14.0, "shipping_price": 3.0},
                        {"marketplace": "eBay", "evidence_type": "SOLD_LISTING", "price": 16.0, "shipping_price": 3.0},
                        {"marketplace": "eBay", "evidence_type": "SOLD_LISTING", "price": 18.0, "shipping_price": 3.5},
                        {"marketplace": "eBay", "evidence_type": "ACTIVE_LISTING", "price": 19.0, "shipping_price": 4.0},
                        {"marketplace": "eBay", "evidence_type": "ACTIVE_LISTING", "price": 20.0, "shipping_price": 4.0},
                    ],
                }
            )
        )

        output = result["output_json"]
        self.assertEqual(output["sold_listing_count"], 5)
        self.assertEqual(output["active_listing_count"], 2)
        self.assertEqual(output["median_sold_price"], 14.0)
        self.assertFalse(output["insufficient_data"])

    def test_competition_agent_reads_competitor_listings(self) -> None:
        agent = CompetitionAgent(self.llm)
        result = asyncio.run(
            agent.run(
                {
                    "product": {"name": "Car seat gap organizer", "category": "Automotive"},
                    "market_summary": {"median_sold_price": 18.99},
                    "competitor_listings": [
                        {"price": 19.99, "sold": False, "photo_score": 45, "title_score": 55, "description_score": 50},
                        {"price": 18.49, "sold": True, "photo_score": 52, "title_score": 58, "description_score": 40},
                        {"price": 17.99, "sold": False, "photo_score": 48, "title_score": 60, "description_score": 45},
                    ],
                }
            )
        )

        output = result["output_json"]
        self.assertIn(output["competition_level"], {"LOW", "MEDIUM", "HIGH", "UNKNOWN"})
        self.assertGreater(output["listing_gap_score"], 0)
        self.assertTrue(output["weaknesses"])
        self.assertTrue(output["recommended_angle"])

    def test_reorder_agent_uses_inventory_and_sales(self) -> None:
        agent = ReorderAgent(self.llm)
        result = asyncio.run(
            agent.run(
                {
                    "product": {"name": "Car seat gap organizer", "created_at": "2026-05-01T00:00:00+00:00"},
                    "inventory": [
                        {"quantity_on_hand": 8, "quantity_ordered": 40, "quantity_sold": 32, "quantity_returned": 1, "reorder_point": 10}
                    ],
                    "sales": [
                        {"sale_date": "2026-05-02T00:00:00+00:00", "quantity": 1, "returned": False},
                        {"sale_date": "2026-05-03T00:00:00+00:00", "quantity": 1, "returned": False},
                        {"sale_date": "2026-05-04T00:00:00+00:00", "quantity": 1, "returned": False},
                    ],
                }
            )
        )

        output = result["output_json"]
        self.assertIn(output["reorder_recommendation"], {"DO_NOT_REORDER", "REORDER_SMALL", "REORDER_MEDIUM", "SCALE", "KILL_PRODUCT"})
        self.assertGreaterEqual(output["current_inventory"], 0)
        self.assertGreaterEqual(output["quantity_sold"], 0)
        self.assertTrue(output["reorder_reason"])


if __name__ == "__main__":
    unittest.main()
