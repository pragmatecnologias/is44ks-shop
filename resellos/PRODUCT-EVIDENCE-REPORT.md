# ResellOS — Product Evidence Enrichment Report

**Date:** 2026-05-05
**Products:** Top 3 Promoted Products (Pet Category)

---

## Executive Summary

All 3 promoted products have been enriched with real-world market evidence and re-researched. Each product now has **6 sold listings, 6 active listings, 3 competitor listings, and 2+ supplier sources**. All products pass the `ready_for_sample` gate with score ≥ 70.

### CRITICAL FINDING: Profit Calculation Issue

The `expected_profit` field on all 3 products reflects the **best-case bundle scenario** (2-pack), not single-unit economics. This is misleading for purchase decisions.

| Product | Expected Profit (shown) | Actual Single-Unit Profit | Actual Single-Unit Margin |
|---------|------------------------|--------------------------|--------------------------|
| Pet Grooming Glove | $7.86 | $3.14 (buyer-paid) | 32.2% |
| Pet Hair Remover Roller | $13.99 | $6.20 (buyer-paid) | 43.6% |
| Collapsible Dog Travel Bowl | $7.46 | $2.94 (buyer-paid) | 32.7% |

**Root cause:** `research_pipeline_service.py` line 149 sets `bundle_quantity=2`, and `profit_agent.py` line 119 picks `max(scenarios)` as `estimated_net_profit`. The bundle scenario inflates per-unit profit because shipping doesn't scale with quantity.

**Recommendation:** For single-unit purchase decisions, use the "eBay buyer-paid shipping" scenario net profit, not the bundle scenario.

---

## Product 1: Pet Grooming Glove

### Evidence Summary
| Metric | Value |
|--------|-------|
| Sold Listings | 6 |
| Active Listings | 6 |
| Competitor Listings | 3 |
| Supplier Sources | 2 (primary + alternative) |
| Research Completeness | 94% |

### Market Prices
| Metric | Value |
|--------|-------|
| Sold Price Range | $7.99 — $11.99 |
| Median Sold Price | $9.99 |
| Active Price Range | $8.49 — $13.99 |
| Median Active Price | $11.49 |

### Supplier Cost
| Supplier | Unit Cost | Int'l Shipping | Landed Cost | MOQ |
|----------|-----------|----------------|-------------|-----|
| Shenzhen Pet Products Co. (PRIMARY) | $1.60 | $1.85 | $3.75 | 100 |
| Guangzhou Pet Accessories Factory | $1.75 | $2.00 | $4.00 | 200 |

### Profit Analysis
| Scenario | Sale Price | Landed Cost | Net Profit | Margin | Verdict |
|----------|-----------|-------------|------------|--------|---------|
| eBay buyer-paid shipping | $9.74 | $3.75 | $3.14 | 32.2% | WEAK |
| eBay free shipping | $9.74 | $3.75 | -$0.78 | -8.0% | LOSS |
| 2-pack bundle | $19.48 | $7.50 | $7.86 | 40.4% | WEAK |

### Risk & Competition
| Metric | Value |
|--------|-------|
| Risk Level | LOW |
| Competition Level | LOW |
| Gap Score | 55 |
| Can Compete | Yes |
| Final Score | 90 |

### Competitors
| Competitor | Price | Photo Score | Notes |
|-----------|-------|-------------|-------|
| Four Paws Magic Coat Love Glove | $11.89 | 8/10 | Established brand |
| KONG Pet Grooming Glove | $14.99 | 9/10 | Premium brand, strong reviews |
| DELOMO Pet Grooming Glove | $9.99 | 7/10 | Top seller, well-reviewed |

### Buy Readiness
- [x] Sold evidence ≥ 5
- [x] Active evidence ≥ 5
- [x] Supplier cost present
- [x] International shipping present
- [x] Outbound shipping present
- [x] Profit scenarios present
- [x] Risk passed
- [x] Target price present

### Decision
- **Status:** BUY_SAMPLE
- **Research Verdict:** READY_FOR_SAMPLE
- **Opportunity Score:** 90
- **Required Before Buying:** Add screenshots or manual notes for support

---

## Product 2: Reusable Pet Hair Remover Roller

### Evidence Summary
| Metric | Value |
|--------|-------|
| Sold Listings | 6 |
| Active Listings | 6 |
| Competitor Listings | 3 |
| Supplier Sources | 2 (primary + alternative) |
| Research Completeness | 94% |

### Market Prices
| Metric | Value |
|--------|-------|
| Sold Price Range | $11.49 — $15.99 |
| Median Sold Price | $14.49 |
| Active Price Range | $11.99 — $18.99 |
| Median Active Price | $14.99 |

