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

// ---------------------------------------------------------------------------
// Campaign
// ---------------------------------------------------------------------------

export async function createProductionCampaign(
  client: ResellOSClient,
  input: {
    name: string;
    goal?: string;
    workspace_type?: string;
    budget_limit_usd?: number;
  },
  config: AppConfig,
): Promise<ToolResult> {
  guardWriteEnabled(config);
  const payload = {
    name: ensureDefined(input.name, 'name'),
    goal: input.goal ?? undefined,
    workspace_type: input.workspace_type ?? undefined,
    budget_limit_usd: input.budget_limit_usd ?? undefined,
  };
  const campaign = await client.post<any>('/api/production/campaigns', payload);
  return wrap('resellos_create_production_campaign', config, payload, campaign, `Created production campaign "${campaign.name ?? payload.name}".`, 'resellos_add_machine_candidate');
}

export async function listProductionCampaigns(
  client: ResellOSClient,
  config: AppConfig,
): Promise<ToolResult> {
  const campaigns = await client.get<any[]>('/api/production/campaigns');
  return {
    ok: true,
    data: { campaigns },
    summary: `Loaded ${campaigns.length} production campaigns.`,
    warnings: [],
    next_recommended_tool: 'resellos_get_production_campaign',
    audit: buildAudit('resellos_list_production_campaigns', config.actor, {}),
  };
}

export async function getProductionCampaign(
  client: ResellOSClient,
  campaignId: string,
  config: AppConfig,
): Promise<ToolResult> {
  const detail = await client.get<any>(`/api/production/campaigns/${campaignId}`);
  return {
    ok: true,
    data: detail,
    summary: `Loaded production campaign "${detail?.campaign?.name ?? campaignId}" with ${detail?.machines?.length ?? 0} machines.`,
    warnings: [],
    next_recommended_tool: 'resellos_add_machine_candidate',
    audit: buildAudit('resellos_get_production_campaign', config.actor, { campaign_id: campaignId }),
  };
}

// ---------------------------------------------------------------------------
// Machine
// ---------------------------------------------------------------------------

export async function addMachineCandidate(
  client: ResellOSClient,
  input: {
    campaign_id: string;
    name: string;
    brand?: string;
    model?: string;
    category?: string;
    description?: string;
    url?: string;
    price_new?: number;
    condition?: string;
    power_requirements?: string;
    workspace_needed?: string;
    safety_notes?: string;
  },
  config: AppConfig,
): Promise<ToolResult> {
  guardWriteEnabled(config);
  const payload = {
    campaign_id: ensureDefined(input.campaign_id, 'campaign_id'),
    name: ensureDefined(input.name, 'name'),
    brand: input.brand ?? undefined,
    model: input.model ?? undefined,
    category: input.category ?? undefined,
    description: input.description ?? undefined,
    url: input.url ?? undefined,
    price_new: input.price_new ?? undefined,
    condition: input.condition ?? undefined,
    power_requirements: input.power_requirements ?? undefined,
    workspace_needed: input.workspace_needed ?? undefined,
    safety_notes: input.safety_notes ?? undefined,
  };
  const machine = await client.post<any>('/api/production/machines', payload);
  return wrap('resellos_add_machine_candidate', config, payload, machine, `Added machine candidate "${machine.name ?? payload.name}".`, 'resellos_get_machine_cockpit');
}

export async function getMachineCockpit(
  client: ResellOSClient,
  machineId: string,
  config: AppConfig,
): Promise<ToolResult> {
  const cockpit = await client.get<any>(`/api/production/machines/${machineId}`);
  const machine = cockpit?.machine;
  return {
    ok: true,
    data: cockpit,
    summary: `Machine "${machine?.name ?? machineId}": ${cockpit?.evidence?.length ?? 0} evidence, ${cockpit?.product_families?.length ?? 0} families, decision: ${cockpit?.decision?.recommendation ?? 'none'}.`,
    warnings: [],
    next_recommended_tool: cockpit?.next_action?.action === 'add_evidence' ? 'resellos_add_machine_evidence' : 'resellos_run_machine_decision',
    audit: buildAudit('resellos_get_machine_cockpit', config.actor, { machine_id: machineId }),
  };
}

