'use strict';
const assert = require('node:assert/strict');
const { chromium } = require('playwright-core');
(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  const origin = process.env.DASHBOARD_BROWSER_ORIGIN || 'http://127.0.0.1:18201';
  const response = await page.request.get(origin + '/dashboard/api/snapshot/');
  assert.equal(response.status(), 200);
  const actual = await response.json();
  await page.goto(origin + '/dashboard/');
  await page.getByRole('heading', { name: 'Projects', exact: true }).waitFor();
  await page.getByText('Inventory current', { exact: true }).waitFor();
  assert.equal(await page.locator('tbody tr').count(), actual.rows.length);
  await page.keyboard.press('Tab');
  assert.equal(await page.locator(':focus').textContent(), 'Skip to projects');
  await page.keyboard.press('Enter');
  assert.equal(await page.locator(':focus').getAttribute('id'), 'projects');
  await page.screenshot({ path: '/checks/output/dashboard-inventory.png', fullPage: true });
  let mode = 'empty';
  const fixture = structuredClone(actual);
  fixture.rows = [actual.rows[0]];
  fixture.rows[0].name = '<img src=x onerror="window.syntheticXss=true">';
  fixture.rows[0].owner = null;
  fixture.rows[0].repository = null;
  await page.route('**/dashboard/api/snapshot/', async route => {
    if (mode === 'failure') return route.fulfill({ status: 503, contentType: 'application/json', body: JSON.stringify({ schema_version: 1, freshness: 'unavailable' }) });
    const value = mode === 'retained' ? { ...fixture, complete: false, rows: fixture.rows.map(row => ({ ...row, inventory_freshness: 'stale' })) } : mode === 'empty' ? { ...fixture, rows: [], complete: true } : mode === 'partial' ? { ...fixture, complete: false, truncated: true, diagnostics: [{ code: 'input_path' }] } : mode === 'stale' ? { ...fixture, freshness: 'stale' } : fixture;
    return route.fulfill({ contentType: 'application/json', body: JSON.stringify(value) });
  });
  await page.reload();
  await page.getByRole('heading', { name: 'No managed projects yet' }).waitFor();
  mode = 'partial'; await page.reload();
  await page.getByText('Partial inventory · scan limit reached', { exact: true }).waitFor();
  assert.equal(await page.locator('tbody img').count(), 0);
  assert.equal(await page.evaluate(() => window.syntheticXss), undefined);
  assert.equal(await page.getByText(fixture.rows[0].name, { exact: true }).count(), 1);
  assert.match(await page.locator('tbody td').filter({ hasText: 'Repository not recorded' }).textContent(), /Not recorded/);
  await page.getByText('Repository not recorded', { exact: true }).waitFor();
  mode = 'retained'; await page.reload();
  await page.getByText('Inventory metadata stale', { exact: true }).waitFor();
  mode = 'stale'; await page.reload();
  await page.getByText('Inventory stale · collector unavailable', { exact: true }).waitFor();
  mode = 'current'; await page.reload();
  await page.getByText('Inventory current', { exact: true }).waitFor();
  mode = 'failure';
  await page.getByText('Inventory stale · collector unavailable', { exact: true }).waitFor({ timeout: 9000 });
  assert.equal(await page.locator('tbody tr').count(), 1);
  mode = 'current';
  await page.getByText('Inventory current', { exact: true }).waitFor({ timeout: 9000 });
  const now = Date.now()/1000;
  fixture.server_time = now;
  fixture.rows[0].components = ['web','api','db'];
  fixture.rows[0].kind = 'group';
  const component = { state:'ready',provider_state:'ready',health:'healthy',operation_busy:false,
    freshness:'current',observed_at:now,last_success_at:now,uptime_seconds:0,restart_count:0,
    last_observed_change:{kind:'first-observed',at:now,after_gap:false,previous_observation_at:null} };
  fixture.rows[0].status = { ...component,provider_version:'1.9.0',publication:{state:'published',origin:'https://forge-dev.example.ts.net'},
    components:{web:{...component},api:{...component},db:{...component,uptime_seconds:null,uptime_reason:'unavailable',restart_count:null,restart_reason:'unsupported'}} };
  await page.reload();
  await page.getByRole('columnheader',{name:'Service status'}).waitFor();
  await page.getByLabel('Service details for '+fixture.rows[0].name).focus();
  await page.keyboard.press('Enter');
  await page.getByRole('region',{name:'WEB service'}).waitFor();
  assert.equal(await page.getByText('0s',{exact:true}).count(),2);
  assert.equal(await page.getByText('Container-instance restarts',{exact:true}).count(),3);
  assert.equal(await page.getByText('Unsupported',{exact:true}).count(),1);
  fixture.rows[0].status.components.api = {...component,freshness:'stale',reason:'observation-timeout'};
  await page.reload();
  await page.getByLabel('Service details for '+fixture.rows[0].name).click();
  await page.getByText('Unknown · previous observation retained',{exact:true}).waitFor();
  await page.getByText('Observation timeout',{exact:true}).waitFor();
  fixture.rows[0].status.components.api = {...component};
  fixture.rows[0].status.last_success_at = now-40;
  fixture.server_time = now;
  await page.reload();
  await page.getByText('Last known: Ready',{exact:true}).waitFor();
  const row = fixture.rows[0];
  row.links = [
    {kind:'app',label:'Open app',scope:'private',url:'https://forge-dev.example.ts.net/projects/'+row.id+'/',available:true,reason:null,observed_at:now,expires_at:null,remaining_seconds:null},
    {kind:'repository',label:'Repository',scope:'repository',url:'https://github.com/example/project',available:true,reason:null,observed_at:null,expires_at:null,remaining_seconds:null},
    {kind:'logs',label:'Logs',scope:'private',url:null,available:false,reason:'log-viewer-not-available',observed_at:null,expires_at:null,remaining_seconds:null},
    {kind:'preview',label:'Public preview',scope:'public',url:'https://preview.example.test/projects/'+row.id+'/',available:true,reason:null,observed_at:now,expires_at:now+60,remaining_seconds:2}
  ];
  row.status.last_success_at = now;
  await page.addInitScript(() => { const clock = Date.now; Date.now = () => clock() + 12 * 3600 * 1000; });
  await page.reload();
  const repository = page.getByRole('link',{name:'Repository',exact:true});
  await repository.waitFor();
  assert.equal(await repository.getAttribute('rel'),'noopener noreferrer');
  await page.getByRole('link',{name:'Open app',exact:true}).waitFor();
  await page.getByText('Log viewer not available',{exact:true}).waitFor();
  await page.getByRole('link',{name:'Public preview',exact:true}).waitFor();
  await page.getByRole('link',{name:'Public preview',exact:true}).waitFor({state:'detached',timeout:4000});
  // No reload is required to withdraw an expired preview; repo stays useful.
  assert.equal(await repository.count(),1);
  row.links[0].available=false;row.links[0].reason='project-unavailable';
  row.links[3].available=false;row.links[3].reason='preview-registry-not-available';row.links[3].url=null;
  await page.reload();
  await page.getByText('Project is unavailable',{exact:true}).waitFor();
  await page.getByText('Preview registry not available',{exact:true}).waitFor();
  assert.equal(await page.getByRole('link',{name:'Open app',exact:true}).count(),0);
  assert.equal(await page.getByRole('link',{name:'Repository',exact:true}).count(),1);
  assert.deepEqual(errors, []);
  console.log('PASS: real inventory render, semantic table, keyboard skip navigation, safe text, metadata gaps, empty/partial/stale/outage/recovery UI; accessible component status, zero/null metrics and stale health; validated navigation and local preview expiry');
  await browser.close();
})().catch(error => { console.error(error); process.exit(1); });
