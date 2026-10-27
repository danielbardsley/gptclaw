import { createHash } from 'node:crypto';
import { lstatSync, readdirSync, readFileSync } from 'node:fs';
import path from 'node:path';
export function identity() {
  const id = process.env.GPTCLAW_PROJECT_ID;
  if (!id || id.length > 48 || !/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.test(id))
    throw new Error('Invalid project identity');
  return id;
}
export function inventory(root) {
  const result = {};
  function walk(folder, relative = '') {
    for (const name of readdirSync(folder).sort()) {
      const rel = relative ? `${relative}/${name}` : name;
      const file = path.join(folder, name);
      const info = lstatSync(file);
      if (info.isSymbolicLink()) throw new Error('Symlinks are unsupported');
      if (info.isDirectory()) walk(file, rel);
      else if (info.isFile())
        result[rel] = createHash('sha256')
          .update(readFileSync(file))
          .digest('hex');
      else throw new Error('Only regular export files are supported');
      if (Object.keys(result).length > 10000)
        throw new Error('Export exceeds file limit');
    }
  }
  walk(root);
  return result;
}
export function sourceDigest(root) {
  const hash = createHash('sha256');
  for (const name of [
    'app',
    'lib',
    'public',
    'scripts',
    'next.config.ts',
    'package.json',
    'pnpm-lock.yaml',
    'pnpm-workspace.yaml',
    'tsconfig.json',
  ]) {
    const file = path.join(root, name);
    if (lstatSync(file).isSymbolicLink())
      throw new Error('Source symlink refused');
    const files = lstatSync(file).isDirectory()
      ? inventory(file)
      : { '': createHash('sha256').update(readFileSync(file)).digest('hex') };
    hash.update(name + JSON.stringify(files));
  }
  return hash.digest('hex');
}
