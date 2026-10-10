import assert from 'node:assert/strict';
import test from 'node:test';
import { GET } from '../app/api/health/route.ts';
test('health identifies the selected application without credentials', async () => {
  process.env.GPTCLAW_PROJECT_ID = 'health-test';
  const response = GET();
  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), { status: 'ok', project: 'health-test' });
});
