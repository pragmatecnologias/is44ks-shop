# ResellOS User Manual

**Version:** Research MVP Manual  
**Audience:** Solo founder / daily product researcher  
**Primary goal:** Help you find, evaluate, and prepare to test low-risk products before spending money on samples.

---

## 1. What ResellOS Is For

ResellOS is a product discovery and research assistant. It is designed to help you answer one question:

> “Is this product idea worth researching further, rejecting, or buying samples for?”

It is not primarily a sales tracker yet. It is not a marketplace publishing system yet. It is not an automated scraping bot. The current research workflow is:

```text
Discovery Idea
→ Quick Scan
→ Category-Specific Research Tasks
→ Manual / AI-Assisted Evidence Capture
→ Opportunity Board
→ Promote to Product
→ Product Cockpit
→ Research Run
→ Ready / Not Ready for Samples
```

The system is built around disciplined evidence collection. The most important rule is:

> Do not buy samples until the product has real evidence, supplier cost clarity, realistic margin, and acceptable risk.

---

## 2. Main Screens

### 2.1 Discovery

Use `/discovery` as your daily home base.

This is where you:

- Add rough product ideas.
- Run Quick Scan.
- Generate category-specific research tasks.
- Mark research tasks as done, skipped, or blocked.
- Run external Google Shopping research through DataForSEO.
- Review evidence candidates.
- Approve candidates as evidence, competitors, or supplier-related data.
- Compare ideas and products on the Opportunity Board.
- Promote the best ideas into full product research cases.

Use this page when you do not know yet what you want to sell.

---

### 2.2 Product Cockpit

Use `/products/{id}` after an idea has been promoted into a full product.

This is where you:

- Add supplier sources.
- Add sold listings.
- Add active listings.
- Add competitor listings.
- Review discovery context from the original idea.
- Review market signal.
- Review supplier signal.
- Review competition gap.
- Review profit scenarios.
- Run the research pipeline.
- See whether the product is ready for samples.

Use this page when an idea deserves deeper research.

---

### 2.3 Capture

Use `/capture` or the capture modal in Discovery when you want to turn pasted text or screenshots into structured research candidates.

This is useful for:

- eBay listing screenshots.
- eBay sold listing text.
- Supplier screenshots from AliExpress, 1688, Kakobuy, etc.
- Competitor listing screenshots.
- Visual risk screenshots.

The capture system should create candidates, not final evidence. You still review and approve before saving.

---

### 2.4 Dashboard

Use the dashboard for a high-level overview. During the research phase, Discovery and Product Cockpit matter more than Dashboard.

---

## 3. External Services Needed

For local testing, keep it simple.

### Required

```text
PostgreSQL — local Docker container
MiniMax — cloud text LLM provider
LM Studio — local Qwen vision model server
```

### Optional

```text
DataForSEO — external Google Shopping product discovery
OpenAI — optional text/vision fallback
Ollama — optional local text model
```

### Not Required Yet

```text
eBay API
Amazon API
Shopify
TikTok Shop
Facebook Marketplace API
Stripe
SendGrid
Twilio
S3
Cloudinary
```

---

## 4. First-Time Local Setup

This setup assumes:

```text
PostgreSQL runs in Docker.
Backend runs locally with Python.
Frontend runs locally with Node.
LM Studio runs locally for Qwen Vision.
MiniMax is used for text agents.
DataForSEO is optional.
```

---

### 4.1 Start PostgreSQL Only

From the repository:

```bash
cd /Users/admin/CascadeProjects/is44ks-shop/resellos
docker compose up -d db
```

Check that Postgres is running:

```bash
docker compose ps
```

Expected:

```text
db service is running and healthy
localhost:5432 is available
```

---

### 4.2 Backend Environment

Create:

```bash
resellos/backend/.env
```

Use this minimal local configuration:

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/resellos

# Text LLM
LLM_PROVIDER=minimax
TEXT_LLM_PROVIDER=minimax
TEXT_LLM_MODEL=MiniMax-Text-01

