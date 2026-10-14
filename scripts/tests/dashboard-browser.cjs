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
  assert.equal(await page.locator('.project-row').count(), actual.rows.length);
  await page.keyboard.press('Tab');
  assert.equal(await page.locator(':focus').textContent(), 'Skip to projects');
  await page.keyboard.press('Enter');
  assert.equal(await page.locator(':focus').getAttribute('id'), 'projects');
  await page.screenshot({ path: '/checks/output/dashboard-inventory.png', fullPage: true });
  let mode = 'empty';
  let layout;
  let reads = 0;
  const fixture = structuredClone(actual);
  fixture.rows = [structuredClone(actual.rows[0])];
  fixture.rows[0].name = '<img src=x onerror="window.syntheticXss=true">';
  fixture.rows[0].owner = null;
  fixture.rows[0].repository = null;
  await page.route('**/dashboard/api/snapshot/', async route => {
    reads++;
    if (mode === 'layout') return route.fulfill({contentType:'application/json',body:JSON.stringify(layout)});
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
  await page.getByText('Repository not recorded', { exact: true }).waitFor();
  mode = 'retained'; await page.reload();
  await page.getByText('Inventory metadata stale', { exact: true }).waitFor();
  mode = 'stale'; await page.reload();
  await page.getByText('Inventory stale · collector unavailable', { exact: true }).waitFor();
  mode = 'current'; await page.reload();
  await page.getByText('Inventory current', { exact: true }).waitFor();
  mode = 'failure';
  await page.getByText('Inventory stale · collector unavailable', { exact: true }).waitFor({ timeout: 9000 });
  assert.equal(await page.locator('.project-row').count(), 1);
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
  await page.getByLabel('Service details for '+fixture.rows[0].name).click();
  await page.getByText('Log viewer not available',{exact:true}).waitFor();
  await page.getByLabel('Service details for '+fixture.rows[0].name).click();
  await page.getByRole('link',{name:'Public preview',exact:true}).waitFor();
  await page.getByRole('link',{name:'Public preview',exact:true}).waitFor({state:'detached',timeout:4000});
  // No reload is required to withdraw an expired preview; repo stays useful.
  assert.equal(await repository.count(),1);
  row.links[0].available=false;row.links[0].reason='project-unavailable';
  row.links[3].available=false;row.links[3].reason='preview-registry-not-available';row.links[3].url=null;row.links[3].expires_at=null;row.links[3].remaining_seconds=null;
  await page.reload();
  await page.getByLabel('Service details for '+fixture.rows[0].name).click();
  await page.getByText('Project is unavailable',{exact:true}).waitFor();
  await page.getByText('Preview registry not available',{exact:true}).waitFor();
  assert.equal(await page.locator('.project-row').getByRole('link',{name:'Open app',exact:true}).count(),0);
  assert.equal(await page.locator('.project-row').getByRole('link',{name:'Repository',exact:true}).count(),1);
  await page.getByLabel('Service details for '+fixture.rows[0].name).click();
  assert.deepEqual(errors, []);
  // Reference-based presentation uses only valid web/API/group data.
  layout = {...structuredClone(actual), server_time:now, rows:[]};
  for (let index=0;index<6;index++) {
    const source=actual.rows[index % actual.rows.length];
    const id='visual-project-'+String(index+1).padStart(2,'0');
    const links=[];
    if (source.kind !== 'api') links.push({kind:'app',label:'Open app',scope:'private',url:'https://forge-dev.example.ts.net/projects/'+id+'/',available:true,reason:null,observed_at:now,expires_at:null,remaining_seconds:null});
    if (source.components.includes('api')) links.push({kind:'api-docs',label:'API docs',scope:'private',url:'https://forge-dev.example.ts.net/projects/'+id+(source.kind==='api'?'/docs':'/api/docs'),available:true,reason:null,observed_at:now,expires_at:null,remaining_seconds:null});
    links.push({...row.links[1]}, {...row.links[2]}, {...row.links[3]});
    layout.rows.push({...structuredClone(source),key:(index+1).toString(16).padStart(32,'0'),id,name:'Synthetic project '+(index+1),location:id,owner:'Project owner',repository:'https://github.com/example/project',documentation:{readme:'present',index:'missing'},links,
      status:{...component,provider_version:'1.9.0',publication:{state:'published',origin:'https://forge-dev.example.ts.net'},components:Object.fromEntries(source.components.map(name=>[name,{...component}]))}});
  }
  mode='layout';
  await page.setViewportSize({width:1440,height:900});await page.reload();
  await page.getByText('Synthetic project 1',{exact:true}).waitFor();
  assert.equal(await page.locator('.project-row').count(),6);
  const normalRows=await page.locator('.project-row').evaluateAll(rows=>rows.map(row=>({height:row.getBoundingClientRect().height,bottom:row.getBoundingClientRect().bottom})));
  assert.ok(normalRows.every(row=>row.height>=72 && row.height<=88),JSON.stringify(normalRows));
  assert.ok(normalRows[5].bottom<=900,'Six collapsed rows must fit');
  assert.equal(await page.getByRole('textbox').count(),0);
  assert.equal(await page.getByRole('button',{name:/Rescan|Filter|Search/i}).count(),0);
  assert.equal(await page.getByRole('link',{name:'Logs',exact:true}).count(),0);
  assert.equal(await page.getByRole('link',{name:'Public preview',exact:true}).count(),0);
  await page.screenshot({path:'/checks/output/dashboard-refined-desktop.png',fullPage:true});
  const first=page.locator('.project-row').first();
  const toggle=first.getByRole('button');
  const before=reads;
  await toggle.focus();await page.keyboard.press('Enter');
  assert.equal(await toggle.getAttribute('aria-expanded'),'true');
  await page.waitForResponse(response=>response.url().includes('/dashboard/api/snapshot/'),{timeout:7000});
  assert.equal(await toggle.getAttribute('aria-expanded'),'true');
  assert.equal(await toggle.evaluate(el=>el===document.activeElement),true);
  assert.ok(reads-before<=2,'Disclosures must not start collection loops');
  const appLink=first.getByRole('link',{name:'Open app',exact:true});
  if(await appLink.count()) {
    // Inspect the actual click interaction while intercepting only navigation.
    await appLink.evaluate(el=>el.addEventListener('click',event=>event.preventDefault(),{once:true}));
    await appLink.click();assert.equal(await toggle.getAttribute('aria-expanded'),'true');
  }
  await page.screenshot({path:'/checks/output/dashboard-refined-details.png',fullPage:true});
  for(const width of [1280,768,390,720]) {
    await page.setViewportSize({width,height:width===720?450:900});
    const bounds=await page.evaluate(()=>({viewport:innerWidth,document:document.documentElement.scrollWidth,overview:document.querySelector('.overview').getBoundingClientRect(),buttons:[...document.querySelectorAll('.project-row button,.project-row a')].map(el=>({width:el.getBoundingClientRect().width,height:el.getBoundingClientRect().height}))}));
    assert.ok(bounds.document<=width+1,'Document overflow at '+width+': '+bounds.document);
    assert.ok(bounds.buttons.every(button=>button.width>= (width<=768?44:24) && button.height>= (width<=768?44:24)),'Small primary targets at '+width);
    assert.equal(await page.getByRole('columnheader',{name:'Project',exact:true}).count(),1);
    assert.equal(await page.getByRole('rowheader').count(),6);
    if(width===390)await page.screenshot({path:'/checks/output/dashboard-refined-mobile.png',fullPage:true});
  }
  // 720 CSS px represents a 1440 px desktop at 200% layout zoom.
  await page.emulateMedia({reducedMotion:'reduce'});
  assert.equal(await toggle.locator('svg').evaluate(el=>getComputedStyle(el).transitionDuration),'0s');
  await page.setViewportSize({width:1440,height:900});
  const states=['ready','stopped','starting','failed','degraded','unknown'];
  layout.rows.forEach((item,index)=>{
    const state=states[index];item.status.state=state;item.status.provider_state=state;
    if(state==='unknown'){item.status.freshness='unavailable';item.status.last_success_at=null;}
    if(state!=='ready')item.links.forEach(link=>{if(link.scope==='private')link.available=false;});
  });
  await page.waitForResponse(response=>response.url().includes('/dashboard/api/snapshot/'),{timeout:7000});
  for(const name of ['Ready','Stopped','Starting','Failed','Degraded','Status unavailable'])assert.ok(await page.locator('.project-row .status-badge').filter({hasText:name}).count());
  const contrast=await page.evaluate(()=>{
    const rgb=s=>s.match(/[\d.]+/g).slice(0,3).map(Number);
    const luminance=s=>rgb(s).map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4;}).reduce((sum,v,i)=>sum+v*[.2126,.7152,.0722][i],0);
    const background=el=>{for(let node=el;node;node=node.parentElement){const c=getComputedStyle(node).backgroundColor;if(c!=='rgba(0, 0, 0, 0)'&&c!=='transparent')return c;}return 'rgb(255,255,255)';};
    return [...document.querySelectorAll('.project-row .secondary,.status-badge,.link-pill,.destination-reason,.managed-tile span')].filter(el=>el.getBoundingClientRect().height).map(el=>{const a=luminance(getComputedStyle(el).color),b=luminance(background(el));return {text:el.textContent,ratio:(Math.max(a,b)+.05)/(Math.min(a,b)+.05)};});
  });
  assert.ok(contrast.every(item=>item.ratio>=4.5),JSON.stringify(contrast.filter(item=>item.ratio<4.5)));
  // Long source values may grow; none may break the document or lose full metadata.
  layout.rows[0].name='Long synthetic project '+ 'x'.repeat(180);
  layout.rows[0].owner='Recorded owner '+ 'y'.repeat(80);
  layout.rows[0].location='synthetic/'+ 'z'.repeat(160);
  layout.rows[0].identity_state='conflict';layout.rows[0].inventory_freshness='stale';layout.complete=false;
  layout.rows[0].documentation={readme:'unavailable',index:'missing'};
  await page.waitForResponse(response=>response.url().includes('/dashboard/api/snapshot/'),{timeout:7000});
  assert.equal(await first.getByRole('button').getAttribute('aria-expanded'),'true');
  await page.setViewportSize({width:390,height:900});
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
  await page.getByText('Conflicting project ID',{exact:true}).waitFor();
  await page.getByText(layout.rows[0].location,{exact:true}).waitFor();
  layout.rows = [{ ...structuredClone(layout.rows[0]), key:'mobile-source-fixture', id:'mobile-source', name:'Native source fixture', kind:'mobile', components:[], manifest_version:5, runtime_support:'unsupported', identity_state:'valid', location:'mobile-source' }];
  await page.setViewportSize({width:1440,height:900}); await page.reload();
  await page.getByText('Native source · Metro not enabled',{exact:true}).waitFor();
  assert.equal(await page.getByText('Native source · v5',{exact:true}).count(),1);
  await page.getByRole('button',{name:'Service details for Native source fixture'}).click();
  assert.equal(await page.getByRole('heading',{name:'Component observations',exact:true}).count(),0);
  layout.rows[0].manifest_version=6;layout.rows[0].runtime_support='supported';
  layout.rows[0].inventory_freshness='current';layout.freshness='current';layout.complete=true;
  const nativeNow=Date.now()/1000;layout.server_time=nativeNow;
  layout.rows[0].status={...component,health:'not-applicable',observed_at:nativeNow,last_success_at:nativeNow,
    components:{},provider_version:'1.12.0',publication:{state:'unavailable',origin:null},
    metro:{schema_version:1,project:'mobile-source',generation:'1'.repeat(32),state:'route-pending',expires_at:nativeNow+3600,
      native_client_acceptance:'unverified',source_quality:'separate-receipt',
      observations:{process:{state:'up',observed_at:nativeNow},protocol:{state:'ready',observed_at:nativeNow},route:{state:'pending',observed_at:nativeNow}}}};
  await page.reload();
  await page.getByText('Metro: Route pending',{exact:true}).waitFor();
  await page.getByRole('button',{name:'Service details for Native source fixture'}).click();
  await page.getByRole('region',{name:'Metro session observations'}).waitFor();
  await page.getByText('Private route',{exact:true}).waitFor();
  await page.getByText('Native client acceptance',{exact:true}).waitFor();
  assert.equal(await page.getByRole('heading',{name:'Component observations',exact:true}).count(),0);
  assert.equal(await page.locator('a[href^="exp"],a[href^="exps"]').count(),0);
  layout.rows[0].status.metro.project='foreign';
  await page.reload();
  await page.getByText('Metro observation unavailable',{exact:true}).waitFor();
  assert.equal(await page.getByRole('region',{name:'Metro session observations'}).count(),0);
  assert.equal(await page.evaluate(()=>localStorage.length),0);
  assert.deepEqual(errors, []);
  console.log('PASS: reference density and responsive bounds, disclosure refresh/focus, safe compact links, readable contrast, reduced motion, long metadata and omitted unsupported controls');
  console.log('PASS: real inventory render, semantic table, keyboard skip navigation, safe text, metadata gaps, empty/partial/stale/outage/recovery UI; accessible component status, zero/null metrics and stale health; validated navigation and local preview expiry');
  await browser.close();
})().catch(error => { console.error(error); process.exit(1); });
