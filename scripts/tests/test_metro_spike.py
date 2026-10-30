#!/usr/bin/env python3
"""Offline SDK spike admission, filtered source and ownership failure cases."""
import contextlib
from datetime import datetime, timedelta, timezone
import hashlib
import copy
import json
import os
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import metro_spike as spike
import metro_security as security
import project_mobile as mobile
import private_apps as app


class SpikeTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        self.root=Path(temp.name)/'source';self.root.mkdir()
        for name in spike.ROOT_FILES:(self.root/name).write_text('{"expo":{}}' if name=='app.json' else 'synthetic')
        (self.root/'src').mkdir();(self.root/'src/index.tsx').write_text('export default null;')
        (self.root/'node_modules').mkdir()
        self.origin='https://'+spike.HOST+':8443'
    def patch(self,target,name,value):
        p=patch.object(target,name,value);p.start();self.addCleanup(p.stop)
    def fixture_policy(self):
        # Simulations need valid synthetic dates, not a live runtime exception.
        value=json.loads((app.REPO/'config/metro/runtime-security-v1.json').read_text())
        now=datetime.now(timezone.utc)
        value['approved_at']=(now-timedelta(minutes=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
        value['expires_at']=(now+timedelta(minutes=10)).strftime('%Y-%m-%dT%H:%M:%SZ')
        return security.policy(value,approved=False)
    def prepare_plan(self):
        self.patch(spike,'TARGETS',{self.root})
        self.patch(app,'target',lambda root:(self.root,{'schema_version':5,'project':{'id':'synthetic'}}))

    def test_watching_is_explicit_runtime_only_and_keeps_all_bounds(self):
        defaults=spike.container_options(self.root,self.root,60)
        watching=spike.container_options(self.root,self.root,60,watch=True)
        self.assertIn('CI=1',defaults);self.assertNotIn('CI=false',defaults)
        self.assertIn('CI=false',watching);self.assertNotIn('CI=1',watching)
        self.assertEqual([v for v in defaults if v!='CI=1'],[v for v in watching if v!='CI=false'])
        for flag in ['--read-only','--http-proxy=false','--memory=1536m','--cpus=1','--pids-limit=256',
                     '--log-driver=none','EXPO_NO_TELEMETRY=1','EXPO_NO_DOTENV=1','--timeout=60']:
            self.assertIn(flag,watching)
        with self.assertRaises(app.AppError):
            spike.container_options(self.root,self.root,60,watch=1)

    def test_ephemeral_sdk_input_is_closed_and_never_an_operator_tty(self):
        runner=spike.EphemeralOutput([sys.executable,'-c',
              "import sys; assert not sys.stdin.isatty(); assert not sys.stdout.isatty(); assert sys.stdin.read()==''"])
        runner.finish()
        self.assertEqual(runner.process.returncode,0)
        self.assertEqual(runner.output,b'')

    def test_ephemeral_output_is_bounded_and_evidence_cannot_contain_source_text(self):
        runner=spike.EphemeralOutput([sys.executable,'-c',"import sys; sys.stdout.write('secret-canary ' * 20000 + ' EACCES'); sys.exit(1)"])
        runner.finish()
        self.assertEqual(len(runner.output),65536)
        result=runner.diagnostic()
        self.assertEqual(result['exit_code'],1);self.assertEqual(result['captured_bytes'],65536)
        self.assertNotIn('secret-canary',json.dumps(result));self.assertNotIn('output',result)
        self.assertEqual(runner.category(),'sdk-startup-or-protocol-failure')
    def test_real_operator_guard_denies_foreign_uid_and_root(self):
        for uid,euid in [(1001,1001),(0,0),(1002,0)]:
            with patch.object(os,'getuid',return_value=uid),patch.object(os,'geteuid',return_value=euid),self.assertRaises(app.AppError) as failure:spike.require_operator()
            self.assertEqual(failure.exception.code,'setup')
    def test_exact_owned_origin_only(self):
        self.assertEqual(spike.origin(self.origin+'/'),self.origin)
        for value in ['http://'+spike.HOST+':8443','https://foreign.ts.net:8443',self.origin+'/projects/',self.origin+'?target=http://localhost',self.origin+'#fragment','https://user@'+spike.HOST+':8443','https://'+spike.HOST+':443','https://'+spike.HOST+':bad']:
            with self.subTest(value=value),self.assertRaises(app.AppError):spike.origin(value)
    def test_readonly_plan_and_explicit_fixture_bound(self):
        self.prepare_plan()
        before=sorted(str(p) for p in self.root.rglob('*'))
        policy=copy.deepcopy(self.fixture_policy());policy['approved_at']=None
        with patch.object(security,'read_policy',return_value=policy),patch.object(app,'command',side_effect=AssertionError('no command')),patch.object(app,'save',side_effect=AssertionError('no writes')):
            result=spike.plan(self.root,self.origin,60)
        self.assertEqual(result['runtime_security'],'approval-pending');self.assertEqual(result['source_retained'],True)
        self.assertEqual(before,sorted(str(p) for p in self.root.rglob('*')))
        for seconds in [0,301,True]:
            with self.assertRaises(app.AppError):spike.plan(self.root,self.origin,seconds)
        with patch.object(spike,'TARGETS',set()),self.assertRaises(app.AppError):spike.plan(self.root,self.origin,60)
    def test_unapproved_run_denies_before_store_and_runtime_writes(self):
        self.prepare_plan()
        value=copy.deepcopy(self.fixture_policy());value['approved_at']=None
        def policy_reader(repo,now=None,approved=True):return security.policy(value,now,approved)
        with patch.object(security,'read_policy',side_effect=policy_reader),patch.object(spike,'require_operator',return_value=None),patch.object(spike,'source_inventory',return_value={}),patch.object(app,'locked',side_effect=AssertionError('no lock write')),patch.object(app,'command',side_effect=AssertionError('no process')):
            with self.assertRaises(security.AdmissionError):spike.run(self.root,self.origin,60)
    def test_filtered_view_excludes_credential_and_git_trees(self):
        for name in ['.git','.ssh','.aws']:
            (self.root/name).mkdir();(self.root/name/'secret').write_text('synthetic-canary')
        (self.root/'.env').write_text('synthetic-canary');(self.root/'unreviewed.js').write_text('synthetic-canary')
        inventory=spike.source_inventory(self.root)
        view=self.root.parent/'view';spike.prepare_view(self.root,view,inventory)
        self.assertEqual(set(inventory),spike.ROOT_FILES|{'src/index.tsx'})
        self.assertFalse(any(b'synthetic-canary' in p.read_bytes() for p in view.rglob('*') if p.is_file()))
    def test_symlink_hardlink_fifo_and_hidden_source_rejected_before_read(self):
        original=self.root/'src/index.tsx';original.unlink()
        for kind in ['symlink','hardlink','fifo','hidden']:
            path=self.root/'src'/('.secret' if kind=='hidden' else 'index.tsx')
            if kind=='symlink':path.symlink_to(self.root/'package.json')
            elif kind=='hardlink':os.link(self.root/'package.json',path)
            elif kind=='fifo':os.mkfifo(path)
            else:path.write_text('synthetic')
            with self.subTest(kind=kind),self.assertRaises((app.AppError,OSError)):spike.source_inventory(self.root)
            path.unlink()
    def test_directory_symlink_and_path_traversal_block(self):
        (self.root/'assets').symlink_to(self.root/'src',target_is_directory=True)
        with self.assertRaises(OSError):spike.source_inventory(self.root)
        with spike.directory(path=self.root) as parent:
            for value in ['../package.json','/etc/passwd','.env','src/../../package.json']:
                with self.assertRaises(app.AppError):spike.relative_bytes(parent,value)
    def test_source_change_and_file_size_bound_block_view(self):
        inventory=spike.source_inventory(self.root)
        (self.root/'src/index.tsx').write_text('changed')
        with self.assertRaises(app.AppError):spike.prepare_view(self.root,self.root.parent/'view',inventory)
        with patch.object(spike,'MAX_FILE',1),self.assertRaises(app.AppError):spike.source_inventory(self.root)
    def test_replaced_parent_symlink_cannot_be_followed(self):
        inventory=spike.source_inventory(self.root)
        (self.root/'src').rename(self.root/'original-src')
        (self.root/'src').symlink_to(self.root/'original-src',target_is_directory=True)
        with self.assertRaises(OSError):spike.prepare_view(self.root,self.root.parent/'view',inventory)
    def test_eas_update_or_plugin_config_block(self):
        for key in ['extra','updates','plugins']:
            (self.root/'app.json').write_text(json.dumps({'expo':{key:{}}}))
            with self.subTest(key=key),self.assertRaises(app.AppError):spike.source_inventory(self.root)
    def test_missing_container_still_cleans_owned_network(self):
        calls=[]
        with patch.object(spike,'ownership',side_effect=['absent','owned']),patch.object(app,'command',side_effect=lambda args,**kw:calls.append(args)):
            spike.cleanup('container','network','token')
        self.assertEqual(calls,[['podman','network','rm','network']])
    def test_foreign_resource_is_preserved_and_other_cleanup_attempted(self):
        calls=[]
        with patch.object(spike,'ownership',side_effect=['foreign','owned']),patch.object(app,'command',side_effect=lambda args,**kw:calls.append(args)),self.assertRaises(app.AppError):
            spike.cleanup('container','network','token')
        self.assertEqual(calls,[['podman','network','rm','network']])
    def test_unknown_exists_failure_is_not_absence(self):
        with patch.object(app,'command',return_value=SimpleNamespace(returncode=125)),self.assertRaises(app.AppError):spike.ownership('container','name','token')
    def test_runtime_argv_enforces_bounds_and_no_log_or_proxy_forwarding(self):
        options=spike.container_options(self.root,self.root,300)
        for flag in ['--timeout=300','--memory=1536m','--memory-swap=1536m','--cpus=1','--pids-limit=256','--cap-drop=all','--read-only','--http-proxy=false','--log-driver=none','--pull=never']:
            self.assertIn(flag,options)
        mounts=[options[i+1] for i,arg in enumerate(options) if arg=='--volume']
        self.assertTrue(all(m.endswith(':ro') for m in mounts))
        self.assertEqual(len(mounts),2)
        self.assertFalse(any(x in options for x in ['--env-host','--privileged','--replace','--network=host']))
    def simulate_run(self,failure=None):
        self.patch(spike,'require_operator',lambda:None)
        self.prepare_plan()
        self.patch(app,'STORE',self.root.parent/'runtime')
        policy=self.fixture_policy();policy=copy.deepcopy(policy)
        policy['approved_at']='2026-10-13T20:00:00Z'
        policy['lock_sha256']=hashlib.sha256((self.root/'pnpm-lock.yaml').read_bytes()).hexdigest()
        self.patch(security,'read_policy',lambda *args,**kwargs:policy)
        self.patch(spike,'prepared_dependencies',lambda *args:None)
        self.patch(spike.deps,'require_clean',lambda *args:None)
        self.patch(spike.tools,'selection',lambda *args:{})
        self.patch(spike.tools,'observed',lambda *args:{'state':'verified','image_present':True,'receipt':{'image':'sha256:'+'1'*64}})
        self.patch(app,'available',lambda *args:True)
        resources={};calls=[];registry=False
        @contextlib.contextmanager
        def locked(name,**kwargs):
            nonlocal registry
            if name=='registry':registry=True
            try:yield
            finally:
                if name=='registry':registry=False
        self.patch(app,'locked',locked)
        def command(argv,**kwargs):
            calls.append(argv)
            if argv[:3]==['podman','network','create']:
                resources[argv[-1]]='owned'
            if argv[:2]==['podman','run']:
                name=argv[argv.index('--name')+1]
                if name.endswith('-audit'):
                    audit={'advisories':{str(i):{'github_advisory_id':e['id'],'module_name':e['package'],'severity':e['severity'],'findings':[{'version':e['version']}]} for i,e in enumerate(policy['exceptions'])},'metadata':{'vulnerabilities':{k:2 if k=='high' else 0 for k in security.LEVELS}}}
                    return SimpleNamespace(returncode=1,stdout=json.dumps(audit))
                self.assertTrue(registry);resources[name]='owned'
                if failure=='start-timeout':raise app.AppError('timeout')
            if argv[:2]==['podman','stop']:resources.pop(argv[-1],None)
            if argv[:3]==['podman','network','rm']:resources.pop(argv[-1],None)
            return SimpleNamespace(returncode=0,stdout='')
        self.patch(app,'command',command)
        def runner(argv):
            command(argv)
            return SimpleNamespace(process=SimpleNamespace(poll=lambda:None),finish=lambda:None,category=lambda:'sdk-startup-or-protocol-failure',diagnostic=lambda:{'exit_code':1,'terms':['error']})
        self.patch(spike,'EphemeralOutput',runner)
        self.patch(spike,'ownership',lambda kind,name,token,**kw:resources.get(name,'absent'))
        def sample(*args):
            self.assertFalse(registry)
            if failure=='protocol':raise app.AppError('health')
            return {'physical_client_verified':False,'private_route_verified':False,'native':{'ios':{},'android':{}}}
        self.patch(spike.protocol,'sample',sample)
        if failure:
            with self.assertRaises(app.AppError):spike.run(self.root,self.origin,60)
            result=None
        else:result=spike.run(self.root,self.origin,60)
        self.assertEqual(resources,{})
        records=list((app.STORE/'metro-spikes').glob('*/spike.json'))
        self.assertEqual(len(records),1)
        return result,json.loads(records[0].read_text()),calls
    def test_simulated_success_releases_registry_then_cleans_owned_handles(self):
        result,record,calls=self.simulate_run()
        self.assertTrue(result['source_unchanged']);self.assertEqual(record['phase'],'complete')
        self.assertFalse(result['protocol']['physical_client_verified'])
        self.assertFalse(result['protocol']['private_route_verified'])
        sdk=next(c for c in calls if 'node_modules/expo/bin/cli' in c)
        self.assertIn('--offline',sdk);self.assertIn('--go',sdk)
        self.assertFalse(any(flag in sdk for flag in ['--lan','--host','--localhost','--tunnel','--https','--dev-client']))
    def test_unknown_start_outcome_cleans_proven_owned_handles(self):
        result,record,calls=self.simulate_run('start-timeout')
        self.assertEqual(record['phase'],'failed')
        self.assertTrue(any(c[:2]==['podman','stop'] for c in calls))
    def test_protocol_failure_is_failed_and_owned_resources_are_reconciled(self):
        result,record,calls=self.simulate_run('protocol')
        self.assertEqual(record['phase'],'failed');self.assertNotIn('protocol',record)
    def test_expiry_bounds_disconnected_container(self):
        policy={'expires_at':'2026-10-13T22:00:00Z'}
        expiry=security.timestamp(policy['expires_at'])
        with patch.object(spike.time,'time',return_value=expiry-30):
            self.assertEqual(spike.remaining_seconds(policy,300),30)
        with patch.object(spike.time,'time',return_value=expiry),self.assertRaises(app.AppError):spike.remaining_seconds(policy,300)
    def test_prepared_dependency_receipt_and_unknown_job_are_required(self):
        journal={'phase':'complete','policy_hash':'reviewed','after':{'lock':'same'}}
        state={'phase':'idle','operation_result':'passed','name':'job','token':'token'}
        with patch.object(spike.deps,'load_journal',return_value=journal),patch.object(spike.deps,'context',return_value={'policy_hash':'reviewed','hashes':{'lock':'same'}}),patch.object(mobile,'load_state',return_value=state),patch.object(spike,'ownership',return_value='absent'):
            spike.prepared_dependencies(self.root,'synthetic')
            for phase in ['checking','unknown']:
                state['phase']='checking' if phase=='checking' else 'idle'
                state['operation_result']='unknown' if phase=='unknown' else 'passed'
                with self.assertRaises(app.AppError):spike.prepared_dependencies(self.root,'synthetic')
            state.update(phase='idle',operation_result='passed');journal['after']={'lock':'changed'}
            with self.assertRaises(app.AppError):spike.prepared_dependencies(self.root,'synthetic')
    def test_directory_count_and_depth_bounds(self):
        with patch.object(spike,'MAX_FILES',1),self.assertRaises(app.AppError):spike.source_inventory(self.root)
        path=self.root/'src'
        for i in range(33):path=path/'nested';path.mkdir()
        with self.assertRaises(app.AppError):spike.source_inventory(self.root)
    def test_symlink_dependency_mount_blocked(self):
        (self.root/'node_modules').rmdir();(self.root/'node_modules').symlink_to(self.root/'src',target_is_directory=True)
        with self.assertRaises(app.AppError):spike.container_options(self.root,self.root,60)

if __name__=='__main__':unittest.main()
