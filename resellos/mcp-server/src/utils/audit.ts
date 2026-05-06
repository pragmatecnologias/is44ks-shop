import type { ToolResult } from '../types.js';

export function buildAudit(tool: string, actor: string, input: Record<string, unknown>, costEstimate?: number | null): ToolResult['audit'] {
  return {
    actor,
    tool,
    timestamp: new Date().toISOString(),
    product_id: input.product_id ? String(input.product_id) : null,
    idea_id: input.idea_id ? String(input.idea_id) : null,
    cost_estimate: typeof costEstimate === 'number' ? costEstimate : null,
  };
}
