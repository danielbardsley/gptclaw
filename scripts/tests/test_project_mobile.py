#!/usr/bin/env python3
"""Offline native generation, policy, identity and non-HTTP regression scenarios."""
import copy
import hashlib
import io
import json
from pathlib import Path
import os
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import private_apps as app
import project_mobile as mobile
import project_templates as templates
import project_dependencies as deps
import project_toolchains as tools
import gptclawctl as cli
from dashboard_inventory import Scanner
from dashboard_status import StatusStore


class MobileTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        self.projects=Path(temp.name)/'projects';self.projects.mkdir()
        self.units=Path(temp.name)/'units';self.units.mkdir()
        for name,value in [('PROJECTS',self.projects),('STORE',self.projects/'.gptclaw-runtime/v1'),('UNITS',self.units)]:
            p=patch.object(app,name,value);p.start();self.addCleanup(p.stop)
        self.release,self.contents=templates.resolve('expo-react-native','1.0.1')
    def new(self,name='mobile-one',**kwargs):
        return Path(app.create(name,template='expo-react-native',template_version='1.0.1',**kwargs)['root'])
    def test_exact_discovery_preserves_web_default(self):
        with patch.object(app,'command') as command:
            data=templates.discover();self.assertEqual(data['default']['id'],'nextjs')
            self.assertEqual(templates.discover('expo-react-native','1.0.0')['release']['manifest_schema'],5)
            command.assert_not_called()
    def test_two_offline_creations_normalize_identity(self):
        with patch.object(app,'command') as command:
            one,two=self.new(),self.new('mobile-two');command.assert_not_called()
        for root in [one,two]:
            self.assertEqual(app.validate_project(root)[2],0)
            self.assertFalse((root/'node_modules').exists())
            self.assertNotIn('service',app.target(root)[1])
        import project_guidance as guidance
        copied, _ = guidance.payload(lambda name: (app.REPO/name).read_bytes(), ['runtime', 'android'])
        names = sorted(set(self.contents) | set(copied) |
                       set(guidance.APP_TEMPLATES.values()) | {'docs/starter-guidance-provenance.json'})
        self.assertEqual(names,sorted(p.relative_to(one).as_posix() for p in one.rglob('*') if p.is_file() and '.gptclaw' not in p.relative_to(one).parts))
        for name in names:
            first, second = (one/name).read_bytes(), (two/name).read_bytes()
            if name in {'docs/README.md', 'docs/platform/features.md'}:
                first = first.replace(b'Mobile One', b'Identity')
                second = second.replace(b'Mobile Two', b'Identity')
            if name == 'docs/starter-guidance-provenance.json':
                records = [json.loads(first), json.loads(second)]
                for root, record in zip([one, two], records):
                    for target, item in record['files'].items():
                        self.assertEqual(item['sha256'], hashlib.sha256((root/target).read_bytes()).hexdigest())
                        if target in {'docs/README.md', 'docs/platform/features.md'}:
                            item['sha256'] = 'normalized-project-identity'
                self.assertEqual(*records)
            elif name != 'app.json':
                self.assertEqual(first, second, name)
        self.assertNotEqual(json.loads((one/'app.json').read_text())['expo']['ios'],json.loads((two/'app.json').read_text())['expo']['ios'])
        self.assertFalse(list(self.units.iterdir()));self.assertFalse(list(app.STORE.glob('*.json')))
    def test_identity_mapping_platform_grammars(self):
        value=mobile.identities('a-b-c');self.assertEqual(value['ios']['bundleIdentifier'],'dev.gptclaw.a-b-c');self.assertEqual(value['android']['package'],'dev.gptclaw.a_b_c')
        for slug in ['A','a_b','a--b','a-','a'*49]:
            with self.assertRaises(app.AppError):mobile.identities(slug)
    def test_same_id_different_destination_refused(self):
        one=self.new()
        with self.assertRaises(app.AppError):self.new(directory=str(self.projects/'other'))
        self.assertFalse((self.projects/'other').exists());self.assertTrue((one/'app.json').is_file())
    def test_existing_destination_and_symlink_preserved(self):
        path=self.projects/'occupied';path.mkdir();(path/'mine').write_text('retain')
        with self.assertRaises(app.AppError):self.new(directory=str(path))
        self.assertEqual((path/'mine').read_text(),'retain')
        (self.projects/'linked').symlink_to(path)
        with self.assertRaises(app.AppError):self.new(directory=str(self.projects/'linked'))
    def test_corrupt_release_creates_nothing(self):
        content=dict(self.contents);content['app.json']=b'{}'
        with self.assertRaises(app.AppError):templates.generate(self.projects/'bad','bad',self.release,content)
        self.assertFalse((self.projects/'bad').exists())
    def test_mobile_policy_edits_are_refused_before_jobs(self):
        root=self.new();(root/'checks/advisory-policy.json').write_text('{}')
        with patch.object(app,'run_in_app') as run:
            with self.assertRaises(app.AppError):app.target(root)
            run.assert_not_called()

    def test_source_edit_preserves_provenance(self):
        root=self.new();(root/'src/app/index.tsx').write_text('edited source')
        templates.validate_provenance(root);self.assertEqual(app.target(root)[1]['project']['kind'],'mobile')
    def test_static_config_and_dynamic_native_denials(self):
        root=self.new();original=(root/'app.json').read_bytes()
        for name in ['app.config.js','app.config.ts','app.config.json','ios','android']:
            path=root/name;path.write_text('untrusted')
            self.assertNotEqual(app.validate_project(root)[2],0);path.unlink()
        (root/'app.json').unlink();(root/'app.json').symlink_to('/dev/null')
        self.assertNotEqual(app.validate_project(root)[2],0)
        (root/'app.json').unlink();(root/'app.json').write_bytes(original)
        value=json.loads(original);value['expo']['android']['package']='invalid-hyphen';(root/'app.json').write_text(json.dumps(value))
        self.assertNotEqual(app.validate_project(root)[2],0)
    def test_unknown_mobile_manifest_fields(self):
        root=self.new();value=app.target(root)[1];value['service']={};(root/'.gptclaw/project.yaml').write_text(json.dumps(value))
        self.assertNotEqual(app.validate_project(root)[2],0)
    def test_sdk_core_change_rejected_before_job(self):
        root=self.new();package=json.loads((root/'package.json').read_text());package['dependencies']['react-native']='0.87.1'
        with self.assertRaises(app.AppError):mobile.validate_package(package)
        with patch.object(app,'run_in_app') as run,patch.object(app,'object_owned',return_value=False):
            with self.assertRaises(app.AppError):deps.operate(root,'update','react-native','0.87.1')
            run.assert_not_called()
    def test_unknown_native_module_rejected_before_job(self):
        root=self.new()
        with patch.object(app,'run_in_app') as run,patch.object(app,'object_owned',return_value=False):
            with self.assertRaises(app.AppError):deps.operate(root,'add','unknown-native','1.0.0')
            run.assert_not_called()
    def test_context_and_toolchain_match_existing_exact_profile(self):
        root=self.new();self.assertEqual(deps.context(root)['policy']['manager_version'],'12.10.1')
        self.assertEqual(tools.selection(root)['profile']['versions'],{'node':'24.21.0','pnpm':'12.10.1'})
    def test_read_only_dependency_inspection(self):
        root=self.new();before=sorted(str(p) for p in app.STORE.rglob('*'))
        with patch.object(app,'command') as command:
            result=deps.status(root);command.assert_not_called()
        self.assertEqual(result['state'],'unprepared');self.assertEqual(before,sorted(str(p) for p in app.STORE.rglob('*')))
    def test_lifecycle_denied_without_ports_units_commands(self):
        root=self.new();before=sorted(str(p) for p in app.STORE.rglob('*'))
        with patch.object(app,'command') as command:
            for action in ['start','stop','restart','status','observe','logs','hooks']:
                with self.subTest(action=action),self.assertRaises(app.AppError) as failure:
                    mobile.dispatch(SimpleNamespace(action=action,project_root=str(root)))
                self.assertEqual(failure.exception.code,'mobile-unsupported')
            command.assert_not_called()
        self.assertEqual(before,sorted(str(p) for p in app.STORE.rglob('*')));self.assertFalse(list(self.units.iterdir()))
    def test_job_descriptor_never_reserves_http(self):
        root=self.new();document=app.target(root)[1]
        with patch.object(app,'reserve') as reserve,patch.object(app,'object_owned',return_value=False):
            value=deps.stopped_state(root,document);reserve.assert_not_called()
        self.assertNotIn('port',value);self.assertEqual(value['adapter'],'mobile')
        mobile.invalidate(value,True);self.assertEqual(mobile.load_state(root,'mobile-one')['phase'],'idle')
        self.assertFalse(list(app.STORE.glob('*.json')))
    def test_job_root_binding_conflict(self):
        root=self.new()
        with patch.object(app,'object_owned',return_value=False):mobile.job_state(root,app.target(root)[1])
        with self.assertRaises(app.AppError):mobile.load_state(root/'other','mobile-one')
    def fake_dependency_job(self,state,argv,**kwargs):
        import base64
        root=Path(state['root'])
        if '--lockfile-only' in argv:
            package=json.loads((root/'package.json').read_text());importer={};packages={}
            for group in deps.GROUPS:
                if group not in package:continue
                importer[group]={}
                for name,version in package[group].items():
                    importer[group][name]={'specifier':version,'version':version}
                    packages[name+'@'+version]={'resolution':{'integrity':'sha512-'+base64.b64encode(bytes(64)).decode()}}
            (root/'pnpm-lock.yaml').write_text(json.dumps({'lockfileVersion':'9.0','importers':{'.':importer},'packages':packages,'snapshots':{}}))
        else:(root/'node_modules').mkdir(exist_ok=True)
        return subprocess.CompletedProcess(argv,0,'','')

    def test_mobile_dependency_transaction_and_source_preservation(self):
        root=self.new();original=(root/'src/components/Counter.tsx').read_bytes()
        with patch.object(app,'object_owned',return_value=False),patch.object(app,'toolchain',return_value='sha256:'+'2'*64),patch.object(app,'run_in_app',side_effect=self.fake_dependency_job):
            deps.operate(root,'install');self.assertEqual(deps.status(root)['state'],'dependencies-ready')
            deps.operate(root,'add','zod','4.3.6');self.assertEqual(json.loads((root/'package.json').read_text())['dependencies']['zod'],'4.3.6')
            deps.operate(root,'remove','zod');self.assertNotIn('zod',json.loads((root/'package.json').read_text())['dependencies'])
        self.assertEqual(original,(root/'src/components/Counter.tsx').read_bytes());self.assertFalse(list(app.STORE.glob('*.json')))

    def test_mobile_interrupted_install_recovers_same_operation(self):
        root=self.new()
        with patch.object(app,'object_owned',return_value=False),patch.object(app,'toolchain',return_value='sha256:'+'2'*64):
            with patch.object(app,'run_in_app',side_effect=app.AppError('timeout')):
                with self.assertRaises(app.AppError):deps.operate(root,'install')
            operation=deps.status(root)['operation']['operation_id']
            with patch.object(app,'run_in_app',side_effect=self.fake_dependency_job):
                deps.operate(root,'recover',operation_id=operation)
            self.assertEqual(deps.status(root)['state'],'dependencies-ready')

    def test_unknown_job_fields_refuse_environment_forwarding(self):
        root=self.new()
        with patch.object(app,'object_owned',return_value=False):state=mobile.job_state(root,app.target(root)[1])
        state['job_env']={'UNKNOWN':'synthetic'};app.save(mobile.location('mobile-one'),state)
        with self.assertRaises(app.AppError):mobile.load_state(root,'mobile-one')

    def test_inventory_without_http_components_or_observation(self):
        self.new();caps={'provider':'gptclawctl','project_manifest_schemas':[1,2,3,4,5],'runtime_manifest_schemas':[1,2,3,4]}
        scanner=Scanner(self.projects,capabilities=caps);snapshot=scanner.scan();self.assertEqual(len(snapshot['rows']),1)
        row=snapshot['rows'][0];self.assertEqual(row['kind'],'mobile');self.assertEqual(row['components'],[]);self.assertEqual(row['runtime_support'],'unsupported')
        with patch('dashboard_status.status_job') as observe:
            store=StatusStore(lambda *args:observe());store.round(scanner.bindings);observe.assert_not_called()
            result=store.snapshot(row['key'],scanner.bindings[row['key']]);self.assertEqual(result['reason'],'unsupported');self.assertEqual(result['freshness'],'unavailable')
    def test_provider_bundle_has_mobile_assets(self):
        paths=app.provider_bundle()
        self.assertTrue((paths/'scripts/project_mobile.py').is_file());self.assertTrue((paths/'schemas/project/v5.schema.json').is_file());self.assertTrue((paths/'config/templates/v5.json').is_file())


if __name__=='__main__':unittest.main()
