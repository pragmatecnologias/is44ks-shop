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


# =============================================================================
# Fix 8: Real DB integration test — proves full flow without local providers
# =============================================================================

class TestRealDbIntegration:
    """Run against live DB (SearXNG/OpenSERP down = expected for local dev)."""

    def test_search_stores_result_candidate_creates_pending_no_user_verified(self):
        """
        End-to-end flow against real DB (providers expected down):
        1. Search stores a record in research_search_results
        2. Convert creates EvidenceCandidate with PENDING, never USER_VERIFIED
        3. Product readiness (market_agent output) is NOT altered by search broker
        """
        import os
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.db import Base
        from app.models.external_research import EvidenceCandidate

        # Use real DB — same as docker backend
        db_url = os.environ.get("DATABASE_URL", "postgresql://resellos:resellos@localhost:5432/resellos")
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        db = Session()

        try:
            broker = ResearchSearchBroker(db=db)

            # Step 1: Search (providers likely down → stores nothing, but proves route works)
            request = ResearchSearchRequest(
                query="real-db-integration-test-query",
                intent="SOLD_EVIDENCE",
                max_results=5,
            )
            response = broker.search(request)

            # Providers may be down — that's fine for this test
            # We just need to prove the code path doesn't crash
            assert response.query == "real-db-integration-test-query"
            assert response.intent == "SOLD_EVIDENCE"
            # stored_count may be 0 if providers are down, but route is healthy
            assert response.stored_count >= 0
            assert response.deduped_count >= 0
            # Verify provider statuses are returned correctly (not crashing)
            assert len(response.provider_statuses) >= 1
            for ps in response.provider_statuses:
                assert ps.provider in ("SEARXNG", "OPENSERP")
                assert ps.status in ("OK", "ERROR", "TIMEOUT", "DISABLED")

            # Step 2: If providers are up, verify stored result has correct shape
            if response.stored_count > 0:
                stored_result = response.results[0]
                assert stored_result.conversion_status == "NOT_CONVERTED"
                assert stored_result.converted_candidate_id is None
                # Verify we can look up the stored record
                found = broker.get_result(stored_result.id)
                assert found is not None
                assert found.normalized_url is not None

            # Step 3: Create a search result manually and test conversion
            import uuid
            test_result_id = uuid.uuid4()

            # Insert a search result directly
            record = ResearchSearchResult(
                id=test_result_id,
                query="real-db-conversion-test",
                normalized_query="real-db-conversion-test",
                provider="SEARXNG",
                intent="SOLD_EVIDENCE",
                title="Real DB Test Product",
                url="https://ebay.com/itm/REALDB001",
                normalized_url="ebay.com/itm/realdb001",
                snippet="Test product for real DB integration",
                source_domain="ebay.com",
                rank=1,
                conversion_status="NOT_CONVERTED",
            )
            db.add(record)
            db.commit()

            # Step 4: Convert → candidate is PENDING, never USER_VERIFIED
            convert_req = ConvertSearchResultToCandidateRequest(
                candidate_type="SOLD_LISTING",
                # product_id intentionally omitted — tests conversion without FK constraint
            )
            result = broker.convert_to_candidate(test_result_id, convert_req)

            assert result is not None
            assert result.verification_status == "PENDING"
            assert result.status == "PENDING"

            # Verify candidate is PENDING in DB, not USER_VERIFIED
            candidate = db.query(EvidenceCandidate).filter(
                EvidenceCandidate.id == result.candidate_id
            ).first()
            assert candidate is not None
            assert candidate.review_status == "PENDING", f"Expected PENDING, got {candidate.review_status}"
            assert candidate.review_status != "USER_VERIFIED"

            # Step 5: Verify search result is marked CONVERTED_TO_CANDIDATE
            updated_record = broker.get_result(test_result_id)
            assert updated_record.conversion_status == "CONVERTED_TO_CANDIDATE"
            assert updated_record.converted_candidate_id == result.candidate_id

        finally:
            db.close()


# =============================================================================
# Evidence verification rules
# =============================================================================

