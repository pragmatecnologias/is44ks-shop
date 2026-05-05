from __future__ import annotations

import json
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.vision_schema import VisionAnalysisResponse, VisionAnalysisType
from app.vision.vision_service import VisionAnalysisService

router = APIRouter(prefix="/api/vision", tags=["vision"])


def _parse_metadata(value: str | None) -> dict:
    if not value:
        return {}
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, dict) else {"value": parsed}
    except Exception:
        return {"raw": value}


@router.post("/analyze", response_model=VisionAnalysisResponse, status_code=201)
async def analyze_image(
    analysis_type: VisionAnalysisType = Form(...),
    image: UploadFile = File(...),
    product_id: uuid.UUID | None = Form(None),
    idea_id: uuid.UUID | None = Form(None),
    file_url: str | None = Form(None),
    notes: str | None = Form(None),
    metadata_json: str | None = Form(None),
    db: Session = Depends(get_db),
):
    service = VisionAnalysisService(db)
    image_bytes, stored_file_url = await service.persist_upload(image)
    metadata = _parse_metadata(metadata_json)
    if notes:
        metadata["notes"] = notes
    if image.content_type:
        metadata["content_type"] = image.content_type

    report = await service.analyze_image(
        image_bytes=image_bytes,
        analysis_type=analysis_type,
        product_id=product_id,
        idea_id=idea_id,
        file_url=file_url or stored_file_url,
        metadata=metadata,
    )
    return VisionAnalysisResponse.model_validate(service.serialize_report(report))


@router.get("/reports", response_model=list[VisionAnalysisResponse])
def list_reports(
    product_id: uuid.UUID | None = None,
    idea_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
):
    service = VisionAnalysisService(db)
    return [
        VisionAnalysisResponse.model_validate(service.serialize_report(report))
        for report in service.list_reports(product_id=product_id, idea_id=idea_id)
    ]


@router.get("/reports/{report_id}", response_model=VisionAnalysisResponse)
def get_report(report_id: uuid.UUID, db: Session = Depends(get_db)):
    service = VisionAnalysisService(db)
    report = service.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Vision analysis report not found")
    return VisionAnalysisResponse.model_validate(service.serialize_report(report))
