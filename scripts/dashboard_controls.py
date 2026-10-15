"""Private typed dashboard controller. Browser data can select no paths or commands."""
import argparse
import contextlib
import fcntl
from http.server import BaseHTTPRequestHandler
import json
import os
from pathlib import Path
import re
import secrets
import socketserver
import stat
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import private_apps as app
import project_controls as lifecycle
from dashboard_inventory import Scanner, InventoryError
from dashboard_collector import SocketLease, bounded

HEX = re.compile(r'[0-9a-f]{32}')
MAX_BODY = 8192
MAX_RECORDS = 1000
MAX_BYTES = 10*1024*1024
CAPABILITY_TIMEOUT = 12
RETENTION = 7*86400
ACTIVE = {'accepted', 'running', 'unknown'}
PUBLIC_FIELDS = {'schema_version', 'operation_id', 'project_key', 'project', 'name', 'action',
                 'component', 'state', 'stage', 'stage_component', 'created_at', 'updated_at', 'reason', 'observed_at'}
REASONS = {'control-disabled', 'invalid-request', 'invalid-session', 'intent-expired', 'unknown-operation',
           'control-unavailable', 'control-conflict', *app.MESSAGES}


class Refusal(Exception):
    def __init__(self, reason, status=409):
        self.reason, self.status = reason, status
        super().__init__(reason)


def require(condition, reason='invalid-request', status=400):
    if not condition:
        raise Refusal(reason, status)


def private_directory(path):
    path = app.safe(Path(path))
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    info = path.lstat()
    require(stat.S_ISDIR(info.st_mode) and info.st_uid == os.getuid() and stat.S_IMODE(info.st_mode) == 0o700, 'path', 503)
    return path


def read_record(path):
    value = app.read_json(path)
    info = path.lstat()
    require(stat.S_IMODE(info.st_mode) == 0o600 and isinstance(value, dict)
            and value.get('schema_version') == 1 and HEX.fullmatch(value.get('operation_id', ''))
            and value.get('state') in {'accepted', 'running', 'succeeded', 'failed', 'unknown'}
            and value.get('action') in lifecycle.ACTIONS and value.get('component') in {None, *lifecycle.COMPONENTS}
            and value.get('reason') in {None, *REASONS}, 'control-recovery', 503)
    return value


def public(record):
    return {key: value for key, value in record.items() if key in PUBLIC_FIELDS}


def strict_json(raw):
    def unique(pairs):
        value = {}
        for key, item in pairs:
            require(key not in value)
            value[key] = item
        return value
    try:
        require(len(raw) <= MAX_BODY)
        value = json.loads(raw, object_pairs_hook=unique, parse_constant=lambda _: require(False))
        require(isinstance(value, dict) and type(value.get('schema_version')) is int and value['schema_version'] == 1)
        return value
    except (ValueError, UnicodeError, RecursionError):
        raise Refusal('invalid-request', 400) from None


def capabilities():
    return {'provider': 'gptclawctl', 'project_manifest_schemas': list(range(1, 10)),
            'runtime_manifest_schemas': [1, 2, 3, 4, 6, 7, 8, 9], 'metro_session_schemas': [1]}


def capability_job(root):
    return lifecycle.capabilities(Path(root))


