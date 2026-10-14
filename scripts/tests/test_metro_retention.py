#!/usr/bin/env python3
"""Owned runtime-copy capacity/cleanup tests with synthetic data only."""
from copy import deepcopy
import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import private_apps as app
import metro_retention as retention
import metro_sessions as sessions
import metro_spike as spike


class RetentionTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.projects = Path(temp.name)/'projects'
        self.projects.mkdir()
        self.root = self.projects/'fixture'
        self.root.mkdir()
        self.patch(app, 'PROJECTS', self.projects)
        self.patch(app, 'STORE', self.projects/'.runtime')
        self.patch(app, 'target', lambda root: (self.root, {'schema_version': 6}))
        self.patch(retention.worktrees, 'canonical', lambda root: {'project': 'fixture', 'key': '1'*64})
        self.patch(sessions, 'assert_stopped', lambda *args: None)
        self.patch(spike, 'require_operator', lambda: None)
        self.patch(retention.time, 'time', lambda: 1800001000)
        self.current = {
            'schema_version': 1, 'adapter': 'metro-v1', 'project': 'fixture',
            'root': str(self.root), 'canonical_key': '1'*64, 'name': 'gptclaw-metro-fixture',
            'generation': '2'*32, 'token': '3'*32, 'image': 'sha256:'+'4'*64,
            'input_digest': '5'*64, 'policy_digest': '6'*64, 'unit_digest': '7'*64,
            'metro_port': 18600, 'proxy_port': 18601,
            'origin': 'https://fixture.tail123.ts.net:8443',
            'phase': 'expired', 'started_at': 1800000000, 'expires_at': 1800000300,
            'operation_id': '8'*32, 'operation_result': 'passed',
            'observations': {'process': {'state': 'down', 'observed_at': 1800000301},
                             'protocol': {'state': 'ready', 'observed_at': 1800000299},
                             'route': {'state': 'pending', 'observed_at': None}},
        }
        self.patch(sessions, 'load', lambda *args: deepcopy(self.current))
        self.seed(self.root)
        self.inventory = spike.source_inventory(self.root)

    def patch(self, obj, key, value):
        mock = patch.object(obj, key, value)
        mock.start()
        self.addCleanup(mock.stop)

    def seed(self, root):
        root.mkdir(parents=True, exist_ok=True)
        for name in spike.ROOT_FILES:
            (root/name).write_text('{"expo":{}}' if name == 'app.json' else 'synthetic')
        (root/'src').mkdir()
        (root/'src/index.tsx').write_text('export const synthetic = true;')
        (root/'assets').mkdir()
        (root/'assets/icon.png').write_bytes(b'synthetic-icon')

    def view(self, generation='9'*32, seal=True):
        value = deepcopy(self.current)
        value['generation'] = generation
        destination = retention.base('fixture')/'sources'/generation
        destination.parent.mkdir(parents=True, exist_ok=True)
        spike.prepare_view(self.root, destination, self.inventory)
        if seal:
            retention.seal(value, self.inventory)
        if generation != self.current['generation']:
            history = retention.base('fixture')/'history'
            history.mkdir(exist_ok=True)
            app.save(history/(generation+'.json'), value)
        return value, destination

    def test_usage_separates_generated_copies_from_metadata_without_reading_canonical_source(self):
        _, view = self.view()
        app.save(retention.base('fixture')/'status.json', {'synthetic': True})
        result = retention.usage('fixture')
        self.assertEqual(result['source_bytes'], retention.source_bytes(self.root, self.inventory))
        self.assertGreater(result['artifact_bytes'], 0)
        self.assertNotIn('export const', json.dumps(result))
        self.assertTrue((self.root/'src/index.tsx').exists())

    def test_capacity_rejects_before_start_or_cache_mutation(self):
        self.view()
        observed = retention.usage('fixture')
        before = observed.copy()
        with patch.object(retention, 'MAX_SOURCES', observed['source_bytes']):
            with self.assertRaises(app.AppError) as error:
                retention.admit('fixture', 1)
        self.assertEqual(error.exception.code, 'metro-capacity')
        self.assertEqual(retention.usage('fixture'), before)

    def test_metadata_budget_reserves_space_for_the_next_operation(self):
        self.view()
        observed = retention.usage('fixture')
        with patch.object(retention, 'MAX_ARTIFACTS', observed['artifact_bytes']+retention.START_RESERVE-1), self.assertRaises(app.AppError):
            retention.admit('fixture', 0)

    def test_copy_count_cannot_exceed_the_cleanup_scan_bound(self):
        self.view()
        with patch.object(retention, 'MAX_COPIES', 1), self.assertRaises(app.AppError):
            retention.admit('fixture', 0)

    def test_symlink_hardlink_and_unknown_objects_are_never_followed(self):
        base = retention.base('fixture')
        base.mkdir(parents=True)
        target = self.root/'src/index.tsx'
        (base/'linked').symlink_to(target)
        with self.assertRaises(app.AppError):
            retention.usage('fixture')
        (base/'linked').unlink()
        os.link(target, base/'linked')
        with self.assertRaises(app.AppError):
            retention.usage('fixture')
        (base/'linked').unlink()
        self.assertEqual(target.read_text(), 'export const synthetic = true;')

    def test_unknown_and_current_copies_are_retained_by_read_only_plan(self):
        self.view(self.current['generation'])
        _, unknown = self.view('a'*32, seal=False)
        before = retention.usage('fixture')
        result = retention.prune(self.root)
        self.assertEqual(result['copies'], [])
        self.assertEqual({item['reason'] for item in result['retained']}, {'current', 'missing-marker'})
        self.assertEqual(retention.usage('fixture'), before)
        self.assertTrue(unknown.exists())

    def test_owned_inactive_copy_cleanup_preserves_current_and_canonical_source(self):
        _, old = self.view()
        _, current = self.view(self.current['generation'])
        source = (self.root/'src/index.tsx').read_bytes()
        plan = retention.prune(self.root)
        self.assertEqual(len(plan['copies']), 1)
        result = retention.prune(self.root, True, plan['plan_digest'])
        self.assertTrue(result['changed'])
        self.assertFalse(old.exists())
        self.assertTrue(current.exists())
        self.assertEqual((self.root/'src/index.tsx').read_bytes(), source)
        self.assertTrue((retention.base('fixture')/'history'/('9'*32+'.json')).exists())

    def test_unconfirmed_prune_never_deletes_generated_copy(self):
        _, old = self.view()
        with self.assertRaises(app.AppError):
            retention.prune(self.root, True, '0'*64)
        self.assertTrue(old.exists())

    def test_edited_generated_copy_is_preserved_and_blocks_confirmation(self):
        _, old = self.view()
        plan = retention.prune(self.root)
        (old/'src/index.tsx').write_text('independent edit')
        with self.assertRaises(app.AppError):
            retention.prune(self.root, True, plan['plan_digest'])
        self.assertEqual((old/'src/index.tsx').read_text(), 'independent edit')

    def test_replaced_directory_identity_is_not_accepted_even_with_same_bytes(self):
        _, old = self.view()
        retained = old.with_name('b'*32)
        old.rename(retained)
        spike.prepare_view(self.root, old, self.inventory)
        with self.assertRaises(app.AppError):
            retention.prune(self.root)
        self.assertTrue(retained.exists())
        self.assertTrue(old.exists())

    def test_unresolved_generation_cannot_be_selected(self):
        value, old = self.view()
        value['phase'] = 'recovery-required'
        value['operation_result'] = 'unknown'
        app.save(retention.base('fixture')/'history'/('9'*32+'.json'), value)
        plan = retention.prune(self.root)
        self.assertEqual(plan['copies'], [])
        self.assertEqual(plan['retained'][0]['reason'], 'unresolved')
        self.assertTrue(old.exists())

    def test_active_or_unknown_current_runtime_blocks_all_cleanup(self):
        self.view()
        with patch.object(sessions, 'assert_stopped', side_effect=app.AppError('busy')), patch.object(retention.shutil, 'rmtree') as remove, self.assertRaises(app.AppError):
            retention.prune(self.root)
        remove.assert_not_called()

    def test_corrupt_or_foreign_marker_is_not_cleanup_authority(self):
        value, old = self.view()
        marker = retention.marker_path('fixture', value['generation'])
        original = app.read_json(marker)
        for key, changed in [('root', str(self.projects/'other')), ('source_bytes', True),
                             ('directory_identity', [True, 1]), ('schema_version', True),
                             ('source_digest', '0'*64)]:
            app.save(marker, dict(original, **{key: changed}))
            with self.subTest(key=key), self.assertRaises(app.AppError):
                retention.prune(self.root)
            self.assertTrue(old.exists())
        app.save(marker, original)

    def test_dirty_placeholder_or_extra_file_is_preserved(self):
        _, old = self.view()
        (old/'.expo/devices.json').write_text('synthetic-owner-edit')
        with self.assertRaises(app.AppError):
            retention.prune(self.root)
        self.assertTrue((old/'.expo/devices.json').exists())

    def test_post_move_racing_replacement_is_retained_for_recovery(self):
        _, old = self.view()
        plan = retention.prune(self.root)
        original = retention.os.rename
        def race(source, target):
            original(source, target)
            if str(target).split('/')[-1].startswith('prune-'):
                (Path(target)/'src/index.tsx').write_text('racing edit')
        with patch.object(retention.os, 'rename', side_effect=race), self.assertRaises(app.AppError) as error:
            retention.prune(self.root, True, plan['plan_digest'])
        self.assertEqual(error.exception.code, 'metro-prune-recovery')
        preserved = list(retention.base('fixture').glob('prune-*'))
        self.assertEqual(len(preserved), 1)
        self.assertEqual((preserved[0]/'src/index.tsx').read_text(), 'racing edit')
        self.assertTrue((self.root/'src/index.tsx').exists())

    def test_old_owned_metadata_retires_after_seven_days_and_evidence_is_preserved(self):
        value, old = self.view()
        failure = retention.base('fixture')/('failure-'+value['generation']+'.json')
        app.save(failure, {'schema_version': 1, 'generation': value['generation'],
                           'stage': 'supervision', 'code': 'health'})
        evidence = retention.base('fixture')/('protocol-evidence-'+value['generation']+'.json')
        app.save(evidence, {'synthetic_acceptance': True})
        with patch.object(retention.time, 'time', return_value=1800000301+retention.RETENTION_SECONDS):
            plan = retention.prune(self.root)
            self.assertEqual(len(plan['retired_records']), 3)
            result = retention.prune(self.root, True, plan['plan_digest'])
        self.assertFalse(old.exists())
        self.assertFalse(failure.exists())
        self.assertFalse((retention.base('fixture')/'history'/(value['generation']+'.json')).exists())
        self.assertTrue(evidence.exists())
        self.assertTrue(result['changed'])

    def test_recent_diagnostics_and_history_are_retained(self):
        value, old = self.view()
        plan = retention.prune(self.root)
        self.assertEqual(plan['retired_records'], [])
        retention.prune(self.root, True, plan['plan_digest'])
        self.assertTrue(retention.marker_path('fixture', value['generation']).exists())

    def test_aged_metadata_without_owned_marker_is_never_retired(self):
        value, old = self.view(seal=False)
        with patch.object(retention.time, 'time', return_value=1800000301+retention.RETENTION_SECONDS):
            plan = retention.prune(self.root)
        self.assertEqual(plan['retired_records'], [])
        self.assertTrue(old.exists())

    def test_changed_metadata_after_move_is_preserved_for_recovery(self):
        value, old = self.view()
        with patch.object(retention.time, 'time', return_value=1800000301+retention.RETENTION_SECONDS):
            plan = retention.prune(self.root)
            original = retention.os.rename
            def race(source, target):
                original(source, target)
                if str(target).split('/')[-1].startswith('prune-record-'):
                    app.save(Path(target), {'independent_edit': True})
            with patch.object(retention.os, 'rename', side_effect=race), self.assertRaises(app.AppError) as error:
                retention.prune(self.root, True, plan['plan_digest'])
        self.assertEqual(error.exception.code, 'metro-prune-recovery')
        preserved = list(retention.base('fixture').glob('prune-record-*'))
        self.assertEqual(app.read_json(preserved[0]), {'independent_edit': True})

    def test_cleanup_plan_batches_copies_and_keeps_metadata_generations_together(self):
        for generation in ['9'*32,'a'*32,'b'*32]:
            self.view(generation)
        with patch.object(retention,'MAX_PRUNE_COPIES',2),patch.object(retention,'MAX_PRUNE_RECORDS',3),patch.object(retention.time,'time',return_value=1800000301+retention.RETENTION_SECONDS):
            plan=retention.prune(self.root)
        self.assertEqual(len(plan['copies']),2)
        self.assertIn('next-batch',{item['reason'] for item in plan['retained']})
        self.assertEqual(len(plan['retired_records']),2)
        self.assertEqual({item['path'].split('/')[-1] for item in plan['retired_records']},{'9'*32+'.json'})

    def test_prune_cli_is_read_only_by_default(self):
        import contextlib, io, gptclawctl
        output = io.StringIO()
        self.view()
        with patch.object(gptclawctl,'os',SimpleNamespace(getuid=lambda:1002,geteuid=lambda:1002)), patch.object(retention.worktrees, 'guard'), contextlib.redirect_stdout(output):
            self.assertEqual(gptclawctl.main(['metro', 'prune', '--project-root', str(self.root)]), 0)
        self.assertEqual(json.loads(output.getvalue())['state'], 'prune-planned')


if __name__ == '__main__':
    unittest.main()
