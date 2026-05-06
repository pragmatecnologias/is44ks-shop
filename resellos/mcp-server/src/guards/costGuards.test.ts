import test from 'node:test';
import assert from 'node:assert/strict';
import { guardDataForSeoRequest, guardQueries } from './costGuards.js';

const config = {
  maxDataForSeoResults: 10,
  maxDataForSeoQueries: 1,
} as const;

test('guardQueries allows a single non-empty query', () => {
  assert.equal(guardQueries(config as any, ['pet hair remover roller']), 'pet hair remover roller');
});

test('guardQueries rejects multiple queries', () => {
  assert.throws(() => guardQueries(config as any, ['a', 'b']), /Only 1 query/);
});

test('guardDataForSeoRequest rejects max results above config', () => {
  assert.throws(() => guardDataForSeoRequest(config as any, 'pet hair remover roller', 11), /<= 10/);
});
