"""Snapshot freshness, bounded workers and actual Unix HTTP boundary tests."""
import http.client
import json
import multiprocessing
import os
from pathlib import Path
import socket
import sys
import tempfile
import threading
import time
import unittest

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dashboard_collector as collector


def hung(_):
    time.sleep(10)
    return {'late': True}


def large(_):
    return {'data': 's'*10000}


def ready(_):
    return {'state': 'ready'}


class UnixClient(http.client.HTTPConnection):
    def __init__(self, path):
        super().__init__('localhost', timeout=3)
        self.path = path

    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.sock.connect(self.path)


class CollectorTests(unittest.TestCase):
    def test_timeout_output_limit_and_reaping(self):
        before = {p.pid for p in multiprocessing.active_children()}
        started = time.monotonic()
        self.assertEqual(collector.bounded(hung, {}, .2)['error'], 'observation-timeout')
        self.assertLess(time.monotonic()-started, 1)
        self.assertEqual(collector.bounded(large, {}, 2, 100)['error'], 'observation-invalid')
        self.assertEqual(collector.bounded(ready, {}, 2), {'state': 'ready'})
        self.assertEqual({p.pid for p in multiprocessing.active_children()}, before)

    def test_empty_initial_stale_failure_recovery_and_no_read_collection(self):
        now = [100.]
        results = [{'snapshot': {'schema_version': 1, 'observed_at': 100., 'last_success_at': 100., 'freshness': 'current',
            'complete': True, 'rows': [], 'diagnostics': []}, 'bindings': {}}]
        calls = []
        def run(*args):
            calls.append(args)
            return results[0]
        c = collector.Collector({}, clock=lambda: now[0], run=run)
        self.assertEqual(c.snapshot()['freshness'], 'unavailable')
        c.refresh_inventory()
        self.assertEqual(c.snapshot()['freshness'], 'current')
        self.assertTrue(c.snapshot()['complete'])
        for _ in range(20):
            c.snapshot()
        self.assertEqual(len(calls), 1)
        now[0] = 161
        self.assertEqual(c.snapshot()['freshness'], 'stale')
        results[0] = {'error': 'observation-timeout'}
        c.refresh_inventory()
        self.assertEqual(c.snapshot()['last_success_at'], 100)
        self.assertEqual(c.snapshot()['freshness'], 'stale')
        results[0] = {'snapshot': {'schema_version': 1, 'observed_at': 161., 'last_success_at': 161., 'freshness': 'current',
            'complete': False, 'truncated': True, 'rows': [], 'diagnostics': [{'code': 'input_path'}]}, 'bindings': {}}
        c.refresh_inventory()
        self.assertEqual(c.snapshot()['freshness'], 'current')
        self.assertTrue(c.snapshot()['truncated'])
        self.assertEqual(c.snapshot()['last_success_at'], 161)

    def test_partial_inventory_preserves_stale_rows_without_target_binding(self):
        first={'snapshot':{'schema_version':1,'observed_at':100.,'last_success_at':100.,
            'freshness':'current','complete':True,'rows':[{'key':'first'},{'key':'second'}],
            'diagnostics':[]},'bindings':{'first':{'id':'a'},'second':{'id':'b'}}}
        c=collector.Collector({},run=lambda *args:first)
        c.refresh_inventory()
        partial={'snapshot':{'schema_version':1,'observed_at':110.,'last_success_at':110.,
            'freshness':'current','complete':False,'rows':[{'key':'first'}],
            'diagnostics':[{'code':'input_unreadable'}]},'bindings':{'first':{'id':'a'}}}
        c.run=lambda *args:partial;c.refresh_inventory()
        rows=c.snapshot()['rows']
        self.assertEqual(len(rows),2)
        self.assertEqual(rows[1]['inventory_freshness'],'stale')
        self.assertEqual(rows[1]['inventory_observed_at'],100.)
        self.assertNotIn('second',c.bindings)
        partial['snapshot']['complete']=True;c.refresh_inventory()
        self.assertEqual([row['key'] for row in c.snapshot()['rows']],['first'])

    def test_actual_http_fixed_reads_mutations_and_socket_ownership(self):
        with tempfile.TemporaryDirectory(prefix='dashboard-socket-') as base:
            path = str(Path(base)/'collector.sock')
            c = collector.Collector({})
            with collector.Server(path, c) as server:
                thread = threading.Thread(target=server.serve_forever)
                thread.start()
                try:
                    self.assertEqual(os.stat(path).st_mode & 0o777, 0o600)
                    for method, route, expected in [('GET','/v1/snapshot',200),('GET','/healthz',200),
                        ('GET','/v1/snapshot?root=/etc',404),('GET','/etc/passwd',404),
                        *[(m,'/v1/snapshot',405) for m in ('POST','PUT','PATCH','DELETE','OPTIONS','TRACE')]]:
                        client = UnixClient(path)
                        client.request(method, route)
                        result = client.getresponse()
                        self.assertEqual(result.status, expected, (method, route))
                        json.loads(result.read());client.close()
                    with self.assertRaises(Exception):
                        collector.socket_path(path)
                finally:
                    server.shutdown();thread.join()


if __name__ == '__main__':
    unittest.main()
