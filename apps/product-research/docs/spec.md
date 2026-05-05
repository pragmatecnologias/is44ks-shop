Software Specification
AI Product Research & Reselling Intelligence Tool
1. Product Name

ResellOS
Alternative names:

ProductHunter AI
SoloCommerce AI
ResellPilot
MarketScout AI
ImportOps AI

For this spec, I’ll call it ResellOS.

2. Vision

ResellOS is an AI-powered research and decision platform for a solo online reselling business.

The tool helps the user discover products, evaluate supplier listings, analyze marketplace demand, estimate profitability, detect risk, generate optimized listings, and make better buy/skip/reorder decisions.

The purpose is not just to “find cheap products.” The purpose is to create a disciplined buying system that prevents emotional purchases, avoids counterfeit/legal risk, identifies profitable opportunities, and builds a repeatable online selling operation.

3. Core Problem

A beginner or solo reseller usually struggles with:

1. Finding products worth buying.
2. Knowing if a product actually sells.
3. Estimating real profit after all costs.
4. Avoiding fake/branded/restricted products.
5. Understanding marketplace competition.
6. Knowing whether competitor listings are weak.
7. Creating better product listings.
8. Tracking samples, inventory, sales, and reorders.
9. Avoiding random buying decisions.
10. Scaling only the products that prove demand.

ResellOS solves this by converting product research into a structured workflow with AI agents, scoring, evidence, and human approval.

4. Product Goal

The system should answer this question for every product:

Should I buy this product, skip it, watch it, or block it?

The answer should be based on:

- Legal/compliance risk
- Marketplace demand
- Active competition
- Sold price evidence
- Supplier cost
- Shipping cost
- Platform fees
- Profit margin
- Listing improvement opportunity
- Product quality risk
- Ease of shipping
- Reorder potential
5. Target User
Primary User

A solo entrepreneur who wants to buy products from sites like Kakobuy, 1688, Taobao, AliExpress, Alibaba, or other sourcing platforms and sell them online in the United States through marketplaces like:

- eBay
- Mercari
- Facebook Marketplace
- TikTok Shop
- Amazon later
- Shopify later
Secondary Users Later

Possible future roles:

- Virtual assistant
- Product researcher
- Listing assistant
- Warehouse/packing assistant
- Business partner

For MVP, the app is single-user.

6. Business Positioning

ResellOS is not a dropshipping tool.

It is a small-batch product research and reselling command center.

The recommended business workflow is:

Find product idea
Research demand
Check risk
Estimate profit
Order samples
Inspect quality
Create listings
Track sales
Reorder winners
Kill losers
7. Non-Negotiable Business Rules

The system must strongly discourage or block:

- Counterfeit products
- Replica products
- Fake designer items
- Fake electronics
- Trademark-infringing products
- Products using famous brand logos without authorization
- Products marketed as “1:1,” “UA,” “mirror,” “replica,” “dupe” with brand intent
- Supplements
- Cosmetics/skincare for early MVP
- Medical products
- Baby safety products
- Food-contact products unless explicitly marked as reviewed
- Products with lithium batteries
- Wall chargers/power adapters
- Automotive safety/mechanical parts
- Weapons or self-defense products
- Hazardous chemicals

The system should not help the user sell counterfeit goods.

8. Product Scope
MVP Scope

The MVP should support:

1. Product idea intake
2. Supplier link/data intake
3. Manual marketplace research entry
4. AI risk analysis
5. AI market analysis
6. AI profitability analysis
7. AI listing gap analysis
8. Final product score
9. Buy/sample/skip/block recommendation
10. Listing generation
11. Basic inventory tracking
12. Basic sales tracking
13. Reorder recommendation
14. Dashboard
15. Product research report export
V2 Scope
1. Browser-assisted marketplace research
2. eBay API integration for active listings
3. Screenshot/listing text analysis
4. Supplier comparison
5. Product image/photo grading
6. Competitor listing database
7. More advanced sales analytics
8. Reorder forecasting
9. Marketplace-specific listing optimizer
10. Notification system
V3 Scope
1. Semi-autonomous product discovery
2. Trend monitoring
3. TikTok/Google Trends integration
4. Shopify listing publishing
5. eBay listing publishing
6. Inventory sync
7. Customer message analysis
8. Return reason analysis
9. Supplier performance scoring
10. AI business coach dashboard
9. High-Level System Concept

The user enters a product idea or supplier link.

The system runs the product through a sequence of AI agents:

Product Intake
   ↓
Risk Agent
   ↓
Market Research Agent
   ↓
Supplier Agent
   ↓
Profit Agent
   ↓
Competition Agent
   ↓
Listing Strategy Agent
   ↓
Decision Agent
   ↓
Human Approval
   ↓
Sample Order / Skip / Watchlist / Block

The system stores all research evidence and recommendations.

10. Main Product Decisions

Every product must end in one of these statuses:

NEW
NEEDS_RESEARCH
RESEARCHING
BLOCKED
WATCHLIST
BUY_SAMPLE
SAMPLE_ORDERED
SAMPLE_RECEIVED
APPROVED_TO_LIST
LISTED
SELLING
SLOW_MOVING
REORDER_CANDIDATE
REORDERED
KILL_PRODUCT
ARCHIVED
11. Final Product Recommendation Types

The Decision Agent must produce one of:

BLOCKED
SKIP
WATCHLIST
BUY_SAMPLE
BUY_SMALL_BATCH
REORDER
SCALE
Meaning
BLOCKED

The product has legal, counterfeit, safety, platform, or serious quality risk.

SKIP

The product is not worth buying because demand, profit, competition, or quality is bad.

WATCHLIST

The product may be interesting but does not have enough evidence.

BUY_SAMPLE

The product is promising enough to order 1–5 units.

BUY_SMALL_BATCH

The product has strong evidence and can be tested with 10–30 units.

REORDER

The product has sold profitably and should be reordered.

SCALE

The product is a proven winner and deserves bundles, branding, ads, or a dedicated storefront.