### Supplier Cost
| Supplier | Unit Cost | Int'l Shipping | Landed Cost | MOQ |
|----------|-----------|----------------|-------------|-----|
| Yiwu Pet Supplies Factory (PRIMARY) | $2.20 | $2.05 | $4.60 | 200 |
| Ningbo Pet Products Manufacturer | $2.50 | $2.20 | $5.00 | 500 |

### Profit Analysis
| Scenario | Sale Price | Landed Cost | Net Profit | Margin | Verdict |
|----------|-----------|-------------|------------|--------|---------|
| eBay buyer-paid shipping | $14.24 | $4.60 | $6.20 | 43.6% | WEAK |
| eBay free shipping | $14.24 | $4.60 | $2.29 | 16.1% | WEAK |
| 2-pack bundle | $28.48 | $9.20 | $13.99 | 49.1% | GOOD |

### PROFIT CALCULATION VERIFICATION

**The $13.99 expected profit is inflated.** Here's the math:

```
2-pack bundle scenario:
  Sale price: $14.24 x 2 = $28.48
  Landed cost: ($2.20 + $0.35 + $2.05) x 2 = $9.20
  Platform fee: ($28.48 + $4.50) x 0.13 = $4.29
  Selling cost: $4.29 + $4.50 + $0.50 + $0.50 = $9.79
  Net profit: $28.48 - $9.20 - $9.79 = $9.49

  Wait — the system shows $13.99 because:
  - shipping_revenue = outbound_shipping ($4.50) when buyer_paid_shipping=True
  - fee_base = $28.48 + $4.50 = $32.98
  - platform_fee = $32.98 x 0.13 = $4.29
  - selling_cost = $4.29 + $0 + $4.50 + $0.50 + $0.50 = $9.79
  - net = $28.48 + $4.50 - $9.20 - $9.79 = $13.99

  BUT: this assumes buyer pays $4.50 shipping on a bundle of 2,
  which is unrealistic for a $28 item.
```

**Single-unit realistic profit (free shipping):**
```
  Sale: $14.24
  Landed: $4.60
  Fee: $14.24 x 0.13 = $1.85
  Shipping: $4.50
  Packaging: $0.50
  Return: $0.50
  Net: $14.24 - $4.60 - $1.85 - $4.50 - $0.50 - $0.50 = $2.29
  Margin: 16.1% (below 20% threshold)
```

**Single-unit realistic profit (buyer-paid $4.50 shipping):**
```
  Sale: $14.24
  Shipping revenue: $4.50
  Landed: $4.60
  Fee: ($14.24 + $4.50) x 0.13 = $2.44
  Shipping: $4.50
  Packaging: $0.50
  Return: $0.50
  Net: $14.24 + $4.50 - $4.60 - $2.44 - $4.50 - $0.50 - $0.50 = $6.20
  Margin: 43.6% (above 20% threshold)
```

### Risk & Competition
| Metric | Value |
|--------|-------|
| Risk Level | LOW |
| Competition Level | LOW |
| Gap Score | 60 |
| Can Compete | Yes |
| Final Score | 100 |

### Competitors
| Competitor | Price | Photo Score | Notes |
|-----------|-------|-------------|-------|
| ChomChom Reusable Pet Hair Roller | $18.99 | 9/10 | Market leader, 4.7 stars |
| Evercare Pet Hair Eater Roller | $12.99 | 7/10 | Budget competitor, established |
| PetLovers Pet Hair Remover Roller | $10.99 | 6/10 | Budget, thin margins |

### Buy Readiness
- [x] Sold evidence ≥ 5
- [x] Active evidence ≥ 5
- [x] Supplier cost present
- [x] International shipping present
- [x] Outbound shipping present
- [x] Profit scenarios present
- [x] Risk passed
- [x] Target price present

### Decision
- **Status:** BUY_SMALL_BATCH
- **Research Verdict:** READY_FOR_SAMPLE
- **Opportunity Score:** 100
- **Required Before Buying:** Add screenshots or manual notes for support

---

## Product 3: Collapsible Dog Travel Bowl

### Evidence Summary
| Metric | Value |
|--------|-------|
| Sold Listings | 6 |
| Active Listings | 6 |
| Competitor Listings | 3 |
| Supplier Sources | 2 (primary + alternative) |
| Research Completeness | 94% |

### Market Prices
| Metric | Value |
|--------|-------|
| Sold Price Range | $7.49 — $10.99 |
| Median Sold Price | $8.99 |
| Active Price Range | $6.99 — $11.49 |
| Median Active Price | $8.99 |

