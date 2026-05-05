from __future__ import annotations

from typing import Any

from app.services.category_templates import CATEGORY_TEMPLATES


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
        source_platform = (context.get("source_platform") or "").strip().lower()
        source_url = (context.get("source_url") or "").strip().lower()
        text_blob = " ".join([idea_name, category, notes, observations, source_platform, source_url]).lower()

        risk_flags: list[str] = []
        counterfeit_terms = ["fake", "replica", "counterfeit", "1:1", "same as original", "mirror quality", "designer", "authentic"]
        if any(term in text_blob for term in counterfeit_terms):
            risk_flags.append("Potential trademark/counterfeit risk.")
        if "logo" in text_blob and any(term in text_blob for term in ["brand", "nike", "apple", "gucci", "rolex", "chanel"]):
            risk_flags.append("Potential logo or brand infringement risk.")
        if any(term in text_blob for term in ["battery", "electrical", "medicine", "supplement"]):
            risk_flags.append("Potential compliance risk.")

        score = 10
        if category and template:
            score += 10
        if rough_supplier_cost is not None:
            score += 15
        if estimated_landed_cost is not None:
            score += 15
        if rough_supplier_cost is not None and float(rough_supplier_cost) <= 5:
            score += 10
        if estimated_landed_cost is not None and float(estimated_landed_cost) <= 8:
            score += 10
        if any(term in text_blob for term in ["small", "simple", "organizer", "accessory", "holder", "clip", "pocket", "bag", "pouch"]):
            score += 10
        if source_platform or source_url:
            score += 5
        if observations:
            score += 5
        if risk_flags:
            score -= min(30, len(risk_flags) * 10)
        score = max(0, min(100, score))

        if risk_flags and score < 25:
            verdict = "REJECT"
            priority = "LOW"
            reason = "The idea looks risky or weak enough to skip."
        elif score < 40:
            verdict = "NEEDS_MARKET_CHECK"
            priority = "MEDIUM"
            reason = "Cheap and generic is not enough yet; marketplace evidence is still missing."
        elif score < 60:
            verdict = "NEEDS_SUPPLIER_CHECK"
            priority = "MEDIUM"
            reason = "The idea looks worth checking, but supplier clarity is still missing."
        else:
            verdict = "PROMISING_FOR_RESEARCH"
            priority = "HIGH"
            reason = "The idea is small and plausible, but it still needs real market evidence."

        suggested_keywords = template.get(
            "suggested_keywords",
            {
                "ebay_sold": [],
                "ebay_active": [],
                "mercari": [],
                "supplier": [],
            },
        )
        required_next_evidence = list(template.get("required_evidence", []))

        return {
            "agent_name": self.agent_name,
            "output_json": {
                "quick_scan_verdict": verdict,
                "quick_scan_reason": reason,
                "research_priority": priority,
                "research_completeness_score": score,
                "opportunity_score": score,
                "buy_readiness_status": "NOT_READY",
                "suggested_keywords": suggested_keywords,
                "required_next_evidence": required_next_evidence,
                "initial_risk_flags": risk_flags,
            },
            "summary": reason,
            "confidence": "HIGH" if verdict == "PROMISING_FOR_RESEARCH" else "MEDIUM" if verdict in {"NEEDS_MARKET_CHECK", "NEEDS_SUPPLIER_CHECK"} else "LOW",
            "warnings": [],
            "evidence_refs": [],
        }
