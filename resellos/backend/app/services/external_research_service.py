from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta
from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.connectors.dataforseo import DataForSEOClient, DataForSEOMerchantClient
from app.connectors.dataforseo.mappers import iter_google_shopping_items, map_google_shopping_item_to_candidate
from app.models.external_research import EvidenceCandidate, ExternalResearchJob
from app.models.product import Product
from app.models.supplier import ProductIdea
from app.schemas.external_research_schema import ExternalResearchJobResponse, ExternalResearchRunRequest, ExternalResearchRunResponse


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


def _json_dump(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, default=str)


class ExternalResearchService:
    def __init__(self, db: Session):
        self.db = db
        self._dataforseo_client: DataForSEOMerchantClient | None = None

    @property
    def client(self) -> DataForSEOMerchantClient:
        if self._dataforseo_client is None:
            client = DataForSEOClient(
                login=settings.DATAFORSEO_LOGIN,
                password=settings.DATAFORSEO_PASSWORD,
            )
            self._dataforseo_client = DataForSEOMerchantClient(client)
        return self._dataforseo_client

    def _require_enabled(self) -> None:
        if not settings.DATAFORSEO_ENABLED:
            raise HTTPException(status_code=503, detail="DataForSEO is disabled in configuration.")

    def _normalize_queries(self, queries: list[str] | None, fallback: list[str] | None = None) -> list[str]:
        values = [query.strip() for query in (queries or []) if query and query.strip()]
        if not values and fallback:
            values = [query.strip() for query in fallback if query and query.strip()]
        deduped: list[str] = []
        for query in values:
            if query not in deduped:
                deduped.append(query)
        return deduped

    def _estimate_cost(self, queries_count: int, max_results: int) -> float:
        return round(float(queries_count * max_results * 0.001), 4)

    def _recent_spend(self) -> float:
        cutoff = datetime.utcnow() - timedelta(days=30)
        jobs = (
            self.db.query(ExternalResearchJob)
            .filter(ExternalResearchJob.created_at >= cutoff)
            .all()
        )
        return round(sum(float(job.cost_estimate or 0) for job in jobs), 4)

    def _cache_cutoff(self) -> datetime:
        return datetime.utcnow() - timedelta(days=settings.DATAFORSEO_CACHE_DAYS)

    def _find_cached_job(
        self,
        *,
        idea_id: uuid.UUID | None,
        product_id: uuid.UUID | None,
        query: str,
    ) -> ExternalResearchJob | None:
        cutoff = self._cache_cutoff()
        query_obj = self.db.query(ExternalResearchJob).filter(
            ExternalResearchJob.provider == "DATAFORSEO",
            ExternalResearchJob.api_area == "MERCHANT_GOOGLE_PRODUCTS",
            ExternalResearchJob.query == query,
            ExternalResearchJob.created_at >= cutoff,
            ExternalResearchJob.status != "FAILED",
        )
        if idea_id is not None:
            query_obj = query_obj.filter(ExternalResearchJob.idea_id == idea_id)
        if product_id is not None:
            query_obj = query_obj.filter(ExternalResearchJob.product_id == product_id)
        return query_obj.order_by(ExternalResearchJob.created_at.desc()).first()

    def _get_idea(self, idea_id: uuid.UUID) -> ProductIdea | None:
        return self.db.query(ProductIdea).filter(ProductIdea.id == idea_id).first()

    def _serialize_job(self, job: ExternalResearchJob) -> dict[str, Any]:
        return {
            "id": job.id,
            "idea_id": job.idea_id,
            "product_id": job.product_id,
            "provider": job.provider,
            "api_area": job.api_area,
            "query": job.query,
            "queue": job.queue,
            "status": job.status,
            "provider_task_id": job.provider_task_id,
            "cost_estimate": float(job.cost_estimate) if job.cost_estimate is not None else None,
            "result_count": int(job.result_count or 0),
            "raw_request": _json_load(job.raw_request, {}),
            "raw_response": _json_load(job.raw_response, {}),
            "last_error": job.last_error,
            "candidate_count": len(job.candidates),
            "created_at": job.created_at or datetime.utcnow(),
            "updated_at": job.updated_at or datetime.utcnow(),
        }

    def _serialize_candidate(self, candidate: EvidenceCandidate) -> dict[str, Any]:
        return {
            "id": candidate.id,
            "job_id": candidate.job_id,
            "idea_id": candidate.idea_id,
            "product_id": candidate.product_id,
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
            "created_at": candidate.created_at or datetime.utcnow(),
        }

    def _submit_query_job(
        self,
        *,
        idea_id: uuid.UUID | None,
        product_id: uuid.UUID | None,
        query: str,
        max_results: int,
        queue: str,
        budget_override: bool = False,
    ) -> ExternalResearchJob:
        if queue != "standard":
            raise HTTPException(status_code=400, detail="Only standard queue is allowed for this workflow.")

        cached = self._find_cached_job(idea_id=idea_id, product_id=product_id, query=query)
        if cached:
            return cached

        if not budget_override and self._recent_spend() + self._estimate_cost(1, max_results) > settings.DATAFORSEO_MONTHLY_BUDGET_USD:
            raise HTTPException(status_code=400, detail="DataForSEO monthly hard stop reached.")

        job = ExternalResearchJob(
            idea_id=idea_id,
            product_id=product_id,
            provider="DATAFORSEO",
            api_area="MERCHANT_GOOGLE_PRODUCTS",
            query=query,
            queue="standard",
            status="QUEUED",
            cost_estimate=self._estimate_cost(1, max_results),
            raw_request={"query": query, "max_results": max_results, "queue": queue},
        )
        self.db.add(job)
        self.db.flush()

        response = self.client.submit_google_shopping_products_task(
            keyword=query,
            location_code=settings.DATAFORSEO_LOCATION_CODE,
            language_code=settings.DATAFORSEO_LANGUAGE_CODE,
            priority=1,
            tag=str(job.id),
        )
        job.raw_response = response
        job.status = "SUBMITTED"

        tasks = response.get("tasks") or []
        if tasks:
            task = tasks[0]
            job.provider_task_id = str(task.get("id") or task.get("task_id") or task.get("result", [{}])[0].get("id") or job.id)

        self.db.commit()
        self.db.refresh(job)
        return job

    def run_google_shopping_for_idea(self, request: ExternalResearchRunRequest) -> ExternalResearchRunResponse:
        self._require_enabled()
        if not request.idea_id:
            raise HTTPException(status_code=400, detail="idea_id is required for idea research.")
        idea = self._get_idea(request.idea_id)
        if not idea:
            raise HTTPException(status_code=404, detail="Discovery idea not found")
        if (idea.status or "").upper() == "REJECTED" or (idea.quick_scan_verdict or "").upper() == "REJECT":
            raise HTTPException(status_code=400, detail="Rejected ideas cannot be sent to external research.")
        queries = self._normalize_queries(
            request.queries,
            fallback=[
                idea.idea_name,
                *(self._keyword_fallbacks(idea.suggested_keywords)[:2]),
            ],
        )
        if not queries:
            raise HTTPException(status_code=400, detail="At least one query is required.")
        if request.queries and len(queries) > settings.DATAFORSEO_MAX_QUERIES_PER_IDEA:
            raise HTTPException(status_code=400, detail=f"Maximum {settings.DATAFORSEO_MAX_QUERIES_PER_IDEA} queries per idea.")
        if not request.queries:
            queries = queries[: settings.DATAFORSEO_MAX_QUERIES_PER_IDEA]
        max_results = min(max(1, request.max_results), settings.DATAFORSEO_MAX_RESULTS_PER_QUERY)

        estimated_cost = self._estimate_cost(len(queries), max_results)
        budget_warning = None
        spend_after = self._recent_spend() + estimated_cost
        warning_threshold = min(20.0, settings.DATAFORSEO_MONTHLY_BUDGET_USD)
        if not request.budget_override and spend_after > settings.DATAFORSEO_MONTHLY_BUDGET_USD:
            raise HTTPException(status_code=400, detail="DataForSEO monthly hard stop reached.")
        if spend_after > warning_threshold:
            budget_warning = "Estimated monthly spend is approaching the warning threshold."

        jobs = [
            self._submit_query_job(
                idea_id=request.idea_id,
                product_id=request.product_id,
                query=query,
                max_results=max_results,
                queue=request.queue,
                budget_override=request.budget_override,
            )
            for query in queries
        ]

        return ExternalResearchRunResponse(
            jobs=[ExternalResearchJobResponse.model_validate(self._serialize_job(job)) for job in jobs],
            estimated_cost=estimated_cost,
            budget_warning=budget_warning,
        )

    def run_google_shopping_for_product(self, request: ExternalResearchRunRequest) -> ExternalResearchRunResponse:
        self._require_enabled()
        if not request.product_id:
            raise HTTPException(status_code=400, detail="product_id is required for product research.")
        product = self.db.query(Product).filter(Product.id == request.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        queries = self._normalize_queries(request.queries, fallback=[product.name])
        if request.queries and len(queries) > settings.DATAFORSEO_MAX_QUERIES_PER_IDEA:
            raise HTTPException(status_code=400, detail=f"Maximum {settings.DATAFORSEO_MAX_QUERIES_PER_IDEA} queries per idea.")
        if not request.queries:
            queries = queries[: settings.DATAFORSEO_MAX_QUERIES_PER_IDEA]
        if not queries:
            raise HTTPException(status_code=400, detail="At least one query is required.")
        max_results = min(max(1, request.max_results), settings.DATAFORSEO_MAX_RESULTS_PER_QUERY)
        estimated_cost = self._estimate_cost(len(queries), max_results)
        budget_warning = None
        spend_after = self._recent_spend() + estimated_cost
        warning_threshold = min(20.0, settings.DATAFORSEO_MONTHLY_BUDGET_USD)
        if not request.budget_override and spend_after > settings.DATAFORSEO_MONTHLY_BUDGET_USD:
            raise HTTPException(status_code=400, detail="DataForSEO monthly hard stop reached.")
        if spend_after > warning_threshold:
            budget_warning = "Estimated monthly spend is approaching the warning threshold."

        jobs = [
            self._submit_query_job(
                idea_id=request.idea_id,
                product_id=request.product_id,
                query=query,
                max_results=max_results,
                queue=request.queue,
                budget_override=request.budget_override,
            )
            for query in queries
        ]
        return ExternalResearchRunResponse(
            jobs=[ExternalResearchJobResponse.model_validate(self._serialize_job(job)) for job in jobs],
            estimated_cost=estimated_cost,
            budget_warning=budget_warning,
        )

    def list_jobs(
        self,
        *,
        idea_id: uuid.UUID | None = None,
        product_id: uuid.UUID | None = None,
        status: str | None = None,
    ) -> list[ExternalResearchJob]:
        query = self.db.query(ExternalResearchJob)
        if idea_id is not None:
            query = query.filter(ExternalResearchJob.idea_id == idea_id)
        if product_id is not None:
            query = query.filter(ExternalResearchJob.product_id == product_id)
        if status:
            query = query.filter(ExternalResearchJob.status == status)
        return query.order_by(ExternalResearchJob.created_at.desc()).all()

    def get_job(self, job_id: uuid.UUID) -> ExternalResearchJob | None:
        return self.db.query(ExternalResearchJob).filter(ExternalResearchJob.id == job_id).first()

    def poll_job(self, job_id: uuid.UUID) -> ExternalResearchJob:
        self._require_enabled()
        job = self.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="External research job not found")
        if job.status == "IMPORTED":
            return job
        if not job.provider_task_id:
            raise HTTPException(status_code=400, detail="Job has not been submitted to DataForSEO yet.")

        response = self.client.get_google_shopping_products_result(job.provider_task_id)
        job.raw_response = response
        job.status = "READY"
        candidates = self.create_candidates_from_job(job, response)
        job.result_count = len(candidates)
        job.status = "IMPORTED"
        self.db.commit()
        self.db.refresh(job)
        return job

    def create_candidates_from_job(self, job: ExternalResearchJob, response: dict[str, Any]) -> list[EvidenceCandidate]:
        if job.candidates:
            return list(job.candidates)
        candidates: list[EvidenceCandidate] = []
        item_sources = list(iter_google_shopping_items(response))
        for item in item_sources:
            candidate_payload = map_google_shopping_item_to_candidate(item, source_job={"job_id": str(job.id), "query": job.query})
            raw_json = {
                "job": {
                    "id": str(job.id),
                    "query": job.query,
                    "provider_task_id": job.provider_task_id,
                },
                "item": item,
            }
            candidate = EvidenceCandidate(
                job_id=job.id,
                idea_id=job.idea_id,
                product_id=job.product_id,
                source=candidate_payload["source"],
                candidate_type=candidate_payload["candidate_type"],
                marketplace=candidate_payload["marketplace"],
                evidence_type=candidate_payload["evidence_type"],
                title=candidate_payload["title"],
                url=candidate_payload["url"],
                price=candidate_payload["price"],
                shipping_price=candidate_payload["shipping_price"],
                seller=candidate_payload["seller"],
                rating=candidate_payload["rating"],
                review_count=candidate_payload["review_count"],
                image_url=candidate_payload["image_url"],
                confidence=candidate_payload["confidence"],
                review_status="PENDING",
                raw_json=raw_json,
            )
            self.db.add(candidate)
            candidates.append(candidate)
        self.db.flush()
        return candidates

    def _keyword_fallbacks(self, suggested_keywords: Any) -> list[str]:
        if isinstance(suggested_keywords, dict):
            values: list[str] = []
            for key in ("ebay_sold", "ebay_active", "mercari", "supplier"):
                group = suggested_keywords.get(key)
                if isinstance(group, list):
                    values.extend([str(value) for value in group if value])
            return values
        if isinstance(suggested_keywords, list):
            return [str(value) for value in suggested_keywords if value]
        if isinstance(suggested_keywords, str):
            try:
                parsed = json.loads(suggested_keywords)
                return self._keyword_fallbacks(parsed)
            except Exception:
                return [suggested_keywords]
        return []
