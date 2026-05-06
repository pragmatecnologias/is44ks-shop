import { z } from 'zod';

export type ToolName =
  | 'resellos_get_discovery_board'
  | 'resellos_create_discovery_idea'
  | 'resellos_run_quick_scan'
  | 'resellos_generate_research_tasks'
  | 'resellos_create_discovery_campaign'
  | 'resellos_get_discovery_campaign'
  | 'resellos_list_discovery_campaigns'
  | 'resellos_create_campaign_task'
  | 'resellos_update_campaign_task'
  | 'resellos_get_campaign_report'
  | 'resellos_generate_campaign_next_tasks'
  | 'resellos_add_idea_to_campaign'
  | 'resellos_run_dataforseo_google_shopping'
  | 'resellos_poll_external_research_job'
  | 'resellos_list_evidence_candidates'
  | 'resellos_approve_candidate'
  | 'resellos_reject_candidate'
  | 'resellos_capture_manual_evidence'
  | 'resellos_get_product_cockpit'
  | 'resellos_run_product_research'
  | 'resellos_get_next_research_action'
  | 'resellos_verify_marketplace_evidence'
  | 'resellos_verify_supplier_source'
  | 'resellos_verify_competitor_listing'
  | 'resellos_generate_product_research_report'
  | 'resellos_get_campaign_next_task'
  | 'resellos_complete_campaign_task'
  | 'resellos_block_campaign_task';

export interface ToolDefinition {
  name: ToolName;
  description: string;
  inputSchema: z.ZodTypeAny;
  jsonSchema: Record<string, unknown>;
}

export const discoveryBoardSchema = z.object({
  include_archived: z.boolean().default(false),
  category: z.string().trim().min(1).optional(),
});

export const createDiscoveryIdeaSchema = z.object({
  idea_name: z.string().min(1),
  category: z.string().optional(),
  source_platform: z.string().optional(),
  source_url: z.string().optional(),
  rough_supplier_cost: z.number().nullable().optional(),
  estimated_landed_cost: z.number().nullable().optional(),
  why_interesting: z.string().optional(),
  marketplace_observation: z.string().optional(),
  notes: z.string().optional(),
});

export const quickScanSchema = z.object({
  idea_id: z.string().uuid(),
});

export const researchTasksSchema = z.object({
  idea_id: z.string().uuid(),
});

export const createCampaignSchema = z.object({
  name: z.string().min(1),
  category: z.string().optional(),
  goal: z.string().optional(),
  constraints_json: z.record(z.string(), z.unknown()).default({}),
  budget_limit_usd: z.number().positive().default(25),
  max_ideas: z.number().int().positive().default(10),
  max_products_to_promote: z.number().int().positive().default(3),
  status: z.enum(['DRAFT', 'RUNNING', 'PAUSED', 'COMPLETED']).default('DRAFT'),
  created_by: z.string().optional(),
});

export const campaignIdSchema = z.object({
  campaign_id: z.string().uuid(),
});

export const createCampaignTaskSchema = z.object({
  campaign_id: z.string().uuid(),
  task_type: z.string().min(1),
  title: z.string().min(1),
  description: z.string().optional(),
  status: z.enum(['TODO', 'IN_PROGRESS', 'DONE', 'BLOCKED', 'SKIPPED']).default('TODO'),
  related_idea_id: z.string().uuid().optional(),
  related_product_id: z.string().uuid().optional(),
  related_candidate_id: z.string().uuid().optional(),
  result_json: z.record(z.string(), z.unknown()).optional(),
  error_message: z.string().optional(),
});

export const updateCampaignTaskSchema = z.object({
  campaign_id: z.string().uuid(),
  task_id: z.string().uuid(),
}).merge(
  createCampaignTaskSchema.partial().omit({ campaign_id: true }),
);

export const addCampaignIdeaSchema = createDiscoveryIdeaSchema.extend({
  campaign_id: z.string().uuid(),
});

export const dataForSeoSchema = z.object({
  idea_id: z.string().uuid().optional(),
  product_id: z.string().uuid().optional(),
  query: z.string().min(1),
  max_results: z.number().int().positive().max(10).default(10),
  confirm: z.boolean().optional(),
});

export const pollJobSchema = z.object({
  job_id: z.string().uuid(),
});

export const listCandidatesSchema = z.object({
  idea_id: z.string().uuid().optional(),
  product_id: z.string().uuid().optional(),
  job_id: z.string().uuid().optional(),
  review_status: z.enum(['PENDING', 'APPROVED', 'REJECTED', 'IGNORED']).optional(),
});

