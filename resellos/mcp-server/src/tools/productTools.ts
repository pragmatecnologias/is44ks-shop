import type { AppConfig, ToolResult } from '../types.js';
import { buildAudit } from '../utils/audit.js';
import type { ResellOSClient } from '../resellosClient.js';
import { guardWriteEnabled } from '../guards/approvalGuards.js';

export async function getProductCockpit(client: ResellOSClient, productId: string, config: AppConfig): Promise<ToolResult> {
  const cockpit = await client.get<any>(`/api/products/${productId}/research/cockpit`);
  return {
    ok: true,
    data: cockpit,
    summary: `Loaded cockpit for product ${productId}.`,
    warnings: [],
    next_recommended_tool: 'resellos_get_next_research_action',
    audit: buildAudit('resellos_get_product_cockpit', config.actor, { product_id: productId }),
  };
}

export async function runProductResearch(client: ResellOSClient, productId: string, config: AppConfig): Promise<ToolResult> {
  guardWriteEnabled(config);
  const response = await client.post<any>(`/api/products/${productId}/research/run`, {});
  return {
    ok: true,
    data: response,
    summary: `Ran product research for ${productId}.`,
    warnings: [],
    next_recommended_tool: 'resellos_get_product_cockpit',
    audit: buildAudit('resellos_run_product_research', config.actor, { product_id: productId }),
  };
}

export async function getNextResearchAction(client: ResellOSClient, productId: string, config: AppConfig): Promise<ToolResult> {
  const cockpit = await client.get<any>(`/api/products/${productId}/research/cockpit`);
  const decision = cockpit?.decision ?? {};
  const buyReadiness = cockpit?.buy_readiness ?? {};
  const product = cockpit?.product ?? {};
  const verifiedSold = Number(buyReadiness.verified_sold_evidence_count ?? 0);
  const verifiedActive = Number(buyReadiness.verified_active_evidence_count ?? 0);
  const verifiedSupplier = String(cockpit?.sources?.find((source: any) => source.verification_status === 'USER_VERIFIED')?.verification_status || '').toUpperCase() === 'USER_VERIFIED';
  const verifiedCompetitorCount = Number(cockpit?.competition?.verified_competitor_count ?? 0);
  const evidenceComplete = verifiedSold >= 5 && verifiedActive >= 5 && verifiedSupplier && verifiedCompetitorCount >= 3;
  const blocker = String(decision.main_blocker || '').trim();
  const nextAction = String(decision.next_action || '').trim() || 'Review cockpit and rerun research.';
  const missingOrWeak = evidenceComplete
    ? [
        blocker || 'Opportunity score below sample-buy threshold',
        'Improve supplier landed cost',
        'Validate active price signal',
        'Sharpen competitor angle',
      ].filter(Boolean)
    : [
        verifiedSold < 5 ? 'Add verified sold evidence' : null,
        verifiedActive < 5 ? 'Add verified active evidence' : null,
        !verifiedSupplier ? 'Verify supplier source' : null,
        verifiedCompetitorCount < 3 ? 'Verify competitor listings' : null,
      ].filter(Boolean);

  return {
    ok: true,
    data: {
      product_id: productId,
      decision: decision.recommendation || product.final_decision || product.status || 'UNKNOWN',
      next_action: evidenceComplete && nextAction ? nextAction : 'Collect more verified evidence.',
      missing_or_weak: missingOrWeak,
    },
    summary: evidenceComplete
      ? `Evidence gates are complete. Next action: ${nextAction || 'review economics and competition.'}`
      : `Evidence gates are incomplete. ${missingOrWeak.join('; ')}`,
    warnings: evidenceComplete ? [] : ['Verified gates are still incomplete.'],
    next_recommended_tool: 'resellos_get_product_cockpit',
    audit: buildAudit('resellos_get_next_research_action', config.actor, { product_id: productId }),
  };
}

export async function generateProductResearchReport(client: ResellOSClient, productId: string, config: AppConfig): Promise<ToolResult> {
  const cockpit = await client.get<any>(`/api/products/${productId}/research/cockpit`);
  const decision = cockpit?.decision ?? {};
  const report = `# Product Research Report\n\nProduct: ${cockpit?.product?.name ?? productId}\nDecision: ${decision.recommendation ?? cockpit?.product?.final_decision ?? 'UNKNOWN'}\nReadiness: ${decision.buy_readiness_status ?? 'UNKNOWN'}\nNext action: ${decision.next_action ?? 'None'}\n`;
  return {
    ok: true,
    data: { report, cockpit },
    summary: `Generated product research report for ${productId}.`,
    warnings: [],
    next_recommended_tool: 'resellos_get_product_cockpit',
    audit: buildAudit('resellos_generate_product_research_report', config.actor, { product_id: productId }),
  };
}
