import { z } from 'zod';
import type { AppConfig } from './types.js';

const envSchema = z.object({
  RESELLOS_API_BASE_URL: z.string().default('http://localhost:8000'),
  RESELLOS_MCP_ACTOR: z.string().default('codex-mcp'),
  RESELLOS_MCP_MODE: z.string().default('local'),
  RESELLOS_MCP_ALLOW_WRITES: z.string().default('true'),
  RESELLOS_MCP_ALLOW_PAID_TOOLS: z.string().default('false'),
  RESELLOS_MCP_MAX_DATAFORSEO_RESULTS: z.string().default('10'),
  RESELLOS_MCP_MAX_DATAFORSEO_QUERIES: z.string().default('1'),
  RESELLOS_MCP_REQUIRE_APPROVAL_FOR_VERIFICATION: z.string().default('true'),
  RESELLOS_MCP_REQUIRE_APPROVAL_FOR_PAID_TOOLS: z.string().default('true'),
  RESELLOS_MCP_LOG_LEVEL: z.string().default('info'),
});

export function loadConfig(env: NodeJS.ProcessEnv = process.env): AppConfig {
  const parsed = envSchema.parse(env);
  return {
    apiBaseUrl: parsed.RESELLOS_API_BASE_URL.replace(/\/$/, ''),
    actor: parsed.RESELLOS_MCP_ACTOR,
    mode: parsed.RESELLOS_MCP_MODE,
    allowWrites: parsed.RESELLOS_MCP_ALLOW_WRITES !== 'false',
    allowPaidTools: parsed.RESELLOS_MCP_ALLOW_PAID_TOOLS === 'true',
    maxDataForSeoResults: Number(parsed.RESELLOS_MCP_MAX_DATAFORSEO_RESULTS) || 10,
    maxDataForSeoQueries: Number(parsed.RESELLOS_MCP_MAX_DATAFORSEO_QUERIES) || 1,
    requireApprovalForVerification: parsed.RESELLOS_MCP_REQUIRE_APPROVAL_FOR_VERIFICATION !== 'false',
    requireApprovalForPaidTools: parsed.RESELLOS_MCP_REQUIRE_APPROVAL_FOR_PAID_TOOLS !== 'false',
    logLevel: parsed.RESELLOS_MCP_LOG_LEVEL,
  };
}
