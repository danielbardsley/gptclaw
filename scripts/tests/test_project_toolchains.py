#!/usr/bin/env python3
"""Offline resolver/acquisition/integration tests; no live engine or network."""
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
import project_toolchains as tools
import gptclawctl

IMAGE = 'sha256:'+'3'*64


class ToolchainTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)/'projects'; base.mkdir()
        units = Path(self.temp.name)/'units'; units.mkdir()
        for key, value in [('PROJECTS', base), ('STORE', base/'.gptclaw-runtime/v1'), ('UNITS', units)]:
            p = patch.object(app, key, value); p.start(); self.addCleanup(p.stop)
        p = patch.object(app, 'available', return_value=True); p.start(); self.addCleanup(p.stop)
        self.root = Path(app.create('alpha')['root']); self.calls = []; self.image = None
        self.selected = tools.selection(self.root)
        self.runner = patch.object(app, 'command', side_effect=self.command); self.runner.start(); self.addCleanup(self.runner.stop)
        self.inspector = patch.object(app, 'json_command', side_effect=self.image_inspect); self.inspector.start(); self.addCleanup(self.inspector.stop)

    def command(self, args, **kwargs):
        self.calls.append((args, kwargs))
        if args[:3] == ['podman', 'image', 'exists']:
            return subprocess.CompletedProcess(args, 0 if self.image else 1, '', '')
        if args[:3] == ['podman', 'container', 'exists']:
            return subprocess.CompletedProcess(args, 1, '', '')
        if args[:2] == ['podman', 'build']:
            self.image = IMAGE
            return subprocess.CompletedProcess(args, 0, '', '')
        if args[:2] == ['podman', 'run']:
            p = self.selected['profile']
            actual = {'versions': p['versions'], 'installed_versions': p['versions'], 'artifact_integrity': p['pnpm_artifact']['integrity']}
            return subprocess.CompletedProcess(args, 0, json.dumps(actual), '')
        return subprocess.CompletedProcess(args, 0, '', '')

    def image_inspect(self, args):
        return [{'Id': self.image, 'Labels': {tools.LABEL: self.selected['profile_hash']}, 'Os': 'linux', 'Architecture': 'amd64'}]

    def sidecar(self, value):
        (self.root/'.gptclaw/toolchain.json').write_text(json.dumps(value))

    def package(self, **values):
        path = self.root/'package.json'; item = json.loads(path.read_text()); item.update(values); path.write_text(json.dumps(item))

    def reject(self):
        with self.assertRaises(app.AppError): tools.inspect(self.root)
        self.assertFalse(self.calls)

    def test_new_exact_selection_and_manifest_v1_unchanged(self):
        self.assertFalse(self.selected['legacy']); self.assertEqual(app.validate_project(self.root)[2], 0)
        manifest = json.loads((self.root/'.gptclaw/project.yaml').read_text()); manifest['toolchain'] = {}
        app.save(self.root/'.gptclaw/project.yaml', manifest)
        self.assertNotEqual(app.validate_project(self.root)[2], 0)

    def test_legacy_selection_is_fixed_and_observation_only(self):
        (self.root/'.gptclaw/toolchain.json').unlink()
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        observed = tools.inspect(self.root)
        self.assertTrue(observed['legacy']); self.assertEqual(observed['state'], 'unprepared')
        self.assertEqual(before, {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
        self.assertFalse(self.calls); self.assertFalse(app.STORE.exists())

    def test_invalid_unknown_range_and_bool_sidecars_refused_offline(self):
        base = self.selected['declaration']
        for value in [{**base, 'unknown': True}, {**base, 'schema_version': True}, {**base, 'profile_version': True},
                      {**base, 'profile_version': 99}, {**base, 'profile': '../foreign'},
                      {**base, 'versions': {**base['versions'], 'node': 'latest'}},
                      {**base, 'versions': {**base['versions'], 'node': '^24.21.0'}},
                      {**base, 'versions': {**base['versions'], 'node': '24.20.0'}}]:
            with self.subTest(value=value): self.sidecar(value); self.reject()

    def test_duplicate_symlink_hardlink_and_oversized_sidecar_refused(self):
        path = self.root/'.gptclaw/toolchain.json'; original = path.read_bytes()
        for blob in [b'{"schema_version":1,"schema_version":1}', b'x'*65537, b'{"schema_version":NaN}']:
            path.write_bytes(blob); self.reject()
        path.write_bytes(original); other = self.root/'hardlink'; os.link(path, other); self.reject(); other.unlink()
        path.unlink(); path.symlink_to(self.root/'package.json'); self.reject()

    def test_metadata_mismatch_runtime_hooks_and_unknown_managers_fail_offline(self):
        original = (self.root/'package.json').read_bytes()
        for values in [{'packageManager': 'pnpm@12.10.0'}, {'devEngines': {}}, {'engines': {'node': '>=25'}},
                       {'engines': {'node': True}}, {'engines': {'bun': '*'}}, {'engines': {'node': '* || >'}}]:
            (self.root/'package.json').write_bytes(original); self.package(**values); self.reject()

    def test_version_files_and_supported_constraints(self):
        self.package(engines={'node': '>=24 <25', 'pnpm': '^12.10.1'})
        (self.root/'.node-version').write_text('24.21.0\n'); tools.selection(self.root)
        (self.root/'.node-version').write_text('24\n'); self.reject()
        (self.root/'.node-version').unlink(); (self.root/'.mise.toml').write_text('synthetic=true'); self.reject()

    def test_range_grammar_matches_stable_semver_cases(self):
        for range_ in ['*', '24', '24.*', '24.21', '>=24 <25', '^24.0.0', '~24.21.0', '24.0.0 - 24.21.0', '<=24', '>23', '22 || 24']:
            self.assertTrue(tools.satisfies('24.21.0', range_), range_)
        for range_ in ['25', '<24', '>24', '>=25', '~24.20.0', '^0.0.1', '22 || 23']:
            self.assertFalse(tools.satisfies('24.21.0', range_), range_)
        for range_ in ['', '* || >', '24.0.0-beta', '024', '24.*.1']:
            with self.assertRaises(app.AppError): tools.satisfies('24.21.0', range_)

    def test_registry_rejects_unreviewed_source_duplicates_or_helper_drift(self):
        original = tools.data(app.REPO/'config/toolchains/v1.json')
        for mutate in [lambda p: p.update(base_image='node:latest'), lambda p: p['pnpm_artifact'].update(url='https://foreign.test/pnpm'),
                       lambda p: p.update(installer_sha256='0'*64), lambda p: p.update(platform={'os':'linux','architecture':'arm64'})]:
            r = copy.deepcopy(original); mutate(r['profiles'][0])
            real = tools.data
            with patch.object(tools, 'data', side_effect=lambda path: r if path.name == 'v1.json' else real(path)):
                with self.assertRaises(app.AppError): tools.registry()
        r = copy.deepcopy(original); r['profiles'].append(copy.deepcopy(r['profiles'][0]))
        real = tools.data
        with patch.object(tools, 'data', side_effect=lambda path: r if path.name == 'v1.json' else real(path)):
            with self.assertRaises(app.AppError): tools.registry()
        self.assertFalse(self.calls)

    def test_distinct_reviewed_fixture_profiles_have_distinct_selection_and_fingerprints(self):
        r, profiles = tools.registry(); r = copy.deepcopy(r); second = copy.deepcopy(r['profiles'][0])
        second.update(profile_version=2, versions={'node':'26.0.0','pnpm':'12.10.1'}); r['profiles'].append(second)
        profiles = {(p['profile'], p['profile_version']): p for p in r['profiles']}
        with patch.object(tools, 'registry', return_value=(r, profiles)):
            self.sidecar({'schema_version':1,'profile':'node-pnpm','profile_version':2,'versions':second['versions']})
            chosen = tools.selection(self.root)
            self.assertNotEqual(chosen['profile_hash'], self.selected['profile_hash'])
            self.assertNotEqual(chosen['selection_hash'], self.selected['selection_hash'])
            self.assertNotEqual(tools.tag_for(chosen), tools.tag_for(self.selected))
            with self.assertRaises(app.AppError): tools.assert_active(chosen, {'toolchain_hash':self.selected['selection_hash']})
        # Synthetic profile is test-only; it is never added to the production registry.

    def test_uncached_acquisition_and_reuse_verify_actual_versions(self):
        result = tools.acquire(self.selected); self.assertTrue(result['changed']); self.assertEqual(result['receipt']['image'], IMAGE)
        receipt = tools.record(self.selected); self.assertEqual(receipt['phase'], 'verified')
        second = tools.acquire(self.selected); self.assertFalse(second['changed'])
        self.assertEqual(sum(args[:2] == ['podman','build'] for args, _ in self.calls), 1)
        self.assertEqual(sum(args[:2] == ['podman','run'] for args, _ in self.calls), 2)
        self.assertEqual(list((tools.location(self.selected)/'jobs').iterdir()), [])
        self.assertTrue((tools.location(self.selected)/'receipts'/(receipt['operation_id']+'.json')).exists())

    def test_inspect_verified_cache_runs_only_metadata_commands(self):
        tools.acquire(self.selected); self.calls.clear()
        self.assertEqual(tools.inspect(self.root)['state'], 'verified')
        self.assertTrue(all(args[:3] == ['podman','image','exists'] for args, _ in self.calls))

    def test_build_context_and_verifier_have_no_project_auth_or_sibling_mount(self):
        tools.acquire(self.selected)
        build = next((args, kw) for args, kw in self.calls if args[:2] == ['podman','build'])
        for flag in ['--memory=1536m','--cpu-quota=100000','--ulimit=nproc=256:256','--layers=false','--authfile']:
            self.assertIn(flag, build[0])
        self.assertEqual(build[1]['timeout'], 300)
        run = next((args, kw) for args, kw in self.calls if args[:2] == ['podman','run'])
        for flag in ['--network=none','--read-only','--cap-drop=all','--security-opt=no-new-privileges','--memory=1536m']:
            self.assertIn(flag, run[0])
        self.assertNotIn('--volume',run[0]); self.assertNotIn(str(self.root),run[0]); self.assertEqual(run[1]['timeout'],30)

    def test_per_profile_lock_refuses_concurrent_acquisition(self):
        with app.locked('toolchain-'+self.selected['profile_hash']):
            with self.assertRaises(app.AppError) as error: tools.acquire(self.selected)
        self.assertEqual(error.exception.code,'busy'); self.assertFalse(self.calls)

    def test_unsupported_platform_refused_before_commands(self):
        with patch.object(tools.platform,'machine',return_value='aarch64'):
            with self.assertRaises(app.AppError) as error: tools.acquire(self.selected)
        self.assertEqual(error.exception.code,'toolchain-platform'); self.assertFalse(self.calls)

    def test_unreceipted_or_retagged_image_is_never_overwritten(self):
        self.image = IMAGE
        with self.assertRaises(app.AppError): tools.acquire(self.selected)
        self.assertFalse(any(args[:2] == ['podman','build'] for args, _ in self.calls))
        self.image = None; tools.acquire(self.selected); self.image = 'sha256:'+'4'*64
        with self.assertRaises(app.AppError): tools.acquire(self.selected)

    def test_bad_image_label_or_architecture_is_refused(self):
        self.image = IMAGE
        for info in [{'Labels': {}, 'Os':'linux','Architecture':'amd64'}, {'Labels':{tools.LABEL:self.selected['profile_hash']},'Os':'linux','Architecture':'arm64'}]:
            with patch.object(app,'json_command',return_value=[{**info,'Id':IMAGE}]):
                with self.assertRaises(app.AppError): tools.acquire(self.selected)

    def test_actual_version_mismatch_never_records_verified(self):
        real = self.command
        def wrong(args, **kw):
            if args[:2] == ['podman','run']: return subprocess.CompletedProcess(args,0,'{}','')
            return real(args, **kw)
        with patch.object(app,'command',side_effect=wrong):
            with self.assertRaises(app.AppError): tools.acquire(self.selected)
        self.assertEqual(tools.record(self.selected)['phase'],'failed')
        with self.assertRaises(app.AppError): tools.acquire(self.selected)

    def test_failed_download_integrity_and_unknown_acquisition_are_honest(self):
        real = self.command
        def timeout(args, **kw):
            if args[:2] == ['podman','build']: raise app.AppError('timeout')
            return real(args, **kw)
        with patch.object(app,'command',side_effect=timeout):
            with self.assertRaises(app.AppError): tools.acquire(self.selected)
        receipt = tools.record(self.selected); self.assertEqual(receipt['phase'],'unknown')
        self.calls.clear()
        with self.assertRaises(app.AppError) as error: tools.acquire(self.selected)
        self.assertEqual(error.exception.code,'toolchain-recovery'); self.assertFalse(self.calls)
        self.assertEqual(tools.inspect(self.root)['state'],'recovery-required')

    def test_known_failed_absent_image_can_retry_without_replacing_failed_job(self):
        real = self.command
        def failure(args, **kw):
            if args[:2] == ['podman','build']: return subprocess.CompletedProcess(args,1,'synthetic artifact failure','')
            return real(args, **kw)
        with patch.object(app,'command',side_effect=failure):
            with self.assertRaises(app.AppError): tools.acquire(self.selected)
        previous = tools.record(self.selected); directory = tools.location(self.selected)/'jobs'/previous['operation_id']
        self.assertTrue((directory/'build.log').exists())
        self.assertTrue(tools.acquire(self.selected)['changed']); self.assertTrue(directory.exists())

    def test_missing_verified_image_recreates_same_profile_without_fallback(self):
        tools.acquire(self.selected); first = tools.record(self.selected)
        self.image = None; tools.acquire(self.selected); second = tools.record(self.selected)
        self.assertNotEqual(first['operation_id'], second['operation_id'])
        self.assertEqual(first['profile_hash'],second['profile_hash'])

    def test_receipt_drift_or_malformed_record_refused(self):
        tools.acquire(self.selected); path = tools.location(self.selected)/'receipt.json'; original = json.loads(path.read_text())
        for value in [{**original,'profile_hash':'0'*64}, {**original,'image':'node:latest'}, {**original,'schema_version':True}, {**original,'unknown': True}]:
            app.save(path,value)
            with self.assertRaises(app.AppError): tools.inspect(self.root)

    def test_explicit_prepare_invalidates_only_selected_state_and_preserves_source(self):
        other = Path(app.create('beta')['root']); _, c = app.target(other); b = app.reserve(other,c)
        _, c = app.target(self.root); s = app.reserve(self.root,c); s.update(prepared_digest='a'*64,build_digest='b'*64);app.save(app.STORE/'alpha.json',s)
        before = {n: (self.root/n).read_bytes() for n in deps.FILES}
        with patch.object(app,'object_owned',return_value=False): result = tools.prepare(self.root)
        self.assertEqual(result['state'],'verified'); self.assertEqual(app.state_for('beta'),b)
        self.assertNotIn('prepared_digest',app.state_for('alpha'))
        self.assertEqual(before,{n:(self.root/n).read_bytes() for n in deps.FILES})

    def test_prepare_refuses_running_target_without_acquisition(self):
        _, c = app.target(self.root); s = app.reserve(self.root,c); app.unit_path(s).write_text('fixture')
        with patch.object(app,'object_owned',return_value=False), patch.object(app,'inspect_service',return_value=(True,True)), patch.object(tools,'acquire') as acquire:
            with self.assertRaises(app.AppError) as error: tools.prepare(self.root)
            self.assertEqual(error.exception.code,'busy'); acquire.assert_not_called()

    def test_active_legacy_compatibility_and_changed_explicit_selection_refused(self):
        legacy = {**self.selected,'legacy':True}
        tools.assert_active(legacy,{})
        with self.assertRaises(app.AppError): tools.assert_active(self.selected,{})
        with self.assertRaises(app.AppError): tools.assert_active(self.selected,{'toolchain_hash':'0'*64})

    def test_distinct_profile_switch_invalidates_fingerprint_and_preserves_other_app(self):
        r, profiles = tools.registry(); r = copy.deepcopy(r)
        second = copy.deepcopy(r['profiles'][0]); second.update(profile_version=2, versions={'node':'26.0.0','pnpm':'12.10.1'})
        profiles[('node-pnpm',2)] = second
        other = Path(app.create('beta')['root']); _, c = app.target(other); b = app.reserve(other,c)
        _, c = app.target(self.root); s = app.reserve(self.root,c); s['image'] = IMAGE
        before = app.dependency_digest(s); s.update(prepared_digest=before,build_digest=before,toolchain_hash=self.selected['selection_hash'])
        app.save(app.STORE/'alpha.json',s)
        with patch.object(tools,'registry',return_value=(r,profiles)):
            self.sidecar({'schema_version':1,'profile':'node-pnpm','profile_version':2,'versions':second['versions']})
            chosen = tools.selection(self.root)
            with patch.object(app,'object_owned',return_value=False), patch.object(tools,'acquire',return_value={'state':'verified','receipt':{'image':'sha256:'+'4'*64}}):
                tools.prepare(self.root)
            switched = app.state_for('alpha')
            self.assertEqual(switched['toolchain_hash'],chosen['selection_hash'])
            self.assertNotEqual(app.dependency_digest(switched),before)
            self.assertNotIn('prepared_digest',switched); self.assertNotIn('build_digest',switched)
            self.assertEqual(app.state_for('beta'),b)
            self.assertIn(switched['image'],app.unit_text(switched,c,'app.example.ts.net'))

    def test_failed_reuse_verification_invalidates_cached_readiness(self):
        tools.acquire(self.selected)
        with patch.object(tools,'verify',side_effect=app.AppError('timeout')):
            with self.assertRaises(app.AppError):tools.acquire(self.selected)
        self.assertEqual(tools.inspect(self.root)['state'],'recovery-required')
        self.assertEqual(tools.record(self.selected)['phase'],'unknown')

    def test_prepare_does_not_save_stale_selection_after_concurrent_metadata_edit(self):
        def changed(selected):
            self.package(engines={'node':'>=24'})
            return {'receipt':{'image':IMAGE}}
        with patch.object(app,'object_owned',return_value=False),patch.object(tools,'acquire',side_effect=changed):
            with self.assertRaises(app.AppError) as error:tools.prepare(self.root)
        self.assertEqual(error.exception.code,'conflict')
        self.assertNotIn('toolchain_hash',app.state_for('alpha'))

    def test_service_observation_rejects_container_image_drift(self):
        _, contract = app.target(self.root); s = app.reserve(self.root,contract);s['image']=IMAGE
        with patch.object(app,'command',return_value=subprocess.CompletedProcess([],0,'active\n','')), patch.object(app,'object_owned',return_value=True), patch.object(app,'json_command',return_value=[{'Image':'4'*64}]):
            with self.assertRaises(app.AppError) as error:app.inspect_service(s,contract)
        self.assertEqual(error.exception.code,'conflict')

    def test_cli_typed_capabilities_and_inspection(self):
        with patch.object(gptclawctl,'os',SimpleNamespace(getuid=lambda:1002,geteuid=lambda:1002)), patch('sys.stdout',new_callable=io.StringIO) as out:
            self.assertEqual(gptclawctl.main(['toolchain','inspect','--project-root',str(self.root)]),0)
            self.assertEqual(json.loads(out.getvalue())['selection'],self.selected['declaration'])
        with patch('sys.stdout',new_callable=io.StringIO) as out:
            self.assertEqual(gptclawctl.main(['--version']),0);self.assertIn('toolchain',json.loads(out.getvalue())['capabilities'])


if __name__ == '__main__': unittest.main(verbosity=2)
