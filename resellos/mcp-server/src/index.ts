import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import { loadConfig } from './config.js';
import { ResellOSClient } from './resellosClient.js';
import { TOOL_DEFINITIONS } from './toolRegistry.js';
import { toErrorPayload } from './utils/errors.js';
import { createDiscoveryIdea, getDiscoveryBoard, runQuickScan } from './tools/discoveryTools.js';
import { createDiscoveryCampaign, listDiscoveryCampaigns, getDiscoveryCampaign, createCampaignTask, updateCampaignTask, getCampaignReport, generateCampaignNextTasks, addIdeaToCampaign, getCampaignNextTask, completeCampaignTask, blockCampaignTask } from './tools/campaignTools.js';
import { runDataForSeoGoogleShopping, pollExternalResearchJob } from './tools/externalResearchTools.js';
import { listEvidenceCandidates, approveCandidate, rejectCandidate, captureManualEvidence } from './tools/candidateTools.js';
import { addKeywordDemand, listKeywordDemand, verifyKeywordDemand, addTrendResearch, listTrendResearch, verifyTrendResearch, getProductValidationChecklist, runProductValidation } from './tools/validationTools.js';
import { getProductCockpit, runProductResearch, getNextResearchAction, generateProductResearchReport } from './tools/productTools.js';
import { verifyMarketplaceEvidence, verifySupplierSource, verifyCompetitorListing } from './tools/verificationTools.js';
import { quickScanSchema, researchTasksSchema, dataForSeoSchema, pollJobSchema, listCandidatesSchema, approveCandidateSchema, rejectCandidateSchema, captureManualEvidenceSchema, productCockpitSchema, productResearchSchema, nextActionSchema, verifyEvidenceSchema, verifySupplierSchema, verifyCompetitorSchema, productReportSchema, createDiscoveryIdeaSchema, discoveryBoardSchema, createCampaignSchema, campaignIdSchema, createCampaignTaskSchema, updateCampaignTaskSchema, addCampaignIdeaSchema, getCampaignNextTaskSchema, completeCampaignTaskSchema, blockCampaignTaskSchema, addKeywordDemandSchema, listKeywordDemandSchema, verifyKeywordDemandSchema, addTrendResearchSchema, listTrendResearchSchema, verifyTrendResearchSchema, productValidationChecklistSchema, runProductValidationSchema } from './toolRegistry.js';
import { guardWriteEnabled } from './guards/approvalGuards.js';
import type { ToolResult } from './types.js';
import type { z } from 'zod';
import { ResellosApiError } from './utils/errors.js';
import type { AppConfig } from './types.js';

const config = loadConfig();
const client = new ResellOSClient(config.apiBaseUrl);

const server = new Server(
  {
    name: 'resellos-mcp-server',
    version: '0.1.0',
  },
  {
    capabilities: {
      tools: {},
    },
  },
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: TOOL_DEFINITIONS.map((tool) => ({
    name: tool.name,
    description: tool.description,
    inputSchema: tool.jsonSchema,
  })),
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const name = request.params.name;
  const args = request.params.arguments ?? {};
  try {
    const result = await invokeTool(name, args, config, client);
    return {
      content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
      isError: false,
    };
  } catch (error) {
    const payload = toErrorPayload(error);
    return {
      content: [{ type: 'text', text: JSON.stringify(payload, null, 2) }],
      isError: true,
    };
  }
});

