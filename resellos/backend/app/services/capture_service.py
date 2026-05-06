from __future__ import annotations

import json
import re
import uuid
from typing import Any

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.config import settings
from app.models.supplier import AgentReport, DiscoveryTask, ProductIdea
from app.models.product import Product
from app.models.external_research import EvidenceCandidate
from app.schemas.vision_schema import VisionAnalysisType
from app.services.evidence_candidate_service import EvidenceCandidateService
from app.vision.vision_service import VisionAnalysisService


class CaptureService:
    def __init__(self, db: Session):
        self.db = db
        self.vision_service = VisionAnalysisService(db)
        self.candidate_service = EvidenceCandidateService(db)

    async def capture_manual(
        self,
        *,
        idea_id: uuid.UUID | None = None,
        product_id: uuid.UUID | None = None,
        task_id: uuid.UUID | None = None,
        capture_type: str,
        url: str | None = None,
        pasted_text: str | None = None,
        screenshot: UploadFile | None = None,
        notes: str | None = None,
    ) -> tuple[EvidenceCandidate, uuid.UUID | None]:
        if not screenshot and not pasted_text:
            raise HTTPException(status_code=400, detail="Provide a screenshot or pasted text for manual capture.")

        if screenshot:
            image_bytes, stored_file_url = await self.vision_service.persist_upload(screenshot)
            if len(image_bytes) > settings.VISION_MAX_IMAGE_MB * 1024 * 1024:
                raise HTTPException(status_code=400, detail="Screenshot exceeds the configured size limit.")
            analysis_type = self._capture_type_to_analysis_type(capture_type)
            metadata = {
                "capture_type": capture_type,
                "url": url,
                "notes": notes,
                "pasted_text": pasted_text,
                "content_type": screenshot.content_type,
            }
            report = None
            output: dict[str, Any] = {}
            try:
                report = await self.vision_service.analyze_image(
                    image_bytes=image_bytes,
                    analysis_type=analysis_type,
                    idea_id=idea_id,
                    product_id=product_id,
                    file_url=stored_file_url,
                    metadata=metadata,
                )
                output = self._coerce_vision_output(report.output_json)
                candidate = self._build_candidate_from_vision(
                    idea_id=idea_id,
                    product_id=product_id,
                    campaign_id=self._resolve_campaign_id(idea_id=idea_id, product_id=product_id, task_id=task_id),
                    capture_type=capture_type,
                    url=url,
                    notes=notes,
                    output=output,
                    screenshot_url=stored_file_url,
                )
                candidate.raw_json = {
                    "capture_type": capture_type,
                    "url": url,
                    "notes": notes,
                    "vision_output": output,
                }
            except Exception as exc:
                fallback_text = "\n".join(part for part in [notes, pasted_text, url] if part)
                candidate = self._build_candidate_from_text(
                    idea_id=idea_id,
                    product_id=product_id,
                    campaign_id=self._resolve_campaign_id(idea_id=idea_id, product_id=product_id, task_id=task_id),
                    capture_type=capture_type,
                    url=url,
                    notes=notes or "Vision capture unavailable; review-only fallback candidate created.",
                    pasted_text=fallback_text,
                    screenshot_url=stored_file_url,
                )
                candidate.raw_json = {
                    "capture_type": capture_type,
                    "url": url,
                    "notes": notes,
                    "vision_error": str(exc),
                    "fallback": True,
                }
            self.db.add(candidate)
            self.db.commit()
            self.db.refresh(candidate)
            return candidate, report.id if report is not None else None

        candidate = self._build_candidate_from_text(
            idea_id=idea_id,
            product_id=product_id,
            campaign_id=self._resolve_campaign_id(idea_id=idea_id, product_id=product_id, task_id=task_id),
            capture_type=capture_type,
            url=url,
            notes=notes,
            pasted_text=pasted_text or "",
        )
        self.db.add(candidate)
        self.db.commit()
        self.db.refresh(candidate)
        return candidate, None

    def _campaign_id_for_idea(self, idea_id: uuid.UUID | None) -> uuid.UUID | None:
        if not idea_id:
            return None
        idea = self.db.query(ProductIdea).filter(ProductIdea.id == idea_id).first()
        return idea.campaign_id if idea else None

    def _campaign_id_for_product(self, product_id: uuid.UUID | None) -> uuid.UUID | None:
        if not product_id:
            return None
        latest_discovery = (
            self.db.query(AgentReport)
            .filter(AgentReport.product_id == product_id, AgentReport.agent_name == "discovery_context")
            .order_by(AgentReport.created_at.desc())
            .first()
        )
        if not latest_discovery or not latest_discovery.output_json:
            return None
        try:
            output = json.loads(latest_discovery.output_json) if isinstance(latest_discovery.output_json, str) else latest_discovery.output_json
        except Exception:
            return None
        idea_id = output.get("idea_id")
        if not idea_id:
            return None
        idea = self.db.query(ProductIdea).filter(ProductIdea.id == uuid.UUID(str(idea_id))).first()
        return idea.campaign_id if idea else None

    def _campaign_id_for_task(self, task_id: uuid.UUID | None) -> uuid.UUID | None:
        if not task_id:
            return None
        task = self.db.query(DiscoveryTask).filter(DiscoveryTask.id == task_id).first()
        if not task:
            return None
        if task.idea and task.idea.campaign_id:
            return task.idea.campaign_id
        if task.linked_product_id:
            return self._campaign_id_for_product(task.linked_product_id)
        return None

    def _resolve_campaign_id(
        self,
        *,
        idea_id: uuid.UUID | None,
        product_id: uuid.UUID | None,
        task_id: uuid.UUID | None = None,
    ) -> uuid.UUID | None:
        return self._campaign_id_for_idea(idea_id) or self._campaign_id_for_product(product_id) or self._campaign_id_for_task(task_id)

    def _capture_type_to_analysis_type(self, capture_type: str) -> VisionAnalysisType:
        capture_type = capture_type.upper().strip()
        if capture_type == "MARKETPLACE_SCREENSHOT":
            return "MARKETPLACE_SCREENSHOT"
        if capture_type == "SUPPLIER_SCREENSHOT":
            return "SUPPLIER_SCREENSHOT"
        if capture_type == "COMPETITOR_SCREENSHOT":
            return "COMPETITOR_PHOTO"
        return "VISUAL_RISK"

    def _build_candidate_from_text(
        self,
        *,
        idea_id: uuid.UUID | None,
        product_id: uuid.UUID | None,
        capture_type: str,
        url: str | None,
        notes: str | None,
        pasted_text: str,
        screenshot_url: str | None = None,
        campaign_id: uuid.UUID | None = None,
    ) -> EvidenceCandidate:
        capture_type = capture_type.upper().strip()
        evidence_type = "ACTIVE_LISTING"
        if "sold" in pasted_text.lower() or capture_type == "MARKETPLACE_SCREENSHOT" and "sold" in pasted_text.lower():
            evidence_type = "SOLD_LISTING"
        candidate_type = self._candidate_type_for_capture(capture_type)
        title = self._first_meaningful_line(pasted_text) or notes or "Manual capture"
        price = self._first_price(pasted_text)
        shipping_price = self._shipping_price(pasted_text)
        raw_json = {
            "capture_type": capture_type,
            "url": url,
            "notes": notes,
            "pasted_text": pasted_text,
            "parsed": {
                "title": title,
                "price": price,
                "shipping_price": shipping_price,
                "evidence_type": evidence_type,
            },
        }
        return EvidenceCandidate(
            idea_id=idea_id,
            product_id=product_id,
            campaign_id=campaign_id,
            source="MANUAL_CAPTURE",
            candidate_type=candidate_type,
            marketplace=capture_type.replace("_", " ").title(),
            evidence_type=evidence_type if candidate_type == "MARKETPLACE_EVIDENCE" else None,
            title=title,
            url=url,
            price=price,
            shipping_price=shipping_price,
            seller=None,
            image_url=screenshot_url,
            confidence="MEDIUM",
            review_status="PENDING",
            raw_json=raw_json,
        )

    def _build_candidate_from_vision(
        self,
        *,
        idea_id: uuid.UUID | None,
        product_id: uuid.UUID | None,
        capture_type: str,
        url: str | None,
        notes: str | None,
        output: dict[str, Any],
        screenshot_url: str | None,
        campaign_id: uuid.UUID | None = None,
    ) -> EvidenceCandidate:
        capture_type = capture_type.upper().strip()
        candidate_type = self._candidate_type_for_capture(capture_type)
        evidence_type = output.get("evidence_type") or ("ACTIVE_LISTING" if candidate_type == "MARKETPLACE_EVIDENCE" else None)
        raw_json = {**output, "capture_type": capture_type, "url": url, "notes": notes}
        return EvidenceCandidate(
            idea_id=idea_id,
            product_id=product_id,
            campaign_id=campaign_id,
            source="VISION",
            candidate_type=candidate_type,
            marketplace=output.get("marketplace") or output.get("supplier_platform") or capture_type.replace("_", " ").title(),
            evidence_type=evidence_type if candidate_type == "MARKETPLACE_EVIDENCE" else None,
            title=output.get("title") or output.get("product_title") or notes,
            url=url,
            price=output.get("price") or output.get("unit_cost"),
            shipping_price=output.get("shipping_price"),
            seller=output.get("seller") or output.get("supplier_platform"),
            rating=output.get("rating"),
            review_count=output.get("review_count") or output.get("reviews_count"),
            image_url=screenshot_url,
            confidence=str(output.get("confidence") or "MEDIUM"),
            review_status="PENDING",
            raw_json=raw_json,
        )

    def _candidate_type_for_capture(self, capture_type: str) -> str:
        if capture_type == "SUPPLIER_SCREENSHOT":
            return "SUPPLIER_SOURCE"
        if capture_type == "COMPETITOR_SCREENSHOT":
            return "COMPETITOR_LISTING"
        if capture_type == "VISUAL_RISK":
            return "RISK_FLAG"
        return "MARKETPLACE_EVIDENCE"

    def _coerce_vision_output(self, output_json: Any) -> dict[str, Any]:
        if isinstance(output_json, dict):
            return output_json
        if isinstance(output_json, str):
            try:
                parsed = json.loads(output_json)
            except Exception:
                return {}
            return parsed if isinstance(parsed, dict) else {}
        return {}

    def _first_meaningful_line(self, text: str) -> str | None:
        for line in text.splitlines():
            cleaned = line.strip()
            if cleaned:
                return cleaned[:500]
        return None

    def _first_price(self, text: str) -> float | None:
        match = re.search(r"\$?\s*(\d+(?:\.\d{1,2})?)", text)
        if not match:
            return None
        try:
            return float(match.group(1))
        except Exception:
            return None

    def _shipping_price(self, text: str) -> float | None:
        match = re.search(r"shipping[^0-9]{0,20}\$?\s*(\d+(?:\.\d{1,2})?)", text, re.I)
        if match:
            try:
                return float(match.group(1))
            except Exception:
                return None
        return None
