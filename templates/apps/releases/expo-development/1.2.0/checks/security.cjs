const fs = require('node:fs');
const cp = require('node:child_process');

function evaluate(audit, policy, now = Date.now()) {
  if (
    !audit ||
    !audit.advisories ||
    typeof audit.advisories !== 'object' ||
    Array.isArray(audit.advisories) ||
    !audit.metadata?.vulnerabilities
  )
    throw new Error('Required audit evidence unavailable');
  if (
    policy.schema_version !== 1 ||
    policy.scope !== 'source-check-and-export' ||
    !Array.isArray(policy.exceptions)
  )
    throw new Error('Invalid advisory policy');
  const counts = { high: 0, critical: 0 };
  const accepted = [];
  for (const finding of Object.values(audit.advisories)) {
    if (
      !['info', 'low', 'moderate', 'high', 'critical'].includes(
        finding.severity,
      ) ||
      !Array.isArray(finding.findings) ||
      finding.findings.length === 0
    )
      throw new Error('Invalid advisory evidence');
    if (!['high', 'critical'].includes(finding.severity)) continue;
    counts[finding.severity] += 1;
    const exception = policy.exceptions.find(
      (entry) =>
        entry.id === finding.github_advisory_id &&
        entry.package === finding.module_name,
    );
    if (
      !exception ||
      finding.severity !== 'high' ||
      !Number.isFinite(Date.parse(exception.expires_at)) ||
      now >= Date.parse(exception.expires_at) ||
      exception.owner !== 'project owner' ||
      !exception.approved_at
    )
      throw new Error('Unaccepted high/critical advisory or expired exception');
    if (finding.findings.some((item) => item.version !== exception.version))
      throw new Error('Advisory version outside accepted scope');
    accepted.push(exception.id);
  }
  for (const severity of ['high', 'critical'])
    if (counts[severity] !== audit.metadata.vulnerabilities[severity])
      throw new Error('Incomplete advisory evidence');
  return {
    vulnerabilities: audit.metadata.vulnerabilities,
    temporary_exceptions: accepted,
    expires_at: policy.exceptions.map((entry) => entry.expires_at),
  };
}
function scanSource(root = '.') {
  let entries = 0;
  function walk(path) {
    for (const entry of fs.readdirSync(path, { withFileTypes: true })) {
      if (++entries > 4096) throw new Error('Source scan bound exceeded');
      if (
        [
          '.git',
          '.gptclaw',
          'node_modules',
          '.cache',
          '.expo',
          '.gptclaw-cache',
          '.gptclaw-build',
          'coverage',
        ].includes(entry.name)
      )
        continue;
      if (entry.isSymbolicLink())
        throw new Error('Source symlink is unsupported');
      const file = path + '/' + entry.name;
      if (entry.isDirectory()) walk(file);
      else if (entry.isFile()) {
        if (
          entry.name === '.env' ||
          entry.name.startsWith('.env.') ||
          /\.(p12|keystore|mobileprovision)$/.test(entry.name)
        )
          throw new Error('Credential material in source');
        const info = fs.statSync(file);
        if (info.size > 2 * 1024 * 1024)
          throw new Error('Source file bound exceeded');
        const text = fs.readFileSync(file, 'utf8');
        if (
          /AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9_]{20,}|tskey-(auth|api)-[A-Za-z0-9-]{10,}/.test(
            text,
          )
        )
          throw new Error('Credential-shaped source content');
      }
    }
  }
  walk(root);
}
function run() {
  scanSource();
  const result = cp.spawnSync('pnpm', ['audit', '--json'], {
    encoding: 'utf8',
    timeout: 60000,
    maxBuffer: 1024 * 1024,
  });
  if (result.error || ![0, 1].includes(result.status))
    throw new Error('Required advisory lookup failed');
  const value = evaluate(
    JSON.parse(result.stdout),
    JSON.parse(fs.readFileSync('checks/advisory-policy.json', 'utf8')),
  );
  console.log(JSON.stringify(value));
}
module.exports = { evaluate, scanSource };
if (require.main === module) run();
