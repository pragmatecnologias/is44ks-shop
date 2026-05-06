from __future__ import annotations

import asyncio
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.agents.decision_agent import DecisionAgent
from app.agents.competition_agent import CompetitionAgent
from app.agents.demand_agent import DemandAgent
from app.agents.market_agent import MarketAgent
from app.agents.profit_agent import ProfitAgent
from app.agents.quick_scan_agent import QuickScanAgent
from app.agents.reorder_agent import ReorderAgent
from app.agents.risk_agent import RiskAgent
from app.agents.trend_agent import TrendAgent
from app.db import Base
from app.llm.base import LLMProvider, Message
from app.models.product import Product
from app.models.supplier import AgentReport, CompetitorListing, DiscoveryTask, MarketplaceEvidence, ProfitAnalysis, ProductIdea, ProductSource
from app.services.agent_utils import agent_data
from app.services.discovery_service import DiscoveryService
from app.services.validation_checklist_service import ValidationChecklistService
from app.services.risk_rules import evaluate_risk_rules
from app.schemas.product_schema import ResearchTaskUpdate


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

    def test_quick_scan_agent_is_conservative(self) -> None:
        agent = QuickScanAgent()
        result = agent.run(
            {
                "idea_name": "Car seat gap organizer",
                "category": "Car accessories",
                "source_platform": "Alibaba",
                "rough_supplier_cost": 2.5,
                "estimated_landed_cost": 5.0,
                "notes": "Small generic accessory.",
            }
        )

        output = result["output_json"]
        self.assertIn(output["quick_scan_verdict"], {"REJECT", "NEEDS_MARKET_CHECK", "NEEDS_SUPPLIER_CHECK", "PROMISING_FOR_RESEARCH"})
        self.assertEqual(output["buy_readiness_status"], "NOT_READY")
        self.assertIsInstance(output["suggested_keywords"], dict)
        self.assertIn("required_next_evidence", output)

    def test_decision_agent_uses_nested_reports(self) -> None:
        agent = DecisionAgent(self.llm)
        result = asyncio.run(
            agent.run(
                {
                    "supplier_summary": {"unit_cost": 4.15, "international_shipping_estimate": 1.2, "verification_status": "API_IMPORTED"},
                    "agent_reports": {
                        "risk_agent": {"output_json": {"risk_level": "LOW", "blocked": False}},
                        "market_agent": {
                            "output_json": {
                                "evidence_quality": "MEDIUM",
                                "sold_listing_count": 4,
                                "verified_sold_listing_count": 4,
                                "active_listing_count": 12,
                                "verified_active_listing_count": 12,
                                "insufficient_data": False,
                                "market_price_missing": False,
                                "median_sold_price": 18.99,
                                "median_active_price": 21.99,
                                "verification_coverage": 1.0,
                            }
                        },
                        "profit_agent": {"output_json": {"estimated_net_profit": 7.42, "scenarios": [{}]}},
                    }
                }
            )
        )

        self.assertEqual(result["output_json"]["recommendation"], "WATCHLIST")
        self.assertEqual(result["output_json"]["research_verdict"], "PROMISING_RESEARCH")
        self.assertIn(result["output_json"]["buy_readiness_status"], {"NOT_READY", "ALMOST_READY", "READY"})
        self.assertIn(result["output_json"]["main_blocker"], {"None", "Sold listings missing", "Active listings missing", "Marketplace evidence is insufficient for a buy decision.", "Supplier cost is missing.", "Supplier cost is not verified.", "Competition gap is too small to compete reliably.", "Competition listings missing"})
        self.assertGreater(result["output_json"]["total_score"], 0)

    def test_decision_agent_blocks_unverified_evidence(self) -> None:
        agent = DecisionAgent(self.llm)
        result = asyncio.run(
            agent.run(
                {
                    "supplier_summary": {"unit_cost": 4.15, "estimated_landed_cost": 5.70, "international_shipping_estimate": 1.2},
                    "agent_reports": {
                        "risk_agent": {"output_json": {"risk_level": "LOW", "blocked": False}},
                        "market_agent": {
                            "output_json": {
                                "evidence_quality": "MEDIUM",
                                "sold_listing_count": 5,
                                "verified_sold_listing_count": 0,
                                "active_listing_count": 12,
                                "verified_active_listing_count": 0,
                                "verified_evidence_count": 0,
                                "unverified_evidence_count": 12,
                                "test_data_evidence_count": 0,
                                "verification_coverage": 0.0,
                                "insufficient_data": True,
                                "market_price_missing": True,
                                "required_next_evidence": ["Verify evidence before sample buying."],
                            }
                        },
                        "profit_agent": {"output_json": {"estimated_net_profit": 7.42, "scenarios": [{"net_profit": 7.42, "margin_percent": 31.0}]}},
                        "competition_agent": {"output_json": {"competition_level": "LOW", "listing_gap_score": 72, "can_compete": True, "competitor_count": 3, "verified_competitor_count": 3}},
                    }
                }
            )
        )

        output = result["output_json"]
        self.assertEqual(output["buy_readiness_status"], "NOT_READY")
        self.assertEqual(output["research_verdict"], "NEEDS_MORE_RESEARCH")
        self.assertIn("Evidence is not verified.", output["hard_blockers"])
        self.assertEqual(output["main_blocker"], "Evidence is not verified.")

    def test_decision_agent_blocks_unverified_supplier_cost(self) -> None:
        agent = DecisionAgent(self.llm)
        result = asyncio.run(
            agent.run(
                {
                    "supplier_summary": {"unit_cost": 4.15, "estimated_landed_cost": 5.70, "international_shipping_estimate": 1.2, "verification_status": "API_IMPORTED"},
                    "agent_reports": {
                        "risk_agent": {"output_json": {"risk_level": "LOW", "blocked": False}},
                        "market_agent": {
                            "output_json": {
                                "evidence_quality": "HIGH",
                                "sold_listing_count": 5,
                                "verified_sold_listing_count": 5,
                                "active_listing_count": 5,
                                "verified_active_listing_count": 5,
                                "verified_evidence_count": 10,
                                "unverified_evidence_count": 0,
                                "test_data_evidence_count": 0,
                                "verification_coverage": 1.0,
                                "insufficient_data": False,
                                "market_price_missing": False,
                                "median_sold_price": 18.99,
                                "median_active_price": 19.99,
                                "required_next_evidence": [],
                            }
                        },
                        "profit_agent": {"output_json": {"estimated_net_profit": 8.0, "scenarios": [{"net_profit": 8.0, "margin_percent": 31.0}], "target_sale_price": 18.99, "minimum_recommended_price": 20.99}},
                        "competition_agent": {"output_json": {"competition_level": "LOW", "listing_gap_score": 72, "can_compete": True, "competitor_count": 3, "verified_competitor_count": 3}},
                    }
                }
            )
        )

        output = result["output_json"]
        self.assertEqual(output["buy_readiness_status"], "NOT_READY")
        self.assertIn("Supplier cost is not verified.", output["hard_blockers"])
        self.assertEqual(output["main_blocker"], "Supplier cost is not verified.")

    def test_decision_agent_requires_verified_competitors(self) -> None:
        agent = DecisionAgent(self.llm)
        result = asyncio.run(
            agent.run(
                {
                    "supplier_summary": {"unit_cost": 4.15, "estimated_landed_cost": 5.70, "international_shipping_estimate": 1.2, "verification_status": "USER_VERIFIED"},
                    "agent_reports": {
                        "risk_agent": {"output_json": {"risk_level": "LOW", "blocked": False}},
                        "market_agent": {
                            "output_json": {
                                "evidence_quality": "HIGH",
                                "sold_listing_count": 5,
                                "verified_sold_listing_count": 5,
                                "active_listing_count": 5,
                                "verified_active_listing_count": 5,
                                "verified_evidence_count": 10,
                                "unverified_evidence_count": 0,
                                "test_data_evidence_count": 0,
                                "verification_coverage": 1.0,
                                "insufficient_data": False,
                                "market_price_missing": False,
                                "median_sold_price": 18.99,
                                "median_active_price": 19.99,
                                "required_next_evidence": [],
                            }
                        },
                        "profit_agent": {"output_json": {"estimated_net_profit": 8.0, "scenarios": [{"net_profit": 8.0, "margin_percent": 31.0}], "target_sale_price": 18.99, "minimum_recommended_price": 20.99}},
                        "competition_agent": {"output_json": {"competition_level": "LOW", "listing_gap_score": 72, "can_compete": True, "competitor_count": 2, "verified_competitor_count": 2}},
                    }
                }
            )
        )

        output = result["output_json"]
        self.assertEqual(output["buy_readiness_status"], "NOT_READY")
        self.assertIn("Verified competitor evidence missing", output["missing_evidence"])
        self.assertIn("Add at least 3 verified competitor listings before buying.", output["required_before_buying"])

    def test_decision_agent_focuses_on_economics_when_gates_are_complete(self) -> None:
        agent = DecisionAgent(self.llm)
        result = asyncio.run(
            agent.run(
                {
                    "supplier_summary": {
                        "unit_cost": 0.82,
                        "estimated_landed_cost": 0.82,
                        "international_shipping_estimate": 0.0,
                        "verification_status": "USER_VERIFIED",
                    },
                    "agent_reports": {
                        "risk_agent": {"output_json": {"risk_level": "MEDIUM", "blocked": False}},
                        "market_agent": {
                            "output_json": {
                                "evidence_quality": "MEDIUM",
                                "sold_listing_count": 5,
                                "verified_sold_listing_count": 5,
                                "active_listing_count": 5,
                                "verified_active_listing_count": 5,
                                "verified_evidence_count": 10,
                                "unverified_evidence_count": 0,
                                "test_data_evidence_count": 0,
                                "verification_coverage": 1.0,
                                "insufficient_data": False,
                                "market_price_missing": False,
                                "median_sold_price": 10.0,
                                "median_active_price": 23.0,
                                "required_next_evidence": [],
                            }
                        },
                        "profit_agent": {
                            "output_json": {
                                "estimated_net_profit": 3.02,
                                "current_net_profit": 3.02,
                                "target_net_profit_threshold": 8.0,
                                "profit_gap_to_buy_sample": 4.98,
                                "current_landed_cost": 20.5,
                                "max_landed_cost_for_target_profit": 15.52,
                                "current_target_sale_price": 28.86,
                                "required_sale_price_for_target_profit": 33.84,
                                "scenarios": [{"net_profit": 0.0, "margin_percent": 0.0}],
                                "target_sale_price": 28.86,
                                "minimum_recommended_price": 9.02,
                            }
                        },
                        "competition_agent": {
                            "output_json": {
                                "competition_level": "LOW",
                                "listing_gap_score": 55,
                                "can_compete": True,
                                "competitor_count": 3,
                                "verified_competitor_count": 3,
                            }
                        },
                    },
                }
            )
        )

        output = result["output_json"]
        self.assertEqual(output["buy_readiness_status"], "ALMOST_READY")
        self.assertEqual(output["main_blocker"], "Verified evidence is complete, but profit is below the sample-buy threshold.")
        self.assertIn("Reduce landed cost to about $15.52 or validate sale prices above $33.84 before sample buying.", output["next_action"])
        self.assertNotIn("Add at least 5 verified sold listings", output["required_before_buying"])
        self.assertNotIn("Add verified active listing evidence for competition checks.", output["required_before_buying"])
        self.assertIn("Reduce landed cost to approximately $15.52 or prove a higher sustainable sale price above $33.84.", output["required_before_buying"])

    def test_decision_agent_does_not_ready_sample_on_keyword_only(self) -> None:
        agent = DecisionAgent(self.llm)
        result = asyncio.run(
            agent.run(
                {
                    "supplier_summary": {"unit_cost": 4.15, "estimated_landed_cost": 5.70, "international_shipping_estimate": 1.2, "verification_status": "USER_VERIFIED"},
                    "agent_reports": {
                        "risk_agent": {"output_json": {"risk_level": "LOW", "blocked": False}},
                        "market_agent": {
                            "output_json": {
                                "evidence_quality": "LOW",
                                "sold_listing_count": 0,
                                "verified_sold_listing_count": 0,
                                "active_listing_count": 0,
                                "verified_active_listing_count": 0,
                                "verified_evidence_count": 0,
                                "unverified_evidence_count": 0,
                                "test_data_evidence_count": 0,
                                "verification_coverage": 0.0,
                                "insufficient_data": True,
                                "market_price_missing": True,
                            }
                        },
                        "demand_agent": {"output_json": {"demand_status": "STRONG", "demand_score": 95, "next_action": "Validate trend stability."}},
                        "profit_agent": {"output_json": {"estimated_net_profit": 0.0, "scenarios": []}},
                        "competition_agent": {"output_json": {"competition_level": "LOW", "listing_gap_score": 0, "can_compete": False, "competitor_count": 0, "verified_competitor_count": 0}},
                    },
                }
            )
        )

        output = result["output_json"]
        self.assertEqual(output["recommendation"], "SKIP")
        self.assertEqual(output["research_verdict"], "WEAK_IDEA")
        self.assertIn("Verified sold listings missing", output["missing_evidence"])

    def test_decision_agent_ignores_unknown_demand_and_trend_for_completeness(self) -> None:
        agent = DecisionAgent(self.llm)
        base_context = {
            "supplier_summary": {
                "unit_cost": 4.15,
                "estimated_landed_cost": 5.70,
                "international_shipping_estimate": 1.2,
                "verification_status": "USER_VERIFIED",
            },
            "agent_reports": {
                "risk_agent": {"output_json": {"risk_level": "LOW", "blocked": False}},
                "market_agent": {
                    "output_json": {
                        "evidence_quality": "HIGH",
                        "sold_listing_count": 5,
                        "verified_sold_listing_count": 5,
                        "active_listing_count": 5,
                        "verified_active_listing_count": 5,
                        "verified_evidence_count": 10,
                        "unverified_evidence_count": 0,
                        "test_data_evidence_count": 0,
                        "verification_coverage": 1.0,
                        "insufficient_data": False,
                        "market_price_missing": False,
                        "median_sold_price": 18.99,
                        "median_active_price": 19.99,
                        "required_next_evidence": [],
                    }
                },
                "profit_agent": {
                    "output_json": {
                        "estimated_net_profit": 8.0,
                        "scenarios": [{"net_profit": 8.0, "margin_percent": 31.0}],
                        "target_sale_price": 18.99,
                        "minimum_recommended_price": 20.99,
                    }
                },
                "competition_agent": {
                    "output_json": {
                        "competition_level": "LOW",
                        "listing_gap_score": 72,
                        "can_compete": True,
                        "competitor_count": 3,
                        "verified_competitor_count": 3,
                    }
                },
            },
        }

        without_validation = asyncio.run(agent.run(base_context))
        with_unknown_validation = asyncio.run(
            agent.run(
                {
                    **base_context,
                    "agent_reports": {
                        **base_context["agent_reports"],
                        "demand_agent": {"output_json": {"demand_status": "UNKNOWN", "demand_score": 0}},
                        "trend_agent": {"output_json": {"trend_status": "UNKNOWN", "trend_stability_score": 0}},
                    },
                }
            )
        )

        self.assertEqual(with_unknown_validation["output_json"]["research_completeness_score"], without_validation["output_json"]["research_completeness_score"])

    def test_research_cockpit_counts_verified_sold_only(self) -> None:
        from types import SimpleNamespace

        from app.routes.research import _build_buy_readiness

        product = SimpleNamespace(status="NEEDS_RESEARCH", target_sale_price=19.99)
        sources = [SimpleNamespace(unit_cost=4.0, estimated_landed_cost=5.0, international_shipping_estimate=1.0)]
        evidence_rows = [
            SimpleNamespace(evidence_type="SOLD_LISTING", verification_status="USER_VERIFIED"),
            SimpleNamespace(evidence_type="SOLD_LISTING", verification_status="API_IMPORTED"),
            SimpleNamespace(evidence_type="ACTIVE_LISTING", verification_status="USER_VERIFIED"),
            SimpleNamespace(evidence_type="ACTIVE_LISTING", verification_status="API_IMPORTED"),
        ]
        profit_rows = [SimpleNamespace()]
        decision_output = {"blocked": False, "hard_blockers": []}

        buy_readiness, missing_evidence, hard_blockers = _build_buy_readiness(product, sources, evidence_rows, profit_rows, decision_output)

        self.assertEqual(buy_readiness["sold_evidence_count"], 2)
        self.assertEqual(buy_readiness["verified_sold_evidence_count"], 1)
        self.assertEqual(buy_readiness["active_evidence_count"], 2)
        self.assertEqual(buy_readiness["verified_active_evidence_count"], 2)
        self.assertNotIn("Sold listings missing", missing_evidence)
        self.assertEqual(hard_blockers, [])

    def test_demand_agent_unknown_without_data(self) -> None:
        agent = DemandAgent(self.llm)
        result = asyncio.run(agent.run({"product": {"name": "Cat tunnel toy", "category": "Pet accessories"}, "demand_research": []}))
        output = result["output_json"]
        self.assertEqual(output["demand_status"], "UNKNOWN")
        self.assertEqual(output["monthly_search_volume"], None)
        self.assertIn("No keyword demand research captured yet.", output["main_demand_blocker"])

    def test_demand_agent_broad_keyword_does_not_overstate_strength(self) -> None:
        agent = DemandAgent(self.llm)
        result = asyncio.run(
            agent.run(
                {
                    "product": {"name": "Cat tunnel toy", "category": "Pet accessories"},
                    "demand_research": [
                        {
                            "keyword": "pet toy",
                            "monthly_search_volume": 50000,
                            "buyer_intent_score": 20,
                            "keyword_specificity_score": 20,
                            "competition_level": "HIGH",
                        }
                    ],
                }
            )
        )
        output = result["output_json"]
        self.assertNotEqual(output["demand_status"], "STRONG")
        self.assertIn(output["demand_status"], {"MODERATE", "WEAK", "UNKNOWN"})

    def test_trend_agent_unknown_without_data(self) -> None:
        agent = TrendAgent(self.llm)
        result = asyncio.run(agent.run({"product": {"name": "Cat tunnel toy", "category": "Pet accessories"}, "trend_research": []}))
        output = result["output_json"]
        self.assertEqual(output["trend_status"], "UNKNOWN")
        self.assertEqual(output["trend_direction"], "UNKNOWN")
        self.assertIn("No trend research captured yet.", output["main_trend_blocker"])

    def test_trend_agent_unknown_seasonality_is_not_evergreen(self) -> None:
        agent = TrendAgent(self.llm)
        result = asyncio.run(
            agent.run(
                {
                    "product": {"name": "Cat tunnel toy", "category": "Pet accessories"},
                    "trend_research": [
                        {
                            "keyword": "cat tunnel toy",
                            "trend_direction": "STABLE",
                            "seasonality_risk": "UNKNOWN",
                            "trend_stability_score": 80,
                            "evergreen_score": 80,
                            "spike_risk_score": 10,
                        }
                    ],
                }
            )
        )
        output = result["output_json"]
        self.assertNotEqual(output["trend_status"], "EVERGREEN")
        self.assertEqual(output["trend_status"], "UNKNOWN")

    def test_validation_checklist_unknown_without_validation_rows(self) -> None:
        from app.services.validation_checklist_service import ValidationChecklistService

        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        try:
            product = Product(sku="RS-VAL-001", name="Cat tunnel toy", category="Pet accessories", status="RESEARCHING")
            session.add(product)
            session.commit()
            checklist = ValidationChecklistService(session).get_checklist(product.id)
            self.assertEqual(checklist["search_demand"]["status"], "UNKNOWN")
            self.assertEqual(checklist["trend_stability"]["status"], "UNKNOWN")
            self.assertEqual(checklist["final_readiness"], "INCOMPLETE")
        finally:
            session.close()
            Base.metadata.drop_all(engine)

    def test_validation_checklist_does_not_promote_on_demand_trend_only(self) -> None:
        from app.services.validation_checklist_service import ValidationChecklistService

        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        try:
            product = Product(sku="RS-VAL-002", name="Cat tunnel toy", category="Pet accessories", status="RESEARCHING")
            session.add(product)
            session.flush()
            session.add(
                AgentReport(
                    product_id=product.id,
                    agent_name="decision_agent",
                    report_type="decision_agent",
                    output_json='{"recommendation":"WATCHLIST","research_verdict":"PROMISING_RESEARCH","buy_readiness_status":"NOT_READY","next_action":"Keep researching economics."}',
                    summary="Decision summary",
                    confidence="MEDIUM",
                )
            )
            session.add(
                AgentReport(
                    product_id=product.id,
                    agent_name="demand_agent",
                    report_type="demand_agent",
                    output_json='{"demand_status":"STRONG","demand_score":95,"next_action":"Validate trend stability."}',
                    summary="Demand summary",
                    confidence="HIGH",
                )
            )
            session.add(
                AgentReport(
                    product_id=product.id,
                    agent_name="trend_agent",
                    report_type="trend_agent",
                    output_json='{"trend_status":"EVERGREEN","trend_stability_score":90,"next_action":"Keep researching economics."}',
                    summary="Trend summary",
                    confidence="HIGH",
                )
            )
            session.commit()

            checklist = ValidationChecklistService(session).get_checklist(product.id)
            self.assertNotEqual(checklist["final_readiness"], "READY_FOR_SAMPLE")
            self.assertIn(checklist["final_readiness"], {"INCOMPLETE", "WEAK", "WATCHLIST"})
        finally:
            session.close()
            Base.metadata.drop_all(engine)

    def test_validation_checklist_uses_latest_agent_reports(self) -> None:
        from app.services.validation_checklist_service import ValidationChecklistService

        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        try:
            product = Product(sku="RS-VAL-003", name="Reusable pet hair remover roller", category="Pet accessories", status="RESEARCHING")
            session.add(product)
            session.flush()
            session.add(
                AgentReport(
                    product_id=product.id,
                    agent_name="market_agent",
                    report_type="market_agent",
                    output_json='{"sold_listing_count":5,"verified_sold_listing_count":1,"active_listing_count":5,"verified_active_listing_count":0,"test_data_evidence_count":0,"verification_coverage":0.1,"insufficient_data":true,"market_price_missing":false,"evidence_quality":"LOW"}',
                    summary="Old market snapshot",
                    confidence="LOW",
                )
            )
            session.add(
                AgentReport(
                    product_id=product.id,
                    agent_name="market_agent",
                    report_type="market_agent",
                    output_json='{"sold_listing_count":5,"verified_sold_listing_count":5,"active_listing_count":5,"verified_active_listing_count":5,"test_data_evidence_count":0,"verification_coverage":1.0,"insufficient_data":false,"market_price_missing":false,"evidence_quality":"MEDIUM"}',
                    summary="Latest market snapshot",
                    confidence="MEDIUM",
                )
            )
            session.add(
                ProductSource(
                    product_id=product.id,
                    supplier_name="Supplier A",
                    supplier_platform="Alibaba",
                    unit_cost=0.82,
                    estimated_landed_cost=0.82,
                    is_primary=True,
                    verification_status="USER_VERIFIED",
                )
            )
            session.commit()

            checklist = ValidationChecklistService(session).get_checklist(product.id)
            self.assertEqual(checklist["sold_demand"]["status"], "PASS")
            self.assertEqual(checklist["sold_demand"]["summary"], "5 verified sold listings.")
            self.assertEqual(checklist["market_presence"]["status"], "WARNING")
        finally:
            session.close()
            Base.metadata.drop_all(engine)

    def test_agent_service_get_reports_returns_newest_first(self) -> None:
        from app.services.agent_service import AgentService

        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        try:
            product = Product(sku="RS-REP-001", name="Report ordering test", category="Pet accessories", status="RESEARCHING")
            session.add(product)
            session.flush()
            first = AgentReport(
                product_id=product.id,
                agent_name="market_agent",
                report_type="market_agent",
                output_json='{"verified_sold_listing_count":1}',
                summary="Old report",
                confidence="LOW",
            )
            second = AgentReport(
                product_id=product.id,
                agent_name="market_agent",
                report_type="market_agent",
                output_json='{"verified_sold_listing_count":5}',
                summary="New report",
                confidence="HIGH",
            )
            session.add_all([first, second])
            session.commit()

            reports = AgentService(session).get_reports(product.id)
            self.assertGreaterEqual(len(reports), 2)
            self.assertEqual(reports[0].summary, "New report")
            self.assertEqual(reports[1].summary, "Old report")
        finally:
            session.close()
            Base.metadata.drop_all(engine)

    def test_profit_agent_returns_profit_gap_fields(self) -> None:
        agent = ProfitAgent(self.llm)
        result = asyncio.run(
            agent.run(
                {
                    "profit_input": {
                        "expected_sale_price": 28.86,
                        "product_cost": 14.25,
                        "china_domestic_shipping": 0.75,
                        "international_shipping": 3.1,
                        "duties": 0,
                        "inspection_cost": 0,
                        "platform_fee_percent": 0.13,
                        "platform_fee_fixed": 0,
                        "payment_fee": 0,
                        "outbound_shipping": 4.0,
                        "packaging": 0.4,
                        "return_allowance": 0.5,
                        "ad_cost": 0,
                        "buyer_paid_shipping": False,
                        "bundle_quantity": 2,
                    }
                }
            )
        )

        output = result["output_json"]
        self.assertIn("current_net_profit", output)
        self.assertIn("target_net_profit_threshold", output)
        self.assertIn("profit_gap_to_buy_sample", output)
        self.assertIn("current_landed_cost", output)
        self.assertIn("max_landed_cost_for_target_profit", output)
        self.assertIn("required_sale_price_for_target_profit", output)
        self.assertIn("landed_cost_ratio", output)
        self.assertIn("landed_cost_ratio_status", output)
        self.assertIn("gross_margin_percent", output)
        self.assertIn("gross_margin_status", output)
        self.assertAlmostEqual(
            output["profit_gap_to_buy_sample"],
            round(max(0.0, float(output["target_net_profit_threshold"]) - float(output["current_net_profit"])), 2),
        )
        self.assertGreaterEqual(float(output["required_sale_price_for_target_profit"]), float(output["current_target_sale_price"]))

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
        self.assertFalse(result["output_json"]["best_scenario"].lower().endswith("bundle"))

    def test_market_agent_uses_evidence_rows(self) -> None:
        agent = MarketAgent(self.llm)
        result = asyncio.run(
            agent.run(
                {
                    "product": {"name": "Test product"},
                    "marketplace_evidence": [
                        {"marketplace": "eBay", "evidence_type": "SOLD_LISTING", "price": 10.0, "shipping_price": 2.0, "verification_status": "USER_VERIFIED"},
                        {"marketplace": "eBay", "evidence_type": "SOLD_LISTING", "price": 12.0, "shipping_price": 2.5, "verification_status": "USER_VERIFIED"},
                        {"marketplace": "eBay", "evidence_type": "SOLD_LISTING", "price": 14.0, "shipping_price": 3.0, "verification_status": "USER_VERIFIED"},
                        {"marketplace": "eBay", "evidence_type": "SOLD_LISTING", "price": 16.0, "shipping_price": 3.0, "verification_status": "USER_VERIFIED"},
                        {"marketplace": "eBay", "evidence_type": "SOLD_LISTING", "price": 18.0, "shipping_price": 3.5, "verification_status": "USER_VERIFIED"},
                        {"marketplace": "eBay", "evidence_type": "ACTIVE_LISTING", "price": 19.0, "shipping_price": 4.0, "verification_status": "API_IMPORTED"},
                        {"marketplace": "eBay", "evidence_type": "ACTIVE_LISTING", "price": 20.0, "shipping_price": 4.0, "verification_status": "API_IMPORTED"},
                    ],
                }
            )
        )

        output = result["output_json"]
        self.assertEqual(output["sold_listing_count"], 5)
        self.assertEqual(output["verified_sold_listing_count"], 5)
        self.assertEqual(output["active_listing_count"], 2)
        self.assertEqual(output["verified_active_listing_count"], 2)
        self.assertEqual(output["median_sold_price"], 14.0)
        self.assertIn("research_completeness_score", output)
        self.assertIn("demand_evidence_quality", output)
        self.assertIn("market_presence_quality", output)
        self.assertFalse(output["insufficient_data"])

    def test_market_agent_ignores_unverified_rows_for_price_signals(self) -> None:
        agent = MarketAgent(self.llm)
        result = asyncio.run(
            agent.run(
                {
                    "product": {"name": "Test product"},
                    "marketplace_evidence": [
                        {"marketplace": "eBay", "evidence_type": "SOLD_LISTING", "price": 100.0, "shipping_price": 10.0, "verification_status": "USER_CAPTURED_UNVERIFIED"},
                        {"marketplace": "eBay", "evidence_type": "SOLD_LISTING", "price": 110.0, "shipping_price": 11.0, "verification_status": "TEST_DATA"},
                        {"marketplace": "eBay", "evidence_type": "ACTIVE_LISTING", "price": 120.0, "shipping_price": 12.0, "verification_status": "USER_CAPTURED_UNVERIFIED"},
                    ],
                }
            )
        )

        output = result["output_json"]
        self.assertEqual(output["sold_listing_count"], 2)
        self.assertEqual(output["verified_sold_listing_count"], 0)
        self.assertEqual(output["verified_active_listing_count"], 0)
        self.assertIsNone(output["median_sold_price"])
        self.assertIsNone(output["median_active_price"])
        self.assertEqual(output["sold_price_range"], [])
        self.assertEqual(output["active_price_range"], [])
        self.assertEqual(output["sold_price_range_total"], [100.0, 110.0])
        self.assertEqual(output["active_price_range_total"], [120.0, 120.0])
        self.assertTrue(output["insufficient_data"])

    def test_market_agent_does_not_treat_api_imported_sold_as_verified_demand(self) -> None:
        agent = MarketAgent(self.llm)
        result = asyncio.run(
            agent.run(
                {
                    "product": {"name": "Test product"},
                    "marketplace_evidence": [
                        {"marketplace": "Google Shopping", "evidence_type": "SOLD_LISTING", "price": 19.0, "shipping_price": 4.0, "verification_status": "API_IMPORTED"},
                        {"marketplace": "eBay", "evidence_type": "ACTIVE_LISTING", "price": 21.0, "shipping_price": 4.0, "verification_status": "API_IMPORTED"},
                    ],
                }
            )
        )

        output = result["output_json"]
        self.assertEqual(output["sold_listing_count"], 1)
        self.assertEqual(output["verified_sold_listing_count"], 0)
        self.assertEqual(output["verified_active_listing_count"], 1)
        self.assertIsNone(output["median_sold_price"])
        self.assertIsNotNone(output["median_active_price"])

    def test_competition_agent_reads_competitor_listings(self) -> None:
        agent = CompetitionAgent(self.llm)
        result = asyncio.run(
            agent.run(
                {
                    "product": {"name": "Car seat gap organizer", "category": "Automotive"},
                    "market_summary": {"median_sold_price": 18.99},
                    "competitor_listings": [
                        {"price": 19.99, "sold": False, "photo_score": 45, "title_score": 55, "description_score": 50, "verification_status": "USER_VERIFIED"},
                        {"price": 18.49, "sold": True, "photo_score": 52, "title_score": 58, "description_score": 40, "verification_status": "USER_VERIFIED"},
                        {"price": 17.99, "sold": False, "photo_score": 48, "title_score": 60, "description_score": 45, "verification_status": "API_IMPORTED"},
                    ],
                }
            )
        )

        output = result["output_json"]
        self.assertIn(output["competition_level"], {"LOW", "MEDIUM", "HIGH", "UNKNOWN"})
        self.assertGreater(output["listing_gap_score"], 0)
        self.assertEqual(output["verified_competitor_count"], 3)
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

    def test_opportunity_board_uses_saved_evidence_and_reports(self) -> None:
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        try:
            product = Product(
                sku="RS-TEST-001",
                name="Car seat gap organizer",
                category="Automotive",
                status="RESEARCHING",
                risk_level="LOW",
                final_decision="WATCHLIST",
            )
            session.add(product)
            session.flush()

            session.add(
                ProductSource(
                    product_id=product.id,
                    supplier_name="Supplier A",
                    supplier_platform="Alibaba",
                    estimated_landed_cost=5.70,
                    unit_cost=4.15,
                    domestic_shipping=0.35,
                    international_shipping_estimate=1.20,
                    supplier_rating="A",
                    is_primary=True,
                )
            )
            session.add_all(
                [
                    MarketplaceEvidence(product_id=product.id, marketplace="eBay", evidence_type="SOLD_LISTING", price=10.0, shipping_price=2.0, verification_status="USER_VERIFIED"),
                    MarketplaceEvidence(product_id=product.id, marketplace="eBay", evidence_type="SOLD_LISTING", price=12.0, shipping_price=2.5, verification_status="USER_VERIFIED"),
                    MarketplaceEvidence(product_id=product.id, marketplace="eBay", evidence_type="SOLD_LISTING", price=14.0, shipping_price=3.0, verification_status="USER_VERIFIED"),
                    MarketplaceEvidence(product_id=product.id, marketplace="eBay", evidence_type="SOLD_LISTING", price=16.0, shipping_price=3.0, verification_status="USER_VERIFIED"),
                    MarketplaceEvidence(product_id=product.id, marketplace="eBay", evidence_type="SOLD_LISTING", price=18.0, shipping_price=3.5, verification_status="USER_VERIFIED"),
                    MarketplaceEvidence(product_id=product.id, marketplace="eBay", evidence_type="ACTIVE_LISTING", price=19.0, shipping_price=4.0, verification_status="USER_VERIFIED"),
                    MarketplaceEvidence(product_id=product.id, marketplace="eBay", evidence_type="ACTIVE_LISTING", price=20.0, shipping_price=4.0, verification_status="API_IMPORTED"),
                ]
            )
            session.add_all(
                [
                    CompetitorListing(
                        product_id=product.id,
                        marketplace="eBay",
                        price=19.99,
                        sold=False,
                        photo_score=45,
                        title_score=55,
                        description_score=50,
                    ),
                    CompetitorListing(
                        product_id=product.id,
                        marketplace="eBay",
                        price=18.49,
                        sold=True,
                        photo_score=52,
                        title_score=58,
                        description_score=40,
                    ),
                ]
            )
            session.add_all(
                [
                    AgentReport(
                        product_id=product.id,
                        agent_name="decision_agent",
                        report_type="decision_agent",
                        output_json='{"research_verdict":"PROMISING_RESEARCH","buy_readiness_status":"NOT_READY","next_action":"Add 5 sold listings"}',
                        summary="Decision summary",
                        confidence="HIGH",
                    ),
                    AgentReport(
                        product_id=product.id,
                        agent_name="competition_agent",
                        report_type="competition_agent",
                        output_json='{"listing_gap_score":84,"recommended_angle":"Real photos"}',
                        summary="Competition summary",
                        confidence="HIGH",
                    ),
                ]
            )
            session.flush()
            session.add_all(
                [
                    ProfitAnalysis(
                        product_id=product.id,
                        scenario_name="eBay buyer-paid shipping",
                        estimated_net_profit=7.42,
                    ),
                    ProfitAnalysis(
                        product_id=product.id,
                        scenario_name="eBay free shipping",
                        estimated_net_profit=3.10,
                    ),
                ]
            )
            session.commit()

            board = DiscoveryService(session).opportunity_board()
            product_row = next(row for row in board if row["entity_type"] == "product")

            self.assertEqual(product_row["sold_evidence_count"], 5)
            self.assertEqual(product_row["active_evidence_count"], 2)
            self.assertEqual(product_row["sold_evidence_count_verified"], 5)
            self.assertEqual(product_row["active_evidence_count_verified"], 2)
            self.assertEqual(product_row["test_data_count"], 0)
            self.assertEqual(product_row["median_sold_price"], 14.0)
            self.assertEqual(product_row["median_active_price"], 19.5)
            self.assertEqual(product_row["median_shipping"], 3.0)
            self.assertEqual(product_row["best_landed_cost"], 5.7)
            self.assertEqual(product_row["competition_gap_score"], 84)
            self.assertEqual(product_row["best_profit_scenario"], "eBay buyer-paid shipping")
            self.assertEqual(product_row["next_action"], "Add 5 sold listings")
        finally:
            session.close()

    def test_opportunity_board_test_data_ignored_for_verified_medians(self) -> None:
        """TEST_DATA sold rows must not affect board median_sold_price."""
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        try:
            product = Product(sku="RS-TEST-VB1", name="Verified board test", category="Test", status="RESEARCHING")
            session.add(product)
            session.flush()

            # 3 TEST_DATA sold listings (should NOT count)
            session.add_all(
                [
                    MarketplaceEvidence(product_id=product.id, marketplace="eBay", evidence_type="SOLD_LISTING", price=5.0, verification_status="TEST_DATA"),
                    MarketplaceEvidence(product_id=product.id, marketplace="eBay", evidence_type="SOLD_LISTING", price=6.0, verification_status="TEST_DATA"),
                    MarketplaceEvidence(product_id=product.id, marketplace="eBay", evidence_type="SOLD_LISTING", price=7.0, verification_status="TEST_DATA"),
                ]
            )
            # 1 USER_VERIFIED sold listing (should count)
            session.add(MarketplaceEvidence(product_id=product.id, marketplace="eBay", evidence_type="SOLD_LISTING", price=20.0, verification_status="USER_VERIFIED"))
            session.commit()

            board = DiscoveryService(session).opportunity_board()
            row = next(r for r in board if r["entity_type"] == "product")

            self.assertEqual(row["sold_evidence_count"], 4)
            self.assertEqual(row["sold_evidence_count_verified"], 1)
            self.assertEqual(row["test_data_count"], 3)
            # Verified median should be 20.0 (only verified sold)
            self.assertEqual(row["median_sold_price"], 20.0)
            # Total median should be 5.5 (all sold including test data)
            self.assertAlmostEqual(row["median_sold_price_total"], 6.5, places=1)
        finally:
            session.close()

    def test_opportunity_board_unverified_sold_not_counted(self) -> None:
        """USER_CAPTURED_UNVERIFIED sold rows must not affect board median_sold_price."""
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        try:
            product = Product(sku="RS-TEST-VB2", name="Unverified board test", category="Test", status="RESEARCHING")
            session.add(product)
            session.flush()

            session.add_all(
                [
                    MarketplaceEvidence(product_id=product.id, marketplace="eBay", evidence_type="SOLD_LISTING", price=8.0, verification_status="USER_CAPTURED_UNVERIFIED"),
                    MarketplaceEvidence(product_id=product.id, marketplace="eBay", evidence_type="SOLD_LISTING", price=9.0, verification_status="AI_EXTRACTED_UNVERIFIED"),
                    MarketplaceEvidence(product_id=product.id, marketplace="eBay", evidence_type="SOLD_LISTING", price=15.0, verification_status="USER_VERIFIED"),
                ]
            )
            session.commit()

            board = DiscoveryService(session).opportunity_board()
            row = next(r for r in board if r["entity_type"] == "product")

            self.assertEqual(row["sold_evidence_count"], 3)
            self.assertEqual(row["sold_evidence_count_verified"], 1)
            self.assertEqual(row["unverified_evidence_count"], 2)
            self.assertEqual(row["median_sold_price"], 15.0)
            self.assertAlmostEqual(row["median_sold_price_total"], 9.0, places=1)
        finally:
            session.close()

    def test_opportunity_board_api_imported_sold_not_verified(self) -> None:
        """API_IMPORTED SOLD_LISTING does not count as verified sold."""
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        try:
            product = Product(sku="RS-TEST-VB3", name="API imported sold test", category="Test", status="RESEARCHING")
            session.add(product)
            session.flush()

            session.add(MarketplaceEvidence(product_id=product.id, marketplace="Google Shopping", evidence_type="SOLD_LISTING", price=12.0, verification_status="API_IMPORTED"))
            session.add(MarketplaceEvidence(product_id=product.id, marketplace="Google Shopping", evidence_type="ACTIVE_LISTING", price=15.0, verification_status="API_IMPORTED"))
            session.commit()

            board = DiscoveryService(session).opportunity_board()
            row = next(r for r in board if r["entity_type"] == "product")

            # API_IMPORTED sold is NOT verified sold (verified sold requires USER_VERIFIED)
            self.assertEqual(row["sold_evidence_count_verified"], 0)
            # API_IMPORTED active IS verified active
            self.assertEqual(row["active_evidence_count_verified"], 1)
            self.assertIsNone(row["median_sold_price"])
            self.assertEqual(row["median_active_price"], 15.0)
        finally:
            session.close()

    def test_opportunity_board_api_imported_active_counts(self) -> None:
        """API_IMPORTED ACTIVE_LISTING counts as active market presence."""
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        try:
            product = Product(sku="RS-TEST-VB4", name="API active test", category="Test", status="RESEARCHING")
            session.add(product)
            session.flush()

            session.add_all(
                [
                    MarketplaceEvidence(product_id=product.id, marketplace="Google Shopping", evidence_type="ACTIVE_LISTING", price=10.0, verification_status="API_IMPORTED"),
                    MarketplaceEvidence(product_id=product.id, marketplace="Google Shopping", evidence_type="ACTIVE_LISTING", price=12.0, verification_status="API_IMPORTED"),
                    MarketplaceEvidence(product_id=product.id, marketplace="Google Shopping", evidence_type="ACTIVE_LISTING", price=14.0, verification_status="USER_VERIFIED"),
                ]
            )
            session.commit()

            board = DiscoveryService(session).opportunity_board()
            row = next(r for r in board if r["entity_type"] == "product")

            self.assertEqual(row["active_evidence_count"], 3)
            self.assertEqual(row["active_evidence_count_verified"], 3)  # both API_IMPORTED and USER_VERIFIED
            self.assertEqual(row["median_active_price"], 12.0)
        finally:
            session.close()

    def test_opportunity_board_returns_total_and_verified_separately(self) -> None:
        """Board returns total/debug medians separately from verified medians."""
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        try:
            product = Product(sku="RS-TEST-VB5", name="Separate medians test", category="Test", status="RESEARCHING")
            session.add(product)
            session.flush()

            session.add_all(
                [
                    MarketplaceEvidence(product_id=product.id, marketplace="eBay", evidence_type="SOLD_LISTING", price=5.0, verification_status="TEST_DATA"),
                    MarketplaceEvidence(product_id=product.id, marketplace="eBay", evidence_type="SOLD_LISTING", price=25.0, verification_status="USER_VERIFIED"),
                    MarketplaceEvidence(product_id=product.id, marketplace="eBay", evidence_type="ACTIVE_LISTING", price=8.0, verification_status="TEST_DATA"),
                    MarketplaceEvidence(product_id=product.id, marketplace="eBay", evidence_type="ACTIVE_LISTING", price=30.0, verification_status="USER_VERIFIED"),
                ]
            )
            session.commit()

            board = DiscoveryService(session).opportunity_board()
            row = next(r for r in board if r["entity_type"] == "product")

            # Main board values use verified only
            self.assertEqual(row["median_sold_price"], 25.0)
            self.assertEqual(row["median_active_price"], 30.0)
            # Total medians exist separately
            self.assertEqual(row["median_sold_price_total"], 15.0)
            self.assertEqual(row["median_active_price_total"], 19.0)
            # Price ranges also separated
            self.assertEqual(row["sold_price_range"], [25.0])
            self.assertEqual(row["sold_price_range_total"], [5.0, 25.0])
            self.assertEqual(row["active_price_range"], [30.0])
            self.assertEqual(row["active_price_range_total"], [8.0, 30.0])
        finally:
            session.close()

    def test_discovery_task_update_persists_status_and_notes(self) -> None:
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        try:
            idea = ProductIdea(idea_name="Desk cable clips", status="QUICK_SCAN_COMPLETE")
            session.add(idea)
            session.flush()

            task = DiscoveryTask(
                idea_id=idea.id,
                task_type="market_research",
                title="Add 5 sold eBay listings",
                status="TODO",
                sort_order=1,
            )
            session.add(task)
            session.commit()

            updated = DiscoveryService(session).update_task(task.id, ResearchTaskUpdate(status="DONE", notes="Captured 5 sold listings"))
            self.assertIsNotNone(updated)
            self.assertEqual(updated.status, "DONE")
            self.assertEqual(updated.notes, "Captured 5 sold listings")
        finally:
            session.close()


if __name__ == "__main__":
    unittest.main()
