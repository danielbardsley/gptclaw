const assert = require('node:assert/strict');
const fs = require('node:fs');
const { NotesClient } = require('./api/client.js');
(async () => {
  const apiUrl = process.env.GPTCLAW_COMPAT_URL;
  const client = new NotesClient({ enabled: true, profile: 'development', contractVersion: 1, apiUrl });
  let ready = false;
  for (let attempt = 0; attempt < 60; attempt++) {
    try { await client.list(); ready = true; break; } catch { await new Promise(resolve => setTimeout(resolve, 500)); }
  }
  assert(ready, 'Owned API fixture did not become ready');
  const startupMs = Date.now() - Number(process.env.QLT_START_MS);
  const schema = await (await fetch(apiUrl + '/openapi.json', { redirect: 'error' })).json();
  assert(schema.paths['/api/v1/notes']);
  const origin = new URL(apiUrl).origin;
  const prefix = new URL(apiUrl).pathname.replace(/\/api$/, '');
  assert.deepEqual(schema.servers, [{ url: prefix }]);
  const docs = await fetch(apiUrl + '/docs', { redirect: 'error' }); assert.equal(docs.status, 200);
  const scripts = [...(await docs.text()).matchAll(/src=["']([^"']+)["']/g)].map(v => v[1]);
  assert(scripts.length);
  for (const path of scripts) {
    const asset = new URL(path, apiUrl + '/docs'); assert.equal(asset.origin, origin); assert(asset.pathname.startsWith(prefix + '/'));
    assert.equal((await fetch(asset, { redirect: 'error' })).status, 200);
  }
  const warmup = process.env.QUALITY_BENCHMARK === '1' ? 30000 : 250;
  await client.list(); await new Promise(resolve => setTimeout(resolve, warmup));
  const samples = [];
  for (let run = 0; run < 3; run++) {
    const times = [];
    for (let request = 0; request < 200; request++) {
      const start = performance.now(); await client.list(); times.push(performance.now() - start);
    }
    times.sort((a, b) => a - b); samples.push(times[Math.ceil(times.length * .95) - 1]);
  }
  samples.sort((a, b) => a - b);
  fs.writeFileSync('/output/http-sample.json', JSON.stringify({ startup_ms: startupMs, latency_ms: samples[1], run_p95_ms: samples, warmup_ms: warmup, requests_per_run: 200, repetitions: 3, driver: 'retained Node notes client; preinitialized disposable PostgreSQL' }));
  console.log('Owned prefixed API/docs/assets and bounded retained-client latency trial passed.');
})().catch(error => { console.error(error.message); process.exit(1); });