class Controller:
    def __init__(self, projects, state, origin, *, enabled=False, registry=None, clock=time.time, spawn=None, inspector=None):
        require(re.fullmatch(r'https://[a-z0-9.-]+\.ts\.net', origin) is not None, 'setup', 503)
        self.projects, self.state, self.origin = Path(projects), private_directory(state), origin
        self.registry, self._enabled, self.clock = registry, enabled, clock
        self.lock = threading.RLock()
        self.sessions, self.intents, self.cache, self.bindings, self.processes = {}, {}, {}, {}, {}
        self.stop_event = threading.Event()
        self.spawn = spawn or self.start_worker
        self.inspector = inspector or self.inspect_capabilities
        self.offset = 0
        self.recover_startup()

    def inspect_capabilities(self, root):
        value=bounded(capability_job,str(root),CAPABILITY_TIMEOUT)
        require(value.get('schema_version')==1 and isinstance(value.get('actions'),list)
                and isinstance(value.get('generation'),str) and re.fullmatch(r'[0-9a-f]{64}',value['generation']), 'control-unavailable',503)
        return value

    @property
    def enabled(self):
        return self._enabled and not (self.state/'disabled').exists()

    def records(self):
        paths = list(self.state.glob('*.json'))
        require(len(paths) <= MAX_RECORDS, 'control-capacity', 503)
        result = []
        for path in paths:
            require(HEX.fullmatch(path.stem), 'control-recovery', 503)
            value = read_record(path)
            require(value['operation_id'] == path.stem, 'control-recovery', 503)
            result.append(value)
        return result

    def recover_startup(self):
        # Service lock plus provider project lock/guard prevents a second
        # controller from replaying an orphan. Never re-dispatch records on boot.
        for record in self.records():
            if record['state'] in {'accepted', 'running'}:
                journal = app.read_json(app.STORE/'control-journals'/(record['operation_id']+'.json'))
                if journal and journal.get('state') == 'succeeded':
                    record.update(state='succeeded', reason=None)
                else:
                    record.update(state='unknown', reason='control-recovery')
                record['updated_at'] = self.clock()
                app.save(self.state/(record['operation_id']+'.json'), record)

    def clean_capacity(self):
        records = self.records()
        for record in records:
            if record['state'] not in ACTIVE and self.clock()-record['updated_at'] > RETENTION:
                (self.state/(record['operation_id']+'.json')).unlink()
        records = self.records()
        require(len(records) < MAX_RECORDS and sum(path.stat().st_size for path in self.state.glob('*.json')) < MAX_BYTES-MAX_BODY,
                'control-capacity', 503)
        return records

    def discover(self):
        scanner = Scanner(self.projects, registry=self.registry, capabilities=capabilities())
        snapshot = scanner.scan()
        require(snapshot['freshness'] == 'current' and snapshot['complete'], 'control-unavailable', 503)
        return scanner.bindings, {row['key']: row for row in snapshot['rows'] if row['identity_state'] == 'valid'}

    def target(self, key):
        require(isinstance(key, str) and HEX.fullmatch(key))
        bindings, rows = self.discover()
        require(key in bindings and key in rows and rows[key]['runtime_support'] == 'supported', 'control-unavailable', 409)
        root = Path(bindings[key]['root'])
        # Recheck pinned directory identity and provider validation. Scanner
        # conflicts or a changed inode cannot silently retarget the same key.
        info = root.stat(follow_symlinks=False)
        require(tuple(bindings[key]['identity']) == (info.st_dev, info.st_ino, info.st_uid), 'control-changed', 409)
        app.need(root.is_relative_to(self.projects) and root.parent == self.projects, 'path')
        _, value = app.target(root)
        require(value['project']['id'] == rows[key]['id'], 'control-changed', 409)
        return root, rows[key]

    def refresh(self):
        if not self.enabled:
            return
        try:
            bindings, rows = self.discover()
            keys = sorted(rows)
            window = keys[self.offset:self.offset+20]
            self.offset = 0 if self.offset+20 >= len(keys) else self.offset+20
            with self.lock:
                self.cache = {key: value for key, value in self.cache.items() if key in rows}
                self.bindings = bindings
            # Finite project workers, bounded by the same native command
            # deadlines as provider reads. Snapshot requests only read cache.
            with ThreadPoolExecutor(max_workers=2) as pool:
                def inspect(item):
                    key, row = item
                    try:
                        value = bounded(capability_job, bindings[key]['root'], CAPABILITY_TIMEOUT)
                        if value.get('schema_version') != 1:
                            raise ValueError('unavailable')
                        return key, value
                    except (app.AppError, OSError, ValueError, KeyError):
                        return key, {'schema_version': 1, 'actions': [], 'reason': 'control-unavailable', 'observed_at': self.clock()}
                pending = [pool.submit(inspect, (key, rows[key])) for key in window]
                for future in as_completed(pending):
                    key, value = future.result()
                    # A slow unrelated project must not age completed reads
                    # while the rest of the collection window is inspected.
                    with self.lock:
                        self.cache[key] = value
        except (Refusal, InventoryError, OSError, ValueError):
            with self.lock:
                self.cache = {}

    def snapshot(self):
        with self.lock:
            records = self.records()
            result = {}
            for key, value in self.cache.items():
                recent = sorted((public(r) for r in records if r['project_key'] == key), key=lambda r: r['created_at'], reverse=True)[:5]
                result[key] = {'schema_version': 1, 'enabled': self.enabled,
                               'capabilities': value, 'recent': recent, 'retention_days': 7}
            return {'schema_version': 1, 'enabled': self.enabled, 'projects': result}

    def session(self):
        require(self.enabled, 'control-disabled', 503)
        with self.lock:
            self.sessions = {key: value for key, value in self.sessions.items() if value['expires_at'] > self.clock()}
            require(len(self.sessions) < 128, 'control-capacity', 503)
            session, csrf = secrets.token_hex(32), secrets.token_hex(32)
            self.sessions[session] = {'csrf': csrf, 'expires_at': self.clock()+900}
            return {'schema_version': 1, 'session': session, 'csrf': csrf, 'expires_at': self.clock()+900}

    def authorize(self, session, csrf):
        require(self.enabled, 'control-disabled', 503)
        value = self.sessions.get(session) if isinstance(session, str) else None
        require(value is not None and value['expires_at'] > self.clock() and isinstance(csrf, str)
                and secrets.compare_digest(value['csrf'], csrf), 'invalid-session', 403)
        return session

    def intent(self, data, session, csrf):
        with self.lock:
            self.authorize(session, csrf)
            require(set(data) == {'schema_version', 'project_key', 'action', 'component'})
            require(data['action'] in lifecycle.ACTIONS and data['component'] in {None, *lifecycle.COMPONENTS})
            self.intents = {key: value for key, value in self.intents.items() if value['expires_at'] > self.clock()}
            require(len(self.intents) < 64, 'control-capacity', 503)
            root, row = self.target(data['project_key'])
            caps = self.inspector(root)
            selected = [a for a in caps['actions'] if a['action'] == data['action'] and a['component'] == data['component']]
            require(len(selected) == 1 and selected[0]['enabled'], selected[0]['reason'] if selected else 'control-unsupported', 409)
            _, value = app.target(root)
            ident = secrets.token_hex(16)
            prepared = self.clock()
            intent = {**data, 'intent_id': ident, 'generation': caps['generation'], 'session': session,
                      'prepared_at': prepared, 'expires_at': prepared+60, 'root': str(root), 'project': row['id'], 'name': row['name'],
                      'impact': lifecycle.impact(value, data['action'], data['component'])}
            self.intents[ident] = intent
            return {key: val for key, val in intent.items() if key not in {'root', 'session'}}

    def submit(self, data, session, csrf):
        with self.lock:
            self.authorize(session, csrf)
            require(set(data) == {'schema_version', 'intent_id', 'idempotency_key'}
                    and isinstance(data['intent_id'], str) and HEX.fullmatch(data['intent_id'])
                    and isinstance(data['idempotency_key'], str) and HEX.fullmatch(data['idempotency_key']))
            ident = data['idempotency_key']
            path = self.state/(ident+'.json')
            if path.exists():
                record = read_record(path)
                require(record['intent_id'] == data['intent_id'] and record['session_hash'] == lifecycle.digest(session), 'control-conflict', 409)
                return public(record)
            intent = self.intents.get(data['intent_id'])
            require(intent is not None and intent['session'] == session and intent['expires_at'] > self.clock(), 'intent-expired', 409)
            require(not intent.get('used'), 'control-conflict', 409)
            records = self.clean_capacity()
            require(sum(record['state'] in ACTIVE for record in records) < 4, 'control-capacity', 503)
            require(not any(r['project'] == intent['project'] and r['state'] in ACTIVE for r in records), 'busy', 409)
            root, row = self.target(intent['project_key'])
            with lifecycle.source_lock(root), lifecycle.project_lock(row['id']):
                caps = self.inspector(root)
                require(caps['generation'] == intent['generation'], 'control-changed', 409)
                selected = next((a for a in caps['actions'] if a['action'] == intent['action'] and a['component'] == intent['component']), None)
                require(selected is not None and selected['enabled'], 'control-state', 409)
                now = self.clock()
                record = {'schema_version': 1, 'operation_id': ident, 'intent_id': intent['intent_id'],
                          'session_hash': lifecycle.digest(session), 'project_key': intent['project_key'],
                          'project': row['id'], 'name': row['name'], 'root': str(root), 'generation': caps['generation'],
                          'action': intent['action'], 'component': intent['component'], 'state': 'accepted',
                          'stage': 'accepted', 'stage_component': None, 'created_at': now, 'updated_at': now,
                          'reason': None, 'observed_at': None}
                app.save(path, record)
                intent['used'] = True
                marker = lifecycle.guard_path(row['id']); private_directory(marker.parent)
                app.save(marker, {'schema_version': 1, 'operation_id': ident, 'project': row['id'], 'root': str(root)})
            try:
                self.processes[ident] = self.spawn(ident)
            except (OSError, app.AppError):
                record.update(state='unknown', reason='control-recovery', updated_at=self.clock())
                app.save(path, record)
            return public(record)

    def start_worker(self, ident):
        # Only the trusted immutable script, exact state directory and opaque ID
        # are argv; no source module or project command executes on the host.
        return subprocess.Popen([sys.executable, '-B', str(Path(__file__).resolve()), 'worker',
                                 '--state', str(self.state), '--operation-id', ident],
                                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                env={'PATH': '/usr/local/bin:/usr/bin:/bin', 'HOME': '/home/forge'}, start_new_session=True)

    def operation(self, ident):
        require(isinstance(ident, str) and HEX.fullmatch(ident))
        path = self.state/(ident+'.json')
        require(path.exists(), 'unknown-operation', 404)
        with self.lock:
            process = self.processes.get(ident)
            record = read_record(path)
            if record['state'] == 'unknown':
                journal = app.read_json(app.STORE/'control-journals'/(ident+'.json'))
                if journal and journal.get('reconciled_at') is not None:
                    record.update(state='failed', reason='control-recovery', updated_at=journal['reconciled_at'], observed_at=journal['reconciled_at'])
                    app.save(path, record)
            if process is not None and process.poll() is not None:
                process.wait(); del self.processes[ident]
                if record['state'] in {'accepted', 'running'}:
                    record.update(state='unknown', reason='control-recovery', updated_at=self.clock())
                    app.save(path, record)
            return public(record)

    def loop(self):
        while not self.stop_event.is_set():
            self.refresh()
            for record in self.records():
                self.operation(record['operation_id'])
            self.stop_event.wait(2)


