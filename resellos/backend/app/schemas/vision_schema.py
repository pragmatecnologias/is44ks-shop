from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


VisionAnalysisType = Literal[
    "MARKETPLACE_SCREENSHOT",
    "SUPPLIER_SCREENSHOT",
    "COMPETITOR_PHOTO",
    "VISUAL_RISK",
]


class VisionAnalysisRequest(BaseModel):
    analysis_type: VisionAnalysisType
    product_id: uuid.UUID | None = None
    idea_id: uuid.UUID | None = None
    file_url: str | None = None
    notes: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class VisionAnalysisResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID | None = None
    idea_id: uuid.UUID | None = None
    file_url: str | None = None
    analysis_type: VisionAnalysisType
    provider: str
    model: str
    input_metadata: dict[str, Any] = Field(default_factory=dict)
    output_json: dict[str, Any] = Field(default_factory=dict)
    confidence: str | None = None
    review_required: bool = True
    created_at: datetime

    class Config:
        from_attributes = True


class VisionAnalysisListResponse(VisionAnalysisResponse):
    pass
