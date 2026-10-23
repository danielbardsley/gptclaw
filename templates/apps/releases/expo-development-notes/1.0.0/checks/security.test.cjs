const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { evaluate, scanSource } = require('./security.cjs');
const policy = {
  schema_version: 1,
  scope: 'source-check-and-export',
  exceptions: [
    {
      id: 'GHSA-known',
      package: 'example',
      version: '1.0.0',
      owner: 'project owner',
      approved_at: '2026-10-13',
      expires_at: '2026-10-28T04:00:00Z',
    },
  ],
};
const audit = {
  advisories: {
    one: {
      github_advisory_id: 'GHSA-known',
      module_name: 'example',
      severity: 'high',
      findings: [{ version: '1.0.0' }],
    },
  },
  metadata: { vulnerabilities: { high: 1, critical: 0 } },
};
test('only the exact approved unexpired finding passes', () => {
  assert.deepEqual(
    evaluate(audit, policy, Date.parse('2026-10-13')).temporary_exceptions,
    ['GHSA-known'],
  );
  assert.throws(() =>
    evaluate(audit, policy, Date.parse('2026-10-28T04:00:00Z')),
  );
  const unknown = structuredClone(audit);
  unknown.advisories.one.github_advisory_id = 'GHSA-unknown';
  assert.throws(() => evaluate(unknown, policy, Date.parse('2026-10-13')));
  const version = structuredClone(audit);
  version.advisories.one.findings[0].version = '1.0.1';
  assert.throws(() => evaluate(version, policy, Date.parse('2026-10-13')));
  const critical = structuredClone(audit);
  critical.advisories.one.severity = 'critical';
  assert.throws(() => evaluate(critical, policy, Date.parse('2026-10-13')));
  assert.throws(() => evaluate({}, policy));
  const incomplete = structuredClone(audit);
  incomplete.metadata.vulnerabilities.high = 2;
  assert.throws(() => evaluate(incomplete, policy, Date.parse('2026-10-13')));
});
test('source secrets and symlinks are refused without logging contents', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'mobile-security-'));
  try {
    fs.writeFileSync(root + '/source.ts', 'ordinary source');
    scanSource(root);
    fs.writeFileSync(root + '/.env', 'synthetic');
    assert.throws(() => scanSource(root));
    fs.unlinkSync(root + '/.env');
    fs.symlinkSync(root + '/source.ts', root + '/linked');
    assert.throws(() => scanSource(root));
  } finally {
    fs.rmSync(root, { recursive: true });
  }
});
