#!/usr/bin/env python3
"""Offline host-tool tests: all installers, network and systemd calls are fake."""
import copy
import datetime as dt
import importlib.util
import json
import os
import sys
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / 'infra/dev-host/lib/host_tools.py'
spec = importlib.util.spec_from_file_location('host_tools', HELPER)
ht = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ht)
BASE = ht.load(ROOT / 'infra/dev-host/host-tools.json')
TODAY = dt.date(2026, 10, 1)


def candidate(version='1.0', host='archive.ubuntu.com'):
    return f'  Candidate: {version}\n  Version table:\n     {version} 500\n        500 http://{host}/ubuntu noble/main amd64 Packages\n'


class Fake:
    def __init__(self):
        self.calls = []
        self.present = True
        self.fail = None
        self.version = '1.0'

    def __call__(self, args, optional=False, umask=-1):
        self.calls.append(args)
        if self.fail and self.fail in args:
            raise ht.ProfileError('synthetic command failure')
        if args[0] == 'dpkg-query':
            return 'installed ' + self.version if self.present else None
        if args[:2] == ['systemctl', 'show']:
            return 'loaded' if self.present and args[-1] == 'amazon-ssm-agent.service' else 'not-found'
        if args[0].endswith('/amazon-ssm-agent'):
            return 'SSM Agent version: 3.3.1.0'
        if args[0] == 'test':
            return '' if self.present and args[-1] != '/usr/local/aws-cli' else None
        if '/usr/local/bin/aws' in args:
            return 'aws-cli/2.31.0 Python/3.13 Linux/amd64'
        if args[0] == '/usr/bin/tailscale':
            return '1.88.0\n  version details'
        if args[-1] == '--version' and 'forge' in args:
            return 'codex-cli 0.40.0'
        if args[:2] == ['apt-cache', 'policy']:
            return candidate(self.version)
        if args[0] == 'curl':
            Path(args[-1]).write_bytes(b'synthetic artifact')
        if args[0] in ('apt-get', 'dpkg', 'snap', 'sh', 'sudo') or args[0].endswith('/aws/install'):
            self.present = True
        return ''


