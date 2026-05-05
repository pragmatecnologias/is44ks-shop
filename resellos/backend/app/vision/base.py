from __future__ import annotations

import base64
import json
from abc import ABC, abstractmethod
from typing import Any


class VisionProvider(ABC):
    provider_name: str = "vision"
    model: str = ""

    @abstractmethod
    async def analyze_image(
        self,
        image_bytes: bytes,
        prompt: str,
        response_schema: dict | None = None,
        metadata: dict | None = None,
    ) -> dict[str, Any]:
        raise NotImplementedError


def guess_image_mime_type(image_bytes: bytes, filename: str | None = None) -> str:
    if image_bytes.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if image_bytes.startswith(b"GIF87a") or image_bytes.startswith(b"GIF89a"):
        return "image/gif"
    if image_bytes.startswith(b"RIFF") and len(image_bytes) > 12 and image_bytes[8:12] == b"WEBP":
        return "image/webp"
    if image_bytes.startswith(b"BM"):
        return "image/bmp"
    if filename:
        lowered = filename.lower()
        if lowered.endswith(".jpg") or lowered.endswith(".jpeg"):
            return "image/jpeg"
        if lowered.endswith(".png"):
            return "image/png"
        if lowered.endswith(".webp"):
            return "image/webp"
        if lowered.endswith(".gif"):
            return "image/gif"
    return "image/png"


def image_bytes_to_data_url(image_bytes: bytes, filename: str | None = None, content_type: str | None = None) -> str:
    mime_type = content_type or guess_image_mime_type(image_bytes, filename)
    encoded = base64.b64encode(image_bytes).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def response_schema_instruction(response_schema: dict | None = None, metadata: dict | None = None) -> str:
    parts: list[str] = ["Return ONLY valid JSON.", "Do not include markdown or commentary."]
    if metadata:
        parts.append(f"Review context: {json.dumps(metadata, ensure_ascii=False)}")
    if response_schema:
        parts.append(f"Expected JSON shape: {json.dumps(response_schema, ensure_ascii=False)}")
    return "\n".join(parts)
