"""Tests for Production Capability Discovery feature."""
from __future__ import annotations

import unittest
import uuid
from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401 - register SQLAlchemy models
from app.db import Base
from app.services.production_service import ProductionService


def utcnow() -> datetime:
    return datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)


class ProductionServiceTests(unittest.TestCase):
    """Test production service CRUD and decision logic via direct service calls."""

    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.session = self.SessionLocal()
        self.service = ProductionService(self.session)

    def tearDown(self) -> None:
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_create_campaign(self) -> None:
        campaign = self.service.create_campaign({"name": "Laser Engraver Campaign"})
        self.assertEqual(campaign.name, "Laser Engraver Campaign")
        self.assertEqual(campaign.status, "DRAFT")

    def test_list_campaigns(self) -> None:
        self.service.create_campaign({"name": "Campaign 1"})
        self.service.create_campaign({"name": "Campaign 2"})
        campaigns = self.service.list_campaigns()
        self.assertEqual(len(campaigns), 2)

    def test_create_machine(self) -> None:
        camp = self.service.create_campaign({"name": "Test"})
        machine = self.service.create_machine(
            {"campaign_id": str(camp.id), "name": "50W Fiber Laser"},
        )
        self.assertEqual(machine.name, "50W Fiber Laser")
        self.assertEqual(machine.status, "SUGGESTED")

    def test_add_evidence(self) -> None:
        camp = self.service.create_campaign({"name": "Test"})
        machine = self.service.create_machine(
            {"campaign_id": camp.id, "name": "Laser"}
        )
        evidence = self.service.create_evidence(
            machine.id,
            {"evidence_type": "NEW_MACHINE_LISTING", "title": "50W Fiber Laser on eBay", "price": 2499},
        )
        self.assertEqual(evidence.evidence_type, "NEW_MACHINE_LISTING")

    def test_verify_evidence(self) -> None:
        camp = self.service.create_campaign({"name": "Test"})
        machine = self.service.create_machine({"campaign_id": camp.id, "name": "Laser"})
        evidence = self.service.create_evidence(
            machine.id,
            {"evidence_type": "NEW_MACHINE_LISTING", "title": "Test listing"},
        )
        result = self.service.verify_evidence(evidence.id, "USER_VERIFIED")
        self.assertIsNotNone(result)
        self.assertEqual(result.verification_status, "USER_VERIFIED")

    def test_add_product_family(self) -> None:
        camp = self.service.create_campaign({"name": "Test"})
        machine = self.service.create_machine({"campaign_id": camp.id, "name": "Laser"})
        family = self.service.create_product_family(
            machine.id, {"name": "Custom Phone Cases"}
        )
        self.assertEqual(family.name, "Custom Phone Cases")

    def test_add_cost_scenario_computes_derived_fields(self) -> None:
        camp = self.service.create_campaign({"name": "Test"})
        machine = self.service.create_machine({"campaign_id": camp.id, "name": "Laser"})
        family = self.service.create_product_family(machine.id, {"name": "Phone Cases"})
        scenario = self.service.create_cost_scenario(
            family.id,
            {
                "scenario_name": "Base Case",
                "material_cost": 4.00,
                "labor_cost": 2.00,
                "sale_price": 29.99,
                "units_per_month": 50,
                "machine_purchase_price": 2500.00,
            },
        )
        self.assertIsNotNone(scenario.total_cost_per_unit)
        self.assertIsNotNone(scenario.net_profit_per_unit)
        self.assertIsNotNone(scenario.margin_percent)
        self.assertIsNotNone(scenario.payback_months)
        self.assertAlmostEqual(float(scenario.total_cost_per_unit), 6.00, places=2)
        self.assertAlmostEqual(float(scenario.net_profit_per_unit), 23.99, places=2)

    def test_add_cost_scenario_uses_provided_values(self) -> None:
        camp = self.service.create_campaign({"name": "Test"})
        machine = self.service.create_machine({"campaign_id": camp.id, "name": "Laser"})
        family = self.service.create_product_family(machine.id, {"name": "Cases"})
        scenario = self.service.create_cost_scenario(
            family.id,
            {
                "scenario_name": "Manual",
                "total_cost_per_unit": 8.00,
                "sale_price": 35.00,
                "net_profit_per_unit": 27.00,
                "margin_percent": 77.14,
                "units_per_month": 40,
                "machine_purchase_price": 3000.00,
                "payback_months": 2.78,
            },
        )
        self.assertEqual(float(scenario.total_cost_per_unit), 8.00)
        self.assertEqual(float(scenario.margin_percent), 77.14)
        self.assertAlmostEqual(float(scenario.payback_months), 2.78, places=1)


