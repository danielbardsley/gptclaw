#!/usr/bin/env python3
"""Synthetic exact Serve ownership/readback and verified-TLS boundary tests."""
from copy import deepcopy
import io
import json
from pathlib import Path
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import private_apps as app
import metro_routes as routes
import metro_sessions as sessions


class RouteTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.projects = Path(temp.name)/'projects'
        self.projects.mkdir()
        self.root = self.projects/'fixture'
        self.root.mkdir()
        self.patch(app, 'PROJECTS', self.projects)
        self.patch(app, 'STORE', self.projects/'.runtime')
        now = time.time()
        self.value = {
            'schema_version': 1, 'adapter': 'metro-v1', 'project': 'fixture',
            'root': str(self.root), 'canonical_key': '1'*64,
            'name': 'gptclaw-metro-fixture', 'generation': '2'*32, 'token': '3'*32,
            'image': 'sha256:'+'4'*64, 'input_digest': '5'*64, 'policy_digest': '6'*64,
            'unit_digest': '7'*64, 'metro_port': 18600, 'proxy_port': 18601,
            'origin': 'https://fixture.tail123.ts.net:8443', 'phase': 'running',
            'started_at': now-1, 'expires_at': now+300,
            'operation_id': '8'*32, 'operation_result': 'passed',
            'observations': {'process': {'state': 'up', 'observed_at': now},
                             'protocol': {'state': 'ready', 'observed_at': now},
                             'route': {'state': 'pending', 'observed_at': None}},
        }
        self.baseline = {'TCP': {'443': {'HTTPS': True}}, 'Web': {
            'fixture.tail123.ts.net:443': {'Handlers': {
                '/projects/': {'Proxy': 'http://127.0.0.1:18079/projects/'},
                '/dashboard/': {'Proxy': 'http://127.0.0.1:18200/dashboard/'}}}}}
        self.current = deepcopy(self.baseline)
        self.entries = {'fixture': {'root': str(self.root), 'canonical_key': '1'*64, 'slot': 0}}
        self.calls = []
        def command(argv, **kw):
            self.calls.append(argv)
            self.assertEqual(argv, ['tailscale', 'serve', 'status', '--json'])
            self.assertEqual(kw['timeout'], 5)
            return SimpleNamespace(stdout=json.dumps(self.current))
        self.patch(app, 'command', command)
        self.patch(app, 'node_identity', lambda: 'fixture.tail123.ts.net')
        self.patch(app, 'target', lambda root: (self.root, {'schema_version': 6}))
        self.patch(sessions, 'load', lambda *args: deepcopy(self.value))
        self.patch(sessions, 'slots', lambda: deepcopy(self.entries))
        self.patch(routes.worktrees, 'canonical', lambda root: {'project': 'fixture', 'key': '1'*64})
        self.patch(sessions.spike, 'require_operator', lambda: None)

    def patch(self, obj, key, value):
        mock = patch.object(obj, key, value)
        mock.start()
        self.addCleanup(mock.stop)

    def record(self):
        plan = routes.plan(self.root)
        return routes.plan(self.root, True, plan['plan_digest'])

    def configure(self, value=None):
        value = value or self.value
        port, authority, web = routes.binding(value)
        self.current.setdefault('TCP', {})[port] = {'HTTPS': True}
        self.current.setdefault('Web', {})[authority] = web

    def test_plan_is_read_only_and_contains_only_exact_operator_commands(self):
        result = routes.plan(self.root)
        self.assertFalse(app.STORE.exists())
        self.assertEqual(result['operator_add'], ['sudo', 'tailscale', 'serve', '--bg',
                                                '--https=8443', 'http://127.0.0.1:18601'])
        self.assertEqual(result['operator_remove'], ['sudo', 'tailscale', 'serve', '--bg', '--https=8443', 'off'])
        self.assertNotIn('token', json.dumps(result))
        self.assertEqual(result['access_policy'], 'operator-confirmation-required')

    def test_record_requires_current_digest_and_never_mutates_serve(self):
        plan = routes.plan(self.root)
        with self.assertRaises(app.AppError):
            routes.plan(self.root, True, '0'*64)
        self.assertFalse(routes.record_path('fixture').exists())
        result = routes.plan(self.root, True, plan['plan_digest'])
        self.assertTrue(result['changed'])
        self.assertEqual(self.current, self.baseline)
        self.assertFalse(routes.plan(self.root, True, plan['plan_digest'])['changed'])

    def test_stale_baseline_is_rejected_before_record(self):
        plan = routes.plan(self.root)
        self.current['Web']['fixture.tail123.ts.net:443']['Handlers']['/other/'] = {'Proxy': 'http://127.0.0.1:19999'}
        with self.assertRaises(app.AppError):
            routes.plan(self.root, True, plan['plan_digest'])
        self.assertFalse(routes.record_path('fixture').exists())

    def test_unowned_even_identical_listener_blocks_adoption(self):
        self.configure()
        with self.assertRaises(app.AppError):
            routes.plan(self.root)
        self.assertFalse(app.STORE.exists())

    def test_partial_occupied_listener_blocks_without_touching_it(self):
        self.current['TCP']['8443'] = {'TCPForward': '127.0.0.1:19999'}
        with self.assertRaises(app.AppError):
            routes.plan(self.root)
        self.assertEqual(self.current['TCP']['8443'], {'TCPForward': '127.0.0.1:19999'})

    def test_funnel_and_unknown_config_fail_closed(self):
        for value in [dict(self.baseline, AllowFunnel={'fixture:443': True}),
                      dict(self.baseline, AllowFunnel={'fixture:443': 0}),
                      dict(self.baseline, Services={}), [], {'TCP': []}]:
            with self.subTest(value=value), self.assertRaises(app.AppError):
                routes.validate_config(value)

    def test_unrecorded_config_never_becomes_verified(self):
        self.configure()
        with patch.object(routes, 'health') as health:
            self.assertEqual(routes.observe(self.value)['state'], 'pending')
            health.assert_not_called()

    def test_recorded_absent_listener_remains_pending(self):
        self.record()
        with patch.object(routes, 'health') as health:
            self.assertEqual(routes.observe(self.value)['state'], 'pending')
            health.assert_not_called()

    def test_exact_listener_and_generation_health_verify_separately(self):
        self.record()
        self.configure()
        with patch.object(routes, 'health', return_value=True) as health:
            self.assertEqual(routes.observe(self.value)['state'], 'verified')
            health.assert_called_once_with(self.value)

    def test_tls_or_health_failure_does_not_change_process_or_claim_readiness(self):
        self.record()
        self.configure()
        with patch.object(routes, 'health', side_effect=app.AppError('health')):
            self.assertEqual(routes.observe(self.value)['state'], 'failed')
        self.assertEqual(self.value['observations']['process']['state'], 'up')

    def test_existing_handler_drift_blocks_and_is_preserved(self):
        self.record()
        self.configure()
        self.current['Web']['fixture.tail123.ts.net:443']['Handlers']['/dashboard/']['Proxy'] = 'http://127.0.0.1:19999'
        with patch.object(routes, 'health') as health:
            self.assertEqual(routes.observe(self.value)['state'], 'failed')
            health.assert_not_called()

    def test_two_approved_listeners_coexist_and_stop_leaves_other_unchanged(self):
        self.record()
        two = deepcopy(self.value)
        two.update(project='second', root=str(self.projects/'second'), name='gptclaw-metro-second',
                   canonical_key='9'*64, metro_port=18602, proxy_port=18603,
                   origin='https://fixture.tail123.ts.net:8444')
        self.entries['second'] = {'root': two['root'], 'canonical_key': '9'*64, 'slot': 1}
        proposal = routes.payload(two, self.baseline)
        record = dict(proposal, plan_digest=routes.digest(proposal), recorded_at=time.time())
        path = routes.record_path('second')
        path.parent.mkdir(parents=True)
        app.save(path, record)
        self.configure()
        self.configure(two)
        with patch.object(routes, 'health', return_value=True):
            self.assertEqual(routes.observe(self.value)['state'], 'verified')
            self.assertEqual(routes.observe(two)['state'], 'verified')
            del self.current['TCP']['8443']
            del self.current['Web']['fixture.tail123.ts.net:8443']
            self.assertEqual(routes.observe(self.value)['state'], 'pending')
            self.assertEqual(routes.observe(two)['state'], 'verified')

    def test_wrong_route_or_generation_binding_denied(self):
        self.record()
        self.configure()
        self.current['Web']['fixture.tail123.ts.net:8443']['Handlers']['/']['Proxy'] = 'http://127.0.0.1:18603'
        with patch.object(routes, 'health') as health:
            self.assertEqual(routes.observe(self.value)['state'], 'failed')
            health.assert_not_called()
        wrong = deepcopy(self.value)
        wrong['canonical_key'] = '8'*64
        self.assertEqual(routes.observe(wrong)['state'], 'failed')

    def test_record_corruption_and_slot_reassignment_are_rejected(self):
        self.record()
        path = routes.record_path('fixture')
        original = app.read_json(path)
        for field, changed in [('plan_digest', '0'*64), ('proxy_port', 18603),
                               ('root', str(self.projects/'other')), ('schema_version', True)]:
            app.save(path, dict(original, **{field: changed}))
            with self.subTest(field=field), self.assertRaises(app.AppError):
                routes.records()
        app.save(path, original)
        self.entries['fixture']['slot'] = 1
        with self.assertRaises(app.AppError):
            routes.records()

    def test_tls_probe_uses_default_trust_and_never_follows_redirect(self):
        data = {'adapter': 'metro-v1', 'project': 'fixture',
                'generation': '2'*32, 'expires_at': self.value['expires_at']}
        response = Mock(status=200)
        response.getheaders.return_value = [('Content-Type', 'application/json')]
        response.getheader.return_value = None
        response.read.return_value = json.dumps(data).encode()
        connection = Mock()
        connection.getresponse.return_value = response
        with patch.object(routes.http.client, 'HTTPSConnection', return_value=connection) as create:
            self.assertTrue(routes.health(self.value))
            create.assert_called_once_with('fixture.tail123.ts.net', 8443, timeout=3)
            self.assertEqual(connection.request.call_args.args, ('GET', routes.HEALTH_PATH))
            response.status = 302
            with self.assertRaises(app.AppError):
                routes.health(self.value)
        self.assertEqual(connection.close.call_count, 2)

    def test_health_response_cannot_certify_wrong_session_or_extra_device_data(self):
        connection = Mock()
        response = connection.getresponse.return_value
        response.status = 200
        response.getheaders.return_value = []
        response.getheader.return_value = None
        for data in [{'adapter': 'metro-v1', 'project': 'other', 'generation': '2'*32,
                      'expires_at': self.value['expires_at']},
                     {'adapter': 'metro-v1', 'project': 'fixture', 'generation': '9'*32,
                      'expires_at': self.value['expires_at']},
                     {'adapter': 'metro-v1', 'project': 'fixture', 'generation': '2'*32,
                      'expires_at': self.value['expires_at'], 'device': 'synthetic'},
                     'x'*4097]:
            response.read.return_value = json.dumps(data).encode()
            with self.subTest(data=data), patch.object(routes.http.client, 'HTTPSConnection', return_value=connection), self.assertRaises(app.AppError):
                routes.health(self.value)

    def test_malformed_record_is_a_failed_observation_without_raw_exception(self):
        path = routes.record_path('fixture')
        path.parent.mkdir(parents=True)
        for changed in [[], {'project': []}, {'project': 'fixture'}]:
            app.save(path, changed)
            self.assertEqual(routes.observe(self.value)['state'], 'failed')

    def test_route_plan_checks_registry_slot_before_showing_operator_command(self):
        self.entries['fixture']['slot'] = 1
        with self.assertRaises(app.AppError):
            routes.plan(self.root)
        self.assertFalse(app.STORE.exists())

    def test_boolean_config_substitution_is_not_exact_ownership(self):
        self.record()
        self.configure()
        self.current['TCP']['8443']['HTTPS'] = 1
        with patch.object(routes, 'health') as health:
            self.assertEqual(routes.observe(self.value)['state'], 'failed')
            health.assert_not_called()

    def test_expired_and_stopped_sessions_cannot_verify_retained_operator_listener(self):
        self.record()
        self.configure()
        for state in ['stopped', 'expired', 'failed']:
            value = dict(self.value, phase=state)
            with patch.object(routes, 'health') as health:
                self.assertEqual(routes.observe(value)['state'], 'failed')
                health.assert_not_called()


if __name__ == '__main__':
    unittest.main()
