from __future__ import annotations

import json
import uuid
from datetime import datetime
from statistics import median
from typing import Any

from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.supplier import AgentReport, CompetitorListing, DiscoveryTask, MarketplaceEvidence, ProfitAnalysis, ProductIdea, ProductSource
from app.agents.quick_scan_agent import QuickScanAgent
from app.services.category_templates import CATEGORY_TEMPLATES
from app.schemas.product_schema import (
    OpportunityBoardRow,
    ProductCreate,
    ProductIdeaCreate,
    ProductIdeaQuickScanRequest,
    ProductIdeaUpdate,
    DiscoveryTaskUpdate,
)
from app.services.product_service import ProductService


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


def _median_or_none(values: list[float]) -> float | None:
    if not values:
        return None
    return round(float(median(values)), 2)


def _best_source_landed_cost(source: ProductSource) -> float | None:
    if source.estimated_landed_cost is not None:
        return round(float(source.estimated_landed_cost), 2)
    components = [
        source.unit_cost,
        source.domestic_shipping,
        source.international_shipping_estimate,
    ]
    values = [float(value) for value in components if value is not None]
    if not values:
        return None
    return round(sum(values), 2)


def _latest_report_output(agent_rows: list[AgentReport], agent_name: str) -> dict[str, Any]:
    for report in agent_rows:
        if report.agent_name == agent_name and report.output_json:
            return _json_load(report.output_json, {})
    return {}


