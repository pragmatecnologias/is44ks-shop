from __future__ import annotations

from typing import Any, Dict

from app.agents.base_agent import BaseAgent
from app.llm.base import LLMProvider
from app.schemas.agent_schema import TrendAgentOutput


def _row_numeric(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None


def _score_trend_row(row: dict[str, Any]) -> dict[str, Any]:
    direction = str(row.get("trend_direction") or "UNKNOWN").upper()
    seasonality = str(row.get("seasonality_risk") or "UNKNOWN").upper()
    evergreen = int(row.get("evergreen_score") or 0)
    stability = int(row.get("trend_stability_score") or 0)
    spike_risk = int(row.get("spike_risk_score") or 0)

    if not stability:
        if direction in {"RISING", "STABLE"}:
            stability = 70 if seasonality in {"LOW", "UNKNOWN"} else 55
        elif direction == "SEASONAL":
            stability = 50
        elif direction == "SPIKY":
            stability = 25
        elif direction == "DECLINING":
            stability = 20

    if not evergreen:
        evergreen = max(0, min(100, stability - spike_risk // 2))
    if not spike_risk:
        spike_risk = max(0, min(100, 100 - stability))

    return {
        "keyword": str(row.get("keyword") or "").strip(),
        "trend_direction": direction,
        "seasonality_risk": seasonality,
        "evergreen_score": max(0, min(100, evergreen)),
        "trend_stability_score": max(0, min(100, stability)),
        "spike_risk_score": max(0, min(100, spike_risk)),
        "average_interest": _row_numeric(row.get("average_interest")),
        "peak_interest": _row_numeric(row.get("peak_interest")),
        "low_interest": _row_numeric(row.get("low_interest")),
        "verification_status": str(row.get("verification_status") or "").upper(),
    }


class TrendAgent(BaseAgent):
    def __init__(self, llm_provider: LLMProvider):
        super().__init__(llm_provider, "trend_agent")

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        product = context.get("product", {}) or {}
        rows = context.get("trend_research", []) or []
        scored_rows = [_score_trend_row(row) for row in rows if isinstance(row, dict)]
        best = max(scored_rows, key=lambda item: (item["trend_stability_score"], item["evergreen_score"], -(item["spike_risk_score"])), default=None)
        all_keywords = []
        for row in scored_rows:
            if row["keyword"] and row["keyword"] not in all_keywords:
                all_keywords.append(row["keyword"])

        if best is None:
            output = TrendAgentOutput.model_validate(
                {
                    "trend_direction": "UNKNOWN",
                    "seasonality_risk": "UNKNOWN",
                    "evergreen_score": 0,
                    "trend_stability_score": 0,
                    "spike_risk_score": 0,
                    "trend_status": "UNKNOWN",
                    "main_trend_blocker": "No trend research captured yet.",
                    "next_action": "Collect Google Trends or evergreen research before promotion.",
                    "confidence": "LOW",
                }
            )
        else:
            direction = best["trend_direction"]
            seasonality = best["seasonality_risk"]
            stability = best["trend_stability_score"]
            evergreen = best["evergreen_score"]
            spike_risk = best["spike_risk_score"]
            if direction in {"RISING", "STABLE"} and seasonality in {"LOW", "UNKNOWN"} and stability >= 70:
                trend_status = "EVERGREEN"
            elif seasonality == "HIGH" or direction == "SEASONAL":
                trend_status = "SEASONAL"
            elif direction == "SPIKY" or spike_risk >= 70:
                trend_status = "SPIKY"
            elif direction == "DECLINING" or stability < 35:
                trend_status = "DECLINING"
            else:
                trend_status = "UNKNOWN"

            if trend_status == "EVERGREEN":
                blocker = None
                next_action = "Trend looks evergreen or stable. Keep researching economics and competition."
            elif trend_status == "SEASONAL":
                blocker = "Demand appears seasonal."
                next_action = "Treat this as a seasonal campaign only if margin is strong."
            elif trend_status == "SPIKY":
                blocker = "Trend looks spiky."
                next_action = "Validate sustained interest before spending more time."
            elif trend_status == "DECLINING":
                blocker = "Trend appears to be declining."
                next_action = "Pause or find a more evergreen idea."
            else:
                blocker = "No stable trend signal captured yet."
                next_action = "Collect trend research before promotion."

            output = TrendAgentOutput.model_validate(
                {
                    "trend_direction": direction,
                    "seasonality_risk": seasonality,
                    "evergreen_score": evergreen,
                    "trend_stability_score": stability,
                    "spike_risk_score": spike_risk,
                    "trend_status": trend_status,
                    "main_trend_blocker": blocker,
                    "next_action": next_action,
                    "confidence": "HIGH" if trend_status == "EVERGREEN" else "MEDIUM" if trend_status == "SEASONAL" else "LOW",
                }
            )

        return {
            "agent_name": "trend_agent",
            "output_json": output.model_dump(),
            "summary": output.next_action,
            "confidence": output.confidence,
            "warnings": output.warnings,
            "evidence_refs": output.evidence_refs,
        }