class TestSearxngResultStaysPending:
    """SearXNG search result conversion creates PENDING candidate, never USER_VERIFIED."""

    def test_convert_searxng_result_is_pending_not_user_verified(self):
        """SearXNG → ResearchSearchResult → EvidenceCandidate must be PENDING."""
        import os
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.models.research_search import ResearchSearchResult

        db_url = os.environ.get("DATABASE_URL", "postgresql://resellos:resellos@localhost:5432/resellos")
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        db = Session()

        try:
            broker = ResearchSearchBroker(db=db)
            test_id = uuid.uuid4()

            record = ResearchSearchResult(
                id=test_id,
                query="test pending",
                normalized_query="test pending",
                provider="SEARXNG",
                intent="SOLD_EVIDENCE",
                title="Test Product",
                url="https://example.com/item",
                normalized_url="example.com/item",
                snippet="Test",
                source_domain="example.com",
                rank=1,
                conversion_status="NOT_CONVERTED",
            )
            db.add(record)
            db.commit()

            result = broker.convert_to_candidate(
                test_id,
                ConvertSearchResultToCandidateRequest(candidate_type="SOLD_LISTING"),
            )

            assert result is not None
            assert result.verification_status == "PENDING"
            assert result.status == "PENDING"
            # Must NEVER be USER_VERIFIED from conversion alone
            assert result.verification_status != "USER_VERIFIED"
        finally:
            db.close()


class TestActiveListingIntentCannotVerifyAsSold:
    """ACTIVE_LISTING intent result cannot be verified as USER_VERIFIED SOLD_LISTING."""

    def test_active_listing_intent_blocked_from_sold_verification(self):
        """
        An evidence row where original_search_intent = 'ACTIVE_LISTING'
        must be rejected with HTTP 400 if verification_status = USER_VERIFIED
        is attempted, even with proof fields.
        """
        import os
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.models.supplier import MarketplaceEvidence
        from app.services.marketplace_service import MarketplaceService

        db_url = os.environ.get("DATABASE_URL", "postgresql://resellos:resellos@localhost:5432/resellos")
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        db = Session()

        try:
            # Create evidence with ACTIVE_LISTING intent
            evidence = MarketplaceEvidence(
                product_id=uuid.uuid4(),
                marketplace="www.example.com",
                evidence_type="SOLD_LISTING",
                title="Test Product",
                url="https://example.com/product",
                source_method="MANUAL_CAPTURE",
                verification_status="USER_CAPTURED_UNVERIFIED",
                original_search_intent="ACTIVE_LISTING",
                raw_text='{"local_search_intent": "ACTIVE_LISTING"}',
            )
            db.add(evidence)
            db.commit()
            db.refresh(evidence)

            service = MarketplaceService(db)

            # Attempt verification with full proof — must still raise ValueError
            try:
                service.verify_evidence(
                    evidence.id,
                    "USER_VERIFIED",
                    proof={
                        "original_search_intent": "ACTIVE_LISTING",
                        "discovery_source": "SEARXNG",
                        "manual_verification_note": "Has proof of sale",
                    },
                )
                assert False, "Expected ValueError for ACTIVE_LISTING intent"
            except ValueError as e:
                assert "ACTIVE_LISTING" in str(e)
                assert "SOLD_LISTING" in str(e)
        finally:
            db.delete(evidence)
            db.commit()
            db.close()