MINIMAX_API_KEY=your_minimax_api_key_here
MINIMAX_MODEL=MiniMax-Text-01
MINIMAX_BASE_URL=https://api.minimax.chat/v1

# Optional OpenAI fallback
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o
OPENAI_BASE_URL=https://api.openai.com/v1

# Optional local text model
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3

# Vision LLM through LM Studio
VISION_LLM_PROVIDER=qwen_vl
VISION_LLM_BASE_URL=http://localhost:1234/v1
VISION_LLM_MODEL=put_exact_lm_studio_model_name_here
VISION_LLM_API_KEY=lm-studio
VISION_LLM_TIMEOUT_SECONDS=120
VISION_MAX_IMAGE_MB=8

# DataForSEO - disabled first
DATAFORSEO_ENABLED=false
DATAFORSEO_LOGIN=
DATAFORSEO_PASSWORD=
DATAFORSEO_QUEUE=standard
DATAFORSEO_LOCATION_CODE=2840
DATAFORSEO_LANGUAGE_CODE=en
DATAFORSEO_MAX_RESULTS_PER_QUERY=20
DATAFORSEO_MAX_QUERIES_PER_IDEA=3
DATAFORSEO_CACHE_DAYS=14
DATAFORSEO_MONTHLY_BUDGET_USD=25.0

# Business defaults
DEFAULT_MARKETPLACE_FEE_PERCENT=13.0
DEFAULT_PACKAGING_COST=0.50
DEFAULT_OUTBOUND_SHIPPING=4.50
DEFAULT_RETURN_ALLOWANCE=0.50
MIN_ACCEPTABLE_PROFIT=3.0
MIN_ACCEPTABLE_MARGIN=20.0

# CORS
ALLOWED_ORIGINS=http://localhost:3000
```

Important:

- Because the backend runs locally, use `http://localhost:1234/v1` for LM Studio.
- Use `host.docker.internal` only when the backend runs inside Docker.

---

### 4.3 Frontend Environment

Create:

```bash
resellos/frontend/.env.local
```

Use:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

### 4.4 Start LM Studio with Qwen Vision

In LM Studio:

1. Load your Qwen vision model.
2. Start the OpenAI-compatible local server.
3. Confirm the server is available at:

```text
http://localhost:1234/v1
```

Test it:

```bash
curl http://localhost:1234/v1/models
```

Copy the exact model ID returned by LM Studio and place it in:

```env
VISION_LLM_MODEL=exact_model_id_from_lm_studio
```

---

### 4.5 Install and Run Backend

```bash
cd /Users/admin/CascadeProjects/is44ks-shop/resellos/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m compileall app
uvicorn app.main:app --reload --port 8000
```

Backend should be available at:

```text
http://localhost:8000
```

API docs:

```text
http://localhost:8000/docs
```

---

### 4.6 Install and Run Frontend

Open a new terminal:

```bash
cd /Users/admin/CascadeProjects/is44ks-shop/resellos/frontend
npm install
npm run dev
```

Frontend should be available at:

```text
http://localhost:3000
```

---

## 5. First Smoke Test

Start with DataForSEO disabled:

```env
DATAFORSEO_ENABLED=false
```

Then test:

1. Open `http://localhost:3000/discovery`.
2. Create a rough product idea.
3. Run Quick Scan.
4. Generate research tasks.
5. Mark one task as done.
6. Promote the idea into a product.
7. Open the product cockpit.
8. Add supplier information manually.
9. Add marketplace evidence manually.
10. Run product research.

Expected result:

```text
The app should create the idea, generate tasks, promote to product, and show cockpit readiness without needing paid APIs.
```

---

## 6. Optional DataForSEO Setup

Use DataForSEO only after the app works without it.

Update backend `.env`:

```env
DATAFORSEO_ENABLED=true
DATAFORSEO_LOGIN=your_dataforseo_login
DATAFORSEO_PASSWORD=your_dataforseo_password
DATAFORSEO_QUEUE=standard
DATAFORSEO_MAX_RESULTS_PER_QUERY=20
DATAFORSEO_MAX_QUERIES_PER_IDEA=3
DATAFORSEO_MONTHLY_BUDGET_USD=25.0
```

