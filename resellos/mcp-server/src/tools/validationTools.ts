import type { AppConfig, ToolResult, ProductDemandResearchInput, ProductDemandResearchVerifyInput, ProductTrendResearchInput, ProductTrendResearchVerifyInput } from '../types.js';
import { buildAudit } from '../utils/audit.js';
import { guardWriteEnabled } from '../guards/approvalGuards.js';
import { guardVerificationApproval } from '../guards/verificationGuards.js';
import type { ResellOSClient } from '../resellosClient.js';

function wrap(tool: string, config: AppConfig, input: Record<string, unknown>, data: unknown, summary: string, nextRecommendedTool: string | null): ToolResult {
  return {
    ok: true,
    data,
    summary,
    warnings: [],
    next_recommended_tool: nextRecommendedTool,
    audit: buildAudit(tool, config.actor, input),
  };
}

function buildQuery(input: { product_id?: string; idea_id?: string; campaign_id?: string; verification_status?: string }): string {
  const params = new URLSearchParams();
  if (input.product_id) params.set('product_id', input.product_id);
  if (input.idea_id) params.set('idea_id', input.idea_id);
  if (input.campaign_id) params.set('campaign_id', input.campaign_id);
  if (input.verification_status) params.set('verification_status', input.verification_status);
  return params.toString();
}

export async function addKeywordDemand(client: ResellOSClient, input: ProductDemandResearchInput, config: AppConfig): Promise<ToolResult> {
  guardWriteEnabled(config);
  const payload = {
    ...input,
    created_by: input.created_by ?? config.actor,
  };
  const response = await client.post<any>('/api/validation/demand', payload);
  return wrap('resellos_add_keyword_demand', config, payload, response, `Captured keyword demand for "${response?.keyword ?? input.keyword}".`, 'resellos_list_keyword_demand');
}

export async function listKeywordDemand(client: ResellOSClient, input: { product_id?: string; idea_id?: string; campaign_id?: string; verification_status?: string }, config: AppConfig): Promise<ToolResult> {
  const query = buildQuery(input);
  const demand = await client.get<any[]>(`/api/validation/demand${query ? `?${query}` : ''}`);
  return {
    ok: true,
    data: { demand },
    summary: `Loaded ${demand.length} keyword demand row(s).`,
    warnings: [],
    next_recommended_tool: demand.length ? 'resellos_get_product_validation_checklist' : 'resellos_add_keyword_demand',
    audit: buildAudit('resellos_list_keyword_demand', config.actor, input as Record<string, unknown>),
  };
}

export async function verifyKeywordDemand(client: ResellOSClient, input: ProductDemandResearchVerifyInput & { id: string }, config: AppConfig): Promise<ToolResult> {
  guardWriteEnabled(config);
  guardVerificationApproval(config, input);
  const response = await client.patch<any>(`/api/validation/demand/${input.id}/verify`, {
    verification_status: input.verification_status,
    source_url: input.source_url ?? undefined,
    screenshot_url: input.screenshot_url ?? undefined,
    verification_notes: input.verification_notes ?? undefined,
  });
  return wrap('resellos_verify_keyword_demand', config, { id: input.id }, response, `Verified keyword demand ${input.id}.`, 'resellos_get_product_validation_checklist');
}

export async function addTrendResearch(client: ResellOSClient, input: ProductTrendResearchInput, config: AppConfig): Promise<ToolResult> {
  guardWriteEnabled(config);
  const payload = {
    ...input,
    created_by: input.created_by ?? config.actor,
  };
  const response = await client.post<any>('/api/validation/trends', payload);
  return wrap('resellos_add_trend_research', config, payload, response, `Captured trend research for "${response?.keyword ?? input.keyword}".`, 'resellos_list_trend_research');
}

export async function listTrendResearch(client: ResellOSClient, input: { product_id?: string; idea_id?: string; campaign_id?: string; verification_status?: string }, config: AppConfig): Promise<ToolResult> {
  const query = buildQuery(input);
  const trends = await client.get<any[]>(`/api/validation/trends${query ? `?${query}` : ''}`);
  return {
    ok: true,
    data: { trends },
    summary: `Loaded ${trends.length} trend research row(s).`,
    warnings: [],
    next_recommended_tool: trends.length ? 'resellos_get_product_validation_checklist' : 'resellos_add_trend_research',
    audit: buildAudit('resellos_list_trend_research', config.actor, input as Record<string, unknown>),
  };
}

export async function verifyTrendResearch(client: ResellOSClient, input: ProductTrendResearchVerifyInput & { id: string }, config: AppConfig): Promise<ToolResult> {
  guardWriteEnabled(config);
  guardVerificationApproval(config, input);
  const response = await client.patch<any>(`/api/validation/trends/${input.id}/verify`, {
    verification_status: input.verification_status,
    source_url: input.source_url ?? undefined,
    screenshot_url: input.screenshot_url ?? undefined,
    verification_notes: input.verification_notes ?? undefined,
  });
  return wrap('resellos_verify_trend_research', config, { id: input.id }, response, `Verified trend research ${input.id}.`, 'resellos_get_product_validation_checklist');
}

export async function getProductValidationChecklist(client: ResellOSClient, productId: string, config: AppConfig): Promise<ToolResult> {
  const checklist = await client.get<any>(`/api/validation/products/${productId}/checklist`);
  return {
    ok: true,
    data: checklist,
    summary: `Loaded validation checklist for product ${productId}.`,
    warnings: [],
    next_recommended_tool: 'resellos_run_product_validation',
    audit: buildAudit('resellos_get_product_validation_checklist', config.actor, { product_id: productId }),
  };
}

export async function runProductValidation(client: ResellOSClient, productId: string, config: AppConfig): Promise<ToolResult> {
  guardWriteEnabled(config);
  const checklist = await client.post<any>(`/api/validation/products/${productId}/run`, {});
  return {
    ok: true,
    data: checklist,
    summary: `Ran validation checklist for product ${productId}.`,
    warnings: [],
    next_recommended_tool: 'resellos_get_product_cockpit',
    audit: buildAudit('resellos_run_product_validation', config.actor, { product_id: productId }),
  };
}
