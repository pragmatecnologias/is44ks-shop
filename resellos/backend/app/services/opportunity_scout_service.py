from __future__ import annotations

import json
import re
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.external_research import EvidenceCandidate
from app.models.product import Product
from app.models.research_search import ResearchSearchResult
from app.models.supplier import CompetitorListing, MarketplaceEvidence, ProductIdea, ProductSource
from app.schemas.product_schema import OpportunityScoutRequest, OpportunityScoutResponse


_PAIN_TERMS = (
    "repair",
    "replace",
    "replacement",
    "stuck",
    "broken",
    "loose",
    "worn",
    "sagging",
    "off track",
    "noise",
    "vibration",
    "draft",
    "leak",
    "clog",
    "walks",
    "puller",
    "removal",
)

_HIGH_RISK_TERMS = (
    "gas line",
    "brake",
    "medical",
    "ingest",
    "chemical",
    "shock",
    "fire",
    "dangerous",
    "unsafe",
    "universal",
    "universal fit",
)

_SPECIFICITY_TERMS = (
    "3/8",
    "1/2",
    "23mm",
    "25mm",
    "27mm",
    "1200",
    "1222",
    "1225",
    "moen",
    "pivot",
    "roller",
    "spline",
    "flush lever",
    "anti-vibration",
    "draft seal",
    "furniture leveler",
)


def _json_dump(value: Any) -> str | None:
    if value is None:
        return None
    return json.dumps(value, ensure_ascii=False)


def _json_load(value: str | None, default: Any) -> Any:
    if not value:
        return default
    try:
        return json.loads(value)
    except Exception:
        return default


def _text_blob(*parts: Any) -> str:
    return " ".join(str(part or "") for part in parts).lower()


def _bounded(value: int) -> int:
    return max(0, min(20, int(value)))


def _extract_price(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value)
    match = re.search(r"(\d+(?:[.,]\d{1,2})?)", text)
    if not match:
        return None
    try:
        return float(match.group(1).replace(",", ""))
    except Exception:
        return None


def _median(values: list[float]) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return round(ordered[middle], 2)
    return round((ordered[middle - 1] + ordered[middle]) / 2, 2)


