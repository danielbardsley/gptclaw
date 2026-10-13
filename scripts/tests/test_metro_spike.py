#!/usr/bin/env python3
"""Offline SDK spike admission, filtered source and ownership failure cases."""
import contextlib
import hashlib
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
    def prepare_plan(self):
        self.patch(spike,'TARGETS',{self.root})
        self.patch(app,'target',lambda root:(self.root,{'schema_version':5,'project':{'id':'synthetic'}}))
    def test_exact_owned_origin_only(self):
        self.assertEqual(spike.origin(self.origin+'/'),self.origin)
        for value in ['http://'+spike.HOST+':8443','https://foreign.ts.net:8443',self.origin+'/projects/',self.origin+'?target=http://localhost',self.origin+'#fragment','https://user@'+spike.HOST+':8443','https://'+spike.HOST+':443','https://'+spike.HOST+':bad']:
            with self.subTest(value=value),self.assertRaises(app.AppError):spike.origin(value)
    def test_readonly_plan_and_explicit_fixture_bound(self):
        self.prepare_plan()
        before=sorted(str(p) for p in self.root.rglob('*'))
        with patch.object(app,'command',side_effect=AssertionError('no command')),patch.object(app,'save',side_effect=AssertionError('no writes')):
            result=spike.plan(self.root,self.origin,60)
        self.assertEqual(result['runtime_security'],'approval-pending');self.assertEqual(result['source_retained'],True)
        self.assertEqual(before,sorted(str(p) for p in self.root.rglob('*')))
        for seconds in [0,301,True]:
            with self.assertRaises(app.AppError):spike.plan(self.root,self.origin,seconds)
        with patch.object(spike,'TARGETS',set()),self.assertRaises(app.AppError):spike.plan(self.root,self.origin,60)
    def test_unapproved_run_denies_before_store_and_runtime_writes(self):
        self.prepare_plan()
        with patch.object(os,'getuid',return_value=1002),patch.object(os,'geteuid',return_value=1002),patch.object(spike,'source_inventory',return_value={}),patch.object(app,'locked',side_effect=AssertionError('no lock write')),patch.object(app,'command',side_effect=AssertionError('no process')):
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
