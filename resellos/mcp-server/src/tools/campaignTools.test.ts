import test from 'node:test';
import assert from 'node:assert/strict';
import { TOOL_DEFINITIONS, addCampaignIdeaSchema, createCampaignSchema, createCampaignTaskSchema, updateCampaignTaskSchema } from '../toolRegistry.js';

test('create campaign schema accepts a minimal campaign payload', () => {
  const parsed = createCampaignSchema.parse({
    name: 'Pet accessories discovery',
    category: 'Pet accessories',
  });
  assert.equal(parsed.name, 'Pet accessories discovery');
  assert.equal(parsed.status, 'DRAFT');
});

test('create campaign task schema requires campaign_id and task fields', () => {
  const parsed = createCampaignTaskSchema.parse({
    campaign_id: '11111111-1111-4111-8111-111111111111',
    task_type: 'SCOUTING',
    title: 'Create first discovery ideas',
  });
  assert.equal(parsed.task_type, 'SCOUTING');
});

test('add idea schema requires a campaign_id', () => {
  assert.throws(() => addCampaignIdeaSchema.parse({ idea_name: 'Pet grooming glove' }), /campaign_id/);
});

test('update campaign task schema accepts task identifiers', () => {
  const parsed = updateCampaignTaskSchema.parse({
    campaign_id: '11111111-1111-4111-8111-111111111111',
    task_id: '22222222-2222-4222-8222-222222222222',
    status: 'DONE',
  });
  assert.equal(parsed.status, 'DONE');
});

test('campaign next tasks tool is registered', () => {
  assert.ok(TOOL_DEFINITIONS.some((tool) => tool.name === 'resellos_generate_campaign_next_tasks'));
});