class OpportunityScoutService:
    def __init__(self, db: Session):
        self.db = db

    def evaluate_idea(
        self,
        idea: ProductIdea,
        request: OpportunityScoutRequest | None = None,
    ) -> dict[str, Any]:
        request = request or OpportunityScoutRequest()
        product_id = request.product_id or idea.promoted_product_id
        campaign_id = request.campaign_id or idea.campaign_id

        search_rows = self._search_rows(idea.id, campaign_id, product_id)
        evidence_candidates = self._candidates(idea.id, campaign_id, product_id)
        marketplace_rows = self._marketplace_rows(product_id)
        source_rows = self._source_rows(product_id)
        competitor_rows = self._competitor_rows(product_id)
        product = self.db.query(Product).filter(Product.id == product_id).first() if product_id else None

        keyword_rows = [row for row in search_rows if str(row.intent or "").upper() == "KEYWORD_DEMAND"]
        active_rows = [row for row in search_rows if str(row.intent or "").upper() == "ACTIVE_LISTING"]
        search_competitor_rows = [row for row in search_rows if str(row.intent or "").upper() == "COMPETITOR"]
        supplier_rows = [row for row in search_rows if str(row.intent or "").upper() == "SUPPLIER"]
        sold_rows = [row for row in search_rows if str(row.intent or "").upper() == "SOLD_EVIDENCE"]

        keyword_signals = list(request.keyword_signals)
        if not keyword_signals:
            keyword_signals = [row.title for row in keyword_rows if row.title][:8]
        active_listing_candidates = list(request.active_listing_candidates)
        competitor_candidates = list(request.competitor_candidates)
        supplier_candidates = list(request.supplier_candidates)
        risk_notes = list(request.risk_notes)
        if request.local_search_summary:
            risk_notes.extend(self._listify(request.local_search_summary.get("risk_notes")))
            keyword_signals.extend(self._listify(request.local_search_summary.get("keyword_signals")))
            active_listing_candidates.extend(self._listify(request.local_search_summary.get("active_listing_candidates")))
            competitor_candidates.extend(self._listify(request.local_search_summary.get("competitor_candidates")))
            supplier_candidates.extend(self._listify(request.local_search_summary.get("supplier_candidates")))

        keyword_count = len(keyword_rows) + len(keyword_signals)
        sold_search_count = len(sold_rows)
        active_count = (
            len(active_rows)
            + len(active_listing_candidates)
            + sum(1 for row in evidence_candidates if str(row.candidate_type or "").upper() == "ACTIVE_LISTING")
            + sum(1 for row in marketplace_rows if str(getattr(row, "evidence_type", "")).upper() == "ACTIVE_LISTING")
        )
        competitor_count = (
            len(search_competitor_rows)
            + len(competitor_candidates)
            + sum(1 for row in evidence_candidates if str(row.candidate_type or "").upper() == "COMPETITOR_LISTING")
            + len(competitor_rows)
        )
        supplier_count = len(supplier_rows) + len(supplier_candidates) + len(source_rows) + sum(1 for row in evidence_candidates if str(row.candidate_type or "").upper() == "SUPPLIER_SOURCE")
        sold_proof_count = self._sold_proof_count(product_id)

        active_prices = [price for price in [_extract_price(row.price_text) for row in active_rows] if price is not None]
        active_prices.extend(
            [
                float(row.price_total_price or row.price)
                for row in marketplace_rows
                if str(getattr(row, "evidence_type", "")).upper() == "ACTIVE_LISTING"
                and (row.price_total_price is not None or row.price is not None)
            ]
        )
        competitor_prices = [price for price in [_extract_price(row.price_text) for row in search_competitor_rows] if price is not None]
        competitor_prices.extend([float(row.price) for row in competitor_rows if row.price is not None])
        supplier_prices = [float(source.estimated_landed_cost) for source in source_rows if source.estimated_landed_cost is not None]
        if not supplier_prices and idea.estimated_landed_cost is not None:
            supplier_prices.append(float(idea.estimated_landed_cost))
        if not supplier_prices and idea.rough_supplier_cost is not None:
            supplier_prices.append(float(idea.rough_supplier_cost))

        median_active_price = _median(active_prices)
        median_competitor_price = _median(competitor_prices)
        best_landed_cost = _median(supplier_prices)

        buyer_problem_score = self._buyer_problem_score(idea, keyword_count, risk_notes)
        active_market_score = self._active_market_score(active_count, active_prices, active_rows, active_listing_candidates)
        supplier_path_score = self._supplier_path_score(supplier_count, supplier_prices, source_rows, supplier_candidates)
        competition_risk_score = self._competition_risk_score(competitor_count, competitor_prices, active_count)
        compatibility_risk_score = self._compatibility_risk_score(idea, product, risk_notes)
        margin_potential_score = self._margin_potential_score(median_active_price, best_landed_cost, active_count, supplier_count)
        evidence_friction_score = self._evidence_friction_score(
            keyword_count=keyword_count,
            sold_search_count=sold_search_count,
            active_count=active_count,
            supplier_count=supplier_count,
            competitor_count=competitor_count,
            sold_proof_count=sold_proof_count,
            active_prices=active_prices,
            supplier_prices=supplier_prices,
        )

        total_raw = (
            buyer_problem_score
            + active_market_score
            + supplier_path_score
            + competition_risk_score
            + compatibility_risk_score
            + margin_potential_score
            + evidence_friction_score
        )
        scout_score = round((total_raw / 140) * 100) if total_raw else 0

        sold_proof_present = sold_proof_count > 0
        strong_cluster = active_market_score >= 12 and supplier_path_score >= 8 and buyer_problem_score >= 10
        confidence = "LOW"
        if sold_proof_present and strong_cluster and competitor_count >= 1:
            confidence = "HIGH"
        elif strong_cluster and (active_count >= 3 or supplier_count >= 2):
            confidence = "MEDIUM"

        if compatibility_risk_score <= 5:
            scout_status = "REJECT"
        elif active_market_score <= 4 or supplier_path_score <= 4:
            scout_status = "REJECT"
        elif scout_score >= 75 and sold_proof_present and confidence in {"MEDIUM", "HIGH"}:
            scout_status = "SHORTLIST"
        elif scout_score >= 65 and not sold_proof_present:
            scout_status = "NEEDS_SOLD_PROOF"
        elif scout_score >= 50:
            scout_status = "WATCH"
        else:
            scout_status = "REJECT"

        if scout_status == "SHORTLIST":
            next_step = "Move to full buy-sample validation."
        elif scout_status == "NEEDS_SOLD_PROOF":
            next_step = "Collect sold proof manually or use paid marketplace source."
        elif scout_status == "WATCH":
            next_step = "Keep scouting for stronger price and fit signal."
        else:
            next_step = "Pause this lane."

        reason_bits = [
            f"{keyword_count} keyword signals",
            f"{sold_search_count} sold search signals",
            f"{active_count} active signals",
            f"{supplier_count} supplier signals",
            f"{competitor_count} competitor signals",
        ]
        if sold_proof_present:
            reason_bits.append(f"{sold_proof_count} sold proof signal(s)")
        else:
            reason_bits.append("sold proof missing")
        if median_active_price is not None:
            reason_bits.append(f"median active price ${median_active_price:.2f}")
        if best_landed_cost is not None:
            reason_bits.append(f"landed cost ${best_landed_cost:.2f}")
        if risk_notes:
            reason_bits.append(f"risk notes: {', '.join(risk_notes[:3])}")

        reason = "; ".join(reason_bits)
        metrics = {
            "buyer_problem_score": buyer_problem_score,
            "active_market_score": active_market_score,
            "supplier_path_score": supplier_path_score,
            "competition_risk_score": competition_risk_score,
            "margin_potential_score": margin_potential_score,
            "compatibility_risk_score": compatibility_risk_score,
            "evidence_friction_score": evidence_friction_score,
            "keyword_count": keyword_count,
            "sold_search_count": sold_search_count,
            "active_count": active_count,
            "supplier_count": supplier_count,
            "competitor_count": competitor_count,
            "sold_proof_count": sold_proof_count,
            "median_active_price": median_active_price,
            "median_competitor_price": median_competitor_price,
            "best_landed_cost": best_landed_cost,
            "sold_proof_present": sold_proof_present,
            "risk_notes": risk_notes,
            "keyword_signals": keyword_signals,
            "active_listing_candidates": active_listing_candidates,
            "competitor_candidates": competitor_candidates,
            "supplier_candidates": supplier_candidates,
            "source_counts": {
                "search_rows": len(search_rows),
                "evidence_candidates": len(evidence_candidates),
                "marketplace_rows": len(marketplace_rows),
                "source_rows": len(source_rows),
            },
        }

        return {
            "idea_id": idea.id,
            "campaign_id": campaign_id,
            "product_id": product_id,
            "scout_status": scout_status,
            "scout_score": scout_score,
            "confidence": confidence,
            "buyer_problem_score": buyer_problem_score,
            "active_market_score": active_market_score,
            "supplier_path_score": supplier_path_score,
            "competition_risk_score": competition_risk_score,
            "margin_potential_score": margin_potential_score,
            "compatibility_risk_score": compatibility_risk_score,
            "evidence_friction_score": evidence_friction_score,
            "reason": reason,
            "next_step": next_step,
            "metrics": metrics,
        }

    def persist_result(self, idea: ProductIdea, result: dict[str, Any]) -> ProductIdea:
        idea.scout_status = result.get("scout_status")
        idea.scout_score = int(result.get("scout_score") or 0)
        idea.scout_confidence = result.get("confidence")
        idea.scout_reason = result.get("reason")
        idea.scout_next_step = result.get("next_step")
        idea.scout_metrics_json = _json_dump(result.get("metrics"))
        idea.scout_updated_at = datetime.utcnow()
        idea.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(idea)
        return idea

    def _search_rows(
        self,
        idea_id: uuid.UUID,
        campaign_id: uuid.UUID | None,
        product_id: uuid.UUID | None,
    ) -> list[ResearchSearchResult]:
        conditions = [ResearchSearchResult.idea_id == idea_id]
        if campaign_id is not None:
            conditions.append(ResearchSearchResult.campaign_id == campaign_id)
        if product_id is not None:
            conditions.append(ResearchSearchResult.product_id == product_id)
        query = self.db.query(ResearchSearchResult).filter(or_(*conditions))
        return query.order_by(ResearchSearchResult.created_at.desc()).all()

    def _candidates(
        self,
        idea_id: uuid.UUID,
        campaign_id: uuid.UUID | None,
        product_id: uuid.UUID | None,
    ) -> list[EvidenceCandidate]:
        conditions = [EvidenceCandidate.idea_id == idea_id]
        if campaign_id is not None:
            conditions.append(EvidenceCandidate.campaign_id == campaign_id)
        if product_id is not None:
            conditions.append(EvidenceCandidate.product_id == product_id)
        query = self.db.query(EvidenceCandidate).filter(or_(*conditions))
        return query.order_by(EvidenceCandidate.created_at.desc()).all()

    def _marketplace_rows(self, product_id: uuid.UUID | None) -> list[MarketplaceEvidence]:
        if product_id is None:
            return []
        return self.db.query(MarketplaceEvidence).filter(MarketplaceEvidence.product_id == product_id).all()

    def _source_rows(self, product_id: uuid.UUID | None) -> list[ProductSource]:
        if product_id is None:
            return []
        return self.db.query(ProductSource).filter(ProductSource.product_id == product_id).all()

    def _competitor_rows(self, product_id: uuid.UUID | None) -> list[CompetitorListing]:
        if product_id is None:
            return []
        return self.db.query(CompetitorListing).filter(CompetitorListing.product_id == product_id).all()

    def _sold_proof_count(self, product_id: uuid.UUID | None) -> int:
        if product_id is None:
            return 0
        rows = (
            self.db.query(MarketplaceEvidence)
            .filter(
                MarketplaceEvidence.product_id == product_id,
                MarketplaceEvidence.evidence_type == "SOLD_LISTING",
                MarketplaceEvidence.verification_status == "USER_VERIFIED",
                MarketplaceEvidence.price_verified.is_(True),
            )
            .all()
        )
        return len(rows)

    def _buyer_problem_score(self, idea: ProductIdea, keyword_count: int, risk_notes: list[str]) -> int:
        text = _text_blob(idea.idea_name, idea.why_interesting, idea.notes, " ".join(risk_notes))
        score = min(8, keyword_count * 2)
        score += 6 if any(term in text for term in _PAIN_TERMS) else 0
        score += 4 if any(term in text for term in ("repair", "replace", "replacement", "fix", "stuck", "broken", "loose")) else 0
        score += 2 if any(term in text for term in ("save", "money", "cost", "avoid plumber", "diy", "home maintenance")) else 0
        return _bounded(score)

    def _active_market_score(
        self,
        active_count: int,
        active_prices: list[float],
        active_rows: list[ResearchSearchResult],
        active_listing_candidates: list[dict[str, Any]],
    ) -> int:
        score = min(8, active_count * 2)
        if active_prices:
            score += 4
            median_active = _median(active_prices)
            if median_active is not None and 10 <= median_active <= 35:
                score += 4
            elif median_active is not None and median_active > 35:
                score += 2
        if active_rows:
            score += 2 if any(row.price_text for row in active_rows) else 0
        if active_listing_candidates:
            score += min(4, len(active_listing_candidates))
        return _bounded(score)

    def _supplier_path_score(
        self,
        supplier_count: int,
        supplier_prices: list[float],
        source_rows: list[ProductSource],
        supplier_candidates: list[dict[str, Any]],
    ) -> int:
        score = min(8, supplier_count * 2)
        if supplier_prices:
            score += 6
            if min(supplier_prices) <= 8:
                score += 4
            elif min(supplier_prices) <= 15:
                score += 2
        if source_rows:
            score += 2
        if supplier_candidates:
            score += min(4, len(supplier_candidates))
        return _bounded(score)

    def _competition_risk_score(self, competitor_count: int, competitor_prices: list[float], active_count: int) -> int:
        score = 18 - min(12, competitor_count * 2)
        if competitor_prices:
            median_comp = _median(competitor_prices)
            if median_comp is not None and median_comp >= 20:
                score += 1
            elif median_comp is not None and median_comp < 10:
                score -= 2
        if active_count >= 8:
            score -= 2
        return _bounded(score)

    def _compatibility_risk_score(self, idea: ProductIdea, product: Product | None, risk_notes: list[str]) -> int:
        text = _text_blob(idea.idea_name, idea.why_interesting, idea.notes, product.name if product else "", " ".join(risk_notes))
        score = 8
        if any(term in text for term in _SPECIFICITY_TERMS):
            score += 8
        if any(term in text for term in ("fit guide", "size guide", "compatibility", "compatible", "model", "thread")):
            score += 4
        if any(term in text for term in _HIGH_RISK_TERMS):
            score -= 8
        if "universal" in text and not any(term in text for term in _SPECIFICITY_TERMS):
            score -= 4
        return _bounded(score)

    def _margin_potential_score(
        self,
        median_active_price: float | None,
        best_landed_cost: float | None,
        active_count: int,
        supplier_count: int,
    ) -> int:
        if median_active_price is None or best_landed_cost is None:
            base = 6 if active_count >= 3 and supplier_count >= 1 else 3
            return _bounded(base)
        approx_net = median_active_price * 0.8 - best_landed_cost - 0.75
        if approx_net >= 10:
            return 20
        if approx_net >= 8:
            return 18
        if approx_net >= 6:
            return 15
        if approx_net >= 4:
            return 12
        if approx_net >= 2:
            return 8
        return 3

    def _evidence_friction_score(
        self,
        *,
        keyword_count: int,
        active_count: int,
        sold_search_count: int,
        supplier_count: int,
        competitor_count: int,
        sold_proof_count: int,
        active_prices: list[float],
        supplier_prices: list[float],
    ) -> int:
        score = min(6, keyword_count * 2)
        score += 2 if sold_search_count else 0
        score += 4 if active_count >= 3 else 0
        score += 4 if supplier_count >= 1 else 0
        score += 3 if competitor_count >= 1 else 0
        score += 3 if active_prices else 0
        score += 2 if supplier_prices else 0
        score += 4 if sold_proof_count > 0 else 0
        return _bounded(score)

    def _listify(self, value: Any) -> list[Any]:
        if isinstance(value, list):
            return value
        if value is None:
            return []
        return [value]
