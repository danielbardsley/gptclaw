import test from 'node:test';
import assert from 'node:assert/strict';
import { allowedRequest } from '../lib/boundary.ts';
const origin = 'https://forge-dev.example.ts.net';
const request = (method = 'GET', url = origin + '/dashboard/api/snapshot/', extra: Record<string, string> = {}) => ({ method, url, headers: new Headers({ host: 'forge-dev.example.ts.net', ...extra }) });
test('only typed reads from the configured host and origin', () => {
  assert.equal(allowedRequest(request(), origin), null);
  assert.equal(allowedRequest(request('HEAD'), origin), null);
  for (const method of ['POST','PUT','PATCH','DELETE','OPTIONS','TRACE']) assert.equal(allowedRequest(request(method), origin), 405);
  for (const headers of ([{ host: 'attacker.example' }, { origin: 'https://attacker.example' }, { 'sec-fetch-site': 'cross-site' }, { 'sec-fetch-site': 'same-site' }] as Record<string, string>[])) assert.equal(allowedRequest(request('GET', undefined, headers), origin), 403);
});
test('rejects arbitrary paths, URL parameters and malformed origins', () => {
  for (const path of ['/dashboard/api/snapshot/?root=/etc', '/dashboard/redirect', '/dashboard/%2e%2e/', '/dashboard//api/snapshot/']) assert.notEqual(allowedRequest(request('GET', origin+path), origin), null);
  assert.equal(allowedRequest(request(), ''), 503);
  assert.equal(allowedRequest(request(), origin+'/wrong'), 503);
});

test('a user can navigate from an external link without opening cross-origin API reads', () => {
  const navigation = { 'sec-fetch-site': 'cross-site', 'sec-fetch-mode': 'navigate', 'sec-fetch-dest': 'document' };
  assert.equal(allowedRequest(request('GET', origin+'/dashboard/', navigation), origin), null);
  assert.equal(allowedRequest(request('GET', origin+'/dashboard/api/snapshot/', navigation), origin), 403);
});

test('controls enable only exact typed same-origin JSON writes',()=>{
  const headers={origin,'sec-fetch-site':'same-origin','content-type':'application/json'};
  const write=request('POST',origin+'/dashboard/api/control-intents/',headers);
  assert.equal(allowedRequest(write,origin,false),405);
  assert.equal(allowedRequest(write,origin,true),null);
  for(const path of ['/dashboard/api/snapshot/','/dashboard/shell/','/dashboard/api/operations/?root=/etc'])assert.notEqual(allowedRequest(request('POST',origin+path,headers),origin,true),null);
  for(const extra of [{origin:''},{origin:'https://attacker.example'},{'sec-fetch-site':'cross-site'},{'content-type':'text/plain'}])assert.equal(allowedRequest(request('POST',write.url,{...headers,...extra}),origin,true),403);
  assert.equal(allowedRequest(request('GET',origin+'/dashboard/api/control-session/',{'sec-fetch-site':'cross-site'}),origin,true),403);
  assert.equal(allowedRequest(request('GET',origin+'/dashboard/api/control-session/',{'sec-fetch-site':'same-origin'}),origin,true),null);
  assert.equal(allowedRequest(request('GET',origin+'/dashboard/api/operations/'+'a'.repeat(32)+'/',{'sec-fetch-site':'same-origin'}),origin,true),null);
  assert.equal(allowedRequest(request('GET',origin+'/dashboard/api/operations/not-an-id/',{'sec-fetch-site':'same-origin'}),origin,true),404);
});
