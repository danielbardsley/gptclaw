import test from 'node:test';
import assert from 'node:assert/strict';
import { validControls } from '../lib/control-types.ts';
test('unknown controls, verbs, components, counts and result states fail closed',()=>{
  const base={schema_version:1,enabled:true,capabilities:{schema_version:1,observed_at:1000,generation:'a'.repeat(64),actions:[{action:'restart',component:'web',enabled:true,reason:null}]},recent:[],retention_days:7};
  assert.ok(validControls(base));
  assert.equal(validControls({...base,enabled:false})?.enabled,false);
  for(const value of [{...base,schema_version:2},{...base,enabled:'true'},{...base,capabilities:{...base.capabilities,schema_version:2}},{...base,capabilities:{...base.capabilities,actions:[{action:'shell',component:null,enabled:true}]}},{...base,capabilities:{...base.capabilities,actions:[{action:'restart',component:'worker',enabled:true}]}},{...base,recent:[{operation_id:'a'.repeat(32),state:'invented'}]}])assert.equal(validControls(value),null);
});
