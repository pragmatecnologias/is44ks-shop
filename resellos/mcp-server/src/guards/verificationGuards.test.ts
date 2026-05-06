import test from 'node:test';
import assert from 'node:assert/strict';
import { guardVerificationApproval, guardSupplierVerification, guardSoldEvidenceVerification } from './verificationGuards.js';

const config = {
  requireApprovalForVerification: true,
} as const;

test('guardVerificationApproval requires proof and confirmation', () => {
  assert.throws(() => guardVerificationApproval(config as any, { confirm: false, source_url: null, screenshot_url: null, verification_notes: null }), /explicit confirmation/);
  assert.throws(() => guardVerificationApproval(config as any, { confirm: true, source_url: null, screenshot_url: null, verification_notes: null }), /requires source_url/);
});

test('guardSoldEvidenceVerification requires price and proof', () => {
  assert.throws(() => guardSoldEvidenceVerification(config as any, { confirm: true, source_url: 'https://example.com', verification_notes: 'ok', price: null }), /price/);
});

test('guardSupplierVerification requires unit cost and proof', () => {
  assert.throws(() => guardSupplierVerification(config as any, { confirm: true, source_url: 'https://example.com', verification_notes: 'ok', unit_cost: null, estimated_landed_cost: 2.5 }), /unit_cost/);
});