12. User Workflow
12.1 Product Research Workflow
1. User creates product idea.
2. User adds product name, category, supplier link, price, and notes.
3. System runs Risk Agent.
4. If product is blocked, workflow stops.
5. User adds marketplace research manually or through assisted research.
6. System runs Market Research Agent.
7. System runs Profit Agent.
8. System runs Competition Agent.
9. System runs Listing Strategy Agent.
10. Decision Agent generates score and recommendation.
11. User approves next action.
12.2 Sample Order Workflow
1. Product receives BUY_SAMPLE recommendation.
2. User marks sample as ordered.
3. User enters sample order cost, shipping, expected arrival date.
4. When sample arrives, user uploads photos and inspection notes.
5. Quality Agent reviews sample notes/photos.
6. Product status changes to APPROVED_TO_LIST or KILL_PRODUCT.
12.3 Listing Workflow
1. User selects approved product.
2. Listing Agent generates title, description, keywords, photo checklist, and price.
3. User creates marketplace listings manually.
4. User stores marketplace URLs in the system.
5. Product status changes to LISTED.
12.4 Sales Tracking Workflow
1. User records each sale manually.
2. System calculates actual profit.
3. System compares actual profit vs estimated profit.
4. Reorder Agent evaluates performance.
5. System recommends reorder, price adjustment, bundle, or kill.
12.5 Reorder Workflow
1. Product reaches reorder threshold.
2. Reorder Agent reviews sales velocity, profit, returns, and remaining inventory.
3. System recommends reorder quantity.
4. User approves reorder.
5. Inventory expected quantity is updated.
13. System Modules
13.1 Product Intake Module

Allows the user to create and manage product ideas.

Fields
Product name
Internal SKU
Category
Subcategory
Description
Supplier source
Supplier URL
Supplier price
Estimated shipping
MOQ
Estimated landed cost
Product weight
Product dimensions
Notes
Images
Status
Functional Requirements
- User can create a product idea.
- User can paste supplier links.
- User can attach images/screenshots.
- User can assign category.
- User can add cost estimates.
- User can mark whether product is branded or generic.
- System can generate an internal SKU.
13.2 Risk & Compliance Module

Evaluates whether the product is safe and acceptable to research further.

Risk Categories
Counterfeit risk
Trademark risk
Marketplace policy risk
Import risk
Electrical risk
Battery risk
Medical risk
Cosmetic risk
Supplement risk
Baby/child safety risk
Automotive safety risk
Food-contact risk
Hazardous material risk
Return/fraud risk
Quality risk
Risk Levels
LOW
MEDIUM
HIGH
BLOCKED
Blocking Keywords

The system should flag product titles/descriptions containing:

replica
1:1
UA
mirror
designer
inspired by
same as original
luxury brand
Nike
Adidas
Jordan
Apple
AirPods
Rolex
LV
Gucci
Prada
Dior
Chanel
Hermes
Supreme
Balenciaga
Yeezy
Stanley logo

The list should be configurable.

Functional Requirements
- System must run risk analysis before market/profit recommendation.
- System must block obviously counterfeit or trademark-risk products.
- System must explain why a product was blocked.
- User can override MEDIUM/HIGH risks only with a reason.
- User cannot override BLOCKED without changing admin policy.
- Every risk result must be stored as an auditable report.
13.3 Marketplace Research Module

Stores and analyzes marketplace data.

Marketplaces Supported in MVP
eBay
Mercari
Facebook Marketplace
Amazon manual research
Other/manual
Data Types
Active listings
Sold listings
Completed listings
Competitor listings
Shipping cost examples
Listing screenshots
Copied listing text
Manual notes
Marketplace Research Fields
Product ID
Marketplace
Search keyword
Search URL
Active listing count
Sold listing count
Min active price
Median active price
Max active price
Min sold price
Median sold price
Max sold price
Shipping min
Shipping median
Shipping max
Number of competitor listings reviewed
Sell-through signal
Competition level
Notes
Evidence links
Research date
Functional Requirements
- User can manually enter marketplace research.
- User can paste multiple competitor listings.
- User can upload screenshots.
- System can summarize pasted listing data.
- System can estimate median price.
- System can estimate competition level.
- System can compare active price vs sold price.
- System can generate a demand confidence score.
13.4 Supplier Research Module

Analyzes supplier options.

Supplier Types
Kakobuy
1688
Taobao
Weidian
AliExpress
Alibaba
Temu-style retail source
Local wholesale source
Other/manual
Supplier Fields
Supplier name
Supplier platform
Supplier URL
Product cost
MOQ
Available variations
Estimated domestic China shipping
Estimated international shipping
Estimated landed cost
Supplier rating
Supplier notes
Risk flags
Sample ordered?
Sample received?
Quality notes
Functional Requirements
- User can add multiple suppliers per product.
- System compares suppliers.
- System estimates landed cost.
- System flags suspicious supplier claims.
- System recommends best supplier for sample order.
- System asks questions the user should ask the supplier.
13.5 Profitability Module

Calculates expected and actual profit.

Expected Profit Formula
Expected Net Profit =
Expected Sale Price
- Product Unit Cost
- Import Shipping Per Unit
- Marketplace Fee
- U.S. Shipping Cost
- Packaging Cost
- Return Allowance
- Payment Processing Fee if separate
- Ad Cost if any
Fields
Expected sale price
Product cost
Import shipping per unit
Landed cost
Marketplace fee
U.S. shipping
Packaging cost
Return allowance
Ad cost
Estimated net profit
Estimated margin %
ROI %
Break-even sale price
Minimum acceptable sale price
Functional Requirements
- System calculates estimated profit.
- System calculates break-even price.
- System calculates minimum sale price.
- System calculates margin.
- System supports marketplace fee presets.
- System supports custom fee override.
- System supports buyer-paid shipping and seller-paid shipping scenarios.
- System supports bundle pricing.
13.6 Competition Analysis Module

Evaluates whether the user can beat existing sellers.

Competition Factors
Number of active listings
Price saturation
Photo quality
Title quality
Description quality
Bundle quality
Shipping speed
Review/trust signals
Listing completeness
Use of real photos
Use of factory photos
Fitment/size clarity
Return policy
Listing Quality Score

Each competitor listing can be scored:

Title score: 0–10
Photo score: 0–10
Description score: 0–10
Price competitiveness: 0–10
Trust score: 0–10
Shipping score: 0–10
Total listing score: 0–60
Functional Requirements
- System identifies competitor weaknesses.
- System recommends listing angles.
- System identifies bundle opportunities.
- System flags race-to-bottom markets.
- System suggests whether user can differentiate.
13.7 Product Scoring Module

Every product gets a structured score.

Score Components
Demand Score: 0–20
Profit Score: 0–20
Risk Score: 0–20
Competition Score: 0–15
Shipping Score: 0–10
Listing Gap Score: 0–10
Supplier Confidence Score: 0–5

Total: 100 points

13.8 Scoring Rules
Demand Score
0–5: No evidence of demand
6–10: Weak demand
11–15: Moderate demand
16–20: Strong demand

Signals:

Sold listings exist
Multiple marketplaces show activity
Product solves obvious problem
Trend evidence exists
Search volume exists
Repeatable buyer need
Profit Score
0–5: Profit too low
6–10: Profit exists but weak
11–15: Acceptable profit
16–20: Strong profit

