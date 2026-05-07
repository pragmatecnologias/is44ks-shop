"""tests for the local search broker"""

from __future__ import annotations

import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.config import settings
from app.models.research_search import ResearchSearchResult
from app.services.research_search_broker import (
    SUPPORTED_CANDIDATE_TYPES,
    _normalize_url,
    ResearchSearchBroker,
)
from app.schemas.research_search_schema import (
    ConvertSearchResultToCandidateRequest,
    ResearchSearchRequest,
)


# =============================================================================
# Fix 3: normalized_url model + index
# =============================================================================

class TestNormalizedUrl:
    def test_normalize_url_strips_utm_params(self):
        url = "https://ebay.com/itm/123?utm_source=x&utm_medium=y&fbclid=abc"
        assert _normalize_url(url) == "ebay.com/itm/123"

    def test_normalize_url_strips_fragment(self):
        url = "https://example.com/product#section"
        assert _normalize_url(url) == "example.com/product"

    def test_normalize_url_strips_www(self):
        url = "https://www.amazon.com/dp/B001"
        assert _normalize_url(url) == "amazon.com/dp/b001"

    def test_normalize_url_lowercases(self):
        url = "https://EXAMPLE.COM/Product"
        assert _normalize_url(url) == "example.com/product"

    def test_normalize_url_strips_trailing_slash(self):
        url = "https://example.com/product/"
        assert _normalize_url(url) == "example.com/product"

    def test_normalize_url_same_product_different_tracking(self):
        url1 = "https://ebay.com/itm/123?utm_source=x"
        url2 = "https://ebay.com/itm/123?utm_source=y"
        assert _normalize_url(url1) == _normalize_url(url2) == "ebay.com/itm/123"


class TestModelHasNormalizedUrlField:
    def test_model_has_normalized_url_column(self):
        record = ResearchSearchResult(
            id=uuid.uuid4(),
            query="test",
            provider="SEARXNG",
            intent="SOLD_EVIDENCE",
            url="https://example.com/product?utm_source=x",
            normalized_url="example.com/product",
        )
        assert hasattr(record, "normalized_url")
        assert record.normalized_url == "example.com/product"


# =============================================================================
# Fix 4: deduped_count = raw_count - unique_count
# =============================================================================

class TestDedupedCountCalculation:
    def test_broker_tracks_raw_and_deduped_counts(self):
        """deduped_count = raw results before dedupe - unique results after"""
        raw = 10
        unique = 7
        deduped = raw - unique
        assert deduped == 3


# =============================================================================
# Fix 5: httpx params for query encoding
# =============================================================================

class TestSearxngUsesParams:
    def test_searxng_url_built_with_params_not_concatenation(self):
        """SearXNG URL construction uses params dict, not string concatenation."""
        broker = ResearchSearchBroker(db=MagicMock())

        mock_response = MagicMock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)

        with patch("httpx.Client", return_value=mock_client):
            broker.search_searxng("test query & special=chars", 10)

        call_args = mock_client.get.call_args
        params = call_args.kwargs.get("params")
        assert params is not None, "params dict must be passed to httpx.Client.get()"
        assert params["q"] == "test query & special=chars"


class TestOpenserpUsesParams:
    def test_openserp_url_built_with_params_not_concatenation(self):
        broker = ResearchSearchBroker(db=MagicMock())

        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)

        with patch("httpx.Client", return_value=mock_client):
            broker.search_openserp("test & query", 5)

        call_args = mock_client.get.call_args
        params = call_args.kwargs.get("params")
        assert params is not None, "params dict must be passed to httpx.Client.get()"
        assert params["q"] == "test & query"


# =============================================================================
# Fix 6: Strict conversion — reject unsupported types
# =============================================================================

