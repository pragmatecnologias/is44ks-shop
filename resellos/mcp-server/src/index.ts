import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import { loadConfig } from './config.js';
import { ResellOSClient } from './resellosClient.js';
import { TOOL_DEFINITIONS } from './toolRegistry.js';
import { toErrorPayload } from './utils/errors.js';
import { createDiscoveryIdea, getDiscoveryBoard } from './tools/discoveryTools.js';
import { runDataForSeoGoogleShopping, pollExternalResearchJob } from './tools/externalResearchTools.js';
import { listEvidenceCandidates, approveCandidate, rejectCandidate, captureManualEvidence } from './tools/candidateTools.js';
import { getProductCockpit, runProductResearch, getNextResearchAction, generateProductResearchReport } from './tools/productTools.js';
import { verifyMarketplaceEvidence, verifySupplierSource, verifyCompetitorListing } from './tools/verificationTools.js';
import { quickScanSchema, researchTasksSchema, dataForSeoSchema, pollJobSchema, listCandidatesSchema, approveCandidateSchema, rejectCandidateSchema, captureManualEvidenceSchema, productCockpitSchema, productResearchSchema, nextActionSchema, verifyEvidenceSchema, verifySupplierSchema, verifyCompetitorSchema, productReportSchema, createDiscoveryIdeaSchema, discoveryBoardSchema } from './toolRegistry.js';
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
      const response = await client.post<any>('/api/discovery/quick-scan', input);
      return wrap('resellos_run_quick_scan', config, input, response, `Quick scan complete for ${input.idea_id}.`, 'resellos_generate_research_tasks');
    }
    case 'resellos_generate_research_tasks': {
      const input = researchTasksSchema.parse(args);
      const tasks = await client.post<any[]>(`/api/discovery/${input.idea_id}/tasks/generate`, {});
      return wrap('resellos_generate_research_tasks', config, input, { tasks }, `Generated ${tasks.length} research tasks.`, 'resellos_run_dataforseo_google_shopping');
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
