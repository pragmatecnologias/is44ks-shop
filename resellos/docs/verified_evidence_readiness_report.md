# Verified Evidence Readiness Report

Date: 2026-05-06

## What changed

- `MarketAgent` now computes counts and price medians from verified evidence only.
- `DecisionAgent` now blocks sample readiness when evidence is unverified or test-only.
- `DecisionAgent` now requires a verified supplier source and at least 3 verified competitor listings.
- `CompetitionAgent` now tracks verified competitor evidence separately from total listings.
- `ResearchPipelineService` now prefers verified supplier sources when choosing the primary source.
- `ProfitAgent` already prefers single-unit scenarios for the primary profit number; regression tests now lock that in.
- `MarketAgent` now uses verified sold evidence for sold medians and verified active evidence for active medians.

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

## Live cockpit check

After the backend rebuild and live API rerun:

- Roller remains blocked because verified sold evidence is `0`, verified active evidence is `0`, supplier verification is missing, and competitor verification is missing.
- Glove remains `NEEDS_MORE_RESEARCH` with only partial active market presence and no verified sold evidence.
- Bowl remains `WEAK_IDEA` or `NOT_READY` because the economics are still weak and the evidence is unverified.

## Why this is better

The app no longer uses raw evidence volume as a proxy for readiness. Test data, unverified manual capture, and unverified competitor/supplier rows do not unlock `READY_FOR_SAMPLE`, and the live cockpit now reflects the stricter verified-only medians.

## Remaining requirement before sample buying

For a product to move to `READY_FOR_SAMPLE`, the backend now expects:

- at least 5 verified sold listings
- at least 5 verified active listings
- a verified supplier source
- verified competitor evidence
- no test-data blocker
- non-blocked risk
- positive profit and margin thresholds
