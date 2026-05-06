import type { AppConfig } from '../types.js';

function hasProof(input: { source_url?: string | null; screenshot_url?: string | null; verification_notes?: string | null }): boolean {
  return Boolean(input.source_url || input.screenshot_url || input.verification_notes);
}

export function guardVerificationApproval(config: AppConfig, input: { confirm?: boolean | null; source_url?: string | null; screenshot_url?: string | null; verification_notes?: string | null }): void {
  if (config.requireApprovalForVerification && !input.confirm) {
    throw new Error('Verification requires explicit confirmation.');
  }
  if (!hasProof(input)) {
    throw new Error('Verification requires source_url, screenshot_url, or verification_notes.');
  }
}

export function guardSupplierVerification(config: AppConfig, input: { confirm?: boolean | null; source_url?: string | null; screenshot_url?: string | null; verification_notes?: string | null; unit_cost?: number | null; estimated_landed_cost?: number | null }): void {
  guardVerificationApproval(config, input);
  if (input.unit_cost == null) {
    throw new Error('Supplier verification requires unit_cost.');
  }
  if (input.estimated_landed_cost == null && !input.verification_notes) {
    throw new Error('Supplier verification requires estimated_landed_cost or explicit shipping note.');
  }
}

export function guardSoldEvidenceVerification(config: AppConfig, input: { confirm?: boolean | null; source_url?: string | null; screenshot_url?: string | null; verification_notes?: string | null; price?: number | null }): void {
  guardVerificationApproval(config, input);
  if (input.price == null) {
    throw new Error('Evidence verification requires a price.');
  }
}
