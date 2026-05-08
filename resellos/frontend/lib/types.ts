export type ProductStatus =
  | 'NEW'
  | 'NEEDS_RESEARCH'
  | 'RESEARCHING'
  | 'BLOCKED'
  | 'WATCHLIST'
  | 'BUY_SAMPLE'
  | 'BUY_SMALL_BATCH'
  | 'SAMPLE_ORDERED'
  | 'SAMPLE_RECEIVED'
  | 'APPROVED_TO_LIST'
  | 'LISTED'
  | 'SELLING'
  | 'SLOW_MOVING'
  | 'REORDER_CANDIDATE'
  | 'REORDERED'
  | 'KILL_PRODUCT'
  | 'ARCHIVED';

export const STATUS_LABELS: Record<ProductStatus, string> = {
  NEW: 'New',
  NEEDS_RESEARCH: 'Needs Research',
  RESEARCHING: 'Researching',
  BLOCKED: 'Blocked',
  WATCHLIST: 'Watchlist',
  BUY_SAMPLE: 'Buy Sample',
  BUY_SMALL_BATCH: 'Buy Small Batch',
  SAMPLE_ORDERED: 'Sample Ordered',
  SAMPLE_RECEIVED: 'Sample Received',
  APPROVED_TO_LIST: 'Approved to List',
  LISTED: 'Listed',
  SELLING: 'Selling',
  SLOW_MOVING: 'Slow Moving',
  REORDER_CANDIDATE: 'Reorder Candidate',
  REORDERED: 'Reordered',
  KILL_PRODUCT: 'Kill Product',
  ARCHIVED: 'Archived',
};

export const STATUS_COLORS: Record<ProductStatus, string> = {
  NEW: 'bg-slate-500/20 text-slate-400 border-slate-500/30',
  NEEDS_RESEARCH: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  RESEARCHING: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  BLOCKED: 'bg-red-500/20 text-red-400 border-red-500/30',
  WATCHLIST: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  BUY_SAMPLE: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
  BUY_SMALL_BATCH: 'bg-fuchsia-500/20 text-fuchsia-400 border-fuchsia-500/30',
  SAMPLE_ORDERED: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
  SAMPLE_RECEIVED: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
  APPROVED_TO_LIST: 'bg-green-500/20 text-green-400 border-green-500/30',
  LISTED: 'bg-green-500/20 text-green-400 border-green-500/30',
  SELLING: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  SLOW_MOVING: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  REORDER_CANDIDATE: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
  REORDERED: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
  KILL_PRODUCT: 'bg-red-500/20 text-red-400 border-red-500/30',
  ARCHIVED: 'bg-slate-500/20 text-slate-400 border-slate-500/30',
};

export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'BLOCKED';

export const RISK_COLORS: Record<RiskLevel, string> = {
  LOW: 'bg-green-500/20 text-green-400 border-green-500/30',
  MEDIUM: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  HIGH: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  BLOCKED: 'bg-red-500/20 text-red-400 border-red-500/30',
};

export type VerificationStatus =
  | 'TEST_DATA'
  | 'AI_EXTRACTED_UNVERIFIED'
  | 'USER_CAPTURED_UNVERIFIED'
  | 'USER_VERIFIED'
  | 'API_IMPORTED'
  | 'REJECTED';

export const VERIFICATION_LABELS: Record<VerificationStatus, string> = {
  TEST_DATA: 'Test Data',
  AI_EXTRACTED_UNVERIFIED: 'AI Extracted',
  USER_CAPTURED_UNVERIFIED: 'User Captured',
  USER_VERIFIED: 'Verified',
  API_IMPORTED: 'API Import',
  REJECTED: 'Rejected',
};

export const VERIFICATION_COLORS: Record<VerificationStatus, string> = {
  TEST_DATA: 'bg-red-500/20 text-red-400 border-red-500/30',
  AI_EXTRACTED_UNVERIFIED: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  USER_CAPTURED_UNVERIFIED: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  USER_VERIFIED: 'bg-green-500/20 text-green-400 border-green-500/30',
  API_IMPORTED: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  REJECTED: 'bg-red-500/20 text-red-400 border-red-500/30',
};

export type FinalDecision =
  | 'BLOCKED'
  | 'SKIP'
  | 'WATCHLIST'
  | 'BUY_SAMPLE'
  | 'BUY_SMALL_BATCH'
  | 'REORDER'
  | 'SCALE';

export type ScoutStatusKnown = 'SHORTLIST' | 'WATCH' | 'REJECT' | 'NEEDS_SOLD_PROOF';
export type ScoutStatus = ScoutStatusKnown | string;
export type ScoutConfidenceKnown = 'LOW' | 'MEDIUM' | 'HIGH';
export type ScoutConfidence = ScoutConfidenceKnown | string;

export const SCOUT_STATUS_LABELS: Record<ScoutStatusKnown, string> = {
  SHORTLIST: 'Shortlist',
  WATCH: 'Watch',
  REJECT: 'Reject',
  NEEDS_SOLD_PROOF: 'Needs Sold Proof',
};

