#!/usr/bin/env python3
"""Offline TypeScript API generation, compatibility and lifecycle contracts."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import private_apps as app
import project_dependencies as deps
import project_templates as templates
import project_toolchains as tools
import project_manifest as manifest


class Tests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(); self.addCleanup(temp.cleanup)
        self.base = Path(temp.name); self.projects = self.base/'projects'; self.projects.mkdir()
        for name, value in [('PROJECTS',self.projects),('STORE',self.base/'runtime'),('UNITS',self.base/'units')]:
            scope = patch.object(app,name,value); scope.start(); self.addCleanup(scope.stop)
        self.root = Path(app.create('typed-api',template='fastify',template_version='1.0.0')['root'])

    def test_exact_release_contract_and_dependency_policy(self):
        root, contract = app.target(self.root)
        self.assertEqual(contract['schema_version'],7)
        self.assertEqual(contract['project']['kind'],'api')
        self.assertEqual(contract['commands']['start'],['pnpm','dev'])
        self.assertEqual(contract['service']['health']['path'],'/projects/typed-api/ready')
        self.assertEqual(tools.selection(root)['declaration']['versions']['node'],'24.21.0')
        deps.context(root)
        with patch.object(app,'command') as command:
            templates.discover('fastify','1.0.0'); command.assert_not_called()
        self.assertEqual(templates.resolve()[0]['id'],'nextjs')

    def test_manifest_unknown_version_and_mismatched_provider_refused(self):
        path=self.root/'.gptclaw/project.yaml'; original=path.read_bytes()
        value=json.loads(original);value['schema_version']=8;app.save(path,value)
        self.assertNotEqual(manifest.validate_project(self.root)[2],0)
        path.write_bytes(original)
        app.save(self.root/'.gptclaw/template.json',{'provider':'fastapi-v1'})
        with patch.object(app,'command') as command:
            with self.assertRaises(app.AppError):app.start(self.root)
            command.assert_not_called()

    def test_safe_health_paths_and_ephemeral_data_only(self):
        path=self.root/'.gptclaw/project.yaml';value=json.loads(path.read_text())
        for change in [('service',{'internal_port':8000,'health':{'path':'/projects/../ready','timeout_seconds':5}}),('data',{'mode':'persistent'}),('exposure',{'private':False,'base_path':'/projects/typed-api/','funnel':True})]:
            candidate={**value,change[0]:change[1]};app.save(path,candidate)
            self.assertNotEqual(manifest.validate_project(self.root)[2],0)

    def test_runtime_unit_uses_node_guard_loopback_and_owned_identity(self):
        _, contract=app.target(self.root)
        with patch.object(app,'available',return_value=True):state=app.reserve(self.root,contract)
        text=app.unit_text(state,contract,'synthetic.ts.net')
        self.assertIn('PublishPort=127.0.0.1:',text)
        self.assertIn(':8000',text)
        self.assertIn('Environment=GPTCLAW_PROJECT_ID=typed-api',text)
        self.assertIn('pnpm_config_ignore_scripts=true',text)
        self.assertNotIn('UV_PYTHON',text)
        self.assertIn('"pnpm"',text)
        self.assertNotIn('adapter',state)

    def test_bundle_contains_new_contracts_and_retains_older_releases(self):
        paths=templates.bundle_paths()
        for name in ['scripts/project_fastify.py','schemas/project/v7.schema.json','config/templates/v6.json','schemas/templates/v6.schema.json','templates/apps/releases/fastify/1.0.0/src/app.ts']:
            self.assertIn(Path(name),paths)
        bundle=app.provider_bundle()
        for name in ['scripts/project_fastify.py','schemas/project/v7.schema.json','config/templates/v6.json']:
            self.assertEqual((bundle/name).read_bytes(),(app.REPO/name).read_bytes())
        for name,version in [('nextjs','1.0.0'),('fastapi','1.0.0'),('notes','1.0.0'),('notes-postgres','1.0.0'),('expo-react-native','1.0.1')]:
            templates.resolve(name,version)


if __name__ == '__main__': unittest.main()
