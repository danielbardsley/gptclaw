const fs = require('node:fs');
const cp = require('node:child_process');
const action = process.argv[2];
process.env.CI = '1';
process.env.EXPO_NO_TELEMETRY = '1';
process.env.EXPO_NO_DOTENV = '1';
function run(command, args) {
  const result = cp.spawnSync(command, args, {
    stdio: 'inherit',
    timeout: 300000,
    env: process.env,
  });
  if (result.error || result.status !== 0) process.exit(1);
}
function sdk() {
  const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));
  const required = JSON.parse(fs.readFileSync('checks/sdk.json', 'utf8'));
  const actual = { ...pkg.dependencies, ...pkg.devDependencies };
  for (const [name, version] of Object.entries(required)) {
    if (actual[name] !== version)
      throw new Error('Unsupported SDK package selection');
  }
  for (const name of ['app.config.js', 'app.config.ts', 'android', 'ios']) {
    if (fs.existsSync(name))
      throw new Error('Unsupported dynamic/native configuration');
  }
}
function check(name) {
  if (name === 'format') run('pnpm', ['exec', 'prettier', '--write', '.']);
  else if (name === 'format-check')
    run('pnpm', ['exec', 'prettier', '--check', '.']);
  else if (name === 'lint')
    run('pnpm', ['exec', 'eslint', '.', '--max-warnings', '0']);
  else if (name === 'typecheck') run('pnpm', ['exec', 'tsc', '--noEmit']);
  else if (name === 'test') {
    run('pnpm', ['exec', 'jest', '--runInBand', '--coverage']);
    run('node', ['--test', 'checks/security.test.cjs']);
  } else if (name === 'sdk') sdk();
  else if (name === 'build') {
    sdk();
    for (const platform of ['ios', 'android'])
      run('pnpm', [
        'exec',
        'expo',
        'export',
        '--platform',
        platform,
        '--output-dir',
        '.gptclaw-build/' + platform,
      ]);
  } else if (name === 'security') {
    sdk();
    run('node', ['checks/security.cjs']);
  } else throw new Error('Unsupported quality action');
}
if (action === 'verify')
  for (const name of [
    'format-check',
    'lint',
    'typecheck',
    'test',
    'sdk',
    'security',
    'build',
  ])
    check(name);
else check(action);