async function invokeTool(name: string, args: Record<string, unknown>, config: AppConfig, client: ResellOSClient): Promise<ToolResult> {
  switch (name) {
    case 'resellos_get_discovery_board': {
      const input = discoveryBoardSchema.parse(args);
      return getDiscoveryBoard(client, input, config);
    }
    case 'resellos_create_discovery_idea': {
      const input = createDiscoveryIdeaSchema.parse(args);
      return createDiscoveryIdea(client, input, config);
    }
    case 'resellos_run_quick_scan': {
      const input = quickScanSchema.parse(args);
      return runQuickScan(client, input, config);
    }
    case 'resellos_generate_research_tasks': {
      const input = researchTasksSchema.parse(args);
      const tasks = await client.post<any[]>(`/api/discovery/${input.idea_id}/tasks/generate`, {});
      return wrap('resellos_generate_research_tasks', config, input, { tasks }, `Generated ${tasks.length} research tasks.`, 'resellos_run_dataforseo_google_shopping');
    }
    case 'resellos_create_discovery_campaign': {
      const input = createCampaignSchema.parse(args);
      return createDiscoveryCampaign(client, input, config);
    }
    case 'resellos_list_discovery_campaigns': {
      return listDiscoveryCampaigns(client, config);
    }
    case 'resellos_get_discovery_campaign': {
      const input = campaignIdSchema.parse(args);
      return getDiscoveryCampaign(client, input.campaign_id, config);
    }
    case 'resellos_create_campaign_task': {
      const input = createCampaignTaskSchema.parse(args);
      return createCampaignTask(client, input, config);
    }
    case 'resellos_update_campaign_task': {
      const input = updateCampaignTaskSchema.parse(args);
      return updateCampaignTask(client, input, config);
    }
    case 'resellos_get_campaign_report': {
      const input = campaignIdSchema.parse(args);
      return getCampaignReport(client, input.campaign_id, config);
    }
    case 'resellos_generate_campaign_next_tasks': {
      const input = campaignIdSchema.parse(args);
      return generateCampaignNextTasks(client, input.campaign_id, config);
    }
    case 'resellos_add_idea_to_campaign': {
      const input = addCampaignIdeaSchema.parse(args);
      return addIdeaToCampaign(client, input, config);
    }
    case 'resellos_run_dataforseo_google_shopping': {
      const input = dataForSeoSchema.parse(args);
      return runDataForSeoGoogleShopping(client, input, config);
    }
    case 'resellos_poll_external_research_job': {
      const input = pollJobSchema.parse(args);
      return pollExternalResearchJob(client, input.job_id, config);
    }
    case 'resellos_list_evidence_candidates': {
      const input = listCandidatesSchema.parse(args);
      return listEvidenceCandidates(client, input, config);
    }
    case 'resellos_approve_candidate': {
      const input = approveCandidateSchema.parse(args);
      return approveCandidate(client, input, config);
    }
    case 'resellos_reject_candidate': {
      const input = rejectCandidateSchema.parse(args);
      return rejectCandidate(client, input, config);
    }
    case 'resellos_capture_manual_evidence': {
      const input = captureManualEvidenceSchema.parse(args);
      return captureManualEvidence(client, input, config);
    }
    case 'resellos_get_product_cockpit': {
      const input = productCockpitSchema.parse(args);
      return getProductCockpit(client, input.product_id, config);
    }
    case 'resellos_run_product_research': {
      const input = productResearchSchema.parse(args);
      return runProductResearch(client, input.product_id, config);
    }
    case 'resellos_get_next_research_action': {
      const input = nextActionSchema.parse(args);
      return getNextResearchAction(client, input.product_id, config);
    }
    case 'resellos_verify_marketplace_evidence': {
      const input = verifyEvidenceSchema.parse(args);
      return verifyMarketplaceEvidence(client, input, config);
    }
    case 'resellos_verify_supplier_source': {
      const input = verifySupplierSchema.parse(args);
      return verifySupplierSource(client, input as any, config);
    }
    case 'resellos_verify_competitor_listing': {
      const input = verifyCompetitorSchema.parse(args);
      return verifyCompetitorListing(client, input, config);
    }
    case 'resellos_generate_product_research_report': {
      const input = productReportSchema.parse(args);
      return generateProductResearchReport(client, input.product_id, config);
    }
    case 'resellos_add_keyword_demand': {
      const input = addKeywordDemandSchema.parse(args);
      return addKeywordDemand(client, input, config);
    }
    case 'resellos_list_keyword_demand': {
      const input = listKeywordDemandSchema.parse(args);
      return listKeywordDemand(client, input, config);
    }
    case 'resellos_verify_keyword_demand': {
      const input = verifyKeywordDemandSchema.parse(args);
      return verifyKeywordDemand(client, input, config);
    }
    case 'resellos_add_trend_research': {
      const input = addTrendResearchSchema.parse(args);
      return addTrendResearch(client, input, config);
    }
    case 'resellos_list_trend_research': {
      const input = listTrendResearchSchema.parse(args);
      return listTrendResearch(client, input, config);
    }
    case 'resellos_verify_trend_research': {
      const input = verifyTrendResearchSchema.parse(args);
      return verifyTrendResearch(client, input, config);
    }
    case 'resellos_get_product_validation_checklist': {
      const input = productValidationChecklistSchema.parse(args);
      return getProductValidationChecklist(client, input.product_id, config);
    }
    case 'resellos_run_product_validation': {
      const input = runProductValidationSchema.parse(args);
      return runProductValidation(client, input.product_id, config);
    }
    case 'resellos_get_campaign_next_task': {
      const input = getCampaignNextTaskSchema.parse(args);
      return getCampaignNextTask(client, input.campaign_id, config);
    }
    case 'resellos_complete_campaign_task': {
      const input = completeCampaignTaskSchema.parse(args);
      return completeCampaignTask(client, input, config);
    }
    case 'resellos_block_campaign_task': {
      const input = blockCampaignTaskSchema.parse(args);
      return blockCampaignTask(client, input, config);
    }
    default:
      throw new Error(`Unknown tool: ${name}`);
  }
}

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
    audit: {
      actor: config.actor,
      tool,
      timestamp: new Date().toISOString(),
      product_id: input.product_id ? String(input.product_id) : null,
      idea_id: input.idea_id ? String(input.idea_id) : null,
      campaign_id: input.campaign_id ? String(input.campaign_id) : null,
      cost_estimate: null,
    },
  };
}

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((error) => {
  console.error('ResellOS MCP server failed to start:', error);
  process.exit(1);
});
