import type { AppConfig, VerifyInput, ToolResult } from '../types.js';
import { buildAudit } from '../utils/audit.js';
import { guardWriteEnabled } from '../guards/approvalGuards.js';
import { guardVerificationApproval, guardSupplierVerification, guardSoldEvidenceVerification } from '../guards/verificationGuards.js';
import type { ResellOSClient } from '../resellosClient.js';

export async function verifyMarketplaceEvidence(client: ResellOSClient, input: VerifyInput, config: AppConfig): Promise<ToolResult> {
  guardWriteEnabled(config);
  guardSoldEvidenceVerification(config, input);
  const response = await client.patch<any>(`/api/marketplace/evidence/detail/${input.id}/verify`, {
    verification_status: input.verification_status,
  });
  return {
    ok: true,
    data: response,
    summary: `Verified marketplace evidence ${input.id}.`,
    warnings: [],
    next_recommended_tool: 'resellos_get_product_cockpit',
    audit: buildAudit('resellos_verify_marketplace_evidence', config.actor, { id: input.id }),
  };
}

export async function verifySupplierSource(client: ResellOSClient, input: VerifyInput & { unit_cost?: number | null; estimated_landed_cost?: number | null }, config: AppConfig): Promise<ToolResult> {
  guardWriteEnabled(config);
  guardSupplierVerification(config, input);
  const response = await client.patch<any>(`/api/marketplace/sources/detail/${input.id}/verify`, {
    verification_status: input.verification_status,
  });
  return {
    ok: true,
    data: response,
    summary: `Verified supplier source ${input.id}.`,
    warnings: [],
    next_recommended_tool: 'resellos_get_product_cockpit',
    audit: buildAudit('resellos_verify_supplier_source', config.actor, { id: input.id }),
  };
}

export async function verifyCompetitorListing(client: ResellOSClient, input: VerifyInput, config: AppConfig): Promise<ToolResult> {
  guardWriteEnabled(config);
  guardVerificationApproval(config, input);
  const response = await client.patch<any>(`/api/marketplace/competitors/detail/${input.id}/verify`, {
    verification_status: input.verification_status,
  });
  return {
    ok: true,
    data: response,
    summary: `Verified competitor listing ${input.id}.`,
    warnings: [],
    next_recommended_tool: 'resellos_get_product_cockpit',
    audit: buildAudit('resellos_verify_competitor_listing', config.actor, { id: input.id }),
  };
}
