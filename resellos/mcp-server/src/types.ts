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

export interface VerifyInput {
  id: string;
  verification_status: 'USER_VERIFIED';
  source_url?: string | null;
  screenshot_url?: string | null;
  verification_notes?: string | null;
  confirm?: boolean | null;
}
