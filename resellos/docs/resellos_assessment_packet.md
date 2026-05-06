# ResellOS Assessment Packet

Assessment date: `2026-05-06`

This packet documents the current workspace state for verified evidence, product research readiness, DataForSEO, agents, and the current pet research dataset.

## 1. Git Identity

Command:
```bash
git rev-parse HEAD
git branch --show-current
git status --short
git log --oneline -5
git remote -v
```

Outputs:
```text
fcc69dfa769d02e0b2b2929c3a13531f243409fb
main

fcc69df Changes
7c4575f Changes
77cd443 Changes
6f9d00d Changes
2f086fe Changes
origin	https://github.com/pragmatecnologias/is44ks-shop.git (fetch)
origin	https://github.com/pragmatecnologias/is44ks-shop.git (push)
```

`git diff --stat` output:
```text
```

Post-write workspace status:
```text
?? resellos/docs/resellos_assessment_packet.md
```

Post-write `git diff --stat` output:
```text
```

## 2. Runtime Verification

### Backend test and compile checks

Command:
```bash
cd resellos/backend
PYTHONPATH=. python -m unittest discover -s tests
python -m compileall app
alembic current
alembic heads
```

`PYTHONPATH=. python -m unittest discover -s tests`
```text
......./opt/homebrew/anaconda3/lib/python3.13/site-packages/sqlalchemy/sql/schema.py:3616: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  return util.wrap_callable(lambda ctx: fn(), fn)  # type: ignore
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/services/discovery_service.py:330: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  idea.updated_at = datetime.utcnow()
........./opt/homebrew/anaconda3/lib/python3.13/site-packages/sqlalchemy/util/langhelpers.py:1312: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x109da6980>
  value = getattr(self, f"_memoized_attr_{key}")()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/opt/homebrew/anaconda3/lib/python3.13/site-packages/sqlalchemy/util/langhelpers.py:1312: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a0a5990>
  value = getattr(self, f"_memoized_attr_{key}")()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
./Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/services/external_research_service.py:74: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  cutoff = datetime.utcnow() - timedelta(days=30)
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/services/external_research_service.py:83: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  return datetime.utcnow() - timedelta(days=settings.DATAFORSEO_CACHE_DAYS)
../opt/homebrew/anaconda3/lib/python3.13/site-packages/sqlalchemy/sql/schema.py:411: ResourceWarning: unclosed database in <sqlite3.Connection object at 0x10a0a4220>
  def _gen_cache_key(
ResourceWarning: Enable tracemalloc to get the object allocation traceback
.
----------------------------------------------------------------------
Ran 20 tests in 0.069s

OK
```

`python -m compileall app`
```text
Listing 'app'...
Listing 'app/agents'...
Listing 'app/connectors'...
Listing 'app/connectors/dataforseo'...
Listing 'app/llm'...
Listing 'app/models'...
Listing 'app/prompts'...
Listing 'app/routes'...
Compiling 'app/routes/marketplace.py'...
Compiling 'app/routes/research.py'...
Listing 'app/schemas'...
Listing 'app/services'...
Compiling 'app/services/capture_service.py'...
Compiling 'app/services/marketplace_service.py'...
Compiling 'app/services/research_pipeline_service.py'...
Listing 'app/vision'...
Listing 'app/vision_agents'...
```

`alembic current` on the host Python environment failed:
```text
Traceback (most recent call last):
  File "/opt/homebrew/anaconda3/bin/alembic", line 7, in <module>
    sys.exit(main())
             ~~~~^^
  File "/opt/homebrew/anaconda3/lib/python3.13/site-packages/alembic/config.py", line 1047, in main
    CommandLine(prog=prog).main(argv=argv)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^
  File "/opt/homebrew/anaconda3/lib/python3.13/site-packages/alembic/config.py", line 1037, in main
    self.run_cmd(cfg, options)
    ~~~~~~~~~~~~^^^^^^^^^^^^^^
  File "/opt/homebrew/anaconda3/lib/python3.13/site-packages/alembic/config.py", line 971, in run_cmd
    fn(
    ~~^
        config,
        ^^^^^^^
        *[getattr(options, k, None) for k in positional],
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        **{k: getattr(options, k, None) for k in kwarg},
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/opt/homebrew/anaconda3/lib/python3.13/site-packages/alembic/command.py", line 722, in current
    script.run_env()
    ~~~~~~~~~~~~~~^^
  File "/opt/homebrew/anaconda3/lib/python3.13/site-packages/alembic/script/base.py", line 545, in run_env
    util.load_python_file(self.dir, "env.py")
    ~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^
  File "/opt/homebrew/anaconda3/lib/python3.13/site-packages/alembic/util/pyfiles.py", line 116, in load_python_file
    module = load_module_py(module_id, path)
  File "/opt/homebrew/anaconda3/lib/python3.13/site-packages/alembic/util/pyfiles.py", line 136, in load_module_py
    spec.loader.exec_module(module)  # type: ignore
    ~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^
  File "<frozen importlib._bootstrap_external>", line 1026, in exec_module
  File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
  File "/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/migrations/env.py", line 52, in <module>
    run_migrations_online()
    ~~~~~~~~~~~~~~~~~~~~~^^
  File "/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/migrations/env.py", line 36, in run_migrations_online
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
  File "/opt/homebrew/anaconda3/lib/python3.13/site-packages/sqlalchemy/engine/create.py", line 823, in engine_from_config
    return create_engine(url, **options)
  File "<string>", line 2, in create_engine
  File "/opt/homebrew/anaconda3/lib/python3.13/site-packages/sqlalchemy/util/deprecations.py", line 281, in warned
    return fn(*args, **kwargs)  # type: ignore[no-any-return]
  File "/opt/homebrew/anaconda3/lib/python3.13/site-packages/sqlalchemy/engine/create.py", line 602, in create_engine
    dbapi = dbapi_meth(**dbapi_args)
  File "/opt/homebrew/anaconda3/lib/python3.13/site-packages/sqlalchemy/dialects/postgresql/psycopg2.py", line 696, in import_dbapi
    import psycopg2
ModuleNotFoundError: No module named 'psycopg2'
```

`docker compose exec -T backend alembic current`
```text
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
0007_evidence_verification (head)
```

`docker compose exec -T backend alembic heads`
```text
0007_evidence_verification (head)
```

### Frontend build

`npm run build`
```text
> resellos-frontend@0.1.0 build
> next build

  ▲ Next.js 14.2.5

   Creating an optimized production build ...
 ✓ Compiled successfully
   Linting and checking validity of types ...
   Collecting page data ...
   Generating static pages (0/15) ...
   Generating static pages (3/15) 
   Generating static pages (7/15) 
   Generating static pages (11/15) 
 ✓ Generating static pages (15/15)
   Finalizing page optimization ...
   Collecting build traces ...

Route (app)                              Size     First Load JS
┌ ○ /                                    136 B          87.3 kB
├ ○ /_not-found                          875 B            88 kB
├ ○ /capture                             2.15 kB         101 kB
├ ○ /dashboard                           4.89 kB         104 kB
├ ○ /discovery                           178 B           109 kB
├ ƒ /ideas                               178 B           109 kB
├ ○ /inventory                           1.85 kB          89 kB
├ ○ /listings                            1.68 kB        88.8 kB
├ ○ /opportunities                       1.95 kB        94.3 kB
├ ○ /products                            4.14 kB         103 kB
├ ƒ /products/[id]                       10.8 kB         110 kB
├ ○ /products/new                        2.46 kB         102 kB
├ ○ /sales                               1.63 kB        88.8 kB
└ ○ /settings                            1.76 kB        88.9 kB
+ First Load JS shared by all            87.1 kB
  ├ chunks/23-5ece9c03a68215b6.js        31.5 kB
  ├ chunks/fd9d1056-83701e137505fb90.js  53.7 kB
  └ other shared chunks (total)          1.94 kB


○  (Static)   prerendered as static content
ƒ  (Dynamic)  server-rendered on demand
```

## 3. MarketAgent Verified Evidence Proof

Current code excerpt from [resellos/backend/app/agents/market_agent.py](/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/agents/market_agent.py):

```python
        evidence_rows = evidence if isinstance(evidence, list) else []
        active_rows = [row for row in evidence_rows if str(row.get("evidence_type", "")).upper() == "ACTIVE_LISTING"]
        sold_rows = [row for row in evidence_rows if str(row.get("evidence_type", "")).upper() == "SOLD_LISTING"]
        supporting_rows = [row for row in evidence_rows if str(row.get("evidence_type", "")).upper() in {"SCREENSHOT", "MANUAL_NOTE"}]

        # Verification-aware filtering
        VERIFIED_SOLD = {"USER_VERIFIED"}
        VERIFIED_ACTIVE = {"USER_VERIFIED", "API_IMPORTED"}
        TEST = {"TEST_DATA", "REJECTED"}

        def _status(row: dict) -> str:
            return str(row.get("verification_status") or "").upper()

        verified_sold_rows = [row for row in sold_rows if _status(row) in VERIFIED_SOLD]
        verified_active_rows = [row for row in active_rows if _status(row) in VERIFIED_ACTIVE]
        test_data_count = sum(1 for row in evidence_rows if _status(row) == "TEST_DATA")
        verified_evidence_count = sum(1 for row in evidence_rows if _status(row) in VERIFIED_SOLD or _status(row) in VERIFIED_ACTIVE)
        unverified_evidence_count = sum(1 for row in evidence_rows if _status(row) not in VERIFIED_SOLD and _status(row) not in VERIFIED_ACTIVE and _status(row) not in TEST and _status(row) != "")

        active_listing_count = len(active_rows)
        sold_listing_count = len(sold_rows)
        verified_sold_count = len(verified_sold_rows)
        verified_active_count = len(verified_active_rows)

        active_prices_total = [float(row.get("price")) for row in active_rows if row.get("price") is not None]
        sold_prices_total = [float(row.get("price")) for row in sold_rows if row.get("price") is not None]
        active_shipping_prices_total = [float(row.get("shipping_price")) for row in active_rows if row.get("shipping_price") is not None]
        sold_shipping_prices_total = [float(row.get("shipping_price")) for row in sold_rows if row.get("shipping_price") is not None]

        verified_active_prices = [float(row.get("price")) for row in verified_active_rows if row.get("price") is not None]
        verified_sold_prices = [float(row.get("price")) for row in verified_sold_rows if row.get("price") is not None]
        verified_active_shipping_prices = [float(row.get("shipping_price")) for row in verified_active_rows if row.get("shipping_price") is not None]
        verified_sold_shipping_prices = [float(row.get("shipping_price")) for row in verified_sold_rows if row.get("shipping_price") is not None]

        active_price_range = [round(min(verified_active_prices), 2), round(max(verified_active_prices), 2)] if verified_active_prices else []
        sold_price_range = [round(min(verified_sold_prices), 2), round(max(verified_sold_prices), 2)] if verified_sold_prices else []
        active_price_range_total = [round(min(active_prices_total), 2), round(max(active_prices_total), 2)] if active_prices_total else []
        sold_price_range_total = [round(min(sold_prices_total), 2), round(max(sold_prices_total), 2)] if sold_prices_total else []
        median_active_price = _median(verified_active_prices)
        median_sold_price = _median(verified_sold_prices)
        median_active_shipping = _median(verified_active_shipping_prices)
        median_sold_shipping = _median(verified_sold_shipping_prices)
        median_active_price_total = _median(active_prices_total)
        median_sold_price_total = _median(sold_prices_total)
        median_active_shipping_total = _median(active_shipping_prices_total)
        median_sold_shipping_total = _median(sold_shipping_prices_total)
```

