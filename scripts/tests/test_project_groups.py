#!/usr/bin/env python3
"""Isolated group contract, ownership, lifecycle and proxy regressions."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import private_apps as a
import project_groups as g
import project_toolchains as tools
import project_templates as templates


class Groups(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name)/'projects';self.base.mkdir()
        for key,value in [('PROJECTS',self.base),('STORE',self.base/'.gptclaw-runtime/v1'),('UNITS',self.base/'units')]:
            mock=patch.object(a,key,value);mock.start();self.addCleanup(mock.stop)
        a.UNITS.mkdir()
        self.root=Path(a.create('notes',template='notes',template_version='1.0.0')['root'])
        self.value=a.target(self.root)[1]

    def save_contract(self,value):a.save(self.root/'.gptclaw/project.yaml',value)

    def runtime(self):
        with g.scope(self.root,self.value) as children:
            group=g.reserve(self.root,self.value)
            for name,(path,value) in children.items():
                s=a.reserve(path,value);s.update(image='sha256:'+'1'*64,phase='stopped',health_ready=False)
                a.save(a.STORE/(s['id']+'.json'),s)
        return group,children

    def test_generation_is_explicit_and_observation_only(self):
        with patch.object(a,'command') as command:
            self.assertEqual(a.validate_project(self.root)[2],0)
            templates.validate_provenance(self.root)
            self.assertEqual(templates.resolve()[0]['id'],'nextjs')
            command.assert_not_called()
        self.assertTrue((self.root/'api/docs/python-standards.md').is_file())
        self.assertEqual(tools.selection(self.root/'api')['profile']['profile'],'python-uv')
        with self.assertRaises(a.AppError):a.create('notes',template='notes',template_version='1.0.0')

    def test_component_cannot_bypass_group_lock_or_target(self):
        for name in g.ORDER:
            with self.assertRaises(a.AppError):a.start(self.root/name)
            with self.assertRaises(a.AppError):a.quality_app(self.root/name)
        with a.locked('notes'):
            with self.assertRaises(a.AppError) as error:g.dispatch(self.root,'test')
            self.assertEqual(error.exception.code,'busy')

    def test_bad_topology_paths_profiles_and_versions_refused(self):
        mutations=[lambda v:v.update(schema_version=4),lambda v:v['components']['web'].update(root='../api'),
                   lambda v:v['components']['web'].update(root='api'),lambda v:v['components']['web'].update(root='api/src'),
                   lambda v:v['components']['api'].update(depends_on=['web']),lambda v:v['components'].update(worker={}),
                   lambda v:v['components']['web'].update(adapter='fastapi-v1')]
        for mutate in mutations:
            value=copy.deepcopy(self.value);mutate(value);self.save_contract(value)
            with patch.object(a,'command') as command:
                self.assertNotEqual(a.validate_project(self.root)[2],0);command.assert_not_called()
        self.save_contract(self.value)
        (self.root/'web').rename(self.root/'retained');(self.root/'web').symlink_to(self.root/'retained')
        self.assertNotEqual(a.validate_project(self.root)[2],0)

    def test_port_ids_and_profile_are_independent(self):
        with patch.object(a,'available',return_value=True):s,children=self.runtime()
        api=a.state_for(s['components']['api']);web=a.state_for(s['components']['web'])
        self.assertNotEqual(api['port'],web['port']);self.assertNotEqual(api['name'],web['name'])
        self.assertEqual(api['group'],'notes');self.assertEqual(len(a.states()),2)
        self.assertEqual(api['network'],web['network'])
        self.assertEqual(api['adapter'],'python')
        text=a.unit_text(web,children['web'][1],'example.ts.net')
        self.assertIn('Network=gptclaw-group-notes',text);self.assertIn('--network-alias=web',text)
        self.assertIn('Environment=GPTCLAW_PROJECT_ID=notes',text)
        self.assertIn('GPTCLAW_API_READY_URL=http://api:8000/projects/notes/api/ready',text)
        self.assertIn('PublishPort=127.0.0.1:',text)
        self.assertNotIn('/home/forge:',text)

    def test_schema2_group_receipt_refuses_tampered_ownership(self):
        with patch.object(a,'available',return_value=True):s,_=self.runtime()
        for updates in [{'network':'foreign'},{'root':'/etc'},{'components':{'api':'foreign','web':'foreign'}},{'phase':'invented'},{'token':'bad'}]:
            with self.assertRaises(a.AppError):g.valid_state({**s,**updates})

    def test_start_api_first_and_publish_after_both(self):
        calls=[]
        def start(root,**kwargs):
            calls.append(Path(root).name)
            self.assertEqual(a.state_for('notes')['health_ready'],False)
            return {'state':'ready'}
        cold={n:{'health':'unknown','active':False,'operation_busy':False} for n in g.ORDER}
        ready={n:{'health':'ready','active':True,'operation_busy':False} for n in g.ORDER}
        with patch.object(a,'object_owned',return_value=False),patch.object(g,'observe',side_effect=[cold,ready]),patch.object(g,'network'),patch.object(a,'start',side_effect=start),patch.object(a,'ensure_ingress') as ingress,patch.object(g,'status',return_value={'state':'ready','route':{'state':'configured'}}),patch.object(a,'route_info'):
            result=g.start(self.root)
        self.assertEqual(calls,['api','web']);ingress.assert_called_once();self.assertTrue(result['changed'])
        self.assertEqual(a.state_for('notes')['phase'],'ready')

    def test_second_start_failure_cleans_reverse_order_without_publication(self):
        calls=[]
        def start(root,**kwargs):
            if Path(root).name=='web':raise a.AppError('health')
        def stop(root,**kwargs):calls.append(Path(root).name)
        cold={n:{'health':'unknown','active':False,'operation_busy':False} for n in g.ORDER}
        with patch.object(a,'object_owned',return_value=False),patch.object(g,'observe',return_value=cold),patch.object(g,'network',return_value=False),patch.object(a,'start',side_effect=start),patch.object(a,'stop',side_effect=stop),patch.object(a,'ensure_ingress') as ingress,patch.object(a,'route_info'):
            with self.assertRaises(a.AppError):g.start(self.root)
        self.assertEqual(calls,['web','api']);ingress.assert_not_called()
        state=a.state_for('notes');self.assertFalse(state['health_ready']);self.assertEqual(state['error'],'health')

    def test_stop_attempts_both_when_first_fails_and_retains_source(self):
        with patch.object(a,'available',return_value=True):self.runtime()
        calls=[]
        def stop(root,**kwargs):
            calls.append(Path(root).name)
            self.assertFalse(a.state_for('notes')['health_ready'])
            if Path(root).name=='web':raise a.AppError('conflict')
        with patch.object(a,'object_owned',return_value=False),patch.object(g,'network',return_value=False),patch.object(a,'stop',side_effect=stop):
            with self.assertRaises(a.AppError):g.stop(self.root)
        self.assertEqual(calls,['web','api']);self.assertTrue((self.root/'api/uv.lock').exists())
        self.assertEqual(a.state_for('notes')['cleanup_errors'],{'web':'conflict'})

    def test_unknown_network_is_not_removed(self):
        with patch.object(a,'available',return_value=True):s,children=self.runtime()
        with patch.object(a,'object_owned',side_effect=a.AppError('conflict')),patch.object(a,'command') as command:
            with self.assertRaises(a.AppError):g.network(s,create=True)
            command.assert_not_called()

    def test_interrupted_or_active_partial_start_requires_reconciliation(self):
        with patch.object(a,'available',return_value=True):s,_=self.runtime()
        for result in ['running','passed']:
            s.update(phase='starting',operation_result=result);g.save(s)
            observed={n:{'health':'unhealthy','active':n=='api','operation_busy':False} for n in g.ORDER}
            with patch.object(g,'observe',return_value=observed),patch.object(g,'network') as network:
                with self.assertRaises(a.AppError):g.start(self.root)
                network.assert_not_called()

    def test_mutations_require_explicit_component_and_stopped_group(self):
        with patch.object(a,'available',return_value=True):s,_=self.runtime()
        for action in ['deps','toolchain','format','logs']:
            with self.assertRaises(a.AppError):g.dispatch(self.root,action)
        ready={n:{'health':'ready','active':True,'operation_busy':False} for n in g.ORDER}
        with patch.object(g,'observe',return_value=ready):
            with self.assertRaises(a.AppError):g.dispatch(self.root,'format','api')

    def test_namespace_selection_and_unhealthy_group_block(self):
        with patch.object(a,'available',return_value=True):s,_=self.runtime()
        with patch.object(a,'verify_unit'),patch.object(a,'healthy',return_value=True):
            self.assertEqual(g.upstream(s,'/projects/notes/api/v1/notes')['component'],'api')
            self.assertEqual(g.upstream(s,'/projects/notes/api-other/')['component'],'web')
            self.assertFalse(g.upstream(s,'/projects/notes/api/admin'))
        with patch.object(a,'verify_unit'),patch.object(a,'healthy',return_value=False):
            self.assertIsNone(g.upstream(s,'/projects/notes/'))

    def test_parent_hooks_idempotent_and_foreign_hooks_preserved(self):
        directory=self.root/'.git/hooks';directory.mkdir(parents=True)
        first=g.install_hooks(self.root);self.assertTrue(first['changed'])
        self.assertFalse(g.install_hooks(self.root)['changed'])
        hook=directory/'pre-commit';hook.write_text('keep foreign hook')
        with self.assertRaises(a.AppError):g.install_hooks(self.root)
        self.assertEqual(hook.read_text(),'keep foreign hook')

    def test_group_template_inventory_and_snapshot(self):
        paths=a.provider_bundle()
        self.assertTrue((paths/'scripts/project_groups.py').is_file())
        self.assertTrue((paths/'schemas/project/v3.schema.json').is_file())
        self.assertTrue((paths/'config/templates/v3.json').is_file())


if __name__=='__main__':unittest.main(verbosity=2)
