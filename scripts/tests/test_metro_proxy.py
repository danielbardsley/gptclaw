#!/usr/bin/env python3
"""Real task-owned loopback transport fixtures; no Podman or private routes."""
import asyncio
import base64
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import struct
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import private_apps as app
import metro_proxy as module


class ProxyTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.projects = Path(temporary.name)/'projects'
        self.projects.mkdir()
        mock = patch.object(app, 'PROJECTS', self.projects)
        mock.start()
        self.addCleanup(mock.stop)
        now = time.time()
        self.value = {
            'schema_version': 1, 'adapter': 'metro-v1', 'project': 'fixture',
            'root': str(self.projects/'fixture'), 'canonical_key': '1'*64,
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
        self.proxy = module.Proxy(self.value, lambda: deepcopy(self.value))
        self.seen, self.upstream_tasks = [], set()
        self.response = b'HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nok'
        self.behavior = None
        self.upstream_server = await asyncio.start_server(self.serve, '127.0.0.1', 0)
        self.upstream_port = self.upstream_server.sockets[0].getsockname()[1]
        async def upstream():
            return await asyncio.open_connection('127.0.0.1', self.upstream_port,
                                                 limit=module.MAX_HEADERS+1)
        self.proxy.upstream = upstream
        self.server = await asyncio.start_server(self.proxy.accept, '127.0.0.1', 0,
                                                limit=module.MAX_HEADERS+1)
        self.port = self.server.sockets[0].getsockname()[1]

    async def asyncTearDown(self):
        self.server.close()
        self.upstream_server.close()
        tasks = list(self.proxy.tasks | self.upstream_tasks)
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        await self.server.wait_closed()
        await self.upstream_server.wait_closed()

    async def serve(self, reader, writer):
        task = asyncio.current_task()
        self.upstream_tasks.add(task)
        try:
            raw = await reader.readuntil(b'\r\n\r\n')
            first, headers = module.fields(raw)
            self.seen.append((first, headers))
            if self.behavior:
                await self.behavior(reader, writer, first, headers)
            else:
                writer.write(self.response)
                await writer.drain()
        except (OSError, asyncio.IncompleteReadError):
            pass
        finally:
            await module.close(writer)
            self.upstream_tasks.discard(task)

    async def connect(self, target='/src/index.bundle?platform=android', extra='', method='GET'):
        reader, writer = await asyncio.open_connection('127.0.0.1', self.port)
        writer.write((method+' '+target+' HTTP/1.1\r\nHost: fixture.tail123.ts.net:8443\r\n'
                      +extra+'\r\n').encode())
        await writer.drain()
        return reader, writer

    async def request(self, target='/src/index.bundle?platform=android', extra='', method='GET'):
        reader, writer = await self.connect(target, extra, method)
        try:
            return await asyncio.wait_for(reader.read(), 3)
        finally:
            await module.close(writer)

    async def test_streams_bundle_over_two_mib_with_exact_bytes(self):
        body = b'x'*(3*1024*1024)
        self.response = b'HTTP/1.1 200 OK\r\nContent-Type: application/javascript\r\nContent-Length: '+str(len(body)).encode()+b'\r\n\r\n'+body
        response = await self.request()
        self.assertEqual(hashlib.sha256(response.split(b'\r\n\r\n', 1)[1]).hexdigest(),
                         hashlib.sha256(body).hexdigest())
        self.assertEqual(self.proxy.counters['upstream_bytes'], len(body))

    async def test_backpressure_streams_before_upstream_finishes(self):
        release = asyncio.Event()
        async def behavior(reader, writer, first, headers):
            writer.write(b'HTTP/1.1 200 OK\r\nContent-Length: 4\r\n\r\nab')
            await writer.drain()
            await release.wait()
            writer.write(b'cd')
            await writer.drain()
        self.behavior = behavior
        reader, writer = await self.connect()
        try:
            await asyncio.wait_for(reader.readuntil(b'\r\n\r\n'), 1)
            self.assertEqual(await asyncio.wait_for(reader.readexactly(2), 1), b'ab')
            release.set()
            self.assertEqual(await asyncio.wait_for(reader.read(), 1), b'cd')
        finally:
            release.set()
            await module.close(writer)

    async def test_chunked_and_eof_sources_stream_without_body_rewrite(self):
        for response in [
            b'HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n2\r\nab\r\n2\r\ncd\r\n0\r\n\r\n',
            b'HTTP/1.1 200 OK\r\n\r\nabcd',
        ]:
            self.response = response
            raw = await self.request()
            self.assertTrue(raw.startswith(b'HTTP/1.1 200'))
            chunks = raw.split(b'\r\n\r\n', 1)[1]
            reader = asyncio.StreamReader()
            reader.feed_data(chunks)
            reader.feed_eof()
            decoded = bytearray()
            while True:
                size = int((await reader.readline()).strip(), 16)
                if not size:
                    break
                decoded.extend(await reader.readexactly(size))
                self.assertEqual(await reader.readexactly(2), b'\r\n')
            self.assertEqual(decoded, b'abcd')

    async def test_http_receipt_forces_owned_http_advertisement_and_keeps_entry_guard(self):
        self.value.update(schema_version=2, transport='private-tailnet-http',
                          origin='http://fixture.tail123.ts.net:8443')
        self.proxy.receipt = deepcopy(self.value)
        entry = module.SESSION_PREFIX+self.value['generation']
        response = await self.request(entry, 'X-Forwarded-Proto: https\r\n')
        self.assertTrue(response.startswith(b'HTTP/1.1 200'))
        self.assertEqual(self.seen[-1][1]['x-forwarded-proto'], 'http')
        self.assertTrue((await self.request(module.SESSION_PREFIX+'9'*32)).startswith(b'HTTP/1.1 503'))

    async def test_manifest_requires_exact_current_generation(self):
        for target in ['/', '/?gptclawSession='+'9'*32,
                       '/?gptclawSession='+'2'*32+'&gptclawSession='+'2'*32]:
            self.assertTrue((await self.request(target)).startswith(b'HTTP/1.1 503'))
        self.assertEqual(self.seen, [])
        self.assertTrue((await self.request('/?gptclawSession='+'2'*32,
                                           'Expo-Platform: android\r\n')).startswith(b'HTTP/1.1 200'))

    async def test_session_path_survives_missing_query_and_preserves_sdk_response(self):
        body = b'unchanged-synthetic-signed-manifest'
        self.response = (b'HTTP/1.1 200 OK\r\nContent-Type: multipart/mixed; boundary=fixture\r\n'
                         b'Expo-Signature: synthetic-signature\r\nContent-Length: '
                         + str(len(body)).encode() + b'\r\n\r\n' + body)
        entry = module.SESSION_PREFIX + self.value['generation']
        for ending in ['', '/']:
            for query in ['', '?platform=android']:
                response = await self.request(entry + ending + query, 'Expo-Platform: android\r\n')
                self.assertEqual(response.split(b'\r\n\r\n', 1)[1], body)
                self.assertIn(b'expo-signature: synthetic-signature', response)
                self.assertEqual(self.seen[-1][0], 'GET /' + query + ' HTTP/1.1')
        self.assertEqual(self.proxy.resources['manifest']['responses']['2xx'], 4)

    async def test_old_or_malformed_session_paths_and_unbound_manifest_aliases_reject(self):
        prefix = module.SESSION_PREFIX
        for target in [prefix + '9'*32 + '/', prefix + self.value['generation'] + '//',
                       prefix + self.value['generation'] + '/index.exp',
                       prefix + self.value['generation'] + '/?gptclawSession='+'9'*32,
                       prefix + self.value['generation'] + '/?gptclawSession='+'2'*32+'&gptclawSession='+'2'*32,
                       '/manifest', '/index.exp']:
            with self.subTest(target=target):
                self.assertTrue((await self.request(target)).startswith(b'HTTP/1.1 503'))
        self.assertEqual(self.seen, [])
        self.value['generation'] = '9'*32
        self.assertTrue((await self.request(prefix+'2'*32+'/')).startswith(b'HTTP/1.1 503'))
        self.assertEqual(self.seen, [])

    async def test_foreign_host_origin_credentials_and_absolute_targets_reject(self):
        for extra in ['Host: foreign.ts.net:8443\r\n', 'Origin: https://foreign.example\r\n',
                      'Authorization: synthetic-canary\r\n', 'Cookie: synthetic-canary\r\n']:
            response = await self.request(extra=extra)
            self.assertTrue(response.startswith(b'HTTP/1.1 503'))
            self.assertNotIn(b'synthetic-canary', response)
        for target in ['https://foreign.example/a', '//foreign.example/a',
                       '/assets/../secret', '/assets/%2e%2e/secret',
                       '/assets/.env', '/assets/%252eenv', '/x?%74oken=canary']:
            self.assertTrue((await self.request(target)).startswith(b'HTTP/1.1 503'))
        self.assertEqual(self.seen, [])

    async def test_transport_diagnostics_preserve_health_and_expose_no_request_identity(self):
        await self.request('/?gptclawSession='+'9'*32)
        await self.request('/?gptclawSession='+self.value['generation'],
                           'Authorization: Bearer synthetic-private-canary\r\n')
        response=await self.request('/_gptclaw/metro-transport')
        self.assertTrue(response.startswith(b'HTTP/1.1 200'))
        payload=json.loads(response.split(b'\r\n\r\n',1)[1])
        self.assertEqual(payload['generation'],self.value['generation'])
        self.assertEqual(payload['rejections']['stale-launch'],1)
        self.assertEqual(payload['rejections']['credential-header'],1)
        self.assertEqual(payload['native_client_acceptance'],'unverified')
        self.assertEqual(set(payload['capacity']),{'active','native','pending_headers','websockets','limit'})
        self.assertEqual(payload['capacity']['limit'],8)
        self.assertNotIn('synthetic-private-canary',response.decode())
        self.assertNotIn('authorization',response.decode().lower())
        self.assertEqual(set(payload['rejections']),module.REJECTION_CODES)
        self.assertEqual(self.seen,[])
        health=await self.request('/_gptclaw/metro-health')
        actual=json.loads(health.split(b'\r\n\r\n',1)[1])
        self.assertEqual(actual,{'adapter':'metro-v1','project':'fixture',
            'generation':self.value['generation'],'expires_at':self.value['expires_at']})

    async def test_transport_resource_counts_distinguish_backend_status_without_paths(self):
        self.response=b'HTTP/1.1 500 Internal Error\r\nContent-Length: 0\r\n\r\n'
        await self.request('/?gptclawSession='+self.value['generation'])
        self.response=b'HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nok'
        await self.request('/src/private-synthetic-canary.bundle?platform=android')
        value=self.proxy.diagnostics()
        self.assertEqual(value['resources']['manifest']['responses']['5xx'],1)
        self.assertEqual(value['resources']['bundle']['responses']['2xx'],1)
        self.assertEqual(value['resources']['bundle']['requests'],1)
        self.assertNotIn('private-synthetic-canary',json.dumps(value))
        self.assertNotIn('platform=android',json.dumps(value))

    async def test_diagnostic_counters_saturate_and_unknown_reasons_cannot_add_fields(self):
        self.proxy.counters['upstream_bytes']=module.MAX_COUNTER-1
        self.proxy.count('upstream_bytes',65536)
        self.proxy.reject('untrusted-request-canary')
        self.assertEqual(self.proxy.counters['upstream_bytes'],module.MAX_COUNTER)
        self.assertEqual(self.proxy.rejections['other'],1)
        self.assertNotIn('untrusted-request-canary',json.dumps(self.proxy.diagnostics()))
        self.value['phase']='stopping'
        self.assertTrue((await self.request('/_gptclaw/metro-transport')).startswith(b'HTTP/1.1 503'))

    async def test_forwarded_headers_are_fixed_and_identity_headers_are_discarded(self):
        await self.request(extra='X-Forwarded-Proto: http\r\nX-Forwarded-Host: foreign.example\r\n'
                                'Tailscale-User-Login: synthetic-identity\r\nAccept-Encoding: gzip\r\n'
                                'Expo-Platform: ios\r\nExpo-Expect-Signature: keyid="main"\r\n')
        headers = self.seen[0][1]
        self.assertEqual(headers['host'], 'fixture.tail123.ts.net:8443')
        self.assertEqual(headers['x-forwarded-proto'], 'https')
        self.assertEqual(headers['accept-encoding'], 'identity')
        self.assertEqual(headers['expo-platform'], 'ios')
        self.assertEqual(headers['expo-expect-signature'], 'keyid="main"')
        self.assertNotIn('tailscale-user-login', headers)
        self.assertNotIn('x-forwarded-host', headers)

    async def test_header_and_request_body_bounds_precede_upstream(self):
        for extra in ['X-Large: '+'x'*module.MAX_HEADERS+'\r\n',
                      'Content-Length: 1\r\n', 'Transfer-Encoding: chunked\r\n',
                      'Expect: 100-continue\r\n']:
            self.assertTrue((await self.request(extra=extra)).startswith(b'HTTP/1.1 503'))
        self.assertTrue((await self.request('/symbolicate',
                                           'Content-Length: 65537\r\n', 'POST')).startswith(b'HTTP/1.1 503'))
        self.assertEqual(self.seen, [])

    async def test_response_redirect_encoding_and_size_declarations_reject(self):
        for headers in [
            'Location: https://foreign.example\r\n', 'Content-Encoding: gzip\r\n',
            'Content-Length: '+str(module.MAX_BODY+1)+'\r\n',
            'Content-Length: 2\r\nTransfer-Encoding: chunked\r\n',
        ]:
            self.response = ('HTTP/1.1 200 OK\r\n'+headers+'\r\n').encode()
            self.assertTrue((await self.request()).startswith(b'HTTP/1.1 503'))

    async def test_chunked_overflow_truncation_and_trailers_do_not_complete(self):
        with patch.object(module, 'MAX_BODY', 16):
            for body in [b'11\r\n' + b'x'*17 + b'\r\n0\r\n\r\n',
                         b'2\r\na', b'0\r\nX-Secret: synthetic-canary\r\n\r\n']:
                self.response = b'HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n'+body
                response = await self.request()
                self.assertNotIn(b'synthetic-canary', response)
                self.assertFalse(response.endswith(b'0\r\n\r\n'))
        self.assertEqual(self.proxy.counters['upstream_bytes'], 1)

    async def test_changed_stale_or_inactive_receipt_cannot_route(self):
        original = deepcopy(self.value)
        for key, value in [('generation', '9'*32), ('root', str(self.projects/'foreign')),
                           ('phase', 'stopping'), ('operation_result', 'unknown')]:
            self.value = deepcopy(original)
            self.value[key] = value
            self.assertTrue((await self.request()).startswith(b'HTTP/1.1 503'))
        self.value = deepcopy(original)
        self.value['observations']['process']['observed_at'] = time.time()-31
        self.value['started_at'] = time.time()-40
        self.assertTrue((await self.request()).startswith(b'HTTP/1.1 503'))
        self.assertEqual(self.seen, [])

    async def test_health_is_bound_metadata_without_sdk_or_native_acceptance_claim(self):
        response = await self.request('/_gptclaw/metro-health')
        self.assertTrue(response.startswith(b'HTTP/1.1 200'))
        self.assertIn(('2'*32).encode(), response)
        self.assertNotIn(('3'*32).encode(), response)
        self.assertNotIn(b'phone', response)
        self.assertNotIn(b'ready', response)
        self.assertEqual(self.seen, [])

    async def test_expiry_closes_stalled_transfer(self):
        self.value['expires_at'] = time.time()+.15
        self.proxy.receipt['expires_at'] = self.value['expires_at']
        async def behavior(reader, writer, first, headers):
            writer.write(b'HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\na')
            await writer.drain()
            await asyncio.sleep(2)
        self.behavior = behavior
        response = await self.request()
        self.assertTrue(response.endswith(b'\r\n\r\na'))

    async def test_eight_connections_bound_independent_session_capacity(self):
        clients = [await asyncio.open_connection('127.0.0.1', self.port)
                   for _ in range(module.MAX_CONNECTIONS)]
        await asyncio.sleep(.03)
        self.assertEqual(len(self.proxy.connections), module.MAX_CONNECTIONS)
        try:
            try:
                response = await self.request()
                self.assertTrue(response.startswith(b'HTTP/1.1 503'))
            except ConnectionResetError:
                # Immediate capacity rejection may reset an unread request.
                self.assertGreaterEqual(self.proxy.counters['rejected'], 1)
            self.assertEqual(self.seen, [])
        finally:
            for _, writer in clients:
                await module.close(writer)

    async def test_idle_header_sockets_cannot_starve_current_health(self):
        clients = [await asyncio.open_connection('127.0.0.1', self.port)
                   for _ in range(module.MAX_CONNECTIONS)]
        await asyncio.sleep(.03)
        self.assertEqual(len(self.proxy.header_tasks), module.MAX_CONNECTIONS)
        try:
            with patch.object(module, 'HEADER_RECLAIM_SECONDS', 0):
                response = await self.request('/_gptclaw/metro-health')
            self.assertTrue(response.startswith(b'HTTP/1.1 200'))
            self.assertLessEqual(len(self.proxy.connections), module.MAX_CONNECTIONS)
            self.assertEqual(self.seen, [])
            closed = sum(reader.at_eof() for reader, _ in clients)
            self.assertGreaterEqual(closed, 1)
        finally:
            for _, writer in clients:
                await module.close(writer)

    async def test_native_saturation_keeps_health_within_eight_total_slots(self):
        release = asyncio.Event()
        async def behavior(reader, writer, first, headers):
            await release.wait()
            writer.write(self.response)
            await writer.drain()
        self.behavior = behavior
        clients = [await self.connect('/status')
                   for _ in range(module.MAX_NATIVE_CONNECTIONS)]
        try:
            for _ in range(100):
                if len(self.proxy.native_connections) == module.MAX_NATIVE_CONNECTIONS:
                    break
                await asyncio.sleep(.01)
            self.assertEqual(len(self.proxy.native_connections), 7)
            response = await self.request('/_gptclaw/metro-health')
            self.assertTrue(response.startswith(b'HTTP/1.1 200'))
            self.assertEqual(json.loads(response.split(b'\r\n\r\n', 1)[1])['generation'],
                             self.value['generation'])
            self.assertLessEqual(len(self.proxy.connections), module.MAX_CONNECTIONS)
            self.assertTrue((await self.request('/status')).startswith(b'HTTP/1.1 503'))
            self.assertEqual(len(self.seen), module.MAX_NATIVE_CONNECTIONS)
        finally:
            release.set()
            for _, writer in clients:
                await module.close(writer)
        for _ in range(100):
            if not self.proxy.native_connections:
                break
            await asyncio.sleep(.01)
        self.assertEqual(self.proxy.native_connections, set())

    async def websocket_connect(self):
        key = base64.b64encode(b'0123456789abcdef').decode()
        reader, writer = await self.connect('/hot', 'Connection: Upgrade\r\nUpgrade: websocket\r\n'
                                            'Sec-WebSocket-Version: 13\r\nSec-WebSocket-Key: '+key+'\r\n')
        response = await asyncio.wait_for(reader.readuntil(b'\r\n\r\n'), 1)
        return reader, writer, response

    async def websocket_server(self, reader, writer, first, headers):
        accept = base64.b64encode(hashlib.sha1((headers['sec-websocket-key']+
                    '258EAFA5-E914-47DA-95CA-C5AB0DC85B11').encode()).digest())
        writer.write(b'HTTP/1.1 101 Switching Protocols\r\nConnection: Upgrade\r\n'
                     b'Upgrade: websocket\r\nSec-WebSocket-Accept: '+accept+b'\r\n\r\n')
        await writer.drain()
        await self.ws_behavior(reader, writer)

    async def test_websocket_reconnect_pressure_preserves_manifest_and_health_capacity(self):
        release = asyncio.Event()
        async def hold(reader, writer):
            await release.wait()
        self.ws_behavior = hold
        self.behavior = self.websocket_server
        clients = [await self.websocket_connect() for _ in range(module.MAX_WEBSOCKETS)]
        try:
            self.assertEqual(len(self.proxy.websockets), 4)
            reader, writer, response = await self.websocket_connect()
            try:
                self.assertTrue(response.startswith(b'HTTP/1.1 503'))
            finally:
                await module.close(writer)
            self.assertEqual(len(self.proxy.websockets), 4)
            self.behavior = None
            entry = module.SESSION_PREFIX+self.value['generation']
            self.assertTrue((await self.request(entry)).startswith(b'HTTP/1.1 200'))
            self.assertTrue((await self.request('/_gptclaw/metro-health')).startswith(b'HTTP/1.1 200'))
            self.assertLessEqual(len(self.proxy.connections), module.MAX_CONNECTIONS)
        finally:
            release.set()
            for _, writer, _ in clients:
                await module.close(writer)
        for _ in range(100):
            if not self.proxy.websockets:
                break
            await asyncio.sleep(.01)
        self.assertEqual(self.proxy.websockets, set())

    async def test_websocket_masked_ping_and_fragmented_reload_frames_roundtrip(self):
        async def behavior(reader, writer):
            frame = await reader.readexactly(10)
            mask = frame[2:6]
            self.assertEqual(bytes(c ^ mask[i % 4] for i, c in enumerate(frame[6:])), b'ping')
            writer.write(b'\x8a\x04ping'+b'\x01\x02ab'+b'\x80\x02cd')
            await writer.drain()
            await reader.read()
        self.ws_behavior = behavior
        self.behavior = self.websocket_server
        reader, writer, response = await self.websocket_connect()
        self.assertTrue(response.startswith(b'HTTP/1.1 101'))
        mask = b'abcd'
        writer.write(b'\x89\x84'+mask+bytes(c ^ mask[i % 4] for i, c in enumerate(b'ping')))
        await writer.drain()
        self.assertEqual(await asyncio.wait_for(reader.readexactly(14), 1),
                         b'\x8a\x04ping\x01\x02ab\x80\x02cd')
        await module.close(writer)

    async def test_malformed_or_oversized_websocket_frame_never_reaches_sdk(self):
        received = []
        async def behavior(reader, writer):
            received.append(await reader.read())
        self.ws_behavior = behavior
        self.behavior = self.websocket_server
        for frame in [b'\x81\x01x', b'\x81\xff'+struct.pack('!Q', module.MAX_BODY+1),
                      b'\x09\x80abcd', b'\x80\x80abcd']:
            reader, writer, response = await self.websocket_connect()
            self.assertTrue(response.startswith(b'HTTP/1.1 101'))
            writer.write(frame)
            await writer.drain()
            self.assertEqual(await asyncio.wait_for(reader.read(), 1), b'')
            await module.close(writer)
        await asyncio.sleep(.03)
        self.assertEqual(received, [b'']*4)

    async def test_session_change_closes_existing_websocket(self):
        async def behavior(reader, writer):
            await reader.read()
        self.ws_behavior = behavior
        self.behavior = self.websocket_server
        reader, writer, _ = await self.websocket_connect()
        self.value['phase'] = 'stopping'
        writer.write(b'\x89\x80abcd')
        await writer.drain()
        self.assertEqual(await asyncio.wait_for(reader.read(), 1), b'')
        await module.close(writer)

    async def test_http_deadline_bounds_slow_chunk_headers(self):
        async def behavior(reader, writer, first, headers):
            writer.write(b'HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n')
            await writer.drain()
            await asyncio.sleep(.4)
            writer.write(b'0\r\n\r\n')
            await writer.drain()
        self.behavior = behavior
        with patch.object(module, 'HTTP_SECONDS', .1):
            begin = time.monotonic()
            response = await self.request()
        self.assertLess(time.monotonic()-begin, .35)
        self.assertFalse(response.endswith(b'0\r\n\r\n'))

    async def test_stop_closes_partial_requests_and_releases_listener(self):
        original = module.asyncio.start_server
        async def bind(callback, host, port, **kwargs):
            self.assertEqual((host, port), ('127.0.0.1', 18601))
            return await original(callback, host, 0, **kwargs)
        service = module.Service(self.value, lambda: deepcopy(self.value))
        with patch.object(module.asyncio, 'start_server', side_effect=bind):
            service.start()
        port = service.proxy.server.sockets[0].getsockname()[1]
        reader, writer = await asyncio.open_connection('127.0.0.1', port)
        try:
            writer.write(b'GET /hot HTTP/1.1\r\n')
            await writer.drain()
            await asyncio.sleep(.03)
            await asyncio.to_thread(service.stop)
            self.assertEqual(await asyncio.wait_for(reader.read(), 1), b'')
            self.assertFalse(service.thread.is_alive())
            with self.assertRaises(OSError):
                await asyncio.open_connection('127.0.0.1', port)
        finally:
            await module.close(writer)

    async def test_expiry_cancels_stalled_upstream_before_headers(self):
        entered = asyncio.Event()
        async def behavior(reader, writer, first, headers):
            entered.set()
            await reader.read()
        self.behavior = behavior
        self.value['expires_at'] = time.time()+.5
        self.proxy.receipt['expires_at'] = self.value['expires_at']
        reader, writer = await self.connect()
        try:
            await asyncio.wait_for(entered.wait(), 1)
            response = await asyncio.wait_for(reader.read(), 1)
            self.assertNotIn(b'200 OK', response)
            self.assertEqual(self.proxy.counters['upstream_bytes'], 0)
        finally:
            await module.close(writer)

    async def test_service_bind_failure_is_terminal_without_fallback_or_route(self):
        service = module.Service(self.value, lambda: self.value)
        with patch.object(module.asyncio, 'start_server', side_effect=OSError('synthetic collision')) as bind:
            with self.assertRaises(app.AppError):
                service.start()
        self.assertFalse(service.thread.is_alive())
        self.assertEqual(bind.call_args.args[1:3], ('127.0.0.1', 18601))


if __name__ == '__main__':
    unittest.main()
