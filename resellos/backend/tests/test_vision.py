from __future__ import annotations

import asyncio
import tempfile
import unittest
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401 - ensure SQLAlchemy models register
from app.db import Base
from app.vision.base import VisionProvider
from app.vision.vision_service import VisionAnalysisService


class FakeVisionProvider(VisionProvider):
    provider_name = "fake_vision"
    model = "fake-model"

    async def analyze_image(self, image_bytes: bytes, prompt: str, response_schema=None, metadata=None):
        return {
            "marketplace": "eBay",
            "evidence_type": "SOLD_LISTING",
            "title": "Car Seat Gap Organizer",
            "price": 18.99,
            "shipping_price": 4.99,
            "condition": "New",
            "seller": "Demo Seller",
            "sold_date": "2026-05-05T00:00:00Z",
            "confidence": "HIGH",
            "warnings": [],
        }


class VisionServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(bind=self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def tearDown(self) -> None:
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_vision_analysis_persists_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db = self.SessionLocal()
            try:
                service = VisionAnalysisService(db=db, provider=FakeVisionProvider(), upload_dir=Path(tmpdir))
                report = asyncio.run(
                    service.analyze_image(
                        image_bytes=b"fake-image-bytes",
                        analysis_type="MARKETPLACE_SCREENSHOT",
                        product_id=None,
                        idea_id=None,
                        file_url="file:///tmp/demo.png",
                        metadata={"marketplace": "eBay", "content_type": "image/png"},
                    )
                )

                self.assertEqual(report.provider, "fake_vision")
                self.assertEqual(report.analysis_type, "MARKETPLACE_SCREENSHOT")
                self.assertEqual(db.query(type(report)).count(), 1)

                serialized = service.serialize_report(report)
                self.assertEqual(serialized["output_json"]["title"], "Car Seat Gap Organizer")
                self.assertEqual(serialized["confidence"], "HIGH")
                self.assertTrue(serialized["review_required"])
            finally:
                db.close()