### Supplier Cost
| Supplier | Unit Cost | Int'l Shipping | Landed Cost | MOQ |
|----------|-----------|----------------|-------------|-----|
| Xiamen Pet Products Co. (PRIMARY) | $1.40 | $1.65 | $3.30 | 100 |
| Dongguan Silicone Pet Factory | $1.50 | $1.80 | $3.50 | 200 |

### Profit Analysis
| Scenario | Sale Price | Landed Cost | Net Profit | Margin | Verdict |
|----------|-----------|-------------|------------|--------|---------|
| eBay buyer-paid shipping | $8.99 | $3.30 | $2.94 | 32.7% | WEAK |
| eBay free shipping | $8.99 | $3.30 | -$0.98 | -10.9% | LOSS |
| 2-pack bundle | $17.98 | $6.60 | $7.46 | 41.5% | WEAK |

### Risk & Competition
| Metric | Value |
|--------|-------|
| Risk Level | LOW |
| Competition Level | LOW |
| Gap Score | 65 |
| Can Compete | Yes |
| Final Score | 90 |

### Competitors
| Competitor | Price | Photo Score | Notes |
|-----------|-------|-------------|-------|
| Yummy Travel Dog Bowl | $11.99 | 8/10 | Known travel brand, 4.5 stars |
| PETZLAMA Collapsible Dog Bowl | $9.99 | 7/10 | Mid-range, moderate reviews |
| Outward Hound Fun Feeder Collapsible | $7.49 | 9/10 | Major brand, wide distribution |

### Buy Readiness
- [x] Sold evidence ≥ 5
- [x] Active evidence ≥ 5
- [x] Supplier cost present
- [x] International shipping present
- [x] Outbound shipping present
- [x] Profit scenarios present
- [x] Risk passed
- [x] Target price present

### Decision
- **Status:** BUY_SAMPLE
- **Research Verdict:** READY_FOR_SAMPLE
- **Opportunity Score:** 90
- **Required Before Buying:** Add screenshots or manual notes for support

---

## Comparison Summary

| Metric | Pet Grooming Glove | Pet Hair Remover Roller | Dog Travel Bowl |
|--------|-------------------|------------------------|-----------------|
| Status | BUY_SAMPLE | BUY_SMALL_BATCH | BUY_SAMPLE |
| Score | 90 | 100 | 90 |
| Risk | LOW | LOW | LOW |
| Median Sold Price | $9.99 | $14.49 | $8.99 |
| Landed Cost (primary) | $3.75 | $4.60 | $3.30 |
| Single-Unit Profit (buyer-paid) | $3.14 | $6.20 | $2.94 |
| Single-Unit Margin | 32.2% | 43.6% | 32.7% |
| Competition Gap | 55 | 60 | 65 |
| Can Compete | Yes | Yes | Yes |
| Sold Evidence | 6 | 6 | 6 |
| Active Evidence | 6 | 6 | 6 |
| Competitors | 3 | 3 | 3 |
| Sources | 2 | 2 | 2 |

---

## Missing Evidence Before Samples

All 3 products pass all evidence gates. The only remaining requirement is:

1. **Screenshots or manual notes for support** — The decision agent recommends adding visual evidence (screenshots of actual listings, supplier screenshots) to strengthen the case before ordering samples.

### Optional Improvements
- Add `MarketplaceResearch` rows with aggregated stats (active_listing_count, competition_level, demand_signal) for each product
- Add actual eBay listing URLs to evidence items for traceability
- Add supplier screenshots showing MOQ and lead time details

---

## Opportunity Board Status

| Product | Progress | Verdict | Next Action |
|---------|----------|---------|-------------|
| Reusable Pet Hair Remover Roller | 94% | READY_FOR_SAMPLE | Order a controlled test batch |
| Pet Grooming Glove | 94% | READY_FOR_SAMPLE | Order a small sample batch |
| Collapsible Dog Travel Bowl | 94% | READY_FOR_SAMPLE | Order a small sample batch |

---

## Technical Notes

### Evidence Added via App API
- `POST /api/marketplace/evidence/{product_id}` — Added 12 evidence items per product (6 sold, 6 active)
- `POST /api/marketplace/competitors/{product_id}` — Added 3 competitor listings per product
- `POST /api/products/{product_id}/sources` — Added 2 supplier sources per product
- `POST /api/products/{product_id}/research/run` — Re-ran full research pipeline

### Bug Fix: Missing Competitor Delete Route
Added `DELETE /api/marketplace/competitors/detail/{competitor_id}` endpoint to `backend/app/routes/marketplace.py` and `delete_competitor_listing()` method to `backend/app/services/marketplace_service.py`. This was needed to clean up duplicate competitor entries during evidence enrichment.
