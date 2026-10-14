"""Bounded origin-root Metro transport. No route administration or request logs."""
import asyncio
import base64
from copy import deepcopy
import hashlib
import json
import re
import threading
import time
from urllib.parse import parse_qsl, unquote, urlsplit

import private_apps as app
import metro_state as states

MAX_HEADERS = 16384
MAX_BODY = 64 * 1024 * 1024
MAX_REQUEST = 65536
MAX_CONNECTIONS = 8
CHUNK = 65536
IDLE_SECONDS = 60
HTTP_SECONDS = 120
REQUEST_HEADERS = {
    'accept', 'content-type', 'user-agent', 'if-none-match', 'if-modified-since',
    'expo-platform', 'expo-protocol-version', 'expo-runtime-version',
    'expo-expect-signature', 'expo-updates-environment',
}
RESPONSE_HEADERS = {
    'content-type', 'cache-control', 'etag', 'last-modified', 'vary',
    'expo-protocol-version', 'expo-sfv-version', 'expo-signature',
}
BINDING = (
    'project', 'root', 'canonical_key', 'generation', 'token', 'image',
    'input_digest', 'policy_digest', 'unit_digest', 'metro_port',
    'proxy_port', 'origin', 'started_at', 'expires_at',
)


class TransportError(Exception):
    """A fixed code only; never retain a request, header, URL or response body."""
    def __init__(self, code):
        super().__init__(code)
        self.code = code


def require(ok, code='invalid-request'):
    if not ok:
        raise TransportError(code)


def path(value, generation):
    require(isinstance(value, str) and 0 < len(value) <= 8192
            and all(32 < ord(c) < 127 for c in value))
    parsed = urlsplit(value)
    require(not parsed.scheme and not parsed.netloc and not parsed.fragment
            and parsed.path.startswith('/') and not parsed.path.startswith('//')
            and len(parsed.query) <= 4096)
    require(not re.search(r'%(?![0-9a-fA-F]{2})', parsed.path))
    decoded = unquote(parsed.path, errors='strict')
    require('\\' not in decoded and '%' not in decoded
            and all(32 <= ord(c) < 127 for c in decoded)
            and all(not part.startswith('.') for part in decoded.split('/')))
    try:
        query = parse_qsl(parsed.query, keep_blank_values=True, max_num_fields=64)
    except ValueError:
        raise TransportError('invalid-request') from None
    require(all(k.lower() not in {
        'token', 'access_token', 'auth', 'authorization', 'password', 'secret', 'key'
    } for k, _ in query))
    launches = [v for k, v in query if k == 'gptclawSession']
    if parsed.path == '/':
        require(launches == [generation], 'stale-launch')
    elif launches:
        require(launches == [generation], 'stale-launch')
    return parsed


def fields(raw):
    require(len(raw) <= MAX_HEADERS and raw.endswith(b'\r\n\r\n'), 'header-bound')
    lines = raw[:-4].split(b'\r\n')
    require(lines and len(lines[0]) <= 8192)
    headers = {}
    for line in lines[1:]:
        require(b':' in line and not line.startswith((b' ', b'\t')))
        name, value = line.split(b':', 1)
        require(re.fullmatch(rb"[!#$%&'*+.^_\x60|~0-9A-Za-z-]+", name))
        require(all(32 <= c < 127 for c in value))
        key = name.decode('ascii').lower()
        require(key not in headers, 'duplicate-header')
        headers[key] = value.decode('ascii').strip()
    return lines[0].decode('ascii'), headers


async def read_headers(reader, timeout):
    try:
        raw = await asyncio.wait_for(reader.readuntil(b'\r\n\r\n'), timeout)
    except (asyncio.LimitOverrunError, asyncio.IncompleteReadError):
        raise TransportError('header-bound') from None
    return fields(raw)


def length(value, maximum):
    require(isinstance(value, str) and re.fullmatch('[0-9]{1,12}', value))
    number = int(value)
    require(number <= maximum, 'body-bound')
    return number


async def write(writer, data, timeout):
    writer.write(data)
    await asyncio.wait_for(writer.drain(), timeout)


async def close(writer):
    writer.close()
    try:
        await asyncio.wait_for(writer.wait_closed(), 1)
    except (OSError, asyncio.TimeoutError):
        pass


