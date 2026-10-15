#!/usr/bin/env python3
"""Behavior tests for typed lifecycle isolation and interruption; synthetic native engine."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import private_apps as app
import project_controls as ctl
import project_groups as groups


class Controls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='controls-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)/'projects'; self.base.mkdir()
        for key, value in [('PROJECTS', self.base), ('STORE', self.base/'.gptclaw-runtime/v1'), ('UNITS', self.base/'units')]:
            context = patch.object(app, key, value); context.start(); self.addCleanup(context.stop)
        app.UNITS.mkdir()
        self.root = Path(app.create('sample', template='notes', template_version='1.0.0')['root'])
        self.value = app.target(self.root)[1]
        with patch.object(app, 'available', return_value=True), groups.scope(self.root, self.value) as resolved:
            self.group = groups.reserve(self.root, self.value)
            self.group.update(phase='ready', health_ready=True); groups.save(self.group)
            self.children = resolved
            self.native = {}
            for name, (path, contract) in resolved.items():
                state = app.reserve(path, contract)
                state.update(image='sha256:'+'1'*64, phase='ready', health_ready=True, operation_result='passed', unit_sha256='1'*64)
                app.save(app.STORE/(state['id']+'.json'), state)
                self.native[state['name']] = {'Id': name+'-instance-1', 'Image': state['image'],
                                             'State': {'Running': True, 'Paused': False, 'StartedAt': 'first'}}
        self.commands = []
        for key, side_effect in [('command', self.command), ('json_command', self.json_command),
                                 ('object_owned', self.owned), ('inspect_service', self.inspect_service)]:
            context = patch.object(app, key, side_effect=side_effect); context.start(); self.addCleanup(context.stop)
        context = patch.object(app, 'verify_unit'); context.start(); self.addCleanup(context.stop)

    def owned(self, kind, name, token):
        if kind == 'container':
            return name in self.native
        return False

    def json_command(self, argv):
        return [copy.deepcopy(self.native[argv[-1]])]

    def inspect_service(self, s, contract):
        obj = self.native.get(s['name'])
        active = bool(obj and (obj['State']['Running'] or obj['State']['Paused']))
        return active, bool(active and not obj['State']['Paused'])

    def command(self, argv, **kwargs):
        self.commands.append(argv)
        if argv[:3] == ['systemctl', '--user', 'stop']:
            self.native[argv[3].removesuffix('.service')]['State']['Running'] = False
        if argv[:3] == ['systemctl', '--user', 'start']:
            obj = self.native[argv[3].removesuffix('.service')]
            obj['State']['Running'] = True; obj['Id'] += '-replacement'
        if argv[:2] in [['podman', 'pause'], ['podman', 'unpause']]:
            self.native[argv[2]]['State']['Paused'] = argv[1] == 'pause'
            self.native[argv[2]]['State']['Running'] = argv[1] == 'unpause'
        return subprocess.CompletedProcess(argv, 0, '', '')

    def test_web_restart_preserves_api_identity_network_and_source(self):
        before = copy.deepcopy(self.native)
        network = app.state_for('sample')['network']
        result = ctl.execute(self.root, 'restart', 'web')
        self.assertEqual(result['state'], 'succeeded')
        api, web = (app.state_for(self.group['components'][name])['name'] for name in ('api', 'web'))
        self.assertEqual(self.native[api], before[api])
        self.assertNotEqual(self.native[web]['Id'], before[web]['Id'])
        self.assertEqual(app.state_for('sample')['network'], network)
        self.assertTrue((self.root/'api/uv.lock').is_file())
        self.assertFalse(ctl.guard_path('sample').exists())
        self.assertFalse(any(cmd[:2] == ['podman', 'rm'] for cmd in self.commands))

    def test_pause_consumer_first_resume_dependency_first_same_instances(self):
        before = {name: obj['Id'] for name, obj in self.native.items()}
        ctl.execute(self.root, 'pause')
        commands = [c for c in self.commands if c[:2] == ['podman', 'pause']]
        self.assertTrue(commands[0][2].endswith('-web'))
        self.assertTrue(commands[1][2].endswith('-api'))
        self.assertEqual(app.state_for('sample')['phase'], 'paused')
        self.assertTrue(all(not row['State']['Running'] and row['State']['Paused'] for row in self.native.values()))
        self.assertFalse(app.state_for('sample')['health_ready'])
        with self.assertRaises(app.AppError) as error: ctl.execute(self.root, 'restart', 'web')
        self.assertEqual(error.exception.code, 'control-paused')
        ctl.execute(self.root, 'resume')
        commands = [c for c in self.commands if c[:2] == ['podman', 'unpause']]
        self.assertTrue(commands[0][2].endswith('-api'))
        self.assertEqual({name: obj['Id'] for name, obj in self.native.items()}, before)
        self.assertTrue(app.state_for('sample')['health_ready'])

    def test_completion_write_failure_retains_unknown_guard_without_replay(self):
        ident='6'*32;journal=app.STORE/'control-journals'/(ident+'.json')
        before=copy.deepcopy(self.native);save=app.save
        def fail_completion(path,value):
            if Path(path)==journal and value.get('state')=='succeeded':raise OSError('synthetic write failure')
            return save(path,value)
        with patch.object(app,'save',side_effect=fail_completion),self.assertRaises(OSError):
            ctl.execute(self.root,'restart','web',operation_id=ident)
        web=app.state_for(self.group['components']['web'])['name']
        self.assertNotEqual(self.native[web]['Id'],before[web]['Id'])
        self.assertTrue(ctl.guard_path('sample').exists())
        self.assertEqual(app.read_json(journal)['state'],'unknown')
        after=copy.deepcopy(self.native);count=len(self.commands)
        with self.assertRaises(app.AppError):ctl.execute(self.root,'restart','web')
        self.assertEqual(len(self.commands),count)
        ctl.reconcile(self.root,ident,'sample')
        self.assertEqual(self.native,after)
        self.assertFalse(ctl.guard_path('sample').exists())

    def test_changed_source_after_preview_refuses_before_effects(self):
        generation = ctl.capabilities(self.root)['generation']
        (self.root/'api/README.md').write_text('changed source')
        with self.assertRaises(app.AppError) as error:
            ctl.execute(self.root, 'restart', 'api', expected=generation)
        self.assertEqual(error.exception.code, 'control-changed')
        self.assertEqual(self.commands, [])

    def test_partial_pause_requires_reconciliation_then_stop_unfreezes_owned_instances(self):
        ident='e'*32
        before={name:row['Id'] for name,row in self.native.items()}
        api=app.state_for(self.group['components']['api'])['name']
        web=app.state_for(self.group['components']['web'])['name']
        def fail_second(argv,**kwargs):
            if argv==['podman','pause',api]:raise app.AppError('timeout')
            return self.command(argv,**kwargs)
        with patch.object(app,'command',side_effect=fail_second),self.assertRaises(app.AppError):
            ctl.execute(self.root,'pause',operation_id=ident)
        self.assertTrue(self.native[web]['State']['Paused']);self.assertFalse(self.native[api]['State']['Paused'])
        self.assertFalse(app.state_for('sample')['health_ready']);self.assertTrue(ctl.guard_path('sample').exists())
        with self.assertRaises(app.AppError):ctl.execute(self.root,'resume')
        recovered=ctl.reconcile(self.root,ident,'sample')
        self.assertTrue(recovered['components']['web']['paused']);self.assertFalse(recovered['components']['api']['paused'])
        self.assertFalse(ctl.guard_path('sample').exists())
        with self.assertRaises(app.AppError) as error:ctl.execute(self.root,'resume')
        self.assertEqual(error.exception.code,'control-recovery')
        def stop(*args,**kw):
            self.assertFalse(any(row['State']['Paused'] for row in self.native.values()))
            for row in self.native.values():row['State']['Running']=False
        with patch.object(app,'stop',side_effect=stop):result=ctl.execute(self.root,'stop')
        self.assertEqual(result['state'],'succeeded')
        self.assertEqual({name:row['Id'] for name,row in self.native.items()},before)
        self.assertFalse(ctl.guard_path('sample').exists())

    def test_dependency_refusal_does_not_stop_target(self):
        api = app.state_for(self.group['components']['api'])
        self.native[api['name']]['State']['Running'] = False
        with self.assertRaises(app.AppError) as error: ctl.execute(self.root, 'restart', 'web')
        self.assertEqual(error.exception.code, 'control-dependency')
        self.assertEqual(self.commands, [])

    def test_fail_after_stop_retains_durable_guard_and_journal(self):
        def command(argv, **kwargs):
            if argv[:3] == ['systemctl', '--user', 'start']: raise app.AppError('timeout')
            return self.command(argv, **kwargs)
        ident = 'a'*32
        with patch.object(app, 'command', side_effect=command):
            with self.assertRaises(app.AppError): ctl.execute(self.root, 'restart', 'web', operation_id=ident)
        self.assertTrue(ctl.guard_path('sample').exists())
        record = app.read_json(app.STORE/'control-journals'/(ident+'.json'))
        self.assertEqual(record['state'], 'unknown')
        self.assertIn('stop', [stage['stage'] for stage in record['stages']])
        with self.assertRaises(app.AppError) as error:
            with app.locked('sample'): pass
        self.assertEqual(error.exception.code, 'control-recovery')
        self.assertFalse(app.state_for('sample')['health_ready'])
        recovered = ctl.reconcile(self.root, ident, 'sample')
        self.assertEqual(recovered['state'], 'reconciled')
        self.assertFalse(ctl.guard_path('sample').exists())
        with app.locked('sample'): pass

    def test_existing_cli_lock_blocks_control(self):
        with app.locked('sample'):
            with self.assertRaises(app.AppError) as error: ctl.execute(self.root, 'restart', 'api')
        self.assertEqual(error.exception.code, 'busy')
        self.assertEqual(self.commands, [])

    def test_capability_matrix_is_per_profile_and_component(self):
        def row(active=True, paused=False):
            return {'active': active, 'ready': active and not paused, 'paused': paused, 'busy': False, 'receipt':{'owned':True,'expires_at':ctl.time.time()+3600}}
        for version, rows, unavailable in [(1, {'web':row()}, set()), (2, {'api':row()}, set()),
            (7, {'api':row()}, set()), (3, {'api':row(),'web':row()}, set()), (4, {'api':row(),'web':row(),'db':row()}, {'pause','resume'}),
            (8, {'api':row(),'db':row()}, {'pause','resume'}), (6, {'metro':row()}, {'pause','resume','rebuild'}),
            (9, {'metro':row()}, {'pause','resume','rebuild'})]:
            for verb in ctl.ACTIONS:
                reason = ctl.eligibility({'schema_version':version}, rows, verb)
                if verb in unavailable: self.assertEqual(reason,'control-unsupported')
                elif verb != 'resume': self.assertIsNone(reason)
            for name in rows:
                self.assertIsNone(ctl.eligibility({'schema_version':version},rows,'restart',name))
            with self.assertRaises(app.AppError):ctl.eligibility({'schema_version':version},rows,'restart','worker')

    def test_failed_build_leaves_instances_and_publication_unchanged(self):
        before = copy.deepcopy(self.native)
        with patch.object(ctl, 'build_sources', side_effect=app.AppError('command')):
            with self.assertRaises(app.AppError): ctl.execute(self.root, 'rebuild')
        self.assertEqual(self.native, before)
        self.assertTrue(app.state_for('sample')['health_ready'])
        self.assertEqual(self.commands, [])

    def metro_operation(self, action, *, seconds=300, active=True, component=None):
        import metro_sessions as metro
        old={'expires_at':ctl.time.time()+seconds,'origin':'http://synthetic.example.ts.net:8443'}
        rows={'metro':{'active':active,'ready':active,'paused':False,'busy':False,'receipt':old,'generation':'owned'}}
        value={'schema_version':9,'project':{'id':'sample'}}
        calls=[]
        def stop(root):
            calls.append(('stop',root));rows['metro'].update(active=False,ready=False)
        def start(root, **kw):
            calls.append(('start',root,kw));rows['metro'].update(active=True,ready=True)
        with patch.object(app,'target',return_value=(self.root,value)),patch.object(ctl,'inspect',return_value=(self.root,value,None,rows,'generation')),patch.object(ctl,'runtime_rows',return_value=(None,rows)),patch.object(metro,'stop',side_effect=stop),patch.object(metro,'start',side_effect=start):
            result=ctl.execute(self.root,action,component)
        return result,calls,old

    def test_running_metro_start_is_noop_even_near_absolute_expiry(self):
        before=copy.deepcopy(self.native)
        result,calls,_=self.metro_operation('start',seconds=30)
        self.assertEqual(result['state'],'succeeded');self.assertEqual(calls,[])
        self.assertEqual(self.native,before);self.assertEqual(self.commands,[])

    def test_metro_observation_refresh_keeps_intent_generation_but_failed_protocol_is_not_ready(self):
        import metro_sessions as metro
        owned={'phase':'running','expires_at':ctl.time.time()+300,'canonical_key':'canonical',
               'input_digest':'inputs','name':'metro-sample','token':'owned',
               'observations':{'protocol':{'state':'ready','observed_at':1}}}
        identity={'key':'canonical','root_identity':[1,2]}
        control={'root_identity':[1,2],'mount_identities':{'src':[3,4]}}
        with patch.object(metro,'load',return_value=owned),patch.object(metro,'admitted'),patch.object(metro,'control',return_value=control),patch.object(metro.contract,'inputs'),patch.object(metro,'require_idle'),patch.object(metro.worktrees,'canonical',return_value=identity),patch.object(metro,'mount_identities',return_value=control['mount_identities']),patch.object(metro,'hashes',return_value={}),patch.object(metro,'digest',return_value='inputs'),patch.object(metro,'verify_unit'),patch.object(metro,'ownership',return_value='owned'),patch.object(metro,'result',return_value={'state':'ready'}) as descriptor:
            first=ctl.runtime_rows(self.root,{'schema_version':9,'project':{'id':'sample'}})[1]['metro']
            owned['observations']['protocol']['observed_at']=2
            refreshed=ctl.runtime_rows(self.root,{'schema_version':9,'project':{'id':'sample'}})[1]['metro']
            self.assertEqual(first['generation'],refreshed['generation']);self.assertTrue(refreshed['ready'])
            descriptor.return_value={'state':'failed'}
            failed=ctl.runtime_rows(self.root,{'schema_version':9,'project':{'id':'sample'}})[1]['metro']
            self.assertTrue(failed['active']);self.assertFalse(failed['ready'])

    def test_metro_restart_retains_transport_and_absolute_expiry_without_backend_effects(self):
        before=copy.deepcopy(self.native)
        result,calls,old=self.metro_operation('restart',component='metro')
        self.assertEqual(result['state'],'succeeded')
        self.assertEqual([call[0] for call in calls],['stop','start'])
        self.assertEqual(calls[1][2]['transport'],'tailnet-http')
        self.assertEqual(calls[1][2]['lease_expiry'],old['expires_at'])
        self.assertLessEqual(calls[1][2]['ttl_seconds'],300)
        self.assertEqual(self.native,before);self.assertEqual(self.commands,[])

    def test_metro_near_expiry_can_stop_but_cannot_start_or_restart(self):
        result,calls,_=self.metro_operation('stop',seconds=30)
        self.assertEqual(result['state'],'succeeded');self.assertEqual([c[0] for c in calls],['stop'])
        for action,active in [('start',False),('restart',True)]:
            with self.subTest(action=action),self.assertRaises(app.AppError) as error:
                self.metro_operation(action,seconds=30,active=active)
            self.assertEqual(error.exception.code,'control-expired')

    def test_database_restart_retains_generation_and_application_instances(self):
        import project_database as db
        value=copy.deepcopy(self.value);value['schema_version']=4
        value['components']['db']={'adapter':'postgres-v1','depends_on':[]}
        value['components']['api']['depends_on']=['db']
        owned={'project':'sample','token':'owned-token','active':'generation-one','epoch':'credentials-one',
               'revision':'0001','blocked':False,'operation':None}
        before=copy.deepcopy(self.native);calls=[]
        rows={'db':{'receipt':owned}}
        with patch.object(db,'state',return_value=owned),patch.object(db,'active',return_value=True),patch.object(db,'busy',return_value=False),patch.object(db,'ready',return_value=True),patch.object(db,'stop',side_effect=lambda s:calls.append(('stop',s['active']))),patch.object(db,'start',side_effect=lambda s:calls.append(('start',s['active']))):
            ctl.restart_selected(self.root,value,self.group,rows,'db',lambda *_:None)
        self.assertEqual(calls,[('stop','generation-one'),('start','generation-one')])
        self.assertEqual(self.native,before)
        self.assertEqual(owned['epoch'],'credentials-one');self.assertEqual(self.commands,[])

    def test_database_dependency_failure_reports_without_cascade(self):
        import project_database as db
        value=copy.deepcopy(self.value);value['schema_version']=4
        owned={'blocked':False}
        with patch.object(app,'DEADLINE',0),patch.object(db,'busy',return_value=False),patch.object(db,'stop'),patch.object(db,'start'),patch.object(db,'ready',return_value=True),patch.object(ctl,'runtime_rows',return_value=(self.group,{'api':{'ready':False},'web':{'ready':True},'db':{'ready':True}})):
            with self.assertRaises(app.AppError) as failure:
                ctl.restart_selected(self.root,value,self.group,{'db':{'receipt':owned}},'db',lambda *_:None)
            self.assertEqual(failure.exception.code,'control-dependency')
        self.assertFalse(app.state_for('sample')['health_ready'])
        self.assertEqual(self.commands,[])

    def test_running_rebuild_builds_before_replacement_and_retains_siblings(self):
        stages=[]
        def build(*args):
            stages.append('built')
            self.assertEqual(self.commands,[])
            return {'api':None,'web':None}
        with patch.object(ctl,'build_sources',side_effect=build):
            result=ctl.execute(self.root,'rebuild',stage=lambda phase,component:stages.append((phase,component)))
        self.assertEqual(result['state'],'succeeded')
        self.assertLess(stages.index('built'),stages.index(('stop','api')))
        self.assertLess(stages.index(('stop','api')),stages.index(('stop','web')))

    def test_rebuild_stopped_project_does_not_start_it(self):
        for obj in self.native.values():obj['State']['Running']=False
        with patch.object(ctl,'build_sources',return_value={'api':{},'web':{}}) as build, patch.object(ctl,'install_prepared'):
            result=ctl.execute(self.root,'rebuild')
        self.assertEqual(result['state'],'succeeded');build.assert_called_once()
        self.assertFalse(any(obj['State']['Running'] for obj in self.native.values()))
        self.assertEqual(self.commands,[])

    def test_successful_build_publication_retains_prior_generated_outputs(self):
        child, contract=self.children['web']
        state=app.state_for(self.group['components']['web'])
        self.native[state['name']]['State']['Running']=False
        old=child/'node_modules';old.mkdir();(old/'previous.txt').write_text('old generated output')
        staged=app.STORE/'control-builds'/('b'*32)/'web';staged.mkdir(parents=True)
        incoming=staged/'node_modules';incoming.mkdir();(incoming/'new.txt').write_text('new generated output')
        before=ctl.source_files(child)
        prepared={'directory':str(staged),'source':ctl.digest(before),'image':'sha256:'+'1'*64,'toolchain_hash':'a'*64}
        with patch.object(app,'dependency_digest',return_value='c'*64):
            ctl.install_prepared(state,contract,prepared,lambda *_:None)
        self.assertEqual((child/'node_modules/new.txt').read_text(),'new generated output')
        self.assertEqual((staged/'previous-node_modules/previous.txt').read_text(),'old generated output')
        self.assertEqual(ctl.source_files(child),before)
        self.assertEqual(app.state_for(state['id'])['prepared_digest'],'c'*64)

    @unittest.skipUnless(hasattr(os,'fork'),'Linux process-death evidence')
    def test_worker_death_leaves_guard_until_explicit_inspection(self):
        import signal
        ident='f'*32
        pid=os.fork()
        if pid==0:
            def terminate(phase,component):
                if phase=='validated':os.kill(os.getpid(),signal.SIGKILL)
            ctl.execute(self.root,'restart','api',operation_id=ident,stage=terminate)
            os._exit(0)
        _,result=os.waitpid(pid,0)
        self.assertTrue(os.WIFSIGNALED(result));self.assertEqual(os.WTERMSIG(result),signal.SIGKILL)
        self.assertTrue(ctl.guard_path('sample').exists())
        with self.assertRaises(app.AppError):ctl.execute(self.root,'restart','api')
        ctl.reconcile(self.root,ident,'sample')
        self.assertFalse(ctl.guard_path('sample').exists())
        self.assertEqual(self.commands,[])

    def test_unknown_component_and_remote_task_rejected(self):
        for action, component in [('shell', None), ('restart', 'worker'), ('open-task', None)]:
            with self.assertRaises(app.AppError): ctl.execute(self.root, action, component)
        self.assertEqual(self.commands, [])

    def test_source_snapshot_accepts_dynamic_routes_but_rejects_symlinks_and_secrets(self):
        folder = self.root/'web/app/[id]';folder.mkdir(parents=True)
        (folder/'page.tsx').write_text('export default 1')
        self.assertIn('web/app/[id]/page.tsx',ctl.source_files(self.root))
        (folder/'link').symlink_to('/etc/hostname')
        with self.assertRaises(app.AppError):ctl.source_files(self.root)
        (folder/'link').unlink();(folder/'.env').write_text('synthetic=true')
        with self.assertRaises(app.AppError):ctl.source_files(self.root)


if __name__ == '__main__': unittest.main(verbosity=2)
