from __future__ import annotations

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.vision import VisionAnalysisReport
from app.schemas.vision_schema import VisionAnalysisType
from app.vision import get_vision_provider


def _json_load(value: str | None, default: Any) -> Any:
    if not value:
        return default
    try:
        return json.loads(value)
    except Exception:
        return default


def _json_dump(value: Any) -> str | None:
    if value is None:
        return None
    return json.dumps(value, ensure_ascii=False, default=str)


class VisionAnalysisService:
    def __init__(
        self,
        db: Session | None = None,
        provider: Any | None = None,
        upload_dir: str | Path | None = None,
    ):
        self.db = db
        self.provider = provider or get_vision_provider()
        default_upload_dir = Path(__file__).resolve().parents[2] / "data" / "vision_uploads"
        self.upload_dir = Path(upload_dir or os.getenv("VISION_UPLOAD_DIR") or default_upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def _build_prompt(self, analysis_type: VisionAnalysisType, metadata: dict[str, Any] | None = None) -> tuple[str, dict[str, Any]]:
        metadata = metadata or {}
        if analysis_type == "MARKETPLACE_SCREENSHOT":
            return (
                "Extract marketplace listing evidence from this screenshot. "
                "Do not save anything automatically. Infer whether the listing is active or sold. Return a review-ready JSON candidate with marketplace, evidence_type, title, price, shipping_price, condition, seller, sold_date, confidence, warnings.",
                {
                    "marketplace": "eBay",
                    "evidence_type": "ACTIVE_LISTING|SOLD_LISTING",
                    "title": "string",
                    "price": 0.0,
                    "shipping_price": 0.0,
                    "condition": "string",
                    "seller": "string",
                    "sold_date": "string",
                    "confidence": "LOW|MEDIUM|HIGH",
                    "warnings": ["string"],
                },
            )
        if analysis_type == "SUPPLIER_SCREENSHOT":
            return (
                "Extract supplier page details from this screenshot. "
                "Do not save anything automatically. Return a review-ready JSON candidate with supplier_platform, product_title, unit_cost, moq, variations, shipping_notes, logo_or_brand_risk, missing_info, confidence, warnings.",
                {
                    "supplier_platform": "1688",
                    "product_title": "string",
                    "unit_cost": 0.0,
                    "moq": 0,
                    "variations": ["string"],
                    "shipping_notes": "string",
                    "logo_or_brand_risk": False,
                    "missing_info": ["string"],
                    "confidence": "LOW|MEDIUM|HIGH",
                    "warnings": ["string"],
                },
            )
        if analysis_type == "COMPETITOR_PHOTO":
            return (
                "Analyze the competitor listing screenshot or photo. "
                "Do not save anything automatically. Return a review-ready JSON candidate with photo_score, title_score, description_score, weaknesses, opportunity_angle, confidence, warnings.",
                {
                    "photo_score": 0,
                    "title_score": 0,
                    "description_score": 0,
                    "weaknesses": ["string"],
                    "opportunity_angle": "string",
                    "confidence": "LOW|MEDIUM|HIGH",
                    "warnings": ["string"],
                },
            )
        return (
            "Check the screenshot for visible logo, brand, safety, or compliance risk. "
            "Do not make legal conclusions. Return a review-ready JSON candidate with risk_flags, visible_brands, visible_claims, blocked, notes, confidence, warnings.",
            {
                "risk_flags": ["string"],
                "visible_brands": ["string"],
                "visible_claims": ["string"],
                "blocked": False,
                "notes": "string",
                "confidence": "LOW|MEDIUM|HIGH",
                "warnings": ["string"],
            },
        )

    async def persist_upload(self, upload: UploadFile) -> tuple[bytes, str]:
        image_bytes = await upload.read()
        suffix = Path(upload.filename or "").suffix or ".png"
        file_name = f"{uuid.uuid4()}{suffix}"
        file_path = self.upload_dir / file_name
        file_path.write_bytes(image_bytes)
        return image_bytes, str(file_path)

    async def analyze_image(
        self,
        image_bytes: bytes,
        analysis_type: VisionAnalysisType,
        *,
        product_id: uuid.UUID | None = None,
        idea_id: uuid.UUID | None = None,
        file_url: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> VisionAnalysisReport:
        prompt, response_schema = self._build_prompt(analysis_type, metadata)
        output = await self.provider.analyze_image(
            image_bytes=image_bytes,
            prompt=prompt,
            response_schema=response_schema,
            metadata=metadata,
        )
        confidence = str(output.get("confidence") or "MEDIUM")
        report = VisionAnalysisReport(
            product_id=product_id,
            idea_id=idea_id,
            file_url=file_url,
            analysis_type=analysis_type,
            provider=getattr(self.provider, "provider_name", self.provider.__class__.__name__),
            model=getattr(self.provider, "model", ""),
            input_metadata=_json_dump(metadata or {}),
            output_json=_json_dump(output),
            confidence=confidence,
        )
        if self.db is not None:
            self.db.add(report)
            self.db.commit()
            self.db.refresh(report)
        return report

    def list_reports(
        self,
        *,
        product_id: uuid.UUID | None = None,
        idea_id: uuid.UUID | None = None,
    ) -> list[VisionAnalysisReport]:
        if self.db is None:
            return []
        query = self.db.query(VisionAnalysisReport)
        if product_id is not None:
            query = query.filter(VisionAnalysisReport.product_id == product_id)
        if idea_id is not None:
            query = query.filter(VisionAnalysisReport.idea_id == idea_id)
        return query.order_by(VisionAnalysisReport.created_at.desc()).all()

    def get_report(self, report_id: uuid.UUID) -> VisionAnalysisReport | None:
        if self.db is None:
            return None
        return self.db.query(VisionAnalysisReport).filter(VisionAnalysisReport.id == report_id).first()

    def serialize_report(self, report: VisionAnalysisReport) -> dict[str, Any]:
        return {
            "id": report.id,
            "product_id": report.product_id,
            "idea_id": report.idea_id,
            "file_url": report.file_url,
            "analysis_type": report.analysis_type,
            "provider": report.provider,
            "model": report.model,
            "input_metadata": _json_load(report.input_metadata, {}),
            "output_json": _json_load(report.output_json, {}),
            "confidence": report.confidence,
            "review_required": True,
            "created_at": report.created_at or datetime.utcnow(),
        }