class Proxy:
    def __init__(self, receipt, loader):
        self.receipt = deepcopy(states.validate(receipt))
        self.loader = loader
        self.authority = urlsplit(receipt['origin']).netloc
        self.connections = set()
        self.tasks = set()
        self.server = None
        self.counters = {'accepted': 0, 'rejected': 0, 'upstream_bytes': 0}
        self.stop_event = None

    def active(self):
        current = states.validate(self.loader())
        require(all(current[k] == self.receipt[k] for k in BINDING), 'session-changed')
        now = time.time()
        require(current['started_at'] <= now < current['expires_at'], 'session-expired')
        require(current['phase'] in {'starting', 'running'}
                and current['operation_result'] in {'running', 'passed'}, 'session-inactive')
        observed = current['observations']['process']
        require(observed['state'] == 'up' and observed['observed_at'] is not None
                and 0 <= now-observed['observed_at'] <= states.FRESH_SECONDS, 'session-stale')
        return current

    def timeout(self, ceiling=IDLE_SECONDS):
        self.active()
        return max(.001, min(ceiling, self.receipt['expires_at']-time.time()))

    async def upstream(self):
        return await asyncio.wait_for(
            asyncio.open_connection('127.0.0.1', self.receipt['metro_port'],
                                    limit=MAX_HEADERS+1), self.timeout(5))

    async def error(self, writer, status=400):
        try:
            await write(writer, f'HTTP/1.1 {status} Unavailable\r\nContent-Length: 0\r\n'
                        'Connection: close\r\nCache-Control: no-store\r\n\r\n'.encode(), 1)
        except (OSError, asyncio.TimeoutError):
            pass

    async def accept(self, reader, writer):
        if len(self.connections) >= MAX_CONNECTIONS:
            self.counters['rejected'] += 1
            try:
                await self.error(writer, 503)
            finally:
                writer.close()
                await close(writer)
            return
        self.connections.add(writer)
        task = asyncio.current_task()
        self.tasks.add(task)
        upstream_writer = None
        sent = False
        try:
            first, headers = await read_headers(reader, max(.001, min(10, self.receipt['expires_at']-time.time())))
            self.active()
            match = re.fullmatch(r'(GET|HEAD|POST) ([^ ]+) HTTP/1\.1', first)
            require(match is not None)
            method, target = match.groups()
            parsed = path(target, self.receipt['generation'])
            require(headers.get('host') == self.authority, 'foreign-host')
            require('authorization' not in headers and 'cookie' not in headers, 'credential-header')
            require(headers.get('origin') in {None, self.receipt['origin']}, 'foreign-origin')
            require('transfer-encoding' not in headers and 'expect' not in headers, 'request-framing')
            body_size = length(headers['content-length'], MAX_REQUEST) if 'content-length' in headers else 0
            require((method == 'POST' and parsed.path == '/symbolicate')
                    or (method in {'GET', 'HEAD'} and body_size == 0), 'request-method')
            upgrade = headers.get('upgrade')
            websocket = upgrade is not None
            if websocket:
                require(method == 'GET' and parsed.path in {'/message', '/hot'}
                        and upgrade.lower() == 'websocket'
                        and headers.get('connection', '').lower() == 'upgrade'
                        and headers.get('sec-websocket-version') == '13', 'websocket-handshake')
                try:
                    key = base64.b64decode(headers.get('sec-websocket-key', ''), validate=True)
                except ValueError:
                    raise TransportError('websocket-handshake') from None
                require(len(key) == 16 and 'sec-websocket-protocol' not in headers, 'websocket-handshake')
            self.counters['accepted'] += 1
            if parsed.path == '/_gptclaw/metro-health':
                require(method == 'GET' and not websocket)
                payload = json.dumps({'adapter': 'metro-v1', 'project': self.receipt['project'],
                                      'generation': self.receipt['generation'],
                                      'expires_at': self.receipt['expires_at']},
                                     sort_keys=True, separators=(',', ':')).encode()
                await write(writer, b'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n'
                            b'Cache-Control: no-store\r\nConnection: close\r\nContent-Length: '
                            +str(len(payload)).encode()+b'\r\n\r\n'+payload, self.timeout(5))
                sent = True
                return
            require(not parsed.path.startswith('/_gptclaw/'), 'reserved-path')
            upstream_reader, upstream_writer = await self.upstream()
            forwarded = {k: v for k, v in headers.items() if k in REQUEST_HEADERS}
            forwarded.update({'host': self.authority, 'x-forwarded-proto': 'https',
                              'accept-encoding': 'identity', 'connection': 'close'})
            if body_size:
                forwarded['content-length'] = str(body_size)
            if websocket:
                forwarded.update({'connection': 'Upgrade', 'upgrade': 'websocket',
                                  'sec-websocket-version': '13',
                                  'sec-websocket-key': headers['sec-websocket-key']})
            request = first+'\r\n'+''.join(k+': '+v+'\r\n' for k, v in forwarded.items())+'\r\n'
            await write(upstream_writer, request.encode('ascii'), self.timeout(10))
            if body_size:
                body = await asyncio.wait_for(reader.readexactly(body_size), self.timeout(10))
                await write(upstream_writer, body, self.timeout(10))
            response, received = await read_headers(upstream_reader, self.timeout(HTTP_SECONDS))
            status = re.fullmatch(r'HTTP/1\.[01] ([0-9]{3})(?: [ -~]*)?', response)
            require(status is not None, 'upstream-framing')
            code = int(status[1])
            require(100 <= code <= 599 and code not in range(300, 304) and code not in range(305, 400)
                    and 'location' not in received, 'upstream-redirect')
            require(received.get('content-encoding') in {None, 'identity'}, 'upstream-encoding')
            outgoing = {k: v for k, v in received.items() if k in RESPONSE_HEADERS}
            if websocket:
                require(code == 101 and received.get('upgrade', '').lower() == 'websocket'
                        and received.get('connection', '').lower() == 'upgrade', 'websocket-handshake')
                expected = base64.b64encode(hashlib.sha1(
                    (headers['sec-websocket-key']+'258EAFA5-E914-47DA-95CA-C5AB0DC85B11').encode()
                ).digest()).decode()
                require(received.get('sec-websocket-accept') == expected
                        and 'sec-websocket-extensions' not in received
                        and 'sec-websocket-protocol' not in received, 'websocket-handshake')
                outgoing.update({'connection': 'Upgrade', 'upgrade': 'websocket',
                                 'sec-websocket-accept': expected})
            else:
                require(code >= 200, 'upstream-framing')
                require(not ('content-length' in received and 'transfer-encoding' in received), 'upstream-framing')
                if 'content-length' in received:
                    outgoing['content-length'] = str(length(received['content-length'], MAX_BODY))
                else:
                    require(received.get('transfer-encoding') in {None, 'chunked'}, 'upstream-framing')
                    if method != 'HEAD' and code not in {204, 304}:
                        outgoing['transfer-encoding'] = 'chunked'
                outgoing['connection'] = 'close'
            header = response+'\r\n'+''.join(k+': '+v+'\r\n' for k, v in outgoing.items())+'\r\n'
            await write(writer, header.encode('ascii'), self.timeout(10))
            sent = True
            if websocket:
                await self.websocket(reader, writer, upstream_reader, upstream_writer)
            elif method != 'HEAD' and code not in {204, 304}:
                await self.body(upstream_reader, writer, received)
        except (TransportError, app.AppError, ValueError, UnicodeError, OSError,
                asyncio.IncompleteReadError, asyncio.LimitOverrunError, asyncio.TimeoutError):
            self.counters['rejected'] += 1
            if not sent:
                await self.error(writer, 503)
        finally:
            # Close both transports before awaiting either close notification.
            # Cancellation must never leave the other socket open.
            if upstream_writer:
                upstream_writer.close()
            writer.close()
            self.connections.discard(writer)
            self.tasks.discard(task)
            if upstream_writer:
                await close(upstream_writer)
            await close(writer)

    async def body(self, reader, writer, headers):
        count = 0
        deadline = time.monotonic()+min(HTTP_SECONDS, self.timeout(HTTP_SECONDS))
        def bound():
            remaining = deadline-time.monotonic()
            require(remaining > 0, 'response-timeout')
            return min(self.timeout(), remaining)
        async def part(number):
            nonlocal count
            while number:
                self.active()
                require(time.monotonic() < deadline, 'response-timeout')
                data = await asyncio.wait_for(reader.read(min(CHUNK, number)),
                                               min(bound(), max(.001, deadline-time.monotonic())))
                require(data, 'upstream-truncated')
                count += len(data)
                require(count <= MAX_BODY, 'body-bound')
                if 'content-length' in headers:
                    await write(writer, data, bound())
                else:
                    await write(writer, f'{len(data):x}\r\n'.encode()+data+b'\r\n', bound())
                self.counters['upstream_bytes'] += len(data)
                number -= len(data)
        if 'content-length' in headers:
            await part(length(headers['content-length'], MAX_BODY))
        elif headers.get('transfer-encoding') == 'chunked':
            while True:
                line = await asyncio.wait_for(reader.readuntil(b'\r\n'), bound())
                require(len(line) <= 32 and re.fullmatch(rb'[0-9A-Fa-f]{1,8}\r\n', line), 'upstream-framing')
                size = int(line.strip(), 16)
                require(size <= MAX_BODY-count, 'body-bound')
                if size == 0:
                    require(await asyncio.wait_for(reader.readexactly(2), bound()) == b'\r\n', 'upstream-framing')
                    await write(writer, b'0\r\n\r\n', bound())
                    return
                await part(size)
                require(await asyncio.wait_for(reader.readexactly(2), bound()) == b'\r\n', 'upstream-framing')
        else:
            while True:
                require(time.monotonic() < deadline, 'response-timeout')
                self.active()
                data = await asyncio.wait_for(reader.read(CHUNK), bound())
                if not data:
                    await write(writer, b'0\r\n\r\n', bound())
                    return
                count += len(data)
                require(count <= MAX_BODY, 'body-bound')
                await write(writer, f'{len(data):x}\r\n'.encode()+data+b'\r\n', bound())
                self.counters['upstream_bytes'] += len(data)

    async def frames(self, reader, writer, masked):
        count, fragmented = 0, False
        while True:
            first = await asyncio.wait_for(reader.readexactly(2), self.timeout())
            self.active()
            opcode, final = first[0] & 15, bool(first[0] & 128)
            require(first[0] & 112 == 0 and opcode in {0, 1, 2, 8, 9, 10}
                    and bool(first[1] & 128) == masked, 'websocket-frame')
            size = first[1] & 127
            extra = b''
            if size in {126, 127}:
                extra = await asyncio.wait_for(reader.readexactly(2 if size == 126 else 8), self.timeout())
                number = int.from_bytes(extra, 'big')
                require(number >= (126 if size == 126 else 65536), 'websocket-frame')
                size = number
            count += 2+len(extra)+(4 if masked else 0)
            require(size <= MAX_BODY-count and (opcode < 8 or final and size <= 125)
                    and (opcode != 8 or size != 1), 'websocket-bound')
            if opcode == 0:
                require(fragmented, 'websocket-frame')
                if final:
                    fragmented = False
            elif opcode in {1, 2}:
                require(not fragmented, 'websocket-frame')
                fragmented = not final
            mask = await asyncio.wait_for(reader.readexactly(4), self.timeout()) if masked else b''
            await write(writer, first+extra+mask, self.timeout())
            remaining = size
            while remaining:
                data = await asyncio.wait_for(reader.readexactly(min(CHUNK, remaining)), self.timeout())
                self.active()
                await write(writer, data, self.timeout())
                remaining -= len(data)
            count += size
            if opcode == 8:
                return

    async def websocket(self, reader, writer, upstream_reader, upstream_writer):
        tasks = [asyncio.create_task(self.frames(reader, upstream_writer, True)),
                 asyncio.create_task(self.frames(upstream_reader, writer, False))]
        try:
            done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                task.result()
        finally:
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)

    async def run(self, ready):
        self.stop_event = asyncio.Event()
        try:
            self.server = await asyncio.start_server(self.accept, '127.0.0.1',
                                                     self.receipt['proxy_port'], limit=MAX_HEADERS+1)
            ready.set()
            remaining = max(.001, self.receipt['expires_at']-time.time())
            try:
                await asyncio.wait_for(self.stop_event.wait(), remaining)
            except asyncio.TimeoutError:
                pass
        finally:
            if self.server:
                self.server.close()
            pending = list(self.tasks)
            for writer in list(self.connections):
                writer.close()
            for task in pending:
                task.cancel()
            await asyncio.gather(*pending, return_exceptions=True)
            if self.server:
                await self.server.wait_closed()


class Service:
    """One thread in the owned supervisor; no detached process or public binding."""
    def __init__(self, receipt, loader):
        self.proxy = Proxy(receipt, loader)
        self.ready = threading.Event()
        self.loop = None
        self.failure = False
        self.thread = threading.Thread(target=self._run, daemon=True, name='gptclaw-metro-proxy')

    def _run(self):
        async def run():
            self.loop = asyncio.get_running_loop()
            await self.proxy.run(self.ready)
        try:
            asyncio.run(run())
        except (OSError, app.AppError, ValueError):
            self.failure = True
        finally:
            self.ready.set()

    def start(self):
        self.thread.start()
        app.need(self.ready.wait(5) and not self.failure and self.thread.is_alive()
                 and self.proxy.server is not None and self.proxy.server.is_serving(), 'ports')
        return self

    def stop(self):
        if self.loop and not self.loop.is_closed() and self.proxy.stop_event:
            try:
                self.loop.call_soon_threadsafe(self.proxy.stop_event.set)
            except RuntimeError:
                # A concurrent natural expiry can close the event loop.
                pass
        self.thread.join(timeout=5)
        app.need(not self.thread.is_alive(), 'timeout')