Output construction:

```python
                "verified_sold_listing_count": verified_sold_count,
                "verified_active_listing_count": verified_active_count,
                "total_evidence_count": len(evidence_rows),
                "verified_evidence_count": verified_evidence_count,
                "unverified_evidence_count": unverified_evidence_count,
                "test_data_evidence_count": test_data_count,
                "verification_coverage": round(verification_coverage, 2),
                "research_completeness_score": research_completeness_score,
                "median_active_price": median_active_price,
                "median_sold_price": median_sold_price,
                "median_active_price_total": median_active_price_total,
                "median_sold_price_total": median_sold_price_total,
                "median_active_shipping": median_active_shipping,
                "median_sold_shipping": median_sold_shipping,
                "median_active_shipping_total": median_active_shipping_total,
                "median_sold_shipping_total": median_sold_shipping_total,
                "median_shipping": median_shipping,
                "active_price_range": active_price_range,
                "sold_price_range": sold_price_range,
                "active_price_range_total": active_price_range_total,
                "sold_price_range_total": sold_price_range_total,
```

`grep -n "VERIFIED_SOLD\|VERIFIED_ACTIVE\|active_price_range_total\|sold_price_range_total\|median_sold_price_total\|median_active_price_total" resellos/backend/app/agents/market_agent.py`
```text
59:        VERIFIED_SOLD = {"USER_VERIFIED"}
60:        VERIFIED_ACTIVE = {"USER_VERIFIED", "API_IMPORTED"}
66:        verified_sold_rows = [row for row in sold_rows if _status(row) in VERIFIED_SOLD]
67:        verified_active_rows = [row for row in active_rows if _status(row) in VERIFIED_ACTIVE]
69:        verified_evidence_count = sum(1 for row in evidence_rows if _status(row) in VERIFIED_SOLD or _status(row) in VERIFIED_ACTIVE)
70:        unverified_evidence_count = sum(1 for row in evidence_rows if _status(row) not in VERIFIED_SOLD and _status(row) not in VERIFIED_ACTIVE and _status(row) not in TEST and _status(row) != "")
89:        active_price_range_total = [round(min(active_prices_total), 2), round(max(active_prices_total), 2)] if active_prices_total else []
90:        sold_price_range_total = [round(min(sold_prices_total), 2), round(max(sold_prices_total), 2)] if sold_prices_total else []
95:        median_active_price_total = _median(active_prices_total)
96:        median_sold_price_total = _median(sold_prices_total)
189:                "median_active_price_total": median_active_price_total,
190:                "median_sold_price_total": median_sold_price_total,
198:                "active_price_range_total": active_price_range_total,
199:                "sold_price_range_total": sold_price_range_total,
```

`MISSING` note:
- The identifiers `active_prices` and `sold_prices` do not exist in the current live code; the file uses `active_prices_total`, `sold_prices_total`, `verified_active_prices`, and `verified_sold_prices`.

## 4. MarketAgent Schema Proof

Current schema excerpt from [resellos/backend/app/schemas/agent_schema.py](/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/schemas/agent_schema.py):

```python
class MarketAgentOutput(BaseModel):
    evidence_quality: Literal["LOW", "MEDIUM", "HIGH"] = "LOW"
    insufficient_data: bool = True
    market_price_missing: bool = True
    supporting_evidence_count: int = 0
    active_listing_count: int = 0
    sold_listing_count: int = 0
    verified_sold_listing_count: int = 0
    verified_active_listing_count: int = 0
    total_evidence_count: int = 0
    verified_evidence_count: int = 0
    unverified_evidence_count: int = 0
    test_data_evidence_count: int = 0
    verification_coverage: float = 0.0
    research_completeness_score: int = 0
    demand_signal: Literal["LOW", "MEDIUM", "HIGH", "UNKNOWN"] = "UNKNOWN"
    demand_evidence_quality: Literal["LOW", "MEDIUM", "HIGH", "UNKNOWN"] = "UNKNOWN"
    market_presence_quality: Literal["LOW", "MEDIUM", "HIGH", "UNKNOWN"] = "UNKNOWN"
    competition_level: Literal["LOW", "MEDIUM", "HIGH", "UNKNOWN"] = "UNKNOWN"
    median_active_price: float | None = None
    median_sold_price: float | None = None
    median_active_price_total: float | None = None
    median_sold_price_total: float | None = None
    median_active_shipping: float | None = None
    median_sold_shipping: float | None = None
    median_active_shipping_total: float | None = None
    median_sold_shipping_total: float | None = None
    median_shipping: float | None = None
    active_price_range: list[float] = Field(default_factory=list)
    sold_price_range: list[float] = Field(default_factory=list)
    active_price_range_total: list[float] = Field(default_factory=list)
    sold_price_range_total: list[float] = Field(default_factory=list)
```

`grep -n "active_price_range_total\|sold_price_range_total\|median_sold_price_total\|verified_sold_listing_count" resellos/backend/app/schemas/agent_schema.py`
```text
47:    verified_sold_listing_count: int = 0
62:    median_sold_price_total: float | None = None
70:    active_price_range_total: list[float] = Field(default_factory=list)
71:    sold_price_range_total: list[float] = Field(default_factory=list)
```

## 5. DecisionAgent Verified Gate Proof

Current excerpt from [resellos/backend/app/agents/decision_agent.py](/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/agents/decision_agent.py):

```python
        verified_sold = int(market.get("verified_sold_listing_count", 0) or 0)
        verified_active = int(market.get("verified_active_listing_count", 0) or 0)
        test_data_count = int(market.get("test_data_evidence_count", 0) or 0)
        competition_level = str(competition.get("competition_level", "UNKNOWN")).upper()
        listing_gap_score = int(competition.get("listing_gap_score", 0) or 0)
        can_compete = bool(competition.get("can_compete", True))
        verified_competitor_count = int(competition.get("verified_competitor_count", 0) or 0)
        ...
        supplier_verification_status = str(supplier_summary.get("verification_status") or "").upper()
        supplier_verified = supplier_verification_status == "USER_VERIFIED"
```

Readiness gate:

```python
        ready_for_sample = (
            not blocked
            and risk_level != "BLOCKED"
            and verified_sold >= 5
            and verified_active >= 5
            and unverified_evidence_count == 0
            and test_data_count == 0
            and verification_coverage >= 1.0
            and has_supplier_cost
            and supplier_verified
            and not market_price_missing
            and target_sale_price > 0
            and net_profit >= min_profit
            and best_margin >= min_margin
            and score >= 70
            and competition.get("can_compete", True)
            and verified_competitor_count >= 3
        )
```

Blocker text:

```python
        if not supplier_verified:
            if recommendation in {"BUY_SAMPLE", "BUY_SMALL_BATCH", "REORDER", "SCALE"}:
                recommendation = "WATCHLIST"
            hard_blockers.append("Supplier cost is not verified.")
            required_before_buying.append("Verify supplier URL, screenshot, unit cost, shipping, and landed cost.")
            if research_verdict == "READY_FOR_SAMPLE":
                research_verdict = "NEEDS_MORE_RESEARCH"

        if unverified_evidence_count > 0 or test_data_count > 0 or verification_coverage < 1.0:
            verification_blocker = "Evidence is not verified."
            if verification_blocker not in hard_blockers:
                hard_blockers.append(verification_blocker)
            required_before_buying.append("Verify evidence before sample buying.")
```

`grep -n "has_verified_supplier\|verified_competitor_count\|Evidence is not verified\|Supplier cost is not verified\|verified_sold" resellos/backend/app/agents/decision_agent.py`
```text
47:        verified_sold = int(market.get("verified_sold_listing_count", 0) or 0)
53:        verified_competitor_count = int(competition.get("verified_competitor_count", 0) or 0)
65:        supplier_verified = supplier_verification_status == "USER_VERIFIED"
72:        research_completeness_score += min(25, verified_sold * 5)
80:        if supplier_verified and verified_competitor_count >= 3 and verification_coverage >= 1.0:
126:        if verified_sold == 0:
147:        if verified_competitor_count < 3:
164:            and verified_sold >= 5
177:            and verified_competitor_count >= 3
252:            hard_blockers.append("Supplier cost is not verified.")
258:            verification_blocker = "Evidence is not verified."
286:            and verified_competitor_count >= 3
```

## 6. CompetitionAgent Verified Competitor Proof

Current excerpt from [resellos/backend/app/agents/competition_agent.py](/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/agents/competition_agent.py):

```python
        listings = competitor_listings if isinstance(competitor_listings, list) else []
        VERIFIED = {"USER_VERIFIED", "API_IMPORTED"}

        def _status(row: dict[str, Any]) -> str:
            return str(row.get("verification_status") or "").upper()

        verified_listings = [row for row in listings if _status(row) in VERIFIED]
        unverified_listings = [row for row in listings if row not in verified_listings]
        verified_prices = [float(row.get("price")) for row in verified_listings if row.get("price") is not None]
        verified_photo_scores = [float(row.get("photo_score")) for row in verified_listings if row.get("photo_score") is not None]
        verified_title_scores = [float(row.get("title_score")) for row in verified_listings if row.get("title_score") is not None]
        verified_description_scores = [float(row.get("description_score")) for row in verified_listings if row.get("description_score") is not None]
        verified_sold_count = sum(1 for row in verified_listings if bool(row.get("sold")))
        verified_active_count = len(verified_listings) - verified_sold_count
        ...
        can_compete = gap_score >= 55 and bool(verified_listings)
```

`grep -n "verified_competitor_count\|verified_listings\|can_compete" resellos/backend/app/agents/competition_agent.py`
```text
54:        verified_listings = [row for row in listings if _status(row) in VERIFIED]
55:        unverified_listings = [row for row in listings if row not in verified_listings]
69:        verification_coverage = (len(verified_listings) / len(listings)) if listings else 0.0
77:        elif not verified_listings:
121:        can_compete = gap_score >= 55 and bool(verified_listings)
137:                "can_compete": can_compete,
139:                "verified_competitor_count": len(verified_listings),
140:                "unverified_competitor_count": len(unverified_listings),
156:                "confidence": "HIGH" if verified_listings and gap_score >= 55 else "MEDIUM" if verified_listings else "LOW",
```

## 7. ResearchPipelineService Serialization Proof

Current excerpt from [resellos/backend/app/services/research_pipeline_service.py](/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/services/research_pipeline_service.py):