Restart backend.

The app should use DataForSEO for Google Shopping research candidates.

Cost-saving rules:

```text
Use Standard Queue.
Run only when you click the button.
Limit to 3 queries per idea.
Limit to 20 results per query.
Review candidates before approving.
Do not auto-save API results as final evidence.
```

---

## 7. Daily User Workflow

This is the daily routine for a product researcher.

---

### Step 1 — Add Rough Ideas

Go to `/discovery`.

Add 10–30 rough product ideas.

For each idea, enter:

```text
Idea name
Category
Source platform
Source URL
Rough supplier cost
Estimated landed cost
Why it looks interesting
Notes
```

Example:

```text
Idea name: Car seat gap organizer
Category: Car accessories
Source platform: AliExpress
Source URL: supplier or search URL
Rough supplier cost: 2.50
Estimated landed cost: 5.00
Why interesting: Small, generic, solves a daily car organization problem.
```

---

### Step 2 — Run Quick Scan

Click Quick Scan.

The system should return:

```text
Quick scan verdict
Research priority
Reason
Suggested keywords
Required next evidence
Initial risk flags
Generated tasks
```

Interpretation:

```text
REJECT → ignore/archive
NEEDS_MARKET_CHECK → collect sold/active listings
NEEDS_SUPPLIER_CHECK → verify cost and shipping
PROMISING_FOR_RESEARCH → work the research tasks next
```

Do not treat Quick Scan as permission to buy. It only decides whether the idea deserves more research.

---

### Step 3 — Generate and Work Tasks

Generate category-specific tasks.

Common task types:

```text
Market research
Supplier research
Competition research
Risk research
Shipping/dimension research
```

Mark each task as:

```text
TODO
DONE
SKIPPED
BLOCKED
```

Add notes when useful.

Examples:

```text
Task: Add 5 sold eBay listings
Note: Found 3 strong sold listings; need 2 more.
Status: TODO
```

```text
Task: Confirm product weight and shipping
Note: Supplier says 150g/unit, shipping for 5 units is $8.40.
Status: DONE
```

---

### Step 4 — Run External Research if Needed

If DataForSEO is enabled, use External Research to get Google Shopping candidates.

Good use cases:

```text
Find Google Shopping product price range.
Find active sellers.
Find common product titles.
Find product variants.
```

Important:

```text
Google Shopping results are active market presence, not sold demand proof.
Do not count them as sold evidence.
Use them as candidates only.
```

Workflow:

1. Click Run External Research.
2. Review generated queries.
3. Submit standard queue job.
4. Poll job later.
5. Review candidates.
6. Approve useful candidates as evidence or competitors.
7. Reject irrelevant candidates.

---

### Step 5 — Capture Manual Evidence

Use capture when you manually find useful data online.

Capture inputs:

```text
URL
Pasted text
Screenshot
Notes
```

Capture types:

```text
Marketplace screenshot/text
Supplier screenshot/text
Competitor screenshot/text
Visual risk screenshot
```

The system creates an evidence candidate. You approve or reject it.

Use manual capture for:

```text
eBay sold listings
Mercari listings
Supplier pages
Competitor listings
Screenshots with price/shipping info
```

---

### Step 6 — Review Evidence Candidates

Evidence candidates are not final evidence.

For each candidate, choose:

```text
Approve as marketplace evidence
Approve as competitor listing
Approve as supplier source, if supported by the current UI
Reject
```

When approving, link the candidate to a task if possible.

Example:

```text
Task: Add 5 sold eBay listings
Candidate: eBay SOLD_LISTING, $18.99 + $4.99 shipping
Action: Approve as marketplace evidence and link to task
```

---

### Step 7 — Use the Opportunity Board

Use the Opportunity Board to decide what to work on next.

For ideas, focus on:

```text
Discovery completeness
Quick scan verdict
Research priority
Task progress
Next action
```

For promoted products, focus on:

```text
Research completeness
Sold evidence count
Active evidence count
Median sold price
Best landed cost
Best profit scenario
Competition gap score
Buy readiness
Next action
```

