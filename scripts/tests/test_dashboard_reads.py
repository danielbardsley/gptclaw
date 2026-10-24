"""Byte integrity, scoped native snapshots and persistent fixed read-only queries."""
import http.server
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dashboard_observation as reads
import private_apps as app
import project_dependencies as deps
import project_database as db


class TrustedTests(unittest.TestCase):
    def test_exact_bytes_membership_and_copy_isolation(self):
        with tempfile.TemporaryDirectory(prefix='trusted-dashboard-') as temp:
            root = Path(temp)
            (root/'config/templates').mkdir(parents=True)
            (root/'config/toolchains').mkdir()
            source = root/'config/templates/v1.json'
            source.write_text('{"value":1}')
            calls = []
            def loader():
                calls.append(True)
                return deps.json_data(deps.read_bytes(source))
            with patch.object(app, 'REPO', root):
                cache = reads.CatalogueCache(loader)
                self.assertTrue(cache.unchanged())
                cache.get(loader)['value'] = 99
                self.assertEqual(cache.get(loader), {'value': 1})
                self.assertEqual(len(calls), 1)
                old = source.stat()
                source.write_text('{"value":2}')
                os.utime(source, ns=(old.st_atime_ns, old.st_mtime_ns))
                self.assertFalse(cache.unchanged())
                self.assertEqual(cache.get(loader), {'value': 2})
                self.assertEqual(len(calls), 2)
                source.write_text('{"value":1}')
                (source.parent/'v2.json').write_text('{}')
                self.assertFalse(cache.unchanged())

    def test_manifest_parse_cache_tracks_exact_text_and_does_not_cross_reads(self):
        import project_manifest as manifests
        text = 'schema_version: 1\nproject: {id: example}\n'
        with patch.object(manifests, 'parse_manifest', wraps=manifests.parse_manifest) as parse:
            with reads.cached_reads():
                manifests.parse_manifest(text)['schema_version'] = 99
                self.assertEqual(manifests.parse_manifest(text)['schema_version'], 1)
                self.assertEqual(manifests.parse_manifest(text.replace(': 1', ': 2'))['schema_version'], 2)
                self.assertEqual(parse.call_count, 2)
            with reads.cached_reads(): manifests.parse_manifest(text)
            self.assertEqual(parse.call_count, 3)

    def test_symlinks_and_hardlinks_cannot_reuse_a_validation(self):
        with tempfile.TemporaryDirectory(prefix='trusted-links-') as temp:
            root = Path(temp)
            (root/'config/templates').mkdir(parents=True)
            (root/'config/toolchains').mkdir()
            source = root/'config/templates/v1.json'; source.write_text('{}')
            def loader(): return deps.json_data(deps.read_bytes(source))
            with patch.object(app, 'REPO', root):
                cache = reads.CatalogueCache(loader)
                other = root/'other.json'; other.write_text('{}')
                source.unlink(); source.symlink_to(other)
                self.assertFalse(cache.unchanged())
                with self.assertRaises(app.AppError): cache.get(loader)
                source.unlink(); os.link(other, source)
                self.assertFalse(cache.unchanged())
                with self.assertRaises(app.AppError): cache.get(loader)


class HttpTests(unittest.TestCase):
    def test_http_never_follows_redirects_or_uses_proxy_or_tls(self):
        paths = []
        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, *_): pass
            def do_GET(self):
                paths.append(self.path)
                self.send_response(302 if self.path == '/redirect' else 200)
                self.send_header('Location', 'https://untrusted.invalid/')
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.end_headers()
        server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever); thread.start()
        try:
            with patch.dict(os.environ, {'http_proxy': 'http://untrusted.invalid:1'}), \
                 patch('ssl.create_default_context', side_effect=AssertionError('TLS startup')):
                self.assertTrue(reads.http_probe(server.server_port, '/ready', .5, html=True))
                self.assertFalse(reads.http_probe(server.server_port, '/redirect', .5))
                self.assertEqual(paths, ['/ready', '/redirect'])
        finally:
            server.shutdown(); server.server_close(); thread.join()


