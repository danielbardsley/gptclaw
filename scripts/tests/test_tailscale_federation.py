#!/usr/bin/env python3
"""Offline synthetic tests; never contact AWS/Tailscale or enroll the host."""
import importlib.util
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
path = ROOT / 'infra/dev-host/lib/tailscale_federation.py'
spec = importlib.util.spec_from_file_location('federation', path)
f = importlib.util.module_from_spec(spec)
spec.loader.exec_module(f)
CONFIG = dict(client_id='synthetic-client-id', audience='api.tailscale.com/synthetic-client-id',
              tag='tag:gptclaw-dev', hostname='forge-dev-01', region='us-east-1')
ONLINE = {'BackendState': 'Running', 'Self': {'Online': True, 'Tags': ['tag:gptclaw-dev'], 'TailscaleIPs': ['100.64.0.1']}}

class Fake:
    def __init__(self, version='1.94.0', initial=None, final=None):
        self.calls=[]; self.version=version; self.status=initial or {'BackendState':'NeedsLogin'}
        self.final=ONLINE if final is None else final
    def __call__(self,args,region):
        self.calls.append(args)
        if args[1]=='version': return self.version+'\n'
        if args[1]=='up': self.status=self.final; return ''
        return json.dumps(self.status)

class Tests(unittest.TestCase):
    def test_fresh_enrollment_without_keys(self):
        fake=Fake(); self.assertEqual(f.enroll(CONFIG,fake)['status'],'passed')
        up=next(a for a in fake.calls if a[1]=='up')
        self.assertIn('--client-id=synthetic-client-id?ephemeral=false&preauthorized=true',up)
        self.assertIn('--audience=api.tailscale.com/synthetic-client-id',up)
        self.assertIn('--ssh=false',up)
        self.assertFalse(any('auth-key' in a for a in up))
    def test_existing_matching_node_is_not_reenrolled(self):
        fake=Fake(initial=ONLINE); f.enroll(CONFIG,fake)
        self.assertFalse(any(a[1]=='up' for a in fake.calls))
    def test_old_or_invalid_client_fails_before_enrollment(self):
        for version in ['1.92.9','broken','']:
            fake=Fake(version)
            with self.assertRaises((f.EnrollmentError,IndexError)): f.enroll(CONFIG,fake)
            self.assertFalse(any(a[1]=='up' for a in fake.calls))
    def test_wrong_state_tag_or_offline_never_succeeds(self):
        for status in [{'BackendState':'NeedsLogin'}, {'BackendState':'Running','Self':{'Online':False}},
                       {'BackendState':'Running','Self':{'Online':True,'TailscaleIPs':['100.64.0.1'],'Tags':['tag:other']}}]:
            with self.assertRaises(f.EnrollmentError): f.enroll(CONFIG,Fake(final=status))
    def test_bad_configuration_precedes_commands(self):
        for key,value in [('client_id','x;bad'),('audience','https://elsewhere'),('tag','tag:prod'),('hostname','bad\nname'),('region','us-west-2')]:
            config=dict(CONFIG);config[key]=value; fake=Fake()
            with self.assertRaises(f.EnrollmentError): f.enroll(config,fake)
            self.assertEqual(fake.calls,[])
    def test_command_failure_does_not_expose_output(self):
        with patch.object(f.subprocess,'run') as run:
            run.return_value.returncode=1;run.return_value.stdout='sensitive diagnostic'
            with self.assertRaises(f.EnrollmentError) as caught: f.command(['tailscale','up'],'us-east-1')
            self.assertNotIn('sensitive',str(caught.exception))
    def test_timeout_is_bounded_and_sanitized(self):
        with patch.object(f.subprocess,'run',side_effect=subprocess.TimeoutExpired('token',180)):
            with self.assertRaises(f.EnrollmentError): f.command(['tailscale','up'],'us-east-1')
    def test_environment_cannot_inherit_static_aws_credentials(self):
        with patch.dict(f.os.environ, {'AWS_ACCESS_KEY_ID':'synthetic','AWS_SECRET_ACCESS_KEY':'synthetic'}), patch.object(f.subprocess,'run') as run:
            run.return_value.returncode=0;run.return_value.stdout='ok'
            f.command(['tailscale','version'],'us-east-1')
            env=run.call_args.kwargs['env']
            self.assertNotIn('AWS_ACCESS_KEY_ID',env)
            self.assertEqual(env['AWS_SHARED_CREDENTIALS_FILE'],'/dev/null')
            self.assertEqual(env['AWS_REGION'],'us-east-1')
    def test_checkout_cannot_enroll(self):
        result=subprocess.run(['python3',str(path)],capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
    def test_account_stack_is_protected_and_isolated(self):
        text=(ROOT/'infra/tailscale-federation/main.tf').read_text()
        self.assertIn('prevent_destroy = true',text)
        self.assertNotIn('resource "aws_instance"',text)
        workflow=(ROOT/'.github/workflows/terraform-tailscale-federation.yml').read_text()
        self.assertIn('environment: federation-bootstrap',workflow)
        self.assertIn('TF_WORKSPACE: gptclaw-tailscale-federation',workflow)
        self.assertIn('inputs.operation == \'apply\'',workflow)
        self.assertIn('"$GITHUB_SHA" != "$current_main_sha"',workflow)
    def test_migration_never_deletes_legacy_secret(self):
        text=(ROOT/'infra/dev-host/secrets.tf').read_text()
        self.assertIn('destroy = false',text)
        self.assertIn('prevent_destroy = true',text)
        self.assertNotIn('secret_string_wo =',text)

if __name__=='__main__': unittest.main(verbosity=2)