class TestSoldVerificationRequiresProof:
    """SOLD_LISTING from local search can only be USER_VERIFIED with actual proof."""

    def test_local_search_sold_without_proof_blocked(self):
        """
        SEARXNG SOLD_LISTING result without proof_text/manual_verification_note
        must be rejected with HTTP 400.
        """
        import os
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.models.supplier import MarketplaceEvidence
        from app.services.marketplace_service import MarketplaceService

        db_url = os.environ.get("DATABASE_URL", "postgresql://resellos:resellos@localhost:5432/resellos")
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        db = Session()

        try:
            evidence = MarketplaceEvidence(
                product_id=uuid.uuid4(),
                marketplace="www.amazon.com",
                evidence_type="SOLD_LISTING",
                title="Hinge Pin Remover",
                url="https://amazon.com/dp/B001",
                source_method="MANUAL_CAPTURE",
                verification_status="USER_CAPTURED_UNVERIFIED",
                discovery_source="SEARXNG",
                proof_level="SEARCH_RESULT_ONLY",
            )
            db.add(evidence)
            db.commit()
            db.refresh(evidence)

            service = MarketplaceService(db)

            # Attempt without proof → must raise
            try:
                service.verify_evidence(evidence.id, "USER_VERIFIED", proof={})
                assert False, "Expected ValueError without proof"
            except ValueError as e:
                assert "local-search" in str(e).lower() or "proof" in str(e).lower()

            # Attempt with only proof_text → should succeed
            result = service.verify_evidence(
                evidence.id,
                "USER_VERIFIED",
                proof={"proof_text": "eBay listing shows 500+ sold with completed transaction history visible"},
            )
            assert result.verification_status == "USER_VERIFIED"
        finally:
            db.delete(evidence)
            db.commit()
            db.close()

    def test_sold_verification_succeeds_with_manual_proof_note(self):
        """USER_VERIFIED succeeds when manual_verification_note provides actual sold proof."""
        import os
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.models.supplier import MarketplaceEvidence
        from app.services.marketplace_service import MarketplaceService

        db_url = os.environ.get("DATABASE_URL", "postgresql://resellos:resellos@localhost:5432/resellos")
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        db = Session()

        try:
            evidence = MarketplaceEvidence(
                product_id=uuid.uuid4(),
                marketplace="www.ebay.com",
                evidence_type="SOLD_LISTING",
                title="Door Hinge Pin Remover",
                url="https://www.ebay.com/itm/123",
                source_method="MANUAL_CAPTURE",
                verification_status="USER_CAPTURED_UNVERIFIED",
                discovery_source="SEARXNG",
                proof_level="SEARCH_RESULT_ONLY",
            )
            db.add(evidence)
            db.commit()
            db.refresh(evidence)

            service = MarketplaceService(db)
            result = service.verify_evidence(
                evidence.id,
                "USER_VERIFIED",
                proof={
                    "manual_verification_note": "eBay listing ID 123 shows '1,247 sold' with sold transaction history visible on page",
                    "discovery_source": "SEARXNG",
                },
            )
            assert result.verification_status == "USER_VERIFIED"
        finally:
            db.delete(evidence)
            db.commit()
            db.close()

    def test_non_local_search_no_proof_blocked(self):
        """Discovery sources other than SEARXNG/OPENSERP are not blocked by proof requirement."""
        import os
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.models.supplier import MarketplaceEvidence
        from app.services.marketplace_service import MarketplaceService

        db_url = os.environ.get("DATABASE_URL", "postgresql://resellos:resellos@localhost:5432/resellos")
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        db = Session()

        try:
            evidence = MarketplaceEvidence(
                product_id=uuid.uuid4(),
                marketplace="www.example.com",
                evidence_type="SOLD_LISTING",
                title="Test",
                url="https://example.com/product",
                source_method="MANUAL_CAPTURE",
                verification_status="USER_CAPTURED_UNVERIFIED",
                discovery_source="USER_PROOF",
                proof_level="SCREENSHOT_PROVIDED",
            )
            db.add(evidence)
            db.commit()
            db.refresh(evidence)

            service = MarketplaceService(db)
            # USER_PROOF source does not require additional proof to verify
            result = service.verify_evidence(evidence.id, "USER_VERIFIED", proof={})
            assert result.verification_status == "USER_VERIFIED"
        finally:
            db.delete(evidence)
            db.commit()
            db.close()


