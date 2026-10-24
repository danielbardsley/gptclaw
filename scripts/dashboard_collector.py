"""Private, bounded in-memory dashboard reads over an owned Unix socket."""
import argparse
import io
from concurrent.futures import ThreadPoolExecutor
import copy
import contextlib
import fcntl
import http.server
import json
import multiprocessing
import os
from pathlib import Path
import signal
import socketserver
import stat
import threading
import time

from dashboard_inventory import Scanner, MAX_OUTPUT, InventoryError, open_directory
# Trusted imports are preloaded by the clean forkserver, not by discovered projects.
import dashboard_observation
import project_groups
import project_database
import project_templates
import project_toolchains
from project_manifest import load_schema

# Compile the immutable contracts once in the clean forkserver. Workers
# still read exact schema bytes and fully validate each project's current data.
for schema_version in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12):
    load_schema(schema_version)

multiprocessing.set_forkserver_preload(['dashboard_collector'])
FORKSERVER_START_LOCK = threading.Lock()

class ReadActivity:
    """Shared viewer lease; requests wake background readers without doing probes."""
    def __init__(self, *, clock=time.monotonic, lease=15):
        self.clock, self.lease = clock, lease
        self.condition = threading.Condition()
        self.expires = float('-inf')
        self.resumed = float('-inf')

    def touch(self):
        with self.condition:
            now = self.clock()
            if now >= self.expires:
                self.resumed = now
            self.expires = now + self.lease
            self.condition.notify_all()

    def due(self, last, interval):
        now = self.clock()
        return now < self.expires and (last is None or last < self.resumed or now-last >= interval)

    def wait(self, stop, last, interval):
        with self.condition:
            while not stop.is_set():
                if self.due(last, interval):
                    return self.clock()
                # Stop remains responsive; idle waits create no workers or probes.
                self.condition.wait(1)
        return None


def observation_context():
    # The forkserver is a fresh interpreter. Give it only the known tooling path
    # while starting, then restore the parent environment before any project read.
    from multiprocessing import forkserver
    with FORKSERVER_START_LOCK:
        previous = os.environ.get('PYTHONPATH')
        os.environ['PYTHONPATH'] = str(Path(__file__).resolve().parent)
        try:
            forkserver.ensure_running()
        finally:
            if previous is None:
                os.environ.pop('PYTHONPATH', None)
            else:
                os.environ['PYTHONPATH'] = previous
    return multiprocessing.get_context('forkserver')


def _worker(connection, function, argument):
    os.setsid()
    try:
        value = function(argument)
        connection.send_bytes(json.dumps(value, allow_nan=False).encode())
    except Exception:
        try:
            connection.send_bytes(b'{"error":"observation-unavailable"}')
        except OSError:
            pass
    finally:
        connection.close()


def bounded(function, argument, seconds, limit=MAX_OUTPUT, *, context=None):
    """Kill/reap the whole owned worker process group on timeout or invalid output."""
    ctx = context or observation_context()
    reader, writer = ctx.Pipe(duplex=False)
    process = ctx.Process(target=_worker, args=(writer, function, argument))
    process.start()
    writer.close()
    try:
        if not reader.poll(seconds):
            return {'error': 'observation-timeout'}
        try:
            value = json.loads(reader.recv_bytes(limit))
            return value if isinstance(value, dict) else {'error': 'observation-invalid'}
        except (OSError, ValueError, EOFError):
            return {'error': 'observation-invalid'}
    finally:
        reader.close()
        process.join(.1)
        if process.is_alive():
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                process.terminate()
            process.join(.2)
        if process.is_alive():
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                process.kill()
            process.join()
        process.close()


def scan_job(config):
    scanner = Scanner(**config)
    snapshot = scanner.scan()
    return {'snapshot': snapshot, 'bindings': scanner.bindings}


