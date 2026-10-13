"""Synthetic inventory security/identity behavior; no live service operations."""
import copy
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import dashboard_inventory as inventory
import project_manifest as manifest
import project_groups as groups
import project_python as python
import project_templates as templates

CAPS = {'provider': 'gptclawctl', 'project_manifest_schemas': [1, 2, 3, 4]}


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='dashboard-inventory-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.projects = self.base / 'projects'
        self.projects.mkdir()
        self.registry = self.base / 'metadata.json'

    def project(self, name, version=1, slug=None):
        slug = slug or name
        root = self.projects / name
        (root / '.gptclaw').mkdir(parents=True)
        if version == 1:
            value = manifest.parse_manifest((ROOT/'examples/project-manifest/web.yaml').read_text())
            value['project'].update(id=slug, name=slug)
            value['exposure']['base_path'] = '/projects/'+slug+'/'
        elif version == 2:
            value = python.contract(slug)
        else:
            release, _ = templates.resolve('notes-postgres' if version == 4 else 'notes', '1.0.0')
            value = groups.contract(slug, release['toolchains'])
            for component in ('api', 'web'):
                (root/component).mkdir()
            if version == 4:
                value.update(schema_version=4, data={'mode': 'persistent'})
                value['components']['api']['depends_on'] = ['db']
                value['components']['db'] = {'adapter': 'postgres-v1', 'profile': 'postgres18-v1', 'depends_on': []}
                value['database'] = {'storage': 'runtime-volume-v1', 'head': '0001',
                    'migrate': ['.venv/bin/python','-m','fastapi_app.db_cli','migrate'],
                    'seed': ['.venv/bin/python','-m','fastapi_app.db_cli','seed']}
        (root/'.gptclaw/project.yaml').write_text(json.dumps(value))
        return root

    def scan(self, **kwargs):
        return inventory.Scanner(self.projects, capabilities=CAPS, **kwargs).scan()

    def metadata(self, rows):
        self.registry.write_text(json.dumps({'schema_version': 1, 'projects': rows}))
        self.registry.chmod(0o600)

    def test_four_schemas_group_once_stopped_independent_of_runtime(self):
        roots = [self.project('d-db', 4), self.project('c-group', 3), self.project('b-api', 2), self.project('a-web')]
        for root in roots:
            self.assertEqual(manifest.validate_project(root)[2], 0)
        (self.projects/'ordinary').mkdir()
        (self.projects/'.hidden').mkdir()
        with (patch.object(subprocess, 'Popen', side_effect=AssertionError('execution')),
              patch.object(socket, 'create_connection', side_effect=AssertionError('network'))):
            result = self.scan()
        self.assertTrue(result['complete'], result)
        self.assertEqual([r['id'] for r in result['rows']], ['a-web','b-api','c-group','d-db'])
        self.assertEqual(result['rows'][-1]['components'], ['api','db','web'])
        self.assertNotIn('commands', json.dumps(result))

    def test_metadata_presence_and_missing_are_honest(self):
        root = self.project('web')
        (root/'README.md').write_text('Do not read this prose')
        (root/'docs').mkdir()
        (root/'docs/README.md').symlink_to(root/'README.md')
        self.metadata([{'root': str(root), 'id': 'web', 'owner': 'Project owner',
                       'repository': 'https://github.com/example/project', 'ignored': 'synthetic-secret'}])
        result = self.scan(registry=self.registry)
        row = result['rows'][0]
        self.assertEqual(row['owner'], 'Project owner')
        self.assertEqual(row['documentation'], {'readme': 'present', 'index': 'unavailable'})
        self.assertNotIn('synthetic-secret', json.dumps(result))
        self.assertEqual(self.scan()['rows'][0]['owner'], None)

    def test_invalid_registry_does_not_replace_identity(self):
        root = self.project('web')
        self.metadata([{'root': str(root), 'id': 'web', 'repository': 'https://token@github.com/a/b'}])
        result = self.scan(registry=self.registry)
        self.assertEqual(result['rows'][0]['id'], 'web')
        self.assertIsNone(result['rows'][0]['repository'])
        self.assertEqual(result['metadata_state'], 'invalid')
        self.assertNotIn('token', json.dumps(result))

    def test_duplicate_ids_cannot_select_target(self):
        self.project('one', slug='same')
        self.project('two', slug='same')
        scanner = inventory.Scanner(self.projects, capabilities=CAPS)
        rows = scanner.scan()['rows']
        self.assertEqual(len({row['key'] for row in rows}), 2)
        self.assertTrue(all(row['identity_state'] == 'conflict' for row in rows))
        self.assertEqual(scanner.bindings, {})

    def test_unavailable_and_unsupported_provider_not_health(self):
        self.project('web')
        scanner = inventory.Scanner(self.projects)
        self.assertEqual(scanner.scan()['rows'][0]['runtime_support'], 'unavailable')
        scanner.capabilities = {'provider': 'gptclawctl', 'project_manifest_schemas': [2]}
        self.assertEqual(scanner.scan()['rows'][0]['runtime_support'], 'unsupported')
        self.assertNotIn('health', scanner.scan()['rows'][0])

    def test_symlink_fifo_hardlink_and_malformed_secret_are_refused(self):
        good = self.project('good')
        (self.projects/'link').symlink_to(good, target_is_directory=True)
        for name in ('fifo','hard','bad','large','unreadable','meta-link'):
            root = self.project(name)
            file = root/'.gptclaw/project.yaml'
            if name == 'fifo':
                file.unlink(); os.mkfifo(file)
            elif name == 'hard':
                file.unlink(); original = self.base/'hard-original'; original.write_text('{}'); os.link(original, file)
            elif name == 'bad':
                file.write_text('SECRET-SYNTHETIC: !!python/object:bad\n')
            elif name == 'large':
                file.write_text('s' * 65537)
            elif name == 'unreadable':
                file.chmod(0)
            else:
                shutil.rmtree(root/'.gptclaw'); (root/'.gptclaw').symlink_to(good/'.gptclaw')
        result = self.scan()
        self.assertEqual([r['id'] for r in result['rows']], ['good'])
        self.assertFalse(result['complete'])
        self.assertNotIn('SECRET-SYNTHETIC', json.dumps(result))
        self.assertLess(len(result['diagnostics']), 10)

    def test_root_symlink_and_root_missing_are_global_unavailable(self):
        link = self.base/'linked'; link.symlink_to(self.projects)
        for root in (link, self.base/'absent'):
            result = inventory.Scanner(root).scan()
            self.assertEqual(result['freshness'], 'unavailable')
            self.assertNotEqual(result['freshness'], 'current')

    def test_directory_replacement_during_validation_is_refused(self):
        root = self.project('web')
        actual = inventory.validate_project
        def replace(path, **kwargs):
            root.rename(self.projects/'retired')
            self.project('web', slug='other')
            return actual(path, **kwargs)
        with patch.object(inventory, 'validate_project', side_effect=replace):
            result = self.scan()
        self.assertEqual(result['rows'], [])
        self.assertIn({'code': 'path-changed'}, result['diagnostics'])

    def test_pinned_manifest_and_group_checks_do_not_follow_replacement(self):
        root = self.project('group', 3)
        fd = inventory.open_directory(root)
        self.addCleanup(os.close, fd)
        root.rename(self.projects/'retired')
        replacement = self.project('group', slug='other')
        result, value, code = manifest.validate_project(replacement, directory_fd=fd)
        self.assertEqual(code, 0, result)
        self.assertEqual(value['project']['id'], 'group')

    def test_empty_scan_and_limits_are_distinct_from_unavailable(self):
        result = self.scan()
        self.assertTrue(result['complete'])
        self.assertEqual(result['rows'], [])
        for name in ('a','b','c'):
            self.project(name)
        result = self.scan(max_candidates=2)
        self.assertTrue(result['truncated'])
        self.assertFalse(result['complete'])
        self.assertEqual(len(result['rows']), 2)
        result = self.scan(max_entries=1)
        self.assertTrue(result['truncated'])
        result = self.scan(max_output=700)
        self.assertTrue(result['truncated'])
        self.assertLessEqual(len(json.dumps(result).encode()), 700)

    def test_deadline_and_diagnostic_count_are_bounded(self):
        self.project('a')
        ticks = iter([0, 20])
        result = self.scan(monotonic=lambda: next(ticks, 20))
        self.assertTrue(result['truncated'])
        for index in range(70):
            (self.projects/f'link{index}').symlink_to(self.projects/'a')
        result = self.scan()
        self.assertEqual(len(result['diagnostics']), 50)
        self.assertTrue(result['truncated'])

    def test_registry_bounds_duplicates_and_stale_binding(self):
        root = self.project('web')
        self.metadata([{'root': str(root), 'id': 'other', 'owner': 'Wrong owner'}])
        self.assertIsNone(self.scan(registry=self.registry)['rows'][0]['owner'])
        self.registry.write_text('{"schema_version":1,"schema_version":1,"projects":[]}')
        self.assertEqual(self.scan(registry=self.registry)['metadata_state'], 'invalid')
        self.registry.write_text('s'*(inventory.MAX_REGISTRY+1))
        self.assertEqual(self.scan(registry=self.registry)['metadata_state'], 'invalid')
        self.registry.unlink(); self.registry.symlink_to(root/'.gptclaw/project.yaml')
        self.assertEqual(self.scan(registry=self.registry)['metadata_state'], 'invalid')


if __name__ == '__main__':
    unittest.main()
