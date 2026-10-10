#!/usr/bin/env python3
"""Offline release and generation failure/race tests; no host service operations."""
import copy
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import private_apps as app
import project_templates as templates
import gptclawctl as cli


class Tests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        self.base=Path(temp.name);self.repo=self.base/'repo';self.repo.mkdir()
        for rel in ['config/templates','schemas/templates','config/toolchains','schemas/toolchains','config/project-dependencies','schemas/project-dependencies','schemas/project','templates/apps/releases','templates/apps/node-toolchain']:
            shutil.copytree(app.REPO/rel,self.repo/rel)
        shutil.copytree(app.REPO/'scripts',self.repo/'scripts',ignore=shutil.ignore_patterns('__pycache__'))
        self.projects=self.base/'projects';self.projects.mkdir()
        for key,value in [('REPO',self.repo),('PROJECTS',self.projects),('STORE',self.projects/'.gptclaw-runtime/v1')]:
            p=patch.object(app,key,value);p.start();self.addCleanup(p.stop)
        self.catalogue=templates.data(self.repo/'config/templates/v1.json')
    def write(self,value=None):
        (self.repo/'config/templates/v1.json').write_text(json.dumps(value or self.catalogue))
    def seal(self,r):
        r['digest']=templates.digest({k:v for k,v in r.items() if k!='digest'})
    def new(self,name='alpha',**kwargs):
        return Path(app.create(name,**kwargs)['root'])
    def test_discovery_observation_only(self):
        before=sorted(str(p) for p in self.base.rglob('*'))
        with patch.object(app,'command') as run,patch.object(app,'save') as save:
            a=templates.discover();b=templates.discover();self.assertEqual(a,b)
            self.assertEqual(templates.discover('nextjs','1.0.0')['release']['data'],'ephemeral')
            run.assert_not_called();save.assert_not_called()
        self.assertEqual(before,sorted(str(p) for p in self.base.rglob('*')))
    def test_cli_discovery_and_exact_pair(self):
        output=io.StringIO()
        with contextlib.redirect_stdout(output):self.assertEqual(cli.main(['templates','list']),0)
        self.assertEqual(json.loads(output.getvalue())['schema_version'],1)
        with self.assertRaises(app.AppError):app.create('bad',template='nextjs')
        self.assertFalse((self.projects/'bad').exists())
    def test_unknown_range_and_mismatched_selection(self):
        for pair in [('python','1.0.0'),('nextjs','latest'),('nextjs','^1.0.0'),('nextjs','2.0.0')]:
            with self.assertRaises(app.AppError):app.create('alpha',template=pair[0],template_version=pair[1])
        self.assertFalse((self.projects/'alpha').exists())
    def test_bad_schema_unknown_keys_and_duplicates(self):
        for changed in [dict(self.catalogue,schema_version=True),dict(self.catalogue,extra=True),dict(self.catalogue,releases=self.catalogue['releases']*2)]:
            self.write(changed)
            with self.assertRaises(app.AppError):templates.catalogue()
        (self.repo/'config/templates/v1.json').write_text('{"schema_version":1,"schema_version":1}')
        with self.assertRaises(app.AppError):templates.catalogue()
    def test_content_missing_or_modified(self):
        path=self.repo/'templates/apps/releases/nextjs/1.0.0/README.md';path.write_text('changed')
        with self.assertRaises(app.AppError):self.new()
        path.unlink()
        with self.assertRaises(app.AppError):self.new()
        self.assertFalse((self.projects/'alpha').exists())
    def test_invalid_paths_and_reserved_outputs(self):
        for name in ['../README.md','/tmp/x','app/../x','app//x','./x','.', '.gptclaw/toolchain.json','node_modules/x','.env.local']:
            c=copy.deepcopy(self.catalogue);r=c['releases'][0];r['files'][0]['output']=name;self.seal(r);self.write(c)
            with self.assertRaises(app.AppError):self.new()
            self.assertFalse((self.projects/'alpha').exists())
    def test_symlink_asset_and_ancestor_refused(self):
        root=self.repo/'templates/apps/releases/nextjs/1.0.0';path=root/'README.md';path.unlink();path.symlink_to('/dev/null')
        with self.assertRaises(app.AppError):templates.catalogue()
        path.unlink();path.write_text('x')
        folder=root/'app';folder.rename(root/'saved');folder.symlink_to(root/'saved',target_is_directory=True)
        with self.assertRaises(app.AppError):templates.catalogue()
    def test_duplicate_outputs_and_parent_collision(self):
        for change in ['README.md','app']:
            c=copy.deepcopy(self.catalogue);r=c['releases'][0];r['files'][0]['output']=change;self.seal(r);self.write(c)
            with self.assertRaises(app.AppError):templates.catalogue()
    def test_bad_digest_and_toolchain(self):
        c=copy.deepcopy(self.catalogue);c['releases'][0]['digest']='0'*64;self.write(c)
        with self.assertRaises(app.AppError):templates.catalogue()
        c=copy.deepcopy(self.catalogue);r=c['releases'][0];r['toolchain']['versions']['node']='1.0.0';self.seal(r);self.write(c)
        with self.assertRaises(app.AppError):templates.catalogue()
    def test_distinct_release_default_and_explicit_selection(self):
        release=copy.deepcopy(self.catalogue['releases'][0]);release['version']='1.0.1'
        base=self.repo/'templates/apps/releases/nextjs';shutil.copytree(base/'1.0.0',base/'1.0.1')
        path=base/'1.0.1/README.md';path.write_text('Synthetic other release\n')
        import hashlib
        next(x for x in release['files'] if x['source']=='README.md')['sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
        self.seal(release);self.catalogue['releases'].append(release);self.catalogue['default']={'id':'nextjs','version':'1.0.1'};self.write()
        one=self.new(template='nextjs',template_version='1.0.0');two=self.new('beta')
        self.assertNotEqual((one/'README.md').read_bytes(),(two/'README.md').read_bytes())
        self.assertEqual(json.loads((two/'.gptclaw/template-release.json').read_text())['version'],'1.0.1')
        self.assertEqual(json.loads((one/'.gptclaw/toolchain.json').read_text()),release['toolchain'])
    def test_release_toolchain_independent_of_registry_default(self):
        path=self.repo/'config/toolchains/v1.json';value=json.loads(path.read_text())
        second=copy.deepcopy(value['profiles'][0]);second['profile_version']=2
        value['profiles'].append(second);value['default']={'profile':'node-pnpm','profile_version':2}
        path.write_text(json.dumps(value))
        root=self.new()
        self.assertEqual(json.loads((root/'.gptclaw/toolchain.json').read_text())['profile_version'],1)

    def test_concurrent_processes_publish_one_complete_destination(self):
        code="import private_apps as a,pathlib,sys,json; a.REPO=pathlib.Path(sys.argv[1]);a.PROJECTS=pathlib.Path(sys.argv[2]);a.STORE=a.PROJECTS/'.gptclaw-runtime/v1';\ntry: print(json.dumps(a.create('alpha')))\nexcept a.AppError as e: print(e.code);sys.exit(1)"
        env=os.environ.copy();env['PYTHONPATH']=str(self.repo/'scripts')
        processes=[subprocess.Popen([sys.executable,'-B','-c',code,str(self.repo),str(self.projects)],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True) for _ in range(2)]
        outputs=[p.communicate(timeout=20) for p in processes]
        self.assertEqual(sorted(p.returncode for p in processes),[0,1],outputs)
        app.target(self.projects/'alpha')
        self.assertFalse(list(self.projects.glob('.gptclaw-create-*')))

    def test_same_release_reproducible_and_source_edits_allowed(self):
        one=self.new();two=self.new('beta',template='nextjs',template_version='1.0.0')
        for p in one.rglob('*'):
            if p.is_file() and p.name!='project.yaml':self.assertEqual(p.read_bytes(),(two/p.relative_to(one)).read_bytes())
        normalized=[]
        for root in [one,two]:
            manifest=json.loads((root/'.gptclaw/project.yaml').read_text())
            manifest['project']['id']='identity';manifest['project']['name']='Identity'
            manifest['service']['health']['path']='/projects/identity/api/health/'
            manifest['exposure']['base_path']='/projects/identity/'
            normalized.append(manifest)
        self.assertEqual(*normalized)
        (one/'app/page.tsx').write_text('edited source');app.target(one)
    def test_legacy_unchanged_and_malformed_provenance(self):
        root=self.new();path=root/'.gptclaw/template-release.json';path.unlink()
        before=(root/'.gptclaw/toolchain.json').read_bytes();app.target(root)
        self.assertFalse(path.exists());self.assertEqual(before,(root/'.gptclaw/toolchain.json').read_bytes())
        for value in [{'schema_version':True},{'schema_version':1,'id':'nextjs','version':'9.0.0','digest':'0'*64},templates.provenance(self.catalogue['releases'][0])|{'digest':'0'*64}]:
            path.write_text(json.dumps(value))
            with patch.object(app,'command') as run:
                with self.assertRaises(app.AppError):app.start(root)
                run.assert_not_called()
    def test_existing_and_racing_destination_never_overwritten(self):
        root=self.new();(root/'sentinel').write_text('keep')
        with self.assertRaises(app.AppError):self.new()
        self.assertEqual((root/'sentinel').read_text(),'keep')
        original=templates.publish
        def race(stage,dest):
            dest.mkdir();original(stage,dest)
        with patch.object(templates,'publish',side_effect=race):
            with self.assertRaises(app.AppError) as error:self.new('beta')
        self.assertTrue((self.projects/'beta').is_dir());self.assertEqual(list((self.projects/'beta').iterdir()),[])
        self.assertTrue(Path(error.exception.recovery_path).is_dir())
    def test_generation_failure_retains_only_owned_staging(self):
        with patch.object(app,'save',side_effect=app.AppError('invalid')):
            with self.assertRaises(app.AppError) as error:self.new()
        self.assertFalse((self.projects/'alpha').exists())
        stage=Path(error.exception.recovery_path);self.assertTrue(stage.name.startswith('.gptclaw-create-'))
        self.assertTrue((stage/'package.json').exists())
    def test_destination_lock_serializes_creation(self):
        import hashlib
        path=self.projects/'alpha';key='create-'+hashlib.sha256(str(path).encode()).hexdigest()
        with app.locked(key):
            with self.assertRaises(app.AppError) as error:self.new()
        self.assertEqual(error.exception.code,'busy');self.assertFalse(path.exists())
    def test_provider_bundle_inventory_contains_release_and_schema(self):
        paths=templates.bundle_paths()
        self.assertIn(Path('schemas/templates/v1.schema.json'),paths)
        self.assertIn(Path('templates/apps/releases/nextjs/1.0.0/.gitignore'),paths)
    def test_installed_snapshot_parity_and_default_rollback(self):
        bundle=app.provider_bundle()
        original=templates.discover()
        project=self.new()
        before={p.relative_to(project):p.read_bytes() for p in project.rglob('*') if p.is_file()}
        output=subprocess.run([sys.executable,str(bundle/'scripts/gptclawctl.py'),'templates','list'],check=True,capture_output=True,text=True)
        self.assertEqual(original,json.loads(output.stdout))
        env=os.environ.copy();env['PYTHONPATH']=str(bundle/'scripts')
        code="import private_apps as a, pathlib, json; a.PROJECTS=pathlib.Path(__import__('sys').argv[1]); a.STORE=a.PROJECTS/'.gptclaw-runtime/v1'; print(json.dumps(a.create('snapshot',template='nextjs',template_version='1.0.0')))"
        subprocess.run([sys.executable,'-B','-c',code,str(self.projects)],env=env,check=True,capture_output=True)
        self.assertEqual((project/'README.md').read_bytes(),(self.projects/'snapshot/README.md').read_bytes())
        # A later source default does not rewrite a previously installed snapshot.
        later=copy.deepcopy(self.catalogue['releases'][0]);later['version']='1.0.1';self.seal(later)
        source=self.repo/'templates/apps/releases/nextjs'
        shutil.copytree(source/'1.0.0',source/'1.0.1')
        self.catalogue['releases'].append(later)
        self.catalogue['default']={'id':'nextjs','version':'1.0.1'};self.write()
        new_bundle=app.provider_bundle()
        with patch.object(app,'REPO',new_bundle):
            app.target(project)
            newer=self.new('later')
        with patch.object(app,'REPO',bundle):
            with self.assertRaises(app.AppError):app.target(newer)
        output=subprocess.run([sys.executable,str(bundle/'scripts/gptclawctl.py'),'templates','list'],check=True,capture_output=True,text=True)
        self.assertEqual(original,json.loads(output.stdout))
        with patch.object(app,'REPO',bundle):app.target(project)
        self.assertEqual(before,{p.relative_to(project):p.read_bytes() for p in project.rglob('*') if p.is_file()})

    def test_ci_generator_keeps_creation_locks_in_fixture(self):
        base=self.base/'ci-projects'
        result=subprocess.run([sys.executable,str(self.repo/'scripts/tests/check_app_template.py'),str(base)],capture_output=True,text=True,check=True)
        self.assertEqual(result.stdout.strip(),str(base/'template-ci'))
        self.assertTrue(list((base/'.gptclaw-runtime/v1').glob('create-*.lock')))

    def test_historical_release_mutation_rejected(self):
        spec=importlib.util.spec_from_file_location('release_check',Path(__file__).resolve().parents[1]/'check-template-releases.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        def git(*args):subprocess.run(['git',*args],cwd=self.repo,check=True,capture_output=True)
        git('init');git('add','.');git('-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-m','baseline')
        module.verify_baseline('HEAD')
        self.catalogue['releases'][0]['description']='Changed old release';self.seal(self.catalogue['releases'][0]);self.write()
        with self.assertRaises(app.AppError):module.verify_baseline('HEAD')


if __name__=='__main__':unittest.main(verbosity=2)
