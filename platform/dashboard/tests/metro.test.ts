import test from 'node:test';
import assert from 'node:assert/strict';
import { metroView } from '../lib/metro.ts';
import type { ProjectStatus } from '../lib/status.ts';
const base:ProjectStatus={state:'ready',provider_state:'ready',health:'not-applicable',operation_busy:false,
  freshness:'current',last_success_at:100,components:{},publication:{state:'unavailable',origin:null},provider_version:'1.12.0',
  metro:{schema_version:1,project:'fixture',generation:'1'.repeat(32),state:'ready',expires_at:200,
    native_client_acceptance:'unverified',source_quality:'separate-receipt',
    observations:{process:{state:'up',observed_at:100},protocol:{state:'ready',observed_at:100},route:{state:'verified',observed_at:100}}}};
test('Metro layers age independently and expire without ready launch claims',()=>{
  assert.equal(metroView(base,'fixture',100,0)?.state,'ready');
  assert.equal(metroView(base,'fixture',100,31)?.state,'stale');
  assert.equal(metroView(base,'fixture',100,100)?.state,'expired');
  assert.equal(metroView(base,'fixture',100,0,true)?.state,'stale');
  assert.equal(metroView(base,'fixture',90,0)?.state,'stale');
  const value=structuredClone(base);(value.metro as any).observations.route.observed_at=60;
  assert.equal(metroView(value,'fixture',100,0)?.observations.process.freshness,'current');
  assert.equal(metroView(value,'fixture',100,0)?.observations.route.freshness,'stale');
  assert.equal(metroView(value,'fixture',100,0)?.state,'stale');
});
test('foreign malformed or unsupported native metadata cannot become ready',()=>{
  assert.equal(metroView(base,'foreign',100,0),null);
  for (const [field,value] of Object.entries({schema_version:true,state:[],generation:'bad',expires_at:NaN,native_client_acceptance:'accepted'})) {
    const status=structuredClone(base);(status.metro as any)[field]=value;
    assert.equal(metroView(status,'fixture',100,0),null);
  }
  assert.equal(metroView({...base,metro:undefined},'fixture',100,0),null);
  const status=structuredClone(base);(status.metro as any).observations.process.observed_at=true;
  assert.equal(metroView(status,'fixture',100,0),null);
});