```python
    def _serialize_competitor(self, row: CompetitorListing) -> dict[str, Any]:
        return {
            "marketplace": row.marketplace,
            "title": row.title,
            "url": row.url,
            "price": float(row.price) if row.price is not None else None,
            "shipping_price": float(row.shipping_price) if row.shipping_price is not None else None,
            "sold": row.sold,
            "verification_status": row.verification_status,
            "notes": row.notes,
        }

    def _serialize_evidence(self, row: MarketplaceEvidence) -> dict[str, Any]:
        return {
            "marketplace": row.marketplace,
            "evidence_type": row.evidence_type,
            "title": row.title,
            "url": row.url,
            "price": float(row.price) if row.price is not None else None,
            "shipping_price": float(row.shipping_price) if row.shipping_price is not None else None,
            "source_method": row.source_method,
            "verification_status": row.verification_status,
            "raw_text": row.raw_text,
            "confidence": row.confidence,
        }

    def _serialize_source(self, source: ProductSource | None) -> dict[str, Any]:
        if not source:
            return {}
        return {
            "supplier_name": source.supplier_name,
            "supplier_platform": source.supplier_platform,
            "supplier_url": source.supplier_url,
            "unit_cost": float(source.unit_cost) if source.unit_cost is not None else None,
            "domestic_shipping": float(source.domestic_shipping) if source.domestic_shipping is not None else None,
            "international_shipping_estimate": float(source.international_shipping_estimate) if source.international_shipping_estimate is not None else None,
            "estimated_landed_cost": float(source.estimated_landed_cost) if source.estimated_landed_cost is not None else None,
            "moq": source.moq,
            "supplier_rating": source.supplier_rating,
            "notes": source.notes,
            "is_primary": source.is_primary,
            "verification_status": source.verification_status,
        }

    def _primary_source(self, sources: list[ProductSource]) -> ProductSource | None:
        if not sources:
            return None
        verified_statuses = {"USER_VERIFIED", "API_IMPORTED"}
        verified_sources = [source for source in sources if str(source.verification_status or "").upper() in verified_statuses]
        if verified_sources:
            return next((source for source in verified_sources if source.is_primary), verified_sources[0])
        return next((source for source in sources if source.is_primary), sources[0])
```

`grep -n "verification_status\|USER_VERIFIED\|_serialize_evidence\|_serialize_source\|_serialize_competitor" resellos/backend/app/services/research_pipeline_service.py`
```text
78:                "competitor_listings": [self._serialize_competitor(row) for row in competitor_rows],
107:                "competitor_listings": [self._serialize_competitor(row) for row in competitor_rows],
108:                "marketplace_evidence": [self._serialize_evidence(row) for row in evidence_rows],
120:                "competitor_listings": [self._serialize_competitor(row) for row in competitor_rows],
121:                "marketplace_evidence": [self._serialize_evidence(row) for row in evidence_rows],
177:                "supplier_summary": self._serialize_source(primary_source) if primary_source else {},
188:                "supplier_summary": self._serialize_source(primary_source) if primary_source else {},
192:                "competitor_listings": [self._serialize_competitor(row) for row in competitor_rows],
258:    def _serialize_competitor(self, row: CompetitorListing) -> dict[str, Any]:
266:            "verification_status": row.verification_status,
270:    def _serialize_evidence(self, row: MarketplaceEvidence) -> dict[str, Any]:
279:            "verification_status": row.verification_status,
310:    def _serialize_source(self, source: ProductSource | None) -> dict[str, Any]:
325:            "verification_status": source.verification_status,
331:        verified_statuses = {"USER_VERIFIED", "API_IMPORTED"}
332:        verified_sources = [source for source in sources if str(source.verification_status or "").upper() in verified_statuses]
```

## 8. ProfitAgent Single-Unit Proof

Current excerpt from [resellos/backend/app/agents/profit_agent.py](/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/agents/profit_agent.py):

```python
        scenarios = [buyer_paid, free_ship, bundle]
        # Prefer single-unit scenarios for the primary estimated_net_profit.
        # Bundle scenarios inflate profit because shipping doesn't scale.
        single_unit_scenarios = [s for s in scenarios if "bundle" not in s["name"].lower()]
        best = max(single_unit_scenarios or scenarios, key=lambda item: float(item["net_profit"]))
        break_even = float(best["landed_cost"]) + float(best["selling_cost"])
        minimum_recommended_price = round(break_even * 1.1, 2)
        market_reference_price = sale_price if sale_price > 0 else 0
        target_sale_price = sale_price if sale_price > 0 else 0

        output = ProfitAgentOutput.model_validate(
            {
                "scenarios": [ProfitScenario.model_validate(item).model_dump() for item in scenarios],
                "estimated_net_profit": float(best["net_profit"]),
                "break_even_price": round(break_even, 2),
                "minimum_recommended_price": minimum_recommended_price,
                "target_sale_price": round(target_sale_price, 2),
                "market_reference_price": round(market_reference_price, 2),
                "best_scenario": str(best["name"]),
            }
        )
```

`grep -n "single_unit_scenarios\|bundle\|estimated_net_profit\|best =" resellos/backend/app/agents/profit_agent.py`
```text
45:        bundle_quantity = max(int(input_data.get("bundle_quantity", 1) or 1), 1)
55:            bundle_multiplier: int = 1,
58:            unit_product_cost = product_cost * bundle_multiplier
59:            unit_china_domestic = china_domestic_shipping * bundle_multiplier
60:            unit_international = international_shipping * bundle_multiplier
61:            unit_duties = duties * bundle_multiplier
62:            unit_inspection = inspection_cost * bundle_multiplier
78:                "assumptions": assumptions or ([ "Bundle ships in one package" ] if bundle_multiplier > 1 else [ "Standard parcel shipping" ]),
105:        bundle = scenario(
106:            f"{bundle_quantity}-pack bundle",
110:            bundle_multiplier=bundle_quantity,
118:        scenarios = [buyer_paid, free_ship, bundle]
119:        # Prefer single-unit scenarios for the primary estimated_net_profit.
121:        single_unit_scenarios = [s for s in scenarios if "bundle" not in s["name"].lower()]
122:        best = max(single_unit_scenarios or scenarios, key=lambda item: float(item["net_profit"]))
131:                "estimated_net_profit": float(best["net_profit"]),
```

## 9. DataForSEO Correctness Proof

### Config defaults

Excerpt from [resellos/backend/app/config.py](/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/config.py):

```python
    VISION_LLM_PROVIDER: Literal["qwen_vl", "openai"] = "qwen_vl"
    VISION_LLM_BASE_URL: str = "http://localhost:1234/v1"
    VISION_LLM_MODEL: str = "Qwen/Qwen3-VL-8B-Instruct"
    VISION_LLM_TIMEOUT_SECONDS: int = 120
    VISION_LLM_API_KEY: str = ""
    VISION_MAX_IMAGE_MB: int = 8
    DATAFORSEO_ENABLED: bool = False
    DATAFORSEO_LOGIN: str = ""
    DATAFORSEO_PASSWORD: str = ""
    DATAFORSEO_QUEUE: Literal["standard", "priority"] = "standard"
    DATAFORSEO_LOCATION_CODE: int = 2840
    DATAFORSEO_LANGUAGE_CODE: str = "en"
    DATAFORSEO_MAX_RESULTS_PER_QUERY: int = 20
    DATAFORSEO_MAX_QUERIES_PER_IDEA: int = 3
    DATAFORSEO_CACHE_DAYS: int = 14
    DATAFORSEO_MONTHLY_BUDGET_USD: float = 25.0
```

### Connector and mapper code

`resellos/backend/app/connectors/dataforseo/client.py`
```python
class DataForSEOClient:
    def __init__(
        self,
        login: str,
        password: str,
        base_url: str = "https://api.dataforseo.com/v3",
        timeout_seconds: int = 120,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.client = httpx.Client(
            base_url=self.base_url,
            auth=httpx.BasicAuth(login, password),
            headers={"Content-Type": "application/json"},
            timeout=timeout_seconds,
        )

    def post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        response = self.client.post(path, json=payload)
        response.raise_for_status()
        return response.json()

    def get_json(self, path: str) -> dict[str, Any]:
        response = self.client.get(path)
        response.raise_for_status()
        return response.json()
```

`resellos/backend/app/connectors/dataforseo/merchant.py`
```python
    def submit_google_shopping_products_task(
        self,
        *,
        keyword: str,
        location_code: int,
        language_code: str,
        depth: int = 10,
        priority: int = 1,
        tag: str | None = None,
    ) -> dict[str, Any]:
        payload = [
            {
                "keyword": keyword,
                "location_code": location_code,
                "language_code": language_code,
                "depth": depth,
                "device": "desktop",
                "os": "windows",
                "priority": priority,
            }
        ]
        if tag:
            payload[0]["tag"] = tag
        return self.client.post_json("/merchant/google/products/task_post", payload)

    def get_google_shopping_products_result(self, task_id: str) -> dict[str, Any]:
        return self.client.get_json(f"/merchant/google/products/task_get/advanced/{task_id}")
```

`resellos/backend/app/connectors/dataforseo/mappers.py`
```python
    return {
        "source": "DATAFORSEO",
        "candidate_type": "MARKETPLACE_EVIDENCE",
        "marketplace": "Google Shopping",
        "evidence_type": "ACTIVE_LISTING",
        "title": item.get("title") or item.get("description"),
        "url": url,
        "price": _as_float(item.get("price")),
        "shipping_price": _as_float(delivery_price),
        "seller": seller,
        "rating": _as_float(rating_value),
        "review_count": _as_int(reviews_count),
        "image_url": image_url,
        "confidence": "MEDIUM" if item.get("title") else "LOW",
        "review_status": "PENDING",
        "raw_json": item,
    }
```

`resellos/backend/app/services/external_research_service.py`
```python
    def _require_enabled(self) -> None:
        if not settings.DATAFORSEO_ENABLED:
            raise HTTPException(status_code=503, detail="DataForSEO is disabled in configuration.")

    def _find_cached_job(
        self,
        *,
        idea_id: uuid.UUID | None,
        product_id: uuid.UUID | None,
        query: str,
    ) -> ExternalResearchJob | None:
        cutoff = self._cache_cutoff()
        query_obj = self.db.query(ExternalResearchJob).filter(
            ExternalResearchJob.provider == "DATAFORSEO",
            ExternalResearchJob.api_area == "MERCHANT_GOOGLE_PRODUCTS",
            ExternalResearchJob.query == query,
            ExternalResearchJob.created_at >= cutoff,
            ExternalResearchJob.status != "FAILED",
        )
        ...

        if not request.budget_override and self._recent_spend() + self._estimate_cost(1, max_results) > settings.DATAFORSEO_MONTHLY_BUDGET_USD:
            raise HTTPException(status_code=400, detail="DataForSEO monthly hard stop reached.")

        job = ExternalResearchJob(
            idea_id=idea_id,
            product_id=product_id,
            provider="DATAFORSEO",
            api_area="MERCHANT_GOOGLE_PRODUCTS",
            query=query,
            queue="standard",
            status="QUEUED",
            cost_estimate=self._estimate_cost(1, max_results),
            raw_request={"query": query, "max_results": max_results, "queue": queue},
        )
        ...
        response = self.client.submit_google_shopping_products_task(
            keyword=query,
            location_code=settings.DATAFORSEO_LOCATION_CODE,
            language_code=settings.DATAFORSEO_LANGUAGE_CODE,
            depth=max_results,
            priority=1,
            tag=str(job.id),
        )
        ...
        if status_code < 20000:
            job.status = "READY"
            ...
        candidates = self.create_candidates_from_job(job, response)
        job.result_count = len(candidates)
        job.status = "IMPORTED"
        ...

    def create_candidates_from_job(self, job: ExternalResearchJob, response: dict[str, Any]) -> list[EvidenceCandidate]:
        if job.candidates:
            return list(job.candidates)
        candidates: list[EvidenceCandidate] = []
        item_sources = list(iter_google_shopping_items(response))
        for item in item_sources:
            candidate_payload = map_google_shopping_item_to_candidate(item, source_job={"job_id": str(job.id), "query": job.query})
            ...
            candidate = EvidenceCandidate(
                job_id=job.id,
                idea_id=job.idea_id,
                product_id=job.product_id,
                source=candidate_payload["source"],
                candidate_type=candidate_payload["candidate_type"],
                marketplace=candidate_payload["marketplace"],
                evidence_type=candidate_payload["evidence_type"],
                ...
                review_status="PENDING",
                raw_json=raw_json,
            )
```