A good product candidate should show:

```text
Low risk
Enough sold evidence
Enough active evidence
Clear supplier cost
Good landed cost
Good profit scenario
Weak enough competition
Clear next action
```

---

### Step 8 — Promote the Best Ideas

Promote only the best ideas into products.

A good idea to promote has:

```text
Acceptable quick scan verdict
Clear category
Low obvious risk
Some market signal
Possible supplier path
Research tasks worth completing
```

After promotion, go to the Product Cockpit.

---

### Step 9 — Complete Product Cockpit Research

In the Product Cockpit, add:

```text
Supplier sources
Sold listing evidence
Active listing evidence
Competitor listings
Manual capture candidates
Vision-extracted candidates
```

Minimum evidence before considering samples:

```text
5 sold listings
5 active listings
2 supplier options when possible
3 competitor examples
Supplier landed cost
Shipping estimate
Product weight/dimensions
```

---

### Step 10 — Run Product Research

Click Run Research.

The system should analyze:

```text
Risk
Market evidence
Competition
Profit scenarios
Decision readiness
```

It should return:

```text
Research verdict
Buy readiness
Research completeness score
Opportunity score
Main blocker
Hard blockers
Required before buying
Target sale price
Max landed cost
Max quantity to buy
```

---

## 8. Decision Rules

Do not buy samples unless the product is ready.

A product should not be treated as sample-ready unless:

```text
Risk is not blocked.
Sold listing count is at least 5.
Active listing count is at least 5.
Supplier cost exists.
International shipping estimate exists.
Market price is not missing.
Target sale price is greater than 0.
Estimated net profit meets your minimum.
Margin meets your minimum.
Competition is beatable.
```

If those are not true, the result should be:

```text
Needs more research
Promising research
Watchlist
Reject
```

Only buy when the system indicates:

```text
READY_FOR_SAMPLE
```

---

## 9. Evidence Standards

### Sold Listing Evidence

For each sold listing, capture:

```text
Marketplace
Evidence type: SOLD_LISTING
Title
Sold price
Shipping price
Sold date, if available
Condition
URL
Notes
```

### Active Listing Evidence

For each active listing, capture:

```text
Marketplace
Evidence type: ACTIVE_LISTING
Title
Active price
Shipping price
Condition
URL
Notes
```

### Supplier Evidence

For each supplier, capture:

```text
Supplier platform
Supplier name
Supplier URL
Unit cost
Domestic shipping
International shipping estimate
Estimated landed cost
MOQ
Supplier rating/notes
Product weight
Product dimensions
Logo/brand risk
```

### Competitor Evidence

For each competitor, capture:

```text
Marketplace
Title
URL
Price
Shipping
Sold or active
Photo quality
Title quality
Description quality
Weakness notes
```

---

## 10. What to Research by Category

The app has category playbooks. Use them as guidance.

### Car Accessories

Look for:

```text
Non-mechanical products
Non-safety-critical products
Clear dimensions
Universal fit claims
Installation photos
Bundle opportunities
```

Avoid:

```text
Airbag-related items
Seatbelt-related items
Brake/engine/mechanical parts
Electrical/battery items unless reviewed
```

---

### Pet Accessories

Look for:

```text
Grooming tools
Hair removers
Bowls or simple accessories
Cleaning/use-case photos
Material clarity
```

Avoid:

```text
Pet medicine
Supplements
Ingestible products
Shock collars
Strong safety claims
```

---

### Desk Accessories

Look for:

```text
Cable management
Desk organization
Simple setup tools
Aesthetic appeal
Bundle potential
```

Check:

```text
Dimensions
Material
Photo quality
Competitor listing weaknesses
```

---

### Home Organization

Look for:

```text
Drawer organizers
Closet helpers
Storage clips
Small space-saving products
Before/after photo potential
```

Check:

```text
Dimensions
Material quality
Shipping size
Bundle potential
```

---

### Travel Accessories

Look for:

```text
Packing helpers
Cable pouches
Bag organization
Compact lightweight items
```

Check:

```text
Weight
Dimensions
Durability
Real-use photos
```