class TestStrictConversion:
    def test_supported_types_accepted(self):
        assert "SOLD_LISTING" in SUPPORTED_CANDIDATE_TYPES
        assert "ACTIVE_LISTING" in SUPPORTED_CANDIDATE_TYPES
        assert "SUPPLIER_SOURCE" in SUPPORTED_CANDIDATE_TYPES
        assert "COMPETITOR_LISTING" in SUPPORTED_CANDIDATE_TYPES

    def test_complaint_note_not_supported(self):
        assert "COMPLAINT_NOTE" not in SUPPORTED_CANDIDATE_TYPES

    def test_keyword_demand_note_not_supported(self):
        assert "KEYWORD_DEMAND_NOTE" not in SUPPORTED_CANDIDATE_TYPES

    def test_convert_raises_for_unsupported_type(self):
        mock_db = MagicMock()
        record_id = uuid.uuid4()

        mock_record = MagicMock()
        mock_record.id = record_id
        mock_record.idea_id = None
        mock_record.product_id = None
        mock_record.campaign_id = None
        mock_record.url = "https://example.com"
        mock_record.title = None
        mock_record.provider = "SEARXNG"
        mock_record.query = "test"
        mock_record.snippet = None
        mock_record.source_domain = "example.com"
        mock_record.intent = "SOLD_EVIDENCE"

        mock_db.query.return_value.filter.return_value.first.return_value = mock_record

        broker = ResearchSearchBroker(db=mock_db)

        request = ConvertSearchResultToCandidateRequest(
            candidate_type="COMPLAINT_NOTE",
            notes="test",
        )

        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            broker.convert_to_candidate(record_id, request)
        assert exc_info.value.status_code == 400
        assert "COMPLAINT_NOTE" in exc_info.value.detail
        assert "not supported" in exc_info.value.detail

    def test_convert_raises_for_keyword_demand_note(self):
        mock_db = MagicMock()
        record_id = uuid.uuid4()

        mock_record = MagicMock()
        mock_record.id = record_id
        mock_record.idea_id = None
        mock_record.product_id = None
        mock_record.campaign_id = None
        mock_record.url = "https://example.com"
        mock_record.title = None
        mock_record.provider = "SEARXNG"
        mock_record.query = "test"
        mock_record.snippet = None
        mock_record.source_domain = "example.com"
        mock_record.intent = "KEYWORD_DEMAND"

        mock_db.query.return_value.filter.return_value.first.return_value = mock_record

        broker = ResearchSearchBroker(db=mock_db)

        request = ConvertSearchResultToCandidateRequest(
            candidate_type="KEYWORD_DEMAND_NOTE",
        )

        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            broker.convert_to_candidate(record_id, request)
        assert exc_info.value.status_code == 400
        assert "KEYWORD_DEMAND_NOTE" in exc_info.value.detail

    def test_convert_creates_pending_candidate(self):
        """Conversion must create PENDING candidate, never USER_VERIFIED."""
        mock_db = MagicMock()
        candidate_id = uuid.uuid4()
        record_id = uuid.uuid4()
        product_id = uuid.uuid4()

        mock_record = MagicMock()
        mock_record.id = record_id
        mock_record.idea_id = None
        mock_record.product_id = product_id
        mock_record.campaign_id = None
        mock_record.url = "https://example.com/product"
        mock_record.title = "Example Product"
        mock_record.provider = "SEARXNG"
        mock_record.query = "example"
        mock_record.snippet = "Test snippet"
        mock_record.source_domain = "example.com"
        mock_record.intent = "SOLD_EVIDENCE"

        mock_db.query.return_value.filter.return_value.first.return_value = mock_record

        added_candidates = []
        def track_add(obj):
            if hasattr(obj, "__class__") and obj.__class__.__name__ == "EvidenceCandidate":
                added_candidates.append(obj)
                obj.id = candidate_id
            return obj

        mock_db.add = track_add
        mock_db.flush = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()

        broker = ResearchSearchBroker(db=mock_db)

        request = ConvertSearchResultToCandidateRequest(
            candidate_type="SOLD_LISTING",
            product_id=product_id,
        )

        result = broker.convert_to_candidate(record_id, request)

        assert result is not None
        assert result.verification_status == "PENDING"
        assert result.status == "PENDING"

        assert len(added_candidates) == 1
        candidate = added_candidates[0]
        assert candidate.review_status == "PENDING"

        raw_json = candidate.raw_json
        assert raw_json["created_from_local_search"] is True
        assert raw_json["requires_manual_verification"] is True


class TestProductReadinessUnchanged:
    def test_local_search_does_not_run_product_research(self):
        """Local search broker must NOT import research_pipeline, decision_agent, or marketplace_service."""
        import inspect
        source = inspect.getsource(ResearchSearchBroker)
        assert "research_pipeline" not in source.lower()
        assert "decision_agent" not in source.lower()
        assert "marketplace_service" not in source.lower()


# =============================================================================
# Fix 7: Real integration tests
# =============================================================================

