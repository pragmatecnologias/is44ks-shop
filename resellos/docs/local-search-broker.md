# ResellOS Local Search Broker

## Purpose

ResellOS product-scouting agents are blocked when external/monthly web-search tools are exhausted. The Local Search Broker provides an internal search layer backed by local/open-source providers, so agents are no longer blocked by paid API quota limits.

Search results are **discovery artifacts**, not verified evidence. They feed the candidate pipeline and require manual review before any evidence verification or product readiness decision.

---

## Architecture

```
Agent / MCP Tool
    |
    v
ResellOS Research Search Broker
    |
    +--> SearXNG (local, localhost:8888)
    +--> OpenSERP (local, localhost:7000)
    +--> Playwright targeted capture (stub, disabled by default)
    +--> DataForSEO (paid fallback, budget-capped)
    |
    v
Stored ResearchSearchResult rows
    |
    v
EvidenceCandidate rows (PENDING / USER_CAPTURED_UNVERIFIED)
    |
    v
Manual/user/agent review
    |
    v
MarketplaceEvidence / Supplier / Competitor records
    (only after explicit verification)
```

---

## Core Rule

Search results are discovery artifacts, **not verified evidence**.

Local search must **never**:
- mark evidence `USER_VERIFIED` automatically
- mark a product `READY`
- mark a product `READY_FOR_SAMPLE`
- override `final_decision`
- bypass sold-evidence requirements
- bypass supplier/economics checks
- bypass competitor/risk checks

All existing readiness gates remain authoritative.

---

## Providers

### SearXNG

Self-hosted metasearch engine.

**Start SearXNG:**
```bash
docker run -d --name searxng -p 8888:8080 searxng/searxng
```

**Test:**
```bash
curl "http://localhost:8888/search?q=dryer+vent+cleaning+kit&format=json"
```

**Config:** `SEARXNG_BASE_URL=http://localhost:8888`

### OpenSERP

Lightweight structured search.

**Start OpenSERP:**
```bash
docker run -p 7000:7000 karust/openserp serve -a 0.0.0.0
```

**Config:** `OPENSERP_BASE_URL=http://localhost:7000`

### Playwright Capture (Stub)

**Config:** `ENABLE_PLAYWRIGHT_CAPTURE=false`

Not implemented in this pass. Stub returns `DISABLED`. Future work:
- `POST /api/research/capture-url` for targeted URL fetch
- Captures screenshot + text snippets

### DataForSEO

Retains existing budget caps. Never the default. Only when explicitly allowed.

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ENABLE_LOCAL_SEARCH_BROKER` | `true` | Enable/disable the broker |
| `SEARXNG_BASE_URL` | `http://localhost:8888` | SearXNG endpoint |
| `OPENSERP_BASE_URL` | `http://localhost:7000` | OpenSERP endpoint |
| `ENABLE_SEARXNG_PROVIDER` | `true` | Enable SearXNG |
| `ENABLE_OPENSERP_PROVIDER` | `true` | Enable OpenSERP |
| `ENABLE_PLAYWRIGHT_CAPTURE` | `false` | Enable Playwright (stub) |
| `LOCAL_SEARCH_DEFAULT_MAX_RESULTS` | `10` | Default max results |
| `LOCAL_SEARCH_REQUEST_TIMEOUT_SECONDS` | `15` | Provider timeout |
| `LOCAL_SEARCH_STORE_RAW_JSON` | `true` | Store raw JSON from providers |

---

## API Endpoints

### `POST /api/research/search`

Run a local search query.

```json
{
  "query": "door hinge pin removal tool sold eBay 2026",
  "intent": "SOLD_EVIDENCE",
  "providers": ["SEARXNG", "OPENSERP"],
  "max_results": 10,
  "product_id": "a78f6e2a-f8df-490a-9aab-fc4c0ecc467c",
  "idea_id": null,
  "campaign_id": null,
  "store_results": true
}
```

Response:
```json
{
  "query": "...",
  "intent": "SOLD_EVIDENCE",
  "requested_providers": ["SEARXNG", "OPENSERP"],
  "provider_statuses": [
    {"provider": "SEARXNG", "status": "OK", "result_count": 8},
    {"provider": "OPENSERP", "status": "ERROR", "message": "Connection refused", "result_count": 0}
  ],
  "result_count": 8,
  "stored_count": 8,
  "deduped_count": 0,
  "results": [...]
}
```

### `GET /api/research/search-results`

List stored results.

Query params: `product_id`, `idea_id`, `campaign_id`, `intent`, `provider`, `limit`, `offset`

### `POST /api/research/search-results/{result_id}/candidate`

Convert a search result to an evidence candidate.

```json
{
  "candidate_type": "SOLD_LISTING",
  "product_id": "...",
  "idea_id": "...",
  "notes": "Found via local search",
  "price": null,
  "title_override": null
}
```

Converted candidates default to `PENDING` verification status. **Never** `USER_VERIFIED`.

### `PATCH /api/research/search-results/{result_id}/reject`

Reject a search result so it is not converted.

---

## MCP Tools

### `resellos_search_web_local`

```json
{
  "query": "hinge pin removal tool sold",
  "intent": "SOLD_EVIDENCE",
  "providers": ["SEARXNG", "OPENSERP"],
  "max_results": 10,
  "product_id": "...",
  "idea_id": null,
  "campaign_id": null
}
```

**Warning in response:** "Local search results are NOT verified evidence. Do NOT treat active listings as sold evidence. Convert to candidates and verify before any readiness decision."

### `resellos_list_research_search_results`

### `resellos_convert_search_result_to_candidate`

### `resellos_reject_search_result`

---

## Recommended Agent Workflow

```
1. resellos_search_web_local   → discover URLs and snippets
2. resellos_list_research_search_results → review stored results
3. resellos_convert_search_result_to_candidate → convert promising results
4. resellos_list_evidence_candidates → review pending candidates
5. resellos_approve_candidate (as MARKETPLACE_EVIDENCE, COMPETITOR_LISTING, or SUPPLIER_SOURCE)
6. resellos_verify_marketplace_evidence / resellos_verify_supplier_source / resellos_verify_competitor_listing
7. resellos_run_product_research → only after evidence gates are complete
```

---

## Limitations

- Local search may still be blocked by upstream search engines (Google, Bing) that SearXNG proxies
- Local search results are **not** sold-proof verification
- Marketplace pages (eBay, Amazon) may require manual review or Playwright capture to get structured data
- eBay completed-sale data is particularly difficult to obtain automatically
- Providers must be running locally; connection refused errors return partial results from available providers

---

## Files

| File | Purpose |
|------|---------|
| `backend/app/models/research_search.py` | ResearchSearchResult SQLAlchemy model |
| `backend/app/schemas/research_search_schema.py` | Pydantic request/response schemas |
| `backend/app/services/research_search_broker.py` | Provider calls, normalization, deduping, storage |
| `backend/app/routes/research_search.py` | FastAPI route handlers |
| `backend/migrations/versions/0012_research_search.py` | Alembic migration |
| `mcp-server/src/tools/researchSearchTools.ts` | 4 new MCP tools |
| `mcp-server/src/toolRegistry.ts` | Schemas and TOOL_DEFINITIONS updates |
| `mcp-server/src/index.ts` | Switch case dispatch for new tools |
| `frontend/app/research/search/page.tsx` | Research Search UI |
| `frontend/lib/api.ts` | Frontend API client functions |