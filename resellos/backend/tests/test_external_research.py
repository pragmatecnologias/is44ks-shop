from __future__ import annotations

import unittest
import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings
from app.db import Base
from app.models.external_research import EvidenceCandidate, ExternalResearchJob
from app.models.product import Product
from app.models.supplier import DiscoveryTask, ProductIdea, MarketplaceEvidence
from app.schemas.external_research_schema import EvidenceCandidateReviewRequest, ExternalResearchRunRequest
from app.services.evidence_candidate_service import EvidenceCandidateService
from app.services.external_research_service import ExternalResearchService
from app.connectors.dataforseo.mappers import map_google_shopping_item_to_candidate


class FakeMerchantClient:
    def __init__(self):
        self.submitted = []

    def submit_google_shopping_products_task(self, *, keyword, location_code, language_code, priority=1, tag=None):
        self.submitted.append(keyword)
        return {
            "tasks": [
                {
                    "id": str(uuid.uuid4()),
                    "status_code": 20100,
                    "status_message": "Task Created.",
                    "data": {
                        "keyword": keyword,
                        "location_code": location_code,
                        "language_code": language_code,
                    },
                }
            ]
        }

    def get_google_shopping_products_result(self, task_id):
        return {
            "tasks": [
                {
                    "id": task_id,
                    "status_code": 20000,
                    "result": [
                        {
                            "items": [
                                {
                                    "type": "google_shopping_serp",
                                    "title": "Car seat gap organizer",
                                    "price": 18.99,
                                    "shopping_url": "https://example.com/item",
                                    "seller": "Example Seller",
                                    "reviews_count": 128,
                                    "product_images": ["https://example.com/image.jpg"],
                                }
                            ]
                        }
                    ],
                }
            ]
        }


class ExternalResearchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()
        self._original_enabled = settings.DATAFORSEO_ENABLED
        settings.DATAFORSEO_ENABLED = True

    def tearDown(self) -> None:
        settings.DATAFORSEO_ENABLED = self._original_enabled
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_google_shopping_mapper_defaults_to_active_listing(self) -> None:
        payload = map_google_shopping_item_to_candidate(
            {
                "type": "google_shopping_serp",
                "title": "Car seat gap organizer",
                "price": 18.99,
                "shopping_url": "https://example.com/item",
                "seller": "Example Seller",
                "reviews_count": 128,
                "product_images": ["https://example.com/image.jpg"],
            },
            source_job={"job_id": "job-1", "query": "car seat gap organizer"},
        )

        self.assertEqual(payload["candidate_type"], "MARKETPLACE_EVIDENCE")
        self.assertEqual(payload["evidence_type"], "ACTIVE_LISTING")
        self.assertEqual(payload["title"], "Car seat gap organizer")
        self.assertEqual(payload["seller"], "Example Seller")

    def test_candidate_approval_creates_marketplace_evidence_and_links_task(self) -> None:
        product = Product(sku="RS-TEST-001", name="Car seat gap organizer", status="RESEARCHING")
        self.session.add(product)
        self.session.flush()

        idea = ProductIdea(
            idea_name="Car seat gap organizer",
            status="PROMOTED_TO_PRODUCT",
            promoted_product_id=product.id,
        )
        self.session.add(idea)
        self.session.flush()

        task = DiscoveryTask(
            idea_id=idea.id,
            task_type="market_research",
            title="Add 5 sold eBay listings",
        )
        self.session.add(task)

        candidate = EvidenceCandidate(
            idea_id=idea.id,
            product_id=product.id,
            source="DATAFORSEO",
            candidate_type="MARKETPLACE_EVIDENCE",
            marketplace="Google Shopping",
            evidence_type="ACTIVE_LISTING",
            title="Car seat gap organizer",
            url="https://example.com/item",
            price=18.99,
            shipping_price=4.99,
            seller="Example Seller",
            confidence="MEDIUM",
            review_status="PENDING",
            raw_json={"title": "Car seat gap organizer"},
        )
        self.session.add(candidate)
        self.session.commit()

        service = EvidenceCandidateService(self.session)
        result = service.approve_candidate(
            candidate.id,
            EvidenceCandidateReviewRequest(
                approve_as="MARKETPLACE_EVIDENCE",
                task_id=task.id,
            ),
        )

        self.assertEqual(result.candidate.review_status, "APPROVED")
        linked_task = self.session.query(DiscoveryTask).filter(DiscoveryTask.id == task.id).first()
        self.assertIsNotNone(linked_task.linked_evidence_id)
        evidence = self.session.query(MarketplaceEvidence).filter(MarketplaceEvidence.product_id == product.id).first()
        self.assertIsNotNone(evidence)
        self.assertEqual(evidence.evidence_type, "ACTIVE_LISTING")

    def test_external_research_service_submits_and_polls_jobs(self) -> None:
        idea = ProductIdea(
            idea_name="Car seat gap organizer",
            category="Car accessories",
            status="IDEA",
        )
        self.session.add(idea)
        self.session.commit()

        service = ExternalResearchService(self.session)
        service._dataforseo_client = FakeMerchantClient()

        run_result = service.run_google_shopping_for_idea(
            ExternalResearchRunRequest(
                idea_id=idea.id,
                queries=["car seat gap organizer"],
                max_results=20,
                queue="standard",
            )
        )

        self.assertEqual(len(run_result.jobs), 1)
        job_id = run_result.jobs[0].id

        polled = service.poll_job(job_id)
        self.assertEqual(polled.status, "IMPORTED")
        candidates = service.list_candidates(job_id=job_id)
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].candidate_type, "MARKETPLACE_EVIDENCE")

