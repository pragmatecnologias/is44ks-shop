# ResellOS MCP Tool Reference

## Read tools

- `resellos_get_discovery_board`
- `resellos_list_evidence_candidates`
- `resellos_get_product_cockpit`
- `resellos_get_next_research_action`
- `resellos_generate_product_research_report`

## Write tools

- `resellos_create_discovery_idea`
- `resellos_run_quick_scan`
- `resellos_generate_research_tasks`
- `resellos_capture_manual_evidence`
- `resellos_run_product_research`
- `resellos_reject_candidate`

## Controlled paid tools

- `resellos_run_dataforseo_google_shopping`
- `resellos_poll_external_research_job`

## Verification tools

- `resellos_verify_marketplace_evidence`
- `resellos_verify_supplier_source`
- `resellos_verify_competitor_listing`

## Guardrails

- DataForSEO stays standard queue and low result count.
- Verification requires proof fields.
- Readiness decisions remain backend-owned.
