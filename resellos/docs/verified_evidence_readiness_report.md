# Verified Evidence Readiness Report

Date: 2026-05-06

## What changed

- `MarketAgent` now computes counts and price medians from verified evidence only.
- `DecisionAgent` now blocks sample readiness when evidence is unverified or test-only.
- `DecisionAgent` now requires a verified supplier source and at least one verified competitor listing.
- `CompetitionAgent` now tracks verified competitor evidence separately from total listings.
- `ResearchPipelineService` now prefers verified supplier sources when choosing the primary source.
- `ProfitAgent` already prefers single-unit scenarios for the primary profit number; regression tests now lock that in.

## Validation

Backend tests pass:

`PYTHONPATH=. python -m unittest discover -s tests`

Live research runs after the rebuild:

- `Reusable pet hair remover roller`
  - `research_verdict`: `WEAK_IDEA`
  - `buy_readiness_status`: `NOT_READY`
  - `main_blocker`: `Evidence is not verified.`
- `Pet grooming glove`
  - `research_verdict`: `NEEDS_MORE_RESEARCH`
  - `buy_readiness_status`: `NOT_READY`
  - `main_blocker`: `Evidence is not verified.`
- `Collapsible dog travel bowl`
  - `research_verdict`: `WEAK_IDEA`
  - `buy_readiness_status`: `NOT_READY`
  - `main_blocker`: `Evidence is not verified.`

## Why this is better

The app no longer uses raw evidence volume as a proxy for readiness. Test data, unverified manual capture, and unverified competitor/supplier rows do not unlock `READY_FOR_SAMPLE`.

## Remaining requirement before sample buying

For a product to move to `READY_FOR_SAMPLE`, the backend now expects:

- at least 5 verified sold listings
- at least 5 verified active listings
- a verified supplier source
- verified competitor evidence
- no test-data blocker
- non-blocked risk
- positive profit and margin thresholds