class Collector:
    def __init__(self, config, *, clock=time.time, run=bounded, enable_status=False, enable_links=False, enable_controls=False):
        self.config, self.clock, self.run = config, clock, run
        self.lock = threading.RLock()
        self.stop_event = threading.Event()
        self.activity = ReadActivity()
        self.inventory = None
        self.bindings = {}
        self.inventory_error = None
        from dashboard_status import StatusStore
        status_options = {'deadline':8,'workers':2} if enable_controls else {}
        self.status = StatusStore(run, clock=clock, **status_options) if enable_status or enable_links or enable_controls else None
        self.status_error = False
        self.enable_links = enable_links

    def refresh_inventory(self):
        result = self.run(scan_job, self.config, 10.5)
        snapshot = copy.deepcopy(result.get('snapshot'))
        with self.lock:
            if not isinstance(snapshot, dict) or snapshot.get('freshness') == 'unavailable':
                self.inventory_error = 'inventory-unavailable'
                return
            # A partial scan cannot establish disappearance. Retain earlier rows
            # as explicitly stale diagnostics, with no active target binding.
            for row in snapshot['rows']:
                row['inventory_freshness'] = 'current'
                row['inventory_observed_at'] = snapshot['observed_at']
            if self.inventory and not snapshot.get('complete'):
                present = {row['key'] for row in snapshot['rows']}
                for previous in self.inventory['rows']:
                    if previous['key'] not in present:
                        retained = copy.deepcopy(previous)
                        retained['inventory_freshness'] = 'stale'
                        snapshot['rows'].append(retained)
                while len(snapshot['rows']) > 256 or len(json.dumps(snapshot).encode()) > MAX_OUTPUT:
                    snapshot['rows'].pop()
                    snapshot['truncated'] = True
            self.inventory = snapshot
            self.bindings = result.get('bindings', {})
            self.inventory_error = None
            if self.status:
                self.status.retain({row['key'] for row in snapshot['rows']}, complete=snapshot['complete'])

    def snapshot(self):
        self.activity.touch()
        with self.lock:
            if self.inventory is None:
                return {'schema_version': 1, 'freshness': 'unavailable', 'complete': False,
                        'truncated': False, 'rows': [], 'diagnostics': [{'code': self.inventory_error or 'inventory-loading'}]}
            value = copy.deepcopy(self.inventory)
            if self.inventory_error or self.clock() - value['last_success_at'] > 60:
                value['freshness'] = 'stale'
            if self.inventory_error:
                value['diagnostics'].append({'code': self.inventory_error})
            if self.status:
                value['status_capacity'] = copy.deepcopy(self.status.capacity)
                for row in value['rows']:
                    binding = self.bindings.get(row['key'])
                    row['status'] = self.status.snapshot(row['key'], binding or {'components':row['components']})
                    if binding is None or value['freshness']!='current' or self.status_error:
                        row['status']['freshness']='stale' if row['status'].get('last_success_at') is not None else 'unavailable'
                        row['status']['publication']['state']='unavailable'
                        row['status']['reason']='inventory-stale' if binding is None or value['freshness']!='current' else 'observation-unavailable'
                        for component in row['status']['components'].values():
                            component['freshness']='stale' if component.get('last_success_at') is not None else 'unavailable'
                            component['reason']=row['status']['reason']
            if self.enable_links:
                from dashboard_links import links
                for row in value['rows']:
                    row['links']=links(row,row.get('status'),self.clock())
            value['server_time'] = self.clock()
            return value

    def inventory_loop(self):
        last = None
        while (started := self.activity.wait(self.stop_event, last, 30)) is not None:
            self.refresh_inventory()
            last = started

    def status_loop(self):
        last = None
        while (started := self.activity.wait(self.stop_event, last, 5)) is not None:
            with self.lock:
                bindings=copy.deepcopy(self.bindings) if not self.inventory_error else {}
            try:
                self.status.round(bindings)
                self.status_error=False
            except Exception:
                self.status_error=True
            # Rest after a round, including expensive or timed-out rounds.
            # Subtracting read time from the interval creates continuous work.
            last = time.monotonic()

    def start(self):
        thread = threading.Thread(target=self.inventory_loop, name='dashboard-inventory', daemon=True)
        thread.start()
        threads=[thread]
        if self.status:
            status_thread=threading.Thread(target=self.status_loop,name='dashboard-status',daemon=True)
            status_thread.start();threads.append(status_thread)
        return threads


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def reply(self, code, value):
        body = json.dumps(value, allow_nan=False).encode()
        if len(body) > MAX_OUTPUT:
            code, body = 503, b'{"error":"output-limit"}'
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Connection', 'close')
        self.end_headers()
        if self.command != 'HEAD':
            self.wfile.write(body)
        self.close_connection = True

    def do_GET(self):
        if self.headers.get('Transfer-Encoding') or self.headers.get('Content-Length', '0') != '0':
            return self.reply(400, {'error': 'invalid-request'})
        if self.path == '/v1/snapshot':
            return self.reply(200, self.server.collector.snapshot())
        if self.path == '/healthz':
            return self.reply(200, {'service': 'gptclaw-dashboard-collector', 'schema_version': 1})
        return self.reply(404, {'error': 'unknown-read'})

    do_HEAD = do_GET

    def mutation(self):
        self.reply(405, {'error': 'read-only'})

    do_POST = do_PUT = do_PATCH = do_DELETE = do_OPTIONS = do_TRACE = mutation


class Server(socketserver.UnixStreamServer):
    request_queue_size = 16

    def __init__(self, address, collector):
        self.collector = collector
        self.pool = ThreadPoolExecutor(max_workers=8)
        self.slots = threading.BoundedSemaphore(8)
        super().__init__(address, Handler)
        os.chmod(address, 0o600)

    def process_request(self, request, client_address):
        if not self.slots.acquire(blocking=False):
            self.shutdown_request(request)
            return
        self.pool.submit(self.worker, request, client_address)

    def worker(self, request, client_address):
        try:
            request.settimeout(3)
            self.finish_request(request, client_address)
        except (OSError, ValueError):
            pass
        finally:
            self.shutdown_request(request)
            self.slots.release()

    def server_close(self):
        super().server_close()
        self.pool.shutdown(wait=True)