class MachineDecisionSafetyTests(unittest.TestCase):
    """Decision safety: BUY_MACHINE blocked without verified evidence."""

    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.session = self.SessionLocal()
        self.service = ProductionService(self.session)

    def tearDown(self) -> None:
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def _full_setup(self, verified_count: int = 0) -> uuid.UUID:
        """Create machine with 2 evidence, family with market evidence, and cost scenario."""
        from app.models.production import (
            ProductionCampaign, MachineCandidate, MachineEvidence,
            MachineProductFamily, ProductionCostScenario,
        )
        campaign = ProductionCampaign(
            id=uuid.uuid4(), name="Test", mode="PRODUCTION",
            status="RUNNING", budget_limit_usd=5000.00,
            created_at=utcnow(), updated_at=utcnow(),
        )
        self.session.add(campaign)
        machine = MachineCandidate(
            id=uuid.uuid4(), campaign_id=campaign.id, name="Laser",
            status="RESEARCHING",
            created_at=utcnow(), updated_at=utcnow(),
        )
        self.session.add(machine)
        self.session.flush()

        for i in range(2):
            self.session.add(MachineEvidence(
                id=uuid.uuid4(), machine_id=machine.id,
                evidence_type="NEW_MACHINE_LISTING", title=f"Listing {i+1}",
                verification_status="USER_VERIFIED" if i < verified_count else "AI_EXTRACTED_UNVERIFIED",
                created_at=utcnow(),
            ))
        self.session.flush()

        family = MachineProductFamily(
            id=uuid.uuid4(), machine_id=machine.id, name="Custom Cases",
            has_market_evidence=True, status="SHORTLISTED",
            created_at=utcnow(), updated_at=utcnow(),
        )
        self.session.add(family)
        self.session.flush()

        self.session.add(ProductionCostScenario(
            id=uuid.uuid4(), machine_id=machine.id, product_family_id=family.id,
            scenario_name="Base", material_cost=4.00, labor_cost=2.00,
            sale_price=29.99, units_per_month=50, machine_purchase_price=2500.00,
            total_cost_per_unit=6.00, net_profit_per_unit=23.99,
            margin_percent=79.99, payback_months=20.83,
            created_at=utcnow(),
        ))
        self.session.commit()
        return machine.id

    def test_buy_machine_blocked_without_verified_evidence(self) -> None:
        """BUY_MACHINE must not be possible with only unverified evidence."""
        machine_id = self._full_setup(verified_count=0)
        decision = self.service.run_machine_decision(machine_id)
        self.assertNotEqual(decision.recommendation, "BUY_MACHINE")
        self.assertIn("No verified evidence", decision.reason)

    def test_buy_machine_allowed_with_verified_evidence(self) -> None:
        """BUY_MACHINE is allowed when at least 1 evidence is USER_VERIFIED."""
        machine_id = self._full_setup(verified_count=1)
        decision = self.service.run_machine_decision(machine_id)
        self.assertEqual(decision.recommendation, "BUY_MACHINE")

    def test_decision_blocked_without_enough_evidence(self) -> None:
        """BUY_MACHINE blocked when fewer than 2 evidence items exist."""
        from app.models.production import ProductionCampaign, MachineCandidate, MachineEvidence
        campaign = ProductionCampaign(
            id=uuid.uuid4(), name="Test", mode="PRODUCTION",
            status="RUNNING", budget_limit_usd=5000,
            created_at=utcnow(), updated_at=utcnow(),
        )
        self.session.add(campaign)
        machine = MachineCandidate(
            id=uuid.uuid4(), campaign_id=campaign.id, name="Test",
            status="RESEARCHING",
            created_at=utcnow(), updated_at=utcnow(),
        )
        self.session.add(machine)
        self.session.flush()
        self.session.add(MachineEvidence(
            id=uuid.uuid4(), machine_id=machine.id,
            evidence_type="NEW_MACHINE_LISTING", title="Only listing",
            verification_status="USER_VERIFIED",
            created_at=utcnow(),
        ))
        self.session.commit()
        decision = self.service.run_machine_decision(machine.id)
        self.assertNotEqual(decision.recommendation, "BUY_MACHINE")


