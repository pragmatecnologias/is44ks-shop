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
