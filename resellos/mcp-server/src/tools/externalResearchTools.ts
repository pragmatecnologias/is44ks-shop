import type { AppConfig, DataForSeoInput, ToolResult } from '../types.js';
import { buildAudit } from '../utils/audit.js';
import { guardDataForSeoRequest, guardQueries } from '../guards/costGuards.js';
import type { ResellOSClient } from '../resellosClient.js';

export async function runDataForSeoGoogleShopping(client: ResellOSClient, input: DataForSeoInput, config: AppConfig): Promise<ToolResult> {
  if (!config.allowPaidTools && !input.confirm) {
    throw new Error('Paid DataForSEO tool is disabled. Set RESELLOS_MCP_ALLOW_PAID_TOOLS=true or confirm the call explicitly.');
  }
  const query = guardQueries(config, [input.query]);
  const guarded = guardDataForSeoRequest(config, query, input.max_results);
  const response = await client.post<any>('/api/external-research/google-shopping', {
    idea_id: input.idea_id ?? undefined,
    queries: [guarded.query],
    max_results: guarded.maxResults,
    queue: 'standard',
  });
  const estimatedCost = Number(response?.estimated_cost ?? 0);
  return {
    ok: true,
    data: response,
    summary: `Submitted Google Shopping research for "${guarded.query}".`,
    warnings: response?.budget_warning ? [String(response.budget_warning)] : [],
    next_recommended_tool: 'resellos_poll_external_research_job',
    audit: buildAudit('resellos_run_dataforseo_google_shopping', config.actor, { ...input, query: guarded.query, max_results: guarded.maxResults }, estimatedCost),
  };
}

export async function pollExternalResearchJob(client: ResellOSClient, jobId: string, config: AppConfig): Promise<ToolResult> {
  const response = await client.post<any>(`/api/external-research/jobs/${jobId}/poll`, {});
  const candidates = Array.isArray(response?.candidates) ? response.candidates : [];
  return {
    ok: true,
    data: response,
    summary: `Polled external research job ${jobId}. ${candidates.length} candidate(s) available.`,
    warnings: [],
    next_recommended_tool: candidates.length ? 'resellos_list_evidence_candidates' : 'resellos_get_product_cockpit',
    audit: buildAudit('resellos_poll_external_research_job', config.actor, { job_id: jobId }),
  };
}