def socket_path(path):
    path = Path(path)
    fd = open_directory(path.parent)
    try:
        if stat.S_IMODE(os.fstat(fd).st_mode) != 0o700:
            raise InventoryError('unsafe-socket-directory')
        try:
            os.stat(path.name, dir_fd=fd, follow_symlinks=False)
        except FileNotFoundError:
            return path
        raise InventoryError('socket-conflict')
    finally:
        os.close(fd)


class SocketLease:
    """Reconcile only a proven owned stale socket under an exclusive file lock."""
    def __init__(self, path):
        self.path = Path(path)
        self.stamp = self.path.with_suffix('.owner.json')
        self.lock_path = self.path.with_suffix('.lock')
        self.fd = None
        self.recorded = None

    def __enter__(self):
        parent = open_directory(self.path.parent)
        try:
            if stat.S_IMODE(os.fstat(parent).st_mode) != 0o700:
                raise InventoryError('unsafe-socket-directory')
            self.fd = os.open(self.lock_path.name, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600, dir_fd=parent)
            info = os.fstat(self.fd)
            if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
                    or info.st_nlink != 1 or stat.S_IMODE(info.st_mode) != 0o600):
                raise InventoryError('unsafe-socket-lock')
            fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            if self.path.exists() or self.path.is_symlink():
                self.verify_record()
                import socket
                with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as probe:
                    probe.settimeout(.2)
                    try:
                        probe.connect(str(self.path))
                    except ConnectionRefusedError:
                        self.path.unlink()
                        self.stamp.unlink()
                    else:
                        raise InventoryError('socket-in-use')
            elif self.stamp.exists() or self.stamp.is_symlink():
                # A missing socket with an orphan stamp still needs explicit inspection.
                raise InventoryError('socket-conflict')
            return self
        except BaseException:
            if self.fd is not None:
                os.close(self.fd); self.fd = None
            raise
        finally:
            os.close(parent)

    def verify_record(self):
        info = self.path.lstat()
        stamp = self.stamp.lstat()
        if (not stat.S_ISSOCK(info.st_mode) or info.st_uid != os.getuid()
                or stat.S_IMODE(info.st_mode) != 0o600 or not stat.S_ISREG(stamp.st_mode)
                or stamp.st_uid != os.getuid() or stamp.st_nlink != 1
                or stat.S_IMODE(stamp.st_mode) != 0o600 or stamp.st_size > 1024):
            raise InventoryError('socket-conflict')
        fd = os.open(self.stamp, os.O_RDONLY | os.O_NOFOLLOW)
        with os.fdopen(fd) as stream:
            value = json.load(stream)
        expected = {'schema_version': 1, 'device': info.st_dev, 'inode': info.st_ino}
        if value != expected:
            raise InventoryError('socket-conflict')
        return value

    def record(self):
        info = self.path.lstat()
        self.recorded = {'schema_version': 1, 'device': info.st_dev, 'inode': info.st_ino}
        fd = os.open(self.stamp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, 'w') as stream:
            json.dump(self.recorded, stream)

    def __exit__(self, *_):
        try:
            if self.recorded and self.path.exists() and self.verify_record() == self.recorded:
                self.path.unlink()
                self.stamp.unlink()
        finally:
            if self.fd is not None:
                os.close(self.fd)


def stop_signal(*_):
    raise SystemExit(0)


def provider_capabilities():
    """Read only the bundled CLI contract, never infer installed support from plans."""
    import gptclawctl
    output=io.StringIO()
    with contextlib.redirect_stdout(output):
        code=gptclawctl.main(['--version'])
    raw=output.getvalue()
    if code!=0 or len(raw)>65536:raise InventoryError('provider-unavailable')
    value=json.loads(raw)
    if not isinstance(value,dict) or value.get('provider')!='gptclawctl':
        raise InventoryError('provider-unavailable')
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--projects-root', required=True)
    parser.add_argument('--socket', required=True)
    parser.add_argument('--registry')
    parser.add_argument('--status',action='store_true')
    parser.add_argument('--links',action='store_true')
    parser.add_argument('--controls',action='store_true',help='Use the bounded status budget for a controls-enabled release')
    args = parser.parse_args()
    collector = Collector({'projects': args.projects_root, 'registry': args.registry,
                           'capabilities': provider_capabilities()}, enable_status=args.status or args.links, enable_links=args.links, enable_controls=args.controls)
    try:
        signal.signal(signal.SIGTERM, stop_signal)
        with SocketLease(args.socket) as lease:
            with Server(str(lease.path), collector) as server:
                lease.record()
                collector.start()
                try:
                    server.serve_forever()
                finally:
                    collector.stop_event.set()
    except (OSError, InventoryError):
        raise SystemExit('Dashboard collector could not acquire its owned socket.') from None


if __name__ == '__main__':
    main()
