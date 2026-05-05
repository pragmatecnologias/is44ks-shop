from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


@dataclass(frozen=True)
class RiskRule:
    id: str
    severity: str
    match_fields: tuple[str, ...]
    patterns: tuple[str, ...]
    reason: str


@dataclass
class RiskRuleMatch:
    rule_id: str
    severity: str
    matched_text: str
    reason: str


RISK_RULES: tuple[RiskRule, ...] = (
    RiskRule(
        id="counterfeit_brand_name",
        severity="BLOCKED",
        match_fields=("name", "description", "supplier_title", "supplier_notes", "marketplace_notes", "competitor_text"),
        patterns=(
            "nike",
            "airpods",
            "rolex",
            "gucci",
            "chanel",
            "louis vuitton",
            "mirror",
        ),
        reason="Known brand or counterfeit indicator detected.",
    ),
    RiskRule(
        id="replica_language",
        severity="BLOCKED",
        match_fields=("name", "description", "supplier_title", "supplier_notes", "marketplace_notes", "competitor_text"),
        patterns=("replica", "1:1", "same as original", "mirror quality", "unbranded replica"),
        reason="Replica/counterfeit language detected.",
    ),
    RiskRule(
        id="pet_ingestible",
        severity="HIGH",
        match_fields=("name", "description", "category", "supplier_title", "marketplace_notes"),
        patterns=("pet supplement", "pet vitamin", "pet medicine", "dog medicine", "cat medicine"),
        reason="Pet ingestible or medicine requires compliance review.",
    ),
    RiskRule(
        id="pet_accessory",
        severity="ALLOW",
        match_fields=("name", "description", "category", "supplier_title", "marketplace_notes"),
        patterns=("pet accessory", "pet grooming", "pet hair remover", "pet bowl", "pet leash", "pet toy"),
        reason="Generic pet accessory; not automatically blocked.",
    ),
    RiskRule(
        id="battery_risk",
        severity="HIGH",
        match_fields=("name", "description", "category", "supplier_title", "marketplace_notes"),
        patterns=("lithium battery", "power bank", "battery pack", "rechargeable battery"),
        reason="Battery or lithium-related product needs shipping and compliance review.",
    ),
    RiskRule(
        id="medical_claim_risk",
        severity="HIGH",
        match_fields=("name", "description", "category", "supplier_title", "marketplace_notes"),
        patterns=("treats", "cures", "diagnoses", "medical device", "therapy", "pain relief"),
        reason="Medical or health claim detected.",
    ),
)


def _normalize_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.lower()
    return str(value).lower()


def evaluate_risk_rules(context: dict) -> dict:
    combined_fields = {
        "name": _normalize_text(context.get("name")),
        "description": _normalize_text(context.get("description")),
        "category": _normalize_text(context.get("category")),
        "supplier_title": _normalize_text(context.get("supplier_title")),
        "supplier_notes": _normalize_text(context.get("supplier_notes")),
        "marketplace_notes": _normalize_text(context.get("marketplace_notes")),
        "competitor_text": _normalize_text(context.get("competitor_text")),
    }

    risk_flags: list[dict] = []
    blocked = False
    highest_severity = "LOW"

    def severity_rank(severity: str) -> int:
        order = {"ALLOW": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "BLOCKED": 4}
        return order.get(severity, 0)

    for rule in RISK_RULES:
        matched_text = ""
        for field in rule.match_fields:
            field_text = combined_fields.get(field, "")
            if not field_text:
                continue
            for pattern in rule.patterns:
                if pattern in field_text:
                    matched_text = pattern
                    break
            if matched_text:
                break
        if matched_text:
            risk_flags.append(
                {
                    "rule_id": rule.id,
                    "severity": rule.severity,
                    "matched_text": matched_text,
                    "reason": rule.reason,
                }
            )
            if rule.severity == "BLOCKED":
                blocked = True
            if severity_rank(rule.severity) > severity_rank(highest_severity):
                highest_severity = rule.severity

    if blocked:
        risk_level = "BLOCKED"
    elif highest_severity == "HIGH":
        risk_level = "HIGH"
    elif highest_severity == "MEDIUM":
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    requires_manual_review = risk_level in {"HIGH", "BLOCKED"} or any(flag["severity"] in {"HIGH", "BLOCKED"} for flag in risk_flags)

    return {
        "risk_level": risk_level,
        "blocked": blocked,
        "risk_flags": risk_flags,
        "red_flags": [flag["reason"] for flag in risk_flags if flag["severity"] in {"HIGH", "BLOCKED"}],
        "requires_manual_review": requires_manual_review,
    }
