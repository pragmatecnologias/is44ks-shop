import type { AppConfig, ToolResult } from '../types.js';
import { buildAudit } from '../utils/audit.js';
import { ensureDefined } from '../utils/validation.js';
import { guardWriteEnabled } from '../guards/approvalGuards.js';
import type { ResellOSClient } from '../resellosClient.js';

function wrap(
  tool: string,
  config: AppConfig,
  input: Record<string, unknown>,
  data: unknown,
  summary: string,
  nextRecommendedTool: string | null,
): ToolResult {
  return {
    ok: true,
    data,
    summary,
    warnings: [],
    next_recommended_tool: nextRecommendedTool,
    audit: buildAudit(tool, config.actor, input),
  };
}

export async function createDiscoveryCampaign(
  client: ResellOSClient,
  input: {
    name: string;
    shop_concept_id?: string;
    collection_id?: string;
    category?: string;
    goal?: string;
    constraints_json?: Record<string, unknown>;
    budget_limit_usd?: number;
    max_ideas?: number;
    max_products_to_promote?: number;
    status?: string;
    created_by?: string;
  },
  config: AppConfig,
): Promise<ToolResult> {
  guardWriteEnabled(config);
  const payload = {
    name: ensureDefined(input.name, 'name'),
    shop_concept_id: input.shop_concept_id ?? undefined,
    collection_id: input.collection_id ?? undefined,
    category: input.category ?? undefined,
    goal: input.goal ?? undefined,
    constraints_json: input.constraints_json ?? {},
    budget_limit_usd: input.budget_limit_usd ?? 25,
    max_ideas: input.max_ideas ?? 10,
    max_products_to_promote: input.max_products_to_promote ?? 3,
    status: input.status ?? 'DRAFT',
    created_by: input.created_by ?? config.actor,
  };
  const campaign = await client.post<any>('/api/discovery/campaigns', payload);
  return wrap('resellos_create_discovery_campaign', config, payload, campaign, `Created discovery campaign "${campaign.name ?? payload.name}".`, 'resellos_add_idea_to_campaign');
}

export async function listDiscoveryCampaigns(client: ResellOSClient, config: AppConfig): Promise<ToolResult> {
  const campaigns = await client.get<any[]>('/api/discovery/campaigns');
  return {
    ok: true,
    data: { campaigns },
    summary: `Loaded ${campaigns.length} discovery campaigns.`,
    warnings: [],
    next_recommended_tool: 'resellos_get_discovery_campaign',
    audit: buildAudit('resellos_list_discovery_campaigns', config.actor, {}),
  };
}

export async function getDiscoveryCampaign(client: ResellOSClient, campaignId: string, config: AppConfig): Promise<ToolResult> {
  const detail = await client.get<any>(`/api/discovery/campaigns/${campaignId}`);
  return {
    ok: true,
    data: detail,
    summary: `Loaded campaign "${detail?.campaign?.name ?? campaignId}".`,
    warnings: [],
    next_recommended_tool: 'resellos_get_campaign_report',
    audit: buildAudit('resellos_get_discovery_campaign', config.actor, { campaign_id: campaignId }),
  };
}

export async function createCampaignTask(
  client: ResellOSClient,
  input: {
    campaign_id: string;
    task_type: string;
    title: string;
    description?: string;
    status?: string;
    related_idea_id?: string;
    related_product_id?: string;
    related_candidate_id?: string;
    result_json?: Record<string, unknown>;
    error_message?: string;
  },
  config: AppConfig,
): Promise<ToolResult> {
  guardWriteEnabled(config);
  const payload = {
    task_type: ensureDefined(input.task_type, 'task_type'),
    title: ensureDefined(input.title, 'title'),
    description: input.description ?? undefined,
    status: input.status ?? 'TODO',
    related_idea_id: input.related_idea_id ?? undefined,
    related_product_id: input.related_product_id ?? undefined,
    related_candidate_id: input.related_candidate_id ?? undefined,
    result_json: input.result_json ?? undefined,
    error_message: input.error_message ?? undefined,
  };
  const task = await client.post<any>(`/api/discovery/campaigns/${input.campaign_id}/tasks`, payload);
  return wrap('resellos_create_campaign_task', config, { ...payload, campaign_id: input.campaign_id }, task, `Created campaign task "${task.title ?? payload.title}".`, 'resellos_get_discovery_campaign');
}

export async function updateCampaignTask(
  client: ResellOSClient,
  input: {
    campaign_id: string;
    task_id: string;
    task_type?: string;
    title?: string;
    description?: string;
    status?: string;
    related_idea_id?: string;
    related_product_id?: string;
    related_candidate_id?: string;
    result_json?: Record<string, unknown>;
    error_message?: string;
  },
  config: AppConfig,
): Promise<ToolResult> {
  guardWriteEnabled(config);
  const payload = {
    task_type: input.task_type ?? undefined,
    title: input.title ?? undefined,
    description: input.description ?? undefined,
    status: input.status ?? undefined,
    related_idea_id: input.related_idea_id ?? undefined,
    related_product_id: input.related_product_id ?? undefined,
    related_candidate_id: input.related_candidate_id ?? undefined,
    result_json: input.result_json ?? undefined,
    error_message: input.error_message ?? undefined,
  };
  const task = await client.patch<any>(`/api/discovery/campaigns/${input.campaign_id}/tasks/${input.task_id}`, payload);
  return wrap('resellos_update_campaign_task', config, { ...payload, campaign_id: input.campaign_id, task_id: input.task_id }, task, `Updated campaign task "${task.title ?? input.task_id}".`, 'resellos_get_discovery_campaign');
}

