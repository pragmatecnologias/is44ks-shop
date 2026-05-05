from __future__ import annotations

from typing import Any


def agent_data(reports: dict[str, Any], name: str) -> dict[str, Any]:
    report = reports.get(name, {})
    if isinstance(report, dict):
        if isinstance(report.get("output_json"), dict):
            return report["output_json"] or {}
        if isinstance(report.get("data"), dict):
            return report["data"] or {}
        return report
    return {}


def collect_text_fields(*values: Any) -> str:
    parts: list[str] = []
    for value in values:
        if value is None:
            continue
        if isinstance(value, str):
            parts.append(value)
        elif isinstance(value, dict):
            parts.extend(collect_text_fields(*value.values()).split("\n"))
        elif isinstance(value, (list, tuple, set)):
            parts.extend(collect_text_fields(*value).split("\n"))
        else:
            parts.append(str(value))
    return "\n".join(part for part in parts if part)

