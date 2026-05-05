from __future__ import annotations

from typing import Any


CATEGORY_TEMPLATES: dict[str, dict[str, Any]] = {
    "car accessories": {
        "required_evidence": [
            "Add 5 sold eBay listings",
            "Add 5 active eBay listings",
            "Add 2 supplier sources",
        ],
        "suggested_keywords": {
            "ebay_sold": ["car seat gap organizer", "car side pocket storage"],
            "supplier": ["car seat gap storage box", "auto side organizer"],
        },
    },
    "desk accessories": {
        "required_evidence": [
            "Add 5 sold eBay listings",
            "Add 5 active eBay listings",
            "Add 2 supplier sources",
        ],
        "suggested_keywords": {
            "ebay_sold": ["desk cable clips", "desk organizer"],
            "supplier": ["desk accessory", "cable clip organizer"],
        },
    },
    "pet accessories": {
        "required_evidence": [
            "Add 5 sold eBay listings",
            "Add 5 active eBay listings",
            "Add 2 supplier sources",
        ],
        "suggested_keywords": {
            "ebay_sold": ["pet hair remover", "pet grooming glove"],
            "supplier": ["pet accessory", "pet grooming tool"],
        },
    },
}


class QuickScanAgent:
    def __init__(self) -> None:
        self.agent_name = "quick_scan_agent"

    def run(self, context: dict[str, Any]) -> dict[str, Any]:
        category = (context.get("category") or "").strip().lower()
        template = CATEGORY_TEMPLATES.get(category, {})
        idea_name = context.get("idea_name") or ""
        notes = context.get("notes") or ""
        rough_supplier_cost = context.get("rough_supplier_cost")
        estimated_landed_cost = context.get("estimated_landed_cost")
        observations = (context.get("marketplace_observation") or "").lower()
        text_blob = " ".join([idea_name, category, notes, observations]).lower()

        risk_flags: list[str] = []
        if any(term in text_blob for term in ["fake", "replica", "counterfeit", "logo", "brand"]):
            risk_flags.append("Potential trademark/counterfeit risk.")
        if any(term in text_blob for term in ["battery", "electrical", "medicine", "supplement"]):
            risk_flags.append("Potential compliance risk.")

        score = 50
        if rough_supplier_cost is not None:
            score += 10
        if estimated_landed_cost is not None:
            score += 10
        if rough_supplier_cost is not None and float(rough_supplier_cost) <= 5:
            score += 10
        if estimated_landed_cost is not None and float(estimated_landed_cost) <= 8:
            score += 10
        if any(term in text_blob for term in ["small", "simple", "organizer", "accessory", "holder"]):
            score += 5
        if risk_flags:
            score -= min(20, len(risk_flags) * 5)
        score = max(0, min(100, score))

        if risk_flags and score < 40:
            verdict = "REJECT"
            priority = "LOW"
            reason = "The idea looks risky or weak enough to skip."
        elif score >= 75:
            verdict = "PROMISING"
            priority = "HIGH"
            reason = "The idea looks small, cheap, and worth deeper research."
        else:
            verdict = "NEEDS_MARKET_CHECK"
            priority = "MEDIUM"
            reason = "The idea needs market evidence before it can be promoted."

        suggested_keywords = template.get("suggested_keywords", {})
        required_next_evidence = list(template.get("required_evidence", []))

        return {
            "agent_name": self.agent_name,
            "output_json": {
                "quick_scan_verdict": verdict,
                "quick_scan_reason": reason,
                "research_priority": priority,
                "research_completeness_score": score,
                "opportunity_score": score,
                "buy_readiness_status": "ALMOST_READY" if verdict == "PROMISING" else "NOT_READY",
                "suggested_keywords": suggested_keywords,
                "required_next_evidence": required_next_evidence,
                "initial_risk_flags": risk_flags,
            },
            "summary": reason,
            "confidence": "HIGH" if verdict == "PROMISING" else "MEDIUM" if verdict == "NEEDS_MARKET_CHECK" else "LOW",
            "warnings": [],
            "evidence_refs": [],
        }
