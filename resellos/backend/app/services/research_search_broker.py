from __future__ import annotations

import logging
import urllib.parse
import uuid
from datetime import datetime
from typing import Any

import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.models.research_search import ResearchSearchResult
from app.schemas.research_search_schema import (
    ConvertSearchResultToCandidateRequest,
    ConvertSearchResultToCandidateResponse,
    ProviderStatus,
    ResearchSearchRequest,
    ResearchSearchResponse,
    ResearchSearchResultResponse,
    SearchIntent,
    SearchProvider,
)

logger = logging.getLogger(__name__)

# Keys to strip from URL query strings (tracking params)
_TRACKING_QUERY_KEYS = frozenset({
    "utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term",
    "fbclid", "gclid", "msclkid", "ref", "affiliate", "partner", "source",
    "campaign", "adid", "creative_id", "placement", "matchtype", "device",
    "cadillac_id",
})


def _normalize_url(raw_url: str) -> str:
    """
    Normalize URL for deduplication:
    - Strip scheme and leading www
    - Strip tracking query params (utm_*, fbclid, etc.)
    - Strip fragment
    - Lowercase
    - Strip trailing slash
    """
    if not raw_url:
        return ""
    # Strip fragment
    url = raw_url.split("#")[0]
    # Strip scheme and www
    url = url.lower()
    url = url.replace("https://", "").replace("http://", "")
    url = url.replace("www.", "")
    # Parse query string and filter tracking params
    if "?" in url:
        path_part, query_part = url.split("?", 1)
        parsed_qs = urllib.parse.parse_qsl(query_part, keep_blank_values=True)
        cleaned_qs = [(k, v) for k, v in parsed_qs if k not in _TRACKING_QUERY_KEYS]
        query_part = urllib.parse.urlencode(cleaned_qs)
        if query_part:
            url = f"{path_part}?{query_part}"
        else:
            url = path_part
    # Strip trailing slash
    url = url.rstrip("/")
    return url


def _extract_domain(url: str) -> str | None:
    try:
        if url.startswith("http"):
            parts = url.split("/")
            return parts[2] if len(parts) > 2 else None
        return url.split("/")[0] if url else None
    except Exception:
        return None


class NormalizedSearchResult:
    def __init__(
        self,
        title: str | None,
        url: str,
        snippet: str | None,
        provider: SearchProvider,
        rank: int,
        price_text: str | None = None,
        currency: str | None = None,
        raw_json: dict[str, Any] | None = None,
    ):
        self.title = title
        self.url = url
        self.snippet = snippet
        self.provider = provider
        self.rank = rank
        self.price_text = price_text
        self.currency = currency
        self.raw_json = raw_json or {}
        self.normalized_url = _normalize_url(url)


# Types that can be converted to actual evidence candidates
SUPPORTED_CANDIDATE_TYPES = {"SOLD_LISTING", "ACTIVE_LISTING", "SUPPLIER_SOURCE", "COMPETITOR_LISTING"}