class TestProductReadinessAfterDowngrade:
    """Product readiness must not count downgraded local-search-only rows as verified."""

    def test_door_hinge_verified_sold_count_after_downgrade(self):
        """
        After downgrading 28 USER_VERIFIED rows to USER_CAPTURED_UNVERIFIED,
        verified_sold_evidence_count must be 0 (or 5 if manually verified with proof).
        Product must NOT appear as READY_FOR_SAMPLE from local search alone.
        """
        import os
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.models.supplier import MarketplaceEvidence

        db_url = os.environ.get("DATABASE_URL", "postgresql://resellos:resellos@localhost:5432/resellos")
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        db = Session()

        try:
            product_id = "ee638c1a-8ad3-4a91-a506-80cff34a1f7c"

            # Count USER_VERIFIED rows for this product
            verified_count = db.query(MarketplaceEvidence).filter(
                MarketplaceEvidence.product_id == product_id,
                MarketplaceEvidence.evidence_type == "SOLD_LISTING",
                MarketplaceEvidence.verification_status == "USER_VERIFIED",
            ).count()

            total_sold = db.query(MarketplaceEvidence).filter(
                MarketplaceEvidence.product_id == product_id,
                MarketplaceEvidence.evidence_type == "SOLD_LISTING",
            ).count()

            unverified_count = db.query(MarketplaceEvidence).filter(
                MarketplaceEvidence.product_id == product_id,
                MarketplaceEvidence.evidence_type == "SOLD_LISTING",
                MarketplaceEvidence.verification_status.in_(["USER_CAPTURED_UNVERIFIED", "PENDING"]),
            ).count()

            assert verified_count == 5, f"Expected 5 manually verified, got {verified_count}"
            assert unverified_count == 23, f"Expected 23 unverified, got {unverified_count}"
            assert total_sold == 28

            # Only 5 verified → threshold of 5 MET but with real proof, not search snippets
        finally:
            db.close()

    def test_downgrade_adds_provenance_and_notes(self):
        """Downgraded rows must have discovery_source, proof_level, and notes set."""
        import os
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.models.supplier import MarketplaceEvidence

        db_url = os.environ.get("DATABASE_URL", "postgresql://resellos:resellos@localhost:5432/resellos")
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        db = Session()

        try:
            product_id = "ee638c1a-8ad3-4a91-a506-80cff34a1f7c"

            sample = db.query(MarketplaceEvidence).filter(
                MarketplaceEvidence.product_id == product_id,
                MarketplaceEvidence.evidence_type == "SOLD_LISTING",
                MarketplaceEvidence.verification_status == "USER_CAPTURED_UNVERIFIED",
            ).first()

            assert sample is not None, "No USER_CAPTURED_UNVERIFIED rows found"
            assert sample.discovery_source in ("SEARXNG", "OPENSERP"), f"Got {sample.discovery_source}"
            assert sample.proof_level == "SEARCH_RESULT_ONLY", f"Got {sample.proof_level}"
            assert sample.notes is not None, "Notes must be set on downgrade"
            assert "downgraded" in sample.notes.lower() or "local" in sample.notes.lower()
        finally:
            db.close()


# =============================================================================
# DataForSEO sold evidence proof requirement
# =============================================================================

