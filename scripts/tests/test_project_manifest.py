"""Behavioral contract tests with disposable synthetic projects; no service starts."""
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
import project_manifest as manifest

EXAMPLE = (ROOT / 'examples/project-manifest/web.yaml').read_text()
VALID = manifest.parse_manifest(EXAMPLE)
CLI = ROOT / 'scripts/validate-project-manifest.py'


class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='gptclaw-manifest-test-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / '.gptclaw').mkdir()
        self.file = self.root / '.gptclaw/project.yaml'
        self.file.write_text(EXAMPLE)

    def validate(self, data=None):
        if data is not None:
            self.file.write_text(json.dumps(data))
        return manifest.validate_project(self.root)

    def invalid(self, data=None, code=None, path=None):
        result, contract, status = self.validate(data)
        self.assertEqual(status, 1, result)
        self.assertFalse(result['valid'])
        self.assertIsNone(contract)
        self.assertIsNone(result['project_id'])
        self.assertIsNone(result['schema_version'])
        if code:
            self.assertIn(code, [e['code'] for e in result['errors']], result)
        if path is not None:
            self.assertIn(path, [e['path'] for e in result['errors']], result)
        return result

    def change(self, path, value):
        data = copy.deepcopy(VALID)
        target = data
        for part in path[:-1]:
            target = target[part]
        target[path[-1]] = value
        return data

    def cli(self, *args, python=None):
        return subprocess.run([python or sys.executable, '-B', str(CLI), *args],
                              capture_output=True, text=True, timeout=10)

    def test_example_and_copy_break_fix_workflow(self):
        shutil.copyfile(ROOT / 'examples/project-manifest/web.yaml', self.file)
        good = self.cli('--project-root', str(self.root), '--json')
        self.assertEqual(good.returncode, 0, good.stderr)
        self.assertEqual(json.loads(good.stdout)['project_id'], 'example-web')
        self.file.write_text(EXAMPLE.replace('timeout_seconds: 5', 'timeout_seconds: 0'))
        bad = self.cli('--project-root', str(self.root), '--json')
        self.assertEqual(bad.returncode, 1)
        self.assertEqual(json.loads(bad.stdout)['errors'][0]['path'], '/service/health/timeout_seconds')
        self.file.write_text(EXAMPLE)
        fixed = self.cli('--project-root', str(self.root))
        self.assertEqual(fixed.returncode, 0)
        self.assertEqual(fixed.stdout, 'Valid manifest: example-web (schema 1).\n')
        self.assertEqual(fixed.stderr, '')

    def test_boundaries(self):
        for port in (1024, 65535):
            for timeout in (1, 60):
                data = copy.deepcopy(VALID)
                data['service']['internal_port'] = port
                data['service']['health']['timeout_seconds'] = timeout
                data['project']['id'] = 'a' * 48
                data['project']['name'] = 'x' * 100
                data['exposure']['base_path'] = '/projects/' + 'a' * 48 + '/'
                data['commands']['build'] = ['x' * 4096] + [''] * 63
                self.assertEqual(self.validate(data)[2], 0)

    def test_versions(self):
        for value in [0, 2, -1, True, False, 1.0, '1', None, {}, []]:
            with self.subTest(value=value):
                self.invalid(self.change(['schema_version'], value), 'version', '/schema_version')
        data = copy.deepcopy(VALID)
        del data['schema_version']
        self.invalid(data, 'version')

    def test_required_fields(self):
        def objects(value, path=()):
            if isinstance(value, dict):
                yield path, value
                for key, item in value.items():
                    yield from objects(item, path + (key,))
        for path, obj in objects(VALID):
            for key in obj:
                if key == 'schema_version':
                    continue
                data = copy.deepcopy(VALID)
                target = data
                for part in path:
                    target = target[part]
                del target[key]
                with self.subTest(path=path, key=key):
                    self.invalid(data, 'field_required', '/' + '/'.join(path + (key,)))

    def test_unknown_fields_at_every_object_level_do_not_leak_keys(self):
        for path in [[], ['project'], ['commands'], ['service'], ['service', 'health'], ['exposure'], ['data']]:
            with self.subTest(path=path):
                data = self.change(path + ['SYNTHETIC_SECRET_KEY'], 'SYNTHETIC_SECRET_VALUE')
                result = self.invalid(data, 'field_unknown', ''.join('/' + p for p in path))
                self.assertNotIn('SYNTHETIC_SECRET', json.dumps(result))

    def test_invalid_fields(self):
        cases = [
            (['project','id'], ['', '1a', 'A', '-a', 'a-', 'a--b', 'a/b', '../a', 'a\n', 'a' * 49]),
            (['project','name'], ['', ' ', '\t', 'x\n', 'x\x7f', 'x\u0085', 'x\u2028', 'x'*101]),
            (['project','kind'], ['api', True, None]),
            (['service','internal_port'], [1023, 65536, True, 3000.0, '3000', None]),
            (['service','health','timeout_seconds'], [0, 61, True, 5.0, '5']),
            (['commands','start'], ['', [], [''], ['x']*65, ['x'*4097], ['x', 4], ['x','a\n'], ['x','\u009f']]),
            (['exposure','private'], [False, 'true', 1]),
            (['exposure','funnel'], [True, 'false', 0]),
            (['data','mode'], ['persistent', None]),
        ]
        for path, values in cases:
            for value in values:
                with self.subTest(path=path,value=value):
                    self.invalid(self.change(path,value))

    def test_health_paths(self):
        for path in ['/', '/health', '/health/', '/a-b_c.d/ok', '/' + 'a'*255]:
            self.assertEqual(self.validate(self.change(['service','health','path'], path))[2], 0, path)
        for path in ['', 'health', '//x', '/a//b', '/.', '/..', '/a/../b', '/a/./', '/a?b', '/a#b',
                     '/%2e', '/a b', '/a\\b', 'https://x', '/x\n', '/'+'a'*256]:
            with self.subTest(path=path):
                self.invalid(self.change(['service','health','path'], path), 'field_value')

    def test_base_path_matches_project(self):
        for path in ['/projects/other/', '/projects/example-web', '/', 'https://x', '/projects/example-web/\n']:
            self.invalid(self.change(['exposure','base_path'], path), 'field_value', '/exposure/base_path')

    def test_unsupported_capabilities(self):
        for path, value in [(['environment'], {'X':'x'}), (['secrets'], {}), (['include'], '/tmp/file'),
                            (['service','host_port'], 3000), (['service','bind'], '0.0.0.0'),
                            (['data','volumes'], []), (['exposure','url'], 'https://x'),
                            (['state'], {'pid':1}), (['commands','install'], ['x'])]:
            self.invalid(self.change(path,value), 'field_unknown')

    def test_yaml_restrictions(self):
        cases = [('', 'document'), ('---\n---\n{}', 'document'), ('[]', 'document'),
                 ('schema_version: [', 'parse'), ('schema_version: 1\nschema_version: 1', 'mapping_key'),
                 ('project:\n  id: a\n  id: b', 'mapping_key'), ('{1: x}', 'mapping_key'),
                 ('{true: x}', 'mapping_key'), ('{[a]: x}', 'mapping_key'),
                 ('x: &a hi', 'yaml_feature'), ('x: *a', 'yaml_feature'),
                 ('x: !thing hi', 'yaml_feature'), ('x: !!str hi', 'yaml_feature'),
                 ('x: {<<: {a: b}}', 'yaml_feature'), ('x: 1e999', 'parse')]
        for text, code in cases:
            with self.subTest(text=text):
                self.file.write_text(text)
                self.invalid(code=code)

    def test_no_yaml_11_coercion(self):
        self.assertEqual(manifest.parse_manifest('x: yes\ny: 2026-09-30\nz: 012\nw: .nan'),
                         {'x':'yes', 'y':'2026-09-30', 'z':'012', 'w':'.nan'})
        self.file.write_text(EXAMPLE.replace('private: true', 'private: yes'))
        self.invalid(code='field_type')

    def test_limits_before_construction(self):
        self.file.write_bytes(b'#' * (manifest.MAX_BYTES + 1))
        self.invalid(code='input_size')
        self.file.write_text('x: ' + '['*17 + '0' + ']'*17)
        with patch.object(manifest.JsonLoader, 'get_single_node', side_effect=AssertionError('must not construct')):
            self.invalid(code='input_depth')
        padding = manifest.MAX_BYTES - len(EXAMPLE.encode())
        self.file.write_text(EXAMPLE + '#' * padding)
        self.assertEqual(self.validate()[2], 0)

    def test_utf8_failure_is_sanitized(self):
        self.file.write_bytes(b'\xffSYNTHETIC_SECRET')
        result = self.invalid(code='parse')
        self.assertNotIn('SYNTHETIC_SECRET', json.dumps(result))

    def test_missing_file_and_parent(self):
        self.file.unlink()
        self.invalid(code='input_missing')
        (self.root / '.gptclaw').rmdir()
        self.invalid(code='input_missing')

    @unittest.skipIf(os.geteuid() == 0, 'real unreadable-file check needs an unprivileged user')
    def test_unreadable_file_and_parent(self):
        self.file.chmod(0)
        try:
            self.invalid(code='input_unreadable')
            self.assertEqual(self.file.stat().st_mode & 0o777, 0)
        finally:
            self.file.chmod(0o600)
        self.file.parent.chmod(0)
        try:
            self.invalid(code='input_unreadable')
        finally:
            self.file.parent.chmod(0o700)

    def test_symlink_file_directory_root_and_ancestor(self):
        actual = self.root / 'actual.yaml'
        self.file.rename(actual)
        self.file.symlink_to(actual)
        self.invalid(code='input_path')
        self.file.unlink()
        actual.rename(self.file)
        moved = self.root / 'actual-directory'
        self.file.parent.rename(moved)
        self.file.parent.symlink_to(moved, target_is_directory=True)
        self.invalid(code='input_path')
        self.file.parent.unlink()
        moved.rename(self.file.parent)
        link = self.root / 'linked-root'
        link.symlink_to(self.root, target_is_directory=True)
        self.assertEqual(manifest.validate_project(link)[0]['errors'][0]['code'], 'input_path')
        child = self.root / 'child'
        child.mkdir()
        self.assertEqual(manifest.validate_project(link / 'child')[0]['errors'][0]['code'], 'input_path')
        self.assertEqual(manifest.validate_project(link / '..')[0]['errors'][0]['code'], 'input_path')

    def test_nonregular_file_does_not_block(self):
        self.file.unlink()
        os.mkfifo(self.file)
        result = self.cli('--project-root', str(self.root), '--json')
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)['errors'][0]['code'], 'input_kind')
        self.file.unlink()
        self.file.mkdir()
        self.invalid(code='input_kind')

    def test_file_swap_at_open_never_follows_symlink(self):
        actual_open = os.open
        external = self.root / 'external'
        external.write_text(EXAMPLE)
        def replace_at_open(path, flags, **kwargs):
            if path == 'project.yaml':
                self.file.unlink()
                self.file.symlink_to(external)
            return actual_open(path, flags, **kwargs)
        with patch.object(manifest.os, 'open', side_effect=replace_at_open):
            self.invalid(code='input_path')

    def test_no_commands_expansion_network_or_project_writes(self):
        sentinel = self.root / 'EXECUTED'
        script = self.root / 'do-not-run'
        script.write_text('#!/bin/sh\ntouch "' + str(sentinel) + '"\n')
        script.chmod(0o700)
        data = copy.deepcopy(VALID)
        data['commands']['start'] = [str(script), '$MANIFEST_SENTINEL', '$(touch EXECUTED)', ';']
        self.file.write_text(json.dumps(data))
        (self.root / 'sitecustomize.py').write_text('raise RuntimeError("PROJECT_IMPORT")')
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        with patch.dict(os.environ, {'MANIFEST_SENTINEL':'SYNTHETIC_SECRET'}), \
             patch.object(socket, 'socket', side_effect=AssertionError('network disabled')), \
             patch.object(socket, 'create_connection', side_effect=AssertionError('network disabled')), \
             patch.object(subprocess, 'Popen', side_effect=AssertionError('execution disabled')), \
             patch.object(os, 'system', side_effect=AssertionError('execution disabled')):
            result, contract, status = self.validate()
        self.assertEqual(status, 0, result)
        self.assertEqual(contract['commands']['start'], data['commands']['start'])
        self.assertNotIn('SYNTHETIC_SECRET', json.dumps(result))
        self.assertFalse(sentinel.exists())
        after = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before, after)

    def test_errors_are_deterministic_bounded_and_redacted(self):
        data = copy.deepcopy(VALID)
        data['commands']['build'] = ['SYNTHETIC_SECRET\n'] * 64
        self.file.write_text(json.dumps(data))
        first = self.invalid()
        self.assertEqual(first, self.invalid())
        self.assertEqual(len(first['errors']), 50)
        self.assertTrue(first['truncated'])
        self.assertNotIn('SYNTHETIC_SECRET', json.dumps(first))
        self.file.write_text('SYNTHETIC_SECRET: [')
        result = self.cli('--project-root', str(self.root))
        self.assertEqual(result.returncode, 1)
        self.assertNotIn('SYNTHETIC_SECRET', result.stderr)
        self.assertNotIn('Traceback', result.stderr)

    def test_json_and_human_errors_agree(self):
        self.validate(self.change(['service','internal_port'], True))
        human = self.cli('--project-root', str(self.root))
        machine = self.cli('--project-root', str(self.root), '--json')
        self.assertEqual(human.returncode, machine.returncode)
        self.assertFalse(human.stdout)
        self.assertFalse(machine.stderr)
        for error in json.loads(machine.stdout)['errors']:
            self.assertIn(error['code'], human.stderr)
            self.assertIn(error['path'], human.stderr)

    def test_usage_does_not_echo_arguments(self):
        for args in [[], ['--bad', 'SYNTHETIC_SECRET'], ['--project-root'], ['--project-r', str(self.root)]]:
            result = self.cli(*args, '--json')
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stdout)['errors'][0]['code'], 'usage')
            self.assertNotIn('SYNTHETIC_SECRET', result.stdout + result.stderr)

    def test_missing_dependencies(self):
        result = subprocess.run([sys.executable, '-S', '-B', str(CLI), '--project-root', str(self.root), '--json'],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)['errors'][0]['code'], 'setup')
        self.assertFalse(result.stderr)

    def test_schema_failure_and_remote_refs_fail_without_network(self):
        for content in ['{', '{}', '{"$id":"urn:gptclaw:project:v1","type":"object","$ref":"https://example.invalid/SYNTHETIC_SECRET"}']:
            schema = self.root / 'schema.json'
            schema.write_text(content)
            with patch.object(manifest, 'SCHEMA_PATH', schema), \
                 patch.object(socket, 'socket', side_effect=AssertionError('network disabled')):
                result, contract, status = self.validate()
            self.assertEqual(status, 2)
            self.assertIsNone(contract)
            self.assertEqual(result['errors'][0]['code'], 'setup')
            self.assertNotIn('SYNTHETIC_SECRET', json.dumps(result))
        with patch.object(manifest, 'SCHEMA_PATH', self.root / 'missing.json'):
            self.assertEqual(self.validate()[2], 2)

    def test_setup_preserves_existing_destination(self):
        marker = self.root / 'preserve-me'
        marker.write_text('synthetic existing environment data')
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/setup-project-manifest.py'),
                                 '--venv', str(self.root)], capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(marker.read_text(), 'synthetic existing environment data')
        self.assertFalse((self.root / 'pyvenv.cfg').exists())

    def test_cli_from_project_directory_does_not_import_project_modules(self):
        marker = self.root / 'IMPORTED'
        for name in ['yaml.py', 'jsonschema.py', 'project_manifest.py']:
            (self.root / name).write_text('from pathlib import Path; Path(' + repr(str(marker)) + ').touch()')
        env = dict(os.environ)
        env.pop('PYTHONPATH', None)
        result = subprocess.run([sys.executable, '-B', str(CLI), '--project-root', '.', '--json'],
                                cwd=self.root, env=env, capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(marker.exists())

    def test_internal_failure_is_sanitized(self):
        with patch.object(manifest, 'read_manifest', side_effect=RuntimeError('SYNTHETIC_SECRET')):
            result, contract, status = self.validate()
        self.assertEqual(status, 2)
        self.assertEqual(result['errors'][0]['code'], 'internal')
        self.assertNotIn('SYNTHETIC_SECRET', json.dumps(result))
        self.assertIsNone(contract)


if __name__ == '__main__':
    unittest.main()
