#!/usr/bin/env python3
"""Synthetic native build archives, durable job failures and native launch boundaries."""
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import private_apps as app
import project_templates as templates
import project_mobile as mobile
import native_builds as builds
import native_contract as contract
import native_runtime
import metro_sessions
import metro_state
import project_manifest


class NativeBuilds(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalogue = templates.catalogue()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        for name, value in [('PROJECTS', self.base), ('STORE', self.base / '.runtime'), ('UNITS', self.base / '.units')]:
            p = patch.object(app, name, value); p.start(); self.addCleanup(p.stop)
        p = patch.object(builds, 'security_gate'); p.start(); self.addCleanup(p.stop)
        p = patch.object(templates, 'catalogue', return_value=self.catalogue); p.start(); self.addCleanup(p.stop)
        self.root = Path(app.create('native-one', template='expo-development', template_version='1.0.0')['root'])
        self.document = app.target(self.root)[1]
        self.identity = {'project': 'native-one', 'key': 'a' * 64, 'root_identity': [1, 2]}
        p = patch.object(contract.worktrees, 'canonical', return_value=self.identity); p.start(); self.addCleanup(p.stop)
        self.config = {'schema_version': 1, 'platform': 'android', 'environment': 'development',
                       'account': 'synthetic-owner', 'project_id': '11111111-1111-1111-1111-111111111111',
                       'signing': 'expo-managed', 'certificate_sha256': 'b' * 64, 'retention_days': 30,
                       'artifact_access': 'authenticated', 'attempt_limit': 3, 'budget_cents': 2500,
                       'attempt_cost_ceiling_cents': 100, 'credential_scope': 'isolated-account',
                       'approval_id': 'synthetic-approval', 'expires_at': '2099-01-01T00:00:00Z'}
        app.save(self.root / contract.CONFIG, self.config)
        expo = json.loads((self.root / 'app.json').read_text())
        expo['expo'].update(owner=self.config['account'], extra={'eas': {'projectId': self.config['project_id']}})
        app.save(self.root / 'app.json', expo)
        self.git('init', '-q')
        self.git('config', 'user.name', 'Synthetic fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.commit()

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.root), *args], check=True, capture_output=True).stdout

    def commit(self):
        self.git('add', '--all'); self.git('commit', '--quiet', '--allow-empty', '-m', 'Synthetic fixture')

    def remote(self, value, status='IN_QUEUE'):
        return {'id': '22222222-2222-2222-2222-222222222222', 'platform': 'ANDROID',
                'buildProfile': 'development', 'distribution': 'INTERNAL', 'status': status,
                'appIdentifier': contract.identity('native-one')['android']['package'],
                'app': {'id': self.config['project_id'], 'ownerAccount': {'name': self.config['account']}},
                'message': 'gptclaw:' + value['operation_id'] + ':' + value['plan']['plan_digest']}

    def submit(self, fail=False):
        digest = builds.plan(self.root)[0]['plan_digest']
        def response(value, *args):
            self.assertEqual(builds.load('native-one', value['operation_id'])['state'], 'submitting')
            if fail:
                raise app.AppError('timeout')
            return self.remote(value)
        with patch.object(builds, 'toolchain', return_value='sha256:' + 'd' * 64), patch.object(builds, 'worker', side_effect=response):
            return builds.submit(self.root, digest, '/synthetic/not-read')

    def test_new_schema_generation_and_static_identity(self):
        self.assertEqual(self.document['schema_version'], 11)
        self.assertTrue(mobile.manifest_config(self.root, self.document))
        self.assertEqual(project_manifest.validate_project(self.root)[2], 0)
        self.assertNotEqual(contract.identity('native-one')['android']['package'], mobile.identities('native-one')['android']['package'])
        bound = Path(app.create('bound-two', template='expo-development-notes', template_version='1.0.0')['root'])
        self.assertEqual(project_manifest.validate_project(bound)[1]['schema_version'], 12)
        self.assertFalse((bound / '.gptclaw/backend.local.json').exists())

    def test_frozen_profile_preserves_legacy_packages(self):
        self.assertTrue(mobile.profile()['unsupported_native'])
        self.assertNotIn('expo-dev-client', mobile.profile()['packages'])
        self.assertEqual(mobile.profile(True)['packages']['expo-dev-client'], '57.0.20')
        legacy = copy.deepcopy(self.document); legacy['schema_version'] = 6
        self.assertTrue(list(project_manifest.load_schema(6)[1].iter_errors(legacy)))

    def test_exact_archive_is_deterministic_and_contains_no_local_metadata(self):
        first, _, data = builds.plan(self.root); second, _, again = builds.plan(self.root)
        self.assertEqual(first, second); self.assertEqual(data, again)
        with tarfile.open(fileobj=io.BytesIO(data)) as t:
            self.assertTrue(all(n.startswith('project/') for n in t.getnames()))
            self.assertFalse(any('.git' in n or 'backend.local' in n for n in t.getnames()))
        builds.verify_archive(data, first['inventory'])

    def test_dirty_source_refuses_before_remote(self):
        (self.root / 'src/native-demo.ts').write_text('changed')
        with self.assertRaises(app.AppError), patch.object(builds, 'worker') as remote:
            builds.public_plan(self.root)
        remote.assert_not_called()

    def test_tracked_symlink_and_gitlink_refuse(self):
        (self.root / 'src/escape.ts').symlink_to('/etc/passwd'); self.commit()
        with self.assertRaises(app.AppError): builds.plan(self.root)

    def test_forbidden_source_and_token_canaries_refuse(self):
        for name, data in [('secret.json', '{}'), ('fixture.ts', 'EXPO_TOKEN=' + 'synthetic-canary')]:
            path = self.root / 'src' / name; path.write_text(data); self.commit()
            with self.assertRaises(app.AppError): builds.plan(self.root)
            path.unlink(); self.commit()

    def test_archive_foreign_paths_duplicates_and_tamper_refuse(self):
        p, _, data = builds.plan(self.root)
        wrong = dict(p['inventory']); wrong['app.json'] = '0' * 64
        with self.assertRaises(app.AppError): builds.verify_archive(data, wrong)
        out = io.BytesIO()
        with tarfile.open(fileobj=out, mode='w:gz') as t:
            x = tarfile.TarInfo('project/../../escape'); x.size = 1; t.addfile(x, io.BytesIO(b'x'))
        with self.assertRaises(app.AppError): builds.verify_archive(out.getvalue(), {})

    def test_native_and_js_drift_have_different_compatibility(self):
        before = contract.fingerprint(self.root)
        p = self.root / 'src/native-demo.ts'; p.write_text(p.read_text() + '\n// JS-only edit\n')
        self.assertEqual(before, contract.fingerprint(self.root))
        p = self.root / 'app.json'; d = json.loads(p.read_text()); d['expo']['version'] = '1.0.1'; app.save(p, d)
        self.assertNotEqual(before, contract.fingerprint(self.root))

    def test_invalid_account_profile_config_and_dynamic_source_refuse(self):
        for key, val in [('environment', 'production'), ('account', 'other'), ('retention_days', True), ('budget_cents', -1)]:
            d = copy.deepcopy(self.config); d[key] = val; app.save(self.root / contract.CONFIG, d)
            with self.assertRaises(app.AppError): contract.inspect(self.root)
        app.save(self.root / contract.CONFIG, self.config)
        (self.root / 'app.config.js').write_text('throw new Error("must never execute")')
        self.assertFalse(mobile.manifest_config(self.root, self.document))

    def test_submit_records_intent_and_remote_identity(self):
        result = self.submit(); self.assertEqual(result['state'], 'queued')
        value = builds.load('native-one', result['operation_id'])
        self.assertEqual(value['plan']['commit'], self.git('rev-parse', 'HEAD').decode().strip())
        self.assertNotIn('synthetic/not-read', json.dumps(value))
        self.assertNotIn('artifacts', value)

    def test_ambiguous_submit_blocks_retry_and_can_reconcile(self):
        result = self.submit(fail=True); self.assertEqual(result['state'], 'unknown')
        with self.assertRaises(app.AppError): self.submit()
        value = builds.load('native-one', result['operation_id'])
        with patch.object(builds, 'worker', return_value=self.remote(value, 'FINISHED')):
            observed = builds.observe(self.root, result['operation_id'], '/synthetic/not-read', '22222222-2222-2222-2222-222222222222')
        self.assertEqual(observed['state'], 'succeeded')
        self.assertFalse(observed['artifact_verified'])

    def test_scoped_job_id_survives_incomplete_remote_metadata(self):
        digest=builds.plan(self.root)[0]['plan_digest']
        def response(value,*args):
            remote=self.remote(value);remote.pop('appIdentifier');return remote
        with patch.object(builds,'worker',side_effect=response):
            result=builds.submit(self.root,digest,'/not-read')
        self.assertEqual(result['state'],'unknown')
        self.assertEqual(result['job_id'],'22222222-2222-2222-2222-222222222222')
        with self.assertRaises(app.AppError):self.submit()

    def test_remote_identity_mismatch_leaves_unknown(self):
        digest = builds.plan(self.root)[0]['plan_digest']
        def response(value, *args):
            remote = self.remote(value); remote['app']['id'] = 'foreign'; return remote
        with patch.object(builds, 'toolchain', return_value='sha256:' + 'a' * 64), patch.object(builds, 'worker', side_effect=response):
            self.assertEqual(builds.submit(self.root, digest, '/not-read')['state'], 'unknown')

    def test_observation_failure_preserves_job_and_staleness(self):
        result = self.submit(); value = builds.load('native-one', result['operation_id'])
        with patch.object(builds, 'worker', side_effect=app.AppError('timeout')):
            observed = builds.observe(self.root, result['operation_id'], '/not-read')
        self.assertEqual(observed['state'], 'queued')
        self.assertEqual(observed['last_remote_at'], value['last_remote_at'])
        self.assertEqual(observed['observation'], 'unavailable')

    def test_budget_and_attempt_limits_precede_remote(self):
        d = dict(self.config, budget_cents=0, attempt_cost_ceiling_cents=0, attempt_limit=1)
        app.save(self.root / contract.CONFIG, d); self.commit()
        result = self.submit(); value = builds.load('native-one', result['operation_id']); value['state'] = 'failed'; builds.save(value)
        with patch.object(builds, 'worker') as remote, self.assertRaises(app.AppError): self.submit()
        remote.assert_not_called()

    def test_plan_drift_refuses_before_intent(self):
        with patch.object(builds, 'toolchain'), patch.object(builds, 'worker') as remote, self.assertRaises(app.AppError):
            builds.submit(self.root, '0' * 64, '/not-read')
        remote.assert_not_called(); self.assertEqual(builds.receipts('native-one'), [])

    def test_corrupt_receipt_blocks_recovery_and_new_submission(self):
        result = self.submit(); path = builds.directory('native-one') / result['operation_id'] / 'receipt.json'
        path.write_text('{}')
        with self.assertRaises(app.AppError): builds.load('native-one', result['operation_id'])
        with self.assertRaises(app.AppError): self.submit()

    def test_launch_requires_installation_and_native_compatibility(self):
        result = self.submit(); op = result['operation_id']
        self.assertEqual(builds.launch(self.root, op, 'a' * 32)['state'], 'installation-unknown')
        value = builds.load('native-one', op); value['state'] = 'succeeded'
        value['download_sha256']='a'*64
        value['artifact'] = {'sha256': 'a' * 64, 'package':contract.identity('native-one')['android']['package'],
                             'certificate_sha256':'b'*64,'job_id':value['job_id'],'verified_at':time.time(),
                             'expires_at':time.time()+60,'evidence':'apksig-8.13.0-and-binary-manifest'}
        value['installed'] = {'artifact_sha256': 'a' * 64, 'native_fingerprint': contract.fingerprint(self.root),
                              'os':'Android 11','reported_at':time.time()}; builds.save(value)
        descriptor = {'generation': 'c' * 32, 'transport_available': True, 'requested_mode': 'development-client',
                      'origin': 'https://synthetic.tailnet.ts.net:8443'}
        with patch.object(metro_sessions, 'status', return_value=descriptor):
            payload = builds.launch(self.root, op, 'c' * 32)
            self.assertTrue(payload['launch'].startswith('gptclaw-native-one-dev://expo-development-client/'))
            descriptor['origin'] = 'http://synthetic.tailnet.ts.net:8443'
            with self.assertRaises(app.AppError): builds.launch(self.root, op, 'c' * 32)
            descriptor['generation'] = 'b' * 32
            with self.assertRaises(app.AppError): builds.launch(self.root, op, 'c' * 32)
        value['installed']['native_fingerprint'] = 'e' * 64; builds.save(value)
        self.assertEqual(builds.launch(self.root, op, 'c' * 32)['state'], 'rebuild-required')

    def test_native_tool_image_must_be_owned_and_preparation_is_explicit(self):
        def result(code,text=''):
            return subprocess.CompletedProcess([],code,text,'')
        with patch.object(app,'command',return_value=result(1)) as command:
            with self.assertRaises(app.AppError):builds.reviewed_image('synthetic', 'a'*64,'scope',self.base,False,10)
            self.assertEqual(command.call_count,1)
        with patch.object(app,'command',side_effect=[result(0),result(0,'sha256:'+'b'*64+' foreign')]) as command:
            with self.assertRaises(app.AppError):builds.reviewed_image('synthetic','a'*64,'scope',self.base,True,10)
            self.assertFalse(any('build' in call.args[0] for call in command.call_args_list))
        with patch.object(app,'command',side_effect=[result(1),result(0),result(0,'sha256:'+'b'*64+' '+'a'*64)]):
            self.assertEqual(builds.reviewed_image('synthetic','a'*64,'scope',self.base,True,10),'sha256:'+'b'*64)

    def test_audit_gate_requires_complete_evidence(self):
        counts={k:0 for k in ['info','low','moderate','high','critical']}
        self.assertEqual(builds.audit_ok({'vulnerabilities':{},'metadata':{'vulnerabilities':counts}}),counts)
        with self.assertRaises(app.AppError):
            builds.audit_ok({'vulnerabilities':{'hidden':{'severity':'high'}},'metadata':{'vulnerabilities':counts}})
        with self.assertRaises(app.AppError):builds.audit_ok({'metadata':{'vulnerabilities':counts}})

    def test_native_repository_plan_carries_its_distinct_identity(self):
        import project_repositories as repos
        import test_project_repositories as fixtures
        api=fixtures.FakeAPI(self.base/'unused-synthetic-remote')
        plan=repos.plan('native-created',self.base/'native-created',api,template='expo-development',template_version='1.0.0')['plan']
        self.assertEqual(plan['mobile_inputs']['identity']['android']['package'],'dev.gptclaw.native_created.development')
        self.assertEqual(plan['mobile_inputs']['profile_digest'],contract.digest(mobile.profile(True)))

    def test_no_job_resolution_requires_explicit_attestation(self):
        result = self.submit(fail=True); op=result['operation_id']
        value=builds.load('native-one',op)
        with self.assertRaises(app.AppError):builds.resolve_not_submitted(self.root,op,'wrong')
        resolved=builds.resolve_not_submitted(self.root,op,op+':'+value['plan']['plan_digest'])
        self.assertEqual(resolved['state'],'failed')
        self.assertEqual(builds.load('native-one',op)['reserved_cost_cents'],100)

    def test_artifact_download_destinations_refuse_foreign_hosts(self):
        for url in ['http://expo.dev/file.apk','https://evil.invalid/file.apk','https://user@expo.dev/file.apk','https://expo.dev:8443/file.apk']:
            with self.assertRaises(app.AppError):builds.artifact_url(url)
        self.assertEqual(builds.artifact_url('https://expo.dev/artifacts/eas/synthetic.apk'),'https://expo.dev/artifacts/eas/synthetic.apk')

    def test_signed_metadata_alone_cannot_certify_wrong_job_or_bytes(self):
        result=self.submit();op=result['operation_id'];value=builds.load('native-one',op)
        value['state']='succeeded';builds.save(value)
        apk=self.base/'synthetic.apk';apk.write_bytes(b'not downloaded from this job')
        with self.assertRaises(app.AppError),patch.object(builds,'apk_toolchain') as verifier:
            builds.verified_artifact(self.root,op,apk)
        verifier.assert_not_called()

    def test_bound_native_configuration_uses_existing_typed_backend_contract(self):
        import mobile_backend
        backend=Path(app.create('native-api',template='fastapi-postgres',template_version='1.1.0')['root'])
        bound=Path(app.create('native-bound',template='expo-development-notes',template_version='1.0.0')['root'])
        with patch.object(app,'node_identity',return_value='synthetic.tailnet.ts.net'):
            result=mobile_backend.bind(bound,backend,'https://synthetic.tailnet.ts.net/projects/native-api/api')
            self.assertEqual(result['state'],'backend-bound')
            self.assertEqual(mobile_backend.inspect(bound)['backend'],'native-api')
        self.assertNotIn('password',(bound/mobile_backend.GENERATED).read_text())

    def test_native_runtime_never_accepts_go_advisory_exceptions(self):
        policy = native_runtime.policy(self.root); lock = (self.root / 'pnpm-lock.yaml').read_bytes()
        counts = {x: 0 for x in ['info', 'low', 'moderate', 'high', 'critical']}
        self.assertEqual(native_runtime.evaluate({'advisories': {}, 'metadata': {'vulnerabilities': counts}}, policy, lock)['temporary_exceptions'], [])
        counts['high'] = 1
        with self.assertRaises(app.AppError):
            native_runtime.evaluate({'advisories': {'go-exception': {'severity': 'high'}}, 'metadata': {'vulnerabilities': counts}}, policy, lock)

    def test_native_http_refusal_precedes_any_runtime_mutation(self):
        with patch.object(metro_sessions.spike, 'require_operator'), patch.object(app, 'command') as command, self.assertRaises(app.AppError):
            metro_sessions.start(self.root, transport='tailnet-http')
        command.assert_not_called()


if __name__ == '__main__':
    unittest.main()
