from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.supplier import DiscoveryTask, ProductDiscoveryIdea
from app.schemas.product_schema import DiscoveryIdeaCreate, DiscoveryQuickScanRequest, DiscoveryIdeaUpdate, ProductCreate
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

    def list_ideas(self) -> list[ProductDiscoveryIdea]:
        return self.db.query(ProductDiscoveryIdea).order_by(ProductDiscoveryIdea.updated_at.desc()).all()

    def get_idea(self, idea_id: uuid.UUID) -> ProductDiscoveryIdea | None:
        return self.db.query(ProductDiscoveryIdea).filter(ProductDiscoveryIdea.id == idea_id).first()

    def create_idea(self, data: DiscoveryIdeaCreate) -> ProductDiscoveryIdea:
        idea = ProductDiscoveryIdea(
            idea_name=data.idea_name,
            category=data.category,
            source_platform=data.source_platform,
            source_url=data.source_url,
            rough_supplier_cost=data.rough_supplier_cost,
            estimated_landed_cost=data.estimated_landed_cost,
            why_interesting=data.why_interesting,
            notes=data.notes,
            status="IDEA",
        )
        self.db.add(idea)
        self.db.commit()
        self.db.refresh(idea)
        return idea

    def update_idea(self, idea_id: uuid.UUID, data: DiscoveryIdeaUpdate) -> ProductDiscoveryIdea | None:
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

    def quick_scan(self, data: DiscoveryQuickScanRequest) -> dict[str, Any]:
        template = CATEGORY_TEMPLATES.get(_norm_category(data.category), {})
        required_evidence = list(template.get("required_evidence", [
            "5 sold listings",
            "10 active listings",
            "supplier cost",
        ]))
        suggested_keywords = list(template.get("suggested_keywords", []))

        risk_flags: list[str] = []
        text_blob = " ".join(
            part for part in [
                data.idea_name,
                data.category or "",
                data.why_interesting or "",
                data.notes or "",
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

        if risk_flags and score < 45:
            verdict = "REJECT"
        elif score >= 75:
            verdict = "PROMISING"
        elif score >= 55:
            verdict = "CONTINUE_RESEARCH"
        else:
            verdict = "WEAK"

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

        research_priority = "HIGH" if verdict == "PROMISING" else "MEDIUM" if verdict == "CONTINUE_RESEARCH" else "LOW"
        reason = "Quick scan completed."
        if verdict == "REJECT":
            reason = "Risk terms or weak economics suggest skipping this idea."
        elif verdict == "PROMISING":
            reason = "The idea looks small, cheap, and likely worth deeper research."
        elif verdict == "WEAK":
            reason = "The idea needs stronger evidence or better economics."

        idea = self.create_idea(
            DiscoveryIdeaCreate(
                idea_name=data.idea_name,
                category=data.category,
                source_platform=data.source_platform,
                source_url=data.source_url,
                rough_supplier_cost=data.rough_supplier_cost,
                estimated_landed_cost=data.estimated_landed_cost,
                why_interesting=data.why_interesting,
                notes=data.notes,
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
        idea.status = "PROMOTED_TO_PRODUCT_RESEARCH"
        self.db.commit()
        self.db.refresh(idea)
        return product

    def _apply_scan_result(
        self,
        idea: ProductDiscoveryIdea,
        *,
        verdict: str,
        reason: str,
        priority: str,
        risk_flags: list[str],
        required_evidence: list[str],
        suggested_keywords: list[str],
        quick_market_signal: str,
        quick_profit_signal: str,
    ) -> None:
        idea.status = "QUICK_SCAN_COMPLETE"
        idea.quick_scan_verdict = verdict
        idea.quick_scan_reason = reason
        idea.research_priority = priority
        idea.risk_flags = _json_dump(risk_flags)
        idea.required_next_evidence = _json_dump(required_evidence)
        idea.suggested_keywords = _json_dump(suggested_keywords)
        idea.quick_market_signal = quick_market_signal
        idea.quick_profit_signal = quick_profit_signal
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

    def _serialize_idea(self, idea: ProductDiscoveryIdea) -> dict[str, Any]:
        tasks = (
            self.db.query(DiscoveryTask)
            .filter(DiscoveryTask.idea_id == idea.id)
            .order_by(DiscoveryTask.sort_order.asc(), DiscoveryTask.created_at.asc())
            .all()
        )
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