---

### Creator Tools

Look for:

```text
Phone stands
Lighting accessories
Cable organization
Simple camera/desk helpers
```

Avoid:

```text
Complex electronics
Battery products unless carefully reviewed
Trademark/brand-risk designs
```

---

## 11. Daily Research Routine

Use this daily routine.

### Morning Session — 30 to 45 minutes

```text
Add 5–10 new ideas.
Quick scan them.
Archive obvious rejects.
Generate tasks for promising ideas.
```

### Research Session — 60 to 90 minutes

```text
Pick top 3 ideas from Opportunity Board.
Collect sold listings.
Collect active listings.
Capture supplier pages.
Capture competitor listings.
Approve/reject evidence candidates.
Mark tasks done/skipped/blocked.
```

### Review Session — 20 to 30 minutes

```text
Check Opportunity Board.
Promote strongest idea to product.
Run product research.
Review readiness.
Decide next action.
```

---

## 12. Weekly Research Goal

For one week, aim for:

```text
50 product ideas entered
20 quick scanned
10 researched lightly
5 researched deeply
2 promoted to product cockpit
1 possible READY_FOR_SAMPLE candidate
```

Do not buy samples in week one unless the evidence is strong.

---

## 13. What Not to Do Yet

Do not focus on:

```text
Sales tracking
Inventory analytics
Reorder logic
Returns
Marketplace publishing
Shopify
TikTok Shop
Amazon seller automation
Mass scraping
Proxy rotation
CAPTCHA bypass
Auto-buying
```

The current mission is:

```text
Find one low-risk, generic product with real sold evidence, clear supplier cost, realistic profit, and beatable competition.
```

---

## 14. DataForSEO Usage Rules

Use DataForSEO carefully.

Recommended settings:

```text
Standard queue
Max 3 queries per idea
Max 20 results per query
Monthly budget: $25
Cache same query for 14 days
```

Use DataForSEO for:

```text
Google Shopping active market presence
Price ranges
Seller/domain discovery
Product title variations
Idea expansion
```

Do not use it as final buying proof.

Google Shopping is not sold evidence. It shows what is listed, not necessarily what buyers purchased.

---

## 15. Vision Usage Rules

Use Qwen Vision for:

```text
Screenshots
Listing extraction
Supplier page extraction
Competitor photo analysis
Visual risk checks
```

Never auto-save vision output as final evidence.

Correct flow:

```text
Upload screenshot
→ Vision extracts candidate
→ You review
→ You approve or reject
→ Evidence is saved only after approval
```

Common mistakes to watch for:

```text
Wrong price extraction
Shipping confused with item price
Quantity confused with price
Seller name missing
Sold/active status misread
Logo risk missed
```

---

## 16. Troubleshooting

### Backend cannot connect to Postgres

Check Docker:

```bash
docker compose ps
```

Make sure backend `.env` uses:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/resellos
```

because backend is local and Postgres is Docker-exposed to localhost.

---

### LM Studio Vision fails

Check:

```bash
curl http://localhost:1234/v1/models
```

Make sure:

```env
VISION_LLM_BASE_URL=http://localhost:1234/v1
VISION_LLM_MODEL=exact_model_id_from_lm_studio
```

Restart backend after editing `.env`.

---

### DataForSEO does not run

Check:

```env
DATAFORSEO_ENABLED=true
DATAFORSEO_LOGIN=your_login
DATAFORSEO_PASSWORD=your_password
```

Also confirm you are not over your budget limit:

```env
DATAFORSEO_MONTHLY_BUDGET_USD=25.0
```

---

### Frontend shows demo data

The frontend has fallback/demo behavior when API calls fail. If the app looks like it is showing demo products, check that backend is running:

```text
http://localhost:8000/health
```

And confirm frontend `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Restart frontend after editing `.env.local`.

---

### Migrations fail

Run:

```bash
cd resellos/backend
alembic upgrade head
```

If it fails, verify Postgres is running and the database URL is correct.

---

## 17. First Real Research Run

Do this after setup works.

### Phase 1 — Add Ideas

Add these 20 rough ideas:

