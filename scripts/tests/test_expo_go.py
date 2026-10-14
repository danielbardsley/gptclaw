#!/usr/bin/env python3
"""Eligibility drift, ownership, client and no-hidden-operation boundaries."""
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
from contextlib import redirect_stdout
from types import SimpleNamespace
import unittest
from unittest.mock import patch
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import private_apps as app
import project_mobile as mobile
import expo_go as go
import metro_sessions as sessions
import gptclawctl as cli


class Tests(unittest.TestCase):
    def setUp(self):
        temporary=tempfile.TemporaryDirectory();self.addCleanup(temporary.cleanup)
        self.projects=Path(temporary.name);self.root=self.projects/'one';self.root.mkdir()
        self.document=mobile.contract('one');self.document['schema_version']=6
        (self.root/'.gptclaw').mkdir();(self.root/'.gptclaw/toolchain.json').write_text(json.dumps(mobile.profile()['toolchain']))
        matrix=mobile.profile()
        self.package={'gptclawMobile':'expo-v1','main':'expo-router/entry','dependencies':matrix['packages']}
        (self.root/'package.json').write_text(json.dumps(self.package))
        (self.root/'app.json').write_text(json.dumps({'expo':{**mobile.identities('one'),
            'version':'1.0.0','platforms':['ios','android'],'orientation':'portrait'}}))
        (self.root/'pnpm-lock.yaml').write_bytes((app.REPO/'templates/apps/releases/expo-react-native/1.0.0/pnpm-lock.yaml').read_bytes())
        for target,name,value in [(app,'PROJECTS',self.projects),(app,'target',lambda root:(self.root,self.document)),
                                  (go.worktrees,'canonical',lambda root:{'key':'a'*64})]:
            mocked=patch.object(target,name,value);mocked.start();self.addCleanup(mocked.stop)
        selection=patch.object(go.tools,'selection',return_value={'declaration':{'schema_version':1,**mobile.profile()['toolchain']}})
        self.selection=selection.start();self.addCleanup(selection.stop)
        mocked=patch.object(sessions,'status',return_value={'state':'ready','transport_available':True})
        self.session=mocked.start();self.addCleanup(mocked.stop)
    def inspect(self,**kwargs):return go.inspect(self.root,'android','57.0.9','11',**kwargs)
    def test_ready_metro_and_reported_matching_client_never_certify_phone(self):
        result=self.inspect()
        self.assertTrue(result['source_eligible']);self.assertTrue(result['transport_available'])
        self.assertEqual(result['state'],'unsupported');self.assertFalse(result['launch_available'])
        self.assertEqual(result['reason'],'expo-go-android-requires-private-http-session')
        self.assertTrue(result['requires_http_devserver'])
        self.assertEqual(result['follow_up'],'MOB-004')
        self.assertEqual(result['physical_client_acceptance'],'unverified')
        self.assertNotIn('origin',result);self.assertNotIn('generation',result)
    def test_approved_http_session_still_does_not_certify_phone_or_launch(self):
        self.session.return_value = {'schema_version': 2, 'transport': 'private-tailnet-http',
                                     'state': 'ready', 'transport_available': True}
        result = self.inspect()
        self.assertEqual(result['state'], 'check-required')
        self.assertEqual(result['reason'], 'physical-client-and-launch-rule-unverified')
        self.assertFalse(result['launch_available'])
        self.assertEqual(result['physical_client_acceptance'], 'unverified')

    def test_unknown_client_or_os_requires_owner_check(self):
        for client,os in [(None,None),('57.0.9',None),(None,'11')]:
            self.assertEqual(go.inspect(self.root,'android',client,os)['reason'],'report-installed-client-and-os')
    def test_foreign_client_routes_to_separate_build_scope(self):
        result=go.inspect(self.root,'android','56.0.1','11')
        self.assertEqual(result['state'],'unsupported');self.assertEqual(result['follow_up'],'MOB-004')
        self.assertFalse(result['launch_available'])
    def test_ios_assumption_does_not_certify_os_or_launch(self):
        result=go.inspect(self.root,'ios','57.0.9','19.0')
        self.assertEqual(result['reason'],'expo-go-cli-login-outside-scope');self.assertFalse(result['launch_available'])
        self.assertTrue(result['requires_cli_login']);self.assertEqual(result['follow_up'],'MOB-004')
    def test_lock_drift_is_unsupported_without_source_mutation(self):
        path=self.root/'pnpm-lock.yaml';path.write_bytes(path.read_bytes()+b'\n# changed graph\n')
        original=path.read_bytes();result=self.inspect()
        self.assertEqual(result['reason'],'source-graph-not-in-go-profile');self.assertFalse(result['source_eligible'])
        self.assertEqual(path.read_bytes(),original)
    def test_native_package_and_dynamic_config_drift_block(self):
        self.package['dependencies']['react-native']='0.87.0'
        (self.root/'package.json').write_text(json.dumps(self.package))
        with self.assertRaises(app.AppError):self.inspect()
        self.package['dependencies']['react-native']=mobile.profile()['packages']['react-native']
        (self.root/'package.json').write_text(json.dumps(self.package))
        (self.root/'app.config.js').write_text('throw new Error("do not execute")')
        with self.assertRaises(app.AppError):self.inspect()
    def test_profile_drift_does_not_implicitly_recertify(self):
        original=go.deps.read_bytes
        for field,value in [('sdk',58),('certification_max_age_seconds',604801),('source_profile_sha256','0'*64)]:
            candidate=go.profile();candidate[field]=value
            def read(path,*args):
                return json.dumps(candidate).encode() if Path(path).name=='expo-go-v1.json' else original(path,*args)
            with patch.object(go.deps,'read_bytes',side_effect=read):
                with self.assertRaises(app.AppError):go.profile()
    def test_unreviewed_acquisition_or_hidden_login_bypass_is_rejected(self):
        original=go.deps.read_bytes
        for field,value in [('acquisition_source','https://untrusted.invalid'),('requires_cli_login',False)]:
            candidate=go.profile();candidate['targets']['ios'][field]=value
            def read(path,*args):
                return json.dumps(candidate).encode() if Path(path).name=='expo-go-v1.json' else original(path,*args)
            with patch.object(go.deps,'read_bytes',side_effect=read):
                with self.assertRaises(app.AppError):go.profile()
    def test_known_android_http_requirement_cannot_be_silently_bypassed(self):
        original = go.deps.read_bytes
        for field, value in [('requires_http_devserver', False), ('status', 'unsupported')]:
            candidate = go.profile(); candidate['targets']['android'][field] = value
            def read(path, *args):
                return json.dumps(candidate).encode() if Path(path).name == 'expo-go-v1.json' else original(path, *args)
            with patch.object(go.deps, 'read_bytes', side_effect=read):
                with self.assertRaises(app.AppError): go.profile()

    def test_wrong_toolchain_is_not_eligible(self):
        self.selection.return_value={'declaration':{'schema_version':1,'profile':'foreign'}}
        with self.assertRaises(app.AppError):self.inspect()
    def test_false_certification_in_profile_is_rejected(self):
        candidate=go.profile();candidate['targets']['android']['launch_rule_verified']=True
        original=go.deps.read_bytes
        def read(path,*args):
            return json.dumps(candidate).encode() if Path(path).name=='expo-go-v1.json' else original(path,*args)
        with patch.object(go.deps,'read_bytes',side_effect=read):
            with self.assertRaises(app.AppError):go.profile()
    def test_malformed_caller_metadata_and_target_are_denied(self):
        for platform,client,os in [('web','57.0.9','11'),('android','57.0.9?token=x','11'),('android','57.0.9','owner-device-id')]:
            with self.assertRaises(app.AppError):go.inspect(self.root,platform,client,os)
    def test_source_only_and_stopped_remain_separate_from_client_state(self):
        self.document['schema_version']=5;result=self.inspect()
        self.assertEqual(result['metro_state'],'source-only');self.assertFalse(result['transport_available'])
        self.session.assert_not_called()
        self.document['schema_version']=6;self.session.return_value={'state':'expired','transport_available':False}
        self.assertEqual(self.inspect()['metro_state'],'expired')
    def test_inspection_never_starts_or_routes_and_does_not_write_source(self):
        before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in self.root.iterdir() if p.is_file()}
        with patch.object(sessions,'start',side_effect=AssertionError('hidden start')),             patch.object(sessions.routes,'plan',side_effect=AssertionError('hidden route')):
            self.inspect()
        self.assertEqual(before,{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in self.root.iterdir() if p.is_file()})
    def test_cli_rejects_root_and_foreign_operator_without_dispatch(self):
        for uid in [0,1001]:
            with patch.object(cli,'os',SimpleNamespace(getuid=lambda:uid,geteuid=lambda:uid)),\
                 patch.object(go,'inspect') as inspect,redirect_stdout(io.StringIO()),\
                 __import__('contextlib').redirect_stderr(io.StringIO()):
                result=cli.main(['go','inspect','--project-root',str(self.root),'--platform','android'])
            self.assertEqual(result,2);inspect.assert_not_called()
    def test_cli_inspect_forwards_exact_bounded_fields(self):
        with patch.object(cli,'os',SimpleNamespace(getuid=lambda:1002,geteuid=lambda:1002)),             patch.object(go,'inspect',return_value={'state':'check-required'}) as inspect,             patch.object(go.worktrees,'guard'),redirect_stdout(io.StringIO()):
            result=cli.main(['go','inspect','--project-root',str(self.root),'--platform','android',
                             '--client-version','57.0.9','--os-version','11'])
        self.assertEqual(result,0);inspect.assert_called_once_with(str(self.root),'android','57.0.9','11')


if __name__=='__main__':unittest.main()
