#!/usr/bin/env python3
"""Offline policy/transaction tests with task-owned fixtures and mocked container jobs."""
import base64
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import private_apps as app
import project_dependencies as deps
import gptclawctl


class DependencyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)/'projects'; self.base.mkdir()
        self.units = Path(self.temp.name)/'units'; self.units.mkdir()
        for key, value in [('PROJECTS', self.base), ('STORE', self.base/'.gptclaw-runtime/v1'), ('UNITS', self.units)]:
            p = patch.object(app, key, value); p.start(); self.addCleanup(p.stop)
        for key, value in [('available', True), ('object_owned', False), ('toolchain', 'sha256:'+'2'*64)]:
            p = patch.object(app, key, return_value=value); p.start(); self.addCleanup(p.stop)
        self.root = Path(app.create('alpha')['root']); self.calls = []
        self.runner = patch.object(app, 'run_in_app', side_effect=self.fake_job); self.runner.start(); self.addCleanup(self.runner.stop)

    def fake_job(self, state, argv, **kwargs):
        root = Path(state['root']); self.calls.append((root, argv))
        self.assertIn('--ignore-scripts', argv); self.assertIn('--no-runtime', argv)
        self.assertIn('--pm-on-fail=error', argv); self.assertIn('--ignore-pnpmfile', argv)
        if '--lockfile-only' in argv:
            manifest = json.loads((root/'package.json').read_text()); importer = {}; packages = {}
            for group in deps.GROUPS:
                if group not in manifest: continue
                importer[group] = {}
                for name, version in manifest[group].items():
                    importer[group][name] = {'specifier': version, 'version': version}
                    packages[name+'@'+version] = {'resolution': {'integrity': 'sha512-'+base64.b64encode(bytes(64)).decode()}}
            lock = {'lockfileVersion': '9.0', 'importers': {'.': importer}, 'packages': packages, 'snapshots': {}}
            (root/'pnpm-lock.yaml').write_text(json.dumps(lock))
        else:
            (root/'node_modules').mkdir(exist_ok=True)
        return subprocess.CompletedProcess(argv, 0, '', '')

    def snapshot(self):
        return {name: (self.root/name).read_bytes() for name in deps.FILES}

    def edit_package(self, **changes):
        p = self.root/'package.json'; value = json.loads(p.read_text()); value.update(changes); p.write_text(json.dumps(value))

    def test_baseline_two_document_lock_and_policy_validate(self):
        self.assertEqual(len(deps.yaml_documents((self.root/'pnpm-lock.yaml').read_bytes(), 2)), 2)
        self.assertEqual(deps.context(self.root)['policy']['manager_version'], '12.10.1')

    def test_read_only_status_writes_or_executes_nothing(self):
        before = self.snapshot()
        with patch.object(app, 'command') as command:
            result = deps.status(self.root)
        self.assertEqual(result['policy'], 'valid'); command.assert_not_called()
        self.assertEqual(self.snapshot(), before); self.assertFalse(app.STORE.exists()); self.assertFalse(self.calls)

    def test_unknown_policy_and_wrong_schema_version_are_rejected(self):
        repo = Path(self.temp.name)/'repo'
        (repo/'config/project-dependencies').mkdir(parents=True); (repo/'schemas/project-dependencies').mkdir(parents=True)
        (repo/'schemas/project-dependencies/v1.schema.json').write_bytes((app.REPO/'schemas/project-dependencies/v1.schema.json').read_bytes())
        policy, _ = deps.policy()
        for change in ({'schema_version': 2}, {'schema_version': True}, {'unrecognized': 'x'}, {'install_hooks': True}):
            (repo/'config/project-dependencies/v1.json').write_text(json.dumps({**policy, **change}))
            with patch.object(app, 'REPO', repo), self.assertRaises(app.AppError): deps.context(self.root)
        self.assertFalse(self.calls)

    def test_duplicate_json_yaml_alias_tags_keys_and_document_limits(self):
        for blob in [b'{"name":1,"name":2}', b'{"x": NaN}']:
            with self.assertRaises(app.AppError): deps.json_data(blob)
        for blob in [b'a: &a {}\nb: *a\n', b'a: !!python/object/apply:os.system [x]\n', b'a: 1\na: 2\n', b'1: x\n', b'---\na: 1\n---\nb: 2\n']:
            with self.assertRaises(app.AppError): deps.yaml_documents(blob)
        with self.assertRaises(app.AppError): deps.yaml_documents(('a: '*40+'1').encode())

    def test_unsafe_files_and_executable_configuration_rejected_before_jobs(self):
        for name in ('.pnpmfile.cjs', '.pnpmfile.mjs', '.npmrc', '.env.local'):
            path = self.root/name; path.write_text('synthetic')
            with self.assertRaises(app.AppError): deps.operate(self.root, 'install')
            path.unlink()
        path = self.root/'.pnpmfile.cjs'; path.symlink_to(self.root/'missing')
        with self.assertRaises(app.AppError): deps.context(self.root)
        self.assertFalse(self.calls)

    def test_manifest_global_runtime_sources_and_ranges_rejected(self):
        original = (self.root/'package.json').read_bytes()
        for change in [{'workspaces': ['../beta']}, {'pnpm': {'overrides': {}}}, {'devEngines': {'runtime': {'name': 'node'}}},
                       {'packageManager': 'pnpm@latest'}, {'dependencies': {'evil': 'https://example.org/x.tgz'}},
                       {'dependencies': {'evil': 'file:../beta'}}, {'dependencies': {'evil': '^1.0.0'}}, {'peerDependencies': True}]:
            self.edit_package(**change)
            with self.assertRaises(app.AppError): deps.context(self.root)
            (self.root/'package.json').write_bytes(original)
        self.assertFalse(self.calls)

    def test_workspace_override_and_cache_escape_rejected(self):
        original = (self.root/'pnpm-workspace.yaml').read_bytes()
        for value in [{'packages': ['../beta']}, {'storeDir': '/outside'}, {'registries': {'default':'https://other/'}},
                      {'allowBuilds': {'evil': True}}, {'minimumReleaseAge': 0}, {'minimumReleaseAgeExclude':['*']}]:
            (self.root/'pnpm-workspace.yaml').write_text(json.dumps(value))
            with self.assertRaises(app.AppError): deps.context(self.root)
        (self.root/'pnpm-workspace.yaml').write_bytes(original)

    def test_lock_integrity_exotic_resolution_and_extra_importer_rejected(self):
        context = deps.context(self.root); docs = deps.yaml_documents(context['files']['pnpm-lock.yaml'], 2)
        p = context['policy']; key = next(iter(docs[1]['packages']))
        for mutate in [lambda d:d[1]['packages'][key].update(resolution={'integrity':'sha512-bad'}),
                       lambda d:d[1]['packages'][key]['resolution'].update(tarball='https://evil.invalid/package'),
                       lambda d:d[1]['importers'].update({'../beta':{}}),
                       lambda d:d[0]['importers']['.']['configDependencies'].update({'evil':'1.0.0'}),
                       lambda d:d[1]['snapshots'].update({'evil@git:foo':{}})]:
            candidate = copy.deepcopy(docs); mutate(candidate)
            with self.assertRaises(app.AppError): deps.validate_lock(candidate, context['manifest'], p)

    def test_typed_requests_reject_flag_injection_and_implicit_upgrade(self):
        for name, version in [('--global','1.0.0'), ('a;touch-sentinel','1.0.0'), ('ok','latest'), ('ok','^1.0.0')]:
            with self.assertRaises(app.AppError): deps.operate(self.root, 'add', name, version)
        self.assertFalse(self.calls)

    def test_frozen_install_preserves_source_and_has_operation_receipt(self):
        before = self.snapshot(); result = deps.operate(self.root, 'install')
        self.assertEqual(result['state'], 'complete'); self.assertFalse(result['changed'])
        self.assertEqual(result['before'], result['after']); self.assertEqual(self.snapshot(), before)
        s = app.state_for('alpha'); self.assertEqual(s['operation_id'], result['operation_id']); self.assertEqual(s['operation'], 'deps')
        self.assertEqual(s['phase'], 'stopped'); self.assertEqual(s['operation_result'], 'passed')

    def test_add_update_remove_with_reviewable_hashes_and_unrelated_work(self):
        sentinel = self.root/'user-work.txt'; sentinel.write_text('keep')
        result = deps.operate(self.root, 'add', 'is-number', '6.0.0', 'development')
        self.assertEqual(set(result['changed_files']), {'package.json','pnpm-lock.yaml'})
        self.assertEqual(json.loads((self.root/'package.json').read_text())['devDependencies']['is-number'], '6.0.0')
        deps.operate(self.root, 'update', 'is-number', '7.0.0')
        self.assertEqual(json.loads((self.root/'package.json').read_text())['devDependencies']['is-number'], '7.0.0')
        deps.operate(self.root, 'remove', 'is-number')
        self.assertNotIn('is-number', json.loads((self.root/'package.json').read_text())['devDependencies'])
        self.assertEqual(sentinel.read_text(), 'keep'); self.assertEqual(list((deps.location('alpha')/'jobs').iterdir()), [])
        self.assertFalse(deps.operate(self.root, 'remove', 'is-number')['changed'])

    def test_empty_dependencies_still_have_valid_lock(self):
        self.edit_package(dependencies={}, devDependencies={})
        self.fake_job({'root':str(self.root)}, ['--lockfile-only',*deps.INSTALL_FLAGS])
        deps.context(self.root)
        self.assertFalse(deps.operate(self.root,'install')['changed'])

    def test_running_or_busy_target_refused_without_package_job(self):
        before = self.snapshot()
        with patch.object(app,'object_owned',return_value=True), self.assertRaises(app.AppError): deps.operate(self.root,'install')
        with app.locked('alpha'), self.assertRaises(app.AppError): deps.operate(self.root,'install')
        self.assertEqual(self.snapshot(),before); self.assertFalse(self.calls)

    def test_failed_fetch_keeps_originals_blocks_retry_and_supports_abort(self):
        before = self.snapshot()
        with patch.object(app,'run_in_app',side_effect=app.AppError('command')):
            with self.assertRaises(app.AppError): deps.operate(self.root,'add','is-number','6.0.0')
        journal = deps.load_journal('alpha',self.root); self.assertEqual(journal['phase'],'failed')
        self.assertEqual(self.snapshot(),before)
        with self.assertRaises(app.AppError): deps.operate(self.root,'install')
        result=deps.operate(self.root,'recover',operation_id=journal['operation_id'],abort=True)
        self.assertEqual(result['state'],'aborted'); self.assertEqual(self.snapshot(),before)
        deps.operate(self.root,'install')

    def test_timeout_and_owned_job_are_not_cancelled_or_replaced(self):
        with patch.object(app,'run_in_app',side_effect=app.AppError('timeout')):
            with self.assertRaises(app.AppError): deps.operate(self.root,'install')
        journal=deps.load_journal('alpha',self.root); self.assertEqual(journal['phase'],'unknown')
        with patch.object(app,'object_owned',return_value=True), self.assertRaises(app.AppError):
            deps.operate(self.root,'recover',operation_id=journal['operation_id'])
        self.assertEqual(deps.load_journal('alpha',self.root)['operation_id'],journal['operation_id'])
        result=deps.operate(self.root,'recover',operation_id=journal['operation_id'])
        self.assertEqual(result['operation_id'],journal['operation_id']); self.assertEqual(result['state'],'complete')

    def test_interrupted_publication_recovers_same_id_without_replacing_other_files(self):
        publish=deps.publish_file
        def fail_second(root,name,journal):
            if name=='pnpm-lock.yaml': raise OSError('synthetic publication interruption')
            return publish(root,name,journal)
        with patch.object(deps,'publish_file',side_effect=fail_second), self.assertRaises(app.AppError):
            deps.operate(self.root,'add','is-number','6.0.0')
        journal=deps.load_journal('alpha',self.root); self.assertEqual(journal['phase'],'failed')
        self.assertTrue((deps.workspace(journal).parent/'original/package.json').exists())
        result=deps.operate(self.root,'recover',operation_id=journal['operation_id'])
        self.assertEqual(result['operation_id'],journal['operation_id']); self.assertEqual(result['state'],'complete')
        deps.context(self.root)

    def test_concurrent_editor_change_is_preserved_and_abort_does_not_revert_it(self):
        def edit(state,argv,**kwargs):
            result=self.fake_job(state,argv)
            if '--lockfile-only' in argv:self.edit_package(description='concurrent user edit')
            return result
        with patch.object(app,'run_in_app',side_effect=edit), self.assertRaises(app.AppError):
            deps.operate(self.root,'add','is-number','6.0.0')
        self.assertEqual(json.loads((self.root/'package.json').read_text())['description'],'concurrent user edit')
        journal=deps.load_journal('alpha',self.root)
        deps.operate(self.root,'recover',operation_id=journal['operation_id'],abort=True)
        self.assertEqual(json.loads((self.root/'package.json').read_text())['description'],'concurrent user edit')

    def test_frozen_job_that_writes_lock_is_not_accepted(self):
        def edit(state,argv,**kwargs):
            result=self.fake_job(state,argv);(Path(state['root'])/'pnpm-lock.yaml').write_text('{}');return result
        with patch.object(app,'run_in_app',side_effect=edit), self.assertRaises(app.AppError): deps.operate(self.root,'install')
        self.assertNotEqual(deps.load_journal('alpha',self.root)['phase'],'complete')

    def test_policy_change_invalidates_preparation_and_blocks_partial_start(self):
        _, contract=app.target(self.root); s=app.reserve(self.root,contract);s['image']='sha256:'+'2'*64
        digest=app.dependency_digest(s)
        with patch.object(deps,'policy',return_value=(deps.policy()[0],'f'*64)):
            self.assertNotEqual(app.dependency_digest(s),digest)
        with patch.object(app,'run_in_app',side_effect=app.AppError('command')):
            with self.assertRaises(app.AppError):deps.operate(self.root,'install')
        with patch.object(app,'toolchain') as build, self.assertRaises(app.AppError): app.start(self.root)
        build.assert_not_called()

    def test_status_surfaces_partial_lock_without_writing_it(self):
        with patch.object(app,'run_in_app',side_effect=app.AppError('command')):
            with self.assertRaises(app.AppError):deps.operate(self.root,'install')
        (self.root/'pnpm-lock.yaml').write_text('{}'); before=self.snapshot()
        result=deps.status(self.root)
        self.assertEqual(result['state'],'recovery-required'); self.assertEqual(result['policy'],'invalid')
        self.assertEqual(self.snapshot(),before)

    def test_journal_identity_and_cleanup_marker_are_validated(self):
        with patch.object(app,'run_in_app',side_effect=app.AppError('command')):
            with self.assertRaises(app.AppError):deps.operate(self.root,'add','is-number','6.0.0')
        journal=deps.load_journal('alpha',self.root)
        marker=deps.workspace(journal).parent/'owner.json'; marker.write_text(json.dumps({'operation_id':'0'*32,'project':'alpha'}))
        with self.assertRaises(app.AppError):deps.cleanup(journal)
        changed={**journal,'root':'/other'};app.save(deps.location('alpha')/'journal.json',changed)
        with self.assertRaises(app.AppError):deps.load_journal('alpha',self.root)

    def test_crash_after_capture_before_publish_keeps_original_inode_and_recovers(self):
        link=os.link
        def crash(source,target,**kwargs):
            if target==self.root/'package.json':raise OSError('synthetic crash after capture')
            return link(source,target,**kwargs)
        with patch.object(deps.os,'link',side_effect=crash),self.assertRaises(app.AppError):
            deps.operate(self.root,'add','is-number','6.0.0')
        journal=deps.load_journal('alpha',self.root)
        self.assertFalse((self.root/'package.json').exists())
        self.assertTrue((deps.captured_files(journal)/'package.json').exists())
        self.assertEqual(deps.status(self.root)['state'],'recovery-required')
        result=deps.operate(self.root,'recover',operation_id=journal['operation_id'])
        self.assertEqual(result['state'],'complete');deps.context(self.root)

    def test_editor_replacement_during_publication_is_never_overwritten(self):
        rename=os.rename
        def replace(source,target):
            result=rename(source,target)
            if source==self.root/'package.json':
                value=json.loads(Path(target).read_text());value['description']='editor replacement'
                (self.root/'package.json').write_text(json.dumps(value))
            return result
        with patch.object(deps.os,'rename',side_effect=replace),self.assertRaises(app.AppError):
            deps.operate(self.root,'add','is-number','6.0.0')
        self.assertEqual(json.loads((self.root/'package.json').read_text())['description'],'editor replacement')
        journal=deps.load_journal('alpha',self.root)
        deps.operate(self.root,'recover',operation_id=journal['operation_id'],abort=True)
        self.assertEqual(json.loads((self.root/'package.json').read_text())['description'],'editor replacement')

    def test_receipt_history_survives_later_operations(self):
        first=deps.operate(self.root,'install');deps.operate(self.root,'add','is-number','6.0.0')
        historical=deps.status(self.root,first['operation_id'])['operation']
        self.assertEqual(historical['operation_id'],first['operation_id']);self.assertEqual(historical['phase'],'complete')
        with self.assertRaises(app.AppError):deps.operate(self.root,'recover',operation_id=first['operation_id'])

    def test_frozen_container_metadata_mounts_are_read_only_and_scoped(self):
        _,c=app.target(self.root);state=app.reserve(self.root,c);state['image']='sha256:'+'2'*64
        self.runner.stop()
        with patch.object(app,'command',side_effect=[subprocess.CompletedProcess([],1,'',''),subprocess.CompletedProcess([],0,'','')]) as command:
            app.run_in_app(state,['pnpm','install','--frozen-lockfile',*deps.INSTALL_FLAGS],read_only_dependency_files=True)
        args=command.call_args.args[0]
        volumes=[args[i+1] for i,v in enumerate(args) if v=='--volume']
        self.assertEqual(set(volumes),{str(self.root)+':/workspace:rw',*(str(self.root/n)+':/workspace/'+n+':ro' for n in deps.FILES)})
        self.assertIn('pnpm_config_pm_on_fail=error',args)
        self.assertFalse(any('/.ssh' in v or '/.aws' in v or 'sock' in v for v in volumes))

    def test_second_project_source_and_state_are_unchanged(self):
        other=Path(app.create('beta')['root']);_,c=app.target(other); state=app.reserve(other,c)
        before=(app.STORE/'beta.json').read_bytes(); source=(other/'pnpm-lock.yaml').read_bytes()
        deps.operate(self.root,'add','is-number','6.0.0')
        self.assertEqual((app.STORE/'beta.json').read_bytes(),before);self.assertEqual((other/'pnpm-lock.yaml').read_bytes(),source)

    def test_cli_package_version_does_not_trigger_provider_version(self):
        with patch.object(gptclawctl,'os',SimpleNamespace(getuid=lambda:1002,geteuid=lambda:1002)),patch('sys.stdout',new_callable=io.StringIO) as out:
            self.assertEqual(gptclawctl.main(['deps','add','--project-root',str(self.root),'--package','is-number','--version','6.0.0']),0)
        self.assertEqual(json.loads(out.getvalue())['action'],'add')


if __name__=='__main__':unittest.main(verbosity=2)
