import test from 'node:test';
import assert from 'node:assert/strict';
import {goView} from '../lib/expo-go.ts';
import {localQr} from '../lib/local-qr.ts';
import type {ProjectStatus} from '../lib/status.ts';
const generation='1'.repeat(32),uri='exp://synthetic.tail123.ts.net:8443/_gptclaw/metro-session/'+generation;
const base:ProjectStatus={state:'ready',provider_state:'ready',health:'not-applicable',operation_busy:false,
  freshness:'current',last_success_at:1000,components:{},publication:{state:'unavailable',origin:null},provider_version:'1.12.0',
  metro:{schema_version:1,project:'fixture',generation,state:'ready',expires_at:2000,native_client_acceptance:'unverified',source_quality:'separate-receipt',
    observations:{process:{state:'up',observed_at:1000},protocol:{state:'ready',observed_at:1000},route:{state:'verified',observed_at:1000}}},
  expo_go:{schema_version:1,adapter:'expo-go-v1',project:'fixture',platform:'android',client_evidence:'reviewed-profile',client_version:'57.0.9',os_version:'11',
    state:'compatible',reason:'verified-client-profile',physical_verified_at:900,certification_expires_at:605700,
    launch:{schema_version:1,project:'fixture',platform:'android',generation,uri,expires_at:2000}}};
test('current compatible session offers exact locally encoded Go payload',()=>{
  const view=goView(base,'fixture',1000,0);assert.equal(view?.uri,uri);assert.ok(localQr(view!.uri!).svg.length<150000);
});
test('stale inventory, layers, expired sessions and certification withdraw launch',()=>{
  for(const [time,elapsed,forced] of [[1000,31,false],[1000,0,true],[2000,0,false],[899,0,false],[605700,0,false]] as const)
    assert.equal(goView(base,'fixture',time,elapsed,forced)?.uri,null);
  const v=structuredClone(base);(v.metro as any).observations.route.state='pending';assert.equal(goView(v,'fixture',1000,0)?.uri,null);
});
test('foreign or secret-bearing payloads and malformed profile cannot become actions',()=>{
  assert.equal(goView(base,'other',1000,0),null);
  for(const [field,value] of Object.entries({schema_version:true,state:[],client_evidence:'phone-detected',reason:'physical-client-and-launch-rule-unverified',physical_verified_at:NaN})) {
    const v=structuredClone(base);(v.expo_go as any)[field]=value;assert.equal(goView(v,'fixture',1000,0),null);
  }
  for(const [field,value] of Object.entries({project:'other',generation:'2'.repeat(32),uri:uri+'?token=secret',expires_at:2001})) {
    const v=structuredClone(base);(v.expo_go as any).launch[field]=value;assert.equal(goView(v,'fixture',1000,0),null);
  }
});
test('missing provider capability and candidate profile do not offer Go links',()=>{
  assert.equal(goView({...base,expo_go:undefined},'fixture',1000,0),null);
  const v=structuredClone(base);Object.assign(v.expo_go as any,{state:'check-required',reason:'physical-client-and-launch-rule-unverified',physical_verified_at:null,certification_expires_at:null,launch:null});
  assert.equal(goView(v,'fixture',1000,0)?.uri,null);
});