`resellos/backend/app/routes/external_research.py`
```python
@router.post("/google-shopping", response_model=ExternalResearchRunResponse)
@router.post("/dataforseo/google-shopping", response_model=ExternalResearchRunResponse)
def run_google_shopping(request: ExternalResearchRunRequest, db: Session = Depends(get_db)):
    ...

@router.get("/jobs", response_model=list[ExternalResearchJobResponse])
def list_jobs(...):
    ...

@router.post("/jobs/{job_id}/poll", response_model=ExternalResearchJobDetailResponse)
def poll_job(job_id: uuid.UUID, db: Session = Depends(get_db)):
    ...
```

`grep -R -n "task_post\|task_get\|DATAFORSEO\|ACTIVE_LISTING\|SOLD_LISTING\|budget\|cache" ...`
```text
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/connectors/dataforseo/merchant.py:35:        return self.client.post_json("/merchant/google/products/task_post", payload)
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/connectors/dataforseo/merchant.py:38:        return self.client.get_json(f"/merchant/google/products/task_get/advanced/{task_id}")
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/connectors/dataforseo/mappers.py:81:        "source": "DATAFORSEO",
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/connectors/dataforseo/mappers.py:84:        "evidence_type": "ACTIVE_LISTING",
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/services/external_research_service.py:50:                login=settings.DATAFORSEO_LOGIN,
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/services/external_research_service.py:51:                password=settings.DATAFORSEO_PASSWORD,
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/services/external_research_service.py:57:        if not settings.DATAFORSEO_ENABLED:
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/services/external_research_service.py:82:    def _cache_cutoff(self) -> datetime:
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/services/external_research_service.py:83:        return datetime.utcnow() - timedelta(days=settings.DATAFORSEO_CACHE_DAYS)
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/services/external_research_service.py:85:    def _find_cached_job(
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/services/external_research_service.py:94:            ExternalResearchJob.provider == "DATAFORSEO",
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/services/external_research_service.py:162:        budget_override: bool = False,
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/services/external_research_service.py:167:        cached = self._find_cached_job(idea_id=idea_id, product_id=product_id, query=query)
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/services/external_research_service.py:169:            return cached
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/services/external_research_service.py:171:        if not budget_override and self._recent_spend() + self._estimate_cost(1, max_results) > settings.DATAFORSEO_MONTHLY_BUDGET_USD:
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/services/external_research_service.py:177:            provider="DATAFORSEO",
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/services/external_research_service.py:190:            location_code=settings.DATAFORSEO_LOCATION_CODE,
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/services/external_research_service.py:191:            language_code=settings.DATAFORSEO_LANGUAGE_CODE,
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/services/external_research_service.py:233:        if request.queries and len(queries) > settings.DATAFORSEO_MAX_QUERIES_PER_IDEA:
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/services/external_research_service.py:237:        max_results = min(max(1, request.max_results), settings.DATAFORSEO_MAX_RESULTS_PER_QUERY)
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/services/external_research_service.py:243:        if not request.budget_override and spend_after > settings.DATAFORSEO_MONTHLY_BUDGET_USD:
```

## 10. EvidenceCandidate Approval Proof

Current excerpt from [resellos/backend/app/services/evidence_candidate_service.py](/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/services/evidence_candidate_service.py):

```python
        if not candidate:
            raise HTTPException(status_code=404, detail="Evidence candidate not found")
        candidate.review_status = "REJECTED"
        ...

        if data.approve_as == "MARKETPLACE_EVIDENCE":
            created = MarketplaceEvidence(
                ...
                source_method=candidate.source,
                verification_status=initial_verification,
                ...
            )
        elif data.approve_as == "COMPETITOR_LISTING":
            created = CompetitorListing(
                ...
                verification_status=initial_verification,
                notes=data.notes or candidate.source,
            )
        elif data.approve_as == "SUPPLIER_SOURCE":
            ...
            created = ProductSource(
                ...
                verification_status=initial_verification,
                notes=data.notes or raw.get("shipping_notes"),
                is_primary=False,
            )
        ...
        candidate.review_status = "APPROVED"
        ...
        if data.task_id:
            task = self.db.query(DiscoveryTask).filter(DiscoveryTask.id == data.task_id).first()
            if task:
                task.linked_evidence_id = created_object_id if data.approve_as == "MARKETPLACE_EVIDENCE" else None
                task.linked_source_id = created_object_id if data.approve_as == "SUPPLIER_SOURCE" else None
                task.linked_competitor_id = created_object_id if data.approve_as == "COMPETITOR_LISTING" else None
                task.linked_product_id = product_id
```

`resellos/backend/app/routes/evidence_candidates.py`

```python
@router.post("/{candidate_id}/approve", response_model=EvidenceCandidateReviewResponse)
def approve_candidate(candidate_id: uuid.UUID, request: EvidenceCandidateReviewRequest, db: Session = Depends(get_db)):
    service = EvidenceCandidateService(db)
    if not request.approve_as:
        raise HTTPException(status_code=400, detail="approve_as is required")
    return service.approve_candidate(candidate_id, request)

@router.post("/{candidate_id}/reject", response_model=EvidenceCandidateResponse)
def reject_candidate(candidate_id: uuid.UUID, request: EvidenceCandidateRejectRequest, db: Session = Depends(get_db)):
    service = EvidenceCandidateService(db)
    candidate = service.reject_candidate(candidate_id, request)
    return EvidenceCandidateResponse.model_validate(service.serialize_candidate(candidate))
```

`grep -R -n "approve_as\|MARKETPLACE_EVIDENCE\|COMPETITOR_LISTING\|SUPPLIER_SOURCE\|verification_status\|API_IMPORTED\|APPROVED\|REJECTED" ...`
```text
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/services/evidence_candidate_service.py:97:        candidate.review_status = "REJECTED"
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/services/evidence_candidate_service.py:127:        initial_verification = "API_IMPORTED"
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/services/evidence_candidate_service.py:133:        if data.approve_as == "MARKETPLACE_EVIDENCE":
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/services/evidence_candidate_service.py:145:                verification_status=initial_verification,
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/services/evidence_candidate_service.py:155:        elif data.approve_as == "COMPETITOR_LISTING":
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/services/evidence_candidate_service.py:166:                verification_status=initial_verification,
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/services/evidence_candidate_service.py:173:        elif data.approve_as == "SUPPLIER_SOURCE":
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/services/evidence_candidate_service.py:183:                verification_status=initial_verification,
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/services/evidence_candidate_service.py:194:        candidate.review_status = "APPROVED"
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/services/evidence_candidate_service.py:198:            "approve_as": data.approve_as,
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/services/evidence_candidate_service.py:208:                task.linked_evidence_id = created_object_id if data.approve_as == "MARKETPLACE_EVIDENCE" else None
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/services/evidence_candidate_service.py:209:                task.linked_source_id = created_object_id if data.approve_as == "SUPPLIER_SOURCE" else None
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/services/evidence_candidate_service.py:210:                task.linked_competitor_id = created_object_id if data.approve_as == "COMPETITOR_LISTING" else None
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/routes/evidence_candidates.py:35:    if not request.approve_as:
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/routes/evidence_candidates.py:36:        raise HTTPException(status_code=400, detail="approve_as is required")
```

## 11. Verification Metadata Model Proof

Current excerpt from [resellos/backend/app/models/supplier.py](/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/models/supplier.py):

```python
class ProductSource(Base):
    __tablename__ = "product_sources"
    ...
    supplier_url = Column(Text)
    unit_cost = Column(Numeric(10, 2))
    domestic_shipping = Column(Numeric(10, 2))
    international_shipping_estimate = Column(Numeric(10, 2))
    estimated_landed_cost = Column(Numeric(10, 2))
    moq = Column(Integer)
    supplier_rating = Column(String(50))
    notes = Column(Text)
    is_primary = Column(Boolean, default=False)
    verification_status = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
```

```python
class CompetitorListing(Base):
    __tablename__ = "competitor_listings"
    ...
    url = Column(Text)
    price = Column(Numeric(10, 2))
    shipping_price = Column(Numeric(10, 2))
    condition = Column(String(50))
    seller_name = Column(String(200))
    sold = Column(Boolean, default=False)
    verification_status = Column(String(50))
    photo_score = Column(Numeric(5, 2))
    title_score = Column(Numeric(5, 2))
    description_score = Column(Numeric(5, 2))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
```

```python
class MarketplaceEvidence(Base):
    __tablename__ = "marketplace_evidence"
    ...
    url = Column(Text)
    price = Column(Numeric(10, 2))
    shipping_price = Column(Numeric(10, 2))
    sold_date = Column(DateTime)
    condition = Column(String(100))
    seller_name = Column(String(200))
    source_method = Column(String(50))
    verification_status = Column(String(50))
    raw_text = Column(Text)
    screenshot_url = Column(Text)
    confidence = Column(String(50))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
```

```python
class DiscoveryTask(Base):
    __tablename__ = "discovery_tasks"
    ...
    linked_evidence_id = Column(UUID(as_uuid=True), ForeignKey("marketplace_evidence.id"))
    linked_source_id = Column(UUID(as_uuid=True), ForeignKey("product_sources.id"))
    linked_competitor_id = Column(UUID(as_uuid=True), ForeignKey("competitor_listings.id"))
    linked_product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
```

`grep -n "verification_status\|source_method\|screenshot_url\|candidate_id\|capture_id\|verified_at\|verification_notes\|linked_evidence_id\|linked_source_id\|linked_competitor_id" resellos/backend/app/models/supplier.py`
```text
25:    verification_status = Column(String(50))
72:    verification_status = Column(String(50))
137:    source_method = Column(String(50))
138:    verification_status = Column(String(50))
140:    screenshot_url = Column(Text)
241:    linked_evidence_id = Column(UUID(as_uuid=True), ForeignKey("marketplace_evidence.id"))
242:    linked_source_id = Column(UUID(as_uuid=True), ForeignKey("product_sources.id"))
243:    linked_competitor_id = Column(UUID(as_uuid=True), ForeignKey("competitor_listings.id"))
```