export async function updateMachineCandidate(
  client: ResellOSClient,
  input: {
    machine_id: string;
    name?: string;
    brand?: string;
    status?: string;
    price_new?: number;
    notes?: string;
    [key: string]: unknown;
  },
  config: AppConfig,
): Promise<ToolResult> {
  guardWriteEnabled(config);
  const machineId = ensureDefined(input.machine_id, 'machine_id');
  const { machine_id, ...payload } = input;
  const machine = await client.patch<any>(`/api/production/machines/${machineId}`, payload);
  return wrap('resellos_update_machine_candidate', config, input, machine, `Updated machine "${machine?.name ?? machineId}".`, 'resellos_get_machine_cockpit');
}

// ---------------------------------------------------------------------------
// Evidence
// ---------------------------------------------------------------------------

export async function addMachineEvidence(
  client: ResellOSClient,
  input: {
    machine_id: string;
    evidence_type: string;
    title?: string;
    url?: string;
    price?: number;
    source?: string;
    seller?: string;
    condition?: string;
    pros?: string;
    cons?: string;
    notes?: string;
  },
  config: AppConfig,
): Promise<ToolResult> {
  guardWriteEnabled(config);
  const machineId = ensureDefined(input.machine_id, 'machine_id');
  const payload = {
    evidence_type: ensureDefined(input.evidence_type, 'evidence_type'),
    title: input.title ?? undefined,
    url: input.url ?? undefined,
    price: input.price ?? undefined,
    source: input.source ?? undefined,
    seller: input.seller ?? undefined,
    condition: input.condition ?? undefined,
    pros: input.pros ?? undefined,
    cons: input.cons ?? undefined,
    notes: input.notes ?? undefined,
  };
  const evidence = await client.post<any>(`/api/production/machines/${machineId}/evidence`, payload);
  return wrap('resellos_add_machine_evidence', config, input, evidence, `Added ${input.evidence_type} evidence.`, 'resellos_get_machine_cockpit');
}

export async function verifyMachineEvidence(
  client: ResellOSClient,
  input: { machine_id: string; evidence_id: string; status?: string },
  config: AppConfig,
): Promise<ToolResult> {
  guardWriteEnabled(config);
  const { machine_id, evidence_id, status = 'USER_VERIFIED' } = input;
  const evidence = await client.patch<any>(
    `/api/production/machines/${machine_id}/evidence/${evidence_id}/verify`,
    { status },
  );
  return wrap('resellos_verify_machine_evidence', config, input, evidence, `Verified evidence as ${status}.`, 'resellos_get_machine_cockpit');
}

export async function rejectMachineEvidence(
  client: ResellOSClient,
  input: { machine_id: string; evidence_id: string; reason?: string },
  config: AppConfig,
): Promise<ToolResult> {
  guardWriteEnabled(config);
  const { machine_id, evidence_id, reason } = input;
  const result = await client.post<any>(
    `/api/production/machines/${machine_id}/evidence/${evidence_id}/reject`,
    { reason },
  );
  return wrap('resellos_reject_machine_evidence', config, input, result, `Rejected evidence.`, 'resellos_get_machine_cockpit');
}

// ---------------------------------------------------------------------------
// Product Families
// ---------------------------------------------------------------------------

export async function addMachineProductFamily(
  client: ResellOSClient,
  input: {
    machine_id: string;
    name: string;
    description?: string;
    material_cost_per_unit?: number;
    estimated_sale_price?: number;
    estimated_demand?: string;
    notes?: string;
  },
  config: AppConfig,
): Promise<ToolResult> {
  guardWriteEnabled(config);
  const machineId = ensureDefined(input.machine_id, 'machine_id');
  const payload = {
    name: ensureDefined(input.name, 'name'),
    description: input.description ?? undefined,
    material_cost_per_unit: input.material_cost_per_unit ?? undefined,
    estimated_sale_price: input.estimated_sale_price ?? undefined,
    estimated_demand: input.estimated_demand ?? undefined,
    notes: input.notes ?? undefined,
  };
  const family = await client.post<any>(`/api/production/machines/${machineId}/product-families`, payload);
  return wrap('resellos_add_machine_product_family', config, input, family, `Added product family "${family.name ?? input.name}".`, 'resellos_add_cost_scenario');
}