```text
car seat gap organizer
car trash bag holder
car trunk hook
car cup holder expander
pet hair remover
dog grooming glove
collapsible pet bowl
desk cable clips
under desk cable tray
foldable phone stand
drawer divider
closet organizer clips
travel cable pouch
packing cube tags
makeup brush organizer
kitchen bag clips
reusable lint remover
shoe cleaning brush
plant watering spikes
small tool magnetic tray
```

### Phase 2 — Quick Scan

Quick scan all 20.

Archive:

```text
Obvious brand risk
Medical/supplement/ingestible products
Electrical/battery products unless worth deeper review
Weak/unclear products
```

### Phase 3 — Research Top 5

For the top 5:

```text
Add 5 sold listings
Add 5 active listings
Add 2 suppliers
Add 3 competitors
Confirm dimensions
Confirm shipping/weight
```

### Phase 4 — Promote Top 2–3

Promote only the strongest ideas.

### Phase 5 — Run Product Research

In the product cockpit:

```text
Review discovery context
Check evidence counts
Check profit scenarios
Run research
Check readiness
```

### Phase 6 — Decide

Only buy samples if:

```text
READY_FOR_SAMPLE
```

Otherwise keep researching or reject.

---

## 18. Completion Definition for Research Phase

The research phase is “working” when you can:

```text
Create ideas
Quick scan ideas
Generate category-specific tasks
Capture evidence manually or by screenshot
Run external Google Shopping research when needed
Review and approve candidates
Link tasks to proof
Compare ideas/products on Opportunity Board
Promote ideas to products
Run product research
Identify one READY_FOR_SAMPLE product
```

Once you can do that, stop coding and start researching.

---

## 19. Practical Daily Rule

Every product must earn your money.

Before you buy samples, force the product to answer:

```text
Who is buying this?
What proof do I have?
What price does it sell for?
What will it cost me landed?
Can I ship it profitably?
Can I beat competitors?
Is it safe and generic?
What is my max quantity to buy?
```

If the answers are weak, do not buy.

---

## 20. Recommended First Milestone

Your first real milestone is not revenue.

Your first milestone is:

```text
One researched product reaches READY_FOR_SAMPLE with real evidence.
```

That means:

```text
5+ sold evidence rows
5+ active evidence rows
2 supplier options if possible
3 competitor examples
clear landed cost
clear target sale price
acceptable profit
acceptable margin
low risk
beatable competition
```

When you reach that point, order the smallest reasonable sample quantity.

---

## Appendix A — Minimal Local Command List

```bash
# Terminal 1: Postgres only
cd /Users/admin/CascadeProjects/is44ks-shop/resellos
docker compose up -d db
```

```bash
# Terminal 2: Backend
cd /Users/admin/CascadeProjects/is44ks-shop/resellos/backend
source .venv/bin/activate
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

```bash
# Terminal 3: Frontend
cd /Users/admin/CascadeProjects/is44ks-shop/resellos/frontend
npm run dev
```

```text
LM Studio: running separately at http://localhost:1234/v1
```

---

## Appendix B — Minimum API Keys

Required:

```text
MiniMax API key
```

Required for vision:

```text
Local LM Studio Qwen model running
```

Optional:

```text
DataForSEO login/password
```

Not needed yet:

```text
eBay
Amazon
Shopify
Stripe
TikTok
Facebook
SendGrid
Twilio
```

---

## Appendix C — Source Areas Reviewed

This manual was based on the current repository structure and the app areas for:

```text
resellos/backend/app/routes/discovery.py
resellos/backend/app/routes/external_research.py
resellos/backend/app/routes/evidence_candidates.py
resellos/backend/app/routes/capture.py
resellos/backend/app/routes/vision.py
resellos/backend/app/services/discovery_service.py
resellos/backend/app/services/category_templates.py
resellos/frontend/app/discovery/page.tsx
resellos/frontend/app/products/[id]/page.tsx
resellos/frontend/app/capture/page.tsx
resellos/frontend/lib/api.ts
resellos/backend/.env.example
resellos/docker-compose.yml
```

