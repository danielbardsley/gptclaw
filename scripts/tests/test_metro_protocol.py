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
from unittest.mock import patch
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
        self.server.declared=2;self.server.extra_header=None;self.server.delay=0;self.server.bad_accept=False
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
    def test_real_bounded_websocket_upgrade_and_masked_ping(self):
        for path in ['/message','/hot']:
            result=protocol.websocket(self.port,ORIGIN,path,time.monotonic()+3)
            self.assertEqual(result['status'],101);self.assertTrue(result['ping_pong'])
            self.assertEqual(result['bytes_observed'],8);self.assertNotIn('payload',result)
    def test_wrong_websocket_accept_and_unknown_path_are_rejected(self):
        self.server.bad_accept=True
        with self.assertRaises(app.AppError):protocol.websocket(self.port,ORIGIN,'/hot',time.monotonic()+2)
        with self.assertRaises(app.AppError):protocol.websocket(self.port,ORIGIN,'/debugger',time.monotonic()+2)
    def test_stalled_body_cannot_extend_deadline(self):
        self.server.delay=.6
        started=time.monotonic()
        with self.assertRaises(app.AppError):self.get(deadline=started+.1)
        self.assertLess(time.monotonic()-started,.4)
    def test_manifest_parse_and_memory_bound(self):
        self.server.payload=b'not json';self.server.declared=len(self.server.payload)
        with self.assertRaises(app.AppError):protocol.request(self.port,ORIGIN,'/','ios',max_bytes=1024,manifest=True)
        with self.assertRaises(app.AppError):protocol.request(self.port,ORIGIN,'/','ios',max_bytes=protocol.MAX_MANIFEST+1,manifest=True)

if __name__=='__main__':unittest.main()
