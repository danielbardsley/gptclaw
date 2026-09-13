#!/usr/bin/env python3
"""Offline authoring checks; never simulate or claim Codex instruction loading."""

import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock

from test_repository_agents import validate_policy

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / 'templates/agents/nested'
FIXTURE = ROOT / 'scripts/tests/fixtures/nested-agents'
AREAS = ('infrastructure', 'mobile', 'backend', 'migrations', 'ui')
SECTIONS = ('Scope and ownership', 'Local conventions', 'Commands and verification',
            'Constraints', 'Maintenance')
PLACEHOLDERS = {'AREA_NAME', 'AREA_SCOPE', 'PARENT_GUIDANCE', 'OWNER', 'AREA_PURPOSE',
                'LOCAL_CONVENTIONS', 'VERIFICATION', 'AREA_CONSTRAINTS', 'MAINTENANCE'}


def field(text, key):
    values = re.findall(rf'(?m)^{re.escape(key)}: (.+)$', text)
    if len(values) != 1 or not values[0].strip():
        raise ValueError(f'expected one nonempty {key}')
    return values[0]


def validate_area(path, root, *, template=False):
    size = validate_policy(path, root, template=template, max_bytes=4096,
                           sections=SECTIONS, placeholder_names=PLACEHOLDERS)
    text = re.sub(r'(?ms)^```[^\n]*\n.*?^```\s*$', '', path.read_text())
    version = field(text, 'Template-Version' if template else 'Source-Template-Version')
    if not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', version):
        raise ValueError('invalid version')
    field(text, 'Template-Source')
    field(text, 'Owner')
    scope = field(text, 'Area-Scope')
    parent = field(text, 'Parent-Guidance')
    if template:
        if scope != '{{AREA_SCOPE}}' or parent != '{{PARENT_GUIDANCE}}':
            raise ValueError('template scope/parent contract changed')
        return size
    # Canonical POSIX repo-relative directory, no dot segments or absolute paths.
    if not re.fullmatch(r'[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*', scope) or any(
            part in {'.', '..'} for part in scope.split('/')):
        raise ValueError('invalid area scope')
    root = root.resolve()
    area = path.parent.resolve()
    if area == root or root / scope != area:
        raise ValueError('area scope must match policy directory')
    parent_path = PurePosixPath(parent)
    if (parent_path.is_absolute() or '\\' in parent or
            parent_path.name not in {'AGENTS.md', 'AGENTS.override.md'}):
        raise ValueError('invalid parent guidance path')
    resolved = (area / parent).resolve()
    if (not resolved.is_relative_to(root) or resolved.parent not in area.parents
            or not resolved.is_file()):
        raise ValueError('parent guidance must be an existing ancestor policy')
    return size


def materialize_fixture(destination, *, scenario='baseline'):
    """Materialize a fixed inventory only into an empty caller-owned directory.

    No commands, settings, or paths are derived from policy contents.
    """
    destination = Path(destination)
    if scenario not in {'baseline', 'override', 'conflict'}:
        raise ValueError('unknown fixture scenario')
    if not destination.is_dir() or any(destination.iterdir()):
        raise ValueError('fixture destination must be an empty directory')
    shutil.copyfile(FIXTURE / 'AGENTS.md.fixture', destination / 'AGENTS.md')
    shutil.copyfile(FIXTURE / 'README.md', destination / 'README.md')
    for area in AREAS:
        folder = destination / area
        folder.mkdir()
        shutil.copyfile(SOURCES / 'examples' / f'{area}.example', folder / 'AGENTS.md')
    (destination / 'backend/archive').mkdir()
    shutil.copyfile(FIXTURE / 'deep.example', destination / 'backend/archive/AGENTS.md')
    if scenario == 'override':
        shutil.copyfile(FIXTURE / 'override.example', destination / 'ui/AGENTS.override.md')
    elif scenario == 'conflict':
        shutil.copyfile(FIXTURE / 'conflict.example', destination / 'backend/AGENTS.md')


class NestedAgentsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='gptclaw-agt003-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        materialize_fixture(self.root)
        self.policy = self.root / 'backend/AGENTS.md'
        self.original = self.policy.read_text()

    def invalid(self, text, message):
        self.policy.write_text(text)
        with self.assertRaisesRegex(ValueError, message):
            validate_area(self.policy, self.root)

    def test_shipped_template_adoption_and_examples(self):
        validate_area(SOURCES / 'AGENTS.md.template', ROOT, template=True)
        validate_area(ROOT / 'infra/dev-host/AGENTS.md', ROOT)
        for area in AREAS:
            validate_area(self.root / area / 'AGENTS.md', self.root)
        validate_area(self.root / 'backend/archive/AGENTS.md', self.root)

    def test_template_adaptation(self):
        text = (SOURCES / 'AGENTS.md.template').read_text().replace(
            '\nTemplate-Version:', '\nSource-Template-Version:')
        values = {'AREA_NAME': 'Backend', 'AREA_SCOPE': 'backend',
                  'PARENT_GUIDANCE': '../AGENTS.md', 'OWNER': 'Fixture owner',
                  'AREA_PURPOSE': 'Synthetic notes.', 'LOCAL_CONVENTIONS': 'Use record.',
                  'VERIFICATION': 'Review Markdown per [guide](../README.md).',
                  'AREA_CONSTRAINTS': 'Synthetic data only.',
                  'MAINTENANCE': 'Owner reviews updates per [guide](../README.md).'}
        for key, value in values.items():
            text = text.replace('{{' + key + '}}', value)
        self.policy.write_text(text)
        validate_area(self.policy, self.root)

    def test_required_sections_and_metadata(self):
        for section in SECTIONS:
            self.invalid(self.original.replace('## ' + section, '### ' + section), 'section')
            self.invalid(self.original + '\n## ' + section + '\nDuplicate\n', 'section')
        self.invalid(re.sub(r'(?s)(## Local conventions).*?(## Commands)',
                            r'\1\n\n\2', self.original), 'empty section')
        for key in ('Area-Scope', 'Parent-Guidance', 'Owner', 'Source-Template-Version',
                    'Template-Source'):
            for text in (re.sub(rf'(?m)^{key}:.*\n', '', self.original),
                         self.original + f'\n{key}: duplicate\n'):
                with self.subTest(key=key):
                    self.invalid(text, key if key in {'Area-Scope', 'Parent-Guidance', 'Owner'}
                                 else 'Version|version|source|Source')
        self.invalid(self.original.replace('1.0.0', 'latest'), 'Version')

    def test_scope_and_parent_boundaries(self):
        for scope in ('ui', '.', '..', '/backend', 'backend/../backend',
                      'backend//archive', 'backend/', 'missing', 'backend archive'):
            self.invalid(self.original.replace('Area-Scope: backend', f'Area-Scope: {scope}'),
                         'scope')
        for parent in ('AGENTS.md', '../ui/AGENTS.md', '../README.md',
                       '../../AGENTS.md', '/etc/AGENTS.md', '../missing/AGENTS.md'):
            self.invalid(self.original.replace('Parent-Guidance: ../AGENTS.md',
                                                f'Parent-Guidance: {parent}'), 'parent')
        # A real file outside the fixture still cannot be used as parent or link.
        with tempfile.TemporaryDirectory(prefix='gptclaw-agt003-outside-') as other:
            outside = Path(other) / 'AGENTS.md'
            outside.write_text('Synthetic outside content')
            (self.root / 'alias').symlink_to(Path(other), target_is_directory=True)
            self.invalid(self.original.replace('Parent-Guidance: ../AGENTS.md',
                                                'Parent-Guidance: ../alias/AGENTS.md'), 'parent')
            self.invalid(self.original + '\n[escape](../alias/AGENTS.md)', 'escapes')

    def test_links_and_placeholders(self):
        for target in ('missing.md', '../README.md?query=1', '/etc/passwd'):
            self.invalid(self.original + f'\n[bad]({target})', 'link|query|relative')
        for token in ('{{UNFILLED}}', '{{bad}}', '{{OPEN', 'STRAY}}'):
            self.invalid(self.original + token, 'placeholder')
        self.invalid(self.original + '\n[ref][id]\n[id]: ../README.md', 'inline')

    def test_encoding_and_byte_boundary(self):
        raw = self.original.encode()
        self.policy.write_bytes(raw + b' ' * (4096 - len(raw)))
        self.assertEqual(validate_area(self.policy, self.root), 4096)
        for value in (b'', raw + b' ' * (4097 - len(raw)), raw + b'\xff', raw + b'\x00',
                      b'\xef\xbb\xbf' + raw, raw + 'é'.encode() * 4096):
            self.policy.write_bytes(value)
            with self.assertRaises(ValueError):
                validate_area(self.policy, self.root)

    def test_validation_is_read_only_and_never_executes_or_fetches(self):
        self.policy.write_text(self.original + '\n`touch executed`\n'
                               '[external](https://example.invalid/policy)\n')
        files = [self.root / 'AGENTS.md', self.root / 'README.md', self.policy]
        before = {p: p.read_bytes() for p in files}
        real_open = Path.open
        def only_policy(path, *args, **kwargs):
            if path != self.policy:
                raise AssertionError('validator read a linked or unrelated file')
            return real_open(path, *args, **kwargs)
        with mock.patch('subprocess.run', side_effect=AssertionError('execution')), \
                mock.patch('os.system', side_effect=AssertionError('execution')), \
                mock.patch('socket.socket', side_effect=AssertionError('network')), \
                mock.patch.object(Path, 'open', only_policy):
            validate_area(self.policy, self.root)
        self.assertFalse((self.policy.parent / 'executed').exists())
        self.assertEqual(before, {p: p.read_bytes() for p in files})

    def test_scenario_inventory_is_inert_until_materialized(self):
        # Validate content and placement only: these are not agent behavior tests.
        for scenario, target in (('override', 'ui/AGENTS.override.md'),
                                 ('conflict', 'backend/AGENTS.md')):
            with tempfile.TemporaryDirectory(prefix='gptclaw-agt003-scenario-') as scratch:
                root = Path(scratch)
                materialize_fixture(root, scenario=scenario)
                validate_area(root / target, root)
                self.assertTrue((root / 'ui/AGENTS.md').is_file())
                if scenario == 'override':
                    self.assertIn('title case', (root / target).read_text())
                    self.assertIn('sentence case', (root / 'ui/AGENTS.md').read_text())
                else:
                    self.assertIn('must include its scope', (root / 'AGENTS.md').read_text())
                    self.assertIn('Do not include a scope', (root / target).read_text())
        with self.assertRaisesRegex(ValueError, 'empty'):
            materialize_fixture(self.root)
        self.assertEqual(self.policy.read_text(), self.original)
        for directory in (SOURCES, FIXTURE):
            self.assertFalse(list(directory.rglob('AGENTS.md')))
            self.assertFalse(list(directory.rglob('AGENTS.override.md')))

    def test_targeted_rollback_preserves_later_work(self):
        env = {'PATH': os.defpath, 'GIT_CONFIG_NOSYSTEM': '1',
               'GIT_CONFIG_GLOBAL': os.devnull, 'GIT_TERMINAL_PROMPT': '0'}
        def git(*args):
            return subprocess.run(
                ['git', '-c', 'user.name=Fixture', '-c', 'user.email=fixture@localhost',
                 '-c', 'commit.gpgsign=false', '-c', 'core.hooksPath=/dev/null', *args],
                cwd=self.root, env=env, check=True, capture_output=True, text=True).stdout.strip()
        git('init', '--quiet')
        git('add', 'AGENTS.md', 'README.md')
        git('commit', '-qm', 'Baseline')
        git('add', 'backend/AGENTS.md')
        git('commit', '-qm', 'Adopt area guidance')
        adoption = git('rev-parse', 'HEAD')
        self.policy.write_text(self.original.replace('Backend contract examples', 'Backend updated examples'))
        git('add', 'backend/AGENTS.md')
        git('commit', '-qm', 'Update area guidance')
        update = git('rev-parse', 'HEAD')
        readme = self.root / 'README.md'
        readme.write_text(readme.read_text() + '\nUnrelated later documentation.\n')
        git('add', 'README.md')
        git('commit', '-qm', 'Unrelated commit')
        # Preserve both a tracked dirty file and an untracked note.
        readme.write_text(readme.read_text() + 'Uncommitted tracked edit.\n')
        note = self.root / 'note.txt'
        note.write_text('Uncommitted note\n')
        expected = readme.read_bytes()
        git('revert', '--no-edit', update)
        self.assertEqual(self.policy.read_text(), self.original)
        validate_area(self.policy, self.root)
        git('revert', '--no-edit', adoption)
        self.assertFalse(self.policy.exists())
        self.assertEqual(readme.read_bytes(), expected)
        self.assertEqual(note.read_text(), 'Uncommitted note\n')
        self.assertTrue((self.root / 'AGENTS.md').is_file())


if __name__ == '__main__':
    unittest.main(verbosity=2)
