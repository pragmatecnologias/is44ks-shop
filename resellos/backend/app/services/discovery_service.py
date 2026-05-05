from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.supplier import DiscoveryTask, ProductIdea
from app.schemas.product_schema import (
    OpportunityBoardRow,
    ProductCreate,
    ProductIdeaCreate,
    ProductIdeaQuickScanRequest,
    ProductIdeaUpdate,
)
from app.services.product_service import ProductService


CATEGORY_TEMPLATES: dict[str, dict[str, Any]] = {
    "car accessories": {
        "required_evidence": [
            "5 sold listings",
            "10 active listings",
            "dimensions",
            "fitment notes",
            "shipping weight",
        ],
        "risk_checks": ["not mechanical", "not safety-critical", "not electrical unless reviewed"],
        "listing_angles": ["keeps car organized", "prevents items falling", "easy installation", "universal fit"],
        "marketplaces": ["eBay", "Mercari"],
        "suggested_keywords": ["car organizer", "car accessory", "seat gap organizer", "car storage"],
    },
    "desk accessories": {
        "required_evidence": ["5 sold listings", "10 active listings", "shipping weight", "bundle angles"],
        "risk_checks": ["not electrical", "not fragile", "not branded"],
        "listing_angles": ["cleans up desk clutter", "boosts productivity", "small space solution"],
        "marketplaces": ["eBay", "Mercari"],
        "suggested_keywords": ["desk organizer", "cable clip", "monitor stand", "desk accessory"],
    },
    "home organization": {
        "required_evidence": ["5 sold listings", "10 active listings", "dimensions", "material", "shipping weight"],
        "risk_checks": ["not food contact", "not child safety", "not electrical"],
        "listing_angles": ["saves space", "neat home", "simple storage"],
        "marketplaces": ["eBay", "Facebook Marketplace"],
        "suggested_keywords": ["home organizer", "storage solution", "drawer organizer"],
    },
    "pet accessories": {
        "required_evidence": ["5 sold listings", "10 active listings", "material notes", "shipping weight"],
        "risk_checks": ["not ingestible", "not medicine", "not prescription", "not claims-heavy"],
        "listing_angles": ["makes pet care easier", "safe generic accessory", "simple cleanup"],
        "marketplaces": ["eBay", "Mercari"],
        "suggested_keywords": ["pet accessory", "pet grooming", "pet hair remover", "pet organizer"],
    },
    "travel accessories": {
        "required_evidence": ["5 sold listings", "10 active listings", "dimensions", "bundle potential"],
        "risk_checks": ["not battery", "not electrical", "not high-return fragile"],
        "listing_angles": ["travel convenience", "compact storage", "easy packing"],
        "marketplaces": ["eBay", "Mercari"],
        "suggested_keywords": ["travel accessory", "travel organizer", "packing cube"],
    },
    "creator tools": {
        "required_evidence": ["5 sold listings", "10 active listings", "photo quality", "feature clarity"],
        "risk_checks": ["not electronics unless verified", "not trademarked"],
        "listing_angles": ["content creator utility", "desk-friendly setup", "simple workflow"],
        "marketplaces": ["eBay", "Mercari"],
        "suggested_keywords": ["creator tool", "content creator accessory", "desk mount"],
    },
    "small tools": {
        "required_evidence": ["5 sold listings", "10 active listings", "dimensions", "material", "tool use case"],
        "risk_checks": ["not powered", "not safety-critical"],
        "listing_angles": ["easy job completion", "small workshop helper"],
        "marketplaces": ["eBay", "Facebook Marketplace"],
        "suggested_keywords": ["small tool", "hand tool", "utility tool"],
    },
}


def _norm_category(category: str | None) -> str:
    return (category or "").strip().lower()


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


