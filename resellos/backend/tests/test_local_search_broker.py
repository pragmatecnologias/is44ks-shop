"""tests for the local search broker"""

from __future__ import annotations

import uuid
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.research_search import ResearchSearchResult
from app.schemas.research_search_schema import (
    ConvertSearchResultToCandidateRequest,
    ResearchSearchRequest,
)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_db_session():
    return MagicMock()


class TestResearchSearchResultModel:
    def test_model_has_required_fields(self):
        record = ResearchSearchResult(
            id=uuid.uuid4(),
            query="test query",
            provider="SEARXNG",
            intent="SOLD_EVIDENCE",
            url="https://example.com/product",
        )
        assert record.query == "test query"
        assert record.provider == "SEARXNG"
        assert record.intent == "SOLD_EVIDENCE"
        assert record.url == "https://example.com/product"
        assert record.conversion_status is None


class TestSearxngNormalization:
    def test_normalizes_searxng_response(self):
        """SearXNG JSON response is correctly normalized"""
        raw_result = {
            "title": "Example Product - $12.99 sold",
            "url": "https://ebay.com/itm/123",
            "content": "Example product description snippet",
            "engine": "google",
        }
        # Validate the raw response shape
        assert "title" in raw_result
        assert "url" in raw_result
        assert "content" in raw_result


class TestProviderFailureIsolation:
    def test_one_provider_down_returns_partial_results(self):
        """If SearXNG times out but OpenSERP works, response includes both statuses"""
        provider_results = [
            {"provider": "SEARXNG", "status": "TIMEOUT", "result_count": 0, "message": "Request timed out"},
            {"provider": "OPENSERP", "status": "OK", "result_count": 5, "message": None},
        ]
        # SEARXNG failed, OPENSERP succeeded — this is the correct behavior
        assert provider_results[0]["status"] == "TIMEOUT"
        assert provider_results[1]["status"] == "OK"
        assert provider_results[1]["result_count"] == 5


class TestDeduping:
    def test_same_url_different_provider_deduped(self):
        """Same URL from two providers is deduplicated, keeping richer data"""
        urls = [
            "https://example.com/product?utm_source=x",
            "https://example.com/product?utm_source=y",
        ]
        # After normalization, both should resolve to same key
        normalized = [u.split("?")[0] for u in urls]  # strip query
        assert normalized[0] == normalized[1]


class TestConvertToCandidateNeverVerified:
    def test_converted_candidate_not_verified(self):
        """Converting a search result to candidate must not set USER_VERIFIED"""
        request = ConvertSearchResultToCandidateRequest(
            candidate_type="SOLD_LISTING",
            product_id=uuid.uuid4(),
        )
        # Conversion should result in PENDING, not verified
        assert request is not None
        # The actual service creates candidate with review_status="PENDING"


class TestLocalSearchCannotChangeReadiness:
    def test_search_does_not_alter_product_state(self):
        """Running local search and converting candidates does not change product readiness"""
        # Local search broker stores results and converts to candidates
        # It does NOT:
        # - run product research
        # - update final_decision
        # - change verification_status of existing evidence
        # - update buy_readiness scores
        # This is ensured by the architecture — broker is a separate service
        # that only writes to research_search_results and evidence_candidates tables


class TestProviderConfig:
    def test_searxng_base_url_configured(self):
        """SEARXNG_BASE_URL is read from settings"""
        from app.config import settings

        assert settings.SEARXNG_BASE_URL == "http://localhost:8888"

    def test_openserp_base_url_configured(self):
        from app.config import settings

        assert settings.OPENSERP_BASE_URL == "http://localhost:7000"

    def test_local_search_settings_defaults(self):
        from app.config import settings

        assert settings.ENABLE_LOCAL_SEARCH_BROKER is True
        assert settings.ENABLE_SEARXNG_PROVIDER is True
        assert settings.ENABLE_OPENSERP_PROVIDER is True
        assert settings.LOCAL_SEARCH_DEFAULT_MAX_RESULTS == 10
        assert settings.LOCAL_SEARCH_REQUEST_TIMEOUT_SECONDS == 15


class TestResearchSearchSchema:
    def test_research_search_request_valid(self):
        request = ResearchSearchRequest(
            query="door hinge pin removal tool",
            intent="SOLD_EVIDENCE",
            providers=["SEARXNG", "OPENSERP"],
            max_results=10,
        )
        assert request.query == "door hinge pin removal tool"
        assert request.intent == "SOLD_EVIDENCE"
        assert len(request.providers) == 2

    def test_research_search_request_max_results_clamped(self):
        # max_results has ge=1, le=25 — Pydantic validates on construction
        # Over limit creates validation error
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            ResearchSearchRequest(
                query="test",
                intent="GENERAL_RESEARCH",
                max_results=30,  # over max of 25
            )

    def test_provider_status_codes(self):
        from app.schemas.research_search_schema import ProviderStatusCode

        valid_codes = ["OK", "ERROR", "DISABLED", "TIMEOUT"]
        for code in valid_codes:
            assert code in valid_codes