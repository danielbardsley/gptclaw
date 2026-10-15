#!/usr/bin/env python3
"""Isolated controller identity, CSRF, idempotency, capacity and socket tests."""
import contextlib
import http.client
import json
import os
from pathlib import Path
import socket
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import private_apps as app
import project_controls as lifecycle
import dashboard_controls as controls

ORIGIN='https://forge-dev.example.ts.net'


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='dashboard-controls-');self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name);self.projects=self.base/'projects';self.projects.mkdir()
        self.root=self.projects/'sample';self.root.mkdir()
        for key,value in [('PROJECTS',self.projects),('STORE',self.projects/'.gptclaw-runtime/v1')]:
            p=patch.object(app,key,value);p.start();self.addCleanup(p.stop)
        self.now=1000.0;self.launched=[]
        self.controller=controls.Controller(self.projects,self.base/'state',ORIGIN,enabled=True,
            clock=lambda:self.now,spawn=lambda ident:self.launched.append(ident),inspector=lambda root:dict(self.caps))
        self.key='b'*32
        self.row={'key':self.key,'id':'sample','name':'Sample','runtime_support':'supported','identity_state':'valid'}
        self.value={'schema_version':1,'project':{'id':'sample','name':'Sample','kind':'web'},'data':{'mode':'ephemeral'}}
        self.caps={'schema_version':1,'generation':'c'*64,'project':'sample','name':'Sample','observed_at':self.now,
                   'actions':[{'action':a,'component':comp,'enabled':True,'reason':None} for comp,verbs in [(None,lifecycle.ACTIONS),('web',['restart'])] for a in verbs]}
        p=patch.object(self.controller,'target',return_value=(self.root,self.row));p.start();self.addCleanup(p.stop)
        p=patch.object(lifecycle,'capabilities',side_effect=lambda root:dict(self.caps));p.start();self.addCleanup(p.stop)
        p=patch.object(app,'target',return_value=(self.root,self.value));p.start();self.addCleanup(p.stop)
        p=patch.object(lifecycle,'source_lock',return_value=contextlib.nullcontext());p.start();self.addCleanup(p.stop)
        self.session=self.controller.session()

    def intent(self,**kwargs):
        return self.controller.intent({'schema_version':1,'project_key':self.key,'action':'restart','component':'web',**kwargs},
            self.session['session'],self.session['csrf'])

    def submit(self,intent,ident='d'*32):
        return self.controller.submit({'schema_version':1,'intent_id':intent['intent_id'],'idempotency_key':ident},
            self.session['session'],self.session['csrf'])

    def test_intent_has_no_effects_and_public_result_has_no_host_path_or_session(self):
        intent=self.intent();self.assertEqual(self.launched,[])
        self.assertNotIn('root',intent);self.assertNotIn('session',intent)
        self.assertIn('Restart WEB',intent['impact'])
        self.assertFalse(lifecycle.guard_path('sample').exists())
        result=self.submit(intent)
        self.assertEqual(result['state'],'accepted');self.assertEqual(self.launched,['d'*32])
        for key in ('root','session_hash','generation'):self.assertNotIn(key,result)
        self.assertTrue(lifecycle.guard_path('sample').exists())

    def test_duplicate_same_operation_never_dispatches_twice(self):
        intent=self.intent();first=self.submit(intent);second=self.submit(intent)
        self.assertEqual(first,second);self.assertEqual(self.launched,['d'*32])
        with self.assertRaises(controls.Refusal):self.submit(intent,'e'*32)
        self.assertEqual(self.launched,['d'*32])

    def test_session_and_csrf_invalid_or_expired_refuse(self):
        data={'schema_version':1,'project_key':self.key,'action':'restart','component':'web'}
        for session,csrf in [('missing',self.session['csrf']),(self.session['session'],'wrong')]:
            with self.assertRaises(controls.Refusal) as e:self.controller.intent(data,session,csrf)
            self.assertEqual(e.exception.status,403)
        self.now+=901
        with self.assertRaises(controls.Refusal):self.intent()
        self.assertEqual(self.launched,[])

    def test_confirmation_expiry_and_changed_generation_refuse(self):
        intent=self.intent();self.now+=61
        with self.assertRaises(controls.Refusal):self.submit(intent)
        intent=self.intent();self.caps['generation']='f'*64
        with self.assertRaises(controls.Refusal):self.submit(intent)
        self.assertEqual(self.launched,[])

    def test_extra_fields_arbitrary_paths_and_unknown_actions_refuse(self):
        for changes in [{'root':'/etc'},{'command':'touch /bad'},{'action':'open-task'},{'component':'worker'}]:
            with self.assertRaises(controls.Refusal):self.intent(**changes)
        self.assertEqual(self.launched,[])
        for raw in [b'{"schema_version":1,"schema_version":1}',b'[]',b'{"schema_version":true}',b'{"schema_version":NaN}',b' '*8193]:
            with self.assertRaises(controls.Refusal):controls.strict_json(raw)

    def test_storage_budget_does_not_prune_unknown_or_recent_results(self):
        self.submit(self.intent())
        self.now+=controls.RETENTION+1
        with patch.object(controls,'MAX_RECORDS',1):
            with self.assertRaises(controls.Refusal):self.controller.clean_capacity()
        self.assertTrue((self.controller.state/('d'*32+'.json')).exists())

    def test_restart_preserves_uncertainty_and_never_replays(self):
        self.submit(self.intent())
        recovered=controls.Controller(self.projects,self.controller.state,ORIGIN,enabled=True,clock=lambda:self.now,spawn=lambda _:self.fail('replay'))
        result=recovered.operation('d'*32)
        self.assertEqual(result['state'],'unknown');self.assertEqual(result['reason'],'control-recovery')
        self.assertTrue(lifecycle.guard_path('sample').exists())
        with self.assertRaises(controls.Refusal):recovered.submit({'schema_version':1,'intent_id':'a'*32,'idempotency_key':'e'*32},'old','bad')

    def test_default_off_and_bounded_intents_sessions(self):
        disabled=controls.Controller(self.projects,self.base/'off',ORIGIN)
        with self.assertRaises(controls.Refusal):disabled.session()
        self.assertFalse(disabled.snapshot()['enabled'])
        for _ in range(64):self.intent()
        with self.assertRaises(controls.Refusal):self.intent()
        self.assertEqual(self.launched,[])

    def test_two_tabs_project_busy_and_native_cli_contention(self):
        first=self.intent();second=self.intent()
        with app.locked('sample'):
            with self.assertRaises(app.AppError):self.submit(first)
        self.assertEqual(self.launched,[])
        self.submit(first)
        with self.assertRaises(controls.Refusal):self.submit(second,'e'*32)
        self.assertEqual(len(self.launched),1)

    def test_failed_spawn_retains_operation_and_guard_without_retry(self):
        with patch.object(self.controller,'spawn',side_effect=OSError('synthetic')):
            result=self.submit(self.intent())
        self.assertEqual(result['state'],'unknown')
        self.assertTrue(lifecycle.guard_path('sample').exists())
        self.assertEqual(self.launched,[])

    def test_admission_storage_failure_dispatches_nothing_and_can_be_reconciled(self):
        intent=self.intent();save=app.save
        def fail_guard(path,value):
            if path==lifecycle.guard_path('sample'):raise OSError('synthetic storage failure')
            return save(path,value)
        with patch.object(app,'save',side_effect=fail_guard):
            with self.assertRaises(OSError):self.submit(intent)
        self.assertEqual(self.launched,[])
        self.assertFalse(lifecycle.guard_path('sample').exists())
        rows={'web':{'active':False,'ready':False,'paused':False,'busy':False,'receipt':None}}
        with patch.object(lifecycle,'inspect',return_value=(self.root,self.value,None,rows,'c'*64)),patch.object(app,'object_owned',return_value=False):
            result=controls.reconcile_operation(self.root,'d'*32,'sample',state=self.controller.state)
        self.assertEqual(result['state'],'failed');self.assertTrue(result['reconciled'])
        self.assertEqual(self.controller.operation('d'*32)['state'],'failed')
        with self.assertRaises(controls.Refusal):self.submit(intent,'e'*32)
        self.assertEqual(self.launched,[])

    def test_reconciled_admission_cannot_later_execute(self):
        intent=self.intent();self.submit(intent)
        marker=lifecycle.guard_path('sample');marker.unlink()
        with patch.object(lifecycle,'inspect') as inspect:
            with self.assertRaises(app.AppError):
                token=lifecycle.OWNER.set('d'*32)
                try:lifecycle.execute(self.root,'restart','web',operation_id='d'*32,admitted=True)
                finally:lifecycle.OWNER.reset(token)
            inspect.assert_not_called()

    def test_socket_rejects_cross_origin_and_malformed_requests_before_dispatch(self):
        socket_path=self.base/'control.sock'
        server=controls.Server(str(socket_path),self.controller)
        self.addCleanup(server.server_close)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        self.addCleanup(server.shutdown)
        def request(method,path,headers,body=b''):
            conn=http.client.HTTPConnection('localhost');conn.sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
            conn.sock.connect(str(socket_path));conn.request(method,path,body=body,headers={'Host':ORIGIN.removeprefix('https://'),**headers})
            response=conn.getresponse();status=response.status;response.read();conn.close();return status
        data=json.dumps({'schema_version':1,'project_key':self.key,'action':'restart','component':'web'}).encode()
        headers={'Origin':ORIGIN,'Sec-Fetch-Site':'same-origin','Content-Type':'application/json',
                 'X-Control-Session':self.session['session'],'X-CSRF-Token':self.session['csrf']}
        self.assertEqual(request('POST','/v1/intents',headers,data),200)
        for changes in [{'Origin':'https://attacker.example'},{'Origin':''},{'Sec-Fetch-Site':'cross-site'},
                        {'Content-Type':'text/plain'},{'X-CSRF-Token':'bad'},{'Host':'attacker.example'}]:
            self.assertIn(request('POST','/v1/intents',{**headers,**changes},data),(400,403))
        self.assertEqual(request('GET','/v1/snapshot',{}),200)
        self.assertEqual(request('GET','/v1/intents',{}),404)
        self.assertEqual(request('POST','/v1/operations?root=/etc',headers,data),404)
        self.assertEqual(request('POST','/v1/intents',headers,b'x'*8193),400)
        self.assertEqual(self.launched,[])


if __name__=='__main__':unittest.main(verbosity=2)
