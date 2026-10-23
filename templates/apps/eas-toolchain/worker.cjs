// Trusted wrapper for eas-cli 25.3.0. Never execute a project-supplied CLI/config.
const fs = require('node:fs');
const crypto = require('node:crypto');
const cp = require('node:child_process');
const root = '/opt/eas/node_modules/eas-cli';
if (require(root + '/package.json').version !== '25.3.0') process.exit(2);
const mode = process.argv[2];
const job = process.argv[3];
if (!['submit', 'observe', 'cancel'].includes(mode)) process.exit(2);
if (mode !== 'submit' && !/^[a-f0-9-]{36}$/.test(job || '')) process.exit(2);
// The archive is prepared and inspected before this process can receive a token.
if (mode === 'submit') {
  const data = fs.readFileSync('/input/archive.tar.gz');
  const expected = fs.readFileSync('/input/archive.sha256', 'utf8').trim();
  if (crypto.createHash('sha256').update(data).digest('hex') !== expected) process.exit(2);
  const repository = require(root + '/build/build/utils/repository.js');
  if (typeof repository.makeProjectTarballAsync !== 'function') process.exit(2);
  repository.makeProjectTarballAsync = async () => {
    const path = '/tmp/gptclaw-exact-upload.tar.gz';
    fs.writeFileSync(path, data, { mode: 0o600, flag: 'wx' });
    return { path, size: data.length };
  };
}
const token = fs.readFileSync('/run/secrets/expo-token', 'utf8').trim();
if (!/^[A-Za-z0-9_.-]{16,4096}$/.test(token)) process.exit(2);
process.env.EXPO_TOKEN = token;
if (mode === 'submit') {
  // A reused account must not inject account/project variables into this build.
  // Capture only; never relay variable values to logs or source.
  for (const scope of ['project', 'shared']) {
    const check = cp.spawnSync(process.execPath, [root + '/bin/run', 'env:list',
      'development', '--scope', scope, '--format', 'short'], {
      encoding: 'utf8', timeout: 60000, maxBuffer: 65536,
      env: process.env, stdio: ['ignore', 'pipe', 'pipe'],
    });
    const clean = (check.stdout || '').replace(/\u001b\[[0-9;]*m/g, '').trim();
    if (check.error || check.status !== 0 || clean !== 'Environment: development\nNo variables found for this environment.') {
      process.exit(2);
    }
  }
}

// All local configuration is bounded static JSON, with exact reviewed plugins;
// arbitrary app.config files and lifecycle hooks are refused by the planner.
process.argv = [process.execPath, root + '/bin/run', ...(mode === 'submit'
  ? ['build', '--platform', 'android', '--profile', 'development', '--non-interactive', '--no-wait', '--json', '--message', process.argv[4]]
  : mode === 'observe' ? ['build:view', job, '--json'] : ['build:cancel', job, '--non-interactive'])];
require(root + '/bin/run');