`MISSING` note:
- The current model file does not contain `candidate_id`, `capture_id`, `verified_at`, `verification_notes`, `is_synthetic`, or `is_verified_real`.

## 12. Frontend Verified Evidence UI Proof

### Product cockpit

Current excerpt from [resellos/frontend/app/products/[id]/page.tsx](/Users/admin/CascadeProjects/is44ks-shop/resellos/frontend/app/products/[id]/page.tsx):

```tsx
  const VERIFIED_STATUSES = ['USER_VERIFIED', 'API_IMPORTED'];
  const verifiedSoldCount = evidenceRows.filter((row) => row.evidence_type === 'SOLD_LISTING' && row.verification_status && VERIFIED_STATUSES.includes(row.verification_status)).length;
  const verifiedActiveCount = evidenceRows.filter((row) => row.evidence_type === 'ACTIVE_LISTING' && row.verification_status && VERIFIED_STATUSES.includes(row.verification_status)).length;
  const testDataCount = evidenceRows.filter((row) => row.verification_status === 'TEST_DATA').length;
  const totalTestDataCount = [...evidenceRows, ...competitorRows, ...supplierSources].filter((row) => 'verification_status' in row && (row as { verification_status?: string }).verification_status === 'TEST_DATA').length;
```

```tsx
  const readinessChecks = [
    { label: 'Sold evidence (verified)', ok: verifiedSoldCount >= 5, detail: `${verifiedSoldCount}/5+ verified sold listings (${soldEvidenceCount} total)` },
    { label: 'Active evidence (verified)', ok: verifiedActiveCount >= 5, detail: `${verifiedActiveCount}/5+ verified active listings (${activeEvidenceCount} total)` },
    { label: 'No test data', ok: testDataCount === 0, detail: testDataCount > 0 ? `${testDataCount} test data items present` : 'All evidence is real' },
    { label: 'Supplier cost', ok: supplierCostPresent, detail: supplierCostPresent ? 'Entered' : 'Missing' },
    { label: 'International shipping', ok: internationalShippingPresent, detail: internationalShippingPresent ? 'Entered' : 'Missing' },
    { label: 'Profit scenarios', ok: profitScenariosPresent, detail: profitScenariosPresent ? `${profitRows.length} generated` : 'Missing' },
    { label: 'Risk review', ok: riskPassed, detail: riskPassed ? 'Passed' : 'Blocked' },
    { label: 'Target price', ok: targetPricePresent, detail: targetPricePresent ? money(targetSalePrice) : 'Missing' },
  ];
```

```tsx
              <StatRow label="Sold listings" value={`${verifiedSoldCount} verified / ${soldEvidenceCount} total`} />
              <StatRow label="Active listings" value={`${verifiedActiveCount} verified / ${activeEvidenceCount} total`} />
              <StatRow label="Test data items" value={String(testDataCount)} />
```

```tsx
                          {row.verification_status && row.verification_status !== 'USER_VERIFIED' && row.verification_status !== 'API_IMPORTED' ? (
                            <button
                              type="button"
                              onClick={async () => { await verifyEvidenceItem(row.id, 'USER_VERIFIED'); await loadCockpit(); }}
                              className="rounded-lg border border-green-500/30 bg-green-500/10 px-2 py-1 text-xs text-green-400 hover:bg-green-500/20"
                            >
                              Verify
                            </button>
                          ) : null}
```

### Discovery page

Current excerpt from [resellos/frontend/app/discovery/page.tsx](/Users/admin/CascadeProjects/is44ks-shop/resellos/frontend/app/discovery/page.tsx):

```tsx
      <div className="mt-3 grid gap-2 text-sm text-zinc-300 md:grid-cols-2">
        <StatRow label="Verdict" value={idea.quick_scan_verdict || 'IDEA'} />
        <StatRow label="Priority" value={idea.research_priority || '—'} />
        <StatRow label="Readiness" value={idea.buy_readiness_status || 'NOT_READY'} />
        <StatRow label="Discovery completeness" value={`${idea.discovery_completeness_score ?? idea.research_completeness_score ?? 0}%`} />
        <StatRow label="Supplier cost" value={money(idea.rough_supplier_cost)} />
        <StatRow label="Landed cost" value={money(idea.estimated_landed_cost)} />
      </div>
```

```tsx
                <div className="mt-2 text-xs text-zinc-400">
                  {renderTaskLinkStatus(task) === 'No evidence linked' ? (
                    <span>{renderTaskLinkStatus(task)}</span>
                  ) : (
                    <Link href={taskLinkHref(task, idea.promoted_product_id)} className="text-indigo-300 hover:text-indigo-200">
                      {renderTaskLinkStatus(task)}
                    </Link>
                  )}
                </div>
                {task.status === 'DONE' && !hasTaskLink(task) ? (
                  <div className="mt-1 text-xs text-amber-300">Done by note only — no evidence linked.</div>
                ) : null}
```

```tsx
                <div className="mt-3 rounded-xl border border-zinc-800 bg-zinc-950/80 p-3">
                  <div className="text-[11px] uppercase tracking-[0.14em] text-zinc-500">Proof</div>
                  <div className="mt-2 text-sm text-zinc-300">{renderTaskLinkStatus(task)}</div>
                  <div className="mt-1 text-[11px] text-zinc-500">
                    {hasTaskLink(task) ? 'Strong proof attached.' : 'Proof is optional, but linking real evidence makes the task auditable.'}
                  </div>
                </div>
```

```tsx
function EvidenceCandidateCard({
  candidate,
  idea,
  taskLink,
  onTaskLinkChange,
  onApprove,
  onReject,
}: {
  candidate: EvidenceCandidate;
  idea: DiscoveryIdea | null;
  taskLink: string;
  onTaskLinkChange: (value: string) => void;
  onApprove: (candidateId: string, approveAs: 'MARKETPLACE_EVIDENCE' | 'COMPETITOR_LISTING' | 'SUPPLIER_SOURCE') => void;
  onReject: (candidateId: string) => void;
}) {
  const canApprove = Boolean(idea?.promoted_product_id || candidate.product_id);
  const canReview = candidate.review_status === 'PENDING';
  ...
  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-950/80 p-3">
      ...
      <div className="mt-3 rounded-xl border border-zinc-800 bg-zinc-950/80 p-3 text-xs text-zinc-300">
        <div className="text-[11px] uppercase tracking-[0.14em] text-zinc-500">Proof state</div>
        <div className="mt-1 text-sm text-white">
          {candidate.review_status === 'APPROVED' ? 'Approved candidate' : 'Pending review'}
        </div>
        <div className="mt-1 text-zinc-500">
          {canApprove ? 'Linked to a promoted product' : 'Promote the idea first before approving proof into product records.'}
        </div>
      </div>
      ...
      <div className="mt-3 flex flex-wrap gap-2">
        {candidate.candidate_type === 'RISK_FLAG' ? (
          <div className="text-xs text-zinc-500">Risk candidates stay review-only for now.</div>
        ) : candidate.candidate_type === 'SUPPLIER_SOURCE' ? (
          <button
            type="button"
            onClick={() => onApprove(candidate.id, 'SUPPLIER_SOURCE')}
            disabled={!canApprove || !canReview}
            className="rounded-lg border border-cyan-500/20 bg-cyan-500/10 px-3 py-1.5 text-xs text-cyan-300 hover:bg-cyan-500/20 disabled:opacity-60"
          >
            Approve as supplier
          </button>
        ) : (
          <>
            <button
              type="button"
              onClick={() => onApprove(candidate.id, 'MARKETPLACE_EVIDENCE')}
              disabled={!canApprove || !canReview}
              className="rounded-lg border border-emerald-500/20 bg-emerald-500/10 px-3 py-1.5 text-xs text-emerald-300 hover:bg-emerald-500/20 disabled:opacity-60"
            >
              Approve as evidence
            </button>
            <button
              type="button"
              onClick={() => onApprove(candidate.id, 'COMPETITOR_LISTING')}
              disabled={!canApprove || !canReview}
              className="rounded-lg border border-violet-500/20 bg-violet-500/10 px-3 py-1.5 text-xs text-violet-300 hover:bg-violet-500/20 disabled:opacity-60"
            >
              Approve as competitor
            </button>
          </>
        )}
```

