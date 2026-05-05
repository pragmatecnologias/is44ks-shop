from __future__ import annotations

from typing import Any
import uuid

from app.schemas.vision_schema import VisionAnalysisType
from app.vision.vision_service import VisionAnalysisService


class BaseVisionAgent:
    def __init__(
        self,
        analysis_type: VisionAnalysisType,
        service: VisionAnalysisService | None = None,
        agent_name: str | None = None,
    ):
        self.analysis_type = analysis_type
        self.service = service or VisionAnalysisService()
        self.agent_name = agent_name or self.__class__.__name__.lower()

    async def run(
        self,
        image_bytes: bytes,
        *,
        product_id: uuid.UUID | None = None,
        idea_id: uuid.UUID | None = None,
        file_url: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        report = await self.service.analyze_image(
            image_bytes=image_bytes,
            analysis_type=self.analysis_type,
            product_id=product_id,
            idea_id=idea_id,
            file_url=file_url,
            metadata=metadata,
        )
        serialized = self.service.serialize_report(report)
        return {
            "agent_name": self.agent_name,
            "output_json": serialized["output_json"],
            "summary": f"{self.analysis_type} analysis completed.",
            "confidence": serialized.get("confidence", "MEDIUM"),
            "warnings": serialized["output_json"].get("warnings", []),
            "evidence_refs": [],
        }
