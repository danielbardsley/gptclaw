"""Synthetic bootstrap tests: no network, credentials, or host changes."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('bootstrap', ROOT / 'scripts/bootstrap-project.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)


class BootstrapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = tempfile.TemporaryDirectory(prefix='gptclaw-bootstrap-source-')
        cls.source_base = Path(cls.fixture.name) / 'source'
        cls.source_base.mkdir()
        for prefix in [b.STARTER, b.SKILL]:
            shutil.copytree(ROOT / prefix, cls.source_base / prefix)
        (cls.source_base / '.codex').mkdir()
        (cls.source_base / '.codex/auth.json').write_text('synthetic excluded sentinel')
        b.git(cls.source_base, 'init', '--quiet', '--initial-branch=main', '--template=')
        b.git(cls.source_base, 'add', '.')
        b.git(cls.source_base, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
              'commit', '--quiet', '-m', 'synthetic source')
        cls.revision = b.git(cls.source_base, 'rev-parse', 'HEAD').stdout.decode().strip()

    @classmethod
    def tearDownClass(cls):
        cls.fixture.cleanup()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='gptclaw-bootstrap-test-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / 'source'
        shutil.copytree(self.source_base, self.source)
        self.dest = self.root / 'sample-project'

    def create(self, destination=None, **kwargs):
        with contextlib.redirect_stdout(io.StringIO()):
            return b.create(self.source, self.revision, destination or self.dest,
                            kwargs.pop('name', 'Sample Project'), kwargs.pop('purpose', 'Plan a small local tool.'),
                            kwargs.pop('owner', 'Fixture Owner'), **kwargs)

    def snapshot(self, path):
        return {str(p.relative_to(path)): (p.lstat().st_ino, p.read_bytes())
                for p in path.rglob('*') if p.is_file() and not p.is_symlink()}

    def test_new_project_is_complete_and_local(self):
        self.assertEqual(self.create()['status'], 'created')
        self.assertFalse((self.dest / b.MARKER).exists())
        self.assertFalse((self.dest / '.codex').exists())
        self.assertFalse((self.dest / '.agents/skills/gptclaw-project-bootstrap').exists())
        record = json.loads((self.dest / b.PROVENANCE).read_text())
        self.assertEqual(record['source_revision'], self.revision)
        for name, hash_value in record['files'].items():
            self.assertEqual(b.digest((self.dest / name).read_bytes()), hash_value)
        for name in b.SKILL_FILES:
            self.assertEqual((self.dest / b.SKILL / name).read_bytes(), (self.source / b.SKILL / name).read_bytes())
        self.assertIn('Fixture Owner', (self.dest / 'AGENTS.md').read_text())
        self.assertNotIn('{{', (self.dest / 'AGENTS.md').read_text())
        self.assertFalse(b.git(self.dest, 'remote').stdout)
        self.assertFalse(b.git(self.dest, 'ls-files').stdout)
        self.assertNotEqual(b.git(self.dest, 'rev-parse', '--verify', 'HEAD', check=False).returncode, 0)
        self.assertEqual(b.git(self.dest, 'symbolic-ref', 'HEAD').stdout.strip(), b'refs/heads/main')
        self.assertFalse(list(self.root.glob('.gptclaw-staging-*')))

    def test_existing_empty_directory_identity_preserved(self):
        self.dest.mkdir(mode=0o750)
        before = self.dest.stat()
        self.create()
        self.assertEqual(b.identity(before), b.identity(self.dest.stat()))
        self.assertEqual(before.st_mode, self.dest.stat().st_mode)

    def test_preview_no_writes(self):
        before = set(self.root.iterdir())
        self.assertEqual(self.create(check_only=True)['status'], 'ready')
        self.assertEqual(before, set(self.root.iterdir()))

    def test_retry_unchanged_is_read_only(self):
        self.create()
        before = self.snapshot(self.dest)
        self.assertEqual(self.create()['status'], 'already-created')
        self.assertEqual(before, self.snapshot(self.dest))

    def test_modified_output_preserved(self):
        self.create()
        (self.dest / 'README.md').write_text('owner work')
        before = self.snapshot(self.dest)
        with self.assertRaises(b.BootstrapError):
            self.create()
        self.assertEqual(before, self.snapshot(self.dest))

    def test_changed_inputs_refused(self):
        self.create()
        before = self.snapshot(self.dest)
        with self.assertRaises(b.BootstrapError):
            self.create(owner='Another Owner')
        self.assertEqual(before, self.snapshot(self.dest))

    def test_added_files_and_directories_refused(self):
        self.create()
        (self.dest / 'owner-work').mkdir()
        with self.assertRaises(b.BootstrapError):
            self.create()
        self.assertTrue((self.dest / 'owner-work').exists())

    def test_occupied_destination_preserved(self):
        self.dest.mkdir()
        (self.dest / 'keep.txt').write_text('owner work')
        before = self.snapshot(self.dest)
        with self.assertRaises(b.BootstrapError):
            self.create()
        self.assertEqual(before, self.snapshot(self.dest))

    def test_destination_file_refused(self):
        self.dest.write_text('keep')
        with self.assertRaises(b.BootstrapError):
            self.create()
        self.assertEqual(self.dest.read_text(), 'keep')

    def test_symlink_destination_and_parent_refused(self):
        real = self.root / 'real'
        real.mkdir()
        self.dest.symlink_to(real, target_is_directory=True)
        for path in [self.dest, self.dest / 'child']:
            with self.assertRaises(b.BootstrapError):
                self.create(path)
        self.assertEqual(list(real.iterdir()), [])

    def test_path_traversal_and_unsafe_slugs_refused(self):
        for value in [str(self.root / '../escape'), str(self.root / 'Bad Name'), str(self.root / '-bad'), str(self.root / 'a--b')]:
            with self.subTest(value=value), self.assertRaises(b.BootstrapError):
                self.create(value)
        self.assertFalse(self.dest.exists())

    def test_nested_repository_refused(self):
        parent = self.root / 'parent'
        parent.mkdir()
        b.git(parent, 'init', '--quiet', '--template=')
        with self.assertRaises(b.BootstrapError):
            self.create(parent / 'child')
        self.assertFalse((parent / 'child').exists())

    def test_invalid_revision_metadata_and_missing_parent(self):
        with self.assertRaises(b.BootstrapError):
            b.load_payload(self.source, 'main', b.metadata('Name', 'Purpose', 'Owner'))
        for value in ['bad\ntext', '{{UNKNOWN}}', '', 'x\x00y']:
            with self.subTest(value=value), self.assertRaises(b.BootstrapError):
                self.create(purpose=value)
        with self.assertRaises(b.BootstrapError):
            self.create(self.root / 'missing/child')
        self.assertFalse(self.dest.exists())

    def test_metadata_markdown_is_literal(self):
        self.create(name='A [link](file) | `tool`')
        self.assertIn(r'A \[link\]\(file\) \| \`tool\`', (self.dest / 'README.md').read_text())

    def test_dirty_source_ignored(self):
        (self.source / b.SKILL / 'SKILL.md').write_text('unreviewed dirt')
        self.create()
        self.assertNotIn('unreviewed dirt', (self.dest / b.SKILL / 'SKILL.md').read_text())

    def test_source_missing_or_extra_skill_asset_refused(self):
        (self.source / b.SKILL / 'extra.md').write_text('not allowlisted')
        b.git(self.source, 'add', '.')
        b.git(self.source, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
              'commit', '--quiet', '-m', 'extra')
        revision = b.git(self.source, 'rev-parse', 'HEAD').stdout.decode().strip()
        with self.assertRaises(b.BootstrapError):
            b.load_payload(self.source, revision, b.metadata('Name', 'Purpose', 'Owner'))

    def test_source_symlink_refused(self):
        target = self.source / b.SKILL / 'assets/spec.md'
        target.unlink()
        target.symlink_to('/nonexistent-synthetic')
        b.git(self.source, 'add', '.')
        b.git(self.source, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
              'commit', '--quiet', '-m', 'symlink')
        revision = b.git(self.source, 'rev-parse', 'HEAD').stdout.decode().strip()
        with self.assertRaises(b.BootstrapError):
            b.load_payload(self.source, revision, b.metadata('Name', 'Purpose', 'Owner'))

    def test_destination_created_during_staging_preserved(self):
        original_git = b.git
        def racing_git(root, *args, **kwargs):
            result = original_git(root, *args, **kwargs)
            if args[0] == 'init':
                self.dest.mkdir()
                (self.dest / 'keep').write_text('concurrent work')
            return result
        with patch.object(b, 'git', racing_git), self.assertRaises(FileExistsError):
            self.create()
        self.assertEqual((self.dest / 'keep').read_text(), 'concurrent work')
        self.assertEqual(len(list(self.dest.iterdir())), 1)

    def test_empty_destination_replaced_during_staging_preserved(self):
        self.dest.mkdir()
        original_git = b.git
        def racing_git(root, *args, **kwargs):
            result = original_git(root, *args, **kwargs)
            if args[0] == 'init':
                self.dest.rename(self.root / 'original-directory')
                self.dest.mkdir()
            return result
        with patch.object(b, 'git', racing_git), self.assertRaises(b.BootstrapError):
            self.create()
        self.assertEqual(list(self.dest.iterdir()), [])
        self.assertEqual(list((self.root / 'original-directory').iterdir()), [])

    def test_empty_destination_occupied_during_staging(self):
        self.dest.mkdir()
        original_git = b.git
        def racing_git(root, *args, **kwargs):
            result = original_git(root, *args, **kwargs)
            if args[0] == 'init':
                (self.dest / 'keep').write_text('concurrent')
            return result
        with patch.object(b, 'git', racing_git), self.assertRaises(b.BootstrapError):
            self.create()
        self.assertEqual([p.name for p in self.dest.iterdir()], ['keep'])

    def test_failure_before_publication_leaves_no_target(self):
        original_git = b.git
        def failing_git(root, *args, **kwargs):
            if args[0] == 'init':
                raise b.BootstrapError('synthetic init failure')
            return original_git(root, *args, **kwargs)
        with patch.object(b, 'git', failing_git), self.assertRaises(b.BootstrapError):
            self.create()
        self.assertFalse(self.dest.exists())
        self.assertFalse(list(self.root.glob('.gptclaw-staging-*')))

    def test_mid_publication_failure_preserves_marker_and_files(self):
        original_link = os.link
        count = 0
        def failing_link(*args, **kwargs):
            nonlocal count
            count += 1
            if count == 3:
                raise OSError('synthetic publication failure')
            return original_link(*args, **kwargs)
        with patch.object(b.os, 'link', failing_link), self.assertRaises(OSError):
            self.create()
        self.assertTrue((self.dest / b.MARKER).exists())
        before = self.snapshot(self.dest)
        with self.assertRaises(b.BootstrapError):
            self.create()
        self.assertEqual(before, self.snapshot(self.dest))
        self.assertFalse(list(self.root.glob('.gptclaw-staging-*')))

    def test_concurrent_file_is_not_overwritten(self):
        original_link = os.link
        def racing_link(src, dst, **kwargs):
            if dst == 'README.md':
                fd = os.open(dst, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600,
                             dir_fd=kwargs['dst_dir_fd'])
                os.write(fd, b'concurrent owner content')
                os.close(fd)
            return original_link(src, dst, **kwargs)
        with patch.object(b.os, 'link', racing_link), self.assertRaises(FileExistsError):
            self.create()
        self.assertEqual((self.dest / 'README.md').read_text(), 'concurrent owner content')
        self.assertTrue((self.dest / b.MARKER).exists())

    def test_global_git_templates_not_copied(self):
        templates = self.root / 'evil-template'
        templates.mkdir()
        (templates / 'config').write_text('[remote "unexpected"]\nurl = synthetic\n')
        with patch.dict(os.environ, {'GIT_TEMPLATE_DIR': str(templates), 'GIT_DIR': '/not-a-repo'}):
            self.create()
        self.assertFalse(b.git(self.dest, 'remote').stdout)


if __name__ == '__main__':
    unittest.main()