class ResearchSearchBroker:
    def __init__(self, db: Session):
        self.db = db
        self.request_timeout = getattr(settings, "LOCAL_SEARCH_REQUEST_TIMEOUT_SECONDS", 15)
        self.searxng_base = getattr(settings, "SEARXNG_BASE_URL", "http://localhost:8888")
        self.openserp_base = getattr(settings, "OPENSERP_BASE_URL", "http://localhost:7000")
        self.enable_searxng = getattr(settings, "ENABLE_SEARXNG_PROVIDER", True)
        self.enable_openserp = getattr(settings, "ENABLE_OPENSERP_PROVIDER", True)
        self.enable_playwright = getattr(settings, "ENABLE_PLAYWRIGHT_CAPTURE", False)

    def search(self, request: ResearchSearchRequest) -> ResearchSearchResponse:
        providers_to_call = [p for p in request.providers if self._is_provider_enabled(p)]
        if not providers_to_call:
            providers_to_call = ["SEARXNG", "OPENSERP"]

        all_results: list[NormalizedSearchResult] = []
        provider_statuses: list[ProviderStatus] = []

        for provider in providers_to_call:
            results, status = self._call_provider(provider, request.query, request.max_results)
            all_results.extend(results)
            provider_statuses.append(status)

        raw_count = len(all_results)
        deduped = self._dedupe_results(all_results)
        unique_count = len(deduped)
        deduped_count = raw_count - unique_count

        stored = 0
        if request.store_results:
            stored = self._store_results(deduped, request)

        response_results = [
            ResearchSearchResultResponse(
                id=r.id if hasattr(r, "id") else uuid.uuid4(),
                query=request.query,
                provider=r.provider,
                intent=request.intent,
                title=r.title,
                url=r.url,
                snippet=r.snippet,
                source_domain=_extract_domain(r.url),
                rank=r.rank,
                price_text=r.price_text,
                currency=r.currency,
                fetched_at=datetime.utcnow(),
                product_id=request.product_id,
                idea_id=request.idea_id,
                campaign_id=request.campaign_id,
                conversion_status="NOT_CONVERTED",
            )
            for r in deduped[: request.max_results]
        ]

        return ResearchSearchResponse(
            query=request.query,
            intent=request.intent,
            requested_providers=request.providers,
            provider_statuses=provider_statuses,
            result_count=unique_count,
            stored_count=stored,
            deduped_count=deduped_count,
            results=response_results,
        )

    def _is_provider_enabled(self, provider: SearchProvider) -> bool:
        if provider == "SEARXNG":
            return self.enable_searxng
        if provider == "OPENSERP":
            return self.enable_openserp
        if provider == "PLAYWRIGHT":
            return self.enable_playwright
        return True

    def _call_provider(
        self, provider: SearchProvider, query: str, max_results: int
    ) -> tuple[list[NormalizedSearchResult], ProviderStatus]:
        if provider == "SEARXNG":
            return self.search_searxng(query, max_results)
        elif provider == "OPENSERP":
            return self.search_openserp(query, max_results)
        elif provider == "PLAYWRIGHT":
            return self.search_playwright(query, "GENERAL_RESEARCH")
        else:
            return [], ProviderStatus(provider=provider, status="DISABLED", message="Unknown provider", result_count=0)

    def search_searxng(self, query: str, max_results: int) -> tuple[list[NormalizedSearchResult], ProviderStatus]:
        try:
            with httpx.Client(timeout=self.request_timeout) as client:
                response = client.get(
                    f"{self.searxng_base}/search",
                    params={"q": query, "format": "json"},
                )
                response.raise_for_status()
                data = response.json()

            results: list[NormalizedSearchResult] = []
            raw_results = data.get("results", [])[:max_results]
            for rank, item in enumerate(raw_results, start=1):
                results.append(
                    NormalizedSearchResult(
                        title=item.get("title"),
                        url=item.get("url", ""),
                        snippet=item.get("content", item.get("snippet")),
                        provider="SEARXNG",
                        rank=rank,
                        raw_json={"engine": item.get("engine"), "raw": item},
                    )
                )
            return results, ProviderStatus(provider="SEARXNG", status="OK", result_count=len(results))
        except httpx.TimeoutException:
            logger.warning("SearXNG timeout for query: %s", query)
            return [], ProviderStatus(provider="SEARXNG", status="TIMEOUT", message="Request timed out", result_count=0)
        except Exception as exc:
            logger.warning("SearXNG error for query %s: %s", query, exc)
            return [], ProviderStatus(provider="SEARXNG", status="ERROR", message=str(exc), result_count=0)

    def search_openserp(self, query: str, max_results: int) -> tuple[list[NormalizedSearchResult], ProviderStatus]:
        try:
            with httpx.Client(timeout=self.request_timeout) as client:
                response = client.get(
                    f"{self.openserp_base}/search",
                    params={"q": query, "limit": max_results},
                )
                response.raise_for_status()
                data = response.json()

            results: list[NormalizedSearchResult] = []
            items = data if isinstance(data, list) else data.get("results", data.get("items", []))
            for rank, item in enumerate(items[:max_results], start=1):
                if isinstance(item, dict):
                    results.append(
                        NormalizedSearchResult(
                            title=item.get("title"),
                            url=item.get("url", item.get("link", "")),
                            snippet=item.get("snippet", item.get("description")),
                            provider="OPENSERP",
                            rank=rank,
                            raw_json={"raw": item},
                        )
                    )
            return results, ProviderStatus(provider="OPENSERP", status="OK", result_count=len(results))
        except httpx.TimeoutException:
            logger.warning("OpenSERP timeout for query: %s", query)
            return [], ProviderStatus(provider="OPENSERP", status="TIMEOUT", message="Request timed out", result_count=0)
        except Exception as exc:
            logger.warning("OpenSERP error for query %s: %s", query, exc)
            return [], ProviderStatus(provider="OPENSERP", status="ERROR", message=str(exc), result_count=0)

    def search_playwright(self, query_or_url: str, intent: SearchIntent) -> tuple[list[NormalizedSearchResult], ProviderStatus]:
        return [], ProviderStatus(provider="PLAYWRIGHT", status="DISABLED", message="Playwright capture not enabled", result_count=0)

    def _dedupe_results(self, results: list[NormalizedSearchResult]) -> list[NormalizedSearchResult]:
        """Deduplicate by normalized_url, keeping first occurrence's richer data."""
        seen: dict[str, NormalizedSearchResult] = {}
        for r in results:
            key = r.normalized_url
            if key not in seen:
                seen[key] = r
            else:
                # Keep richer data from first occurrence
                if r.title and not seen[key].title:
                    seen[key].title = r.title
                if r.snippet and not seen[key].snippet:
                    seen[key].snippet = r.snippet
                if r.raw_json and not seen[key].raw_json:
                    seen[key].raw_json = r.raw_json
        return list(seen.values())

    def _store_results(
        self, results: list[NormalizedSearchResult], request: ResearchSearchRequest
    ) -> int:
        stored = 0
        for r in results:
            # Use normalized_url for dedup check — same URL with different tracking params = duplicate
            exists = self.db.query(ResearchSearchResult).filter(
                ResearchSearchResult.normalized_url == r.normalized_url,
                ResearchSearchResult.product_id == request.product_id,
                ResearchSearchResult.idea_id == request.idea_id,
                ResearchSearchResult.campaign_id == request.campaign_id,
                ResearchSearchResult.intent == request.intent,
            ).first()
            if exists:
                continue
            record = ResearchSearchResult(
                query=request.query,
                normalized_query=request.query.strip().lower(),
                provider=r.provider,
                intent=request.intent,
                title=r.title,
                url=r.url,
                normalized_url=r.normalized_url,
                snippet=r.snippet,
                source_domain=_extract_domain(r.url),
                rank=r.rank,
                price_text=r.price_text,
                currency=r.currency,
                raw_json={"created_from_local_search": True, "requires_manual_verification": True, "provider_raw": r.raw_json},
                fetched_at=datetime.utcnow(),
                product_id=request.product_id,
                idea_id=request.idea_id,
                campaign_id=request.campaign_id,
                conversion_status="NOT_CONVERTED",
            )
            self.db.add(record)
            stored += 1
        if stored > 0:
            self.db.commit()
        return stored

    def list_results(
        self,
        product_id: uuid.UUID | None = None,
        idea_id: uuid.UUID | None = None,
        campaign_id: uuid.UUID | None = None,
        intent: str | None = None,
        provider: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ResearchSearchResult]:
        query = self.db.query(ResearchSearchResult)
        if product_id:
            query = query.filter(ResearchSearchResult.product_id == product_id)
        if idea_id:
            query = query.filter(ResearchSearchResult.idea_id == idea_id)
        if campaign_id:
            query = query.filter(ResearchSearchResult.campaign_id == campaign_id)
        if intent:
            query = query.filter(ResearchSearchResult.intent == intent)
        if provider:
            query = query.filter(ResearchSearchResult.provider == provider)
        return query.order_by(ResearchSearchResult.fetched_at.desc()).offset(offset).limit(limit).all()

    def get_result(self, result_id: uuid.UUID) -> ResearchSearchResult | None:
        return self.db.query(ResearchSearchResult).filter(ResearchSearchResult.id == result_id).first()

    def reject_result(self, result_id: uuid.UUID, reason: str) -> ResearchSearchResult | None:
        record = self.get_result(result_id)
        if not record:
            return None
        record.conversion_status = "REJECTED"
        record.reject_reason = reason
        self.db.commit()
        self.db.refresh(record)
        return record

    def convert_to_candidate(self, result_id: uuid.UUID, request: ConvertSearchResultToCandidateRequest) -> ConvertSearchResultToCandidateResponse | None:
        """
        Convert a search result to an evidence candidate.

        Only SOLD_LISTING, ACTIVE_LISTING, SUPPLIER_SOURCE, COMPETITOR_LISTING are supported.
        COMPLAINT_NOTE and KEYWORD_DEMAND_NOTE are rejected with a clear error.
        Converted candidates are always PENDING — never USER_VERIFIED.
        """
        from fastapi import HTTPException

        record = self.get_result(result_id)
        if not record:
            return None

        # Strict conversion: reject unsupported types explicitly
        if request.candidate_type not in SUPPORTED_CANDIDATE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Candidate type '{request.candidate_type}' is not supported. "
                        f"Supported types: {sorted(SUPPORTED_CANDIDATE_TYPES)}. "
                        f"COMPLAINT_NOTE and KEYWORD_DEMAND_NOTE require a different storage path.",
            )

        from app.models.external_research import EvidenceCandidate

        # Map to EvidenceCandidate candidate_type — only these four are valid here
        candidate_type_map: dict[str, str] = {
            "SOLD_LISTING": "MARKETPLACE_EVIDENCE",
            "ACTIVE_LISTING": "MARKETPLACE_EVIDENCE",
            "SUPPLIER_SOURCE": "SUPPLIER_SOURCE",
            "COMPETITOR_LISTING": "COMPETITOR_LISTING",
        }
        evidence_type_map: dict[str, str] = {
            "SOLD_LISTING": "SOLD_LISTING",
            "ACTIVE_LISTING": "ACTIVE_LISTING",
            "SUPPLIER_SOURCE": "SUPPLIER_SOURCE",
            "COMPETITOR_LISTING": "COMPETITOR_LISTING",
        }

        candidate = EvidenceCandidate(
            idea_id=request.idea_id or record.idea_id,
            product_id=request.product_id or record.product_id,
            campaign_id=request.campaign_id or record.campaign_id,
            source="MANUAL_CAPTURE",
            candidate_type=candidate_type_map[request.candidate_type],
            marketplace=_extract_domain(record.url) or "Unknown",
            evidence_type=evidence_type_map[request.candidate_type],
            title=request.title_override or record.title,
            url=record.url,
            price=request.price,
            seller=None,
            confidence="LOW",
            review_status="PENDING",
            raw_json={
                "search_result_id": str(record.id),
                "provider": record.provider,
                "query": record.query,
                "snippet": record.snippet,
                "source_domain": record.source_domain,
                "created_from_local_search": True,
                "requires_manual_verification": True,
                "local_search_intent": record.intent,
            },
        )
        self.db.add(candidate)
        self.db.flush()

        record.conversion_status = "CONVERTED_TO_CANDIDATE"
        record.converted_candidate_id = candidate.id
        self.db.commit()
        self.db.refresh(record)

        return ConvertSearchResultToCandidateResponse(
            search_result_id=record.id,
            candidate_id=candidate.id,
            verification_status="PENDING",
            status="PENDING",
        )
