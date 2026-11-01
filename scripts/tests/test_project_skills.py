"""Offline selection/materialization regressions; synthetic project-owned files only."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import project_guidance as guidance
import project_skills as skills


class SkillDeliveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='gptclaw-journey-skills-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'project'
        self.root.mkdir()
        self.read = lambda name: (ROOT / name).read_bytes()
        files, self.record = guidance.payload(self.read)
        for name, content in files.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)

    def snapshot(self):
        return {p.relative_to(self.root).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
                for p in self.root.rglob('*') if p.is_file() and not p.is_symlink()}

    def selection(self):
        return json.loads((self.root / skills.SELECTION).read_text())

    def test_selection_exact_and_mixed_union(self):
        for caps in [[], ['runtime'], ['android'], ['runtime', 'android'], ['android', 'native-build'], ['native-build', 'android', 'runtime']]:
            files, record = guidance.payload(self.read, caps)
            actual = {Path(p).parts[2] for p in files if p.startswith('.agents/skills/')}
            self.assertEqual(actual, set(skills.selected(caps)))
            self.assertEqual(record['capabilities'], sorted(set(caps)))
            for path, item in record['files'].items():
                self.assertEqual(skills.digest(files[path]), item['sha256'])
            self.assertLessEqual(len(files[skills.BUNDLE]), 1048576)

    def test_unknown_and_inconsistent_capabilities_refused(self):
        for caps in [['ios'], ['native-build'], ['runtime;touch sentinel'], [1]]:
            with self.assertRaises(ValueError):
                guidance.payload(self.read, caps)

    def test_preview_is_no_write_and_apply_retries_are_noop(self):
        before = self.snapshot()
        caps = ['runtime', 'android', 'native-build']
        preview = skills.materialize(self.root, caps)
        self.assertEqual(before, self.snapshot())
        applied = skills.materialize(self.root, caps, True)
        self.assertEqual(preview['add'], applied['add'])
        self.assertEqual(self.selection()['packages'], sorted(skills.PACKAGES))
        after = self.snapshot()
        self.assertEqual(skills.materialize(self.root, caps, True)['status'], 'unchanged')
        self.assertEqual(after, self.snapshot())

    def test_standalone_without_source_import_or_checkout(self):
        # Isolated Python can import only the copied script's stdlib dependencies.
        result = subprocess.run([sys.executable, '-I', str(self.root / skills.HELPER),
                                 '--project-root', str(self.root), '--capability', 'android', '--apply'],
                                cwd=self.root, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'materialized')
        self.assertTrue((self.root / '.agents/skills/gptclaw-android-operation/references/device.md').is_file())

    def test_current_capabilities_never_removed(self):
        skills.materialize(self.root, ['android'], True)
        skills.materialize(self.root, ['runtime'], True)
        self.assertEqual(self.selection()['capabilities'], ['android', 'runtime'])

    def test_later_native_build_can_extend_existing_android_selection(self):
        skills.materialize(self.root, ['android'], True)
        skills.materialize(self.root, ['native-build'], True)
        self.assertEqual(self.selection()['capabilities'], ['android', 'native-build'])

    def test_catalogue_stage_rejects_bad_engineering_link(self):
        stage = self.root.parent / 'stage'
        stage.mkdir()
        (stage / 'AGENTS.md').write_text('# Synthetic project')
        def broken(name):
            data = self.read(name)
            if name == guidance.ENGINEERING + 'delivery.md':
                data += b'\n[Missing](missing.md)\n'
            return data
        with self.assertRaisesRegex(ValueError, 'Broken generated'):
            guidance.install(stage, broken, capabilities=['runtime'])
        self.assertFalse((stage / 'docs/starter-guidance-provenance.json').exists())

    def test_adapted_active_skill_preserved_with_no_writes(self):
        path = self.root / '.agents/skills/gptclaw-specification/SKILL.md'
        path.write_text(path.read_text() + '\nProject adaptation\n')
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, 'Adapted active'):
            skills.materialize(self.root, ['android'], True)
        self.assertEqual(before, self.snapshot())

    def test_unknown_collision_is_not_adopted_even_if_identical(self):
        bundle = json.loads((self.root / skills.BUNDLE).read_text())
        name = '.agents/skills/gptclaw-android-operation/SKILL.md'
        path = self.root / name
        path.parent.mkdir()
        path.write_text(bundle['files'][name]['text'])
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, 'collision'):
            skills.materialize(self.root, ['android'], True)
        self.assertEqual(before, self.snapshot())

    def test_unrelated_skill_is_preserved(self):
        path = self.root / '.agents/skills/project-owned/SKILL.md'
        path.parent.mkdir()
        path.write_text('Unrelated owner work')
        skills.materialize(self.root, ['android'], True)
        self.assertEqual(path.read_text(), 'Unrelated owner work')

    def test_missing_active_resource_refuses_before_additions(self):
        (self.root / '.agents/skills/gptclaw-specification/assets/tasks.md').unlink()
        with self.assertRaises(ValueError):
            skills.materialize(self.root, ['android'], True)
        self.assertFalse((self.root / skills.MARKER).exists())

    def test_bundle_and_helper_modification_refused(self):
        for relative in [skills.BUNDLE, skills.HELPER]:
            path = self.root / relative
            before = path.read_bytes()
            path.write_bytes(before + b'\n')
            with self.assertRaisesRegex(ValueError, 'identity mismatch'):
                skills.materialize(self.root, ['android'], True)
            path.write_bytes(before)

    def test_missing_resource_bad_hash_and_escape_refused(self):
        original = json.loads((self.root / skills.BUNDLE).read_text())
        import copy
        for mode in ['missing', 'hash', 'escape', 'link']:
            bundle = copy.deepcopy(original)
            path = '.agents/skills/gptclaw-android-operation/SKILL.md'
            if mode == 'missing':
                del bundle['files'][path]
            elif mode == 'hash':
                bundle['files'][path]['sha256'] = '0' * 64
            elif mode == 'escape':
                bundle['files']['../../outside'] = bundle['files'].pop(path)
            else:
                item = bundle['files'][path]
                item['text'] += '\n[Missing](../../outside.md)\n'
                item['sha256'] = skills.digest(item['text'].encode())
            with self.assertRaises(ValueError):
                skills.validate_bundle(bundle)

    def test_symlink_skill_parent_refuses_without_external_writes(self):
        outside = self.root.parent / 'outside'
        outside.mkdir()
        (self.root / '.agents/skills/gptclaw-android-operation').symlink_to(outside, target_is_directory=True)
        with self.assertRaises(ValueError):
            skills.materialize(self.root, ['android'], True)
        self.assertEqual(list(outside.iterdir()), [])

    def test_symlink_root_ancestor_refused(self):
        alias = self.root.parent / 'alias'
        alias.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(ValueError):
            skills.materialize(alias, ['android'], True)

    def test_partial_publication_retains_marker_and_blocks_blind_retry(self):
        original = skills.publish
        def interrupt(root, path, data):
            if path != skills.MARKER:
                raise OSError('synthetic interruption')
            return original(root, path, data)
        with patch.object(skills, 'publish', side_effect=interrupt), self.assertRaises(OSError):
            skills.materialize(self.root, ['android'], True)
        self.assertTrue((self.root / skills.MARKER).exists())
        with self.assertRaisesRegex(ValueError, 'Incomplete'):
            skills.materialize(self.root, ['android'], True)

    def test_missing_source_resource_and_invalid_link_reject_payload(self):
        path = '.agents/skills/gptclaw-native-preview/references/preview.md'
        def missing(name):
            if name == path:
                raise ValueError('missing')
            return self.read(name)
        with self.assertRaises(ValueError):
            guidance.payload(missing)
        def broken(name):
            data = self.read(name)
            if name == path:
                data += b'\n[Missing](missing.md)\n'
            return data
        with self.assertRaises(ValueError):
            guidance.payload(broken)


if __name__ == '__main__':
    unittest.main()
