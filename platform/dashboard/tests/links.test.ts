import test from 'node:test';
import assert from 'node:assert/strict';
import { activeLink, validDestination, type ProjectLink } from '../lib/links.ts';
const key='1'.repeat(32);
const preview: ProjectLink = {kind:'preview',label:'Public preview',scope:'public',url:'https://preview.example.test/projects/example/',available:true,reason:null,observed_at:100,expires_at:110,remaining_seconds:10};
test('preview expires with collector time and elapsed time independently of client wall clock', () => {
  assert.equal(activeLink(preview,'example',key,100,0,false),true);
  assert.equal(activeLink(preview,'example',key,100,10,false),false);
  assert.equal(activeLink({...preview,remaining_seconds:3},'example',key,100,4,false),false);
  assert.equal(activeLink(preview,'example',key,100,0,true),false);
});
test('rendering rejects unsafe destinations while repository links survive runtime outages', () => {
  const repo={...preview,kind:'repository',scope:'repository',url:'https://github.com/example/project'};
  assert.equal(activeLink(repo,'example',key,undefined,100,true),true);
  for(const url of ['javascript:alert(1)','https://token@github.com/example/project','https://github.com/example/project?token=value','https://github.com/example/%2e%2e/']) assert.equal(validDestination({...repo,url},'example',key),false);
  const app={...preview,kind:'app',scope:'private',url:'https://forge-dev.example.ts.net/projects/example/'};
  assert.equal(activeLink(app,'example',key,100,0,false),true);
  assert.equal(activeLink(app,'example',key,100,31,false),false);
  assert.equal(validDestination({...app,url:'https://untrusted.test/projects/example/'},'example',key),false);
});
