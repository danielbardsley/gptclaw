const assert = require('node:assert/strict');
const { chromium } = require('playwright-core');
(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  page.on('pageerror', error => console.error('Browser script error:', error.message));
  page.on('console', msg => { if (msg.type() === 'error') console.error('Browser console:', msg.text()); });
  try {
  const prefix = `/projects/${process.env.GPTCLAW_PROJECT_ID}`;
  const origin = process.env.GPTCLAW_BROWSER_URL || 'http://web:3000';
  if (!process.env.GPTCLAW_BROWSER_URL) {
    // Exercise the real separate API while preserving the UI's same-origin URL.
    await page.route('**' + prefix + '/api/**', async route => {
      const url = new URL(route.request().url());
      const response = await route.fetch({ url: 'http://api:8000' + url.pathname + url.search });
      await route.fulfill({ response });
    });
  }
  const target = origin + prefix + '/';
  for (let attempt = 0; attempt < 60; attempt++) {
    try { const response = await page.request.get(target); if (response.ok()) break; } catch {}
    await new Promise(resolve => setTimeout(resolve, 500));
  }
  await page.goto(target);
  console.log('Loaded browser UI');
  await page.getByText('No notes yet. Write your first idea.').waitFor();
  console.log('Empty notes visible');
  assert.ok(await page.getByText('Shared, temporary notes.', { exact: false }).isVisible());
  await page.getByLabel('Title', { exact: true }).fill('Synthetic browser note');
  await page.getByLabel('Note', { exact: true }).fill('<img src=x onerror="window.synthetic = true">');
  await page.getByRole('button', { name: 'Save note', exact: true }).click();
  await page.getByRole('heading', { name: 'Edit note' }).waitFor();
  await page.reload();
  await page.getByRole('button', { name: /Synthetic browser note/ }).click();
  await page.getByRole('heading', { name: 'Edit note' }).waitFor();
  assert.equal(await page.getByLabel('Note', { exact: true }).inputValue(), '<img src=x onerror="window.synthetic = true">');
  assert.equal(await page.evaluate(() => window.synthetic), undefined);
  await page.getByLabel('Title', { exact: true }).fill('Updated browser note');
  await page.getByRole('button', { name: 'Save note', exact: true }).click();
  await page.getByRole('button', { name: /Updated browser note/ }).waitFor();
  // A failed mutation must retain the draft and report an accessible error.
  await page.route('**' + prefix + '/api/v1/notes/**', route => route.fulfill({ status: 503, body: '' }));
  await page.getByLabel('Note', { exact: true }).fill('Unsaved synthetic draft');
  await page.getByRole('button', { name: 'Save note', exact: true }).click();
  await page.getByRole('alert').waitFor();
  assert.equal(await page.getByLabel('Note', { exact: true }).inputValue(), 'Unsaved synthetic draft');
  await page.unroute('**' + prefix + '/api/v1/notes/**');
  page.once('dialog', dialog => dialog.accept());
  await page.getByRole('button', { name: 'Delete note', exact: true }).click();
  await page.getByText('No notes yet. Write your first idea.').waitFor();
  console.log('Empty notes visible');
  await page.getByLabel('Title', { exact: true }).focus();
  await page.keyboard.press('Tab');
  assert.equal(await page.evaluate(() => document.activeElement.id), 'body');
  await page.setViewportSize({ width: 390, height: 844 });
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth));
  await page.screenshot({ path: '/checks/output/notes.png', fullPage: true });
  } catch (error) { await page.screenshot({ path: '/checks/output/failure.png', fullPage: true }); throw error; }
  await browser.close();
  console.log('Browser CRUD, refresh retention, plain text, failed draft, labels/keyboard and responsive checks passed.');
})().catch(error => { console.error(error.message); process.exit(1); });
