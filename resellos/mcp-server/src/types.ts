export type JsonValue = string | number | boolean | null | JsonObject | JsonValue[];
export interface JsonObject {
  [key: string]: JsonValue | undefined;
}

export interface ToolResult<T = unknown> {
  ok: boolean;
  data?: T;
  summary: string;
  warnings: string[];
  next_recommended_tool?: string | null;
  audit: {
    actor: string;
    tool: string;
    timestamp: string;
    product_id?: string | null;
    idea_id?: string | null;
    campaign_id?: string | null;
    cost_estimate?: number | null;
  };
}

export interface AppConfig {
  apiBaseUrl: string;
  actor: string;
  mode: string;
  allowWrites: boolean;
  allowPaidTools: boolean;
  maxDataForSeoResults: number;
  maxDataForSeoQueries: number;
  requireApprovalForVerification: boolean;
  requireApprovalForPaidTools: boolean;
  logLevel: string;
}

export interface ResellosErrorPayload {
  ok: false;
  status: number;
  message: string;
  details?: unknown;
}

export interface DiscoveryIdeaInput {
  idea_name: string;
  category?: string | null;
  source_platform?: string | null;
  source_url?: string | null;
  rough_supplier_cost?: number | null;
  estimated_landed_cost?: number | null;
  why_interesting?: string | null;
  notes?: string | null;
}

export interface DiscoveryCampaignInput {
  name: string;
  shop_concept_id?: string | null;
  collection_id?: string | null;
  category?: string | null;
  goal?: string | null;
  constraints_json?: Record<string, unknown>;
  budget_limit_usd?: number;
  max_ideas?: number;
  max_products_to_promote?: number;
  status?: string;
  created_by?: string | null;
}

export interface DiscoveryCampaignUpdateInput extends Partial<DiscoveryCampaignInput> {
  name?: string;
}

export interface DiscoveryCampaignTaskInput {
  task_type: string;
  title: string;
  description?: string | null;
  status?: string;
  related_idea_id?: string | null;
  related_product_id?: string | null;
  related_candidate_id?: string | null;
  result_json?: Record<string, unknown>;
  error_message?: string | null;
}

export interface DiscoveryCampaignTaskUpdateInput extends Partial<DiscoveryCampaignTaskInput> {}

export type PortfolioRole =
  | 'CONSIDERING'
  | 'HERO'
  | 'ADD_ON'
  | 'BUNDLE_SUPPORT'
  | 'TRAFFIC'
  | 'PROFIT'
  | 'TEST'
  | 'REJECTED';

export type PortfolioItemStatus = 'CONSIDERING' | 'RESEARCHING' | 'SAMPLE_READY' | 'SAMPLED' | 'REJECTED';
export type ShopConceptStatus = 'DRAFT' | 'ACTIVE' | 'PAUSED';
export type CollectionStatus = 'DRAFT' | 'ACTIVE' | 'PAUSED';

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

export interface QuickScanInput {
  idea_id: string;
}

export interface ResearchTasksInput {
  idea_id: string;
}

export interface DataForSeoInput {
  idea_id?: string | null;
  product_id?: string | null;
  query: string;
  max_results: number;
  confirm?: boolean | null;
}

export interface CandidateQueryInput {
  idea_id?: string | null;
  product_id?: string | null;
  job_id?: string | null;
  review_status?: string | null;
}

export interface CandidateApproveInput {
  candidate_id: string;
  approve_as: 'MARKETPLACE_EVIDENCE' | 'COMPETITOR_LISTING' | 'SUPPLIER_SOURCE';
  task_id?: string | null;
  product_id?: string | null;
  notes?: string | null;
  confirm?: boolean | null;
}

export interface ManualCaptureInput {
  idea_id?: string | null;
  product_id?: string | null;
  task_id?: string | null;
  capture_type: 'MARKETPLACE_SCREENSHOT' | 'SUPPLIER_SCREENSHOT' | 'COMPETITOR_SCREENSHOT' | 'VISUAL_RISK';
  url?: string | null;
  pasted_text?: string | null;
  notes?: string | null;
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

export interface VerifyInput {
  id: string;
  verification_status: 'USER_VERIFIED';
  source_url?: string | null;
  screenshot_url?: string | null;
  verification_notes?: string | null;
  confirm?: boolean | null;
}

// Local Search Broker types
export interface LocalSearchInput {
  query: string;
  intent: 'SOLD_EVIDENCE' | 'ACTIVE_LISTING' | 'SUPPLIER' | 'COMPETITOR' | 'COMPLAINT_RESEARCH' | 'KEYWORD_DEMAND' | 'GENERAL_RESEARCH';
  providers?: ('SEARXNG' | 'OPENSERP')[];
  max_results?: number;
  product_id?: string | null;
  idea_id?: string | null;
  campaign_id?: string | null;
}

export interface ListResearchSearchResultsInput {
  product_id?: string | null;
  idea_id?: string | null;
  campaign_id?: string | null;
  intent?: string | null;
  provider?: string | null;
  limit?: number;
  offset?: number;
}

export interface ConvertSearchResultInput {
  search_result_id: string;
  candidate_type: 'SOLD_LISTING' | 'ACTIVE_LISTING' | 'SUPPLIER_SOURCE' | 'COMPETITOR_LISTING' | 'COMPLAINT_NOTE' | 'KEYWORD_DEMAND_NOTE';
  product_id?: string | null;
  idea_id?: string | null;
  campaign_id?: string | null;
  notes?: string | null;
  price?: number | null;
  title_override?: string | null;
}

export interface RejectSearchResultInput {
  search_result_id: string;
  reject_reason: string;
}