def _competition_gap_from_listings(competitor_rows: list[CompetitorListing]) -> int | None:
    if not competitor_rows:
        return None

    prices = [float(row.price) for row in competitor_rows if row.price is not None]
    photo_scores = [float(row.photo_score) for row in competitor_rows if row.photo_score is not None]
    title_scores = [float(row.title_score) for row in competitor_rows if row.title_score is not None]
    description_scores = [float(row.description_score) for row in competitor_rows if row.description_score is not None]
    sold_count = sum(1 for row in competitor_rows if row.sold)
    active_count = len(competitor_rows) - sold_count

    score = 50
    if active_count >= 10:
        score -= 15
    elif active_count >= 5:
        score -= 8
    elif active_count == 0:
        score += 8

    if sold_count > active_count:
        score += 10
    elif active_count > sold_count * 2 and active_count >= 5:
        score -= 8

    if photo_scores:
        avg_photo = sum(photo_scores) / len(photo_scores)
        if avg_photo < 60:
            score += 10
        elif avg_photo >= 80:
            score -= 8

    if title_scores:
        avg_title = sum(title_scores) / len(title_scores)
        if avg_title < 60:
            score += 8

    if description_scores:
        avg_description = sum(description_scores) / len(description_scores)
        if avg_description < 55:
            score += 6

    if prices:
        median_price = _median_or_none(prices)
        if median_price is not None:
            if median_price < 10:
                score += 4
            elif median_price > 25:
                score += 2

    return max(0, min(100, score))


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
            status=data.status or "NEW_IDEA",
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

    def archive_idea(self, idea_id: uuid.UUID) -> ProductIdea | None:
        idea = self.get_idea(idea_id)
        if not idea:
            return None
        idea.status = "ARCHIVED"
        idea.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(idea)
        return idea

    def quick_scan(self, data: ProductIdeaQuickScanRequest) -> dict[str, Any]:
        agent = QuickScanAgent()
        scan = agent.run(data.model_dump())
        template = CATEGORY_TEMPLATES.get(_norm_category(data.category), {})
        required_evidence = list(
            template.get(
                "required_evidence",
                [
                    "Add 5 sold eBay listings",
                    "Add 5 active eBay listings",
                    "Add 2 supplier sources",
                ],
            )
        )
        suggested_keywords = template.get(
            "suggested_keywords",
            {
                "ebay_sold": [],
                "ebay_active": [],
                "mercari": [],
                "supplier": [],
            },
        )
        scan_output = scan.get("output_json", {})
        verdict = scan_output.get("quick_scan_verdict", "NEEDS_MARKET_CHECK")
        research_priority = scan_output.get("research_priority", "MEDIUM")
        reason = scan_output.get("quick_scan_reason", "Quick scan completed.")
        risk_flags = scan_output.get("initial_risk_flags", [])
        score = int(scan_output.get("research_completeness_score", 0) or 0)
        suggested_keywords = scan_output.get("suggested_keywords", suggested_keywords)
        required_evidence = scan_output.get("required_next_evidence", required_evidence)

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
                status="QUICK_SCAN_COMPLETE" if verdict != "REJECT" else "REJECTED",
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
            quick_market_signal="Sold evidence is missing; keep checking the market." if verdict != "REJECT" else "Skip for now",
            quick_profit_signal="Unknown until sold evidence exists" if data.estimated_landed_cost is None else "Potentially viable only after market evidence",
            research_completeness_score=min(100, max(0, score)),
            opportunity_score=min(100, max(0, score)),
        )

        tasks = self._replace_tasks(
            idea.id,
            [
                ("market_research", "Add 5 sold eBay listings", 1),
                ("market_research", "Add 5 active eBay listings", 2),
                ("supplier_research", "Add 2 supplier sources", 3),
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
            "buy_readiness_status": "NOT_READY",
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
                description="\n".join(
                    part
                    for part in [
                        idea.why_interesting,
                        idea.notes,
                        f"Quick scan verdict: {idea.quick_scan_verdict or 'UNKNOWN'}",
                        f"Quick scan reason: {idea.quick_scan_reason or 'No quick scan reason recorded.'}",
                        f"Required evidence: {', '.join(_json_load(idea.required_next_evidence, [])) if _json_load(idea.required_next_evidence, []) else 'None'}",
                    ]
                    if part
                ),
                supplier_url=idea.source_url,
            )
        )
        discovery_context = {
            "idea_id": str(idea.id),
            "idea_name": idea.idea_name,
            "category": idea.category,
            "quick_scan_verdict": idea.quick_scan_verdict,
            "quick_scan_reason": idea.quick_scan_reason,
            "research_priority": idea.research_priority,
            "research_completeness_score": self._research_completeness_for_idea(idea),
            "opportunity_score": self._research_completeness_for_idea(idea),
            "required_next_evidence": _json_load(idea.required_next_evidence, []),
            "suggested_keywords": _json_load(idea.suggested_keywords, {}),
            "risk_flags": _json_load(idea.risk_flags, []),
        }
        self.db.add(
            AgentReport(
                product_id=product.id,
                agent_name="discovery_context",
                report_type="discovery_context",
                output_json=_json_dump(discovery_context),
                summary=idea.quick_scan_reason or "Promoted from discovery.",
                confidence="MEDIUM",
            )
        )
        idea.promoted_product_id = product.id
        idea.status = "PROMOTED_TO_PRODUCT"
        self.db.commit()
        self.db.refresh(idea)
        return product

    def update_task(self, task_id: uuid.UUID, data: DiscoveryTaskUpdate) -> DiscoveryTask | None:
        task = self.db.query(DiscoveryTask).filter(DiscoveryTask.id == task_id).first()
        if not task:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)
        idea = self.get_idea(task.idea_id)
        if idea:
            idea.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(task)
        return task

    def generate_tasks(self, idea_id: uuid.UUID) -> list[DiscoveryTask]:
        idea = self.get_idea(idea_id)
        if not idea:
            return []
        tasks = [
            ("market_research", "Add 5 sold eBay listings", 1),
            ("market_research", "Add 5 active eBay listings", 2),
            ("supplier_research", "Add 2 supplier sources", 3),
            ("competition_research", "Add 3 competitor listings", 4),
            ("research", "Confirm product weight and shipping", 5),
        ]
        return self._replace_tasks(idea.id, tasks)

    def _apply_scan_result(
        self,
        idea: ProductIdea,
        *,
        verdict: str,
        reason: str,
        priority: str,
        risk_flags: list[str],
        required_evidence: list[str],
        suggested_keywords: Any,
        quick_market_signal: str,
        quick_profit_signal: str,
        research_completeness_score: int,
        opportunity_score: int,
    ) -> None:
        if verdict == "REJECT":
            idea.status = "REJECTED"
        elif verdict == "PROMISING_FOR_RESEARCH":
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
            "buy_readiness_status": "NOT_READY",
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

    def _research_completeness_for_idea(self, idea: ProductIdea) -> int:
        tasks = self.db.query(DiscoveryTask).filter(DiscoveryTask.idea_id == idea.id).all()
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
        return min(100, research_completeness_score)

    def opportunity_board(self) -> list[dict[str, Any]]:
        from app.models.product import Product

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
                    "research_verdict": idea.quick_scan_verdict or ("PROMISING_FOR_RESEARCH" if idea.status == "PROMISING" else "NEEDS_MORE_RESEARCH"),
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
            agent_rows = self.db.query(AgentReport).filter(AgentReport.product_id == product.id).order_by(AgentReport.created_at.desc()).all()

            sold_count = sum(1 for row in evidence_rows if row.evidence_type == "SOLD_LISTING")
            active_count = sum(1 for row in evidence_rows if row.evidence_type == "ACTIVE_LISTING")
            screenshot_count = sum(1 for row in evidence_rows if row.evidence_type == "SCREENSHOT")
            manual_note_count = sum(1 for row in evidence_rows if row.evidence_type == "MANUAL_NOTE")
            sold_prices = [float(row.price) for row in evidence_rows if row.evidence_type == "SOLD_LISTING" and row.price is not None]
            active_prices = [float(row.price) for row in evidence_rows if row.evidence_type == "ACTIVE_LISTING" and row.price is not None]
            median_sold_price = _median_or_none(sold_prices)
            median_active_price = _median_or_none(active_prices)
            sold_shipping = [float(row.shipping_price) for row in evidence_rows if row.evidence_type == "SOLD_LISTING" and row.shipping_price is not None]
            active_shipping = [float(row.shipping_price) for row in evidence_rows if row.evidence_type == "ACTIVE_LISTING" and row.shipping_price is not None]
            median_sold_shipping = _median_or_none(sold_shipping)
            median_active_shipping = _median_or_none(active_shipping)
            median_shipping = _median_or_none([value for value in sold_shipping + active_shipping if value is not None])
            best_scenario = None
            if profit_rows:
                top_profit = max(profit_rows, key=lambda row: float(row.estimated_net_profit or 0))
                best_scenario = top_profit.scenario_name
            best_landed_cost = min((value for value in (_best_source_landed_cost(source) for source in sources) if value is not None), default=None)
            latest_decision_output = _latest_report_output(agent_rows, "decision_agent")
            latest_competition_output = _latest_report_output(agent_rows, "competition_agent")
            competition_gap_score = latest_competition_output.get("listing_gap_score")
            if competition_gap_score is None:
                competition_gap_score = _competition_gap_from_listings(competitor_rows)
            completeness = 0
            completeness += min(30, sold_count * 6)
            completeness += min(20, active_count * 4)
            completeness += min(10, (screenshot_count + manual_note_count) * 2)
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
                    "research_verdict": (latest_decision_output or {}).get("research_verdict") or getattr(product, "final_decision", None) or product.status,
                    "buy_readiness_status": (latest_decision_output or {}).get("buy_readiness_status") or ("READY" if product.status in {"BUY_SAMPLE", "BUY_SMALL_BATCH", "APPROVED_TO_LIST"} else "NOT_READY"),
                    "risk_level": product.risk_level,
                    "sold_evidence_count": sold_count,
                    "active_evidence_count": active_count,
                    "median_sold_price": median_sold_price,
                    "median_active_price": median_active_price,
                    "median_sold_shipping": median_sold_shipping,
                    "median_active_shipping": median_active_shipping,
                    "median_shipping": median_shipping,
                    "best_landed_cost": best_landed_cost,
                    "best_profit_scenario": best_scenario,
                    "competition_gap_score": competition_gap_score,
                    "supplier_confidence": next((source.supplier_rating for source in sources if source.supplier_rating), None),
                    "next_action": (latest_decision_output or {}).get("next_action") or getattr(product, "next_action", None) or getattr(product, "decision_reason", None),
                    "source_platform": sources[0].supplier_platform if sources else None,
                    "status": product.status,
                }
            )

        board.sort(key=lambda row: (row["research_completeness_score"], row["title"]), reverse=True)
        return board