export const approveCandidateSchema = z.object({
  candidate_id: z.string().uuid(),
  approve_as: z.enum(['MARKETPLACE_EVIDENCE', 'COMPETITOR_LISTING', 'SUPPLIER_SOURCE']),
  task_id: z.string().uuid().optional(),
  product_id: z.string().uuid().optional(),
  notes: z.string().optional(),
  confirm: z.boolean().optional(),
});

export const rejectCandidateSchema = z.object({
  candidate_id: z.string().uuid(),
  reason: z.string().optional(),
});

export const captureManualEvidenceSchema = z.object({
  idea_id: z.string().uuid().optional(),
  product_id: z.string().uuid().optional(),
  task_id: z.string().uuid().optional(),
  capture_type: z.enum(['MARKETPLACE_SCREENSHOT', 'SUPPLIER_SCREENSHOT', 'COMPETITOR_SCREENSHOT', 'VISUAL_RISK']),
  url: z.string().optional(),
  pasted_text: z.string().optional(),
  notes: z.string().optional(),
});

export const productCockpitSchema = z.object({
  product_id: z.string().uuid(),
});

export const productResearchSchema = z.object({
  product_id: z.string().uuid(),
});

export const nextActionSchema = z.object({
  product_id: z.string().uuid(),
});

export const verifyEvidenceSchema = z.object({
  id: z.string().uuid(),
  verification_status: z.literal('USER_VERIFIED'),
  source_url: z.string().optional(),
  screenshot_url: z.string().optional(),
  verification_notes: z.string().min(1),
  confirm: z.boolean().optional(),
});

export const verifySupplierSchema = z.object({
  id: z.string().uuid(),
  verification_status: z.literal('USER_VERIFIED'),
  source_url: z.string().optional(),
  screenshot_url: z.string().optional(),
  verification_notes: z.string().min(1),
  confirm: z.boolean().optional(),
});

export const verifyCompetitorSchema = z.object({
  id: z.string().uuid(),
  verification_status: z.literal('USER_VERIFIED'),
  source_url: z.string().optional(),
  screenshot_url: z.string().optional(),
  verification_notes: z.string().min(1),
  confirm: z.boolean().optional(),
});

export const productReportSchema = z.object({
  product_id: z.string().uuid(),
  format: z.enum(['markdown']).default('markdown'),
  include_agent_outputs: z.boolean().default(true),
});

export const getCampaignNextTaskSchema = z.object({
  campaign_id: z.string().uuid(),
});

export const completeCampaignTaskSchema = z.object({
  campaign_id: z.string().uuid(),
  task_id: z.string().uuid(),
  result_json: z.record(z.string(), z.unknown()).optional(),
  notes: z.string().optional(),
});

export const blockCampaignTaskSchema = z.object({
  campaign_id: z.string().uuid(),
  task_id: z.string().uuid(),
  error_message: z.string().min(1),
});

