#!/usr/bin/env python3
"""Offline Python contract, ownership, dependency conflict/recovery regressions."""
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import private_apps as app
import project_dependencies as deps
import project_manifest as manifests
import project_python as py
import project_templates as templates
import project_toolchains as tools

IMAGE='sha256:'+'4'*64


class PythonTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='gptclaw-python-test-');self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name);self.projects=self.base/'projects';self.projects.mkdir();self.units=self.base/'units';self.units.mkdir()
        for key,value in [('PROJECTS',self.projects),('STORE',self.projects/'.gptclaw-runtime/v1'),('UNITS',self.units)]:
            p=patch.object(app,key,value);p.start();self.addCleanup(p.stop)
        p=patch.object(app,'available',return_value=True);p.start();self.addCleanup(p.stop)
        self.root=Path(app.create('sample-api',template='fastapi',template_version='1.0.0')['root'])

    def mock_jobs(self):
        for key in ['object_owned','toolchain','run_in_app']:
            p=patch.object(app,key,return_value=IMAGE if key=='toolchain' else False if key=='object_owned' else subprocess.CompletedProcess([],0,'',''));p.start();self.addCleanup(p.stop)

    def fake_uv(self,state,argv,**kwargs):
        root=Path(state['root'])
        if argv[1]=='sync':
            (root/'.venv').mkdir(exist_ok=True);return subprocess.CompletedProcess(argv,0,'','')
        self.assertEqual(argv[1:3],['add','annotated-doc==0.0.5'])
        path=root/'pyproject.toml';text=path.read_text();text=re.sub(r'(dependencies\s*=\s*\[)',r'\1"annotated-doc==0.0.5", ',text,count=1);path.write_text(text)
        path=root/'uv.lock';text=path.read_text().replace('requires-dist = [','requires-dist = [\n    { name = "annotated-doc", specifier = "==0.0.5" },',1);path.write_text(text)
        return subprocess.CompletedProcess(argv,0,'','')

    def test_generation_complete_and_v1_default_unchanged(self):
        self.assertEqual(manifests.validate_project(self.root)[2],0)
        contract=app.target(self.root)[1];self.assertEqual(contract['schema_version'],2)
        self.assertEqual(contract['service']['health']['path'],'/projects/sample-api/ready')
        self.assertTrue((self.root/'docs/python-standards.md').is_file())
        self.assertTrue((self.root/'.pre-commit-config.yaml').is_file())
        self.assertFalse((self.root/'.venv').exists());self.assertFalse((self.root/'.cache').exists())
        web=Path(app.create('sample-web')['root']);self.assertEqual(app.target(web)[1]['schema_version'],1)
        self.assertEqual(templates.resolve()[0]['id'],'nextjs')

    def test_observation_does_not_execute_or_import_application(self):
        (self.root/'src/fastapi_app/main.py').write_text('raise RuntimeError("never imported")\n')
        with patch.object(app,'command') as run,patch.object(app,'save') as save:
            self.assertEqual(manifests.validate_project(self.root)[2],0)
            templates.validate_provenance(self.root);py.context(self.root);tools.selection(self.root)
            run.assert_not_called();save.assert_not_called()

    def test_bad_manifest_versions_and_missing_quality_vectors(self):
        file=self.root/'.gptclaw/project.yaml';original=json.loads(file.read_text())
        for version in [True,2.0,'2',3]:
            value=copy.deepcopy(original);value['schema_version']=version;file.write_text(json.dumps(value));self.assertNotEqual(manifests.validate_project(self.root)[2],0)
        value=copy.deepcopy(original);del value['commands']['security'];file.write_text(json.dumps(value));self.assertEqual(manifests.validate_project(self.root)[2],1)

    def test_api_route_conflict_is_refused_before_runtime_mutation(self):
        with patch.object(app,'route_info',side_effect=app.AppError('conflict')),patch.object(app,'command') as command:
            with self.assertRaises(app.AppError):app.start(self.root)
            command.assert_not_called()
        self.assertFalse((app.STORE/'sample-api.json').exists())

    def test_provider_marker_must_match_manifest(self):
        app.save(self.root/'.gptclaw/template.json',{'provider':'nextjs-v1'})
        with self.assertRaises(app.AppError):app.target(self.root)

    def test_api_requires_explicit_release_provenance(self):
        (self.root/'.gptclaw/template-release.json').unlink()
        with self.assertRaises(app.AppError):app.target(self.root)

    def test_profile_declaration_and_interpreter_mismatches(self):
        self.assertEqual(tools.selection(self.root)['declaration']['versions'],{'python':'3.13.16','uv':'0.13.0'})
        file=self.root/'.python-version';file.write_text('3.12.3\n')
        with self.assertRaises(app.AppError):tools.selection(self.root)
        file.write_text('3.13.16\n');declaration=app.read_json(self.root/'.gptclaw/toolchain.json');declaration['profile_version']=999;app.save(self.root/'.gptclaw/toolchain.json',declaration)
        with self.assertRaises(app.AppError):tools.selection(self.root)

    def test_metadata_rejects_hooks_sources_workspaces_and_dotenv(self):
        original=(self.root/'pyproject.toml').read_text()
        for addition in ['\n[build-system]\nrequires=["setuptools"]\n','\n[tool.uv]\nindex-url="https://unknown.invalid"\n','\n[tool.uv.sources]\nfastapi={git="https://unknown.invalid"}\n']:
            (self.root/'pyproject.toml').write_text(original+addition)
            with self.assertRaises(app.AppError):py.context(self.root)
        (self.root/'pyproject.toml').write_text(original)
        for filename in ['.env.example','.netrc','uv.toml','pip.conf']:
            p=self.root/filename;p.write_text('synthetic only\n')
            with self.assertRaises(app.AppError):py.context(self.root)
            p.unlink()

    def test_dependency_ranges_and_lock_freshness_rejected(self):
        p=self.root/'pyproject.toml';old=p.read_text()
        p.write_text(old.replace('fastapi==0.143.0','fastapi>=0.143.0'))
        with self.assertRaises(app.AppError):py.context(self.root)
        p.write_text(old.replace('fastapi==0.143.0','fastapi==0.142.0'))
        with self.assertRaises(app.AppError):py.context(self.root)

    def test_lock_origins_and_hashes_rejected(self):
        p=self.root/'uv.lock';old=p.read_text()
        for text in [old.replace('https://pypi.org/simple','https://unknown.invalid',1),old.replace('https://files.pythonhosted.org','https://unknown.invalid',1),old.replace('sha256:','md5:',1),old.replace('registry = "https://pypi.org/simple"','git = "https://unknown.invalid"',1)]:
            p.write_text(text)
            with self.assertRaises(app.AppError):py.context(self.root)
        p.write_text(old)

    def test_symlink_dependency_file_refused(self):
        p=self.root/'uv.lock';p.rename(self.root/'saved.lock');p.symlink_to(self.root/'saved.lock')
        with self.assertRaises(app.AppError):py.context(self.root)

    def test_preparation_uses_locked_uv_and_readonly_metadata(self):
        self.mock_jobs();contract=app.target(self.root)[1];s=app.reserve(self.root,contract);s['image']=IMAGE;s['toolchain_hash']=tools.selection(self.root)['selection_hash']
        with patch.object(app,'run_in_app',side_effect=self.fake_uv) as run:
            app.prepare(s,contract,build=False)
            self.assertEqual(run.call_args.args[1][:4],['uv','sync','--locked','--all-groups'])
            self.assertTrue(run.call_args.kwargs['read_only_dependency_files'])
            app.prepare(s,contract,build=False);self.assertEqual(run.call_count,1)
        old=s['prepared_digest'];p=self.root/'pyproject.toml';p.write_text(p.read_text()+'\n# dependency fingerprint\n');self.assertNotEqual(old,app.dependency_digest(s))

    def test_uv_job_guards_and_mounts(self):
        s=app.reserve(self.root,app.target(self.root)[1]);s['image']=IMAGE
        with patch.object(app,'command',return_value=subprocess.CompletedProcess([],1,'','')) as command:
            app.run_in_app(s,['uv','sync'],read_only_dependency_files=True)
            argv=command.call_args.args[0]
            self.assertIn('UV_PYTHON_DOWNLOADS=never',argv);self.assertIn('UV_NO_CONFIG=1',argv)
            for name in py.FILES:self.assertIn(str(self.root/name)+':/workspace/'+name+':ro',argv)
            self.assertFalse(any('.aws' in value or 'docker.sock' in value for value in argv))

    def test_python_quadlet_retains_loopback_limits_and_fixed_environment(self):
        contract=app.target(self.root)[1];s=app.reserve(self.root,contract);s['image']=IMAGE
        text=app.unit_text(s,contract,'synthetic.ts.net')
        self.assertIn('PublishPort=127.0.0.1:',text);self.assertIn('UV_PYTHON_DOWNLOADS=never',text)
        self.assertIn('PYTHONPATH=/workspace/src',text);self.assertIn('NoNewPrivileges=true',text)
        self.assertIn('"--no-proxy-headers"',text)

    def test_typed_dependency_add_transaction(self):
        self.mock_jobs()
        with patch.object(app,'run_in_app',side_effect=self.fake_uv):result=deps.operate(self.root,'add','annotated-doc','0.0.5')
        self.assertEqual(result['state'],'complete');self.assertEqual(deps.load_journal('sample-api',self.root)['schema_version'],2)
        self.assertEqual(py.context(self.root)['groups']['runtime']['annotated-doc'],'0.0.5')
        self.assertEqual(deps.status(self.root)['state'],'dependencies-ready')

    def test_concurrent_editor_change_preserved_and_abort_coherent(self):
        self.mock_jobs();before=(self.root/'pyproject.toml').read_text()
        def edited(state,argv,**kwargs):
            result=self.fake_uv(state,argv,**kwargs)
            if argv[1]=='add':(self.root/'pyproject.toml').write_text(before+'\n# concurrent editor\n')
            return result
        with patch.object(app,'run_in_app',side_effect=edited):
            with self.assertRaises(app.AppError) as error:deps.operate(self.root,'add','annotated-doc','0.0.5')
        self.assertEqual(error.exception.code,'conflict');self.assertIn('concurrent editor',(self.root/'pyproject.toml').read_text())
        journal=deps.load_journal('sample-api',self.root);self.assertEqual(journal['phase'],'conflict')
        result=deps.operate(self.root,'recover',operation_id=journal['operation_id'],abort=True);self.assertEqual(result['state'],'aborted')

    def test_interrupted_publication_recovers_same_operation(self):
        self.mock_jobs();original=deps.publish_file;count=[0]
        def interrupted(root,name,journal):
            original(root,name,journal);count[0]+=1
            if count[0]==1:raise app.AppError('timeout')
        with patch.object(app,'run_in_app',side_effect=self.fake_uv),patch.object(deps,'publish_file',side_effect=interrupted):
            with self.assertRaises(app.AppError):deps.operate(self.root,'add','annotated-doc','0.0.5')
        journal=deps.load_journal('sample-api',self.root);self.assertEqual(journal['phase'],'unknown')
        with patch.object(app,'run_in_app',side_effect=self.fake_uv):result=deps.operate(self.root,'recover',operation_id=journal['operation_id'])
        self.assertEqual(result['state'],'complete');self.assertEqual(py.context(self.root)['groups']['runtime']['annotated-doc'],'0.0.5')

    def test_failed_install_not_ready_and_active_operations_refused(self):
        self.mock_jobs()
        with patch.object(app,'run_in_app',side_effect=app.AppError('command')):
            with self.assertRaises(app.AppError):deps.operate(self.root,'install')
        self.assertEqual(deps.status(self.root)['state'],'recovery-required')
        with patch.object(app,'object_owned',return_value=True):
            with self.assertRaises(app.AppError) as error:deps.operate(self.root,'install')
            self.assertEqual(error.exception.code,'busy')

    def test_invalid_requests_do_not_acquire_or_run(self):
        self.mock_jobs()
        for name,version in [('bad/name','1.0.0'),('annotated-doc','latest'),('annotated-doc','1.0;bad')]:
            with self.assertRaises(app.AppError):deps.operate(self.root,'add',name,version)
        app.run_in_app.assert_not_called();app.toolchain.assert_not_called()

    def test_noop_remove_and_wrong_recovery_id_preserve_source(self):
        self.mock_jobs();before=py.context(self.root)['hashes']
        self.assertFalse(deps.operate(self.root,'remove','not-present')['changed'])
        with self.assertRaises(app.AppError):deps.operate(self.root,'recover',operation_id='0'*32)
        self.assertEqual(py.context(self.root)['hashes'],before)

    def test_python_acquisition_verifies_actual_versions_and_reuse(self):
        selected=tools.selection(self.root); image=[None];calls=[]
        def command(argv,**kwargs):
            calls.append(argv)
            if argv[:3]==['podman','container','exists']:return subprocess.CompletedProcess(argv,1,'','')
            if argv[:2]==['podman','build']:image[0]=IMAGE;return subprocess.CompletedProcess(argv,0,'','')
            if argv[:2]==['podman','run']:return subprocess.CompletedProcess(argv,0,json.dumps(selected['profile']['versions']),'')
            raise AssertionError(argv)
        with patch.object(app,'command',side_effect=command),patch.object(tools,'image_info',side_effect=lambda _:image[0]):
            first=tools.acquire(selected);second=tools.acquire(selected)
            self.assertTrue(first['changed']);self.assertFalse(second['changed'])
            self.assertEqual(first['receipt']['versions'],{'python':'3.13.16','uv':'0.13.0'})
            self.assertEqual(sum(call[:2]==['podman','build'] for call in calls),1)
            self.assertTrue(any('--network=none' in call for call in calls))
            with patch.object(app,'command',return_value=subprocess.CompletedProcess([],0,'{}','')):
                with self.assertRaises(app.AppError):tools.verify(selected,IMAGE,'0'*32)

    def test_explicit_hooks_preserve_unknown_hook_and_are_idempotent(self):
        self.mock_jobs();(self.root/'.git/hooks').mkdir(parents=True)
        hook=self.root/'.git/hooks/pre-commit';hook.write_text('unknown hook\n')
        with self.assertRaises(app.AppError):app.install_hooks(self.root)
        self.assertEqual(hook.read_text(),'unknown hook\n');hook.unlink()
        self.assertTrue(app.install_hooks(self.root)['changed'])
        self.assertIn(' verify --project-root ',hook.read_text())
        self.assertFalse(app.install_hooks(self.root)['changed'])

    def test_bundled_profile_and_assets_include_python_not_cache(self):
        bundle=app.provider_bundle()
        self.assertTrue((bundle/'scripts/project_python.py').is_file())
        self.assertTrue((bundle/'config/templates/v2.json').is_file())
        self.assertFalse(list(bundle.rglob('.venv')));self.assertFalse(list(bundle.rglob('.cache')))


if __name__=='__main__':unittest.main(verbosity=2)