export const SCOUT_STATUS_COLORS: Record<ScoutStatusKnown, string> = {
  SHORTLIST: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
  WATCH: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
  REJECT: 'bg-red-500/20 text-red-300 border-red-500/30',
  NEEDS_SOLD_PROOF: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
};

export interface Product {
  id: string;
  sku: string;
  name: string;
  shop_concept_id?: string | null;
  collection_id?: string | null;
  category?: string;
  subcategory?: string;
  description?: string;
  status: ProductStatus;
  risk_level?: RiskLevel;
  final_score?: number;
  final_decision?: FinalDecision;
  target_sale_price?: number;
  expected_profit?: number;
  target_cost?: number;
  confidence?: 'LOW' | 'MEDIUM' | 'HIGH';
  next_action?: string;
  decision_reason?: string;
  missing_evidence?: string[];
  created_at: string;
  updated_at: string;
  sources?: ProductSource[];
  marketplace_research?: MarketplaceResearch[];
  marketplace_evidence?: MarketplaceEvidence[];
  competitor_listings?: CompetitorListing[];
  profit_analyses?: ProfitAnalysis[];
  agent_reports?: AgentReport[];
  inventory?: InventoryItem[];
  sales?: Sale[];
  files?: ProductFile[];
}

export interface ProductSource {
  id: string;
  product_id: string;
  supplier_name?: string;
  supplier_platform?: string;
  supplier_url?: string;
  unit_cost?: number;
  domestic_shipping?: number;
  international_shipping_estimate?: number;
  estimated_landed_cost?: number;
  moq?: number;
  supplier_rating?: string;
  is_primary?: boolean;
  verification_status?: string;
}

export interface MarketplaceResearch {
  id: string;
  product_id: string;
  marketplace: string;
  keyword?: string;
  active_listing_count?: number;
  sold_listing_count?: number;
  median_active_price?: number;
  median_sold_price?: number;
  competition_level?: string;
  demand_signal?: string;
}

export interface MarketplaceEvidence {
  id: string;
  product_id: string;
  marketplace: string;
  evidence_type: 'ACTIVE_LISTING' | 'SOLD_LISTING' | 'SCREENSHOT' | 'MANUAL_NOTE' | string;
  title?: string;
  url?: string;
  price?: number;
  shipping_price?: number;
  sold_date?: string;
  condition?: string;
  seller_name?: string;
  source_method?: string;
  verification_status?: string;
  raw_text?: string;
  screenshot_url?: string;
  confidence?: string;
  notes?: string;
}

export interface MarketplaceEvidenceInput {
  marketplace: string;
  evidence_type: 'ACTIVE_LISTING' | 'SOLD_LISTING' | 'SCREENSHOT' | 'MANUAL_NOTE' | string;
  title?: string;
  url?: string;
  price?: number;
  shipping_price?: number;
  sold_date?: string;
  condition?: string;
  seller_name?: string;
  source_method?: string;
  verification_status?: string;
  raw_text?: string;
  screenshot_url?: string;
  confidence?: string;
  notes?: string;
}

export interface SupplierInput {
  supplier_name?: string;
  supplier_platform?: string;
  supplier_url?: string;
  unit_cost?: number;
  domestic_shipping?: number;
  international_shipping_estimate?: number;
  estimated_landed_cost?: number;
  moq?: number;
  supplier_rating?: string;
  notes?: string;
  is_primary?: boolean;
}

export interface CompetitorListing {
  id: string;
  product_id: string;
  marketplace?: string;
  title?: string;
  url?: string;
  price?: number;
  shipping_price?: number;
  condition?: string;
  seller_name?: string;
  sold?: boolean;
  photo_score?: number;
  verification_status?: string;
  title_patterns?: string[];
  weaknesses?: string[];
  differentiation_ideas?: string[];
}

export interface ProfitAnalysis {
  id: string;
  product_id: string;
  scenario_name?: string;
  expected_sale_price?: number;
  landed_cost?: number;
  selling_cost?: number;
  marketplace_fee?: number;
  estimated_net_profit?: number;
  margin_percent?: number;
  roi_percent?: number;
  break_even_price?: number;
  minimum_recommended_price?: number;
  target_sale_price?: number;
  verdict?: string;
}

export interface ValidationCheck {
  status: 'PASS' | 'FAIL' | 'WARNING' | 'UNKNOWN';
  score: number;
  summary: string;
  next_action?: string | null;
}