def worker(state, ident):
    require(HEX.fullmatch(ident))
    directory = private_directory(state)
    path = directory/(ident+'.json')
    record = read_record(path)
    require(record['state'] == 'accepted' and record['operation_id'] == ident, 'control-recovery', 409)
    token = lifecycle.OWNER.set(ident)
    try:
        def stage(name, component):
            record.update(state='running', stage=name, stage_component=component, updated_at=time.time())
            app.save(path, record)
        result = lifecycle.execute(record['root'], record['action'], record['component'],
                                   expected=record['generation'], operation_id=ident, stage=stage, admitted=True)
        record.update(state='succeeded', stage='completed', observed_at=result['observed_at'], updated_at=time.time())
    except (app.AppError, OSError, ValueError, KeyError) as error:
        record.update(state='unknown', reason=error.code if isinstance(error, app.AppError) else 'internal', updated_at=time.time())
    finally:
        lifecycle.OWNER.reset(token)
    app.save(path, record)


def reconcile_operation(root, ident, confirm, *, state=Path('/srv/forge/platform/controls/v1')):
    """Explicit host CLI recovery, including failed admission before guard creation.

    The HTTP/browser surface does not expose this function. The same project lock
    excludes live workers; delayed admitted workers must prove their guard still
    exists before effects, so reconciliation can never cause a later replay.
    """
    require(isinstance(ident,str) and HEX.fullmatch(ident))
    root,value=app.target(root);project=value['project']['id']
    require(confirm==project,'control-changed',409)
    path=app.safe(Path(state))/(ident+'.json')
    if not path.exists():return lifecycle.reconcile(root,ident,confirm)
    record=read_record(path)
    require(record['project']==project and record['root']==str(root),'control-recovery',409)
    token=lifecycle.OWNER.set(ident)
    try:
        with lifecycle.source_lock(root),lifecycle.project_lock(project):
            journal=app.read_json(app.STORE/'control-journals'/(ident+'.json'))
            if journal and journal.get('operation_id')==ident and journal.get('project')==project and journal.get('state')=='succeeded':
                require(not lifecycle.guard_path(project).exists(),'control-recovery',409)
                result={'state':'succeeded','observed_at':journal['updated_at']}
                record.update(state='succeeded',reason=None,stage='completed')
            else:
                result=lifecycle.reconcile(root,ident,confirm,allow_absent=True)
                record.update(state='failed',reason='control-recovery')
            record.update(updated_at=time.time(),observed_at=result['observed_at'])
            app.save(path,record)
            return {**public(record),'reconciled':True}
    finally:lifecycle.OWNER.reset(token)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_): pass

    def reply(self, status, value):
        body = json.dumps(value, allow_nan=False).encode()
        self.send_response(status); self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body))); self.send_header('Cache-Control', 'no-store')
        self.send_header('Connection', 'close'); self.end_headers()
        if self.command != 'HEAD': self.wfile.write(body)
        self.close_connection = True

    def request_data(self):
        require(not self.headers.get('Transfer-Encoding'))
        require(len(str(self.headers)) <= 16384)
        require(self.headers.get('Host') == self.server.controller.origin.removeprefix('https://'), 'invalid-session', 403)
        origin = self.headers.get('Origin')
        if self.command == 'POST' or self.path == '/v1/session':
            require(origin == self.server.controller.origin, 'invalid-session', 403)
            require(self.headers.get('Sec-Fetch-Site') == 'same-origin', 'invalid-session', 403)
        elif origin:
            require(origin == self.server.controller.origin, 'invalid-session', 403)
        if self.command == 'POST':
            require(self.headers.get('Content-Type') == 'application/json')
            raw_length = self.headers.get('Content-Length', '')
            require(raw_length.isdecimal() and 0 < int(raw_length) <= MAX_BODY)
            data = self.rfile.read(int(raw_length)); require(len(data) == int(raw_length))
            return strict_json(data)
        require(self.headers.get('Content-Length', '0') == '0')
        return None

    def route(self):
        try:
            data = self.request_data(); c = self.server.controller
            if self.command in {'GET', 'HEAD'}:
                if self.path == '/v1/snapshot': return self.reply(200, c.snapshot())
                if self.path == '/v1/session': return self.reply(200, c.session())
                if re.fullmatch(r'/v1/operations/[0-9a-f]{32}', self.path):
                    return self.reply(200, c.operation(self.path.rsplit('/', 1)[1]))
            elif self.command == 'POST':
                session, csrf = self.headers.get('X-Control-Session'), self.headers.get('X-CSRF-Token')
                if self.path == '/v1/intents': return self.reply(200, c.intent(data, session, csrf))
                if self.path == '/v1/operations': return self.reply(202, c.submit(data, session, csrf))
            self.reply(405 if self.command not in {'GET', 'HEAD', 'POST'} else 404, {'error': 'invalid-request'})
        except Refusal as error: self.reply(error.status, {'error': error.reason})
        except app.AppError as error: self.reply(409, {'error': error.code})
        except (OSError, ValueError, TypeError, KeyError, InventoryError): self.reply(503, {'error': 'control-unavailable'})

    do_GET = do_HEAD = do_POST = do_PUT = do_PATCH = do_DELETE = do_OPTIONS = do_TRACE = route