export const TOOL_DEFINITIONS: ToolDefinition[] = [
  {
    name: 'resellos_get_discovery_board',
    description: 'Read the current discovery ideas, opportunity board, and research queue.',
    inputSchema: discoveryBoardSchema,
    jsonSchema: z.toJSONSchema(discoveryBoardSchema) as Record<string, unknown>,
  },
  {
    name: 'resellos_create_discovery_idea',
    description: 'Create a new discovery idea through ResellOS.',
    inputSchema: createDiscoveryIdeaSchema,
    jsonSchema: z.toJSONSchema(createDiscoveryIdeaSchema) as Record<string, unknown>,
  },
  { name: 'resellos_run_quick_scan', description: 'Run a quick scan for a discovery idea.', inputSchema: quickScanSchema, jsonSchema: z.toJSONSchema(quickScanSchema) as Record<string, unknown> },
  { name: 'resellos_generate_research_tasks', description: 'Generate category-specific research tasks for an idea.', inputSchema: researchTasksSchema, jsonSchema: z.toJSONSchema(researchTasksSchema) as Record<string, unknown> },
  { name: 'resellos_create_discovery_campaign', description: 'Create a controlled discovery campaign.', inputSchema: createCampaignSchema, jsonSchema: z.toJSONSchema(createCampaignSchema) as Record<string, unknown> },
  { name: 'resellos_get_discovery_campaign', description: 'Read a discovery campaign and its current report snapshot.', inputSchema: campaignIdSchema, jsonSchema: z.toJSONSchema(campaignIdSchema) as Record<string, unknown> },
  { name: 'resellos_list_discovery_campaigns', description: 'List all discovery campaigns.', inputSchema: z.object({}).strict(), jsonSchema: z.toJSONSchema(z.object({}).strict()) as Record<string, unknown> },
  { name: 'resellos_create_campaign_task', description: 'Create a task within a discovery campaign.', inputSchema: createCampaignTaskSchema, jsonSchema: z.toJSONSchema(createCampaignTaskSchema) as Record<string, unknown> },
  { name: 'resellos_update_campaign_task', description: 'Update a discovery campaign task.', inputSchema: updateCampaignTaskSchema, jsonSchema: z.toJSONSchema(updateCampaignTaskSchema) as Record<string, unknown> },
  { name: 'resellos_get_campaign_report', description: 'Generate or read the current campaign report.', inputSchema: campaignIdSchema, jsonSchema: z.toJSONSchema(campaignIdSchema) as Record<string, unknown> },
  { name: 'resellos_generate_campaign_next_tasks', description: 'Generate the next suggested tasks for a discovery campaign.', inputSchema: campaignIdSchema, jsonSchema: z.toJSONSchema(campaignIdSchema) as Record<string, unknown> },
  { name: 'resellos_add_idea_to_campaign', description: 'Create a new discovery idea inside a campaign.', inputSchema: addCampaignIdeaSchema, jsonSchema: z.toJSONSchema(addCampaignIdeaSchema) as Record<string, unknown> },
  { name: 'resellos_run_dataforseo_google_shopping', description: 'Run one controlled Google Shopping DataForSEO query.', inputSchema: dataForSeoSchema, jsonSchema: z.toJSONSchema(dataForSeoSchema) as Record<string, unknown> },
  { name: 'resellos_poll_external_research_job', description: 'Poll a DataForSEO job and import candidates when ready.', inputSchema: pollJobSchema, jsonSchema: z.toJSONSchema(pollJobSchema) as Record<string, unknown> },
  { name: 'resellos_list_evidence_candidates', description: 'List pending or filtered evidence candidates.', inputSchema: listCandidatesSchema, jsonSchema: z.toJSONSchema(listCandidatesSchema) as Record<string, unknown> },
  { name: 'resellos_approve_candidate', description: 'Approve an evidence candidate into a real app record.', inputSchema: approveCandidateSchema, jsonSchema: z.toJSONSchema(approveCandidateSchema) as Record<string, unknown> },
  { name: 'resellos_reject_candidate', description: 'Reject an evidence candidate.', inputSchema: rejectCandidateSchema, jsonSchema: z.toJSONSchema(rejectCandidateSchema) as Record<string, unknown> },
  { name: 'resellos_capture_manual_evidence', description: 'Capture manual evidence as a candidate.', inputSchema: captureManualEvidenceSchema, jsonSchema: z.toJSONSchema(captureManualEvidenceSchema) as Record<string, unknown> },
  { name: 'resellos_get_product_cockpit', description: 'Read the product cockpit and current research state.', inputSchema: productCockpitSchema, jsonSchema: z.toJSONSchema(productCockpitSchema) as Record<string, unknown> },
  { name: 'resellos_run_product_research', description: 'Run the product research pipeline.', inputSchema: productResearchSchema, jsonSchema: z.toJSONSchema(productResearchSchema) as Record<string, unknown> },
  { name: 'resellos_get_next_research_action', description: 'Return the next research action for a product.', inputSchema: nextActionSchema, jsonSchema: z.toJSONSchema(nextActionSchema) as Record<string, unknown> },
  { name: 'resellos_verify_marketplace_evidence', description: 'Verify marketplace evidence with proof.', inputSchema: verifyEvidenceSchema, jsonSchema: z.toJSONSchema(verifyEvidenceSchema) as Record<string, unknown> },
  { name: 'resellos_verify_supplier_source', description: 'Verify a supplier source with proof.', inputSchema: verifySupplierSchema, jsonSchema: z.toJSONSchema(verifySupplierSchema) as Record<string, unknown> },
  { name: 'resellos_verify_competitor_listing', description: 'Verify a competitor listing with proof.', inputSchema: verifyCompetitorSchema, jsonSchema: z.toJSONSchema(verifyCompetitorSchema) as Record<string, unknown> },
  { name: 'resellos_generate_product_research_report', description: 'Generate a markdown research report for a product.', inputSchema: productReportSchema, jsonSchema: z.toJSONSchema(productReportSchema) as Record<string, unknown> },
  { name: 'resellos_get_campaign_next_task', description: 'Get the next pending task for a campaign.', inputSchema: getCampaignNextTaskSchema, jsonSchema: z.toJSONSchema(getCampaignNextTaskSchema) as Record<string, unknown> },
  { name: 'resellos_complete_campaign_task', description: 'Mark a campaign task as complete with results.', inputSchema: completeCampaignTaskSchema, jsonSchema: z.toJSONSchema(completeCampaignTaskSchema) as Record<string, unknown> },
  { name: 'resellos_block_campaign_task', description: 'Block a campaign task with an error message.', inputSchema: blockCampaignTaskSchema, jsonSchema: z.toJSONSchema(blockCampaignTaskSchema) as Record<string, unknown> },
];
