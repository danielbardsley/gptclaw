#!/usr/bin/env python3
"""Offline static generation, explicit contracts and build failure boundaries."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import private_apps as app
import project_templates as templates
import project_static as static
import project_dependencies as deps
import project_controls as controls
import project_manifest as manifest


class Tests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(); self.addCleanup(temp.cleanup)
        base = Path(temp.name); self.projects = base/'projects'; self.projects.mkdir()
        for name, value in [('PROJECTS',self.projects),('STORE',base/'runtime'),('UNITS',base/'units')]:
            scope = patch.object(app,name,value); scope.start(); self.addCleanup(scope.stop)
        self.root=Path(app.create('static-one',template='nextjs-static',template_version='1.0.0')['root'])
        _,self.contract=app.target(self.root)

    def test_generation_strict_contract_and_offline_discovery(self):
        self.assertEqual(self.contract,static.contract('static-one'))
        self.assertEqual(manifest.validate_project(self.root)[2],0)
        deps.context(self.root)
        with patch.object(app,'command') as command:
            self.assertEqual(templates.discover('nextjs-static','1.0.0')['schema_version'],8)
            command.assert_not_called()
        self.assertEqual(templates.resolve()[0]['id'],'nextjs')
        old=(self.root/'app/page.tsx').read_bytes()
        with self.assertRaises(app.AppError):app.create('static-one',template='nextjs-static',template_version='1.0.0')
        self.assertEqual((self.root/'app/page.tsx').read_bytes(),old)

    def test_mismatch_and_command_tampering_refused_before_execution(self):
        path=self.root/'.gptclaw/project.yaml';value=json.loads(path.read_text())
        for candidate in [dict(value,schema_version=100),dict(value,commands={**value['commands'],'start':['pnpm','dev']})]:
            app.save(path,candidate)
            with patch.object(app,'command') as command:
                with self.assertRaises(app.AppError):app.start(self.root)
                command.assert_not_called()
        app.save(path,value);app.save(self.root/'.gptclaw/template.json',{'provider':'nextjs-v1'})
        with self.assertRaises(app.AppError):app.target(self.root)

    def test_static_build_bypasses_dependency_only_cache(self):
        with patch.object(app,'available',return_value=True):s=app.reserve(self.root,self.contract)
        (self.root/'node_modules').mkdir()
        s.update(image='synthetic',prepared_digest='same',build_digest='same')
        with patch.object(app,'dependency_digest',return_value='same'), patch.object(app,'run_in_app') as run:
            app.prepare(s,self.contract,build=True)
        self.assertIn(unittest.mock.call(s,['pnpm','build']),run.call_args_list)
        # Existing API caching remains unaffected.
        api={**self.contract,'schema_version':7}
        with patch.object(app,'dependency_digest',return_value='same'), patch.object(app,'run_in_app') as run:
            app.prepare(s,api,build=True);run.assert_not_called()

    def test_rebuild_stops_before_build_and_failure_retains_failed_receipt(self):
        events=[]
        with patch.object(app,'available',return_value=True):state=app.reserve(self.root,self.contract)
        state['unit_sha256']='0'*64
        def stop(*args,**kwargs):events.append('stop')
        def prepare(*args,**kwargs):events.append('build');raise app.AppError('command')
        with patch.object(app,'stop',side_effect=stop),patch.object(app,'prepare',side_effect=prepare),patch.object(app,'toolchain',return_value='sha256:'+'1'*64),patch.object(app,'start') as start:
            with self.assertRaises(app.AppError):static.rebuild(self.root,self.contract,{'web':{'active':False}},lambda *args:None)
            start.assert_not_called()
        self.assertEqual(events,['stop','build'])
        receipt=app.state_for('static-one')
        self.assertEqual(receipt['phase'],'failed');self.assertFalse(receipt['health_ready'])

    def test_output_does_not_pollute_source_identity(self):
        before=controls.source_files(self.root)
        (self.root/'out').mkdir();(self.root/'out/index.html').write_text('derived')
        (self.root/'.static-build').mkdir();(self.root/'.static-build/partial').write_text('incomplete')
        self.assertEqual(before,controls.source_files(self.root))
        (self.root/'app/page.tsx').write_text('changed')
        self.assertNotEqual(before,controls.source_files(self.root))

    def test_inventory_and_private_app_projection(self):
        import dashboard_inventory as inventory
        import dashboard_observation as observation
        caps={'provider':'gptclawctl','project_manifest_schemas':[10],'runtime_manifest_schemas':[10]}
        scan=inventory.Scanner(self.projects,capabilities=caps).scan()
        self.assertTrue(scan['complete'])
        self.assertEqual(len(scan['rows']),1)
        row=scan['rows'][0]
        self.assertEqual(row['kind'],'web')
        self.assertEqual(row['runtime_support'],'supported')
        descriptor=observation.route_descriptor(self.root,self.contract,{'publication':{'state':'published'}})
        self.assertEqual(descriptor['app_path'],'/projects/static-one/')
        self.assertIsNone(descriptor['docs_path'])

    def test_bundle_includes_contract_and_release(self):
        paths=templates.bundle_paths()
        for name in ['scripts/project_static.py','schemas/project/v10.schema.json','config/templates/v8.json','schemas/templates/v8.schema.json','templates/apps/releases/nextjs-static/1.0.0/scripts/serve.mjs']:
            self.assertIn(Path(name),paths)
        bundle=app.provider_bundle()
        with patch.object(app,'REPO',bundle):
            release,contents=templates.resolve('nextjs-static','1.0.0')
            self.assertIn('scripts/serve.mjs',contents)
            self.assertEqual(release['manifest_schema'],10)


if __name__=='__main__':unittest.main()