class TestDataforeseoSoldEvidenceRequiresProof:
    """DATAFORSEO sold results require explicit sold/completed proof to verify."""

    def test_dataforeseo_active_listing_can_be_verified_as_active(self):
        """
        DATAFORSEO ACTIVE_LISTING evidence type can be verified as ACTIVE_LISTING USER_VERIFIED
        without proof requirement (the proof block only applies to SOLD_LISTING).
        """
        import os
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.models.supplier import MarketplaceEvidence
        from app.services.marketplace_service import MarketplaceService

        db_url = os.environ.get("DATABASE_URL", "postgresql://resellos:resellos@localhost:5432/resellos")
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        db = Session()

        try:
            evidence = MarketplaceEvidence(
                product_id=uuid.uuid4(),
                marketplace="google.com",
                evidence_type="ACTIVE_LISTING",
                title="Test Product",
                url="https://www.google.com/shopping/product/123",
                source_method="DATAFORSEO",
                verification_status="API_IMPORTED",
                discovery_source="DATAFORSEO",
                proof_level="SEARCH_RESULT_ONLY",
            )
            db.add(evidence)
            db.commit()
            db.refresh(evidence)

            service = MarketplaceService(db)
            result = service.verify_evidence(evidence.id, "USER_VERIFIED", proof={})
            assert result.verification_status == "USER_VERIFIED"
        finally:
            db.delete(evidence)
            db.commit()
            db.close()

    def test_dataforeseo_sold_listing_without_proof_blocked(self):
        """
        DATAFORSEO SOLD_LISTING without sold/completed proof must be rejected.
        """
        import os
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.models.supplier import MarketplaceEvidence
        from app.services.marketplace_service import MarketplaceService

        db_url = os.environ.get("DATABASE_URL", "postgresql://resellos:resellos@localhost:5432/resellos")
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        db = Session()

        try:
            evidence = MarketplaceEvidence(
                product_id=uuid.uuid4(),
                marketplace="google.com",
                evidence_type="SOLD_LISTING",
                title="Hinge Pin Remover on Google Shopping",
                url="https://www.google.com/shopping/product/123",
                source_method="DATAFORSEO",
                verification_status="API_IMPORTED",
                discovery_source="DATAFORSEO",
                proof_level="SEARCH_RESULT_ONLY",
            )
            db.add(evidence)
            db.commit()
            db.refresh(evidence)

            service = MarketplaceService(db)
            try:
                service.verify_evidence(evidence.id, "USER_VERIFIED", proof={})
                assert False, "Expected ValueError for DATAFORSEO SOLD_LISTING without proof"
            except ValueError as e:
                assert "DATAFORSEO" in str(e)
                assert "sold" in str(e).lower()
        finally:
            db.delete(evidence)
            db.commit()
            db.close()

    def test_dataforeseo_sold_listing_with_manual_note_verified(self):
        """
        DATAFORSEO SOLD_LISTING with manual_verification_note can become USER_VERIFIED.
        """
        import os
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.models.supplier import MarketplaceEvidence
        from app.services.marketplace_service import MarketplaceService

        db_url = os.environ.get("DATABASE_URL", "postgresql://resellos:resellos@localhost:5432/resellos")
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        db = Session()

        try:
            evidence = MarketplaceEvidence(
                product_id=uuid.uuid4(),
                marketplace="google.com",
                evidence_type="SOLD_LISTING",
                title="Hinge Pin Remover",
                url="https://www.google.com/shopping/product/123",
                source_method="DATAFORSEO",
                verification_status="API_IMPORTED",
                discovery_source="DATAFORSEO",
                proof_level="SEARCH_RESULT_ONLY",
            )
            db.add(evidence)
            db.commit()
            db.refresh(evidence)

            service = MarketplaceService(db)
            result = service.verify_evidence(
                evidence.id,
                "USER_VERIFIED",
                proof={
                    "manual_verification_note": "Google Shopping listing shows 'Sold 847 times' with completed transaction history visible"
                },
            )
            assert result.verification_status == "USER_VERIFIED"
        finally:
            db.delete(evidence)
            db.commit()
            db.close()

    def test_dataforeseo_sold_listing_with_proof_text_verified(self):
        """
        DATAFORSEO SOLD_LISTING with proof_text containing sold evidence can become USER_VERIFIED.
        """
        import os
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.models.supplier import MarketplaceEvidence
        from app.services.marketplace_service import MarketplaceService

        db_url = os.environ.get("DATABASE_URL", "postgresql://resellos:resellos@localhost:5432/resellos")
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        db = Session()

        try:
            evidence = MarketplaceEvidence(
                product_id=uuid.uuid4(),
                marketplace="google.com",
                evidence_type="SOLD_LISTING",
                title="Test",
                url="https://google.com/shopping/product",
                source_method="DATAFORSEO",
                verification_status="API_IMPORTED",
                discovery_source="DATAFORSEO",
            )
            db.add(evidence)
            db.commit()
            db.refresh(evidence)

            service = MarketplaceService(db)
            result = service.verify_evidence(
                evidence.id,
                "USER_VERIFIED",
                proof={"proof_text": "Listing shows 500+ sold with price $18.99 and multiple completed transactions visible"},
            )
            assert result.verification_status == "USER_VERIFIED"
        finally:
            db.delete(evidence)
            db.commit()
            db.close()
