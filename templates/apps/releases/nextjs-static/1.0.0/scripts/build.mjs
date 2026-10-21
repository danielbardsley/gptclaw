import {
  cpSync,
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  renameSync,
  rmSync,
  symlinkSync,
  writeFileSync,
} from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { identity, inventory, sourceDigest } from './export.mjs';
const root = process.cwd();
const id = identity();
const completion = path.join(root, 'out/.gptclaw-build.json');
// Invalidate old output before any fallible build; a failure cannot become ready.
rmSync(completion, { force: true });
const before = sourceDigest(root);
mkdirSync('.static-build', { recursive: true });
const stage = mkdtempSync(path.join(root, '.static-build/export-'));
try {
  for (const name of [
    'app',
    'lib',
    'public',
    'next.config.ts',
    'tsconfig.json',
    'next-env.d.ts',
    'package.json',
  ])
    cpSync(path.join(root, name), path.join(stage, name), { recursive: true });
  symlinkSync(
    path.join(root, 'node_modules'),
    path.join(stage, 'node_modules'),
    'dir',
  );
  const child = spawnSync(
    process.execPath,
    [path.join(root, 'node_modules/next/dist/bin/next'), 'build', '--webpack'],
    {
      cwd: stage,
      stdio: 'inherit',
      timeout: 240000,
      env: { ...process.env, NEXT_TELEMETRY_DISABLED: '1' },
    },
  );
  if (child.error || child.status !== 0)
    throw new Error('Static export failed');
  const output = path.join(stage, 'out');
  if (existsSync(path.join(output, '_gptclaw')))
    throw new Error('Reserved health path collision');
  for (const name of [
    'index.html',
    '404.html',
    'guide/getting-started/index.html',
  ]) {
    if (
      !readFileSync(path.join(output, name), 'utf8').includes(`/projects/${id}`)
    )
      throw new Error('Required exported page or identity missing');
  }
  const files = inventory(output);
  if (before !== sourceDigest(root))
    throw new Error('Source changed during build');
  writeFileSync(
    path.join(output, '.gptclaw-build.json'),
    JSON.stringify({
      schema_version: 1,
      project_id: id,
      source_digest: before,
      files,
    }) + '\n',
  );
  rmSync(path.join(root, 'out'), { recursive: true, force: true });
  renameSync(output, path.join(root, 'out'));
  console.log('Completed static export for ' + id);
} finally {
  rmSync(stage, { recursive: true, force: true });
}
