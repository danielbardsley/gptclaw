#!/usr/bin/env python3
"""Offline bound-mobile and API-only lifecycle/ownership regression scenarios."""
import copy
import subprocess
import types
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import private_apps as a
import mobile_backend as mb
import project_groups as groups
import project_database as db
import project_templates as templates


class MobileBackend(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name)
        for key,value in [('PROJECTS',self.base),('STORE',self.base/'.runtime'),('UNITS',self.base/'units')]:
            mock=patch.object(a,key,value);mock.start();self.addCleanup(mock.stop)
        self.backend=Path(a.create('notes-api',template='fastapi-postgres',template_version='1.0.0')['root'])
        self.mobile=Path(a.create('notes-mobile',template='expo-notes',template_version='1.0.0')['root'])
        self.value=a.target(self.backend)[1]

    def test_offline_topology_generation_and_immutable_provenance(self):
        with patch.object(a,'command') as command:
            self.assertEqual(a.validate_project(self.backend)[2],0)
            self.assertEqual(a.validate_project(self.mobile)[2],0)
            self.assertEqual(set(self.value['components']),{'api','db'})
            self.assertEqual(groups.order(self.value),('api',))
            self.assertFalse((self.backend/'web').exists())
            self.assertFalse((self.mobile/mb.CONFIG).exists())
            self.assertNotIn('Counter',(self.mobile/'src/app/index.tsx').read_text())
            templates.validate_provenance(self.backend);templates.validate_provenance(self.mobile)
            command.assert_not_called()

    def test_url_refusal_precedes_network(self):
        host='owned.example.ts.net';valid='https://'+host+'/projects/notes-api/api'
        self.assertEqual(mb.url(valid,'notes-api',host),valid)
        bad=[valid+'/',valid+'?token=x',valid+'#x',valid.replace('https:','http:'),valid.replace(host,'public.example.com'),valid.replace(host,'localhost'),valid.replace(host,'127.0.0.1'),valid.replace(host,'user@'+host),valid.replace(host,host+':443'),valid.replace('notes-api','another'),valid.replace('/projects/','/projects/../projects/')]
        with patch.object(a,'command') as command:
            for value in bad:
                with self.subTest(value=value),self.assertRaises(a.AppError):mb.url(value,'notes-api',host)
            command.assert_not_called()

    def bind(self):
        with patch('project_worktrees.canonical'),patch('metro_sessions.assert_stopped'),patch.object(a,'node_identity',return_value='owned.example.ts.net'):
            return mb.bind(self.mobile,self.backend,'https://owned.example.ts.net/projects/notes-api/api')

    def test_binding_explicit_identity_and_generated_public_bytes(self):
        with patch.object(a,'node_identity',return_value='owned.example.ts.net'),patch('project_worktrees.canonical'):
            with self.assertRaises(a.AppError):mb.inspect(self.mobile)
            self.assertEqual(self.bind()['state'],'backend-bound')
            self.assertEqual(mb.inspect(self.mobile)['backend'],'notes-api')
            text=(self.mobile/mb.GENERATED).read_text();self.assertNotIn('root',text);self.assertNotIn('password',text)
            self.assertEqual(set(mb.fingerprint(self.mobile)),{mb.CONFIG,mb.GENERATED})
            (self.mobile/mb.GENERATED).write_text(text+'// changed')
            with self.assertRaises(a.AppError):mb.fingerprint(self.mobile)

    def test_binding_rejects_changed_identity_and_unsupported_contract(self):
        self.bind()
        with patch.object(a,'node_identity',return_value='owned.example.ts.net'),patch('project_worktrees.canonical'):
            original=a.read_json(self.mobile/mb.CONFIG)
            for field,value in [('mobile','other'),('backend','other'),('contract_version',2),('profile','production'),('root','/etc'),('root',{}),('backend',[]) ]:
                changed={**original,field:value};a.save(self.mobile/mb.CONFIG,changed)
                with self.subTest(field=field),self.assertRaises(a.AppError):mb.inspect(self.mobile)
            a.save(self.mobile/mb.CONFIG,original)
            with patch('metro_sessions.assert_stopped',side_effect=a.AppError('busy')):
                with self.assertRaises(a.AppError):mb.bind(self.mobile,self.backend,original['api_url'])
            self.assertEqual(a.read_json(self.mobile/mb.CONFIG),original)

    def test_api_only_receipt_refuses_invented_components(self):
        with groups.scope(self.backend,self.value):s=groups.reserve(self.backend,self.value)
        self.assertEqual(s['schema_version'],4);groups.valid_state(s)
        with self.assertRaises(a.AppError):groups.valid_state({**s,'components':{**s['components'],'web':'foreign'}})
        for version in (3,4.0,True):
            with self.assertRaises(a.AppError):groups.valid_state({**s,'schema_version':version})

    def test_same_id_runtime_receipt_cannot_redirect_a_canonical_binding(self):
        self.bind();before=(self.mobile/mb.CONFIG).read_bytes()
        with patch.object(a,'node_identity',return_value='owned.example.ts.net'),patch('project_worktrees.canonical'),patch.object(a,'state_for',return_value={'schema_version':4,'root':str(self.base/'another-backend')}):
            with self.assertRaises(a.AppError):mb.inspect(self.mobile)
            with self.assertRaises(a.AppError):mb.bind(self.mobile,self.backend,'https://owned.example.ts.net/projects/notes-api/api')
        self.assertEqual((self.mobile/mb.CONFIG).read_bytes(),before)

    def test_historical_validator_refuses_both_new_contracts(self):
        source=subprocess.run(['git','show','main:scripts/project_manifest.py'],cwd=a.REPO,capture_output=True,text=True,check=True).stdout
        old=types.ModuleType('old_manifest');old.__file__=str(a.REPO/'scripts/project_manifest.py')
        exec(compile(source,'baseline project_manifest.py','exec'),old.__dict__)
        for root in (self.backend,self.mobile):
            result,contract,code=old.validate_project(root)
            self.assertEqual(code,1);self.assertIsNone(contract)
            self.assertEqual(result['errors'][0]['code'],'version')

    def test_stop_removes_only_api_and_db_activation_and_retains_source(self):
        with groups.scope(self.backend,self.value):groups.reserve(self.backend,self.value)
        calls=[]
        with patch.object(a,'stop',side_effect=lambda root,**kw:calls.append(Path(root).name)),patch.object(a,'object_owned',return_value=False),patch.object(groups,'network',return_value=False),patch.object(db,'state',return_value={'owned':True}),patch.object(db,'stop',side_effect=lambda state:calls.append('db')):
            result=groups.stop(self.backend)
        self.assertEqual(calls,['api','db']);self.assertTrue(result['source_retained'])
        self.assertTrue((self.backend/'api/src/fastapi_app/main.py').is_file())

    def test_api_only_gateway_has_no_web_fallback(self):
        s={'id':'notes-api'}
        with patch.object(groups,'probe',return_value={'api':{'port':1234}}):
            self.assertEqual(groups.upstream(s,'/projects/notes-api/api/v1/notes')['port'],1234)
            self.assertFalse(groups.upstream(s,'/projects/notes-api/'))
            self.assertFalse(groups.upstream(s,'/projects/notes-api/api/private'))
        with patch.object(groups,'probe',return_value=None):self.assertIsNone(groups.upstream(s,'/projects/notes-api/api/v1/notes'))

    def test_start_initializes_no_data_and_publishes_only_after_db_and_api(self):
        calls=[]
        cold={'api':{'health':'unknown','active':False,'operation_busy':False}}
        ready={'api':{'health':'ready','active':True,'operation_busy':False}}
        with patch.object(db,'require_storage'),patch.object(db,'state',return_value={'fixture':True}),patch.object(db,'acquire'),patch.object(db,'start',side_effect=lambda _:calls.append('db')),patch.object(db,'ready',return_value=True),patch.object(groups,'observe',side_effect=[cold,ready]),patch.object(groups,'network'),patch.object(a,'object_owned',return_value=False),patch.object(a,'start',side_effect=lambda *args,**kw:calls.append('api')),patch.object(a,'route_info'),patch.object(a,'ensure_ingress',side_effect=lambda:calls.append('route')),patch.object(groups,'status',return_value={'route':{'state':'configured'},'state':'ready'}),patch.object(db,'create') as initialize:
            groups.start(self.backend)
        self.assertEqual(calls,['db','api','route']);initialize.assert_not_called()

    def test_schema_tamper_does_not_execute(self):
        original=copy.deepcopy(self.value)
        for change in [lambda v:v['components'].update(web={}),lambda v:v.update(schema_version=4),lambda v:v['components']['api'].update(depends_on=[]),lambda v:v['database'].update(storage='foreign')]:
            value=copy.deepcopy(original);change(value);a.save(self.backend/'.gptclaw/project.yaml',value)
            with patch.object(a,'command') as command:
                self.assertNotEqual(a.validate_project(self.backend)[2],0);command.assert_not_called()
        a.save(self.backend/'.gptclaw/project.yaml',original)


if __name__=='__main__':unittest.main(verbosity=2)
