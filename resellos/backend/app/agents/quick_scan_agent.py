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
        listing_angles = [str(value).lower() for value in template.get("listing_angles", []) if value]
        category_warnings = [str(value).lower() for value in template.get("category_warnings", []) if value]
        evidence_thresholds = template.get("evidence_thresholds", {})

        risk_flags: list[str] = []
        counterfeit_terms = ["fake", "replica", "counterfeit", "1:1", "same as original", "mirror quality", "designer", "authentic"]
        if any(term in text_blob for term in counterfeit_terms):
            risk_flags.append("Potential trademark/counterfeit risk.")
        brand_terms = ["nike", "apple", "gucci", "rolex", "chanel", "sony", "lego", "disney"]
        if "logo" in text_blob and any(term in text_blob for term in brand_terms):
            risk_flags.append("Potential logo or brand infringement risk.")
        if any(term in text_blob for term in ["battery", "electrical", "medicine", "supplement", "prescription", "ingestible"]):
            risk_flags.append("Potential compliance risk.")
        for warning in category_warnings:
            warning_terms = [part.strip() for part in warning.replace(".", "").split() if len(part.strip()) > 3]
            if warning_terms and any(term in text_blob for term in warning_terms):
                risk_flags.append(warning)

        score = 0
        if category and template:
            score += 12
        if rough_supplier_cost is not None:
            score += 12
        if estimated_landed_cost is not None:
            score += 12
        if rough_supplier_cost is not None and float(rough_supplier_cost) <= 5:
            score += 8
        if estimated_landed_cost is not None and float(estimated_landed_cost) <= 8:
            score += 8
        if any(term in text_blob for term in ["small", "simple", "organizer", "accessory", "holder", "clip", "pocket", "bag", "pouch"]):
            score += 6
        if any(term in text_blob for term in listing_angles):
            score += 8
        if source_platform or source_url:
            score += 6
        if observations:
            score += 10
        if evidence_thresholds.get("sold", 0):
            score += 2
        if risk_flags:
            score -= min(35, len(risk_flags) * 10)
        score = max(0, min(100, score))

        if risk_flags and score < 25:
            verdict = "REJECT"
            priority = "LOW"
            reason = "The idea looks risky or weak enough to skip."
        elif not observations and score < 35:
            verdict = "NEEDS_MARKET_CHECK"
            priority = "MEDIUM"
            reason = "Cheap and generic is not enough yet; marketplace evidence is still missing."
        elif rough_supplier_cost is None and estimated_landed_cost is None:
            verdict = "NEEDS_SUPPLIER_CHECK"
            priority = "MEDIUM"
            reason = "The idea looks worth checking, but supplier clarity is still missing."
        elif score < 50:
            verdict = "NEEDS_MARKET_CHECK"
            priority = "MEDIUM"
            reason = "Cheap and generic is not enough yet; marketplace evidence is still missing."
        elif observations and (source_platform or source_url) and (rough_supplier_cost is not None or estimated_landed_cost is not None):
            verdict = "PROMISING_FOR_RESEARCH"
            priority = "HIGH"
            reason = "The idea is small and plausible, but it still needs real market evidence."
        else:
            verdict = "NEEDS_MARKET_CHECK"
            priority = "MEDIUM"
            reason = "The idea needs more market or supplier evidence before it can be called promising."

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
        if not required_next_evidence and evidence_thresholds:
            if evidence_thresholds.get("sold"):
                required_next_evidence.append(f"Add {evidence_thresholds['sold']} sold eBay listings")
            if evidence_thresholds.get("active"):
                required_next_evidence.append(f"Add {evidence_thresholds['active']} active eBay listings")
            if evidence_thresholds.get("suppliers"):
                required_next_evidence.append(f"Add {evidence_thresholds['suppliers']} supplier sources")
            if evidence_thresholds.get("competitors"):
                required_next_evidence.append(f"Add {evidence_thresholds['competitors']} competitor listings")
            if not required_next_evidence:
                required_next_evidence = [
                    "Add 5 sold eBay listings",
                    "Add 5 active eBay listings",
                    "Add 2 supplier sources",
                ]

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
