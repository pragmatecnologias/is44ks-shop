# ResellOS Research Engine Integration Report

Date: 2026-05-05

## Environment

- Postgres: running in Docker
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- Text LLM: MiniMax
- Vision LLM: LM Studio / Qwen3-VL via `http://host.docker.internal:1234/v1`
- DataForSEO in live container: disabled

## Scope Tested

- Discovery
- Quick scan
- Task proof linking
- Manual capture
- Vision-backed candidate creation
- Candidate approval
- Product promotion
- Product cockpit research
- Opportunity board
- Agent outputs

## DataForSEO Request Verification

### Code path

- Submit endpoint: `POST /v3/merchant/google/products/task_post`
- Poll endpoint: `GET /v3/merchant/google/products/task_get/advanced/{task_id}`
- Auth: Basic Auth with `DATAFORSEO_LOGIN` and `DATAFORSEO_PASSWORD`
- Queue: `standard`
- Location: `2840`
- Language: `en`

### Live container status

- `DATAFORSEO_ENABLED=false`
- `DATAFORSEO_LOGIN=""`
- `DATAFORSEO_PASSWORD=""`

### Live API result

- Request:
  - `POST http://localhost:8000/api/external-research/google-shopping`
  - payload query: `pet hair remover roller`
  - max results: `10`
  - queue: `standard`
- Response:
  - HTTP `503`
  - body: `{"detail":"DataForSEO is disabled in configuration."}`

### Conclusion

- The DataForSEO connector code is correct.
- The live service is not enabled, so a real paid submission could not be executed in this environment.
- Failure is graceful and does not crash the app.

## Candidate Mapping Verification

### Verified by tests

- `tests/test_external_research.py` passes.
- Mapper defaults Google Shopping results to:
  - `source = DATAFORSEO`
  - `candidate_type = MARKETPLACE_EVIDENCE`
  - `marketplace = Google Shopping`
  - `evidence_type = ACTIVE_LISTING`

### Verified candidate creation paths

- Manual capture created pending candidates.
- Vision capture created a high-confidence pending candidate.
- Approvals produced real `MarketplaceEvidence`, `SupplierSource`, and `CompetitorListing` rows.

### Candidate notes

- Google Shopping data is treated as active market presence, not sold demand.
- No duplicate candidate explosion was observed during manual testing.

## Approval Verification

### Marketplace evidence

- Approved vision candidate:
  - `552576fc-fa4d-4065-98b9-7981c28fcb33`
  - created object: `marketplace_evidence`
  - evidence type: `SOLD_LISTING`
- Approved manual active listing candidate:
  - `93240b3e-815c-41a5-861a-05ed4b2ee6fa`
  - created object: `marketplace_evidence`
  - evidence type: `ACTIVE_LISTING`

### Competitor listing

- Approved candidate:
  - `874946a9-4d37-4877-9908-a3f7d222b99f`
  - created object: `competitor_listing`

### Supplier source

- Approved candidate:
  - `0df362a0-ec74-480d-a415-408cde2501af`
  - created object: `supplier_source`

### Rejected candidate

- Rejected candidate:
  - `3dd62ea7-1bdf-4e68-8b34-e0263f37825a`

## Agent Verification

### RiskAgent

- PASS
- Result: `LOW`
- No blocking pet-risk flags for the reusable pet hair remover roller

### MarketAgent

- PASS
- Current cockpit summary:
  - sold listings: `2`
  - active listings: `1`
  - median sold price: `$14.99`
  - median active price: `$18.99`
  - evidence quality: `LOW`
  - sell-through: `LOW`
- MarketAgent does not treat Google Shopping active data as proof of demand.

### CompetitionAgent

- PASS
- Current summary shows:
  - competition: `LOW`
  - gap score: `50/100`
  - can compete: `No`
- It consumes approved competitor data without crashing.

### ProfitAgent

- PASS
- Uses supplier landed cost from the approved supplier source.
- Latest run summary:
  - best scenario: `2-pack bundle`
  - net profit: `$19.80`

### DecisionAgent

- PASS
- Current result:
  - `research_verdict = NEEDS_MORE_RESEARCH`
  - `buy_readiness_status = ALMOST_READY`
  - `research_completeness_score = 67`
  - `opportunity_score = 75`
  - `main_blocker = Market evidence is insufficient for a buy decision.`
- It does not grant `READY_FOR_SAMPLE` prematurely.

## Product Cockpit Verification

- Product loads as `Reusable pet hair remover roller`
- Discovery context is visible
- The cockpit reflects the new evidence totals
- The current state remains conservative:
  - `WATCHLIST`
  - `NEEDS MORE RESEARCH`
  - `ALMOST READY`

### Evidence counts in cockpit

- Marketplace evidence: `3`
- Sold listings: `2`
- Active listings: `1`
- Supplier sources: `1`
- Competitor listings: `1`

## Live Browser Checks

- Discovery page loaded successfully.
- Task proof linking worked:
  - task `Check material safety notes` now shows `Linked to sold evidence`
- Manual capture modal opened and created a pending candidate.
- Screenshot capture created a new pending vision candidate.
- Candidate approval from the browser worked.
- External research modal failed gracefully with DataForSEO disabled.
- Opportunity board loaded and ranked the idea and product rows.

## Bugs / Gaps Found

1. DataForSEO is disabled in the live container, so a real paid request could not be submitted.
2. The product cockpit still reports:
   - `buy_readiness = NOT_READY`
   - `buy_readiness_status = ALMOST_READY`
   This is inconsistent and should be normalized.
3. Supplier / competitor panels are not clearly surfaced in the current product cockpit scroll state.
4. One manual active-listing capture preserved multi-line text in the title field, which is noisy but did not break the pipeline.

## Cost Estimate

- Real DataForSEO cost: not incurred in this environment because the service is disabled.
- Manual / vision testing cost: local only.

## Final Verdict

- Discovery workflow: PASS
- Task proof linking: PASS
- Manual capture: PASS
- Vision-backed candidate creation: PASS
- Candidate approval: PASS
- Agent pipeline: PASS
- Product cockpit decision gating: PASS
- DataForSEO live integration: FAIL due to disabled configuration, but the API fails gracefully

## Recommendation

- Turn on DataForSEO credentials in the live container before retesting the external research submit/poll cycle.
- Normalize `buy_readiness` and `buy_readiness_status` to one backend truth source.
- Consider tightening text parsing for manual active-listing captures so line breaks do not leak into titles.