Suggested thresholds:

Below $3 net profit: weak
$3–$5 net profit: possible
$5–$10 net profit: good
$10+ net profit: strong

Also consider margin:

Below 20%: weak
20–30%: acceptable
30–50%: good
50%+: strong
Risk Score
0: Blocked
1–5: High risk
6–12: Medium risk
13–20: Low risk

Blocked overrides total score.

Competition Score
0–5: Too saturated
6–10: Competitive but possible
11–15: Healthy competition

Competition is not always bad. No competition can mean no demand. Too much competition with identical listings can mean low margin.

Shipping Score
0–3: Heavy/fragile/expensive
4–7: Manageable
8–10: Small, light, easy to ship
Listing Gap Score
0–3: Competitors already have excellent listings
4–7: Some improvement possible
8–10: Major listing improvement opportunity
Supplier Confidence Score
0–1: Suspicious/unknown
2–3: Acceptable for samples
4–5: Strong supplier confidence
13.9 Decision Rules
If risk is BLOCKED:
    Decision = BLOCKED

Else if total score >= 85:
    Decision = BUY_SMALL_BATCH or BUY_SAMPLE

Else if total score >= 70:
    Decision = BUY_SAMPLE

Else if total score >= 55:
    Decision = WATCHLIST

Else:
    Decision = SKIP

Additional rules:

If expected net profit < $3:
    Decision cannot exceed WATCHLIST unless bundle opportunity exists.

If no sold evidence exists:
    Decision cannot exceed WATCHLIST unless strong trend evidence exists.

If product requires safety compliance:
    Decision cannot exceed WATCHLIST without manual approval.

If supplier cost is uncertain:
    Decision cannot exceed BUY_SAMPLE.

If product is fragile/heavy:
    Reduce shipping score and require manual review.
14. AI Agent System
14.1 Agent Overview

The system should include these agents:

1. Product Discovery Agent
2. Risk Agent
3. Marketplace Research Agent
4. Supplier Analysis Agent
5. Profit Agent
6. Competition Agent
7. Listing Strategy Agent
8. Photo Review Agent
9. Decision Agent
10. Reorder Agent
11. Business Coach Agent

MVP should start with:

1. Risk Agent
2. Marketplace Research Agent
3. Profit Agent
4. Listing Strategy Agent
5. Decision Agent
15. Agent Specifications
15.1 Risk Agent
Purpose

Determine whether a product is safe and acceptable to research or sell.

Inputs
Product name
Description
Supplier URL
Supplier text
Images
Category
Marketplace notes
User notes
Outputs
{
  "risk_level": "LOW | MEDIUM | HIGH | BLOCKED",
  "blocked": true,
  "risk_categories": [],
  "reasoning_summary": "",
  "red_flags": [],
  "recommended_action": ""
}
Rules
- Must block counterfeit/replica/trademark-risk products.
- Must flag famous brands.
- Must flag unsafe categories.
- Must not recommend selling restricted products.
- Must explain issues in simple language.
15.2 Marketplace Research Agent
Purpose

Analyze demand, pricing, and competition from marketplace evidence.

Inputs
Product name
Marketplace
Search keyword
Active listing data
Sold listing data
Screenshots
Pasted text
User notes
Outputs
{
  "demand_signal": "LOW | MEDIUM | HIGH",
  "competition_level": "LOW | MEDIUM | HIGH | SATURATED",
  "median_active_price": 0,
  "median_sold_price": 0,
  "price_range": {
    "min": 0,
    "max": 0
  },
  "shipping_observations": "",
  "sell_through_signal": "",
  "evidence_quality": "LOW | MEDIUM | HIGH",
  "summary": "",
  "recommendation": ""
}
Requirements
- Must separate evidence from assumptions.
- Must not invent sold data.
- Must state when data is insufficient.
- Must recommend better keywords if needed.
15.3 Supplier Analysis Agent
Purpose

Evaluate sourcing quality and supplier attractiveness.

Inputs
Supplier platform
Supplier link
Product cost
MOQ
Shipping estimate
Supplier notes
Images
Variations
Outputs
{
  "supplier_confidence": "LOW | MEDIUM | HIGH",
  "estimated_landed_cost": 0,
  "risk_flags": [],
  "questions_for_supplier": [],
  "sample_order_recommendation": "",
  "max_sample_quantity": 0
}
Requirements
- Must recommend sample order before bulk order.
- Must flag factory-only photos.
- Must flag unclear dimensions.
- Must flag logos/brand issues.
15.4 Profit Agent
Purpose

Calculate estimated profitability.

Inputs
Expected sale price
Product cost
Import shipping
U.S. shipping
Marketplace fee
Packaging cost
Return allowance
Ad cost
Quantity
Outputs
{
  "expected_sale_price": 0,
  "landed_cost": 0,
  "total_cost": 0,
  "estimated_net_profit": 0,
  "margin_percent": 0,
  "roi_percent": 0,
  "break_even_price": 0,
  "minimum_recommended_price": 0,
  "profit_verdict": "BAD | WEAK | ACCEPTABLE | GOOD | STRONG",
  "notes": ""
}
Requirements
- Must calculate all costs.
- Must expose assumptions.
- Must compare buyer-paid shipping vs seller-paid shipping.
- Must warn if profit disappears after fees.
15.5 Competition Agent
Purpose

Evaluate how hard it will be to compete and how to differentiate.

Inputs
Competitor listings
Photos
Titles
Descriptions
Prices
Shipping
Reviews
Marketplace data
Outputs
{
  "competition_level": "LOW | MEDIUM | HIGH | SATURATED",
  "competitor_weaknesses": [],
  "differentiation_opportunities": [],
  "bundle_opportunities": [],
  "listing_gap_score": 0,
  "summary": ""
}
Requirements
- Must identify actual weaknesses.
- Must not claim opportunity without evidence.
- Must suggest a listing angle.
15.6 Listing Strategy Agent
Purpose

Generate marketplace-ready listing content.

Inputs
Product name
Features
Dimensions
Photos
Target buyer
Competitor weaknesses
Recommended price
Marketplace
Outputs
{
  "ebay_title": "",
  "mercari_title": "",
  "facebook_title": "",
  "short_description": "",
  "long_description": "",
  "bullet_points": [],
  "seo_keywords": [],
  "photo_checklist": [],
  "bundle_ideas": [],
  "pricing_strategy": ""
}
Requirements
- eBay title must be under 80 characters.
- Must avoid trademarked terms unless product is authorized.
- Must not make false claims.
- Must not overpromise quality.
- Must include dimensions if known.
- Must include what is included.
15.7 Photo Review Agent
Purpose

