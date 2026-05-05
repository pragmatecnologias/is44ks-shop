from __future__ import annotations

import re
import uuid
from typing import Any

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.config import settings
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
            report = await self.vision_service.analyze_image(
                image_bytes=image_bytes,
                analysis_type=analysis_type,
                idea_id=idea_id,
                product_id=product_id,
                file_url=stored_file_url,
                metadata=metadata,
            )
            output = report.output_json if isinstance(report.output_json, dict) else {}
            candidate = self._build_candidate_from_vision(
                idea_id=idea_id,
                product_id=product_id,
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
            self.db.add(candidate)
            self.db.commit()
            self.db.refresh(candidate)
            return candidate, report.id

        candidate = self._build_candidate_from_text(
            idea_id=idea_id,
            product_id=product_id,
            capture_type=capture_type,
            url=url,
            notes=notes,
            pasted_text=pasted_text or "",
        )
        self.db.add(candidate)
        self.db.commit()
        self.db.refresh(candidate)
        return candidate, None

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
            source="MANUAL_CAPTURE",
            candidate_type=candidate_type,
            marketplace=capture_type.replace("_", " ").title(),
            evidence_type=evidence_type if candidate_type == "MARKETPLACE_EVIDENCE" else None,
            title=title,
            url=url,
            price=price,
            shipping_price=shipping_price,
            seller=None,
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
    ) -> EvidenceCandidate:
        capture_type = capture_type.upper().strip()
        candidate_type = self._candidate_type_for_capture(capture_type)
        evidence_type = output.get("evidence_type") or ("ACTIVE_LISTING" if candidate_type == "MARKETPLACE_EVIDENCE" else None)
        raw_json = {**output, "capture_type": capture_type, "url": url, "notes": notes}
        return EvidenceCandidate(
            idea_id=idea_id,
            product_id=product_id,
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