export async function updateMachineProductFamily(
  client: ResellOSClient,
  input: {
    machine_id: string;
    family_id: string;
    name?: string;
    description?: string;
    material_cost_per_unit?: number;
    estimated_sale_price?: number;
    estimated_demand?: string;
    status?: string;
    notes?: string;
  },
  config: AppConfig,
): Promise<ToolResult> {
  guardWriteEnabled(config);
  const { machine_id, family_id, ...payload } = input;
  const family = await client.patch<any>(`/api/production/machines/${machine_id}/product-families/${family_id}`, payload);
  return wrap('resellos_update_machine_product_family', config, input, family, `Updated product family "${family.name}".`, 'resellos_get_machine_cockpit');
}

export async function promoteMachineProductFamily(
  client: ResellOSClient,
  input: { machine_id: string; family_id: string },
  config: AppConfig,
): Promise<ToolResult> {
  guardWriteEnabled(config);
  const { machine_id, family_id } = input;
  const result = await client.post<any>(`/api/production/machines/${machine_id}/product-families/${family_id}/promote-to-product`);
  return wrap('resellos_promote_machine_product_family', config, input, result, `Promoted to idea ${result.idea_id}.`, 'resellos_get_product_cockpit');
}

// ---------------------------------------------------------------------------
// Cost Scenarios
// ---------------------------------------------------------------------------

export async function addCostScenario(
  client: ResellOSClient,
  input: {
    family_id: string;
    scenario_name: string;
    material_cost?: number;
    labor_cost?: number;
    sale_price?: number;
    units_per_month?: number;
    machine_purchase_price?: number;
    notes?: string;
  },
  config: AppConfig,
): Promise<ToolResult> {
  guardWriteEnabled(config);
  const familyId = ensureDefined(input.family_id, 'family_id');
  const payload = {
    scenario_name: ensureDefined(input.scenario_name, 'scenario_name'),
    material_cost: input.material_cost ?? undefined,
    labor_cost: input.labor_cost ?? undefined,
    sale_price: input.sale_price ?? undefined,
    units_per_month: input.units_per_month ?? undefined,
    machine_purchase_price: input.machine_purchase_price ?? undefined,
    notes: input.notes ?? undefined,
  };
  const scenario = await client.post<any>(`/api/production/product-families/${familyId}/cost-scenarios`, payload);
  return wrap('resellos_add_cost_scenario', config, input, scenario, `Added cost scenario "${input.scenario_name}".`, 'resellos_run_machine_decision');
}

// ---------------------------------------------------------------------------
// Decision
// ---------------------------------------------------------------------------

export async function runMachineDecision(
  client: ResellOSClient,
  input: { machine_id: string },
  config: AppConfig,
): Promise<ToolResult> {
  guardWriteEnabled(config);
  const machineId = ensureDefined(input.machine_id, 'machine_id');
  const decision = await client.post<any>(`/api/production/machines/${machineId}/decision`);
  return wrap('resellos_run_machine_decision', config, input, decision, `Decision: ${decision.recommendation} (confidence: ${decision.confidence}). ${decision.hard_blockers?.length ?? 0} blockers.`, null);
}

export async function getMachineNextAction(
  client: ResellOSClient,
  input: { machine_id: string },
  config: AppConfig,
): Promise<ToolResult> {
  const machineId = ensureDefined(input.machine_id, 'machine_id');
  const action = await client.get<any>(`/api/production/machines/${machineId}/next-action`);
  return {
    ok: true,
    data: action,
    summary: `Next action: ${action?.action ?? 'none'} — ${action?.reason ?? 'No action needed.'}`,
    warnings: [],
    next_recommended_tool: action?.action === 'add_evidence' ? 'resellos_add_machine_evidence' : action?.action === 'run_decision' ? 'resellos_run_machine_decision' : null,
    audit: buildAudit('resellos_get_machine_next_action', config.actor, input),
  };
}
