const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const crypto = require('node:crypto');
const worker = fs.readFileSync('/provider/worker.cjs', 'utf8');
function run({ dirty = false, mismatch = false } = {}) {
  const data = Buffer.from('synthetic archive');
  const repository = { makeProjectTarballAsync: async () => { throw new Error('Unexpected archive recreation'); } };
  const writes = [];
  const state = { calls: 0 };
  const process = { argv: ['node', 'worker', 'submit', '', 'synthetic-operation'], env: {},
    execPath: '/usr/local/bin/node', exit: (code) => { throw new Error('exit:' + code); } };
  const context = { process, Buffer, require: (name) => {
    if (name === 'node:crypto') return crypto;
    if (name === 'node:child_process') return { spawnSync: () => {
      state.calls++;
      return { status: 0, stdout: dirty ? 'Environment: development\nSERVER_KEY=must-not-forward' : 'Environment: development\nNo variables found for this environment.\n' };
    } };
    if (name === 'node:fs') return { readFileSync: (path) => {
      if (path.endsWith('.tar.gz')) return data;
      if (path.endsWith('.sha256')) return mismatch ? '0'.repeat(64) : crypto.createHash('sha256').update(data).digest('hex');
      return 'synthetic-credential-canary';
    }, writeFileSync: (path, bytes) => writes.push({ path, bytes }) };
    if (name.endsWith('/package.json')) return { version: '25.3.0' };
    if (name.endsWith('/repository.js')) return repository;
    if (name.endsWith('/bin/run')) { state.argv = process.argv; return {}; }
    throw new Error('Unexpected module');
  } };
  vm.runInNewContext(worker, context);
  return { state, repository, data, writes };
}
test('submits exact inspected bytes and explicit development profile', async () => {
  const result = run();
  assert.equal(result.state.calls, 2);
  const archive = await result.repository.makeProjectTarballAsync();
  assert.equal(archive.size, result.data.length);
  assert.deepEqual(result.writes[0].bytes, result.data);
  assert.ok(result.state.argv.includes('--no-wait'));
  assert.ok(result.state.argv.includes('development'));
  assert.ok(!result.state.argv.some(x => x.includes('synthetic-credential')));
});
test('archive tampering fails before loading EAS or a credential', () => {
  assert.throws(() => run({ mismatch: true }), /exit:2/);
});
test('inherited environment variables fail closed without relaying values', () => {
  assert.throws(() => run({ dirty: true }), /exit:2/);
});
