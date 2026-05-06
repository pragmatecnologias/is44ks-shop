import test from 'node:test';
import assert from 'node:assert/strict';
import { runQuickScan } from './discoveryTools.js';

test('runQuickScan uses the existing-idea quick-scan endpoint', async () => {
  const calls: Array<{ method: string; path: string; body?: unknown }> = [];
  const client = {
    get: async () => ({ idea_name: 'Reusable pet hair remover roller' }),
    post: async (path: string, body?: unknown) => {
      calls.push({ method: 'POST', path, body });
      return {
        idea: { id: 'idea-1' },
        quick_scan_verdict: 'NEEDS_MARKET_CHECK',
        quick_scan_reason: 'ok',
        research_priority: 'MEDIUM',
        research_completeness_score: 12,
        discovery_completeness_score: 12,
        opportunity_score: 12,
        buy_readiness_status: 'NOT_READY',
        tasks: [],
      };
    },
  } as any;

  const result = await runQuickScan(client, { idea_id: 'idea-1' }, { actor: 'codex-mcp', allowWrites: true, allowPaidTools: false, maxDataForSeoResults: 10, maxDataForSeoQueries: 1, requireApprovalForVerification: true, requireApprovalForPaidTools: true, mode: 'local', apiBaseUrl: 'http://localhost:8000', logLevel: 'info' });
  const data = result.data as any;

  assert.equal(calls.length, 1);
  assert.equal(calls[0].path, '/api/discovery/idea-1/quick-scan');
  assert.deepEqual(calls[0].body, {});
  assert.equal(data.original_idea_id, 'idea-1');
  assert.equal(data.scanned_idea?.id, 'idea-1');
});
