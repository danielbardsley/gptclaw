import test from 'node:test';
import assert from 'node:assert/strict';
import { duration, statusFreshness, type ServiceStatus } from '../lib/status.ts';
const status: ServiceStatus = { state:'ready',provider_state:'ready',health:'healthy',operation_busy:false,freshness:'current',last_success_at:100 };
test('freshness ages with elapsed time, failures and clock anomalies', () => {
  assert.equal(statusFreshness(status,100,0), 'current');
  assert.equal(statusFreshness(status,100,31), 'stale');
  assert.equal(statusFreshness(status,90,0), 'stale');
  assert.equal(statusFreshness(status,100,0,true), 'stale');
  assert.equal(statusFreshness({...status,last_success_at:null},100,0), 'unavailable');
});
test('zero uptime remains measured and null is unavailable', () => {
  assert.equal(duration(0),'0s');
  assert.equal(duration(3661),'1h 1m');
  assert.equal(duration(null),'Unavailable');
});
