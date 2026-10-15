import test from 'node:test';
import assert from 'node:assert/strict';
import http from 'node:http';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { submitControl } from '../lib/controls.ts';
const origin='https://forge-dev.example.ts.net';
test('frontend forwards only bounded same-origin cookie/CSRF JSON to the fixed control socket',async()=>{
  const directory=await fs.mkdtemp(path.join(os.tmpdir(),'dashboard-control-api-'));
  const socket=path.join(directory,'control.sock');const calls:{url:string|undefined;body:unknown}[]=[];
  const before={origin:process.env.DASHBOARD_ORIGIN,enabled:process.env.DASHBOARD_CONTROLS,socket:process.env.DASHBOARD_CONTROL_SOCKET};
  const server=http.createServer(async(request,response)=>{
    const chunks:Buffer[]=[];for await(const chunk of request)chunks.push(chunk as Buffer);
    calls.push({url:request.url,body:JSON.parse(Buffer.concat(chunks).toString('utf8'))});
    assert.equal(request.headers.origin,origin);assert.equal(request.headers['sec-fetch-site'],'same-origin');
    assert.equal(request.headers['x-control-session'],'a'.repeat(64));assert.equal(request.headers['x-csrf-token'],'b'.repeat(64));
    response.writeHead(200,{'content-type':'application/json'});response.end(JSON.stringify({schema_version:1,intent_id:'c'.repeat(32)}));
  });
  await new Promise<void>(resolve=>server.listen(socket,resolve));
  process.env.DASHBOARD_ORIGIN=origin;process.env.DASHBOARD_CONTROLS='1';process.env.DASHBOARD_CONTROL_SOCKET=socket;
  const body={schema_version:1,project_key:'d'.repeat(32),action:'restart',component:'api'};
  const headers={host:'forge-dev.example.ts.net',origin,'sec-fetch-site':'same-origin','content-type':'application/json',cookie:'__Secure-gptclaw-control='+'a'.repeat(64),'x-csrf-token':'b'.repeat(64)};
  try{
    const request=(extra:Record<string,string>={},payload=JSON.stringify(body))=>new Request(origin+'/dashboard/api/control-intents/',{method:'POST',headers:{...headers,...extra},body:payload});
    const success=await submitControl(request(),'/v1/intents');assert.equal(success.status,200);
    assert.deepEqual(calls,[{url:'/v1/intents',body}]);
    assert.equal((await submitControl(request({origin:'https://attacker.example'}),'/v1/intents')).status,403);
    assert.equal((await submitControl(request({'x-csrf-token':''}),'/v1/intents')).status,403);
    assert.equal((await submitControl(request({cookie:''}),'/v1/intents')).status,403);
    assert.equal((await submitControl(request({},'x'.repeat(8193)),'/v1/intents')).status,413);
    process.env.DASHBOARD_CONTROLS='0';assert.equal((await submitControl(request(),'/v1/intents')).status,503);
    assert.equal(calls.length,1);
  }finally{
    for(const [key,value] of Object.entries({DASHBOARD_ORIGIN:before.origin,DASHBOARD_CONTROLS:before.enabled,DASHBOARD_CONTROL_SOCKET:before.socket})){if(value===undefined)delete process.env[key];else process.env[key]=value;}
    await new Promise<void>((resolve,reject)=>server.close(error=>error?reject(error):resolve()));
    await fs.rm(directory,{recursive:true});
  }
});


test('a stalled controller cannot delay healthy inventory beyond the shared snapshot deadline',async()=>{
  const directory=await fs.mkdtemp(path.join(os.tmpdir(),'dashboard-independent-read-'));
  const socket=path.join(directory,'collector.sock');
  const names=['DASHBOARD_ORIGIN','DASHBOARD_CONTROLS','DASHBOARD_CONTROL_SOCKET','DASHBOARD_SOCKET'] as const;
  const previous=Object.fromEntries(names.map(name=>[name,process.env[name]]));
  const server=http.createServer((request,response)=>{
    if(request.headers.origin){setTimeout(()=>{response.writeHead(503);response.end('{}');},1800);return;}
    response.writeHead(200,{'content-type':'application/json'});response.end(JSON.stringify({schema_version:1,freshness:'current',rows:[]}));
  });
  await new Promise<void>(resolve=>server.listen(socket,resolve));
  process.env.DASHBOARD_ORIGIN=origin;process.env.DASHBOARD_CONTROLS='1';process.env.DASHBOARD_CONTROL_SOCKET=socket;process.env.DASHBOARD_SOCKET=socket;
  try{
    const {GET}=await import('../app/api/snapshot/route.ts');
    const started=performance.now();const response=await GET();
    assert.equal(response.status,200);assert.equal((await response.json()).freshness,'current');
    assert.ok(performance.now()-started<1400,'controller delayed healthy reads');
  }finally{
    for(const name of names){if(previous[name]===undefined)delete process.env[name];else process.env[name]=previous[name];}
    await new Promise<void>((resolve,reject)=>server.close(error=>error?reject(error):resolve()));
    await fs.rm(directory,{recursive:true});
  }
});
