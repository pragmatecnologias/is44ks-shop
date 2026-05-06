import test from 'node:test';
import assert from 'node:assert/strict';
import { TOOL_DEFINITIONS, shopConceptSchema, portfolioItemSchema, productCollectionSchema, shopPortfolioReportSchema } from '../toolRegistry.js';
import { addPortfolioItem, createProductCollection, createShopConcept, getShopConcept, getShopPortfolioReport, listShopConcepts, updatePortfolioItem, updateProductCollection, updateShopConcept } from './portfolioTools.js';

test('portfolio tools are registered', () => {
  assert.ok(TOOL_DEFINITIONS.some((tool) => tool.name === 'resellos_create_shop_concept'));
  assert.ok(TOOL_DEFINITIONS.some((tool) => tool.name === 'resellos_add_portfolio_item'));
  assert.ok(TOOL_DEFINITIONS.some((tool) => tool.name === 'resellos_get_shop_portfolio_report'));
  assert.equal(shopConceptSchema.parse({ name: 'Practical Pet Home' }).name, 'Practical Pet Home');
  assert.equal(productCollectionSchema.parse({ shop_concept_id: '11111111-1111-4111-8111-111111111111', name: 'Pet Hair Cleanup' }).name, 'Pet Hair Cleanup');
  assert.equal(portfolioItemSchema.parse({ shop_concept_id: '11111111-1111-4111-8111-111111111111', idea_id: '22222222-2222-4222-8222-222222222222' }).idea_id, '22222222-2222-4222-8222-222222222222');
  assert.equal(shopPortfolioReportSchema.parse({ shop_id: '11111111-1111-4111-8111-111111111111' }).shop_id, '11111111-1111-4111-8111-111111111111');
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

test('createShopConcept posts to portfolio shops endpoint', async () => {
  const calls: Array<{ method: string; path: string; body?: unknown }> = [];
  const client = {
    post: async (path: string, body?: unknown) => {
      calls.push({ method: 'POST', path, body });
      return { id: 'shop-1', name: 'Practical Pet Home' };
    },
    get: async () => ([]),
    patch: async () => ({}),
  } as any;
  const result = await createShopConcept(client, { name: 'Practical Pet Home' }, config);
  assert.equal(calls[0]?.path, '/api/portfolio/shops');
  assert.equal(result.ok, true);
});

test('createProductCollection posts to portfolio collection endpoint', async () => {
  const calls: Array<{ method: string; path: string; body?: unknown }> = [];
  const client = {
    post: async (path: string, body?: unknown) => {
      calls.push({ method: 'POST', path, body });
      return { id: 'collection-1', name: 'Pet Hair Cleanup' };
    },
    get: async () => ([]),
    patch: async () => ({}),
  } as any;
  const result = await createProductCollection(client, { shop_concept_id: '11111111-1111-4111-8111-111111111111', name: 'Pet Hair Cleanup' }, config);
  assert.equal(calls[0]?.path, '/api/portfolio/shops/11111111-1111-4111-8111-111111111111/collections');
  assert.equal(result.ok, true);
});

test('addPortfolioItem posts to portfolio item endpoint', async () => {
  const calls: Array<{ method: string; path: string; body?: unknown }> = [];
  const client = {
    post: async (path: string, body?: unknown) => {
      calls.push({ method: 'POST', path, body });
      return { id: 'item-1', idea_name: 'Pet feeding mat' };
    },
    get: async () => ([]),
    patch: async () => ({}),
  } as any;
  const result = await addPortfolioItem(client, { shop_concept_id: '11111111-1111-4111-8111-111111111111', idea_id: '22222222-2222-4222-8222-222222222222' }, config);
  assert.equal(calls[0]?.path, '/api/portfolio/shops/11111111-1111-4111-8111-111111111111/items');
  assert.equal(result.ok, true);
});

test('getShopConcept reads the shop detail endpoint', async () => {
  const client = {
    get: async (path: string) => {
      assert.equal(path, '/api/portfolio/shops/11111111-1111-4111-8111-111111111111');
      return { shop_concept: { id: '11111111-1111-4111-8111-111111111111', name: 'Practical Pet Home' } };
    },
    post: async () => ({}),
    patch: async () => ({}),
  } as any;
  const result = await getShopConcept(client, '11111111-1111-4111-8111-111111111111', config);
  assert.equal(result.ok, true);
});

test('getShopPortfolioReport reads the shop report endpoint', async () => {
  const client = {
    get: async (path: string) => {
      assert.equal(path, '/api/portfolio/shops/11111111-1111-4111-8111-111111111111/report');
      return { shop_concept_id: '11111111-1111-4111-8111-111111111111', shop_concept_name: 'Practical Pet Home' };
    },
    post: async () => ({}),
    patch: async () => ({}),
  } as any;
  const result = await getShopPortfolioReport(client, '11111111-1111-4111-8111-111111111111', config);
  assert.equal(result.ok, true);
});

test('updateShopConcept and updateProductCollection patch the correct endpoints', async () => {
  const calls: string[] = [];
  const client = {
    get: async () => ({}),
    post: async () => ({}),
    patch: async (path: string) => {
      calls.push(path);
      return { id: path };
    },
  } as any;

  await updateShopConcept(client, { shop_id: '11111111-1111-4111-8111-111111111111', status: 'ACTIVE' }, config);
  await updateProductCollection(client, { collection_id: '22222222-2222-4222-8222-222222222222', status: 'ACTIVE' }, config);
  await updatePortfolioItem(client, { item_id: '33333333-3333-4333-8333-333333333333', status: 'RESEARCHING' }, config);

  assert.deepEqual(calls, [
    '/api/portfolio/shops/11111111-1111-4111-8111-111111111111',
    '/api/portfolio/collections/22222222-2222-4222-8222-222222222222',
    '/api/portfolio/items/33333333-3333-4333-8333-333333333333',
  ]);
});

test('listShopConcepts returns the portfolio list endpoint', async () => {
  const client = {
    get: async (path: string) => {
      assert.equal(path, '/api/portfolio/shops');
      return [{ id: 'shop-1', name: 'Practical Pet Home' }];
    },
    post: async () => ({}),
    patch: async () => ({}),
  } as any;
  const result = await listShopConcepts(client, config);
  assert.equal(result.ok, true);
});