class Server(socketserver.UnixStreamServer):
    request_queue_size = 16
    def __init__(self, address, controller):
        self.controller = controller
        self.pool = ThreadPoolExecutor(max_workers=8)
        self.slots = threading.BoundedSemaphore(8)
        super().__init__(address, Handler); os.chmod(address, 0o600)
    def process_request(self, request, address):
        if not self.slots.acquire(blocking=False):
            self.shutdown_request(request); return
        self.pool.submit(self.worker, request, address)
    def worker(self, request, address):
        try:
            request.settimeout(5); self.finish_request(request, address)
        except (OSError, ValueError): pass
        finally:
            self.shutdown_request(request); self.slots.release()
    def server_close(self):
        super().server_close(); self.pool.shutdown(wait=True)


def main():
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument('action', choices=['serve', 'worker'])
    parser.add_argument('--state', required=True)
    parser.add_argument('--operation-id')
    parser.add_argument('--socket'); parser.add_argument('--projects-root'); parser.add_argument('--registry')
    parser.add_argument('--origin'); parser.add_argument('--enabled', action='store_true')
    args = parser.parse_args()
    if args.action == 'worker':
        worker(args.state, args.operation_id); return
    state = private_directory(args.state)
    fd = os.open(state/'controller.lock', os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        controller = Controller(args.projects_root, state, args.origin, enabled=args.enabled, registry=args.registry)
        thread = threading.Thread(target=controller.loop, daemon=True); thread.start()
        with SocketLease(args.socket) as lease, Server(args.socket, controller) as server:
            lease.record()
            try: server.serve_forever()
            finally: controller.stop_event.set(); thread.join(timeout=5)
    finally: os.close(fd)


if __name__ == '__main__': main()
