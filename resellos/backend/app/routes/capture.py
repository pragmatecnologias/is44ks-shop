from __future__ import annotations

import json
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.external_research_schema import ManualCaptureResponse, EvidenceCandidateResponse
from app.services.capture_service import CaptureService

router = APIRouter(prefix="/api/capture", tags=["capture"])


def _parse_metadata(value: str | None) -> dict:
    if not value:
        return {}
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, dict) else {"value": parsed}
    except Exception:
        return {"raw": value}


@router.post("/manual", response_model=ManualCaptureResponse, status_code=201)
async def manual_capture(
    capture_type: str = Form(...),
    idea_id: uuid.UUID | None = Form(None),
    product_id: uuid.UUID | None = Form(None),
    url: str | None = Form(None),
    pasted_text: str | None = Form(None),
    notes: str | None = Form(None),
    screenshot: UploadFile | None = File(None),
    metadata_json: str | None = Form(None),
    db: Session = Depends(get_db),
):
    service = CaptureService(db)
    metadata = _parse_metadata(metadata_json)
    if notes:
        metadata["notes"] = notes
    if url:
        metadata["url"] = url
    if pasted_text:
        metadata["pasted_text"] = pasted_text
    if screenshot and screenshot.content_type:
        metadata["content_type"] = screenshot.content_type

    candidate, report_id = await service.capture_manual(
        idea_id=idea_id,
        product_id=product_id,
        capture_type=capture_type,
        url=url,
        pasted_text=pasted_text,
        screenshot=screenshot,
        notes=notes,
    )
    return ManualCaptureResponse(
        candidate=EvidenceCandidateResponse.model_validate(service.candidate_service.serialize_candidate(candidate)),
        vision_report_id=report_id,
    )