```tsx
function taskLinkHref(
  task: {
    linked_evidence_id?: string | null;
    linked_source_id?: string | null;
    linked_competitor_id?: string | null;
    linked_product_id?: string | null;
  },
  promotedProductId?: string | null,
) {
  const productId = task.linked_product_id || promotedProductId;
  if (!productId) return '#';
  if (task.linked_evidence_id) return `/products/${productId}#evidence-${task.linked_evidence_id}`;
  if (task.linked_source_id) return `/products/${productId}#source-${task.linked_source_id}`;
  if (task.linked_competitor_id) return `/products/${productId}#competitor-${task.linked_competitor_id}`;
  return `/products/${productId}`;
}
```

`grep -R -n "verifiedSold\|verifiedActive\|testData\|TEST DATA\|UNVERIFIED\|VERIFIED\|Done by note only\|linked_evidence_id\|EvidenceCandidate" ...`
```text
/Users/admin/CascadeProjects/is44ks-shop/resellos/frontend/app/products/[id]/page.tsx:115:  const VERIFIED_STATUSES = ['USER_VERIFIED', 'API_IMPORTED'];
/Users/admin/CascadeProjects/is44ks-shop/resellos/frontend/app/products/[id]/page.tsx:116:  const verifiedSoldCount = evidenceRows.filter((row) => row.evidence_type === 'SOLD_LISTING' && row.verification_status && VERIFIED_STATUSES.includes(row.verification_status)).length;
/Users/admin/CascadeProjects/is44ks-shop/resellos/frontend/app/products/[id]/page.tsx:117:  const verifiedActiveCount = evidenceRows.filter((row) => row.evidence_type === 'ACTIVE_LISTING' && row.verification_status && VERIFIED_STATUSES.includes(row.verification_status)).length;
/Users/admin/CascadeProjects/is44ks-shop/resellos/frontend/app/products/[id]/page.tsx:118:  const testDataCount = evidenceRows.filter((row) => row.verification_status === 'TEST_DATA').length;
/Users/admin/CascadeProjects/is44ks-shop/resellos/frontend/app/products/[id]/page.tsx:132:    { label: 'Sold evidence (verified)', ok: verifiedSoldCount >= 5, detail: `${verifiedSoldCount}/5+ verified sold listings (${soldEvidenceCount} total)` },
/Users/admin/CascadeProjects/is44ks-shop/resellos/frontend/app/products/[id]/page.tsx:133:    { label: 'Active evidence (verified)', ok: verifiedActiveCount >= 5, detail: `${verifiedActiveCount}/5+ verified active listings (${activeEvidenceCount} total)` },
/Users/admin/CascadeProjects/is44ks-shop/resellos/frontend/app/products/[id]/page.tsx:134:    { label: 'No test data', ok: testDataCount === 0, detail: testDataCount > 0 ? `${testDataCount} test data items present` : 'All evidence is real' },
/Users/admin/CascadeProjects/is44ks-shop/resellos/frontend/app/products/[id]/page.tsx:382:              <StatRow label="Sold listings" value={`${verifiedSoldCount} verified / ${soldEvidenceCount} total`} />
/Users/admin/CascadeProjects/is44ks-shop/resellos/frontend/app/products/[id]/page.tsx:383:              <StatRow label="Active listings" value={`${verifiedActiveCount} verified / ${activeEvidenceCount} total`} />
/Users/admin/CascadeProjects/is44ks-shop/resellos/frontend/app/products/[id]/page.tsx:384:              <StatRow label="Test data items" value={String(testDataCount)} />
/Users/admin/CascadeProjects/is44ks-shop/resellos/frontend/app/products/[id]/page.tsx:504:                          {row.verification_status && row.verification_status !== 'USER_VERIFIED' && row.verification_status !== 'API_IMPORTED' ? (
/Users/admin/CascadeProjects/is44ks-shop/resellos/frontend/app/products/[id]/page.tsx:507:                              onClick={async () => { await verifyEvidenceItem(row.id, 'USER_VERIFIED'); await loadCockpit(); }}
/Users/admin/CascadeProjects/is44ks-shop/resellos/frontend/app/discovery/page.tsx:18:  approveEvidenceCandidate,
/Users/admin/CascadeProjects/is44ks-shop/resellos/frontend/app/discovery/page.tsx:27:  listEvidenceCandidates,
/Users/admin/CascadeProjects/is44ks-shop/resellos/frontend/app/discovery/page.tsx:32:  rejectEvidenceCandidate,
/Users/admin/CascadeProjects/is44ks-shop/resellos/frontend/app/discovery/page.tsx:40:  EvidenceCandidate,
/Users/admin/CascadeProjects/is44ks-shop/resellos/frontend/app/discovery/page.tsx:68:  const [evidenceCandidates, setEvidenceCandidates] = useState<EvidenceCandidate[]>([]);
/Users/admin/CascadeProjects/is44ks-shop/resellos/frontend/app/discovery/page.tsx:94:        listEvidenceCandidates(),
/Users/admin/CascadeProjects/is44ks-shop/resellos/frontend/app/discovery/page.tsx:99:      setEvidenceCandidates(candidates);
/Users/admin/CascadeProjects/is44ks-shop/resellos/frontend/app/discovery/page.tsx:218:      await approveEvidenceCandidate(candidateId, {
/Users/admin/CascadeProjects/is44ks-shop/resellos/frontend/app/discovery/page.tsx:231:      await rejectEvidenceCandidate(candidateId, {});
/Users/admin/CascadeProjects/is44ks-shop/resellos/frontend/app/discovery/page.tsx:487:                    <EvidenceCandidateCard
/Users/admin/CascadeProjects/is44ks-shop/resellos/frontend/app/discovery/page.tsx:704:      linked_evidence_id?: string | null;
/Users/admin/CascadeProjects/is44ks-shop/resellos/frontend/app/discovery/page.tsx:853:                  <div className="mt-1 text-xs text-amber-300">Done by note only — no evidence linked.</div>
/Users/admin/CascadeProjects/is44ks-shop/resellos/frontend/app/discovery/page.tsx:1057:function EvidenceCandidateCard({
/Users/admin/CascadeProjects/is44ks-shop/resellos/frontend/app/discovery/page.tsx:1065:  candidate: EvidenceCandidate;
/Users/admin/CascadeProjects/is44ks-shop/resellos/frontend/app/discovery/page.tsx:1237:    linked_evidence_id?: string | null;
/Users/admin/CascadeProjects/is44ks-shop/resellos/frontend/app/discovery/page.tsx:1246:  if (task.linked_evidence_id) return `/products/${productId}#evidence-${task.linked_evidence_id}`;
/Users/admin/CascadeProjects/is44ks-shop/resellos/frontend/app/discovery/page.tsx:1253:    linked_evidence_id?: string | null;
/Users/admin/CascadeProjects/is44ks-shop/resellos/frontend/app/discovery/page.tsx:1258:  if (task.linked_evidence_id) return `evidence:${task.linked_evidence_id}`;
/Users/admin/CascadeProjects/is44ks-shop/resellos/frontend/app/discovery/page.tsx:1268:      linked_evidence_id: null,
/Users/admin/CascadeProjects/is44ks-shop/resellos/frontend/app/discovery/page.tsx:1276:    linked_evidence_id: kind === 'evidence' ? id : null,
/Users/admin/CascadeProjects/is44ks-shop/resellos/frontend/app/discovery/page.tsx:1284:  linked_evidence_id?: string | null;
/Users/admin/CascadeProjects/is44ks-shop/resellos/frontend/app/discovery/page.tsx:1289:  return Boolean(task.linked_evidence_id || task.linked_source_id || task.linked_competitor_id || task.linked_product_id);
/Users/admin/CascadeProjects/is44ks-shop/resellos/frontend/app/discovery/page.tsx:1293:  linked_evidence_id?: string | null;
/Users/admin/CascadeProjects/is44ks-shop/resellos/frontend/app/discovery/page.tsx:1298:  if (task.linked_evidence_id) return 'Linked to sold evidence';
```

## 13. Current Live Pet Product Data

Command used:
```bash
docker compose exec -T db psql -U postgres -d resellos -c "WITH target AS (SELECT id, name, category, status FROM products WHERE lower(name) IN ('reusable pet hair remover roller','pet grooming glove','collapsible dog travel bowl')), evidence AS (SELECT product_id, evidence_type, verification_status, source_method, count(*) AS cnt FROM marketplace_evidence GROUP BY product_id, evidence_type, verification_status, source_method), sources AS (SELECT product_id, verification_status, count(*) AS cnt FROM product_sources GROUP BY product_id, verification_status), competitors AS (SELECT product_id, verification_status, count(*) AS cnt FROM competitor_listings GROUP BY product_id, verification_status), latest AS (SELECT DISTINCT ON (product_id, agent_name) product_id, agent_name, output_json, summary FROM agent_reports WHERE product_id IN (SELECT id FROM target) ORDER BY product_id, agent_name, created_at DESC) SELECT ...;"
```

Current product rows:
```text
                  id                  |               name               |    category     |     status     | final_decision 
--------------------------------------+----------------------------------+-----------------+----------------+----------------
 6bfdb8f1-48ad-44f3-85f0-ee82bc24b7ef | Collapsible dog travel bowl      | Pet accessories | NEEDS_RESEARCH | SKIP
 04416fb1-e016-4f3e-8945-8d760b11059f | Pet grooming glove               | Pet accessories | WATCHLIST      | WATCHLIST
 946184b3-d776-49a9-afc5-9b3ee554c4cf | Reusable pet hair remover roller | Pet accessories | NEEDS_RESEARCH | SKIP
(3 rows)
```

Evidence breakdown:
```text
              product_id              | evidence_type  |   verification_status    | source_method  | count 
--------------------------------------+----------------+--------------------------+----------------+-------
 04416fb1-e016-4f3e-8945-8d760b11059f | ACTIVE_LISTING | API_IMPORTED             | DATAFORSEO     |     1
 04416fb1-e016-4f3e-8945-8d760b11059f | ACTIVE_LISTING | TEST_DATA                | manual_entry   |     5
 04416fb1-e016-4f3e-8945-8d760b11059f | SOLD_LISTING   | TEST_DATA                | manual_entry   |     4
 04416fb1-e016-4f3e-8945-8d760b11059f | SOLD_LISTING   | USER_CAPTURED_UNVERIFIED | MANUAL_CAPTURE |     2
 6bfdb8f1-48ad-44f3-85f0-ee82bc24b7ef | ACTIVE_LISTING | TEST_DATA                | manual_entry   |     5
 6bfdb8f1-48ad-44f3-85f0-ee82bc24b7ef | ACTIVE_LISTING | USER_CAPTURED_UNVERIFIED | MANUAL_CAPTURE |     1
 6bfdb8f1-48ad-44f3-85f0-ee82bc24b7ef | SOLD_LISTING   | TEST_DATA                | manual_entry   |     5
 6bfdb8f1-48ad-44f3-85f0-ee82bc24b7ef | SOLD_LISTING   | USER_CAPTURED_UNVERIFIED | MANUAL_CAPTURE |     1
 946184b3-d776-49a9-afc5-9b3ee554c4cf | ACTIVE_LISTING | TEST_DATA                | manual_entry   |     5
 946184b3-d776-49a9-afc5-9b3ee554c4cf | ACTIVE_LISTING | USER_CAPTURED_UNVERIFIED | MANUAL_CAPTURE |     1
 946184b3-d776-49a9-afc5-9b3ee554c4cf | SOLD_LISTING   | TEST_DATA                | manual_entry   |     5
 946184b3-d776-49a9-afc5-9b3ee554c4cf | SOLD_LISTING   | USER_CAPTURED_UNVERIFIED | MANUAL_CAPTURE |     1
(12 rows)
```

Supplier and competitor counts:
```text
              product_id              | verification_status | count 
--------------------------------------+---------------------+-------
 04416fb1-e016-4f3e-8945-8d760b11059f | TEST_DATA           |     3
 6bfdb8f1-48ad-44f3-85f0-ee82bc24b7ef | TEST_DATA           |     3
 946184b3-d776-49a9-afc5-9b3ee554c4cf | TEST_DATA           |     3
(3 rows)
```

Latest agent outputs, compacted by product and agent, are in Section 14 below.

## 14. Latest Agent Report Outputs

### Reusable pet hair remover roller

```text
agent_name	risk_level	blocked	red_flags	evidence_quality	insufficient_data	market_price_missing	sold_listing_count	verified_sold_listing_count	active_listing_count	verified_active_listing_count	median_sold_price	median_sold_price_total	median_active_price	median_active_price_total	active_price_range	active_price_range_total	sold_price_range	sold_price_range_total	test_data_evidence_count	verification_coverage	competition_level	listing_gap_score	can_compete	competitor_count	verified_competitor_count	estimated_net_profit	target_sale_price	best_scenario	minimum_recommended_price	recommendation	research_verdict	buy_readiness_status	main_blocker	total_score	opportunity_score	research_completeness_score	required_before_buying	hard_blockers	summary
competition_agent																				0.0	LOW	25	false	3	0														Competition analysis completed from captured competitor listings.
decision_agent		false																									0.0			SKIP	WEAK_IDEA	NOT_READY	Evidence is not verified.	35	35	35	["Add at least 5 verified sold listings with prices.", "Add verified active listing evidence for competition checks.", "Reach at least medium marketplace evidence quality.", "Record a real sold or active market price.", "Add at least 3 verified competitor listings before buying.", "Verify supplier source before buying.", "Add at least 5 verified sold listings (currently 0 verified of 6 total).", "Add at least 5 verified active listings (currently 0 verified of 6 total).", "Capture shipping examples.", "Add screenshots or manual notes for support.", "Replace 10 test/synthetic evidence items with real verified data.", "Verify 2 unverified evidence items.", "Add real sold listings and a market price.", "Replace test/synthetic evidence with real verified data.", "Capture competitor weaknesses and find a clearer angle.", "Verify supplier URL, screenshot, unit cost, shipping, and landed cost.", "Verify evidence before sample buying.", "Record a real target sale price from market evidence."]	["Market evidence is insufficient for a buy decision.", "10 evidence items are test data — not real market evidence.", "Competition gap is too small to compete reliably.", "Supplier cost is not verified.", "Evidence is not verified."]	Weak economics or too much uncertainty.
discovery_context																																			30	30			The idea looks worth checking, but supplier clarity is still missing.
listing_agent																																							
market_agent				LOW	true	true	6	0	6	0		14.24		14.24	[]	[11.99, 18.99]	[]	[11.49, 15.99]	10	0.0	UNKNOWN															10			Marketplace evidence analyzed from 2 marketplaces.
profit_agent																										-6.18	0.0	eBay buyer-paid shipping	11.75										Best scenario: eBay buyer-paid shipping with net profit $-6.18.
reorder_agent																																							Reorder recommendation: DO_NOT_REORDER based on 0 sold and 0 on hand.
risk_agent	LOW	false	[]																																				Risk evaluation completed.
```

### Pet grooming glove

```text
agent_name	risk_level	blocked	red_flags	evidence_quality	insufficient_data	market_price_missing	sold_listing_count	verified_sold_listing_count	active_listing_count	verified_active_listing_count	median_sold_price	median_sold_price_total	median_active_price	median_active_price_total	active_price_range	active_price_range_total	sold_price_range	sold_price_range_total	test_data_evidence_count	verification_coverage	competition_level	listing_gap_score	can_compete	competitor_count	verified_competitor_count	estimated_net_profit	target_sale_price	best_scenario	minimum_recommended_price	recommendation	research_verdict	buy_readiness_status	main_blocker	total_score	opportunity_score	research_completeness_score	required_before_buying	hard_blockers	summary
competition_agent																				0.0	LOW	25	false	3	0														Competition analysis completed from captured competitor listings.
decision_agent		false																									11.99			WATCHLIST	NEEDS_MORE_RESEARCH	NOT_READY	Evidence is not verified.	55	55	57	["Add at least 5 verified sold listings with prices.", "Reach at least medium marketplace evidence quality.", "Add at least 3 verified competitor listings before buying.", "Verify supplier source before buying.", "Add at least 5 verified sold listings (currently 0 verified of 6 total).", "Add at least 5 verified active listings (currently 1 verified of 6 total).", "Add screenshots or manual notes for support.", "Replace 9 test/synthetic evidence items with real verified data.", "Verify 2 unverified evidence items.", "Add real sold listings and a market price.", "Replace test/synthetic evidence with real verified data.", "Capture competitor weaknesses and find a clearer angle.", "Verify supplier URL, screenshot, unit cost, shipping, and landed cost.", "Verify evidence before sample buying."]	["Market evidence is insufficient for a buy decision.", "9 evidence items are test data — not real market evidence.", "Competition gap is too small to compete reliably.", "Supplier cost is not verified.", "Evidence is not verified."]	The idea is promising, but evidence is still thin.
discovery_context																																			30	30			The idea looks worth checking, but supplier clarity is still missing.
listing_agent																																							
market_agent				LOW	true	false	6	0	6	1		9.74	11.99	11.24	[11.99, 11.99]	[8.49, 13.99]	[]	[7.99, 11.99]	9	0.08	MEDIUM															32			Marketplace evidence analyzed from 3 marketplaces.
profit_agent																										5.1	11.99	eBay buyer-paid shipping	12.53										Best scenario: eBay buyer-paid shipping with net profit $5.10.
reorder_agent																																							Reorder recommendation: DO_NOT_REORDER based on 0 sold and 0 on hand.
risk_agent	LOW	false	[]																																				Risk evaluation completed.
```

### Collapsible dog travel bowl

```text
agent_name	risk_level	blocked	red_flags	evidence_quality	insufficient_data	market_price_missing	sold_listing_count	verified_sold_listing_count	active_listing_count	verified_active_listing_count	median_sold_price	median_sold_price_total	median_active_price	median_active_price_total	active_price_range	active_price_range_total	sold_price_range	sold_price_range_total	test_data_evidence_count	verification_coverage	competition_level	listing_gap_score	can_compete	competitor_count	verified_competitor_count	estimated_net_profit	target_sale_price	best_scenario	minimum_recommended_price	recommendation	research_verdict	buy_readiness_status	main_blocker	total_score	opportunity_score	research_completeness_score	required_before_buying	hard_blockers	summary
competition_agent																				0.0	LOW	25	false	3	0														Competition analysis completed from captured competitor listings.
decision_agent		false																									0.0			SKIP	WEAK_IDEA	NOT_READY	Evidence is not verified.	35	35	35	["Add at least 5 verified sold listings with prices.", "Add verified active listing evidence for competition checks.", "Reach at least medium marketplace evidence quality.", "Record a real sold or active market price.", "Add at least 3 verified competitor listings before buying.", "Verify supplier source before buying.", "Add at least 5 verified sold listings (currently 0 verified of 6 total).", "Add at least 5 verified active listings (currently 0 verified of 6 total).", "Capture shipping examples.", "Add screenshots or manual notes for support.", "Replace 10 test/synthetic evidence items with real verified data.", "Verify 2 unverified evidence items.", "Add real sold listings and a market price.", "Replace test/synthetic evidence with real verified data.", "Capture competitor weaknesses and find a clearer angle.", "Verify supplier URL, screenshot, unit cost, shipping, and landed cost.", "Verify evidence before sample buying.", "Record a real target sale price from market evidence."]	["Market evidence is insufficient for a buy decision.", "10 evidence items are test data — not real market evidence.", "Competition gap is too small to compete reliably.", "Supplier cost is not verified.", "Evidence is not verified."]	Weak economics or too much uncertainty.
discovery_context																																			30	30			The idea looks worth checking, but supplier clarity is still missing.
listing_agent																																							
market_agent				LOW	true	true	6	0	6	0		8.99		8.74	[]	[6.99, 11.49]	[]	[7.49, 10.99]	10	0.0	UNKNOWN															10			Marketplace evidence analyzed from 2 marketplaces.
profit_agent																										-4.88	0.0	eBay buyer-paid shipping	10.32										Best scenario: eBay buyer-paid shipping with net profit $-4.88.
reorder_agent																																							Reorder recommendation: DO_NOT_REORDER based on 0 sold and 0 on hand.
risk_agent	LOW	false	[]																																				Risk evaluation completed.
```

## 15. Regression Tests Proof

Current relevant test excerpts from [resellos/backend/tests/test_agents.py](/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/tests/test_agents.py):

```python
    def test_market_agent_uses_evidence_rows(self) -> None:
        agent = MarketAgent(self.llm)
        result = asyncio.run(
            agent.run(
                {
                    "product": {"name": "Test product"},
                    "marketplace_evidence": [
                        {"marketplace": "eBay", "evidence_type": "SOLD_LISTING", "price": 10.0, "shipping_price": 2.0, "verification_status": "USER_VERIFIED"},
                        {"marketplace": "eBay", "evidence_type": "SOLD_LISTING", "price": 12.0, "shipping_price": 2.5, "verification_status": "USER_VERIFIED"},
                        {"marketplace": "eBay", "evidence_type": "SOLD_LISTING", "price": 14.0, "shipping_price": 3.0, "verification_status": "USER_VERIFIED"},
                        {"marketplace": "eBay", "evidence_type": "SOLD_LISTING", "price": 16.0, "shipping_price": 3.0, "verification_status": "USER_VERIFIED"},
                        {"marketplace": "eBay", "evidence_type": "SOLD_LISTING", "price": 18.0, "shipping_price": 3.5, "verification_status": "USER_VERIFIED"},
                        {"marketplace": "eBay", "evidence_type": "ACTIVE_LISTING", "price": 19.0, "shipping_price": 4.0, "verification_status": "API_IMPORTED"},
                        {"marketplace": "eBay", "evidence_type": "ACTIVE_LISTING", "price": 20.0, "shipping_price": 4.0, "verification_status": "API_IMPORTED"},
                    ],
                }
            )
        )

        output = result["output_json"]
        self.assertEqual(output["sold_listing_count"], 5)
        self.assertEqual(output["verified_sold_listing_count"], 5)
        self.assertEqual(output["active_listing_count"], 2)
        self.assertEqual(output["verified_active_listing_count"], 2)
        self.assertEqual(output["median_sold_price"], 14.0)
        self.assertIn("research_completeness_score", output)
        self.assertIn("demand_evidence_quality", output)
        self.assertIn("market_presence_quality", output)
        self.assertFalse(output["insufficient_data"])
```

```python
    def test_market_agent_ignores_unverified_rows_for_price_signals(self) -> None:
        agent = MarketAgent(self.llm)
        result = asyncio.run(
            agent.run(
                {
                    "product": {"name": "Test product"},
                    "marketplace_evidence": [
                        {"marketplace": "eBay", "evidence_type": "SOLD_LISTING", "price": 100.0, "shipping_price": 10.0, "verification_status": "USER_CAPTURED_UNVERIFIED"},
                        {"marketplace": "eBay", "evidence_type": "SOLD_LISTING", "price": 110.0, "shipping_price": 11.0, "verification_status": "TEST_DATA"},
                        {"marketplace": "eBay", "evidence_type": "ACTIVE_LISTING", "price": 120.0, "shipping_price": 12.0, "verification_status": "USER_CAPTURED_UNVERIFIED"},
                    ],
                }
            )
        )

        output = result["output_json"]
        self.assertEqual(output["sold_listing_count"], 2)
        self.assertEqual(output["verified_sold_listing_count"], 0)
        self.assertEqual(output["verified_active_listing_count"], 0)
        self.assertIsNone(output["median_sold_price"])
        self.assertIsNone(output["median_active_price"])
        self.assertEqual(output["sold_price_range"], [])
        self.assertEqual(output["active_price_range"], [])
        self.assertEqual(output["sold_price_range_total"], [100.0, 110.0])
        self.assertEqual(output["active_price_range_total"], [120.0, 120.0])
        self.assertTrue(output["insufficient_data"])
```

```python
    def test_market_agent_does_not_treat_api_imported_sold_as_verified_demand(self) -> None:
        agent = MarketAgent(self.llm)
        result = asyncio.run(
            agent.run(
                {
                    "product": {"name": "Test product"},
                    "marketplace_evidence": [
                        {"marketplace": "Google Shopping", "evidence_type": "SOLD_LISTING", "price": 19.0, "shipping_price": 4.0, "verification_status": "API_IMPORTED"},
                        {"marketplace": "eBay", "evidence_type": "ACTIVE_LISTING", "price": 21.0, "shipping_price": 4.0, "verification_status": "API_IMPORTED"},
                    ],
                }
            )
        )

        output = result["output_json"]
        self.assertEqual(output["sold_listing_count"], 1)
        self.assertEqual(output["verified_sold_listing_count"], 0)
        self.assertEqual(output["verified_active_listing_count"], 1)
        self.assertIsNone(output["median_sold_price"])
        self.assertIsNotNone(output["median_active_price"])
```

```python
    def test_decision_agent_blocks_unverified_supplier_cost(self) -> None:
        ...
        self.assertEqual(output["buy_readiness_status"], "NOT_READY")
        self.assertIn("Supplier cost is not verified.", output["hard_blockers"])
        self.assertEqual(output["main_blocker"], "Supplier cost is not verified.")
```

```python
    def test_decision_agent_requires_verified_competitors(self) -> None:
        ...
        self.assertEqual(output["buy_readiness_status"], "NOT_READY")
        self.assertIn("Verified competitor evidence missing", output["missing_evidence"])
        self.assertIn("Add at least 3 verified competitor listings before buying.", output["required_before_buying"])
```

```python
    def test_profit_agent_outputs_three_scenarios(self) -> None:
        ...
        self.assertEqual(len(scenarios), 3)
        self.assertGreater(result["output_json"]["estimated_net_profit"], 0)
        self.assertFalse(result["output_json"]["best_scenario"].lower().endswith("bundle"))
```

Current relevant test excerpts from [resellos/backend/tests/test_external_research.py](/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/tests/test_external_research.py):

```python
    def test_google_shopping_mapper_defaults_to_active_listing(self) -> None:
        payload = map_google_shopping_item_to_candidate(
            {
                "type": "google_shopping_serp",
                "title": "Car seat gap organizer",
                "price": 18.99,
                "shopping_url": "https://example.com/item",
                "seller": "Example Seller",
                "reviews_count": 128,
                "product_images": ["https://example.com/image.jpg"],
            },
            source_job={"job_id": "job-1", "query": "car seat gap organizer"},
        )

        self.assertEqual(payload["candidate_type"], "MARKETPLACE_EVIDENCE")
        self.assertEqual(payload["evidence_type"], "ACTIVE_LISTING")
        self.assertEqual(payload["title"], "Car seat gap organizer")
        self.assertEqual(payload["seller"], "Example Seller")
```

```python
    def test_candidate_approval_creates_marketplace_evidence_and_links_task(self) -> None:
        ...
        self.assertEqual(result.candidate.review_status, "APPROVED")
        linked_task = self.session.query(DiscoveryTask).filter(DiscoveryTask.id == task.id).first()
        self.assertIsNotNone(linked_task.linked_evidence_id)
        evidence = self.session.query(MarketplaceEvidence).filter(MarketplaceEvidence.product_id == product.id).first()
        self.assertIsNotNone(evidence)
        self.assertEqual(evidence.evidence_type, "ACTIVE_LISTING")
```

```python
    def test_external_research_service_submits_and_polls_jobs(self) -> None:
        ...
        self.assertEqual(len(run_result.jobs), 1)
        job_id = run_result.jobs[0].id

        polled = service.poll_job(job_id)
        self.assertEqual(polled.status, "IMPORTED")
        candidates = service.list_candidates(job_id=job_id)
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].candidate_type, "MARKETPLACE_EVIDENCE")
```

`grep -n "unverified\|TEST_DATA\|API_IMPORTED\|verified supplier\|verified_competitor\|single_unit\|bundle\|ACTIVE_LISTING" resellos/backend/tests/test_agents.py resellos/backend/tests/test_external_research.py`
```text
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/tests/test_agents.py:88:                    "supplier_summary": {"unit_cost": 4.15, "international_shipping_estimate": 1.2, "verification_status": "API_IMPORTED"},
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/tests/test_agents.py:117:    def test_decision_agent_blocks_unverified_evidence(self) -> None:
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/tests/test_agents.py:133:                                "unverified_evidence_count": 12,
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/tests/test_agents.py:142:                        "competition_agent": {"output_json": {"competition_level": "LOW", "listing_gap_score": 72, "can_compete": True, "competitor_count": 3, "verified_competitor_count": 3}},
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/tests/test_agents.py:154:    def test_decision_agent_blocks_unverified_supplier_cost(self) -> None:
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/tests/test_agents.py:159:                    "supplier_summary": {"unit_cost": 4.15, "estimated_landed_cost": 5.70, "international_shipping_estimate": 1.2, "verification_status": "API_IMPORTED"},
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/tests/test_agents.py:170:                                "unverified_evidence_count": 0,
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/tests/test_agents.py:181:                        "competition_agent": {"output_json": {"competition_level": "LOW", "listing_gap_score": 72, "can_compete": True, "competitor_count": 3, "verified_competitor_count": 3}},
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/tests/test_agents.py:192:    def test_decision_agent_requires_verified_competitors(self) -> None:
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/tests/test_agents.py:208:                                "unverified_evidence_count": 0,
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/tests/test_agents.py:219:                        "competition_agent": {"output_json": {"competition_level": "LOW", "listing_gap_score": 72, "can_compete": True, "competitor_count": 2, "verified_competitor_count": 2}},
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/tests/test_agents.py:277:                        "bundle_quantity": 2,
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/tests/test_agents.py:286:        self.assertFalse(result["output_json"]["best_scenario"].lower().endswith("bundle"))
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/tests/test_agents.py:300:                        {"marketplace": "eBay", "evidence_type": "ACTIVE_LISTING", "price": 19.0, "shipping_price": 4.0, "verification_status": "API_IMPORTED"},
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/tests/test_agents.py:301:                        {"marketplace": "eBay", "evidence_type": "ACTIVE_LISTING", "price": 20.0, "shipping_price": 4.0, "verification_status": "API_IMPORTED"},
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/tests/test_agents.py:318:    def test_market_agent_ignores_unverified_rows_for_price_signals(self) -> None:
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/tests/test_agents.py:326:                        {"marketplace": "eBay", "evidence_type": "SOLD_LISTING", "price": 110.0, "shipping_price": 11.0, "verification_status": "TEST_DATA"},
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/tests/test_agents.py:327:                        {"marketplace": "eBay", "evidence_type": "ACTIVE_LISTING", "price": 120.0, "shipping_price": 12.0, "verification_status": "USER_CAPTURED_UNVERIFIED"},
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/tests/test_agents.py:352:                        {"marketplace": "Google Shopping", "evidence_type": "SOLD_LISTING", "price": 19.0, "shipping_price": 4.0, "verification_status": "API_IMPORTED"},
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/tests/test_agents.py:353:                        {"marketplace": "eBay", "evidence_type": "ACTIVE_LISTING", "price": 21.0, "shipping_price": 4.0, "verification_status": "API_IMPORTED"},
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/tests/test_agents.py:376:                        {"price": 17.99, "sold": False, "photo_score": 48, "title_score": 60, "description_score": 45, "verification_status": "API_IMPORTED"},
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/tests/test_agents.py:385:        self.assertEqual(output["verified_competitor_count"], 3)
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/tests/test_agents.py:454:                    MarketplaceEvidence(product_id=product.id, marketplace="eBay", evidence_type="ACTIVE_LISTING", price=19.0, shipping_price=4.0),
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/tests/test_agents.py:455:                    MarketplaceEvidence(product_id=product.id, marketplace="eBay", evidence_type="ACTIVE_LISTING", price=20.0, shipping_price=4.0),
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/tests/test_external_research.py:100:        self.assertEqual(payload["evidence_type"], "ACTIVE_LISTING")
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/tests/test_external_research.py:130:            evidence_type="ACTIVE_LISTING",
/Users/admin/CascadeProjects/is44ks-shop/resellos/backend/tests/test_external_research.py:157:        self.assertEqual(evidence.evidence_type, "ACTIVE_LISTING")
```

## 16. Final Self-Assessment

Based only on the evidence above:

1. Does the code guarantee synthetic/test evidence cannot make a product `READY_FOR_SAMPLE`? `Yes`.
2. Does `MarketAgent` use verified-only main sold medians? `Yes`.
3. Does `MarketAgent` keep total/debug medians separate? `Yes`.
4. Does `API_IMPORTED` never count as sold demand? `Yes` for sold demand; `API_IMPORTED` only counts as active market presence in the current code.
5. Does `DecisionAgent` require verified supplier? `Yes`.
6. Does `DecisionAgent` require at least 3 verified competitors? `Yes`.
7. Does `ProfitAgent` avoid bundle inflation? `Yes`.
8. Are current pet products `NOT_READY` because evidence is not verified? `Yes`.
9. Is the current pet data useful for testing? `Yes`.
10. Is the current pet data useful for real sample buying? `No`.

## 17. Command Transcript

Commands run for this packet:

```bash
git rev-parse HEAD
git branch --show-current
git status --short
git log --oneline -5
git remote -v
git diff --stat
PYTHONPATH=. python -m unittest discover -s tests
python -m compileall app
alembic current
alembic heads
docker compose exec -T backend alembic current
docker compose exec -T backend alembic heads
npm run build
grep -n "VERIFIED_SOLD\|VERIFIED_ACTIVE\|active_price_range_total\|sold_price_range_total\|median_sold_price_total\|median_active_price_total" /Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/agents/market_agent.py
grep -n "active_price_range_total\|sold_price_range_total\|median_sold_price_total\|verified_sold_listing_count" /Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/schemas/agent_schema.py
grep -n "has_verified_supplier\|verified_competitor_count\|Evidence is not verified\|Supplier cost is not verified\|verified_sold" /Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/agents/decision_agent.py
grep -n "verified_competitor_count\|verified_listings\|can_compete" /Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/agents/competition_agent.py
grep -n "verification_status\|USER_VERIFIED\|_serialize_evidence\|_serialize_source\|_serialize_competitor" /Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/services/research_pipeline_service.py
grep -n "single_unit_scenarios\|bundle\|estimated_net_profit\|best =" /Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/agents/profit_agent.py
grep -R -n "task_post\|task_get\|DATAFORSEO\|ACTIVE_LISTING\|SOLD_LISTING\|budget\|cache" /Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/connectors /Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/services/external_research_service.py /Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/routes/external_research.py
grep -R -n "approve_as\|MARKETPLACE_EVIDENCE\|COMPETITOR_LISTING\|SUPPLIER_SOURCE\|verification_status\|API_IMPORTED\|APPROVED\|REJECTED" /Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/services/evidence_candidate_service.py /Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/routes/evidence_candidates.py
grep -n "verification_status\|source_method\|screenshot_url\|candidate_id\|capture_id\|verified_at\|verification_notes\|linked_evidence_id\|linked_source_id\|linked_competitor_id" /Users/admin/CascadeProjects/is44ks-shop/resellos/backend/app/models/supplier.py
grep -n "verifiedSold\|verifiedActive\|testData\|TEST DATA\|UNVERIFIED\|VERIFIED\|Done by note only\|linked_evidence_id\|EvidenceCandidate" /Users/admin/CascadeProjects/is44ks-shop/resellos/frontend/app/products /Users/admin/CascadeProjects/is44ks-shop/resellos/frontend/app/discovery
grep -n "unverified\|TEST_DATA\|API_IMPORTED\|verified supplier\|verified_competitor\|single_unit\|bundle\|ACTIVE_LISTING" /Users/admin/CascadeProjects/is44ks-shop/resellos/backend/tests/test_agents.py /Users/admin/CascadeProjects/is44ks-shop/resellos/backend/tests/test_external_research.py
```
