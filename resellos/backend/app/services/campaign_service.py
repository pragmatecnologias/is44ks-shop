from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.campaign import DiscoveryCampaign, DiscoveryCampaignTask
from app.models.external_research import EvidenceCandidate, ExternalResearchJob
from app.models.product import Product
from app.models.supplier import AgentReport, ProductIdea
from app.schemas.campaign_schema import (
    DiscoveryCampaignCreate,
    DiscoveryCampaignDetailResponse,
    DiscoveryCampaignIdeaSummary,
    DiscoveryCampaignProductSummary,
    DiscoveryCampaignReportResponse,
    DiscoveryCampaignResponse,
    DiscoveryCampaignTaskCreate,
    DiscoveryCampaignTaskResponse,
    DiscoveryCampaignTaskUpdate,
)
from app.schemas.external_research_schema import EvidenceCandidateResponse
from app.schemas.product_schema import ProductIdeaCreate
from app.services.discovery_service import DiscoveryService


def _json_load(value: Any, default: Any) -> Any:
    if value is None:
        return default
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return default
    return default


class CampaignService:
    def __init__(self, db: Session):
        self.db = db
        self.discovery = DiscoveryService(db)

    def list_campaigns(self) -> list[DiscoveryCampaign]:
        return self.db.query(DiscoveryCampaign).order_by(DiscoveryCampaign.updated_at.desc()).all()

    def get_campaign(self, campaign_id: uuid.UUID) -> DiscoveryCampaign | None:
        return self.db.query(DiscoveryCampaign).filter(DiscoveryCampaign.id == campaign_id).first()

    def create_campaign(self, data: DiscoveryCampaignCreate) -> DiscoveryCampaign:
        campaign = DiscoveryCampaign(
            name=data.name,
            category=data.category,
            goal=data.goal,
            constraints_json=data.constraints_json or {},
            budget_limit_usd=data.budget_limit_usd,
            max_ideas=data.max_ideas,
            max_products_to_promote=data.max_products_to_promote,
            status=data.status or "DRAFT",
            created_by=data.created_by,
        )
        self.db.add(campaign)
        self.db.commit()
        self.db.refresh(campaign)
        return campaign

    def update_campaign(self, campaign_id: uuid.UUID, data: dict[str, Any]) -> DiscoveryCampaign | None:
        campaign = self.get_campaign(campaign_id)
        if not campaign:
            return None
        if data.get("status") == "COMPLETED" and campaign.report_generated_at is None:
            raise HTTPException(status_code=400, detail="Campaign cannot be completed before a report exists.")
        for field, value in data.items():
            if value is not None:
                setattr(campaign, field, value)
        campaign.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(campaign)
        return campaign

    def create_task(self, campaign_id: uuid.UUID, data: DiscoveryCampaignTaskCreate) -> DiscoveryCampaignTask:
        campaign = self.get_campaign(campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Discovery campaign not found")
        task = DiscoveryCampaignTask(
            campaign_id=campaign.id,
            task_type=data.task_type,
            status=data.status,
            title=data.title,
            description=data.description,
            related_idea_id=data.related_idea_id,
            related_product_id=data.related_product_id,
            related_candidate_id=data.related_candidate_id,
            result_json=data.result_json,
            error_message=data.error_message,
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def update_task(self, campaign_id: uuid.UUID, task_id: uuid.UUID, data: DiscoveryCampaignTaskUpdate) -> DiscoveryCampaignTask | None:
        task = (
            self.db.query(DiscoveryCampaignTask)
            .filter(DiscoveryCampaignTask.id == task_id, DiscoveryCampaignTask.campaign_id == campaign_id)
            .first()
        )
        if not task:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(task, field, value)
        task.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(task)
        return task

    def add_idea_to_campaign(self, campaign_id: uuid.UUID, idea_data: ProductIdeaCreate) -> ProductIdea:
        campaign = self.get_campaign(campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Discovery campaign not found")
        if campaign.max_ideas is not None:
            idea_count = self.db.query(ProductIdea).filter(ProductIdea.campaign_id == campaign.id).count()
            if idea_count >= campaign.max_ideas:
                raise HTTPException(status_code=400, detail="Campaign idea limit reached.")
        payload = idea_data.model_dump()
        payload["campaign_id"] = campaign.id
        return self.discovery.create_idea(ProductIdeaCreate(**payload))

    def _campaign_ideas(self, campaign_id: uuid.UUID) -> list[ProductIdea]:
        return self.db.query(ProductIdea).filter(ProductIdea.campaign_id == campaign_id).order_by(ProductIdea.updated_at.desc()).all()

    def _campaign_products(self, campaign_id: uuid.UUID) -> list[Product]:
        idea_ids = [idea.promoted_product_id for idea in self._campaign_ideas(campaign_id) if idea.promoted_product_id]
        if not idea_ids:
            return []
        return self.db.query(Product).filter(Product.id.in_(idea_ids)).order_by(Product.updated_at.desc()).all()

    def _campaign_jobs(self, campaign_id: uuid.UUID) -> list[ExternalResearchJob]:
        return self.db.query(ExternalResearchJob).filter(ExternalResearchJob.campaign_id == campaign_id).all()

    def _campaign_candidates(self, campaign_id: uuid.UUID) -> list[EvidenceCandidate]:
        return self.db.query(EvidenceCandidate).filter(EvidenceCandidate.campaign_id == campaign_id).all()

    def _latest_agent_output(self, agent_rows: list[AgentReport], agent_name: str) -> dict[str, Any]:
        for report in agent_rows:
            if report.agent_name == agent_name and report.output_json:
                return _json_load(report.output_json, {})
        return {}

    def _serialize_campaign(self, campaign: DiscoveryCampaign) -> dict[str, Any]:
        ideas = self._campaign_ideas(campaign.id)
        jobs = self._campaign_jobs(campaign.id)
        promoted_products = [idea for idea in ideas if idea.promoted_product_id]
        rejected_ideas = sum(1 for idea in ideas if (idea.quick_scan_verdict or "").upper() == "REJECT" or (idea.status or "").upper() == "REJECTED")
        promising_ideas = sum(1 for idea in ideas if (idea.quick_scan_verdict or "").upper() == "PROMISING_FOR_RESEARCH")
        spend_estimate = round(sum(float(job.cost_estimate or 0) for job in jobs), 4)
        return {
            "id": str(campaign.id),
            "name": campaign.name,
            "category": campaign.category,
            "goal": campaign.goal,
            "constraints_json": _json_load(campaign.constraints_json, {}),
            "budget_limit_usd": float(campaign.budget_limit_usd) if campaign.budget_limit_usd is not None else 0.0,
            "max_ideas": int(campaign.max_ideas or 0),
            "max_products_to_promote": int(campaign.max_products_to_promote or 0),
            "status": campaign.status,
            "created_by": campaign.created_by,
            "created_at": campaign.created_at,
            "updated_at": campaign.updated_at,
            "idea_count": len(ideas),
            "rejected_idea_count": rejected_ideas,
            "promising_idea_count": promising_ideas,
            "promoted_product_count": len(promoted_products),
            "dataforseo_spend_estimate": spend_estimate,
            "report_generated_at": campaign.report_generated_at,
        }

    def _serialize_task(self, task: DiscoveryCampaignTask) -> dict[str, Any]:
        return {
            "id": str(task.id),
            "campaign_id": str(task.campaign_id),
            "task_type": task.task_type,
            "status": task.status,
            "title": task.title,
            "description": task.description,
            "related_idea_id": str(task.related_idea_id) if task.related_idea_id else None,
            "related_product_id": str(task.related_product_id) if task.related_product_id else None,
            "related_candidate_id": str(task.related_candidate_id) if task.related_candidate_id else None,
            "result_json": _json_load(task.result_json, {}),
            "error_message": task.error_message,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
        }

    def _serialize_product(self, product: Product, *, research_score: int = 0, opportunity_score: int = 0) -> dict[str, Any]:
        agent_rows = self.db.query(AgentReport).filter(AgentReport.product_id == product.id).order_by(AgentReport.created_at.desc()).all()
        decision = self._latest_agent_output(agent_rows, "decision_agent")
        market = self._latest_agent_output(agent_rows, "market_agent")
        research_score = int(decision.get("research_completeness_score") or market.get("research_completeness_score") or research_score or 0)
        opportunity_score = int(decision.get("opportunity_score") or market.get("opportunity_score") or opportunity_score or 0)
        required_before_buying = decision.get("required_before_buying")
        if isinstance(required_before_buying, list):
            next_action = required_before_buying[0] if required_before_buying else None
        elif isinstance(required_before_buying, str):
            next_action = required_before_buying
        else:
            next_action = None
        return {
            "id": str(product.id),
            "name": product.name,
            "category": product.category,
            "status": product.status,
            "research_verdict": decision.get("research_verdict") or product.final_decision,
            "buy_readiness_status": decision.get("buy_readiness_status"),
            "final_decision": product.final_decision,
            "research_completeness_score": research_score,
            "opportunity_score": opportunity_score,
            "next_action": decision.get("next_action") or next_action,
            "main_blocker": decision.get("main_blocker"),
        }

    def _next_action_for_idea(self, idea_payload: dict[str, Any]) -> str:
        idea_name = str(idea_payload.get("idea_name") or "idea")
        verdict = str(idea_payload.get("quick_scan_verdict") or "").upper()
        if idea_payload.get("promoted_product_id"):
            return f"Review product cockpit for {idea_name}."
        if verdict == "REJECT":
            return f"Skip {idea_name} unless new evidence appears."
        if verdict == "PROMISING_FOR_RESEARCH":
            return f"Collect verified evidence for {idea_name} before promotion."
        if verdict == "NEEDS_MARKET_CHECK":
            return f"Run market presence research for {idea_name} before promotion."
        if verdict == "NEEDS_SUPPLIER_CHECK":
            return f"Collect supplier evidence for {idea_name} before promotion."
        return f"Run quick scan for {idea_name}."

    def _build_report(self, campaign: DiscoveryCampaign) -> dict[str, Any]:
        ideas = self._campaign_ideas(campaign.id)
        products = self._campaign_products(campaign.id)
        jobs = self._campaign_jobs(campaign.id)
        candidates = self._campaign_candidates(campaign.id)
        total_ideas = len(ideas)
        rejected_ideas = sum(1 for idea in ideas if (idea.quick_scan_verdict or "").upper() == "REJECT" or (idea.status or "").upper() == "REJECTED")
        promising_ideas = sum(1 for idea in ideas if (idea.quick_scan_verdict or "").upper() == "PROMISING_FOR_RESEARCH")
        promoted_products = len(products)
        spend_estimate = round(sum(float(job.cost_estimate or 0) for job in jobs), 4)
        budget_limit = float(campaign.budget_limit_usd or 0)
        spend_remaining = round(max(0.0, budget_limit - spend_estimate), 4) if budget_limit else None
        budget_used_percent = round(min(100.0, (spend_estimate / budget_limit) * 100), 2) if budget_limit else 0.0

        ideas_by_verdict: dict[str, int] = {}
        for idea in ideas:
            verdict = str(idea.quick_scan_verdict or "UNSCANNED").upper()
            ideas_by_verdict[verdict] = ideas_by_verdict.get(verdict, 0) + 1

        products_by_decision: dict[str, int] = {}
        watchlist_products: list[dict[str, Any]] = []
        skip_products: list[dict[str, Any]] = []
        ready_for_sample_products: list[dict[str, Any]] = []
        for product in products:
            product_payload = self._serialize_product(product)
            decision = str(product_payload.get("final_decision") or product_payload.get("research_verdict") or "UNKNOWN").upper()
            products_by_decision[decision] = products_by_decision.get(decision, 0) + 1
            if decision == "WATCHLIST":
                watchlist_products.append(product_payload)
            elif decision in {"SKIP", "REJECT"}:
                skip_products.append(product_payload)
            elif str(product_payload.get("buy_readiness_status") or "").upper() == "READY" or decision == "READY_FOR_SAMPLE":
                ready_for_sample_products.append(product_payload)

        candidate_count_by_status: dict[str, int] = {}
        for candidate in candidates:
            status = str(candidate.review_status or "PENDING").upper()
            candidate_count_by_status[status] = candidate_count_by_status.get(status, 0) + 1

        idea_payloads = [self.discovery._serialize_idea(idea) for idea in ideas]
        idea_payloads.sort(
            key=lambda payload: (
                int(payload.get("opportunity_score") or 0),
                int(payload.get("research_completeness_score") or 0),
                1 if str(payload.get("quick_scan_verdict") or "").upper() == "PROMISING_FOR_RESEARCH" else 0,
                1 if payload.get("promoted_product_id") else 0,
            ),
            reverse=True,
        )
        idea_summaries = idea_payloads[: min(5, len(idea_payloads))]

        product_summaries: list[dict[str, Any]] = []
        for product in products[: min(5, len(products))]:
            agent_rows = self.db.query(AgentReport).filter(AgentReport.product_id == product.id).order_by(AgentReport.created_at.desc()).all()
            decision = self._latest_agent_output(agent_rows, "decision_agent")
            market = self._latest_agent_output(agent_rows, "market_agent")
            research_score = int(decision.get("research_completeness_score") or market.get("research_completeness_score") or 0)
            opportunity_score = int(decision.get("opportunity_score") or market.get("opportunity_score") or 0)
            product_summaries.append(
                {
                    "id": str(product.id),
                    "name": product.name,
                    "category": product.category,
                    "status": product.status,
                    "research_verdict": decision.get("research_verdict") or product.final_decision,
                    "buy_readiness_status": decision.get("buy_readiness_status"),
                    "final_decision": product.final_decision,
                    "research_completeness_score": research_score,
                    "opportunity_score": opportunity_score,
                    "next_action": decision.get("next_action"),
                    "main_blocker": decision.get("main_blocker"),
                }
            )

        next_actions: list[str] = []
        if ideas:
            for idea in idea_payloads[:3]:
                next_actions.append(self._next_action_for_idea(idea))
        else:
            next_actions.append("Create discovery ideas for this campaign.")
        if spend_estimate > 0 and spend_estimate < float(campaign.budget_limit_usd or 0):
            next_actions.append("Review DataForSEO candidates and keep budget within limits.")
        next_best_task = next_actions[0] if next_actions else None

        return {
            "campaign_id": str(campaign.id),
            "total_ideas": total_ideas,
            "rejected_ideas": rejected_ideas,
            "promising_ideas": promising_ideas,
            "promoted_products": promoted_products,
            "dataforseo_spend_estimate": spend_estimate,
            "budget_limit_usd": budget_limit,
            "spend_remaining": spend_remaining,
            "budget_used_percent": budget_used_percent,
            "ideas_by_verdict": ideas_by_verdict,
            "products_by_decision": products_by_decision,
            "watchlist_products": watchlist_products,
            "skip_products": skip_products,
            "ready_for_sample_products": ready_for_sample_products,
            "candidate_count_by_status": candidate_count_by_status,
            "next_best_task": next_best_task,
            "top_ranked_ideas": idea_summaries,
            "top_products": product_summaries,
            "next_actions": next_actions,
        }

    def get_report(self, campaign_id: uuid.UUID, persist: bool = True) -> DiscoveryCampaignReportResponse:
        campaign = self.get_campaign(campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Discovery campaign not found")
        report = self._build_report(campaign)
        if persist:
            campaign.latest_report_json = json.loads(json.dumps(report, default=str))
            campaign.report_generated_at = datetime.utcnow()
            campaign.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(campaign)
        return DiscoveryCampaignReportResponse.model_validate(report)

    def get_detail(self, campaign_id: uuid.UUID) -> DiscoveryCampaignDetailResponse:
        campaign = self.get_campaign(campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Discovery campaign not found")
        ideas = self._campaign_ideas(campaign.id)
        tasks = self.db.query(DiscoveryCampaignTask).filter(DiscoveryCampaignTask.campaign_id == campaign.id).order_by(DiscoveryCampaignTask.created_at.desc()).all()
        products = self._campaign_products(campaign.id)
        candidates = self._campaign_candidates(campaign.id)
        report = self.get_report(campaign.id, persist=False)
        tasks_by_status: dict[str, int] = {}
        for task in tasks:
            tasks_by_status[task.status] = tasks_by_status.get(task.status, 0) + 1
        return DiscoveryCampaignDetailResponse(
            campaign=DiscoveryCampaignResponse.model_validate(self._serialize_campaign(campaign)),
            ideas=[DiscoveryCampaignIdeaSummary.model_validate(self.discovery._serialize_idea(idea)) for idea in ideas],
            tasks=[DiscoveryCampaignTaskResponse.model_validate(self._serialize_task(task)) for task in tasks],
            report=report,
            products=[DiscoveryCampaignProductSummary.model_validate(self._serialize_product(product)) for product in products],
            evidence_candidates=[EvidenceCandidateResponse.model_validate({
                "id": candidate.id,
                "job_id": candidate.job_id,
                "idea_id": candidate.idea_id,
                "product_id": candidate.product_id,
                "campaign_id": candidate.campaign_id,
                "source": candidate.source,
                "candidate_type": candidate.candidate_type,
                "marketplace": candidate.marketplace,
                "evidence_type": candidate.evidence_type,
                "title": candidate.title,
                "url": candidate.url,
                "price": float(candidate.price) if candidate.price is not None else None,
                "shipping_price": float(candidate.shipping_price) if candidate.shipping_price is not None else None,
                "seller": candidate.seller,
                "rating": float(candidate.rating) if candidate.rating is not None else None,
                "review_count": candidate.review_count,
                "image_url": candidate.image_url,
                "confidence": candidate.confidence,
                "review_status": candidate.review_status,
                "raw_json": _json_load(candidate.raw_json, {}),
                "created_at": candidate.created_at,
            }) for candidate in candidates],
            tasks_by_status=tasks_by_status,
        )

    def generate_next_tasks(self, campaign_id: uuid.UUID) -> list[DiscoveryCampaignTask]:
        campaign = self.get_campaign(campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Discovery campaign not found")

        ideas = self._campaign_ideas(campaign.id)
        products = self._campaign_products(campaign.id)
        report = self._build_report(campaign)
        desired_tasks: list[dict[str, Any]] = []
        existing_keys = {
            (task.task_type, task.title.strip().lower())
            for task in self.db.query(DiscoveryCampaignTask).filter(DiscoveryCampaignTask.campaign_id == campaign.id).all()
        }

        if not ideas:
            desired_tasks.append(
                {
                    "task_type": "IDEA_SCOUTING",
                    "title": "Create initial discovery ideas",
                    "description": "Add a first batch of product ideas for the campaign.",
                }
            )
        elif any((idea.quick_scan_verdict or "").upper() == "" for idea in ideas):
            desired_tasks.append(
                {
                    "task_type": "QUICK_SCAN",
                    "title": "Quick-scan unreviewed ideas",
                    "description": "Run quick scans on the newest ideas so they can be ranked.",
                }
            )
        elif any((idea.quick_scan_verdict or "").upper() == "PROMISING_FOR_RESEARCH" and not idea.promoted_product_id for idea in ideas) and len(products) < int(campaign.max_products_to_promote or 0):
            desired_tasks.append(
                {
                    "task_type": "PROMOTE",
                    "title": "Promote the strongest idea",
                    "description": "Move the highest-ranking promising idea into product research.",
                }
            )

        if float(report.get("dataforseo_spend_estimate") or 0) == 0 and ideas:
            desired_tasks.append(
                {
                    "task_type": "EXTERNAL_RESEARCH",
                    "title": "Run one controlled DataForSEO query",
                    "description": "Use a single low-cost Google Shopping query for the most promising idea.",
                }
            )

        if campaign.report_generated_at is None:
            desired_tasks.append(
                {
                    "task_type": "REPORT",
                    "title": "Generate the campaign report",
                    "description": "Persist the latest ranked report before any completion decision.",
                }
            )

        created: list[DiscoveryCampaignTask] = []
        for payload in desired_tasks:
            key = (payload["task_type"], payload["title"].strip().lower())
            if key in existing_keys:
                continue
            task = DiscoveryCampaignTask(
                campaign_id=campaign.id,
                task_type=payload["task_type"],
                title=payload["title"],
                description=payload.get("description"),
                status="TODO",
            )
            self.db.add(task)
            created.append(task)
        if created:
            self.db.commit()
            for task in created:
                self.db.refresh(task)
        return created