class DiscoveryService:
    def __init__(self, db: Session):
        self.db = db

    def list_ideas(self) -> list[ProductIdea]:
        return self.db.query(ProductIdea).order_by(ProductIdea.updated_at.desc()).all()

    def get_idea(self, idea_id: uuid.UUID) -> ProductIdea | None:
        return self.db.query(ProductIdea).filter(ProductIdea.id == idea_id).first()

    def create_idea(self, data: ProductIdeaCreate) -> ProductIdea:
        notes = data.notes or ""
        if getattr(data, "marketplace_observation", None):
            notes = "\n".join(part for part in [notes, f"Marketplace observation: {data.marketplace_observation}"] if part)
        idea = ProductIdea(
            idea_name=data.idea_name,
            category=data.category,
            source_platform=data.source_platform,
            source_url=data.source_url,
            rough_supplier_cost=data.rough_supplier_cost,
            estimated_landed_cost=data.estimated_landed_cost,
            why_interesting=data.why_interesting,
            notes=notes or None,
            status=data.status or "QUICK_SCAN_NEEDED",
        )
        self.db.add(idea)
        self.db.commit()
        self.db.refresh(idea)
        return idea

    def update_idea(self, idea_id: uuid.UUID, data: ProductIdeaUpdate) -> ProductIdea | None:
        idea = self.get_idea(idea_id)
        if not idea:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(idea, field, value)
        idea.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(idea)
        return idea

    def delete_idea(self, idea_id: uuid.UUID) -> bool:
        idea = self.get_idea(idea_id)
        if not idea:
            return False
        self.db.delete(idea)
        self.db.commit()
        return True

    def quick_scan(self, data: ProductIdeaQuickScanRequest) -> dict[str, Any]:
        template = CATEGORY_TEMPLATES.get(_norm_category(data.category), {})
        required_evidence = list(
            template.get(
                "required_evidence",
                [
                    "5 sold listings",
                    "10 active listings",
                    "supplier cost",
                ],
            )
        )
        suggested_keywords = list(template.get("suggested_keywords", []))

        risk_flags: list[str] = []
        text_blob = " ".join(
            part for part in [
                data.idea_name,
                data.category or "",
                data.why_interesting or "",
                data.notes or "",
                data.marketplace_observation or "",
            ]
            if part
        ).lower()
        blocked_terms = ["fake", "replica", "counterfeit", "brand", "logo", "medicine", "supplement", "battery"]
        for term in blocked_terms:
            if term in text_blob:
                risk_flags.append(f"Matched risk term: {term}")

        score = 50
        if data.rough_supplier_cost is not None:
            score += 10
        if data.estimated_landed_cost is not None:
            score += 10
        if data.rough_supplier_cost is not None and data.rough_supplier_cost <= 5:
            score += 10
        if data.estimated_landed_cost is not None and data.estimated_landed_cost <= 8:
            score += 10
        if any(term in text_blob for term in ["small", "simple", "solves", "organizer", "accessory"]):
            score += 5
        if risk_flags:
            score -= min(20, len(risk_flags) * 4)

        score = max(0, min(100, score))

        if risk_flags and score < 40:
            verdict = "REJECT"
        elif score >= 75:
            verdict = "PROMISING"
        elif score >= 55:
            verdict = "NEEDS_MARKET_CHECK"
        else:
            verdict = "NEEDS_MARKET_CHECK"

        if data.rough_supplier_cost is None:
            required_evidence.append("rough supplier cost")
        if data.estimated_landed_cost is None:
            required_evidence.append("estimated landed cost")
        required_evidence = list(dict.fromkeys(required_evidence))

        if "car" in _norm_category(data.category):
            suggested_keywords.extend(["car seat gap organizer", "car organizer", "car storage"])
        elif "pet" in _norm_category(data.category):
            suggested_keywords.extend(["pet grooming", "pet accessory", "pet hair remover"])
        elif "home" in _norm_category(data.category):
            suggested_keywords.extend(["home organizer", "storage solution", "drawer organizer"])

        suggested_keywords = list(dict.fromkeys([kw for kw in suggested_keywords if kw]))

        research_priority = "HIGH" if verdict == "PROMISING" else "MEDIUM" if verdict == "NEEDS_MARKET_CHECK" else "LOW"
        reason = "Quick scan completed."
        if verdict == "REJECT":
            reason = "Risk terms or weak economics suggest skipping this idea."
        elif verdict == "PROMISING":
            reason = "The idea looks small, cheap, and likely worth deeper research."
        elif verdict == "NEEDS_MARKET_CHECK":
            reason = "The idea needs market evidence before it can be promoted."

        idea = self.create_idea(
            ProductIdeaCreate(
                idea_name=data.idea_name,
                category=data.category,
                source_platform=data.source_platform,
                source_url=data.source_url,
                rough_supplier_cost=data.rough_supplier_cost,
                estimated_landed_cost=data.estimated_landed_cost,
                why_interesting=data.why_interesting,
                notes=data.notes,
                marketplace_observation=data.marketplace_observation,
                status="QUICK_SCAN_COMPLETE",
            )
        )

        self._apply_scan_result(
            idea,
            verdict=verdict,
            reason=reason,
            priority=research_priority,
            risk_flags=risk_flags,
            required_evidence=required_evidence,
            suggested_keywords=suggested_keywords,
            quick_market_signal="Need sold and active checks" if verdict != "REJECT" else "Skip for now",
            quick_profit_signal="Unknown" if data.estimated_landed_cost is None else "Potentially viable" if score >= 55 else "Weak",
            research_completeness_score=min(100, max(0, score)),
            opportunity_score=min(100, max(0, score)),
        )

        tasks = self._replace_tasks(
            idea.id,
            [
                ("market_research", "Search eBay sold listings", 1),
                ("market_research", "Search eBay active listings", 2),
                ("supplier_research", "Add supplier options", 3),
                ("competition_research", "Capture competitor photos and listing notes", 4),
            ],
        )
        return {
            "idea": self._serialize_idea(idea),
            "quick_scan_verdict": idea.quick_scan_verdict,
            "quick_scan_reason": idea.quick_scan_reason,
            "research_priority": idea.research_priority,
            "research_completeness_score": min(100, max(0, score)),
            "opportunity_score": min(100, max(0, score)),
            "buy_readiness_status": "ALMOST_READY" if verdict == "PROMISING" else "NOT_READY",
            "required_next_evidence": _json_load(idea.required_next_evidence, []),
            "suggested_keywords": _json_load(idea.suggested_keywords, []),
            "risk_flags": _json_load(idea.risk_flags, []),
            "tasks": tasks,
        }

    def promote_to_product(self, idea_id: uuid.UUID) -> Product | None:
        idea = self.get_idea(idea_id)
        if not idea:
            return None
        if idea.promoted_product_id:
            return self.db.query(Product).filter(Product.id == idea.promoted_product_id).first()

        product_service = ProductService(self.db)
        product = product_service.create_product(
            ProductCreate(
                name=idea.idea_name,
                category=idea.category,
                subcategory=None,
                description=idea.why_interesting or idea.notes,
                supplier_url=idea.source_url,
            )
        )
        idea.promoted_product_id = product.id
        idea.status = "PROMOTED_TO_PRODUCT"
        self.db.commit()
        self.db.refresh(idea)
        return product

    def _apply_scan_result(
        self,
        idea: ProductIdea,
        *,
        verdict: str,
        reason: str,
        priority: str,
        risk_flags: list[str],
        required_evidence: list[str],
        suggested_keywords: list[str],
        quick_market_signal: str,
        quick_profit_signal: str,
        research_completeness_score: int,
        opportunity_score: int,
    ) -> None:
        if verdict == "REJECT":
            idea.status = "REJECTED"
        elif verdict == "PROMISING":
            idea.status = "PROMISING"
        else:
            idea.status = "QUICK_SCAN_COMPLETE"
        idea.quick_scan_verdict = verdict
        idea.quick_scan_reason = reason
        idea.research_priority = priority
        idea.risk_flags = _json_dump(risk_flags)
        idea.required_next_evidence = _json_dump(required_evidence)
        idea.suggested_keywords = _json_dump(suggested_keywords)
        idea.quick_market_signal = quick_market_signal
        idea.quick_profit_signal = quick_profit_signal
        idea.quick_scan_reason = reason
        idea.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(idea)

    def _replace_tasks(self, idea_id: uuid.UUID, tasks: list[tuple[str, str, int]]) -> list[DiscoveryTask]:
        self.db.query(DiscoveryTask).filter(DiscoveryTask.idea_id == idea_id).delete(synchronize_session=False)
        self.db.commit()
        created: list[DiscoveryTask] = []
        for task_type, title, sort_order in tasks:
            task = DiscoveryTask(
                idea_id=idea_id,
                task_type=task_type,
                title=title,
                status="TODO",
                sort_order=sort_order,
            )
            self.db.add(task)
            created.append(task)
        self.db.commit()
        for task in created:
            self.db.refresh(task)
        return created

    def _serialize_idea(self, idea: ProductIdea) -> dict[str, Any]:
        tasks = (
            self.db.query(DiscoveryTask)
            .filter(DiscoveryTask.idea_id == idea.id)
            .order_by(DiscoveryTask.sort_order.asc(), DiscoveryTask.created_at.asc())
            .all()
        )
        done_tasks = sum(1 for task in tasks if task.status == "DONE")
        research_completeness_score = 0
        if tasks:
            research_completeness_score += min(60, int((done_tasks / len(tasks)) * 60))
        if idea.status == "PROMISING":
            research_completeness_score += 25
        elif idea.status == "QUICK_SCAN_COMPLETE":
            research_completeness_score += 15
        elif idea.status == "REJECTED":
            research_completeness_score += 5
        return {
            "id": str(idea.id),
            "idea_name": idea.idea_name,
            "category": idea.category,
            "source_platform": idea.source_platform,
            "source_url": idea.source_url,
            "rough_supplier_cost": float(idea.rough_supplier_cost) if idea.rough_supplier_cost is not None else None,
            "estimated_landed_cost": float(idea.estimated_landed_cost) if idea.estimated_landed_cost is not None else None,
            "why_interesting": idea.why_interesting,
            "risk_flags": _json_load(idea.risk_flags, []),
            "quick_market_signal": idea.quick_market_signal,
            "quick_profit_signal": idea.quick_profit_signal,
            "research_priority": idea.research_priority,
            "notes": idea.notes,
            "status": idea.status,
            "quick_scan_verdict": idea.quick_scan_verdict,
            "quick_scan_reason": idea.quick_scan_reason,
            "research_completeness_score": min(100, research_completeness_score),
            "opportunity_score": min(100, research_completeness_score),
            "buy_readiness_status": "ALMOST_READY" if idea.status == "PROMISING" else "NOT_READY",
            "suggested_keywords": _json_load(idea.suggested_keywords, []),
            "required_next_evidence": _json_load(idea.required_next_evidence, []),
            "promoted_product_id": str(idea.promoted_product_id) if idea.promoted_product_id else None,
            "tasks": [self._serialize_task(task) for task in tasks],
            "created_at": idea.created_at,
            "updated_at": idea.updated_at,
        }

    def _serialize_task(self, task: DiscoveryTask) -> dict[str, Any]:
        return {
            "id": str(task.id),
            "idea_id": str(task.idea_id),
            "task_type": task.task_type,
            "title": task.title,
            "status": task.status,
            "notes": task.notes,
            "sort_order": task.sort_order,
            "created_at": task.created_at,
        }

    def opportunity_board(self) -> list[dict[str, Any]]:
        from app.models.product import Product
        from app.models.supplier import CompetitorListing, MarketplaceEvidence, ProfitAnalysis, ProductSource

        board: list[dict[str, Any]] = []

        for idea in self.list_ideas():
            tasks = self.db.query(DiscoveryTask).filter(DiscoveryTask.idea_id == idea.id).all()
            total_tasks = len(tasks)
            done_tasks = sum(1 for task in tasks if task.status == "DONE")
            completeness = 20 if idea.quick_scan_verdict else 10
            if total_tasks:
                completeness += min(50, int((done_tasks / total_tasks) * 50))
            if idea.status == "PROMISING":
                completeness += 20
            elif idea.status == "REJECTED":
                completeness = min(completeness, 20)
            board.append(
                {
                    "id": str(idea.id),
                    "entity_type": "idea",
                    "title": idea.idea_name,
                    "category": idea.category,
                    "research_completeness_score": max(0, min(100, completeness)),
                    "research_verdict": idea.quick_scan_verdict or ("PROMISING" if idea.status == "PROMISING" else "NEEDS_MORE_RESEARCH"),
                    "buy_readiness_status": "NOT_READY",
                    "risk_level": "BLOCKED" if idea.status == "REJECTED" else "LOW",
                    "sold_evidence_count": 0,
                    "active_evidence_count": 0,
                    "median_sold_price": None,
                    "median_active_price": None,
                    "best_landed_cost": float(idea.estimated_landed_cost) if idea.estimated_landed_cost is not None else None,
                    "best_profit_scenario": None,
                    "competition_gap_score": None,
                    "supplier_confidence": None,
                    "next_action": (idea.required_next_evidence and _json_load(idea.required_next_evidence, [])[:1] or ["Run quick scan"])[0],
                    "source_platform": idea.source_platform,
                    "status": idea.status,
                }
            )

        products = self.db.query(Product).order_by(Product.updated_at.desc()).all()
        for product in products:
            evidence_rows = self.db.query(MarketplaceEvidence).filter(MarketplaceEvidence.product_id == product.id).all()
            sources = self.db.query(ProductSource).filter(ProductSource.product_id == product.id).all()
            profit_rows = self.db.query(ProfitAnalysis).filter(ProfitAnalysis.product_id == product.id).all()
            competitor_rows = self.db.query(CompetitorListing).filter(CompetitorListing.product_id == product.id).all()

            sold_count = sum(1 for row in evidence_rows if row.evidence_type == "SOLD_LISTING")
            active_count = sum(1 for row in evidence_rows if row.evidence_type == "ACTIVE_LISTING")
            best_profit = max((float(row.estimated_net_profit or 0) for row in profit_rows), default=0)
            best_scenario = None
            if profit_rows:
                top_profit = max(profit_rows, key=lambda row: float(row.estimated_net_profit or 0))
                best_scenario = top_profit.scenario_name
            completeness = 0
            completeness += min(30, sold_count * 6)
            completeness += min(20, active_count * 4)
            completeness += min(20, len(sources) * 10)
            completeness += min(15, len(profit_rows) * 5)
            completeness += min(15, len(competitor_rows) * 3)

            board.append(
                {
                    "id": str(product.id),
                    "entity_type": "product",
                    "title": product.name,
                    "category": product.category,
                    "research_completeness_score": max(0, min(100, completeness)),
                    "research_verdict": getattr(product, "final_decision", None) or product.status,
                    "buy_readiness_status": "READY" if product.status in {"BUY_SAMPLE", "BUY_SMALL_BATCH", "APPROVED_TO_LIST"} else "NOT_READY",
                    "risk_level": product.risk_level,
                    "sold_evidence_count": sold_count,
                    "active_evidence_count": active_count,
                    "median_sold_price": None,
                    "median_active_price": None,
                    "best_landed_cost": float(sources[0].estimated_landed_cost) if sources and sources[0].estimated_landed_cost is not None else None,
                    "best_profit_scenario": best_scenario,
                    "competition_gap_score": None,
                    "supplier_confidence": sources[0].supplier_rating if sources else None,
                    "next_action": getattr(product, "next_action", None) or getattr(product, "decision_reason", None),
                    "source_platform": sources[0].supplier_platform if sources else None,
                    "status": product.status,
                }
            )

        board.sort(key=lambda row: (row["research_completeness_score"], row["title"]), reverse=True)
        return board