class PromoteProductFamilyTests(unittest.TestCase):
    """Product family promotion creates ProductIdea/Product."""

    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.session = self.SessionLocal()
        self.service = ProductionService(self.session)

    def tearDown(self) -> None:
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_promote_creates_product_idea(self) -> None:
        from app.models.production import ProductionCampaign, MachineCandidate, MachineProductFamily
        campaign = ProductionCampaign(
            id=uuid.uuid4(), name="Test", mode="PRODUCTION",
            status="RUNNING",
            created_at=utcnow(), updated_at=utcnow(),
        )
        self.session.add(campaign)
        machine = MachineCandidate(
            id=uuid.uuid4(), campaign_id=campaign.id, name="Laser",
            status="RESEARCHING",
            created_at=utcnow(), updated_at=utcnow(),
        )
        self.session.add(machine)
        self.session.flush()
        family = MachineProductFamily(
            id=uuid.uuid4(), machine_id=machine.id, name="Custom Cases",
            status="SHORTLISTED", has_market_evidence=False,
            created_at=utcnow(), updated_at=utcnow(),
        )
        self.session.add(family)
        self.session.commit()
        result = self.service.promote_product_family(family.id)
        self.assertIn("idea_id", result)
        self.assertIsNotNone(result["idea_id"])

    def test_promote_with_market_evidence_creates_product(self) -> None:
        from app.models.production import ProductionCampaign, MachineCandidate, MachineProductFamily
        campaign = ProductionCampaign(
            id=uuid.uuid4(), name="Test", mode="PRODUCTION",
            status="RUNNING",
            created_at=utcnow(), updated_at=utcnow(),
        )
        self.session.add(campaign)
        machine = MachineCandidate(
            id=uuid.uuid4(), campaign_id=campaign.id, name="Laser",
            status="RESEARCHING",
            created_at=utcnow(), updated_at=utcnow(),
        )
        self.session.add(machine)
        self.session.flush()
        family = MachineProductFamily(
            id=uuid.uuid4(), machine_id=machine.id, name="Custom Cases",
            status="SHORTLISTED", has_market_evidence=True,
            material_cost_per_unit=4.00, estimated_sale_price=29.99,
            created_at=utcnow(), updated_at=utcnow(),
        )
        self.session.add(family)
        self.session.commit()
        result = self.service.promote_product_family(family.id)
        self.assertIn("idea_id", result)
        self.assertIn("product_id", result)


class OpenAPIRouteExistenceTests(unittest.TestCase):
    """Smoke tests: verify routes exist in OpenAPI spec (no DB needed)."""

    def test_openapi_exposes_production_endpoints(self) -> None:
        from fastapi.testclient import TestClient
        from app.main import app as fastapi_app
        client = TestClient(fastapi_app)
        response = client.get("/openapi.json")
        self.assertEqual(response.status_code, 200)
        paths = response.json()["paths"]
        required = [
            "/api/production/campaigns",
            "/api/production/campaigns/{campaign_id}",
            "/api/production/machines",
            "/api/production/machines/{machine_id}",
            "/api/production/machines/{machine_id}/evidence",
            "/api/production/machines/{machine_id}/product-families",
            "/api/production/product-families/{family_id}/cost-scenarios",
        ]
        for route in required:
            self.assertIn(route, paths, f"{route} not registered")


if __name__ == "__main__":
    unittest.main()