Review product photos and recommend improvements.

Inputs
Uploaded product photos
Competitor photos
Listing requirements
Outputs
{
  "photo_score": 0,
  "missing_photos": [],
  "thumbnail_recommendation": "",
  "improvement_notes": [],
  "trust_score": 0
}
Photo Checklist
White background photo
Real-life usage photo
Size/dimensions photo
Close-up material photo
What is included photo
Packaging photo
Before/after photo if applicable
Lifestyle photo
15.8 Decision Agent
Purpose

Combine all reports and produce the final recommendation.

Inputs
Risk report
Market report
Supplier report
Profit report
Competition report
Listing strategy report
User constraints
Outputs
{
  "final_score": 0,
  "decision": "BLOCKED | SKIP | WATCHLIST | BUY_SAMPLE | BUY_SMALL_BATCH | REORDER | SCALE",
  "reason": "",
  "next_action": "",
  "max_quantity_to_buy": 0,
  "max_landed_cost": 0,
  "target_sale_price": 0,
  "confidence": "LOW | MEDIUM | HIGH",
  "open_questions": []
}
Requirements
- Must not recommend bulk buying without sales evidence.
- Must block risky products.
- Must explain decision clearly.
- Must give next action.
15.9 Reorder Agent
Purpose

Determine whether a product should be reordered.

Inputs
Units sold
Days listed
Current inventory
Actual profit
Return rate
Buyer questions
Customer complaints
Price changes
Competitor changes
Supplier availability
Outputs
{
  "reorder_recommendation": "DO_NOT_REORDER | REORDER_SMALL | REORDER_MEDIUM | SCALE",
  "recommended_quantity": 0,
  "reason": "",
  "price_adjustment": "",
  "listing_improvements": [],
  "risk_notes": []
}
Rules
If product sold 70%+ of inventory within target period and return rate is low:
    Consider reorder.

If actual profit is below minimum:
    Do not reorder unless bundle or price increase is possible.

If many customer complaints:
    Do not reorder until quality issue is resolved.
16. UI/UX Specification
16.1 Design Style

The app should feel like a serious business control center.

Recommended style:

Modern dashboard
Dark/light mode
Data-heavy but clean
Cards + tables
AI reports in panels
Evidence attached to decisions
Clear status badges
Strong color coding for risk and decisions

Color meaning:

Green: profitable / low risk / approved
Yellow: watchlist / uncertain / needs review
Red: blocked / high risk / skip
Blue: research / neutral info
Purple: AI-generated insights
17. Main Screens
17.1 Dashboard

Purpose: quick view of the business pipeline.

Widgets
Total products researched
Products blocked
Products in watchlist
Products recommended for samples
Products ordered
Products listed
Units sold
Estimated profit
Actual profit
Reorder candidates
Top categories
Dashboard Sections
1. Product Pipeline
2. Top Opportunities
3. Risk Alerts
4. Recently Researched Products
5. Reorder Recommendations
6. Sales Performance
7. Agent Activity
17.2 Product Ideas Page

A table of product ideas.

Columns
Product
Category
Status
Risk
Score
Expected Profit
Recommended Action
Supplier
Last Updated
Actions
Create product
Import product
Run research
View report
Archive product
Duplicate product
17.3 Product Detail Page

This is the most important screen.

Header
Product name
Status badge
Final score
Decision
Risk level
Expected profit
Tabs
Overview
Supplier
Marketplace Research
Profit
Competition
AI Reports
Listings
Inventory
Sales
Reorder
Files/Images
17.4 Product Overview Tab

Shows:

Product summary
Category
Description
Main supplier
Current status
Final AI recommendation
Next action
Open questions
Timeline
17.5 Supplier Tab

Shows:

Supplier cards
Cost comparison
MOQ
Estimated shipping
Landed cost
Supplier risk
Sample order status
Supplier questions
17.6 Marketplace Research Tab

Shows:

Research entries by marketplace
Active listing data
Sold listing data
Price charts
Competitor table
Evidence links
Screenshots
AI market summary
17.7 Profit Tab

Shows:

Profit calculator
Scenario comparison
Buyer-paid shipping scenario
Free-shipping scenario
Bundle scenario
Break-even price
Minimum acceptable price
17.8 Competition Tab

Shows:

Competitor listing table
Competitor photo score
Title patterns
Weaknesses
Differentiation ideas
Bundle opportunities
17.9 AI Reports Tab

Shows all agent reports:

Risk report
Market report
Supplier report
Profit report
Competition report
Listing strategy report
Decision report

Each report should show:

Agent name
Run date
Input summary
Output
Confidence
Evidence
Warnings
17.10 Listing Builder Page

Generates listing content.

Inputs
Marketplace
Product features
Dimensions
Photos
Target price
Shipping policy
Bundle option
Outputs
Title
Short description
Long description
Bullet points
Keywords
Photo checklist
Pricing strategy
Actions
Copy listing
Save listing
Regenerate
Create variation
Mark as listed
17.11 Inventory Page

Tracks physical inventory.

Columns
SKU
Product
Quantity on hand
Quantity ordered
Quantity sold
Quantity returned
Average landed cost
Location/bin
Reorder point
Status
17.12 Sales Page

Tracks sales manually in MVP.

Columns
Sale date
Product
Marketplace
Quantity
Sale price
Marketplace fee
Shipping cost
Packaging cost
Net profit
Buyer-paid shipping?
Return?
Notes
17.13 Reorder Page

Shows reorder recommendations.

