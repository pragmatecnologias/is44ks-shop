import type { AppConfig, DiscoveryIdeaInput, ToolResult } from '../types.js';
import { buildAudit } from '../utils/audit.js';
import { ensureDefined } from '../utils/validation.js';
import type { ResellOSClient } from '../resellosClient.js';
import type { ToolContext } from '../toolTypes.js';

export async function getDiscoveryBoard(client: ResellOSClient, input: { include_archived?: boolean; category?: string }, config: AppConfig): Promise<ToolResult> {
  const ideas = await client.get<any[]>('/api/discovery');
  const opportunities = await client.get<any[]>('/api/discovery/opportunity-board');
  const filteredIdeas = input.category ? ideas.filter((idea) => String(idea.category || '').toLowerCase() === input.category!.toLowerCase()) : ideas;
  const filteredOpportunities = input.category ? opportunities.filter((row) => String(row.category || '').toLowerCase() === input.category!.toLowerCase()) : opportunities;
  const summary = {
    total_ideas: filteredIdeas.length,
    promoted_products: filteredOpportunities.filter((row) => row.entity_type === 'product').length,
    ready_for_sample: filteredOpportunities.filter((row) => String(row.buy_readiness_status || '').toUpperCase() === 'READY').length,
    watchlist: filteredOpportunities.filter((row) => String(row.status || '').toUpperCase() === 'WATCHLIST' || String(row.final_decision || '').toUpperCase() === 'WATCHLIST').length,
  };
  return {
    ok: true,
    data: { ideas: filteredIdeas, opportunities: filteredOpportunities, summary },
    summary: `Loaded ${filteredIdeas.length} discovery ideas and ${filteredOpportunities.length} opportunity rows.`,
    warnings: input.include_archived ? ['Archived ideas included if present.'] : [],
    next_recommended_tool: 'resellos_get_product_cockpit',
    audit: buildAudit('resellos_get_discovery_board', config.actor, input as Record<string, unknown>),
  };
}

export async function createDiscoveryIdea(client: ResellOSClient, input: DiscoveryIdeaInput, config: AppConfig): Promise<ToolResult> {
  const payload = {
    idea_name: ensureDefined(input.idea_name, 'idea_name'),
    category: input.category ?? undefined,
    source_platform: input.source_platform ?? undefined,
    source_url: input.source_url ?? undefined,
    rough_supplier_cost: input.rough_supplier_cost ?? undefined,
    estimated_landed_cost: input.estimated_landed_cost ?? undefined,
    why_interesting: input.why_interesting ?? undefined,
    notes: input.notes ?? undefined,
    status: 'NEW',
  };
  const idea = await client.post<any>('/api/discovery', payload);
  return {
    ok: true,
    data: idea,
    summary: `Created discovery idea "${idea.idea_name ?? payload.idea_name}".`,
    warnings: [],
    next_recommended_tool: 'resellos_run_quick_scan',
    audit: buildAudit('resellos_create_discovery_idea', config.actor, payload),
  };
}

export async function runQuickScan(client: ResellOSClient, input: { idea_id: string }, config: AppConfig): Promise<ToolResult> {
  const idea = await client.get<any>(`/api/discovery/${input.idea_id}`);
  const response = await client.post<any>('/api/discovery/quick-scan', {
    idea_name: idea.idea_name,
    category: idea.category ?? undefined,
    source_platform: idea.source_platform ?? undefined,
    source_url: idea.source_url ?? undefined,
    rough_supplier_cost: idea.rough_supplier_cost ?? undefined,
    estimated_landed_cost: idea.estimated_landed_cost ?? undefined,
    why_interesting: idea.why_interesting ?? undefined,
    notes: idea.notes ?? undefined,
    marketplace_observation: undefined,
  });
  return {
    ok: true,
    data: {
      original_idea_id: input.idea_id,
      scanned_idea: response?.idea ?? null,
      quick_scan_verdict: response?.quick_scan_verdict ?? null,
      quick_scan_reason: response?.quick_scan_reason ?? null,
      research_priority: response?.research_priority ?? null,
      research_completeness_score: response?.research_completeness_score ?? null,
      discovery_completeness_score: response?.discovery_completeness_score ?? null,
      opportunity_score: response?.opportunity_score ?? null,
      buy_readiness_status: response?.buy_readiness_status ?? null,
      tasks: response?.tasks ?? [],
    },
    summary: `Quick scan completed for discovery idea ${input.idea_id}.`,
    warnings: [],
    next_recommended_tool: 'resellos_generate_research_tasks',
    audit: buildAudit('resellos_run_quick_scan', config.actor, { idea_id: input.idea_id }),
  };
}
