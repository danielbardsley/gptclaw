import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { readFileSync, mkdirSync } from 'node:fs';
import { chromium } from 'playwright-core';
import { staticServer } from './serve.mjs';
import { identity } from './export.mjs';
const id = identity();
const local = process.env.GPTCLAW_BROWSER_URL
  ? null
  : staticServer(process.cwd(), id);
if (local)
  await new Promise((resolve) => local.listen(0, '127.0.0.1', resolve));
const origin =
  process.env.GPTCLAW_BROWSER_URL || `http://127.0.0.1:${local.address().port}`;
const prefix = `/projects/${id}/`;
const browser = await chromium.launch({
  headless: true,
  args: ['--no-sandbox'],
});
const require = createRequire(import.meta.url);
const axe = readFileSync(require.resolve('axe-core/axe.min.js'), 'utf8');
const errors = [];
const page = await browser.newPage();
page.on('pageerror', (error) => errors.push(error.message));
page.on('requestfailed', (req) => {
  if (req.failure()?.errorText !== 'net::ERR_ABORTED')
    errors.push(req.url() + ': ' + req.failure()?.errorText);
});
page.on('response', (response) => {
  if (
    response.status() >= 400 &&
    !new URL(response.url()).pathname.endsWith('/missing-page/')
  )
    errors.push(response.url() + ': ' + response.status());
});
try {
  for (const route of ['', 'guide/getting-started/']) {
    const response = await page.goto(origin + prefix + route, {
      waitUntil: 'networkidle',
    });
    assert.equal(response.status(), 200);
    await page.addScriptTag({ content: axe });
    const results = await page.evaluate(async () => {
      // axe-core is injected only in this disposable browser context.
      return await axe.run(document, {
        runOnly: {
          type: 'tag',
          values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'],
        },
      });
    });
    assert.deepEqual(
      results.violations.map((v) => ({
        id: v.id,
        nodes: v.nodes.map((n) => n.target),
      })),
      [],
    );
    await page.reload({ waitUntil: 'networkidle' });
    assert.ok(await page.getByRole('heading', { level: 1 }).isVisible());
  }
  await page.goto(origin + prefix);
  await page.keyboard.press('Tab');
  assert.equal(
    await page.evaluate(() => document.activeElement.textContent),
    'Skip to content',
  );
  await page.keyboard.press('Enter');
  assert.equal(await page.evaluate(() => document.activeElement.id), 'main');
  await page.getByRole('link', { name: 'Explore the guide' }).click();
  await page.waitForURL('**/guide/getting-started/');
  await page.getByRole('link', { name: 'Jump to your first page' }).click();
  assert.equal(new URL(page.url()).hash, '#first-page');
  await page.goBack();
  const noJS = await browser.newContext({ javaScriptEnabled: false });
  const plain = await noJS.newPage();
  await plain.goto(origin + prefix);
  assert.ok(await plain.getByRole('heading', { level: 1 }).isVisible());
  await plain.getByRole('link', { name: 'Explore the guide' }).click();
  assert.ok(
    await plain.getByRole('heading', { name: 'Make it yours.' }).isVisible(),
  );
  await noJS.close();
  const missing = await page.goto(origin + prefix + 'missing-page/');
  assert.equal(missing.status(), 404);
  assert.ok(
    await page.getByRole('heading', { name: 'Page not found' }).isVisible(),
  );
  await page.goto(origin + prefix);
  await page.setViewportSize({ width: 390, height: 844 });
  await page.evaluate(() => {
    document.documentElement.style.fontSize = '200%';
  });
  assert.ok(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  );
  mkdirSync('.gptclaw-cache', { recursive: true });
  await page.screenshot({
    path: '.gptclaw-cache/static-narrow.png',
    fullPage: true,
  });
  assert.deepEqual(errors, []);
  console.log(
    'Exported browser navigation/refresh/assets, axe WCAG A/AA, no-JS, keyboard, 404 and narrow 200% text checks passed.',
  );
} finally {
  await browser.close();
  if (local) await new Promise((resolve) => local.close(resolve));
}
