import assert from 'node:assert/strict';
import { randomBytes } from 'node:crypto';
import {
  mkdtempSync,
  mkdirSync,
  writeFileSync,
  rmSync,
  symlinkSync,
} from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { request } from 'node:http';
import { test } from 'node:test';
import { inventory } from '../scripts/export.mjs';
import { staticServer, verifiedExport } from '../scripts/serve.mjs';
import { checkOutput } from '../scripts/check-output.mjs';
function fixture() {
  const root = mkdtempSync(path.join(tmpdir(), 'static-test-'));
  const out = path.join(root, 'out');
  mkdirSync(out);
  writeFileSync(
    path.join(out, 'index.html'),
    '<h1 id="main">Example</h1><a href="/projects/test-site/guide/#section">Guide</a><script src="/projects/test-site/app.js"></script>',
  );
  mkdirSync(path.join(out, 'guide'));
  writeFileSync(
    path.join(out, 'guide/index.html'),
    '<h1 id="section">Guide</h1>',
  );
  writeFileSync(path.join(out, '404.html'), '<h1>Page not found</h1>');
  writeFileSync(path.join(out, 'app.js'), 'console.log("local asset");');
  complete(root);
  return root;
}
function complete(root) {
  rmSync(path.join(root, 'out/.gptclaw-build.json'), { force: true });
  writeFileSync(
    path.join(root, 'out/.gptclaw-build.json'),
    JSON.stringify({
      schema_version: 1,
      project_id: 'test-site',
      source_digest: 'fixture',
      files: inventory(path.join(root, 'out')),
    }),
  );
}
function get(port, url, method = 'GET') {
  return new Promise((resolve, reject) => {
    const req = request(
      { hostname: '127.0.0.1', port, path: url, method },
      (res) => {
        const chunks = [];
        res.on('data', (d) => chunks.push(d));
        res.on('end', () =>
          resolve({
            status: res.statusCode,
            headers: res.headers,
            body: Buffer.concat(chunks).toString(),
          }),
        );
      },
    );
    req.on('error', reject);
    req.end();
  });
}
test('HTTP prefix, files, 404, HEAD, health, escapes and methods', async () => {
  const root = fixture();
  const server = staticServer(root, 'test-site', { checkSource: false });
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  const port = server.address().port;
  try {
    for (const url of [
      '/projects/test-site/',
      '/projects/test-site/guide/',
      '/projects/test-site/app.js',
      '/projects/test-site/_gptclaw/ready',
    ])
      assert.equal((await get(port, url)).status, 200);
    assert.match(
      (await get(port, '/projects/test-site/app.js')).headers['content-type'],
      /javascript/,
    );
    assert.equal((await get(port, '/projects/test-site/', 'HEAD')).body, '');
    assert.equal((await get(port, '/projects/test-site/guide')).status, 308);
    const missing = await get(port, '/projects/test-site/unknown/');
    assert.equal(missing.status, 404);
    assert.match(missing.body, /Page not found/);
    for (const url of [
      '/',
      '/projects/other/',
      '/projects/test-site/.gptclaw-build.json',
      '/projects/test-site/%2e%2e/secret',
      '/projects/test-site/%252e%252e/secret',
      '/projects/test-site/%5csecret',
      '/projects/test-site/%zz',
      '/projects/test-site/%00',
    ])
      assert.ok((await get(port, url)).status >= 400, url);
    assert.equal((await get(port, '/projects/test-site/', 'POST')).status, 405);
    symlinkSync(
      path.join(root, 'out/index.html'),
      path.join(root, 'out/linked.html'),
    );
    assert.equal(
      (await get(port, '/projects/test-site/linked.html')).status,
      404,
    );
    rmSync(path.join(root, 'out/.gptclaw-build.json'));
    assert.equal(
      (await get(port, '/projects/test-site/_gptclaw/ready')).status,
      503,
    );
  } finally {
    await new Promise((resolve) => server.close(resolve));
    rmSync(root, { recursive: true, force: true });
  }
});
test('completion refuses wrong identity, altered output and symlinks', () => {
  const root = fixture();
  try {
    assert.throws(() => verifiedExport(root, 'other', false));
    writeFileSync(path.join(root, 'out/app.js'), 'altered');
    assert.throws(() => verifiedExport(root, 'test-site', false));
    complete(root);
    symlinkSync('/tmp', path.join(root, 'out/escape'));
    assert.throws(() => verifiedExport(root, 'test-site', false));
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});
test('crawler refuses broken links/fragments, remote assets and excess budgets', () => {
  const root = fixture();
  const out = path.join(root, 'out');
  try {
    assert.equal(checkOutput(out, 'test-site').pages.length, 3);
    for (const value of [
      '/projects/test-site/missing/',
      '/projects/test-site/guide/#absent',
      '/projects/other/',
    ]) {
      writeFileSync(
        path.join(out, 'index.html'),
        `<a href="${value}">Broken</a>`,
      );
      assert.throws(() => checkOutput(out, 'test-site'));
    }
    writeFileSync(
      path.join(out, 'index.html'),
      '<img src="https://example.invalid/image.png" alt="External" />',
    );
    assert.throws(() => checkOutput(out, 'test-site'));
    writeFileSync(
      path.join(out, 'index.html'),
      '<script src="/projects/test-site/app.js"></script>',
    );
    writeFileSync(path.join(out, 'app.js'), randomBytes(350 * 1024));
    assert.throws(() => checkOutput(out, 'test-site'), /budget/);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});