class NativeTests(unittest.TestCase):
    def test_exact_names_freshness_and_property_allowlist(self):
        name = 'gptclaw-app-example'
        value = {'at':time.time(),'names':[name], 'containers':{name:{'Id':'a'*64}},
                 'network_names':[], 'networks':[], 'globals':{},
                 'units':{name+'.service':{'ActiveState':'active','SourcePath':'owned','DropInPaths':''}}}
        self.assertEqual(reads.native_read(value, ['podman','container','exists',name]).returncode, 0)
        self.assertIsNone(reads.native_read(value, ['podman','container','exists','unrelated']))
        self.assertIsNone(reads.native_read(value, ['podman','stop',name]))
        self.assertIsNone(reads.native_read(value, ['systemctl','--user','show',name+'.service','-p','Environment']))
        value['at'] -= 11
        self.assertIsNone(reads.native_read(value, ['podman','container','exists',name]))

    def test_batch_is_scoped_and_inspection_omits_environment(self):
        with tempfile.TemporaryDirectory(prefix='native-dashboard-') as temp:
            root = Path(temp); info = root.stat()
            binding = {'root':str(root),'id':'example','identity':(info.st_dev,info.st_ino,info.st_uid),'components':['web']}
            calls=[]
            name='gptclaw-app-example'
            def command(argv, **_):
                calls.append(argv)
                if argv[:2] == ['podman','ps']: output=name+'\n'
                elif argv[:3] == ['podman','container','inspect']:
                    output=json.dumps([{'Name':name,'Id':'a'*64,'Config':{'Labels':{app.LABEL:'b'*32}}}])
                elif argv[:3] == ['systemctl','--user','show']:
                    output='Id='+name+'.service\nSourcePath=owned\nDropInPaths=\nActiveState=active\n'
                else: output='{}'
                return subprocess.CompletedProcess(argv,0,output,'')
            with patch.object(app,'command',side_effect=command): result=reads.native_job([binding])
            self.assertEqual(set(result['containers']),{name})
            inspect=next(argv for argv in calls if argv[:3]==['podman','container','inspect'])
            self.assertNotIn('.Env',inspect[-1]); self.assertNotIn('.Mounts',inspect[-1])
            self.assertIn('name=^(gptclaw\\-app\\-example|gptclaw\\-app\\-example\\-job)$',calls[0])
            self.assertNotIn('SYNTHETIC_SECRET',json.dumps(result))


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.receipt={'project':'example','root':'/synthetic/example','active':'a'*32,'epoch':'b'*32,'token':'c'*32}
        self.started=[]
        self.script="import sys\nfor line in sys.stdin:\n if line.startswith('SELECT '):\n  assert line.strip()=='SELECT version_num FROM public.alembic_version;'; print('0001',flush=True)\n elif line.startswith('\\\\echo '): print(line.split(' ',1)[1].strip(),flush=True)\n"
        def start(argv, **kwargs):
            self.started.append(argv)
            return subprocess.Popen([sys.executable,'-u','-c',self.script],**kwargs)
        self.pool=reads.DatabaseReaders(start=start);self.addCleanup(self.pool.close)
        p=patch.object(db,'client',return_value=['podman','exec','--interactive','container','psql']);p.start();self.addCleanup(p.stop)

    def test_reuses_authenticated_session_and_closes_on_idle(self):
        first=self.pool.revision(self.receipt,'d'*64)
        second=self.pool.revision(self.receipt,'d'*64)
        self.assertEqual(first.get('revision'),'0001');self.assertEqual(second.get('revision'),'0001')
        self.assertEqual(len(self.started),1)
        process=next(iter(self.pool.readers.values()))
        self.pool.close();self.assertIsNotNone(process.poll());self.assertEqual(self.pool.readers,{})
        self.assertEqual(self.pool.revision(self.receipt,'d'*64).get('revision'),'0001')
        self.assertEqual(len(self.started),2)
        self.pool.close(shutdown=True)
        self.assertIn('error',self.pool.revision(self.receipt,'d'*64))

    def test_client_start_failure_returns_only_a_fixed_project_failure(self):
        with patch.object(self.pool,'start',side_effect=OSError('SYNTHETIC_SECRET')):
            value=self.pool.revision(self.receipt,'d'*64)
        self.assertIn('error',value)
        self.assertNotIn('SYNTHETIC_SECRET',json.dumps(value))
        self.assertEqual(self.pool.readers,{})

    def test_generation_and_credential_epoch_change_session_identity(self):
        key=self.pool.key(self.receipt,'d'*64)
        self.assertNotEqual(key,self.pool.key(self.receipt,'e'*64))
        self.assertNotEqual(key,self.pool.key({**self.receipt,'epoch':'e'*32},'d'*64))

    def test_sampling_caps_sessions_and_retires_replaced_generations(self):
        with tempfile.TemporaryDirectory(prefix='database-readers-') as temp:
            root=Path(temp);info=root.stat();bindings={};receipts={};native={'at':time.time(),'containers':{}}
            for index in range(9):
                slug='example-'+str(index)
                receipt={**self.receipt,'project':slug,'root':str(root),'blocked':False,'operation':None}
                receipts[slug]=receipt
                bindings[slug]={'root':str(root),'id':slug,'identity':(info.st_dev,info.st_ino,info.st_uid),'components':['api','db']}
                native['containers'][db.name(receipt)]={'Id':'d'*64,'State':{'Running':True},'Config':{'Labels':{app.LABEL:receipt['token']}}}
            with patch.object(db,'state',side_effect=lambda slug,_:receipts[slug]), \
                 patch.object(db,'verify_unit'),patch.object(reads,'verify_database_container'):
                self.pool.sample(bindings,native)
                self.assertEqual(len(self.pool.readers),8)
                self.assertEqual(len(native['database']),8)
                missing=next(r for r in receipts.values() if db.name(r) not in native['database'])
                with patch.object(db,'sql',return_value='0001\n') as sql:
                    with reads.cached_reads(native=native):self.assertEqual(db.revision(missing),'0001')
                    sql.assert_called_once()
                receipt=receipts['example-0'];key=self.pool.key(receipt,'d'*64)
                old=self.pool.readers[key]
                receipt['epoch']='e'*32
                self.pool.sample(bindings,native)
                self.assertIsNotNone(old.poll())
                self.assertNotIn(key,self.pool.readers)
                self.assertEqual(len(self.pool.readers),8)

    def test_oversized_query_output_is_not_exposed_and_reader_is_discarded(self):
        self.script="print('SYNTHETIC_SECRET'*30,flush=True)"
        value=self.pool.revision(self.receipt,'d'*64)
        self.assertIn('error',value)
        self.assertNotIn('SYNTHETIC_SECRET',json.dumps(value))
        self.assertEqual(self.pool.readers,{})

    def test_query_timeout_is_bounded_and_reaps_owned_process(self):
        self.script='import time; time.sleep(10)'
        start=time.monotonic();value=self.pool.revision(self.receipt,'d'*64)
        self.assertLess(time.monotonic()-start,1.6)
        self.assertIn('error',value);self.assertNotIn('revision',value);self.assertEqual(self.pool.readers,{})

    def test_wrong_instance_or_expired_query_cannot_report_healthy(self):
        name=db.name(self.receipt)
        proof={'key':self.pool.key(self.receipt,'e'*64),'at':time.time(),'revision':'0001'}
        native={'at':time.time(),'containers':{name:{'Id':'d'*64}},'database':{name:proof}}
        with reads.cached_reads(native=native),self.assertRaises(app.AppError):db.revision(self.receipt)
        proof.update(key=self.pool.key(self.receipt,'d'*64),at=time.time()-11)
        with reads.cached_reads(native=native),self.assertRaises(app.AppError):db.revision(self.receipt)


if __name__ == '__main__': unittest.main()