Columns
Product
Units sold
Days listed
Sell-through rate
Actual profit
Return rate
Inventory left
Recommended reorder quantity
Decision
18. Data Model
18.1 products
CREATE TABLE products (
    id UUID PRIMARY KEY,
    sku VARCHAR(100) UNIQUE,
    name TEXT NOT NULL,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'NEW',
    risk_level VARCHAR(50),
    final_score NUMERIC(5,2),
    final_decision VARCHAR(50),
    target_sale_price NUMERIC(10,2),
    expected_profit NUMERIC(10,2),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
18.2 product_sources
CREATE TABLE product_sources (
    id UUID PRIMARY KEY,
    product_id UUID NOT NULL REFERENCES products(id),
    supplier_name TEXT,
    supplier_platform VARCHAR(100),
    supplier_url TEXT,
    unit_cost NUMERIC(10,2),
    domestic_shipping NUMERIC(10,2),
    international_shipping_estimate NUMERIC(10,2),
    estimated_landed_cost NUMERIC(10,2),
    moq INTEGER,
    supplier_rating TEXT,
    notes TEXT,
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
18.3 marketplace_research
CREATE TABLE marketplace_research (
    id UUID PRIMARY KEY,
    product_id UUID NOT NULL REFERENCES products(id),
    marketplace VARCHAR(100) NOT NULL,
    keyword TEXT,
    search_url TEXT,
    active_listing_count INTEGER,
    sold_listing_count INTEGER,
    min_active_price NUMERIC(10,2),
    median_active_price NUMERIC(10,2),
    max_active_price NUMERIC(10,2),
    min_sold_price NUMERIC(10,2),
    median_sold_price NUMERIC(10,2),
    max_sold_price NUMERIC(10,2),
    shipping_min NUMERIC(10,2),
    shipping_median NUMERIC(10,2),
    shipping_max NUMERIC(10,2),
    competition_level VARCHAR(50),
    demand_signal VARCHAR(50),
    evidence_quality VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
18.4 competitor_listings
CREATE TABLE competitor_listings (
    id UUID PRIMARY KEY,
    product_id UUID NOT NULL REFERENCES products(id),
    marketplace VARCHAR(100),
    title TEXT,
    url TEXT,
    price NUMERIC(10,2),
    shipping_price NUMERIC(10,2),
    condition TEXT,
    seller_name TEXT,
    sold BOOLEAN DEFAULT FALSE,
    photo_score NUMERIC(5,2),
    title_score NUMERIC(5,2),
    description_score NUMERIC(5,2),
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
18.5 profit_analyses
CREATE TABLE profit_analyses (
    id UUID PRIMARY KEY,
    product_id UUID NOT NULL REFERENCES products(id),
    scenario_name VARCHAR(100),
    expected_sale_price NUMERIC(10,2),
    product_cost NUMERIC(10,2),
    import_shipping_per_unit NUMERIC(10,2),
    landed_cost NUMERIC(10,2),
    marketplace_fee NUMERIC(10,2),
    us_shipping NUMERIC(10,2),
    packaging_cost NUMERIC(10,2),
    return_allowance NUMERIC(10,2),
    ad_cost NUMERIC(10,2),
    estimated_net_profit NUMERIC(10,2),
    margin_percent NUMERIC(8,2),
    roi_percent NUMERIC(8,2),
    break_even_price NUMERIC(10,2),
    verdict VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
18.6 agent_reports
CREATE TABLE agent_reports (
    id UUID PRIMARY KEY,
    product_id UUID REFERENCES products(id),
    agent_name VARCHAR(100) NOT NULL,
    report_type VARCHAR(100),
    input_json JSONB,
    output_json JSONB,
    summary TEXT,
    confidence VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
18.7 inventory_items
CREATE TABLE inventory_items (
    id UUID PRIMARY KEY,
    product_id UUID NOT NULL REFERENCES products(id),
    quantity_on_hand INTEGER DEFAULT 0,
    quantity_ordered INTEGER DEFAULT 0,
    quantity_sold INTEGER DEFAULT 0,
    quantity_returned INTEGER DEFAULT 0,
    average_landed_cost NUMERIC(10,2),
    location_code VARCHAR(100),
    reorder_point INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
18.8 sales
CREATE TABLE sales (
    id UUID PRIMARY KEY,
    product_id UUID NOT NULL REFERENCES products(id),
    marketplace VARCHAR(100),
    sale_date DATE,
    quantity INTEGER,
    sale_price NUMERIC(10,2),
    marketplace_fee NUMERIC(10,2),
    shipping_cost NUMERIC(10,2),
    packaging_cost NUMERIC(10,2),
    net_profit NUMERIC(10,2),
    buyer_paid_shipping BOOLEAN DEFAULT FALSE,
    returned BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
18.9 product_files
CREATE TABLE product_files (
    id UUID PRIMARY KEY,
    product_id UUID NOT NULL REFERENCES products(id),
    file_type VARCHAR(100),
    file_url TEXT,
    original_filename TEXT,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
19. API Specification
19.1 Product APIs
Create Product
POST /api/products

Request:

{
  "name": "Car seat gap organizer",
  "category": "Car accessories",
  "description": "Organizer that fits between car seat and console"
}

Response:

{
  "id": "uuid",
  "sku": "CAR-SEAT-GAP-001",
  "status": "NEW"
}
Get Product
GET /api/products/{productId}
Update Product
PATCH /api/products/{productId}
List Products
GET /api/products?status=WATCHLIST&category=Car
19.2 Supplier APIs
POST /api/products/{productId}/sources
GET /api/products/{productId}/sources
PATCH /api/sources/{sourceId}
DELETE /api/sources/{sourceId}
19.3 Marketplace Research APIs
POST /api/products/{productId}/marketplace-research
GET /api/products/{productId}/marketplace-research
POST /api/products/{productId}/competitor-listings
GET /api/products/{productId}/competitor-listings
19.4 Profit APIs
POST /api/products/{productId}/profit-analysis
GET /api/products/{productId}/profit-analysis
19.5 Agent APIs
Run Risk Agent
POST /api/products/{productId}/agents/risk/run
Run Market Agent
POST /api/products/{productId}/agents/market/run
Run Profit Agent
POST /api/products/{productId}/agents/profit/run
Run Decision Agent
POST /api/products/{productId}/agents/decision/run
Run Full Research Pipeline
POST /api/products/{productId}/research/run

Response:

{
  "product_id": "uuid",
  "status": "RESEARCH_COMPLETE",
  "final_score": 78,
  "decision": "BUY_SAMPLE",
  "next_action": "Order 3-5 sample units"
}
19.6 Listing APIs
POST /api/products/{productId}/listings/generate
GET /api/products/{productId}/listings
PATCH /api/listings/{listingId}
19.7 Inventory APIs
GET /api/inventory
POST /api/products/{productId}/inventory
PATCH /api/inventory/{inventoryId}
19.8 Sales APIs
POST /api/products/{productId}/sales
GET /api/sales
GET /api/products/{productId}/sales
20. Agent Orchestration
20.1 Recommended MVP Orchestration

Use a deterministic backend service that calls agents in sequence.

ProductResearchService
   ├── RiskAgentService
   ├── MarketAgentService
   ├── ProfitAgentService
   ├── ListingAgentService
   └── DecisionAgentService

The system should not let agents randomly call each other.

The backend controls:

- Which agent runs
- In what order
- What data each agent receives
- Where results are stored
- Whether workflow stops
20.2 Full Research Pipeline Logic
function runResearchPipeline(productId):
    product = loadProduct(productId)

    riskReport = runRiskAgent(product)

    saveReport(riskReport)

    if riskReport.blocked:
        updateProductStatus(productId, "BLOCKED")
        return finalDecision("BLOCKED")

    marketReport = runMarketAgent(product)
    saveReport(marketReport)

    supplierReport = runSupplierAgent(product)
    saveReport(supplierReport)

    profitReport = runProfitAgent(product)
    saveReport(profitReport)

    competitionReport = runCompetitionAgent(product)
    saveReport(competitionReport)

    listingReport = runListingStrategyAgent(product)
    saveReport(listingReport)

    decisionReport = runDecisionAgent(
        riskReport,
        marketReport,
        supplierReport,
        profitReport,
        competitionReport,
        listingReport
    )

    saveReport(decisionReport)

    updateProductFinalDecision(productId, decisionReport)

    return decisionReport
21. Prompt Templates
21.1 Risk Agent Prompt
You are the Risk Agent for a U.S.-based reselling research system.

Your job is to determine whether a product is safe, legal, and appropriate to research further for online resale.

Strict rules:
- Block counterfeit, replica, fake, unauthorized branded, or trademark-infringing products.
- Block products that appear to use famous logos or brand names without authorization.
- Flag products with electrical, battery, medical, cosmetic, supplement, baby safety, automotive safety, hazardous, or food-contact risks.
- Do not recommend selling risky products.
- Separate evidence from assumptions.
- Return structured JSON only.

Product data:
{{PRODUCT_JSON}}

Return JSON:
{
  "risk_level": "LOW | MEDIUM | HIGH | BLOCKED",
  "blocked": true/false,
  "risk_categories": [],
  "red_flags": [],
  "evidence": [],
  "assumptions": [],
  "reasoning_summary": "",
  "recommended_action": ""
}
21.2 Market Research Agent Prompt
You are the Marketplace Research Agent for a U.S.-based online reselling business.

Your job is to analyze marketplace evidence and determine demand, pricing, and competition.

Rules:
- Do not invent prices or sold listings.
- If data is insufficient, say so.
- Separate active listing evidence from sold listing evidence.
- Estimate realistic selling price conservatively.
- Identify whether the product is saturated.
- Identify whether better photos, bundles, or descriptions could create an advantage.
- Return structured JSON only.

Product:
{{PRODUCT_JSON}}

Marketplace evidence:
{{MARKETPLACE_RESEARCH_JSON}}

Competitor listings:
{{COMPETITOR_LISTINGS_JSON}}

Return JSON:
{
  "demand_signal": "LOW | MEDIUM | HIGH",
  "competition_level": "LOW | MEDIUM | HIGH | SATURATED",
  "median_active_price": 0,
  "median_sold_price": 0,
  "realistic_sale_price": 0,
  "shipping_observations": "",
  "sell_through_signal": "",
  "evidence_quality": "LOW | MEDIUM | HIGH",
  "competitor_patterns": [],
  "market_risks": [],
  "summary": "",
  "recommendation": ""
}
21.3 Profit Agent Prompt
You are the Profit Agent for a small-batch reselling business.

Your job is to calculate realistic expected profit.

Rules:
- Include product cost, import shipping, marketplace fee, U.S. shipping, packaging, return allowance, and ad cost if provided.
- If a value is missing, use conservative assumptions and list them.
- Calculate break-even price.
- Calculate margin and ROI.
- Return structured JSON only.

Product:
{{PRODUCT_JSON}}

Cost data:
{{COST_JSON}}

Market data:
{{MARKET_JSON}}

Return JSON:
{
  "expected_sale_price": 0,
  "product_cost": 0,
  "import_shipping_per_unit": 0,
  "landed_cost": 0,
  "marketplace_fee": 0,
  "us_shipping": 0,
  "packaging_cost": 0,
  "return_allowance": 0,
  "ad_cost": 0,
  "estimated_net_profit": 0,
  "margin_percent": 0,
  "roi_percent": 0,
  "break_even_price": 0,
  "minimum_recommended_price": 0,
  "profit_verdict": "BAD | WEAK | ACCEPTABLE | GOOD | STRONG",
  "assumptions": [],
  "notes": ""
}
21.4 Decision Agent Prompt
You are the Decision Agent for a U.S.-based reselling research platform.

Your job is to combine all research reports and produce a final business decision.

Rules:
- If Risk Agent says BLOCKED, final decision must be BLOCKED.
- Do not recommend bulk buying without sales evidence.
- If profit is weak, do not recommend buying unless bundle strategy can fix it.
- If market data is insufficient, use WATCHLIST, not BUY.
- Prefer small sample orders for unproven products.
- Return structured JSON only.

Inputs:
Risk report:
{{RISK_REPORT}}

Market report:
{{MARKET_REPORT}}

Supplier report:
{{SUPPLIER_REPORT}}

Profit report:
{{PROFIT_REPORT}}

Competition report:
{{COMPETITION_REPORT}}

Listing report:
{{LISTING_REPORT}}

Return JSON:
{
  "scores": {
    "demand": 0,
    "profit": 0,
    "risk": 0,
    "competition": 0,
    "shipping": 0,
    "listing_gap": 0,
    "supplier_confidence": 0
  },
  "final_score": 0,
  "decision": "BLOCKED | SKIP | WATCHLIST | BUY_SAMPLE | BUY_SMALL_BATCH | REORDER | SCALE",
  "confidence": "LOW | MEDIUM | HIGH",
  "reason": "",
  "next_action": "",
  "max_quantity_to_buy": 0,
  "max_landed_cost": 0,
  "target_sale_price": 0,
  "open_questions": [],
  "warnings": []
}
22. Recommended Technical Architecture
22.1 MVP Stack Option

Because you are technical, I recommend:

Frontend: Next.js or React
Backend: Python FastAPI
Database: PostgreSQL
Background jobs: Celery or RQ
LLM Provider: OpenAI API first, Ollama optional
File storage: local storage first, S3/Supabase later
Browser automation: Playwright later
Authentication: simple local auth or Supabase Auth

Alternative if you want ultra-fast MVP:

Frontend: Streamlit
Backend: Python services
Database: SQLite/PostgreSQL
LLM: OpenAI/Ollama

Since this may become a serious internal tool, I prefer:

Next.js + FastAPI + PostgreSQL
22.2 Architecture Diagram
┌──────────────────────────────────────────────────────────────┐
│                         Frontend                              │
│                  Next.js / React Dashboard                    │
│                                                              │
│  Dashboard | Products | Research | Profit | Listings | Sales  │
└───────────────────────────────┬──────────────────────────────┘
                                │
                                v
┌──────────────────────────────────────────────────────────────┐
│                         Backend API                           │
│                         FastAPI                               │
│                                                              │
│ Product API | Research API | Agent API | Sales API | Files API│
└───────────────────────────────┬──────────────────────────────┘
                                │
              ┌─────────────────┼──────────────────┐
              v                 v                  v
┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐
│ PostgreSQL         │ │ Agent Orchestrator │ │ File Storage       │
│ Products/Sales     │ │ Runs AI Agents     │ │ Images/Screenshots │
└───────────────────┘ └─────────┬─────────┘ └───────────────────┘
                                │
                                v
                    ┌─────────────────────┐
                    │ LLM Provider Layer   │
                    │ OpenAI / Ollama      │
                    └─────────────────────┘
23. Backend Service Design
23.1 Services
ProductService
SupplierService
MarketplaceResearchService
CompetitorListingService
ProfitAnalysisService
AgentReportService
ResearchPipelineService
ListingGenerationService
InventoryService
SalesService
ReorderService
FileService
23.2 Agent Services
RiskAgent
MarketResearchAgent
SupplierAgent
ProfitAgent
CompetitionAgent
ListingAgent
DecisionAgent
ReorderAgent

Each agent should follow the same interface:

class Agent:
    def run(self, input_data: dict) -> AgentResult:
        pass

AgentResult:

class AgentResult:
    agent_name: str
    output_json: dict
    summary: str
    confidence: str
    warnings: list[str]
24. Frontend Component Design
24.1 Main Components
DashboardPage
ProductListPage
ProductDetailPage
ProductOverviewTab
SupplierTab
MarketplaceResearchTab
ProfitAnalysisTab
CompetitionTab
AgentReportsTab
ListingBuilderPage
InventoryPage
SalesPage
ReorderPage
SettingsPage
24.2 Reusable Components
StatusBadge
RiskBadge
DecisionBadge
ScoreCard
ProfitCard
AgentReportCard
CompetitorListingCard
SupplierCard
EvidenceUploader
ProfitCalculator
ProductScoreBreakdown
ResearchTimeline
ActionButtonBar
25. MVP User Stories
Product Intake
As a user, I want to create a product idea so that I can research whether it is worth buying.

Acceptance criteria:

- User can enter name, category, description, supplier URL, and cost.
- System creates product with NEW status.
- System generates SKU.
Risk Analysis
As a user, I want the system to flag risky products so that I do not import or sell problematic items.

Acceptance criteria:

- User can run Risk Agent.
- System returns LOW/MEDIUM/HIGH/BLOCKED.
- BLOCKED products cannot move to BUY_SAMPLE.
- Risk report is stored.
Marketplace Research
As a user, I want to enter active and sold listing data so that the AI can analyze demand.

Acceptance criteria:

- User can add marketplace research.
- User can enter price ranges and listing counts.
- User can paste competitor listing data.
- AI summarizes demand and competition.
Profit Analysis
As a user, I want the system to calculate real profit so that I know if a product is worth buying.

Acceptance criteria:

- User can enter cost values.
- System calculates landed cost.
- System calculates net profit.
- System calculates margin and break-even price.
Final Decision
As a user, I want the system to give a final recommendation so that I can decide what to do next.

Acceptance criteria:

- System combines risk, market, profit, supplier, and competition analysis.
- System gives final score.
- System gives final decision.
- System gives next action.
Listing Generation
As a user, I want the system to generate marketplace listings so that I can sell faster.

Acceptance criteria:

- System generates eBay title under 80 characters.
- System generates description and bullet points.
- System generates photo checklist.
- System avoids risky trademark claims.
Sales Tracking
As a user, I want to record sales so that I can know actual profit.

Acceptance criteria:

- User can record sale price, fees, shipping, and packaging.
- System calculates actual net profit.
- Inventory decreases after sale.
Reorder Recommendation
As a user, I want the system to recommend whether to reorder so that I scale only winners.

Acceptance criteria:

- System reviews sales velocity.
- System reviews profit.
- System reviews returns.
- System recommends reorder or kill.
26. MVP Roadmap
Phase 1: Foundation

Build:

- Product CRUD
- Supplier CRUD
- Marketplace research manual entry
- Profit calculator
- Basic dashboard
- PostgreSQL schema

Deliverable:

User can create product ideas and manually calculate profit.
Phase 2: AI Reports

Build:

- Risk Agent
- Market Agent
- Profit Agent
- Decision Agent
- Agent report storage

Deliverable:

User can run AI research pipeline and get buy/skip/watchlist/block decision.
Phase 3: Listing Builder

Build:

- Listing generation
- Photo checklist
- Marketplace-specific templates
- Copy/save listing content

Deliverable:

User can create optimized listings from approved products.
Phase 4: Inventory and Sales

Build:

- Inventory tracking
- Sales tracking
- Actual profit calculation
- Reorder Agent

Deliverable:

User can track performance and receive reorder recommendations.
Phase 5: Browser-Assisted Research

Build:

- Playwright-assisted search workflow
- User-driven evidence capture
- Screenshot upload and parsing
- Competitor listing extraction where allowed

Deliverable:

User can speed up marketplace research without relying only on manual typing.
27. MVP Build Order

Recommended exact build sequence:

1. Create database schema.
2. Build product list and product detail pages.
3. Build supplier input.
4. Build marketplace research input.
5. Build profit calculator.
6. Build agent report table.
7. Implement Risk Agent.
8. Implement Profit Agent.
9. Implement Market Agent.
10. Implement Decision Agent.
11. Build product score UI.
12. Build listing generator.
13. Build inventory tracker.
14. Build sales tracker.
15. Build reorder recommendation.
28. Example Product Research Report

The system should generate a report like this:

Product: 2-Pack Car Seat Gap Organizer
Category: Car Accessories
Status: BUY_SAMPLE
Final Score: 79/100

Risk:
LOW
No trademark, battery, medical, or safety risk detected. Product is generic.

Market:
Demand appears medium-high based on sold listing evidence. Median sold price estimated at $17.99.

Competition:
Competition is medium. Many sellers use factory photos and weak descriptions.

Profit:
Estimated sale price: $18.99
Estimated landed cost: $5.80
Marketplace fee: $2.70
Packaging: $0.50
U.S. shipping: $4.20
Estimated net profit: $5.79

Listing Opportunity:
Use real car installation photos, show dimensions, and sell as a 2-pack.

Decision:
BUY_SAMPLE

Next Action:
Order 3–5 units. Do not bulk buy until sample quality is verified.
29. Settings

The app should include configurable settings.

Business Settings
Default marketplace fee %
Default packaging cost
Default return allowance
Minimum acceptable profit
Minimum acceptable margin
Maximum sample quantity
Default currency
Risk Settings
Blocked keywords
Restricted categories
Manual override allowed?
High-risk category warnings
Agent Settings
LLM provider
Model
Temperature
Max tokens
Run agents automatically?
Require approval before final status change?
Marketplace Settings
eBay fee estimate
Mercari fee estimate
Facebook fee estimate
Shipping presets
30. Security and Safety
Authentication

MVP can support simple user login.

Future:

Email/password
OAuth
Role-based permissions
Data Protection
- Store API keys encrypted.
- Do not expose LLM API keys to frontend.
- Validate uploaded files.
- Log AI decisions.
- Keep agent outputs auditable.
AI Safety Rules
- Agents must not recommend illegal/counterfeit resale.
- Agents must not invent market data.
- Agents must show assumptions.
- Agents must preserve evidence.
- Agents must produce structured outputs.
31. Browser Automation Policy

The system should support browser-assisted research carefully.

Recommended approach:

- User initiates marketplace search.
- Browser opens search page.
- User manually applies filters if needed.
- System helps capture visible listing data or screenshots.
- System analyzes user-provided evidence.

Avoid:

- Aggressive scraping
- Bypassing anti-bot systems
- Login circumvention
- Collecting private user data
- Violating marketplace terms
32. Success Metrics

The app is successful if it helps the user:

- Reduce bad purchases
- Avoid risky products
- Improve profit estimates
- Find products with real demand
- Create better listings
- Track actual profit
- Reorder winners
- Kill losers faster

Business KPIs:

Products researched per week
Products blocked before purchase
Samples ordered
Products listed
Sell-through rate
Average net profit per sale
Return rate
Reorder success rate
Inventory aging
Actual profit vs estimated profit
33. Definition of Done for MVP

MVP is complete when:

1. User can create a product idea.
2. User can add supplier data.
3. User can add marketplace research manually.
4. Risk Agent can analyze the product.
5. Profit Agent can calculate profitability.
6. Market Agent can summarize demand and competition.
7. Decision Agent can produce final score and recommendation.
8. User can generate listing content.
9. User can record sales.
10. User can see reorder recommendation.
11. All agent outputs are saved.
12. Dashboard shows product pipeline and opportunities.
34. Suggested Folder Structure

For a Next.js + FastAPI build:

resellos/
  frontend/
    app/
      dashboard/
      products/
      listings/
      inventory/
      sales/
      settings/
    components/
      product/
      agents/
      dashboard/
      forms/
      shared/
    lib/
      api.ts
      types.ts

  backend/
    app/
      main.py
      config.py
      db.py
      models/
        product.py
        supplier.py
        marketplace.py
        profit.py
        agent_report.py
        inventory.py
        sale.py
      schemas/
        product_schema.py
        supplier_schema.py
        marketplace_schema.py
        profit_schema.py
        agent_schema.py
      services/
        product_service.py
        supplier_service.py
        marketplace_service.py
        profit_service.py
        research_pipeline_service.py
      agents/
        base_agent.py
        risk_agent.py
        market_agent.py
        supplier_agent.py
        profit_agent.py
        competition_agent.py
        listing_agent.py
        decision_agent.py
        reorder_agent.py
      routes/
        products.py
        suppliers.py
        marketplace.py
        profit.py
        agents.py
        inventory.py
        sales.py
      prompts/
        risk_agent.txt
        market_agent.txt
        profit_agent.txt
        decision_agent.txt
      migrations/
      tests/

  docs/
    SRS.md
    API.md
    AGENTS.md
    SCORING.md
35. Recommended Initial MVP Features Only

To avoid overbuilding, build this first:

1. Product list
2. Product detail
3. Supplier section
4. Marketplace research section
5. Profit calculator
6. Risk Agent
7. Market Agent
8. Profit Agent
9. Decision Agent
10. Listing generator

Do not start with:

- Full marketplace scraping
- Shopify publishing
- Amazon integration
- Automatic purchasing
- Complex inventory forecasting
- Multi-user permissions
- Full accounting

Those come later.

36. Killer MVP Prompt for Your Coding Agent

Use this to ask an AI coding agent to build the first version:

You are a senior full-stack engineer. Build an MVP called ResellOS.

ResellOS is an AI-powered product research and reselling intelligence tool for a solo U.S.-based online reseller.

The MVP must allow the user to:
1. Create product ideas.
2. Add supplier data.
3. Add manual marketplace research.
4. Calculate profitability.
5. Run AI agents:
   - Risk Agent
   - Market Research Agent
   - Profit Agent
   - Decision Agent
6. Store all agent reports.
7. Generate a final product score from 0–100.
8. Recommend BLOCKED, SKIP, WATCHLIST, BUY_SAMPLE, or BUY_SMALL_BATCH.
9. Generate listing content for eBay, Mercari, and Facebook Marketplace.
10. Track basic inventory and sales.

Use:
- Frontend: Next.js + TypeScript
- Backend: FastAPI + Python
- Database: PostgreSQL
- ORM: SQLAlchemy
- Styling: Tailwind
- LLM provider abstraction so OpenAI or Ollama can be used later

Important rules:
- The system must block counterfeit, replica, unauthorized branded, unsafe, or restricted products.
- The system must not invent marketplace data.
- The user must be able to manually enter marketplace evidence.
- AI agent outputs must be stored as JSON.
- Final decisions must be evidence-based.
- Do not implement marketplace scraping in MVP.
- Build clean service boundaries.

Create:
1. Database models
2. API routes
3. Agent service abstraction
4. Prompt templates
5. Product dashboard
6. Product detail page with tabs
7. Profit calculator
8. Agent report viewer
9. Listing generator
10. Basic tests

Use this scoring:
Demand 0–20
Profit 0–20
Risk 0–20
Competition 0–15
Shipping 0–10
Listing gap 0–10
Supplier confidence 0–5

Decision rules:
- If risk is BLOCKED, final decision is BLOCKED.
- 85–100: BUY_SMALL_BATCH or BUY_SAMPLE
- 70–84: BUY_SAMPLE
- 55–69: WATCHLIST
- Below 55: SKIP
- Never recommend bulk buying without sales evidence.

Return a complete implementation plan first, then build incrementally.
37. Final Recommended MVP Product Shape

The first useful version should be simple:

A product research dashboard where you enter a product idea, supplier cost, and marketplace notes, then AI gives you a disciplined buy/skip decision with profit math and listing suggestions.

That is enough to start making better buying decisions immediately.

The system becomes powerful when you add sales feedback:

The AI does not just tell you what might sell.
It learns from what actually sold.

That is the difference between a toy agent and a real business tool.