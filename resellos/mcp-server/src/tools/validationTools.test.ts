import test from 'node:test';
import assert from 'node:assert/strict';
import { TOOL_DEFINITIONS, addKeywordDemandSchema, addTrendResearchSchema, productValidationChecklistSchema } from '../toolRegistry.js';
import { addKeywordDemand, addTrendResearch, getProductValidationChecklist, verifyKeywordDemand, verifyTrendResearch } from './validationTools.js';

test('validation tools are registered', () => {
  assert.ok(TOOL_DEFINITIONS.some((tool) => tool.name === 'resellos_add_keyword_demand'));
  assert.ok(TOOL_DEFINITIONS.some((tool) => tool.name === 'resellos_add_trend_research'));
  assert.ok(TOOL_DEFINITIONS.some((tool) => tool.name === 'resellos_get_product_validation_checklist'));
  assert.equal(addKeywordDemandSchema.parse({ keyword: 'cat tunnel toy' }).keyword, 'cat tunnel toy');
  assert.equal(addTrendResearchSchema.parse({ keyword: 'cat tunnel toy' }).keyword, 'cat tunnel toy');
  assert.equal(productValidationChecklistSchema.parse({ product_id: '11111111-1111-4111-8111-111111111111' }).product_id, '11111111-1111-4111-8111-111111111111');
});

const config = {
  actor: 'codex-mcp',
  allowWrites: true,
  allowPaidTools: false,
  maxDataForSeoResults: 10,
  maxDataForSeoQueries: 1,
  requireApprovalForVerification: true,
  requireApprovalForPaidTools: true,
  mode: 'local',
  apiBaseUrl: 'http://localhost:8000',
  logLevel: 'info',
} as const;

test('addKeywordDemand posts to validation demand endpoint', async () => {
  const calls: Array<{ method: string; path: string; body?: unknown }> = [];
  const client = {
    post: async (path: string, body?: unknown) => {
      calls.push({ method: 'POST', path, body });
      return { id: 'demand-1', keyword: 'cat tunnel toy' };
    },
    get: async () => ({}),
    patch: async () => ({}),
  } as any;

  const result = await addKeywordDemand(client, { keyword: 'cat tunnel toy', product_id: '11111111-1111-4111-8111-111111111111' }, config);
  assert.equal(calls[0]?.path, '/api/validation/demand');
  assert.equal(result.ok, true);
});

test('verifyKeywordDemand requires proof before calling backend', async () => {
  let called = false;
  const client = { patch: async () => { called = true; return {}; } } as any;
  await assert.rejects(
    () => verifyKeywordDemand(client, { id: '11111111-1111-4111-8111-111111111111', verification_status: 'USER_VERIFIED', confirm: true }, config),
    undefined,
  );
  assert.equal(called, false);
});

test('addTrendResearch posts to validation trends endpoint', async () => {
  const calls: Array<{ method: string; path: string; body?: unknown }> = [];
  const client = {
    post: async (path: string, body?: unknown) => {
      calls.push({ method: 'POST', path, body });
      return { id: 'trend-1', keyword: 'cat tunnel toy' };
    },
    get: async () => ({}),
    patch: async () => ({}),
  } as any;

  const result = await addTrendResearch(client, { keyword: 'cat tunnel toy', product_id: '11111111-1111-4111-8111-111111111111' }, config);
  assert.equal(calls[0]?.path, '/api/validation/trends');
  assert.equal(result.ok, true);
});

test('getProductValidationChecklist uses the checklist endpoint', async () => {
  const client = {
    get: async (path: string) => {
      assert.equal(path, '/api/validation/products/11111111-1111-4111-8111-111111111111/checklist');
      return { product_id: '11111111-1111-4111-8111-111111111111' };
    },
    post: async () => ({}),
    patch: async () => ({}),
  } as any;
  const result = await getProductValidationChecklist(client, '11111111-1111-4111-8111-111111111111', config);
  assert.equal(result.ok, true);
});

test('verifyTrendResearch requires proof before calling backend', async () => {
  let called = false;
  const client = { patch: async () => { called = true; return {}; } } as any;
  await assert.rejects(
    () => verifyTrendResearch(client, { id: '11111111-1111-4111-8111-111111111111', verification_status: 'USER_VERIFIED', confirm: true }, config),
    undefined,
  );
  assert.equal(called, false);
});
