#!/usr/bin/env python3
"""Offline explicit migration, concurrent-edit retention and legacy source gates."""
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import private_apps as app
import project_mobile as mobile
import metro_contract as metro
import project_dependencies as deps
import project_templates as templates
import gptclawctl as cli
from dashboard_inventory import Scanner
from project_manifest import load_schema,validate_project


class ContractTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        self.projects=Path(temp.name)/'projects';self.projects.mkdir()
        self.patch(app,'PROJECTS',self.projects);self.patch(app,'STORE',self.projects/'.runtime')
        self.root=Path(app.create('metro-one',template='expo-react-native',template_version='1.0.1')['root'])
        self.manifest=self.root/'.gptclaw/project.yaml'
        self.before=self.manifest.read_bytes()
        self.store_before=sorted(str(p) for p in app.STORE.rglob('*'))
        # Canonical PRJ-006 broker/Git mechanics have their own real-process suite.
        # This fixture isolates migration; the no-write guard case below is real.
        self.patch(metro.worktrees,'canonical',lambda root:{'root':str(root),'project':'metro-one','key':'0'*64})
        def git(root,*argv,**kwargs):
            if 'status' in argv:return b'',0
            if 'ls-files' in argv:return b'.gptclaw/project.yaml\n',0
            raise AssertionError(argv)
        self.patch(metro.worktrees,'git',git)
    def patch(self,obj,name,value):
        p=patch.object(obj,name,value);p.start();self.addCleanup(p.stop)
    def hashes(self):
        return {p.relative_to(self.root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in self.root.rglob('*') if p.is_file()}
    def upgrade(self):
        planned=metro.enable(self.root)
        return metro.enable(self.root,apply=True,confirm_plan=planned['plan_digest'])
    def test_readonly_plan_keeps_source_and_runtime_store_unchanged(self):
        before=self.hashes()
        with patch.object(app,'command',side_effect=AssertionError('no container or unit command')):
            value=metro.enable(self.root)
        self.assertEqual(value['state'],'opt-in-planned');self.assertFalse(value['starts_session'])
        self.assertEqual(self.hashes(),before);self.assertEqual(sorted(str(p) for p in app.STORE.rglob('*')),self.store_before)
        self.assertEqual(value['manifest']['schema_version'],6);self.assertNotIn('origin',value['manifest']['metro'])
    def test_confirmed_upgrade_only_changes_manifest_and_retains_previous(self):
        before=self.hashes();value=self.upgrade();after=self.hashes()
        self.assertEqual([k for k in before if before[k]!=after[k]],['.gptclaw/project.yaml'])
        self.assertEqual(set(before),set(after));self.assertEqual(Path(value['previous_metadata']).read_bytes(),self.before)
        self.assertEqual(validate_project(self.root)[2],0);self.assertEqual(app.target(self.root)[1]['schema_version'],6)
        self.assertFalse(value['private_route_changed']);self.assertTrue(value['metadata_commit_required'])
        self.assertFalse(list(app.STORE.glob('*.json')))
    def test_missing_wrong_or_stale_plan_cannot_write(self):
        for digest in [None,'0'*64]:
            with self.assertRaises(app.AppError):metro.enable(self.root,apply=True,confirm_plan=digest)
        planned=metro.enable(self.root)
        value=json.loads((self.root/'app.json').read_text());value['expo']['version']='1.0.1';(self.root/'app.json').write_text(json.dumps(value))
        with self.assertRaises(app.AppError):metro.enable(self.root,apply=True,confirm_plan=planned['plan_digest'])
        self.assertEqual(self.manifest.read_bytes(),self.before);self.assertEqual(sorted(str(p) for p in app.STORE.rglob('*')),self.store_before)
    def test_dirty_or_untracked_metadata_blocks_before_writes(self):
        for mode in ['dirty','untracked']:
            def git(root,*argv,**kwargs):
                if 'status' in argv:return (b' M .gptclaw/project.yaml\0' if mode=='dirty' else b''),0
                return b'',1
            with patch.object(metro.worktrees,'git',git),self.assertRaises(app.AppError):metro.enable(self.root)
            self.assertEqual(self.manifest.read_bytes(),self.before);self.assertEqual(sorted(str(p) for p in app.STORE.rglob('*')),self.store_before)
    def test_metadata_change_after_plan_is_preserved(self):
        value=metro.enable(self.root);real_locked=app.locked
        from contextlib import contextmanager
        @contextmanager
        def locked(name):
            document=app.target(self.root)[1];document['commands']['test']=['pnpm','lint']
            self.manifest.write_text(json.dumps(document))
            with real_locked(name):yield
        with patch.object(app,'locked',locked),self.assertRaises(app.AppError):metro.enable(self.root,apply=True,confirm_plan=value['plan_digest'])
        self.assertEqual(json.loads(self.manifest.read_text())['commands']['test'],['pnpm','lint'])
        self.assertFalse((app.STORE/'metro-metadata').exists())
    def test_editor_racing_atomic_publication_keeps_both_copies(self):
        planned=metro.enable(self.root);exchange=metro.exchange
        def raced(fd,temporary):
            document=json.loads(self.before);document['commands']['test']=['pnpm','owner-edit']
            self.manifest.write_text(json.dumps(document));exchange(fd,temporary)
        with patch.object(metro,'exchange',raced):value=metro.enable(self.root,apply=True,confirm_plan=planned['plan_digest'])
        self.assertEqual(value['state'],'metadata-recovery-required')
        previous=json.loads(Path(value['previous_metadata']).read_text())
        self.assertEqual(previous['commands']['test'],['pnpm','owner-edit'])
        self.assertEqual(json.loads(self.manifest.read_text())['schema_version'],6)
    def test_recovery_receipt_blocks_retry_without_discarding_either_copy(self):
        planned=metro.enable(self.root);exchange=metro.exchange
        def raced(fd,temporary):
            self.manifest.write_text(self.before.decode()+'\n');exchange(fd,temporary)
        with patch.object(metro,'exchange',raced):value=metro.enable(self.root,apply=True,confirm_plan=planned['plan_digest'])
        prior=Path(value['previous_metadata']).read_bytes();current=self.manifest.read_bytes()
        with self.assertRaises(app.AppError) as error:metro.enable(self.root)
        self.assertEqual(error.exception.code,'metro-metadata-recovery')
        self.assertEqual(prior,Path(value['previous_metadata']).read_bytes());self.assertEqual(current,self.manifest.read_bytes())
    def test_archive_publication_failure_preserves_displaced_metadata(self):
        planned=metro.enable(self.root)
        with patch.object(templates,'publish',side_effect=app.AppError('conflict')),self.assertRaises(app.AppError):metro.enable(self.root,apply=True,confirm_plan=planned['plan_digest'])
        displaced=list(self.manifest.parent.glob('project.yaml.*.tmp'))
        self.assertEqual(len(displaced),1);self.assertEqual(displaced[0].read_bytes(),self.before)
        record=json.loads(next((app.STORE/'metro-metadata').glob('*/*/operation.json')).read_text())
        self.assertEqual(record['phase'],'recovery-required')
    def test_wrong_toolchain_is_rejected_without_metadata_writes(self):
        with patch.object(metro.tools,'selection',return_value={'declaration':{'schema_version':1,'profile':'other','profile_version':1,'versions':{}},'selection_hash':'0'*64}),self.assertRaises(app.AppError) as error:metro.enable(self.root)
        self.assertEqual(error.exception.code,'toolchain-policy');self.assertEqual(self.manifest.read_bytes(),self.before)
        self.assertEqual(sorted(str(p) for p in app.STORE.rglob('*')),self.store_before)
    def test_strict_ttl_and_unknown_runtime_inputs_block(self):
        source=app.target(self.root)[1];source['schema_version']=6
        for ttl in [True,59,28801,7200.0]:
            with self.assertRaises(app.AppError):metro.enable(self.root,ttl)
            source['metro']={'adapter':'metro-v1','mode':'expo-go','ttl_seconds':ttl}
            self.assertTrue(list(load_schema(6)[1].iter_errors(source)))
        source['metro']={'adapter':'metro-v1','mode':'expo-go','ttl_seconds':7200,'environment':{'secret':'synthetic'}}
        self.assertTrue(list(load_schema(6)[1].iter_errors(source)))
        source['metro'].pop('environment');source['metro']['mode']='development-build'
        self.assertTrue(list(load_schema(6)[1].iter_errors(source)))
        self.assertEqual(sorted(str(p) for p in app.STORE.rglob('*')),self.store_before)
    def test_unsupported_sdk_dynamic_config_and_symlink_preserve_metadata(self):
        package=self.root/'package.json';before=package.read_bytes();value=json.loads(before);value['dependencies']['expo']='58.0.0';package.write_text(json.dumps(value))
        with self.assertRaises(app.AppError):metro.enable(self.root)
        package.write_bytes(before);(self.root/'app.config.js').write_text('throw new Error("must not execute")')
        with self.assertRaises(app.AppError):metro.enable(self.root)
        (self.root/'app.config.js').unlink();self.manifest.unlink();self.manifest.symlink_to('/dev/null')
        with self.assertRaises(app.AppError):metro.enable(self.root)
        self.assertEqual(sorted(str(p) for p in app.STORE.rglob('*')),self.store_before)
    def test_worktree_source_only_lexical_guard_precedes_access(self):
        path=self.projects/'.gptclaw-worktrees/metro-one/task'
        with patch.object(app,'command',side_effect=AssertionError('no execution')),self.assertRaises(app.AppError) as error:metro.enable(path)
        self.assertEqual(error.exception.code,'worktree-source-only');self.assertEqual(sorted(str(p) for p in app.STORE.rglob('*')),self.store_before)
    def test_schema5_remains_valid_and_does_not_gain_metro_implicitly(self):
        self.assertEqual(validate_project(self.root)[2],0);self.assertEqual(app.target(self.root)[1]['schema_version'],5)
        value=app.target(self.root)[1];value['metro']={'adapter':'metro-v1','mode':'expo-go','ttl_seconds':7200}
        self.manifest.write_text(json.dumps(value));self.assertNotEqual(validate_project(self.root)[2],0)
    def test_schema6_stays_non_http_and_lifecycle_remains_unavailable(self):
        self.upgrade()
        from types import SimpleNamespace
        with patch.object(app,'command',side_effect=AssertionError('no runtime execution')):
            for action in ['start','stop','restart','status','observe','logs','hooks','db']:
                with self.assertRaises(app.AppError) as error:mobile.dispatch(SimpleNamespace(action=action,project_root=str(self.root)))
                self.assertEqual(error.exception.code,'mobile-unsupported')
        with patch.object(app,'object_owned',return_value=False),patch.object(app,'reserve',side_effect=AssertionError('no HTTP lease')):
            state=deps.stopped_state(self.root,app.target(self.root)[1])
        self.assertNotIn('port',state);self.assertEqual(state['adapter'],'mobile')
        caps={'provider':'gptclawctl','project_manifest_schemas':[1,2,3,4,5,6],'runtime_manifest_schemas':[1,2,3,4]}
        snapshot=Scanner(self.projects,capabilities=caps).scan()
        row=next(r for r in snapshot['rows'] if r['id']=='metro-one')
        self.assertEqual(row['components'],[]);self.assertEqual(row['runtime_support'],'unsupported')
    def test_schema6_source_dependency_and_provenance_contracts_match_schema5(self):
        context=deps.context(self.root);release=(self.root/'.gptclaw/template-release.json').read_bytes()
        self.upgrade();self.assertEqual(deps.context(self.root),context)
        templates.validate_provenance(self.root);self.assertEqual((self.root/'.gptclaw/template-release.json').read_bytes(),release)
    def test_historical_schema5_rejects_optin_without_touching_source(self):
        self.upgrade();before=self.hashes()
        document=app.target(self.root)[1]
        self.assertTrue(list(load_schema(5)[1].iter_errors(document)))
        self.assertEqual(self.hashes(),before)
    def test_provider_bundle_preserves_all_historical_schema_bytes(self):
        before={(app.REPO/'schemas/project'/('v'+str(i)+'.schema.json')).name:hashlib.sha256((app.REPO/'schemas/project'/('v'+str(i)+'.schema.json')).read_bytes()).hexdigest() for i in range(1,6)}
        snapshot=app.provider_bundle()
        self.assertTrue((snapshot/'scripts/metro_contract.py').is_file());self.assertTrue((snapshot/'schemas/project/v6.schema.json').is_file())
        for name,digest in before.items():self.assertEqual(hashlib.sha256((snapshot/'schemas/project'/name).read_bytes()).hexdigest(),digest)
    def test_cli_reports_source_contract_but_no_metro_session_capability(self):
        from contextlib import redirect_stdout
        output=io.StringIO()
        with redirect_stdout(output):self.assertEqual(cli.main(['--version']),0)
        caps=json.loads(output.getvalue());self.assertIn(6,caps['project_manifest_schemas']);self.assertNotIn(6,caps['runtime_manifest_schemas'])
        self.assertEqual(caps['metro_actions'],['enable']);self.assertEqual(caps['metro_session_schemas'],[])

if __name__=='__main__':unittest.main()