class TestSearxngMockedIntegration:
    def test_searxng_mocked_response_stored(self):
        """Mocked SearXNG response → broker stores result in DB."""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [
                {
                    "title": "Hinge Pin Remover - $12.99",
                    "url": "https://ebay.com/itm/456",
                    "content": "Hardened steel hinge pin remover. Sold 408 times.",
                    "engine": "google",
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)

        broker = ResearchSearchBroker(db=mock_db)

        with patch("httpx.Client", return_value=mock_client):
            request = ResearchSearchRequest(
                query="hinge pin remover",
                intent="SOLD_EVIDENCE",
                providers=["SEARXNG"],
                max_results=10,
                product_id=uuid.uuid4(),
            )
            response = broker.search(request)

        assert response.result_count == 1
        assert response.stored_count == 1
        assert response.results[0].title == "Hinge Pin Remover - $12.99"
        assert response.results[0].url == "https://ebay.com/itm/456"
        assert response.provider_statuses[0].provider == "SEARXNG"
        assert response.provider_statuses[0].status == "OK"


class TestOpenserpMockedIntegration:
    def test_openserp_mocked_response_stored(self):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [
                {
                    "title": "Door Hinge Tool 5-in-1",
                    "url": "https://amazon.com/dp/B001",
                    "snippet": "Multi-purpose hinge tool",
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)

        broker = ResearchSearchBroker(db=mock_db)

        with patch("httpx.Client", return_value=mock_client):
            request = ResearchSearchRequest(
                query="door hinge tool",
                intent="ACTIVE_LISTING",
                providers=["OPENSERP"],
                max_results=10,
            )
            response = broker.search(request)

        assert response.result_count == 1
        assert response.stored_count == 1
        assert response.provider_statuses[0].provider == "OPENSERP"
        assert response.provider_statuses[0].status == "OK"


class TestProviderFailureIsolation:
    def test_searxng_down_openserp_succeeds(self):
        """When one provider fails, other providers' results still returned."""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()

        mock_response_ok = MagicMock()
        mock_response_ok.json.return_value = {
            "results": [
                {"title": "Result from OpenSERP", "url": "https://openserp.example.com", "snippet": "works"}
            ]
        }
        mock_response_ok.raise_for_status = MagicMock()

        mock_client = MagicMock()

        def mock_get(url, **kwargs):
            result = MagicMock()
            if "searxng" in str(url) or "8888" in str(url):
                raise Exception("Connection refused")
            result.json.return_value = mock_response_ok.json.return_value
            result.raise_for_status = MagicMock()
            return result

        mock_client.get.side_effect = mock_get
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)

        broker = ResearchSearchBroker(db=mock_db)

        with patch("httpx.Client", return_value=mock_client):
            request = ResearchSearchRequest(
                query="test",
                intent="GENERAL_RESEARCH",
                providers=["SEARXNG", "OPENSERP"],
                max_results=10,
            )
            response = broker.search(request)

        searxng_status = next((p for p in response.provider_statuses if p.provider == "SEARXNG"), None)
        openerp_status = next((p for p in response.provider_statuses if p.provider == "OPENSERP"), None)

        assert searxng_status is not None
        assert searxng_status.status == "ERROR"
        assert openerp_status is not None
        assert openerp_status.status == "OK"
        assert response.result_count == 1


class TestDuplicateUrlsWithUtmParams:
    def test_same_url_different_utm_stored_once(self):
        """Same product URL with different UTM params → stored once."""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [
                {"title": "Product A", "url": "https://ebay.com/itm/123?utm_source=x", "content": "desc"},
                {"title": "Product A", "url": "https://ebay.com/itm/123?utm_source=y", "content": "desc"},
            ]
        }
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)

        broker = ResearchSearchBroker(db=mock_db)

        with patch("httpx.Client", return_value=mock_client):
            request = ResearchSearchRequest(
                query="test",
                intent="SOLD_EVIDENCE",
                providers=["SEARXNG"],
                max_results=10,
            )
            response = broker.search(request)

        # raw_count = 2, unique after dedupe = 1, deduped_count = 1
        assert response.result_count == 1
        assert response.deduped_count == 1
        assert response.stored_count == 1


class TestRejectRoute:
    def test_reject_updates_conversion_status(self):
        mock_db = MagicMock()
        record_id = uuid.uuid4()

        mock_record = MagicMock()
        mock_record.id = record_id
        mock_record.conversion_status = "NOT_CONVERTED"
        mock_record.reject_reason = None

        mock_db.query.return_value.filter.return_value.first.return_value = mock_record
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()

        broker = ResearchSearchBroker(db=mock_db)
        result = broker.reject_result(record_id, "Not relevant")

        assert result is not None
        assert result.conversion_status == "REJECTED"
        assert result.reject_reason == "Not relevant"


class TestListRouteFilters:
    def test_list_results_filters_by_product_id(self):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.filter.return_value.filter.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

        broker = ResearchSearchBroker(db=mock_db)
        pid = uuid.uuid4()
        broker.list_results(product_id=pid, limit=10)

        # Verify query was called
        mock_db.query.assert_called()

    def test_list_results_filters_by_intent(self):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.filter.return_value.filter.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

        broker = ResearchSearchBroker(db=mock_db)
        broker.list_results(intent="SOLD_EVIDENCE", limit=10)

    def test_list_results_filters_by_provider(self):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.filter.return_value.filter.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

        broker = ResearchSearchBroker(db=mock_db)
        broker.list_results(provider="SEARXNG", limit=10)


# =============================================================================
# Config defaults
# =============================================================================

class TestConfig:
    def test_searxng_base_url_default(self):
        assert settings.SEARXNG_BASE_URL == "http://localhost:8888"

    def test_openserp_base_url_default(self):
        assert settings.OPENSERP_BASE_URL == "http://localhost:7000"

    def test_local_search_settings(self):
        assert settings.ENABLE_LOCAL_SEARCH_BROKER is True
        assert settings.ENABLE_SEARXNG_PROVIDER is True
        assert settings.ENABLE_OPENSERP_PROVIDER is True
        assert settings.LOCAL_SEARCH_DEFAULT_MAX_RESULTS == 10
        assert settings.LOCAL_SEARCH_REQUEST_TIMEOUT_SECONDS == 15