export interface ProductDemandResearch {
  id: string;
  product_id?: string | null;
  idea_id?: string | null;
  campaign_id?: string | null;
  task_id?: string | null;
  keyword: string;
  source: string;
  target_country: string;
  target_language: string;
  monthly_search_volume?: number | null;
  monthly_search_volume_min?: number | null;
  monthly_search_volume_max?: number | null;
  competition_level?: string | null;
  cpc_low?: number | null;
  cpc_high?: number | null;
  currency: string;
  buyer_intent_score: number;
  keyword_specificity_score: number;
  demand_score: number;
  related_keywords: Array<Record<string, unknown>>;
  raw_json: Record<string, unknown>;
  verification_status: string;
  source_url?: string | null;
  screenshot_url?: string | null;
  verification_notes?: string | null;
  created_by?: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProductDemandResearchInput {
  product_id?: string | null;
  idea_id?: string | null;
  campaign_id?: string | null;
  task_id?: string | null;
  keyword: string;
  source?: string;
  target_country?: string;
  target_language?: string;
  monthly_search_volume?: number | null;
  monthly_search_volume_min?: number | null;
  monthly_search_volume_max?: number | null;
  competition_level?: string | null;
  cpc_low?: number | null;
  cpc_high?: number | null;
  currency?: string;
  buyer_intent_score?: number;
  keyword_specificity_score?: number;
  demand_score?: number;
  related_keywords?: Array<Record<string, unknown>>;
  raw_json?: Record<string, unknown>;
  verification_status?: string;
  source_url?: string | null;
  screenshot_url?: string | null;
  verification_notes?: string | null;
  created_by?: string | null;
}

export interface ProductDemandResearchVerifyInput {
  verification_status: 'USER_VERIFIED' | 'USER_CAPTURED_UNVERIFIED';
  source_url?: string | null;
  screenshot_url?: string | null;
  verification_notes?: string | null;
  confirm?: boolean | null;
}

export interface ProductTrendResearch {
  id: string;
  product_id?: string | null;
  idea_id?: string | null;
  campaign_id?: string | null;
  task_id?: string | null;
  keyword: string;
  source: string;
  geo: string;
  timeframe: string;
  trend_direction?: string | null;
  seasonality_risk?: string | null;
  evergreen_score: number;
  trend_stability_score: number;
  spike_risk_score: number;
  average_interest?: number | null;
  peak_interest?: number | null;
  low_interest?: number | null;
  trend_points: Array<Record<string, unknown>>;
  raw_json: Record<string, unknown>;
  verification_status: string;
  source_url?: string | null;
  screenshot_url?: string | null;
  verification_notes?: string | null;
  created_by?: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProductTrendResearchInput {
  product_id?: string | null;
  idea_id?: string | null;
  campaign_id?: string | null;
  task_id?: string | null;
  keyword: string;
  source?: string;
  geo?: string;
  timeframe?: string;
  trend_direction?: string | null;
  seasonality_risk?: string | null;
  evergreen_score?: number;
  trend_stability_score?: number;
  spike_risk_score?: number;
  average_interest?: number | null;
  peak_interest?: number | null;
  low_interest?: number | null;
  trend_points?: Array<Record<string, unknown>>;
  raw_json?: Record<string, unknown>;
  verification_status?: string;
  source_url?: string | null;
  screenshot_url?: string | null;
  verification_notes?: string | null;
  created_by?: string | null;
}

export interface ProductTrendResearchVerifyInput {
  verification_status: 'USER_VERIFIED' | 'USER_CAPTURED_UNVERIFIED';
  source_url?: string | null;
  screenshot_url?: string | null;
  verification_notes?: string | null;
  confirm?: boolean | null;
}

export interface ProductValidationSummary {
  id: string;
  product_id: string;
  market_presence_status?: string | null;
  search_demand_status?: string | null;
  sold_demand_status?: string | null;
  trend_status?: string | null;
  supplier_economics_status?: string | null;
  competition_status?: string | null;
  risk_status?: string | null;
  market_presence_score: number;
  search_demand_score: number;
  sold_demand_score: number;
  trend_score: number;
  supplier_economics_score: number;
  competition_score: number;
  risk_score: number;
  overall_validation_score: number;
  validation_readiness: 'INCOMPLETE' | 'WEAK' | 'WATCHLIST' | 'READY_FOR_SAMPLE';
  main_validation_blocker?: string | null;
  next_validation_action?: string | null;
  created_at: string;
  updated_at: string;
}

export interface ValidationChecklistResponse {
  product_id: string;
  market_presence: ValidationCheck;
  search_demand: ValidationCheck;
  sold_demand: ValidationCheck;
  trend_stability: ValidationCheck;
  supplier_economics: ValidationCheck;
  competition_gap: ValidationCheck;
  risk: ValidationCheck;
  final_readiness: 'INCOMPLETE' | 'WEAK' | 'WATCHLIST' | 'READY_FOR_SAMPLE';
  main_blocker?: string | null;
  next_action?: string | null;
  overall_validation_score: number;
}

export interface DecisionSummary {
  recommendation?: FinalDecision;
  research_verdict?: 'REJECT' | 'WEAK_IDEA' | 'NEEDS_MORE_RESEARCH' | 'PROMISING_RESEARCH' | 'READY_FOR_SAMPLE';
  buy_readiness?: 'NOT_READY' | 'READY';
  buy_readiness_status?: 'NOT_READY' | 'ALMOST_READY' | 'READY';
  research_completeness_score?: number;
  opportunity_score?: number;
  main_blocker?: string;
  total_score?: number;
  confidence?: 'LOW' | 'MEDIUM' | 'HIGH';
  reason?: string;
  next_action?: string;
  missing_evidence?: string[];
  assumptions?: string[];
  hard_blockers?: string[];
  max_quantity_to_buy?: number;
  max_landed_cost?: number;
  target_sale_price?: number;
  current_net_profit?: number;
  target_net_profit_threshold?: number;
  profit_gap_to_buy_sample?: number;
  current_landed_cost?: number;
  max_landed_cost_for_target_profit?: number;
  max_landed_cost_for_target_profit_raw?: number;
  target_profit_feasible?: boolean;
  current_target_sale_price?: number;
  required_sale_price_for_target_profit?: number;
  required_before_buying?: string[];
  blocked?: boolean;
  verified_sold_listing_count?: number;
  verified_active_listing_count?: number;
  test_data_evidence_count?: number;
}

export interface CompetitionInsight {
  competition_level?: 'LOW' | 'MEDIUM' | 'HIGH' | 'UNKNOWN';
  listing_gap_score?: number;
  can_compete?: boolean;
  competitor_count?: number;
  active_competitor_count?: number;
  sold_competitor_count?: number;
  median_competitor_price?: number | null;
  avg_photo_score?: number | null;
  avg_title_score?: number | null;
  avg_description_score?: number | null;
  weaknesses?: string[];
  recommended_angle?: string;
  summary?: string;
  confidence?: 'LOW' | 'MEDIUM' | 'HIGH';
  warnings?: string[];
  evidence_refs?: string[];
}

export interface ReorderInsight {
  reorder_recommendation?: 'DO_NOT_REORDER' | 'REORDER_SMALL' | 'REORDER_MEDIUM' | 'SCALE' | 'KILL_PRODUCT';
  current_inventory?: number;
  quantity_sold?: number;
  quantity_ordered?: number;
  quantity_returned?: number;
  average_daily_sales?: number;
  days_of_cover?: number | null;
  reorder_point?: number;
  max_reorder_qty?: number;
  stockout_risk?: 'LOW' | 'MEDIUM' | 'HIGH';
  return_rate_percent?: number;
  average_landed_cost?: number | null;
  reorder_reason?: string;
  summary?: string;
  confidence?: 'LOW' | 'MEDIUM' | 'HIGH';
  warnings?: string[];
  evidence_refs?: string[];
}

export interface AgentReport {
  id: string;
  product_id: string;
  agent_name: string;
  report_type: string;
  input_json?: string;
  output_json?: string;
  summary?: string;
  confidence?: string;
  warnings?: string[];
  evidence_refs?: string[];
  created_at: string;
}

export interface AgentResult {
  agent_name?: string;
  agent_type?: string;
  status?: 'pending' | 'running' | 'completed' | 'failed';
  output_json?: Record<string, unknown>;
  summary?: string;
  confidence?: string;
  warnings?: string[];
  evidence_refs?: string[];
  errors?: string[];
  started_at?: string;
  completed_at?: string;
  duration_seconds?: number;
}

export interface ResearchCockpit {
  product: Product;
  portfolio_context?: PortfolioContext | null;
  sources: ProductSource[];
  marketplace_research: Array<Record<string, unknown>>;
  marketplace_evidence: MarketplaceEvidence[];
  competitor_listings: CompetitorListing[];
  profit_analyses: ProfitAnalysis[];
  agent_reports: AgentReport[];
  decision?: DecisionSummary | null;
  competition?: CompetitionInsight | null;
  reorder?: ReorderInsight | null;
  buy_readiness?: Record<string, unknown>;
  hard_blockers?: string[];
  inventory?: Array<Record<string, unknown>>;
  sales?: Array<Record<string, unknown>>;
  missing_evidence: string[];
  next_action?: string | null;
  confidence?: string | null;
  current_status?: string | null;
  discovery_context?: {
    idea_id?: string;
    idea_name?: string;
    category?: string;
    quick_scan_verdict?: string;
    quick_scan_reason?: string;
    scout_status?: ScoutStatus | null;
    scout_score?: number | null;
    scout_confidence?: ScoutConfidence | null;
    scout_reason?: string | null;
    scout_next_step?: string | null;
    scout_metrics?: Record<string, unknown> | null;
    research_priority?: string;
    research_completeness_score?: number;
    opportunity_score?: number;
    required_next_evidence?: string[] | string | null;
    suggested_keywords?: Record<string, string[]> | string[] | string | null;
    risk_flags?: string[] | string | null;
  } | null;
}

export interface PortfolioContext {
  shop_concept?: ShopConcept | null;
  collection?: ProductCollection | null;
  portfolio_items?: PortfolioItem[];
}

export interface DiscoveryTask {
  id: string;
  idea_id: string;
  task_type: string;
  title: string;
  status: 'TODO' | 'DONE' | 'SKIPPED' | 'BLOCKED' | string;
  notes?: string;
  sort_order: number;
  linked_evidence_id?: string | null;
  linked_source_id?: string | null;
  linked_competitor_id?: string | null;
  linked_product_id?: string | null;
  created_at: string;
}

export interface DiscoveryCampaign {
  id: string;
  name: string;
  shop_concept_id?: string | null;
  collection_id?: string | null;
  category?: string;
  goal?: string;
  constraints_json?: Record<string, unknown>;
  budget_limit_usd?: number;
  max_ideas?: number;
  max_products_to_promote?: number;
  status: 'DRAFT' | 'RUNNING' | 'PAUSED' | 'COMPLETED' | string;
  created_by?: string;
  shop_concept_name?: string | null;
  collection_name?: string | null;
  report_generated_at?: string | null;
  created_at: string;
  updated_at: string;
  idea_count?: number;
  rejected_idea_count?: number;
  promising_idea_count?: number;
  promoted_product_count?: number;
  dataforseo_spend_estimate?: number;
}

export interface DiscoveryCampaignInput {
  name: string;
  shop_concept_id?: string | null;
  collection_id?: string | null;
  category?: string;
  goal?: string;
  constraints_json?: Record<string, unknown>;
  budget_limit_usd?: number;
  max_ideas?: number;
  max_products_to_promote?: number;
  status?: 'DRAFT' | 'RUNNING' | 'PAUSED' | 'COMPLETED' | string;
  created_by?: string;
}

export interface DiscoveryCampaignUpdateInput {
  name?: string;
  shop_concept_id?: string | null;
  collection_id?: string | null;
  category?: string;
  goal?: string;
  constraints_json?: Record<string, unknown>;
  budget_limit_usd?: number;
  max_ideas?: number;
  max_products_to_promote?: number;
  status?: 'DRAFT' | 'RUNNING' | 'PAUSED' | 'COMPLETED' | string;
  created_by?: string;
}

export interface DiscoveryCampaignTask {
  id: string;
  campaign_id: string;
  task_type: string;
  status: 'TODO' | 'IN_PROGRESS' | 'DONE' | 'BLOCKED' | 'SKIPPED' | string;
  title: string;
  description?: string | null;
  related_idea_id?: string | null;
  related_product_id?: string | null;
  related_candidate_id?: string | null;
  result_json?: Record<string, unknown>;
  error_message?: string | null;
  created_at: string;
  updated_at: string;
}

export interface DiscoveryCampaignIdeaSummary {
  id: string;
  idea_name: string;
  category?: string;
  shop_concept_id?: string | null;
  collection_id?: string | null;
  status: string;
  quick_scan_verdict?: string | null;
  buy_readiness_status?: string;
  scout_status?: ScoutStatus | null;
  scout_score?: number | null;
  scout_confidence?: ScoutConfidence | null;
  scout_reason?: string | null;
  scout_next_step?: string | null;
  scout_metrics?: Record<string, unknown> | null;
  opportunity_score?: number;
  research_completeness_score?: number;
  promoted_product_id?: string | null;
  required_next_evidence?: string[] | string | null;
}

export interface DiscoveryCampaignProductSummary {
  id: string;
  name: string;
  category?: string;
  shop_concept_id?: string | null;
  collection_id?: string | null;
  status: string;
  research_verdict?: string | null;
  buy_readiness_status?: string | null;
  final_decision?: string | null;
  research_completeness_score: number;
  opportunity_score: number;
  next_action?: string | null;
  main_blocker?: string | null;
}

export interface DiscoveryCampaignTaskInput {
  task_type: string;
  title: string;
  description?: string | null;
  status?: 'TODO' | 'IN_PROGRESS' | 'DONE' | 'BLOCKED' | 'SKIPPED' | string;
  related_idea_id?: string | null;
  related_product_id?: string | null;
  related_candidate_id?: string | null;
  result_json?: Record<string, unknown>;
  error_message?: string | null;
}

export interface DiscoveryCampaignTaskUpdateInput {
  task_type?: string;
  title?: string;
  description?: string | null;
  status?: 'TODO' | 'IN_PROGRESS' | 'DONE' | 'BLOCKED' | 'SKIPPED' | string;
  related_idea_id?: string | null;
  related_product_id?: string | null;
  related_candidate_id?: string | null;
  result_json?: Record<string, unknown>;
  error_message?: string | null;
}

export interface DiscoveryTaskUpdate {
  status?: 'TODO' | 'DONE' | 'SKIPPED' | 'BLOCKED' | string;
  notes?: string;
  linked_evidence_id?: string | null;
  linked_source_id?: string | null;
  linked_competitor_id?: string | null;
  linked_product_id?: string | null;
}

export interface ProductIdea {
  id: string;
  idea_name: string;
  category?: string;
  campaign_id?: string | null;
  shop_concept_id?: string | null;
  collection_id?: string | null;
  source_platform?: string;
  source_url?: string;
  rough_supplier_cost?: number;
  estimated_landed_cost?: number;
  why_interesting?: string;
  risk_flags?: string[] | string | null;
  quick_market_signal?: string;
  quick_profit_signal?: string;
  research_priority?: string;
  notes?: string;
  status: 'NEW_IDEA' | 'QUICK_SCAN_NEEDED' | 'QUICK_SCAN_COMPLETE' | 'REJECTED' | 'PROMISING' | 'PROMOTED_TO_PRODUCT' | 'ARCHIVED' | string;
  quick_scan_verdict?: string;
  quick_scan_reason?: string;
  scout_status?: ScoutStatus;
  scout_score?: number;
  scout_confidence?: ScoutConfidence;
  scout_reason?: string;
  scout_next_step?: string;
  scout_metrics?: Record<string, unknown> | null;
  scout_updated_at?: string | null;
  research_completeness_score?: number;
  discovery_completeness_score?: number;
  opportunity_score?: number;
  buy_readiness_status?: 'NOT_READY' | 'ALMOST_READY' | 'READY' | string;
  suggested_keywords?: Record<string, string[]> | string[] | string | null;
  required_next_evidence?: string[] | string | null;
  promoted_product_id?: string | null;
  tasks?: DiscoveryTask[];
  created_at: string;
  updated_at: string;
}

export type DiscoveryIdea = ProductIdea;

export interface OpportunityScoutInput {
  campaign_id?: string | null;
  product_id?: string | null;
  local_search_summary?: Record<string, unknown> | null;
  keyword_signals?: string[];
  active_listing_candidates?: Array<Record<string, unknown>>;
  competitor_candidates?: Array<Record<string, unknown>>;
  supplier_candidates?: Array<Record<string, unknown>>;
  risk_notes?: string[];
  force_refresh?: boolean;
}

export interface OpportunityScoutResponse {
  idea_id: string;
  campaign_id?: string | null;
  product_id?: string | null;
  scout_status: ScoutStatus;
  scout_score: number;
  confidence: ScoutConfidence;
  buyer_problem_score: number;
  active_market_score: number;
  supplier_path_score: number;
  competition_risk_score: number;
  margin_potential_score: number;
  compatibility_risk_score: number;
  evidence_friction_score: number;
  reason: string;
  next_step: string;
  metrics: Record<string, unknown>;
}

export interface ProductIdeaQuickScanInput {
  idea_name: string;
  category?: string;
  campaign_id?: string | null;
  shop_concept_id?: string | null;
  collection_id?: string | null;
  source_platform?: string;
  source_url?: string;
  rough_supplier_cost?: number;
  estimated_landed_cost?: number;
  why_interesting?: string;
  notes?: string;
  marketplace_observation?: string;
}

export type DiscoveryQuickScanInput = ProductIdeaQuickScanInput;

export type ExternalResearchQueue = 'standard' | 'priority';
export type ExternalResearchStatus = 'QUEUED' | 'SUBMITTED' | 'READY' | 'FAILED' | 'IMPORTED';
export type EvidenceCandidateSource = 'DATAFORSEO' | 'MANUAL_CAPTURE' | 'VISION';
export type EvidenceCandidateType = 'MARKETPLACE_EVIDENCE' | 'COMPETITOR_LISTING' | 'SUPPLIER_SOURCE' | 'RISK_FLAG';
export type EvidenceReviewStatus = 'PENDING' | 'APPROVED' | 'REJECTED' | 'IGNORED';
export type EvidenceApproveAs = 'MARKETPLACE_EVIDENCE' | 'COMPETITOR_LISTING' | 'SUPPLIER_SOURCE';
export type CaptureType = 'MARKETPLACE_SCREENSHOT' | 'SUPPLIER_SCREENSHOT' | 'COMPETITOR_SCREENSHOT' | 'VISUAL_RISK';

export interface ExternalResearchRunInput {
  idea_id?: string | null;
  product_id?: string | null;
  queries: string[];
  max_results?: number;
  queue?: ExternalResearchQueue;
  budget_override?: boolean;
}

export interface ExternalResearchJob {
  id: string;
  idea_id?: string | null;
  product_id?: string | null;
  campaign_id?: string | null;
  provider: string;
  api_area: string;
  query: string;
  queue: ExternalResearchQueue;
  status: ExternalResearchStatus;
  provider_task_id?: string | null;
  cost_estimate?: number | null;
  result_count?: number;
  raw_request?: Record<string, unknown>;
  raw_response?: Record<string, unknown>;
  last_error?: string | null;
  candidate_count?: number;
  created_at: string;
  updated_at: string;
}

export interface ExternalResearchJobDetailResponse {
  job: ExternalResearchJob;
  candidates: EvidenceCandidate[];
}

export interface EvidenceCandidate {
  id: string;
  job_id?: string | null;
  idea_id?: string | null;
  product_id?: string | null;
  campaign_id?: string | null;
  source: EvidenceCandidateSource;
  candidate_type: EvidenceCandidateType;
  marketplace?: string | null;
  evidence_type?: string | null;
  title?: string | null;
  url?: string | null;
  price?: number | null;
  shipping_price?: number | null;
  seller?: string | null;
  rating?: number | null;
  review_count?: number | null;
  image_url?: string | null;
  confidence?: string;
  review_status: EvidenceReviewStatus;
  raw_json?: Record<string, unknown>;
  created_at: string;
}

export interface DiscoveryCampaignReport {
  campaign_id: string;
  shop_concept_id?: string | null;
  shop_concept_name?: string | null;
  collection_id?: string | null;
  collection_name?: string | null;
  total_ideas: number;
  rejected_ideas: number;
  promising_ideas: number;
  promoted_products: number;
  dataforseo_spend_estimate: number;
  budget_limit_usd: number;
  spend_remaining?: number | null;
  budget_used_percent?: number;
  ideas_by_verdict?: Record<string, number>;
  products_by_decision?: Record<string, number>;
  candidate_count_by_status?: Record<string, number>;
  ideas_with_keyword_demand?: number;
  ideas_with_trend_research?: number;
  products_with_keyword_demand?: number;
  products_with_trend_research?: number;
  products_with_evergreen_trend?: number;
  products_with_weak_landed_cost_ratio?: number;
  portfolio_items_total?: number;
  portfolio_items_by_role?: Record<string, number>;
  portfolio_items_by_status?: Record<string, number>;
  portfolio_collection_gaps?: string[];
  external_jobs_total?: number;
  external_jobs_pending_count?: number;
  external_jobs_imported_count?: number;
  external_jobs_failed_count?: number;
  latest_pending_job_id?: string | null;
  latest_pending_job_query?: string | null;
  latest_pending_job_status?: string | null;
  external_research_next_action?: string | null;
  watchlist_products?: DiscoveryCampaignProductSummary[];
  skip_products?: DiscoveryCampaignProductSummary[];
  ready_for_sample_products?: DiscoveryCampaignProductSummary[];
  next_best_task?: string | null;
  top_ranked_ideas: DiscoveryCampaignIdeaSummary[];
  top_products: DiscoveryCampaignProductSummary[];
  next_actions: string[];
}

export interface DiscoveryCampaignDetail {
  campaign: DiscoveryCampaign;
  ideas: DiscoveryCampaignIdeaSummary[];
  tasks: DiscoveryCampaignTask[];
  report: DiscoveryCampaignReport;
  products: DiscoveryCampaignProductSummary[];
  evidence_candidates: EvidenceCandidate[];
  tasks_by_status: Record<string, number>;
}

export type ShopConceptStatus = 'DRAFT' | 'ACTIVE' | 'PAUSED' | string;
export type CollectionStatus = 'DRAFT' | 'ACTIVE' | 'PAUSED' | string;
export type PortfolioRole = 'CONSIDERING' | 'HERO' | 'ADD_ON' | 'BUNDLE_SUPPORT' | 'TRAFFIC' | 'PROFIT' | 'TEST' | 'REJECTED' | string;
export type PortfolioItemStatus = 'CONSIDERING' | 'RESEARCHING' | 'SAMPLE_READY' | 'SAMPLED' | 'REJECTED' | string;

export interface ShopConcept {
  id: string;
  name: string;
  description?: string | null;
  target_customer?: string | null;
  category?: string | null;
  price_min?: number | null;
  price_max?: number | null;
  avoid_list_json?: Record<string, unknown>;
  preferred_attributes_json?: Record<string, unknown>;
  brand_angle?: string | null;
  status: ShopConceptStatus;
  created_at: string;
  updated_at: string;
  campaign_count?: number;
  collection_count?: number;
  idea_count?: number;
  product_count?: number;
  portfolio_item_count?: number;
}

export interface ProductCollection {
  id: string;
  shop_concept_id: string;
  shop_concept_name?: string | null;
  name: string;
  theme?: string | null;
  target_problem?: string | null;
  description?: string | null;
  status: CollectionStatus;
  created_at: string;
  updated_at: string;
  portfolio_item_count?: number;
  idea_count?: number;
  product_count?: number;
}

export interface PortfolioItem {
  id: string;
  shop_concept_id: string;
  shop_concept_name?: string | null;
  collection_id?: string | null;
  collection_name?: string | null;
  idea_id?: string | null;
  idea_name?: string | null;
  product_id?: string | null;
  product_name?: string | null;
  role: PortfolioRole;
  status: PortfolioItemStatus;
  assortment_fit_score: number;
  bundle_potential_score: number;
  notes?: string | null;
  created_at: string;
  updated_at: string;
}

export interface ShopPortfolioReport {
  shop_concept_id: string;
  shop_concept_name: string;
  shop_readiness_status?: string | null;
  shop_readiness_score?: number;
  shop_readiness_blockers?: string[];
  collections: ProductCollection[];
  portfolio_items: PortfolioItem[];
  total_items: number;
  items_by_role: Record<string, number>;
  items_by_status: Record<string, number>;
  products_by_decision: Record<string, number>;
  watchlist_products: Array<Record<string, unknown>>;
  skip_products: Array<Record<string, unknown>>;
  ready_for_sample_products: Array<Record<string, unknown>>;
  ideas_still_under_research: Array<Record<string, unknown>>;
  collection_gaps: string[];
  next_recommended_campaign?: string | null;
  next_action?: string | null;
}

export interface ShopConceptDetail {
  shop_concept: ShopConcept;
  collections: ProductCollection[];
  portfolio_items: PortfolioItem[];
  report: ShopPortfolioReport;
}

export interface EvidenceCandidateReviewInput {
  approve_as?: EvidenceApproveAs;
  task_id?: string | null;
  product_id?: string | null;
  notes?: string | null;
}

export interface EvidenceCandidateReviewResponse {
  candidate: EvidenceCandidate;
  created_object_type?: string | null;
  created_object_id?: string | null;
  linked_task_id?: string | null;
}

export interface ManualCaptureResponse {
  candidate: EvidenceCandidate;
  vision_report_id?: string | null;
}

export interface ManualCaptureInput {
  idea_id?: string | null;
  product_id?: string | null;
  task_id?: string | null;
  capture_type: CaptureType;
  url?: string | null;
  pasted_text?: string | null;
  notes?: string | null;
  screenshot?: File | null;
}

export interface ProductIdeaQuickScanResponse {
  idea: ProductIdea;
  quick_scan_verdict: string;
  quick_scan_reason: string;
  research_priority: string;
  research_completeness_score?: number;
  discovery_completeness_score?: number;
  opportunity_score?: number;
  buy_readiness_status?: string;
  required_next_evidence: string[];
  suggested_keywords: Record<string, string[]> | string[];
  risk_flags: string[];
  tasks: DiscoveryTask[];
}

export type DiscoveryQuickScanResponse = ProductIdeaQuickScanResponse;

export interface OpportunityBoardRow {
  id: string;
  entity_type: 'idea' | 'product' | string;
  title: string;
  category?: string;
  discovery_completeness_score?: number;
  research_completeness_score: number;
  research_verdict?: string;
  buy_readiness_status?: string;
  risk_level?: string;
  scout_status?: ScoutStatus | null;
  scout_score?: number | null;
  scout_confidence?: ScoutConfidence | null;
  scout_reason?: string | null;
  scout_next_step?: string | null;
  scout_metrics?: Record<string, unknown> | null;
  sold_evidence_count: number;
  active_evidence_count: number;
  sold_evidence_count_verified?: number;
  active_evidence_count_verified?: number;
  test_data_count?: number;
  unverified_evidence_count?: number;
  median_sold_price?: number | null;
  median_active_price?: number | null;
  median_sold_price_total?: number | null;
  median_active_price_total?: number | null;
  sold_price_range?: number[];
  sold_price_range_total?: number[];
  active_price_range?: number[];
  active_price_range_total?: number[];
  median_sold_shipping?: number | null;
  median_active_shipping?: number | null;
  median_shipping?: number | null;
  best_landed_cost?: number | null;
  best_profit_scenario?: string | null;
  competition_gap_score?: number | null;
  supplier_confidence?: string | null;
  next_action?: string | null;
  source_platform?: string | null;
  status?: string | null;
}

export interface ResearchRunResponse {
  product_id: string;
  status: string;
  final_decision?: string | null;
  final_score?: number | null;
  decision?: Record<string, unknown> | null;
  reports: Array<Record<string, unknown>>;
}

export interface InventoryItem {
  id: string;
  product_id: string;
  quantity_on_hand: number;
  quantity_ordered: number;
  quantity_sold: number;
  quantity_returned: number;
  average_landed_cost?: number;
  location_code?: string;
  reorder_point?: number;
}

export interface Sale {
  id: string;
  product_id: string;
  marketplace?: string;
  sale_date?: string;
  quantity: number;
  sale_price?: number;
  marketplace_fee?: number;
  net_profit?: number;
  returned?: boolean;
}

export interface ProductFile {
  id: string;
  product_id: string;
  file_type?: string;
  file_url?: string;
  original_filename?: string;
  notes?: string;
}

export interface Listing {
  id: string;
  product_id: string;
  marketplace: 'ebay' | 'mercari' | 'facebook' | 'other';
  title?: string;
  description?: string;
  price?: number;
  quantity?: number;
  status: 'draft' | 'published' | 'sold' | 'ended';
  url?: string;
}

export interface DashboardStats {
  total_products: number;
  blocked_count: number;
  watchlist_count: number;
  buy_sample_candidates: number;
  products_ordered: number;
  products_listed: number;
  top_categories: Array<{ category: string; count: number }>;
  recent_products: Product[];
  reorder_recommendations: Product[];
  agent_activity: AgentResult[];
}

export interface CreateProductInput {
  name: string;
  category: string;
  subcategory?: string;
  description?: string;
  supplier_url?: string;
}