class HostToolsTests(unittest.TestCase):
    def setUp(self):
        self.profile = copy.deepcopy(BASE)
        # Fixture time is fixed, never extend the deployed policy to make tests pass.
        self.valid_patch = patch.object(ht, 'validate', side_effect=lambda p: original_validate(p, TODAY))
        self.valid_patch.start()
        self.addCleanup(self.valid_patch.stop)

    def invalid(self, mutate):
        p = copy.deepcopy(self.profile)
        mutate(p)
        with self.assertRaises(ht.ProfileError):
            ht.Provisioner(p, Fake())

    def test_baseline_and_duplicate_json(self):
        original_validate(self.profile, TODAY)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'p.json'
            p.write_text('{"schema_version":1,"schema_version":1}')
            with self.assertRaises(ht.ProfileError):
                ht.load(p)

    def test_invalid_shapes_and_unsafe_values_before_commands(self):
        mutations = [
            lambda p: p.update(schema_version=True),
            lambda p: p.update(schema_version=1.0),
            lambda p: p.update(schema_version=2),
            lambda p: p.update(extra='x'),
            lambda p: p.update(components={}),
            lambda p: p['target'].update(extra='x'),
            lambda p: p['components'].append(copy.deepcopy(p['components'][0])),
            lambda p: p['components'][0].update(adapter='shell'),
            lambda p: p['components'][0].update(identity='forge'),
            lambda p: p['components'][0].update(source='https://evil.invalid'),
            lambda p: p['components'][0].update(package='--allow-unauthenticated'),
            lambda p: p['components'][0].update(package='curl; id'),
            lambda p: p['components'][0].update(verification='sh -c id'),
            lambda p: p['components'][0].update(extra='x'),
            lambda p: p['components'][0]['version'].update(policy='latest'),
            lambda p: p['components'][0]['version'].update(value='$(id)'),
            lambda p: p['components'][0].pop('owner'),
            lambda p: p['components'][1].update(package=p['components'][0]['package']),
            lambda p: p['components'].pop(),
            lambda p: p['components'].pop(0),
        ]
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                self.invalid(mutate)

    def test_exception_dates_and_scope(self):
        p = self.profile
        original_validate(p, dt.date(2026, 11, 1))
        for day in (dt.date(2026, 9, 30), dt.date(2026, 11, 2)):
            with self.assertRaises(ht.ProfileError):
                original_validate(p, day)
        for field, value in [('owner', 'someone'), ('scope', 'other'), ('expires_on', 'bad')]:
            self.invalid(lambda p: p['components'][-1]['version']['exception'].update({field:value}))

    def test_selected_origin_and_version(self):
        ht.check_ubuntu_candidate(candidate())
        ht.check_ubuntu_candidate(candidate(host='us-east-1.ec2.archive.ubuntu.com'))
        for policy, selected in [(candidate(host='evil-ubuntu.example'), None),
                                 (candidate(), '9.9'),
                                 (candidate().replace('noble/main', 'jammy/main'), None),
                                 ('  Candidate: (none)', None),
                                 (candidate()+'        500 https://evil.invalid noble/main amd64 Packages\n',None)]:
            with self.assertRaises(ht.ProfileError):
                ht.check_ubuntu_candidate(policy, selected)

    def test_repeat_is_observation_only(self):
        fake = Fake()
        engine = ht.Provisioner(self.profile, fake)
        for _ in range(2):
            for c in self.profile['components']:
                engine.install(c)
        self.assertFalse(any(c[0] in ('apt-get','curl','snap','sh','unzip','dpkg') for c in fake.calls))

    def test_install_missing_apt_and_no_silent_exact_fallback(self):
        fake = Fake(); fake.present = False
        engine = ht.Provisioner(self.profile, fake)
        engine.install(self.profile['components'][0])
        self.assertIn(['apt-get','install','-y','--no-install-recommends','--','ca-certificates'],fake.calls)
        c = self.profile['components'][0]
        c['version'].update(policy='exact',value='9.9')
        fake = Fake(); fake.present = False
        engine = ht.Provisioner(self.profile, fake)
        with self.assertRaises(ht.ProfileError): engine.install(c)
        self.assertFalse(any(x[0]=='apt-get' for x in fake.calls))

    def test_existing_version_conflict_does_not_downgrade(self):
        c = self.profile['components'][0]
        c['version'].update(policy='exact',value='0.9')
        fake=Fake(); engine=ht.Provisioner(self.profile,fake)
        with self.assertRaises(ht.ProfileError): engine.install(c)
        self.assertFalse(any(x[0]=='apt-get' for x in fake.calls))

    def test_bad_artifact_never_executes(self):
        c = next(c for c in self.profile['components'] if c['adapter']=='aws-cli')
        c['version'].update(policy='exact',value='2.31.0',sha256='0'*64,exception=None)
        c['source']='https://awscli.amazonaws.com/awscli-exe-linux-x86_64-2.31.0.zip'
        fake=Fake(); fake.present=False
        engine=ht.Provisioner(self.profile,fake)
        with self.assertRaisesRegex(ht.ProfileError,'integrity'): engine.install(c)
        self.assertFalse(any(x[0]=='unzip' or x[0].endswith('/aws/install') for x in fake.calls))

    def test_download_failure_has_no_fallback(self):
        fake=Fake(); fake.present=False; fake.fail='curl'
        engine=ht.Provisioner(self.profile,fake)
        with self.assertRaises(ht.ProfileError): engine.install(self.profile['components'][-1])
        self.assertEqual(sum(x[0]=='curl' for x in fake.calls),1)
        self.assertFalse(any(x[0]=='sudo' for x in fake.calls))

    def test_channel_installers_and_codex_identity(self):
        for c in self.profile['components']:
            if c['adapter']=='apt': continue
            fake=Fake(); fake.present=False
            engine=ht.Provisioner(self.profile,fake)
            engine.install(c)
            if c['adapter']=='codex':
                calls=[x for x in fake.calls if x[:5]==['sudo','-u','forge','-H','env']]
                self.assertEqual(len(calls),1)
                self.assertIn('CODEX_INSTALL_DIR=/home/forge/.local/bin',calls[0])

    def test_aws_installer_permissions_are_scoped(self):
        c = next(c for c in self.profile['components'] if c['adapter'] == 'aws-cli')
        fake = Fake(); fake.present = False
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            def runner(args, optional=False, umask=-1):
                if args[0].endswith('/aws/install'):
                    # Exercise the real subprocess wrapper with a synthetic installer.
                    ht.run([sys.executable, '-c',
                            "from pathlib import Path; import sys; p=Path(sys.argv[1]); "
                            "(p/'cli').mkdir(); (p/'cli'/'library').write_text('fixture')",
                            d], umask=umask)
                elif args[0] == 'unzip':
                    self.assertEqual(umask, 0o022)
                else:
                    self.assertEqual(umask, -1)
                return fake(args, optional=optional)
            previous = os.umask(0o027)
            try:
                ht.Provisioner(self.profile, runner).install(c)
                (root/'private').write_text('fixture')
            finally:
                os.umask(previous)
            self.assertEqual((root/'cli').stat().st_mode & 0o777, 0o755)
            self.assertEqual((root/'cli'/'library').stat().st_mode & 0o777, 0o644)
            self.assertEqual((root/'private').stat().st_mode & 0o777, 0o640)

    def test_receipt_requires_aws_execution_as_forge(self):
        fake = Fake()
        def denied(args, optional=False, **kwargs):
            if args[:4] == ['sudo', '-u', 'forge', '-H']:
                raise ht.ProfileError('synthetic permission denied')
            return fake(args, optional=optional, **kwargs)
        with self.assertRaisesRegex(ht.ProfileError, 'permission denied'):
            ht.Provisioner(self.profile, denied).receipt('1'*40)
        def mismatch(args, optional=False, **kwargs):
            if args[:4] == ['sudo', '-u', 'forge', '-H']:
                return 'aws-cli/2.0.0 synthetic'
            return fake(args, optional=optional, **kwargs)
        with self.assertRaisesRegex(ht.ProfileError, 'inconsistent'):
            ht.Provisioner(self.profile, mismatch).receipt('1'*40)
        self.assertEqual(ht.Provisioner(self.profile, fake).receipt('1'*40)['status'], 'passed')

    def test_retire_optional_package_preserves_others(self):
        optional=copy.deepcopy(self.profile['components'][0]); optional.update(id='optional-tool',package='ripgrep')
        before=copy.deepcopy(self.profile); before['components'].append(optional)
        original_validate(before,TODAY)
        fake=Fake(); engine=ht.Provisioner(self.profile,fake)
        engine.phase('base-packages')
        self.assertFalse(any('ripgrep' in x or 'remove' in x or 'autoremove' in x for x in fake.calls))

    def test_conflicting_ssm_units_are_not_repaired(self):
        fake=Fake()
        def both(args, optional=False):
            if args[:2]==['systemctl','show']: return 'loaded'
            return fake(args,optional=optional)
        engine=ht.Provisioner(self.profile,both)
        c=next(c for c in self.profile['components'] if c['adapter']=='ssm')
        with self.assertRaisesRegex(ht.ProfileError,'conflicting SSM'): engine.install(c)
        self.assertEqual(fake.calls,[])

    def test_failed_final_verification_cannot_publish_receipt(self):
        with tempfile.TemporaryDirectory() as d:
            state=Path(d); p=state/'profile.json'; p.write_text(json.dumps(self.profile))
            context=state/'context.json'; context.write_text(json.dumps({'deployment_revision':'1'*40}))
            (state/'host-tools.json').write_text('stale-success')
            with patch.object(ht,'STATE',state), patch.object(ht,'PROFILE',p), \
                 patch.object(ht,'CONTEXT',context), patch.object(ht,'check_target'), \
                 patch.object(ht,'__file__','/usr/local/libexec/gptclaw-host-tools'), \
                 patch.object(ht.os,'geteuid',return_value=0), \
                 patch('sys.argv',['host-tools','finish']), \
                 patch.object(ht.Provisioner,'verify',side_effect=ht.ProfileError('missing tool')):
                self.assertEqual(ht.main(),1)
            self.assertFalse((state/'host-tools.json').exists())
            self.assertFalse((state/'bootstrap-complete.json').exists())

    def test_receipt_complete_sanitized_and_failed_probe(self):
        fake=Fake(); engine=ht.Provisioner(self.profile,fake)
        receipt=engine.receipt('1'*40)
        self.assertEqual(len(receipt['components']),len(self.profile['components']))
        self.assertEqual(receipt['profile_digest'],ht.digest(self.profile))
        self.assertNotIn('source',json.dumps(receipt))
        fake.fail='--version'
        with self.assertRaises(ht.ProfileError): engine.receipt('1'*40)

    def test_atomic_interruption_and_invalidation_preserve_unrelated(self):
        with tempfile.TemporaryDirectory() as d:
            state=Path(d)
            for name in ('host-tools.json','bootstrap-complete.json','unrelated'):
                (state/name).write_text('old')
            ht.invalidate(state)
            self.assertEqual((state/'unrelated').read_text(),'old')
            with patch.object(ht.os,'replace',side_effect=OSError('synthetic interruption')):
                with self.assertRaises(OSError): ht.atomic(state/'host-tools.json',{'status':'passed'})
            self.assertFalse((state/'host-tools.json').exists())
            self.assertEqual(list(state.iterdir()),[state/'unrelated'])
            ht.atomic(state/'host-tools.json',{'status':'passed'})
            self.assertEqual((state/'host-tools.json').stat().st_mode & 0o777,0o644)

    def test_failed_cli_attempt_clears_stale_success_before_validation(self):
        with tempfile.TemporaryDirectory() as d:
            state=Path(d)
            profile=state/'profile.json'
            profile.write_text('{"schema_version":99}')
            for name in ('host-tools.json','bootstrap-complete.json'):
                (state/name).write_text('old-success')
            with patch.object(ht,'STATE',state), patch.object(ht,'PROFILE',profile), \
                 patch.object(ht,'__file__','/usr/local/libexec/gptclaw-host-tools'), \
                 patch.object(ht.os,'geteuid',return_value=0), \
                 patch('sys.argv',['host-tools','begin']), patch.object(ht,'run') as runner:
                self.assertEqual(ht.main(),1)
                runner.assert_not_called()
            self.assertFalse((state/'host-tools.json').exists())
            self.assertFalse((state/'bootstrap-complete.json').exists())

    def test_structural_schema_matches_baseline(self):
        import jsonschema
        schema=ht.load(ROOT/'infra/dev-host/host-tools.schema.json')
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.validate(self.profile,schema)
        p=copy.deepcopy(self.profile); p['components'][0]['version']['command']='id'
        with self.assertRaises(jsonschema.ValidationError): jsonschema.validate(p,schema)

    def test_checkout_cannot_provision(self):
        result=subprocess.run(['python3',str(HELPER),'begin'],capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('restricted',result.stdout)

    def test_bootstrap_invalidation_and_phase_order(self):
        s=(ROOT/'infra/dev-host/templates/bootstrap-forge.sh.tftpl').read_text()
        self.assertLess(s.index('rm -f /var/lib/gptclaw/bootstrap-complete.json'),s.index('command -v python3'))
        self.assertLess(s.index('phase base-packages'),s.index('current_phase="forge-user"'))
        self.assertLess(s.index('current_phase="host-policy"'),s.index('phase codex'))
        self.assertLess(s.index('host-tools finish'),s.index('mv /var/lib/gptclaw/.bootstrap-complete'))
        self.assertNotIn('apt-get install',s)
        self.assertNotIn('curl -fsSL',s)


original_validate=ht.validate
if __name__=='__main__':
    unittest.main(verbosity=2)
