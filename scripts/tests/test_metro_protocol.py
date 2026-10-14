#!/usr/bin/env python3
"""Real loopback probe tests; no Expo, tailnet listener or private credentials."""
import hashlib
import base64
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json
from pathlib import Path
import socket
import sys
import threading
import time
import unittest
from unittest.mock import patch,Mock
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import metro_protocol as protocol
import private_apps as app

HOST='fixture.tail123.ts.net'
ORIGIN='https://'+HOST+':8443'


class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_GET(self):
        if self.headers.get('Upgrade')=='websocket':
            self.send_response(101);self.send_header('Connection','Upgrade');self.send_header('Upgrade','websocket')
            key=self.headers['Sec-WebSocket-Key']
            accept=base64.b64encode(hashlib.sha1((key+'258EAFA5-E914-47DA-95CA-C5AB0DC85B11').encode()).digest()).decode()
            self.send_header('Sec-WebSocket-Accept','wrong' if self.server.bad_accept else accept);self.end_headers()
            try:
                header=self.rfile.read(2)
                if len(header)!=2:return
                mask=self.rfile.read(4);data=self.rfile.read(header[1]&127)
                pong=bytes(b^mask[i%4] for i,b in enumerate(data))
                self.wfile.write(bytes([0x8a,len(pong)])+pong);self.wfile.flush()
            except (BrokenPipeError,ConnectionResetError):pass
            return
        self.server.received=(self.headers.get('Host'),self.headers.get('Expo-Platform'),self.headers.get('X-Forwarded-Proto'))
        payload=self.server.payload
        if self.server.header_delay:time.sleep(self.server.header_delay)
        self.send_response(self.server.status)
        if self.server.declared:self.send_header('Content-Length',str(self.server.declared))
        if self.server.extra_header:self.send_header('Synthetic',self.server.extra_header)
        self.end_headers()
        try:
            if self.server.delay:time.sleep(self.server.delay)
            self.wfile.write(payload)
        except (BrokenPipeError,ConnectionResetError):pass


