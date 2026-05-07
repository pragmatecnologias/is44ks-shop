import type { AppConfig, ToolResult } from '../types.js';
import { buildAudit } from '../utils/audit.js';
import type { ResellOSClient } from '../resellosClient.js';

export async function searchWebLocal(
  client: ResellOSClient,
  input: {
    query: string;
    intent: string;
    providers?: string[];
    max_results?: number;
    product_id?: string;
    idea_id?: string;
    campaign_id?: string;
  },
  config: AppConfig,
): Promise<ToolResult> {
  const body: Record<string, unknown> = {
    query: input.query,
    intent: input.intent,
    max_results: input.max_results ?? 10,
    store_results: true,
  };
  if (input.providers) body.providers = input.providers;
  if (input.product_id) body.product_id = input.product_id;
  if (input.idea_id) body.idea_id = input.idea_id;
  if (input.campaign_id) body.campaign_id = input.campaign_id;

  const response = await client.post<any>('/api/research/search', body);
  return {
    ok: true,
    data: response,
    summary: `Local search returned ${response.result_count} result(s) from ${response.requested_providers.join(', ')}.`,
    warnings: [
      'Local search results are NOT verified evidence.',
      'Do NOT treat active listings as sold evidence.',
      'Convert to candidates and verify before any readiness decision.',
    ],
    next_recommended_tool: response.result_count > 0 ? 'resellos_convert_search_result_to_candidate' : 'resellos_get_product_cockpit',
    audit: buildAudit('resellos_search_web_local', config.actor, input),
  };
}

export async function listResearchSearchResults(
  client: ResellOSClient,
  input: {
    product_id?: string;
    idea_id?: string;
    campaign_id?: string;
    intent?: string;
    provider?: string;
    limit?: number;
    offset?: number;
  },
  config: AppConfig,
): Promise<ToolResult> {
  const params = new URLSearchParams();
  if (input.product_id) params.set('product_id', input.product_id);
  if (input.idea_id) params.set('idea_id', input.idea_id);
  if (input.campaign_id) params.set('campaign_id', input.campaign_id);
  if (input.intent) params.set('intent', input.intent);
  if (input.provider) params.set('provider', input.provider);
  if (input.limit) params.set('limit', String(input.limit));
  if (input.offset) params.set('offset', String(input.offset));
  const path = `/api/research/search-results${params.toString() ? `?${params.toString()}` : ''}`;
  const results = await client.get<any[]>(path);
  return {
    ok: true,
    data: { results, count: results.length },
    summary: `Listed ${results.length} search result(s).`,
    warnings: [],
    next_recommended_tool: results.length ? 'resellos_convert_search_result_to_candidate' : null,
    audit: buildAudit('resellos_list_research_search_results', config.actor, input),
  };
}

export async function convertSearchResultToCandidate(
  client: ResellOSClient,
  input: {
    search_result_id: string;
    candidate_type: string;
    product_id?: string;
    idea_id?: string;
    campaign_id?: string;
    notes?: string;
    price?: number;
    title_override?: string;
  },
  config: AppConfig,
): Promise<ToolResult> {
  const response = await client.post<any>(`/api/research/search-results/${input.search_result_id}/candidate`, {
    candidate_type: input.candidate_type,
    product_id: input.product_id ?? undefined,
    idea_id: input.idea_id ?? undefined,
    campaign_id: input.campaign_id ?? undefined,
    notes: input.notes ?? undefined,
    price: input.price ?? undefined,
    title_override: input.title_override ?? undefined,
  });
  return {
    ok: true,
    data: response,
    summary: `Converted search result to candidate. Status: ${response.status}, verification: ${response.verification_status}.`,
    warnings: [
      'Converted candidate is PENDING. Manual review is required.',
      'Candidate is not verified evidence until approved through the normal workflow.',
    ],
    next_recommended_tool: 'resellos_list_evidence_candidates',
    audit: buildAudit('resellos_convert_search_result_to_candidate', config.actor, input),
  };
}

export async function rejectSearchResult(
  client: ResellOSClient,
  input: { search_result_id: string; reject_reason: string },
  config: AppConfig,
): Promise<ToolResult> {
  const response = await client.patch<any>(`/api/research/search-results/${input.search_result_id}/reject`, {
    reject_reason: input.reject_reason,
  });
  return {
    ok: true,
    data: response,
    summary: `Rejected search result: ${input.reject_reason}`,
    warnings: [],
    next_recommended_tool: null,
    audit: buildAudit('resellos_reject_search_result', config.actor, input),
  };
}