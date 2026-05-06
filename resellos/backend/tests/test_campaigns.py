from __future__ import annotations

import unittest
import uuid
import asyncio

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401 - register SQLAlchemy models
from app.db import Base
from app.schemas.campaign_schema import DiscoveryCampaignCreate, DiscoveryCampaignTaskCreate, DiscoveryCampaignTaskUpdate
from app.schemas.product_schema import ProductIdeaCreate
from app.services.campaign_service import CampaignService
from app.services.capture_service import CaptureService
from app.services.discovery_service import DiscoveryService


class CampaignServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.session = self.SessionLocal()

    def tearDown(self) -> None:
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_create_campaign_add_idea_task_and_report(self) -> None:
        service = CampaignService(self.session)
        campaign = service.create_campaign(
            DiscoveryCampaignCreate(
                name="Pet accessories discovery",
                category="Pet accessories",
                goal="Find safe low-cost pet accessory ideas.",
                constraints_json={"avoid": ["medicine", "supplements"]},
                budget_limit_usd=25.0,
                max_ideas=10,
                max_products_to_promote=3,
                created_by="codex",
            )
        )

        idea = service.add_idea_to_campaign(
            campaign.id,
            ProductIdeaCreate(
                idea_name="Reusable pet hair remover roller",
                category="Pet accessories",
                campaign_id=campaign.id,
                source_platform="Manual",
                why_interesting="Reusable pet accessory.",
            ),
        )
        self.assertEqual(idea.campaign_id, campaign.id)

        task = service.create_task(
            campaign.id,
            DiscoveryCampaignTaskCreate(
                task_type="SCOUTING",
                title="Create first discovery ideas",
                description="Add initial ideas to the campaign.",
                related_idea_id=idea.id,
            ),
        )
        updated_task = service.update_task(
            campaign.id,
            task.id,
            DiscoveryCampaignTaskUpdate(status="DONE", error_message=None),
        )
        self.assertIsNotNone(updated_task)
        self.assertEqual(updated_task.status, "DONE")

        report = service.get_report(campaign.id)
        self.assertEqual(report.total_ideas, 1)
        self.assertEqual(report.promoted_products, 0)
        self.assertEqual(report.top_ranked_ideas[0].idea_name, "Reusable pet hair remover roller")

    def test_complete_campaign_requires_report(self) -> None:
        service = CampaignService(self.session)
        campaign = service.create_campaign(DiscoveryCampaignCreate(name="Test campaign"))

        with self.assertRaises(HTTPException) as ctx:
            service.update_campaign(campaign.id, {"status": "COMPLETED"})

        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("report exists", ctx.exception.detail)

    def test_generate_next_tasks_creates_campaign_tasks(self) -> None:
        service = CampaignService(self.session)
        campaign = service.create_campaign(
            DiscoveryCampaignCreate(
                name="Pet accessories discovery",
                category="Pet accessories",
                budget_limit_usd=10.0,
                max_ideas=5,
                max_products_to_promote=2,
            )
        )
        tasks = service.generate_next_tasks(campaign.id)
        self.assertGreaterEqual(len(tasks), 1)
        self.assertEqual(tasks[0].campaign_id, campaign.id)

    def test_campaign_report_includes_budget_and_decision_breakdowns(self) -> None:
        service = CampaignService(self.session)
        campaign = service.create_campaign(
            DiscoveryCampaignCreate(
                name="Pet accessories discovery",
                category="Pet accessories",
                budget_limit_usd=10.0,
                max_ideas=5,
                max_products_to_promote=2,
            )
        )
        report = service.get_report(campaign.id)
        self.assertIn("spend_remaining", report.model_dump())
        self.assertIn("ideas_by_verdict", report.model_dump())
        self.assertIn("products_by_decision", report.model_dump())
        self.assertIn("candidate_count_by_status", report.model_dump())
        self.assertIn("next_best_task", report.model_dump())

    def test_campaign_promotion_limit_blocks_extra_product(self) -> None:
        discovery = DiscoveryService(self.session)
        campaign_service = CampaignService(self.session)
        campaign = campaign_service.create_campaign(
            DiscoveryCampaignCreate(
                name="Pet accessories discovery",
                category="Pet accessories",
                budget_limit_usd=10.0,
                max_ideas=2,
                max_products_to_promote=1,
            )
        )
        idea_one = campaign_service.add_idea_to_campaign(
            campaign.id,
            ProductIdeaCreate(
                idea_name="Reusable pet hair remover roller",
                category="Pet accessories",
                campaign_id=campaign.id,
                source_platform="Manual",
                why_interesting="Reusable pet accessory.",
            ),
        )
        idea_two = campaign_service.add_idea_to_campaign(
            campaign.id,
            ProductIdeaCreate(
                idea_name="Pet grooming glove",
                category="Pet accessories",
                campaign_id=campaign.id,
                source_platform="Manual",
                why_interesting="Pet accessory.",
            ),
        )
        promoted = discovery.promote_to_product(idea_one.id)
        self.assertIsNotNone(promoted)
        with self.assertRaises(HTTPException) as ctx:
            discovery.promote_to_product(idea_two.id)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("promoted product limit", ctx.exception.detail)

    def test_manual_capture_inherits_campaign_id_from_idea(self) -> None:
        service = CampaignService(self.session)
        campaign = service.create_campaign(DiscoveryCampaignCreate(name="Pet accessories discovery"))
        idea = service.add_idea_to_campaign(
            campaign.id,
            ProductIdeaCreate(
                idea_name="Reusable pet hair remover roller",
                category="Pet accessories",
                campaign_id=campaign.id,
                source_platform="Manual",
                why_interesting="Reusable pet accessory.",
            ),
        )
        capture = CaptureService(self.session)
        candidate, _ = asyncio.run(
            capture.capture_manual(
                idea_id=idea.id,
                capture_type="MARKETPLACE_SCREENSHOT",
                pasted_text="Reusable pet hair remover roller\nSold price: $14.99",
                notes="Manual test capture",
            )
        )
        self.assertEqual(candidate.campaign_id, campaign.id)


if __name__ == "__main__":
    unittest.main()