class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.server=None
        for port in range(18600,18632,2):
            try:self.server=ThreadingHTTPServer(('127.0.0.1',port),Handler);break
            except OSError:continue
        if self.server is None:self.fail('task test range unavailable; no foreign listener changed')
        self.server.daemon_threads=True;self.server.payload=b'ok';self.server.status=200
        self.server.declared=2;self.server.extra_header=None;self.server.delay=0;self.server.header_delay=0;self.server.bad_accept=False
        worker=threading.Thread(target=self.server.serve_forever,daemon=True);worker.start()
        def cleanup():self.server.shutdown();self.server.server_close();worker.join(2)
        self.addCleanup(cleanup)
        self.port=self.server.server_address[1]
    def get(self,**kwargs):return protocol.request(self.port,ORIGIN,'/bundle','android',**kwargs)
    def test_native_size_streamed_without_two_mib_ceiling(self):
        payload=b'x'*(3*1024*1024);self.server.payload=payload;self.server.declared=len(payload)
        result=self.get();self.assertEqual(result['bytes'],len(payload));self.assertEqual(result['sha256'],hashlib.sha256(payload).hexdigest())
        self.assertEqual(self.server.received,(HOST+':8443','android','https'))
    def test_body_ceiling_with_and_without_content_length(self):
        self.server.payload=b'x'*100
        for declared in [100,None]:
            self.server.declared=declared
            with self.subTest(declared=declared),self.assertRaises(app.AppError):self.get(max_bytes=64)
    def test_redirect_and_large_headers_refused(self):
        self.server.status=302
        with self.assertRaises(app.AppError):self.get()
        self.server.status=200;self.server.extra_header='x'*17000
        with self.assertRaises(app.AppError):self.get()
    def test_partial_response_is_not_success(self):
        self.server.declared=200
        with self.assertRaises(app.AppError):self.get()
    def test_deadline_and_invalid_local_target_fail(self):
        with self.assertRaises(app.AppError):self.get(deadline=time.monotonic()-1)
        for invalid in [None,True,{},'https://[malformed']:
            with self.assertRaises(app.AppError):protocol.origin(invalid)
        for port in [80,18601,True]:
            with self.assertRaises(app.AppError):protocol.request(port,ORIGIN,'/','android')
        for path in ['https://foreign/','//foreign/','/\r\nHost: foreign','/with space']:
            with self.assertRaises(app.AppError):protocol.request(self.port,ORIGIN,path,'android')
    def test_proxy_probe_ports_are_explicit_and_never_broaden_direct_probes(self):
        for flag,port in [(True,self.port),(False,self.port+1),(True,80),(1,self.port)]:
            with self.assertRaises(app.AppError):protocol.request(port,ORIGIN,'/','android',via_proxy=flag)
        connection=protocol.http.client.HTTPConnection
        with patch.object(protocol.http.client,'HTTPConnection',side_effect=lambda host,port,**kwargs:connection(host,self.port,**kwargs)):
            result=protocol.request(self.port+1,ORIGIN,'/bundle','android',via_proxy=True)
        self.assertEqual(result['bytes'],2)
        for generation in ['',True,'x'*32,'2'*31]:
            with self.assertRaises(app.AppError):protocol.sample(self.port+1,ORIGIN,time.monotonic()+1,generation)

    def test_json_manifest_targets_and_secret_exclusion(self):
        value={'launchAsset':{'url':ORIGIN+'/entry.bundle?platform=android&dev=true'},'assets':[{'url':ORIGIN+'/assets/icon.png'}]}
        payload=json.dumps(value).encode();self.server.payload=payload;self.server.declared=len(payload)
        result=protocol.request(self.port,ORIGIN,'/','android',max_bytes=1024,manifest=True)
        self.assertEqual(result['targets'],{'bundle':'/entry.bundle?platform=android&dev=true','assets':['/assets/icon.png']})
        self.assertNotIn('manifest',result)
    def test_foreign_loopback_credentials_and_malformed_manifest_urls_block(self):
        for url in ['http://127.0.0.1:8081/entry.bundle','https://foreign.ts.net:8443/entry.bundle',ORIGIN+'//foreign/bundle','https://user@'+HOST+':8443/bundle',ORIGIN+'/bundle?token=synthetic',ORIGIN+'/bundle?%74oken=synthetic',ORIGIN+'/bundle#fragment']:
            value={'launchAsset':{'url':url},'assets':[]}
            with self.subTest(url=url),self.assertRaises(app.AppError):protocol.manifest_targets(value,ORIGIN)
        for value in [None,{'launchAsset':{},'assets':[]},{'launchAsset':{'url':ORIGIN+'/bundle'},'assets':['bad']}]:
            with self.assertRaises(app.AppError):protocol.manifest_targets(value,ORIGIN)
    def test_sample_discards_urls_and_never_claims_native_or_private_acceptance(self):
        manifest={'status':200,'bytes':100,'sha256':'0'*64,
                  'targets':{'bundle':'/entry.bundle?platform=android','assets':['/asset.png?hash=public']}}
        def fake(port,advertised,path,platform,**kwargs):
            if kwargs.get('manifest'):return {**manifest,'targets':{**manifest['targets']}}
            return {'status':200,'bytes':3*1024*1024,'sha256':'1'*64,'platform':platform}
        with patch.object(protocol,'request',side_effect=fake),patch.object(protocol,'websocket',return_value={'status':101,'ping_pong':True}):
            result=protocol.sample(self.port,ORIGIN,time.monotonic()+10)
        self.assertFalse(result['physical_client_verified']);self.assertFalse(result['private_route_verified'])
        self.assertEqual(set(result['native']),{'ios','android'})
        self.assertNotIn('entry.bundle',json.dumps(result));self.assertNotIn('targets',json.dumps(result))
    def test_owned_protocol_probe_uses_session_path_without_query(self):
        generation = 'a'*32
        manifest_paths = []
        def fake(port, advertised, path, platform, **kwargs):
            result = {'status': 200, 'bytes': 3*1024*1024, 'sha256': '1'*64, 'platform': platform}
            if kwargs.get('manifest'):
                manifest_paths.append(path)
                result['targets'] = {'bundle': '/entry.bundle?platform='+platform, 'assets': []}
            return result
        with patch.object(protocol, 'request', side_effect=fake), patch.object(protocol, 'websocket', return_value={'status': 101, 'ping_pong': True}):
            result = protocol.sample(18601, ORIGIN, time.monotonic()+10, generation=generation)
        self.assertEqual(manifest_paths, ['/_gptclaw/metro-session/'+generation]*2)
        self.assertFalse(result['physical_client_verified'])

    def test_real_bounded_websocket_upgrade_and_masked_ping(self):
        for path in ['/message','/hot']:
            result=protocol.websocket(self.port,ORIGIN,path,time.monotonic()+3)
            self.assertEqual(result['status'],101);self.assertTrue(result['ping_pong'])
            self.assertEqual(result['bytes_observed'],8);self.assertNotIn('payload',result)
    def test_wrong_websocket_accept_and_unknown_path_are_rejected(self):
        self.server.bad_accept=True
        with self.assertRaises(app.AppError):protocol.websocket(self.port,ORIGIN,'/hot',time.monotonic()+2)
        with self.assertRaises(app.AppError):protocol.websocket(self.port,ORIGIN,'/debugger',time.monotonic()+2)
    def test_cold_transform_header_wait_uses_callers_bounded_deadline(self):
        self.server.header_delay=.15
        self.assertEqual(self.get(deadline=time.monotonic()+1)['bytes'],2)
        self.server.header_delay=.4
        started=time.monotonic()
        with self.assertRaises(app.AppError):self.get(deadline=started+.1)
        self.assertLess(time.monotonic()-started,.3)

    def test_stalled_body_cannot_extend_deadline(self):
        self.server.delay=.6
        started=time.monotonic()
        with self.assertRaises(app.AppError):self.get(deadline=started+.1)
        self.assertLess(time.monotonic()-started,.4)
    def test_manifest_parse_and_memory_bound(self):
        self.server.payload=b'not json';self.server.declared=len(self.server.payload)
        with self.assertRaises(app.AppError):protocol.request(self.port,ORIGIN,'/','ios',max_bytes=1024,manifest=True)
        with self.assertRaises(app.AppError):protocol.request(self.port,ORIGIN,'/','ios',max_bytes=protocol.MAX_MANIFEST+1,manifest=True)

    def test_private_tls_destination_is_exact_node_origin_and_explicit(self):
        with patch.object(app,'node_identity',return_value=HOST):
            self.assertEqual(protocol.destination(8443,ORIGIN,True,True),(HOST,8443))
            for port,origin,proxy,private in [(8444,ORIGIN,True,True),(8443,ORIGIN,False,True),
                    (8443,'https://foreign.ts.net:8443',True,True),(True,ORIGIN,True,True),
                    (8443,ORIGIN,True,1)]:
                with self.subTest(port=port,origin=origin),self.assertRaises(app.AppError):
                    protocol.destination(port,origin,proxy,private)
            with self.assertRaises(app.AppError):
                protocol.sample(8443,ORIGIN,time.monotonic()+1,via_private=True)

    def test_private_https_stream_uses_default_trust_and_hashes_response(self):
        connection=protocol.http.client.HTTPConnection
        self.server.payload=b'native';self.server.declared=6
        with patch.object(app,'node_identity',return_value=HOST),patch.object(
                protocol.http.client,'HTTPSConnection',
                side_effect=lambda host,port,**kwargs:connection('127.0.0.1',self.port,**kwargs)) as tls:
            result=protocol.request(8443,ORIGIN,'/bundle','android',via_proxy=True,via_private=True)
        self.assertEqual(result['sha256'],hashlib.sha256(b'native').hexdigest())
        args,kwargs=tls.call_args
        self.assertEqual(args,(HOST,8443));self.assertEqual(set(kwargs),{'timeout'})

    def test_private_https_certificate_failure_is_unavailable(self):
        tls=Mock();tls.request.side_effect=protocol.ssl.SSLCertVerificationError('synthetic')
        with patch.object(app,'node_identity',return_value=HOST),patch.object(
                protocol.http.client,'HTTPSConnection',return_value=tls),self.assertRaises(protocol.ProbeError):
            protocol.request(8443,ORIGIN,'/bundle','ios',via_proxy=True,via_private=True)
        tls.close.assert_called_once()

    def test_private_websocket_uses_default_trust_and_exact_sni(self):
        connect=socket.create_connection
        context=Mock();context.wrap_socket.side_effect=protocol.ssl.SSLCertVerificationError('synthetic')
        with patch.object(app,'node_identity',return_value=HOST),patch.object(
                protocol.socket,'create_connection',
                side_effect=lambda target,**kwargs:connect(('127.0.0.1',self.port),**kwargs)) as dial,patch.object(
                protocol.ssl,'create_default_context',return_value=context) as trust,self.assertRaises(protocol.ProbeError):
            protocol.websocket(8443,ORIGIN,'/hot',time.monotonic()+1,via_proxy=True,via_private=True)
        self.assertEqual(dial.call_args.args[0],(HOST,8443))
        trust.assert_called_once_with()
        self.assertEqual(context.wrap_socket.call_args.kwargs,{'server_hostname':HOST})

    def test_private_sample_requires_owned_current_route_before_and_after(self):
        import metro_sessions as sessions,metro_routes as routes
        value={'project':'fixture','generation':'1'*32,'phase':'running','operation_result':'passed',
               'expires_at':time.time()+60,'name':'owned-fixture','token':'2'*32,'origin':ORIGIN}
        for observed,owned in [('pending','owned'),('verified','foreign')]:
            with patch.object(sessions,'receipt_for_root',return_value=(Path('/fixture'),value)),patch.object(
                    sessions,'proxy_receipt',return_value=value),patch.object(sessions,'verify_unit'),patch.object(
                    sessions,'ownership',return_value=owned),patch.object(routes,'observe',return_value={'state':observed}),patch.object(
                    protocol,'sample') as sample,self.assertRaises(app.AppError):
                protocol.private_sample('/fixture',value['generation'])
            sample.assert_not_called()
        with patch.object(sessions,'receipt_for_root',return_value=(Path('/fixture'),value)),patch.object(
                sessions,'proxy_receipt',return_value=value),patch.object(sessions,'verify_unit'),patch.object(
                sessions,'ownership',return_value='owned'),patch.object(routes,'observe',
                side_effect=[{'state':'verified'},{'state':'pending'}]),patch.object(protocol,'sample',return_value={}),self.assertRaises(app.AppError):
            protocol.private_sample('/fixture',value['generation'])

    def test_private_sample_binds_generation_expiry_and_physical_flag(self):
        import metro_sessions as sessions,metro_routes as routes
        value={'project':'fixture','generation':'1'*32,'phase':'running','operation_result':'passed',
               'expires_at':time.time()+30,'name':'owned-fixture','token':'2'*32,'origin':ORIGIN}
        with patch.object(sessions,'receipt_for_root',return_value=(Path('/fixture'),value)),patch.object(
                sessions,'proxy_receipt',return_value=value),patch.object(sessions,'verify_unit'),patch.object(
                sessions,'ownership',return_value='owned'),patch.object(routes,'observe',return_value={'state':'verified'}) as observe,patch.object(
                protocol,'sample',return_value={'physical_client_verified':False,'private_route_verified':True}) as sample:
            evidence=protocol.private_sample('/fixture',value['generation'],300)
        self.assertEqual(observe.call_count,2)
        args,kwargs=sample.call_args
        self.assertEqual(args[:2],(8443,ORIGIN));self.assertEqual(args[3],value['generation'])
        self.assertLessEqual(args[2]-time.monotonic(),30)
        self.assertEqual(kwargs,{'via_private':True})
        self.assertEqual(evidence['generation'],value['generation'])
        self.assertFalse(evidence['physical_client_verified'])
        self.assertTrue(evidence['private_route_verified'])

if __name__=='__main__':unittest.main()