export async function getCampaignReport(client: ResellOSClient, campaignId: string, config: AppConfig): Promise<ToolResult> {
  guardWriteEnabled(config);
  const report = await client.get<any>(`/api/discovery/campaigns/${campaignId}/report`);
  return {
    ok: true,
    data: report,
    summary: `Generated campaign report for ${campaignId}.`,
    warnings: [],
    next_recommended_tool: 'resellos_get_discovery_campaign',
    audit: buildAudit('resellos_get_campaign_report', config.actor, { campaign_id: campaignId }),
  };
}

export async function generateCampaignNextTasks(client: ResellOSClient, campaignId: string, config: AppConfig): Promise<ToolResult> {
  guardWriteEnabled(config);
  const tasks = await client.post<any[]>(`/api/discovery/campaigns/${campaignId}/generate-next-tasks`, {});
  return {
    ok: true,
    data: { tasks },
    summary: `Generated ${tasks.length} next task(s) for campaign ${campaignId}.`,
    warnings: [],
    next_recommended_tool: 'resellos_get_discovery_campaign',
    audit: buildAudit('resellos_generate_campaign_next_tasks', config.actor, { campaign_id: campaignId }),
  };
}

export async function addIdeaToCampaign(
  client: ResellOSClient,
  input: {
    campaign_id: string;
    idea_name: string;
    category?: string;
    source_platform?: string;
    source_url?: string;
    rough_supplier_cost?: number | null;
    estimated_landed_cost?: number | null;
    why_interesting?: string;
    marketplace_observation?: string;
    notes?: string;
  },
  config: AppConfig,
): Promise<ToolResult> {
  guardWriteEnabled(config);
  const payload = {
    idea_name: ensureDefined(input.idea_name, 'idea_name'),
    category: input.category ?? undefined,
    campaign_id: input.campaign_id,
    source_platform: input.source_platform ?? undefined,
    source_url: input.source_url ?? undefined,
    rough_supplier_cost: input.rough_supplier_cost ?? undefined,
    estimated_landed_cost: input.estimated_landed_cost ?? undefined,
    why_interesting: input.why_interesting ?? undefined,
    marketplace_observation: input.marketplace_observation ?? undefined,
    notes: input.notes ?? undefined,
  };
  const idea = await client.post<any>(`/api/discovery/campaigns/${input.campaign_id}/ideas`, payload);
  return wrap('resellos_add_idea_to_campaign', config, payload, idea, `Added idea "${idea.idea_name ?? payload.idea_name}" to campaign.`, 'resellos_run_quick_scan');
}

export async function getCampaignNextTask(client: ResellOSClient, campaignId: string, config: AppConfig): Promise<ToolResult> {
  const result = await client.get<any>(`/api/discovery/campaigns/${campaignId}/next-task`);
  const summary = result.message
    ? 'No pending campaign tasks.'
    : `Next task: "${result.title ?? result.id}" (${result.status ?? 'TODO'})`;
  return {
    ok: true,
    data: result,
    summary,
    warnings: [],
    next_recommended_tool: result.message ? null : 'resellos_complete_campaign_task',
    audit: buildAudit('resellos_get_campaign_next_task', config.actor, { campaign_id: campaignId }),
  };
}

export async function completeCampaignTask(
  client: ResellOSClient,
  input: { campaign_id: string; task_id: string; result_json?: Record<string, unknown>; notes?: string },
  config: AppConfig,
): Promise<ToolResult> {
  guardWriteEnabled(config);
  const payload = { status: 'DONE', result_json: input.result_json ?? {}, error_message: input.notes ?? undefined };
  const task = await client.patch<any>(`/api/discovery/campaigns/${input.campaign_id}/tasks/${input.task_id}`, payload);
  return wrap('resellos_complete_campaign_task', config, { ...payload, campaign_id: input.campaign_id, task_id: input.task_id }, task, `Completed campaign task "${task.title ?? input.task_id}".`, 'resellos_get_campaign_next_task');
}

export async function blockCampaignTask(
  client: ResellOSClient,
  input: { campaign_id: string; task_id: string; error_message: string },
  config: AppConfig,
): Promise<ToolResult> {
  guardWriteEnabled(config);
  const payload = { status: 'BLOCKED', error_message: input.error_message };
  const task = await client.patch<any>(`/api/discovery/campaigns/${input.campaign_id}/tasks/${input.task_id}`, payload);
  return wrap('resellos_block_campaign_task', config, { ...payload, campaign_id: input.campaign_id, task_id: input.task_id }, task, `Blocked campaign task "${task.title ?? input.task_id}" — ${input.error_message}.`, 'resellos_get_campaign_next_task');
}
