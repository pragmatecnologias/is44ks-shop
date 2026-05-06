from __future__ import annotations

import unittest
import uuid
import asyncio

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401 - register SQLAlchemy models
from app.models.external_research import ExternalResearchJob
from app.db import Base
from app.schemas.campaign_schema import DiscoveryCampaignCreate, DiscoveryCampaignTaskCreate, DiscoveryCampaignTaskUpdate
from app.schemas.validation_schema import ProductDemandResearchCreate, ProductTrendResearchCreate, ProductDemandResearchVerifyRequest, ProductTrendResearchVerifyRequest
from app.schemas.product_schema import ProductIdeaCreate
from app.services.campaign_service import CampaignService
from app.services.capture_service import CaptureService
from app.services.discovery_service import DiscoveryService
from app.services.demand_research_service import DemandResearchService
from app.services.trend_research_service import TrendResearchService


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
        self.assertIn("ideas_with_keyword_demand", report.model_dump())
        self.assertIn("ideas_with_trend_research", report.model_dump())
        self.assertIn("products_with_keyword_demand", report.model_dump())
        self.assertIn("products_with_trend_research", report.model_dump())
        self.assertIn("products_with_evergreen_trend", report.model_dump())
        self.assertIn("products_with_weak_landed_cost_ratio", report.model_dump())
        self.assertIn("next_best_task", report.model_dump())

    def test_campaign_next_best_task_does_not_suggest_promotion_without_evidence(self) -> None:
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
        idea = service.add_idea_to_campaign(
            campaign.id,
            ProductIdeaCreate(
                idea_name="Pet blanket hair remover",
                category="Pet accessories",
                campaign_id=campaign.id,
                source_platform="Manual",
                why_interesting="Reusable pet accessory.",
            ),
        )
        discovery = DiscoveryService(self.session)
        discovery.quick_scan_existing(idea.id)
        report = service.get_report(campaign.id)
        self.assertIn("Collect keyword demand for Pet blanket hair remover before promotion.", report.next_best_task or "")
        self.assertNotIn("promote", (report.next_best_task or "").lower())

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

    def test_manual_capture_inherits_campaign_id_from_task(self) -> None:
        """When capture_manual is called with only task_id, campaign_id is traced via task.idea.campaign_id."""
        service = CampaignService(self.session)
        discovery = DiscoveryService(self.session)
        campaign = service.create_campaign(DiscoveryCampaignCreate(name="Pet accessories discovery"))
        idea = service.add_idea_to_campaign(
            campaign.id,
            ProductIdeaCreate(
                idea_name="Pet grooming brush",
                category="Pet accessories",
                campaign_id=campaign.id,
                source_platform="Manual",
                why_interesting="Pet accessory.",
            ),
        )
        task = service.create_task(
            campaign.id,
            DiscoveryCampaignTaskCreate(
                task_type="SCOUTING",
                title="Scout pet grooming brush",
                description="Research this product.",
                related_idea_id=idea.id,
            ),
        )
        capture = CaptureService(self.session)
        candidate, _ = asyncio.run(
            capture.capture_manual(
                task_id=task.id,
                capture_type="MARKETPLACE_SCREENSHOT",
                pasted_text="Pet grooming brush\nSold price: $12.99",
                notes="Task-linked capture",
            )
        )
        self.assertEqual(candidate.campaign_id, campaign.id)

    def test_manual_capture_inherits_campaign_id_from_product(self) -> None:
        """When capture_manual is called with only product_id, campaign_id is traced via discovery_context AgentReport."""
        service = CampaignService(self.session)
        discovery = DiscoveryService(self.session)
        campaign = service.create_campaign(DiscoveryCampaignCreate(name="Pet accessories discovery", category="Pet accessories"))
        idea = service.add_idea_to_campaign(
            campaign.id,
            ProductIdeaCreate(
                idea_name="Pet hair remover brush",
                category="Pet accessories",
                campaign_id=campaign.id,
                source_platform="Manual",
                why_interesting="Pet accessory.",
            ),
        )
        # Promote idea to product - this creates discovery_context AgentReport
        promoted = discovery.promote_to_product(idea.id)
        self.assertIsNotNone(promoted)
        capture = CaptureService(self.session)
        candidate, _ = asyncio.run(
            capture.capture_manual(
                product_id=promoted.id,
                capture_type="MARKETPLACE_SCREENSHOT",
                pasted_text="Pet hair remover brush\nSold price: $18.99",
                notes="Product-linked capture",
            )
        )
        self.assertEqual(candidate.campaign_id, campaign.id)

    def test_demand_and_trend_research_inherit_campaign_and_require_proof(self) -> None:
        service = CampaignService(self.session)
        campaign = service.create_campaign(DiscoveryCampaignCreate(name="Pet accessories discovery", category="Pet accessories"))
        idea = service.add_idea_to_campaign(
            campaign.id,
            ProductIdeaCreate(
                idea_name="Cat tunnel toy",
                category="Pet accessories",
                campaign_id=campaign.id,
                source_platform="Manual",
                why_interesting="Reusable pet accessory.",
            ),
        )
        task = service.create_task(
            campaign.id,
            DiscoveryCampaignTaskCreate(
                task_type="SCOUTING",
                title="Add validation signals",
                description="Collect keyword demand and trend research.",
                related_idea_id=idea.id,
            ),
        )

        demand_service = DemandResearchService(self.session)
        trend_service = TrendResearchService(self.session)
        demand = demand_service.create_research(
            ProductDemandResearchCreate(
                idea_id=idea.id,
                task_id=task.id,
                keyword="cat tunnel toy",
                monthly_search_volume=1200,
                source="MANUAL_CAPTURE",
            )
        )
        trend = trend_service.create_research(
            ProductTrendResearchCreate(
                idea_id=idea.id,
                task_id=task.id,
                keyword="cat tunnel toy",
                trend_direction="STABLE",
                seasonality_risk="LOW",
                source="MANUAL_CAPTURE",
            )
        )

        self.assertEqual(demand.campaign_id, campaign.id)
        self.assertEqual(trend.campaign_id, campaign.id)
        self.assertEqual(demand.task_id, task.id)
        self.assertEqual(trend.task_id, task.id)

        with self.assertRaises(HTTPException):
            demand_service.verify_research(
                demand.id,
                ProductDemandResearchVerifyRequest(verification_status="USER_VERIFIED"),
            )

        with self.assertRaises(HTTPException):
            trend_service.verify_research(
                trend.id,
                ProductTrendResearchVerifyRequest(verification_status="USER_VERIFIED"),
            )

    def test_quick_scan_existing_idea_updates_same_record(self) -> None:
        service = CampaignService(self.session)
        discovery = DiscoveryService(self.session)
        campaign = service.create_campaign(DiscoveryCampaignCreate(name="Pet accessories discovery", category="Pet accessories"))
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
        self.assertEqual(self.session.query(type(idea)).count(), 1)
        result = discovery.quick_scan_existing(idea.id)
        self.assertEqual(result["idea"]["id"], str(idea.id))
        self.assertEqual(self.session.query(type(idea)).count(), 1)
        scanned = discovery.get_idea(idea.id)
        self.assertIsNotNone(scanned)
        self.assertIsNotNone(scanned.quick_scan_verdict)
        self.assertEqual(scanned.campaign_id, campaign.id)
        self.assertGreaterEqual(len(result["tasks"]), 1)

    def test_campaign_report_includes_pending_external_jobs_count(self) -> None:
        """Campaign report includes pending_external_jobs_count."""
        service = CampaignService(self.session)
        campaign = service.create_campaign(DiscoveryCampaignCreate(name="Job visibility test", category="Test"))
        self.session.add(ExternalResearchJob(
            campaign_id=campaign.id,
            provider="DATAFORSEO",
            api_area="google_shopping",
            query="pet grooming glove",
            queue="standard",
            status="QUEUED",
            cost_estimate=0.05,
        ))
        self.session.commit()

        report = service.get_report(campaign.id)
        self.assertEqual(report.external_jobs_total, 1)
        self.assertEqual(report.external_jobs_pending_count, 1)
        self.assertEqual(report.external_jobs_imported_count, 0)
        self.assertEqual(report.external_jobs_failed_count, 0)

    def test_campaign_report_includes_latest_pending_job_id(self) -> None:
        """Campaign report includes latest_pending_job_id."""
        service = CampaignService(self.session)
        campaign = service.create_campaign(DiscoveryCampaignCreate(name="Pending job id test", category="Test"))
        job = ExternalResearchJob(
            campaign_id=campaign.id,
            provider="DATAFORSEO",
            api_area="google_shopping",
            query="pet bowl",
            queue="standard",
            status="SUBMITTED",
            cost_estimate=0.05,
        )
        self.session.add(job)
        self.session.flush()

        report = service.get_report(campaign.id)
        self.assertEqual(report.latest_pending_job_id, str(job.id))
        self.assertEqual(report.latest_pending_job_query, "pet bowl")
        self.assertEqual(report.latest_pending_job_status, "SUBMITTED")

    def test_campaign_report_imported_zero_result_task_in_queue_is_pending(self) -> None:
        """IMPORTED job with zero results and 'Task In Queue' raw response is treated as pending."""
        service = CampaignService(self.session)
        campaign = service.create_campaign(DiscoveryCampaignCreate(name="Imported pending test", category="Test"))
        self.session.add(ExternalResearchJob(
            campaign_id=campaign.id,
            provider="DATAFORSEO",
            api_area="google_shopping",
            query="pet blanket",
            queue="standard",
            status="IMPORTED",
            result_count=0,
            cost_estimate=0.05,
            raw_response={
                "tasks": [{"id": "abc123", "status_message": "Task In Queue.", "result_count": 0}],
            },
        ))
        self.session.commit()

        report = service.get_report(campaign.id)
        self.assertEqual(report.external_jobs_total, 1)
        self.assertEqual(report.external_jobs_pending_count, 1)
        self.assertEqual(report.external_jobs_imported_count, 0)
        self.assertEqual(report.external_jobs_failed_count, 0)
        self.assertIsNotNone(report.external_research_next_action)
        self.assertIn("Poll external research job", report.external_research_next_action)

    def test_campaign_report_next_action_says_poll_when_queued(self) -> None:
        """Campaign report next action says to poll when job is queued."""
        service = CampaignService(self.session)
        campaign = service.create_campaign(DiscoveryCampaignCreate(name="Poll action test", category="Test"))
        self.session.add(ExternalResearchJob(
            campaign_id=campaign.id,
            provider="DATAFORSEO",
            api_area="google_shopping",
            query="pet toy",
            queue="standard",
            status="QUEUED",
            cost_estimate=0.05,
        ))
        self.session.commit()

        report = service.get_report(campaign.id)
        self.assertIsNotNone(report.external_research_next_action)
        self.assertIn("Poll", report.external_research_next_action)

    def test_campaign_report_zero_candidates_queued_not_failure(self) -> None:
        """Zero candidates with queued provider status is not treated as failure."""
        service = CampaignService(self.session)
        campaign = service.create_campaign(DiscoveryCampaignCreate(name="Zero candidates test", category="Test"))
        self.session.add(ExternalResearchJob(
            campaign_id=campaign.id,
            provider="DATAFORSEO",
            api_area="google_shopping",
            query="pet leash",
            queue="standard",
            status="QUEUED",
            result_count=0,
            cost_estimate=0.05,
        ))
        self.session.commit()

        report = service.get_report(campaign.id)
        self.assertEqual(report.external_jobs_pending_count, 1)
        self.assertEqual(report.external_jobs_failed_count, 0)
        # The report should suggest polling, not report failure
        self.assertIsNotNone(report.external_research_next_action)


if __name__ == "__main__":
    unittest.main()
