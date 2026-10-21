const assert = require('node:assert/strict');
const { chromium } = require('playwright-core');
const fs = require('node:fs');
(async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage({ reducedMotion: 'reduce' });
    page.on('pageerror', error => console.error('Page error:', error.message));
    page.on('console', message => { if (message.type() === 'error') console.error('Page console:', message.text()); });
    const prefix = '/projects/quality-fixture';
    const base = 'http://service:' + process.env.QUALITY_PORT + prefix;
    const ready = base + (process.env.QUALITY_KIND === 'web' ? '/api/health/' : '/ready');
    let available = false;
    for (let i = 0; i < 120; i++) {
      try { if ((await page.request.get(ready, { maxRedirects: 0 })).ok()) { available = true; break; } } catch {}
      await new Promise(resolve => setTimeout(resolve, 500));
    }
    assert.ok(available, 'Readiness deadline exceeded');
    const startupMs = Date.now() - Number(process.env.QUALITY_START_MS);
    if (process.env.QUALITY_KIND === 'web') {
      const response = await page.goto(base + '/');
      await page.waitForLoadState('networkidle');
      assert.equal(response.status(), 200);
      await page.addScriptTag({ path: '/checks/axe.min.js' });
      const result = await page.evaluate(async () => axe.run(document, { runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'] } }));
      assert.deepEqual(result.violations.map(v => ({ id: v.id, nodes: v.nodes.length })), [], 'Accessibility violations');
      const button = page.getByRole('button', { name: 'Say hello · 0', exact: true });
      await button.focus(); await page.keyboard.press('Enter');
      await page.getByRole('button', { name: 'Say hello · 1', exact: true }).waitFor();
      assert.ok(await page.locator('script[src]').count() > 0, 'Missing application assets');
      for (const path of await page.locator('script[src]').evaluateAll(nodes => nodes.map(n => n.src))) {
        assert.equal(new URL(path).origin, 'http://service:' + process.env.QUALITY_PORT);
        assert.equal((await page.request.get(path, { maxRedirects: 0 })).status(), 200);
      }
      for (const width of [390, 1280]) {
        await page.setViewportSize({ width, height: 900 });
        await page.evaluate(() => { document.documentElement.style.fontSize = '200%'; });
        assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'Zoom/narrow layout overflow');
        assert.ok(await page.getByRole('button', { name: 'Say hello · 1' }).isVisible());
      }
    } else {
      const schema = await page.request.get(base + '/openapi.json', { maxRedirects: 0 });
      assert.equal(schema.status(), 200); const contract = await schema.json();
      assert.ok(contract.paths['/api/v1/examples']);
      assert.deepEqual(contract.servers, [{ url: prefix }], 'API docs must retain the owned project prefix');
      const example = await page.request.get(base + '/api/v1/examples?limit=1', { maxRedirects: 0 });
      assert.equal(example.status(), 200); assert.ok((await example.json()).items.length);
      const docsPath = process.env.QUALITY_KIND === 'fastapi' ? '/docs' : '/docs/';
      const docs = await page.request.get(base + docsPath, { maxRedirects: 0 });
      assert.equal(docs.status(), 200);
      const html = await docs.text();
      const scripts = [...html.matchAll(/src=["']([^"']+)["']/g)].map(match => match[1]);
      assert.ok(scripts.length, 'Missing docs scripts');
      for (const path of scripts) {
        const url = new URL(path, base + docsPath);
        assert.equal(url.origin, 'http://service:' + process.env.QUALITY_PORT, 'External docs asset');
        assert.equal((await page.request.get(url.toString(), { maxRedirects: 0 })).status(), 200);
      }
    }
    const measurementUrl = process.env.QUALITY_KIND === 'web' ? base + '/' : base + '/api/v1/examples?limit=1';
    const warmup = process.env.QUALITY_BENCHMARK === '1' ? 30000 : 250;
    const end = performance.now() + warmup;
    do { const response = await page.request.get(measurementUrl); assert.equal(response.status(), 200); await response.body(); await new Promise(resolve => setTimeout(resolve, Math.min(3000, warmup))); } while (performance.now() < end);
    const samples = [];
    for (let run = 0; run < 3; run++) {
      const times = [];
      for (let request = 0; request < 200; request++) {
        const start = performance.now();
        const response = await page.request.get(measurementUrl, { maxRedirects: 0 });
        assert.equal(response.status(), 200); await response.body(); times.push(performance.now() - start);
      }
      times.sort((a, b) => a - b); samples.push(times[Math.ceil(times.length * .95) - 1]);
    }
    samples.sort((a, b) => a - b);
    fs.writeFileSync('/output/http-sample.json', JSON.stringify({ startup_ms: startupMs, latency_ms: samples[1], run_p95_ms: samples, warmup_ms: warmup, requests_per_run: 200, repetitions: 3 }));
    console.log('Owned isolated route, readiness, assets and journey checks passed; web accessibility/keyboard/zoom where applicable.');
  } finally { await browser.close(); }
})().catch(error => { console.error(error.message); process.exit(1); });
