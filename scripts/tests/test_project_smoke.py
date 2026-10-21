#!/usr/bin/env python3
"""Ownership, private-route, race and lifecycle-preservation smoke checks."""
import contextlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import private_apps as app
import project_smoke as smoke
import project_quality_core as q


class Response:
    status=200
    def __init__(self,data):self.data=data
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def read(self,limit):return self.data[:limit]


class Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='gptclaw-smoke-unit-');self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);(self.root/'quality.json').write_text('{}')
        self.contract={'schema_version':1,'project':{'id':'one'},'service':{'health':{'path':'/projects/one/api/health/'}}}
        self.state={'root':str(self.root),'phase':'ready','name':'owned-service','token':'token','operation_id':'activation','port':app.PORTS.start}
        self.calls=[]
        for name,value in [('target',lambda _: (self.root,self.contract)),('locked',lambda _:contextlib.nullcontext()),('state_for',lambda _:self.state),('object_owned',lambda *_:True),('inspect_service',lambda *_:(True,True))]:
            p=patch.object(app,name,value);p.start();self.addCleanup(p.stop)
        p=patch.object(q,'config',return_value={'template':'nextjs@1.1.0'});p.start();self.addCleanup(p.stop)
        p=patch.object(smoke.urllib.request,'build_opener',return_value=self);p.start();self.addCleanup(p.stop)
    def open(self,url,timeout):
        self.calls.append(url)
        if 'api/health' in url:return Response(b'{"status":"ok"}')
        if url.endswith('asset.js'):return Response(b'/* synthetic asset */')
        return Response(b'<main>synthetic</main><script src="/projects/one/asset.js"></script>')
    def test_owned_direct_and_private_ingress_checks(self):
        value=smoke.check(self.root);self.assertEqual(value['state'],'passed');self.assertIn('separate',value['client_acceptance'])
        self.assertTrue(any(':'+str(app.INGRESS_PORT)+'/' in url for url in self.calls))
    def test_unknown_owner_and_port_refused_before_http(self):
        with patch.object(app,'object_owned',return_value=False):
            with self.assertRaises(app.AppError):smoke.check(self.root)
        self.assertFalse(self.calls)
        self.state['port']=80
        with self.assertRaises(app.AppError):smoke.check(self.root)
        self.assertFalse(self.calls)
    def test_untrusted_asset_cannot_change_origin(self):
        original=self.open
        for path in ['https://example.invalid/steal','/projects/one/%2e%2e/two/asset.js']:
            def bad(url,timeout):
                if url.endswith('/projects/one/'):return Response(('<script src="'+path+'"></script>').encode())
                return original(url,timeout)
            self.calls.clear()
            with patch.object(self,'open',side_effect=bad):
                with self.assertRaises(app.AppError):smoke.check(self.root)
            self.assertFalse(any('example.invalid' in url or '%2e' in url for url in self.calls))
    def test_changed_source_cannot_establish_current_acceptance(self):
        original=self.open
        def changed(url,timeout):
            (self.root/'source.txt').write_text(str(len(self.calls)))
            return original(url,timeout)
        with patch.object(self,'open',side_effect=changed):
            with self.assertRaises(app.AppError):smoke.check(self.root)
    def test_failed_post_start_preserves_runtime_and_data(self):
        meta=self.root/'.gptclaw';meta.mkdir();(meta/'quality-smoke.json').write_text(json.dumps({'schema_version':1,'project':'one','enabled':True}))
        with patch.object(smoke,'check',side_effect=app.AppError('health')),patch.object(app,'command') as command:
            self.assertEqual(smoke.after_start(self.root)['state'],'failed');command.assert_not_called()
        self.assertEqual(self.state['phase'],'ready')
    def test_post_start_requires_explicit_opt_in(self):
        with patch.object(smoke,'check') as check:
            self.assertIsNone(smoke.after_start(self.root));check.assert_not_called()

    def test_observer_retries_transient_failure_and_stays_quiet_when_unchanged(self):
        import io
        output=io.StringIO();clock=[0.0]
        def sleep(amount):clock[0]+=amount
        with patch.object(smoke.time,'monotonic',side_effect=lambda:clock[0]),patch.object(smoke.time,'sleep',side_effect=sleep),patch.object(smoke,'check',side_effect=[app.AppError('health'),{'state':'passed','revision':'one'}]) as check,contextlib.redirect_stdout(output):
            self.assertEqual(smoke.observe(self.root,2,.5),0)
            self.assertEqual(check.call_count,2)
        self.assertEqual(len(output.getvalue().splitlines()),1)

    def test_single_failed_probe_returns_failure(self):
        import io
        with patch.object(smoke,'check',side_effect=app.AppError('health')),contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(smoke.observe(self.root,0),1)

    def test_opt_in_preserves_unknown_metadata(self):
        meta=self.root/'.gptclaw';meta.mkdir();path=meta/'quality-smoke.json';path.write_text('{"schema_version":99,"unknown":true}')
        before=path.read_bytes()
        with self.assertRaises(app.AppError):smoke.configure(self.root,True)
        self.assertEqual(path.read_bytes(),before)

    def test_observer_rejects_unbounded_or_invalid_polling(self):
        for seconds,interval in [(28801,1),(1,.1),(-1,1)]:
            with self.assertRaises(app.AppError):smoke.observe(self.root,seconds,interval)


if __name__=='__main__':unittest.main()
