import assert from 'node:assert/strict';
import test from 'node:test';
import { GET } from '../app/health/route.ts';
test('readiness fails when API is absent or unavailable', async () => {
  delete process.env.GPTCLAW_API_READY_URL;
  assert.equal((await GET()).status, 503);
  process.env.GPTCLAW_API_READY_URL = 'http://127.0.0.1:1/ready';
  assert.equal((await GET()).status, 503);
});
