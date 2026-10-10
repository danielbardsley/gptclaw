// Trusted build helper. No project source or package scripts execute here.
const fs = require('node:fs');
const https = require('node:https');
const crypto = require('node:crypto');
const {execFileSync} = require('node:child_process');
const profile = JSON.parse(fs.readFileSync('/tmp/profile.json', 'utf8'));
if (process.version !== `v${profile.versions.node}`) throw Error('Node version mismatch');
const req = https.get(profile.pnpm_artifact.url, response => {
  if (response.statusCode !== 200) {response.resume(); throw Error('Artifact unavailable');}
  const chunks = []; let size = 0;
  response.on('data', chunk => {
    size += chunk.length;
    if (size > 16 * 1024 * 1024) {response.destroy(); throw Error('Artifact too large');}
    chunks.push(chunk);
  });
  response.on('end', () => {
    const bytes = Buffer.concat(chunks);
    const integrity = 'sha512-' + crypto.createHash('sha512').update(bytes).digest('base64');
    if (integrity !== profile.pnpm_artifact.integrity) throw Error('Artifact integrity mismatch');
    fs.writeFileSync('/tmp/pnpm.tgz', bytes, {flag: 'wx', mode: 0o600});
    execFileSync('npm', ['install', '--global', '--offline', '--ignore-scripts', '--no-audit', '--no-fund', '/tmp/pnpm.tgz'], {stdio: 'inherit', timeout: 60000});
    if (execFileSync('pnpm', ['--version'], {encoding: 'utf8', timeout: 10000}).trim() !== profile.versions.pnpm) throw Error('pnpm version mismatch');
    fs.writeFileSync('/usr/local/share/gptclaw-toolchain.json', JSON.stringify({versions: profile.versions, artifact_integrity: integrity}));
    fs.unlinkSync('/tmp/pnpm.tgz');
  });
});
req.setTimeout(60000, () => req.destroy(Error('Artifact timeout')));
req.on('error', error => {throw error;});
