"""Additive owned runtime observation; no lifecycle/repair or project commands."""
import datetime
import http.client
import selectors
import signal
import secrets
import contextlib
import copy
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import hashlib
import json
import subprocess
import stat
import math
import os
from pathlib import Path
import re
import time
import urllib.request

import private_apps as app
from dashboard_inventory import identity, open_directory

SCHEMA_VERSION = 1
STATE_MAP = {'paused':'paused','pausing':'starting','resuming':'starting','ready':'ready','stopped':'stopped','preparing':'starting','starting':'starting',
             'failed':'failed','degraded':'degraded','unhealthy':'degraded','unpublished':'degraded',
             'recovery-required':'degraded','uninitialized':'stopped'}
HEALTH_MAP = {'ready':'healthy','unhealthy':'unhealthy','unknown':'unknown'}


def unsupported(reason='observation-unavailable'):
    return {'state':'unknown','provider_state':'unknown','health':'unknown','operation_busy':False,
            'reason':reason,'uptime_seconds':None,'uptime_reason':'unavailable',
            'restart_count':None,'restart_reason':'unavailable'}


def http_probe(port, path, timeout, *, html=False):
    """Fixed loopback HTTP only: no proxy, TLS trust-store load or redirects."""
    app.need(type(port) is int and 0 < port < 65536 and isinstance(path, str)
             and path.startswith('/') and not path.startswith('//')
             and not any(c in path for c in '\r\n'), 'conflict')
    connection = http.client.HTTPConnection('127.0.0.1', port, timeout=timeout)
    try:
        connection.request('GET', path)
        response = connection.getresponse()
        return response.status == 200 and (not html or
            response.getheader('Content-Type', '').split(';', 1)[0].strip().lower() == 'text/html')
    except (OSError, http.client.HTTPException):
        return False
    finally:
        connection.close()


def timing(obj, active, now):
    if not active:
        return {'uptime_seconds':None,'uptime_reason':'not-applicable',
                'restart_count':None,'restart_reason':'not-applicable','instance':None}
    value={'uptime_seconds':None,'uptime_reason':'unavailable','restart_count':None,
           'restart_reason':'unavailable','instance':None}
    count=obj.get('RestartCount')
    if type(count) is int and 0 <= count <= 2**31-1:
        value.update(restart_count=count,restart_reason=None)
    start=obj.get('State',{}).get('StartedAt')
    identifier=obj.get('Id')
    if not isinstance(start,str) or len(start)>64:
        return value
    if isinstance(identifier,str) and re.fullmatch(r'[0-9a-f]{64}',identifier):
        value['instance']=hashlib.sha256((identifier+'\0'+start).encode()).hexdigest()[:32]
    try:
        # Podman timestamps can contain nanoseconds; datetime uses microseconds.
        parsed=datetime.datetime.fromisoformat(start.replace('Z','+00:00'))
        if parsed.tzinfo is None or not math.isfinite(now):
            raise ValueError
        elapsed=now-parsed.timestamp()
        if not math.isfinite(elapsed) or elapsed < 0:
            value['uptime_reason']='clock-anomaly'
        else:
            value.update(uptime_seconds=int(elapsed),uptime_reason=None)
    except (ValueError,OverflowError):
        value['uptime_reason']='clock-anomaly'
    return value


def owned_inspection(name, token):
    if not app.object_owned('container',name,token):
        return None
    values=app.json_command(['podman','container','inspect',name])
    app.need(isinstance(values,list) and len(values)==1 and isinstance(values[0],dict),'conflict')
    obj=values[0]
    app.need(obj.get('Config',{}).get('Labels',{}).get(app.LABEL)==token,'conflict')
    return obj


def component(root, contract, *, now):
    slug=contract['project']['id']
    receipt=app.state_for(slug)
    if receipt is None:
        name='gptclaw-app-'+slug
        # A missing receipt must not mask an unowned unit/container with that name.
        app.need(not (app.UNITS/(name+'.container')).exists(),'conflict')
        app.need(app.command(['podman','container','exists',name],optional=True).returncode==1,'conflict')
        return {'state':'stopped','provider_state':'never-started','health':'unknown',
                'operation_busy':False,'reason':None,**timing({},False,now)}
    app.need(receipt['root']==str(root),'conflict')
    active, ready=app.inspect_service(receipt,contract)
    obj=owned_inspection(receipt['name'],receipt['token'])
    # Refuse inconsistent resource state instead of treating it as a successful stop.
    app.need(not active or obj is not None,'conflict')
    if obj is not None:
        app.need(type(obj.get('State',{}).get('Running')) is bool,'conflict')
        app.need((obj['State']['Running'] or obj['State'].get('Paused') is True)==active,'conflict')
    busy=app.object_owned('container',receipt['name']+'-job',receipt['token'])
    provider_state=('paused' if obj and obj.get('State',{}).get('Paused') else 'ready' if active and ready else 'unhealthy' if active else receipt['phase'])
    inconsistent = not active and receipt['phase']=='ready'
    if inconsistent: provider_state='resource-unavailable'
    return {'state':STATE_MAP.get(provider_state,'unknown'),'provider_state':provider_state,
            'health':'healthy' if ready else 'unhealthy' if active else 'unknown',
            'operation_busy':busy,'reason':'observation-inconsistent' if inconsistent else None,
            **timing(obj or {},active,now)}


def verify_database_container(receipt, obj):
    import project_database as db
    app.need(type(obj.get('State',{}).get('Running')) is bool,'conflict')
    actual=obj.get('Image','');actual=actual if actual.startswith('sha256:') else 'sha256:'+actual
    if obj.get('ImageName') == receipt['image']:
        # The creation reference is an exact immutable profile digest, also
        # matched by the verified unit. No mutable tag is accepted here.
        image_matches=True
    else:
        expected=app.command(['podman','image','inspect',receipt['image'],'--format','{{.Id}}']).stdout.strip()
        expected=expected if expected.startswith('sha256:') else 'sha256:'+expected
        image_matches=actual==expected
    app.need(image_matches and not obj.get('HostConfig',{}).get('PortBindings'),'conflict')


def database(root, contract, *, now):
    import project_database as db
    receipt=db.state(contract['project']['id'],root)
    if receipt is None:
        return {'state':'stopped','provider_state':'uninitialized','health':'unknown',
                'operation_busy':False,'reason':None,**timing({},False,now)}
    db.verify_unit(receipt)
    obj=owned_inspection(db.name(receipt),receipt['token'])
    active=bool(obj and obj.get('State',{}).get('Running'))
    if obj is not None:
        verify_database_container(receipt, obj)
    blocked=receipt['blocked'] or bool(receipt['operation'] and receipt['operation']['stage'] in {'failed','unknown'})
    ready=active and not blocked and db.ready(receipt,contract)
    state='recovery-required' if blocked else 'ready' if ready else 'unhealthy' if active else 'stopped'
    return {'state':STATE_MAP[state],'provider_state':state,
            'health':'healthy' if ready else 'unhealthy' if active else 'unknown',
            'operation_busy':bool(receipt['operation'] and receipt['operation']['stage']=='running'),
            'reason':None,**timing(obj or {},active,now)}


class CatalogueCache:
    """Reuse trusted semantic validation only while every input byte still matches.

    Never stores project files, receipts, native state or health. Directory descriptors
    avoid repeatedly walking every ancestor for hundreds of files in one provider.
    """
    def __init__(self, loader):
        import project_dependencies as deps
        self.root, self.loader = app.REPO, loader
        self.inputs = {}
        watched = (Path('config/templates'), Path('config/toolchains'))
        before = {p: tuple(sorted(os.listdir(self.root/p))) for p in watched}
        original = deps.read_bytes
        def read(path, limit=2*1024*1024):
            raw = original(path, limit)
            relative = Path(path).relative_to(self.root)
            app.need('..' not in relative.parts and relative.parts[0] in {'config','schemas','templates'}, 'path')
            app.need(relative not in self.inputs or self.inputs[relative] == raw, 'conflict')
            app.need(len(self.inputs) < 4096, 'conflict')
            self.inputs[relative] = raw
            return raw
        deps.read_bytes = read
        try:
            self.value = loader()
        finally:
            deps.read_bytes = original
        app.need(sum(map(len, self.inputs.values())) <= 64*1024*1024, 'conflict')
        # Optional versioned registries are selected by directory membership.
        directories = {p.parent for p in self.inputs} | {Path('config/templates'), Path('config/toolchains')}
        self.members = {p: tuple(sorted(os.listdir(self.root/p))) for p in directories}
        app.need(all(self.members[p] == names for p,names in before.items()), 'conflict')
        info = self.root.stat()
        self.identity = (info.st_dev, info.st_ino)

    def unchanged(self):
        if app.REPO != self.root:
            return False
        opened = {}
        try:
            opened[Path('.')] = open_directory(self.root)
            info = os.fstat(opened[Path('.')])
            if (info.st_dev, info.st_ino) != self.identity:
                return False
            def directory(relative):
                if relative not in opened:
                    parent = directory(relative.parent)
                    fd = os.open(relative.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=parent)
                    opened[relative] = fd
                return opened[relative]
            for relative, expected in self.inputs.items():
                fd = os.open(relative.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                             dir_fd=directory(relative.parent))
                with os.fdopen(fd, 'rb') as source:
                    info = os.fstat(source.fileno())
                    if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
                            or info.st_nlink != 1 or info.st_size != len(expected)
                            or source.read(len(expected)+1) != expected):
                        return False
            for relative, names in self.members.items():
                if tuple(sorted(os.listdir(directory(relative)))) != names:
                    return False
            # A replaced directory cannot make a retained descriptor hide drift.
            for relative, fd in opened.items():
                if relative == Path('.'):
                    continue
                actual = os.stat(relative.name, dir_fd=opened[relative.parent], follow_symlinks=False)
                pinned = os.fstat(fd)
                if (actual.st_dev, actual.st_ino) != (pinned.st_dev, pinned.st_ino):
                    return False
            return True
        except (OSError, ValueError):
            return False
        finally:
            for fd in opened.values():
                os.close(fd)

    def get(self, loader):
        if loader is self.loader and self.unchanged():
            return copy.deepcopy(self.value)
        return loader()


TRUSTED_CATALOGUE = None

def preload_catalogue():
    global TRUSTED_CATALOGUE
    import project_templates as templates
    try:
        TRUSTED_CATALOGUE = CatalogueCache(templates.catalogue)
    except (app.AppError, OSError, ValueError):
        # Inventory remains useful when optional provider contracts are invalid.
        TRUSTED_CATALOGUE = None


READ_LOCK = threading.Lock()
INSPECT_FORMAT = '[{"Id":{{json .ID}},"Image":{{json .Image}},"ImageName":{{json .ImageName}},"RestartCount":{{json .RestartCount}},"State":{"Running":{{json .State.Running}},"Paused":{{json .State.Paused}},"StartedAt":{{json .State.StartedAt}}},"Config":{"Labels":{{json .Config.Labels}}},"HostConfig":{"PortBindings":{{json .HostConfig.PortBindings}}}}]'


class DatabaseReaders:
    """Bounded authenticated read sessions; no database writes or arbitrary SQL."""
    def __init__(self, *, start=subprocess.Popen):
        self.start = start
        self.readers = {}
        self.closed = False
        self.lock = threading.Lock()

    @staticmethod
    def key(receipt, instance):
        return hashlib.sha256(json.dumps([receipt['project'], receipt['root'], receipt['active'],
            receipt['epoch'], receipt['token'], instance]).encode()).hexdigest()

    @staticmethod
    def close_process(process):
        try: process.stdin.close()
        except OSError: pass
        if process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                process.wait(timeout=.2)
            except subprocess.TimeoutExpired:
                try: os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError: pass
                process.wait()
        process.stdout.close()

    def close(self, *, shutdown=False):
        with self.lock:
            self.closed |= shutdown
            values, self.readers = list(self.readers.values()), {}
        for process in values:
            self.close_process(process)

    def revision(self, receipt, instance):
        import project_database as db
        key = self.key(receipt, instance)
        # Credential epoch and exact container instance bind each live session.
        try:
            with self.lock:
                app.need(not self.closed, 'database-command')
                process = self.readers.get(key)
                if process is not None and process.poll() is not None:
                    self.close_process(process); self.readers.pop(key); process = None
                if process is None:
                    app.need(len(self.readers) < 8, 'conflict')
                    argv = db.client(receipt, 'psql')
                    argv[2:2] = ['--env','PGCONNECT_TIMEOUT=1','--env',
                                'PGOPTIONS=-c statement_timeout=500 -c lock_timeout=500']
                    process = self.start([*argv,'-X','-A','-t','--set=ON_ERROR_STOP=1'],
                        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                        start_new_session=True)
                    self.readers[key] = process
        except (OSError, ValueError, app.AppError):
            return {'key': key, 'at': time.time(), 'error': 'database-command'}
        marker = 'gptclaw_'+secrets.token_hex(16)
        selector = selectors.DefaultSelector()
        try:
            process.stdin.write(('SELECT version_num FROM public.alembic_version;\n\\echo '+marker+'\n').encode())
            process.stdin.flush()
            selector.register(process.stdout, selectors.EVENT_READ)
            output = bytearray(); deadline = time.monotonic()+1
            while time.monotonic() < deadline:
                if not selector.select(max(.001, deadline-time.monotonic())):
                    break
                chunk = os.read(process.stdout.fileno(), 256)
                if not chunk: break
                output.extend(chunk)
                app.need(len(output) <= 256, 'database-command')
                if output.endswith((marker+'\n').encode()):
                    revision = output[:-len(marker)-1].decode().strip()
                    app.need(re.fullmatch(r'[A-Za-z0-9_]{1,32}', revision), 'database-schema')
                    return {'key': key, 'at': time.time(), 'revision': revision}
            raise app.AppError('database-command')
        except (OSError, ValueError, app.AppError):
            with self.lock:
                if self.readers.get(key) is process:
                    self.readers.pop(key)
            self.close_process(process)
            return {'key': key, 'at': time.time(), 'error': 'database-command'}
        finally:
            selector.close()

    def sample(self, bindings, native):
        import project_database as db
        if not isinstance(native, dict) or 'containers' not in native:
            self.close(); return
        targets = []
        keep = set()
        with cached_reads(native=native):
            for binding in bindings.values():
                if 'db' not in binding['components']: continue
                try:
                    root = Path(binding['root'])
                    app.need(identity(root.stat(follow_symlinks=False)) == tuple(binding['identity']), 'conflict')
                    receipt = db.state(binding['id'], root)
                    if not receipt or receipt['blocked'] or (receipt['operation'] and
                        receipt['operation']['stage'] in {'running','failed','unknown'}): continue
                    name = db.name(receipt); obj = native['containers'].get(name)
                    if not obj or not obj.get('State',{}).get('Running'): continue
                    app.need(obj.get('Config',{}).get('Labels',{}).get(app.LABEL) == receipt['token'], 'conflict')
                    instance = obj['Id']
                    app.need(re.fullmatch(r'[0-9a-f]{64}', instance), 'conflict')
                    db.verify_unit(receipt)
                    verify_database_container(receipt, obj)
                    key = self.key(receipt, instance)
                    if key not in keep:
                        keep.add(key); targets.append((name, receipt, instance))
                except (app.AppError, OSError, KeyError, TypeError, ValueError):
                    continue
        # Stop old generations and unused sessions before admitting replacements.
        with self.lock:
            removed = [self.readers.pop(key) for key in list(self.readers) if key not in keep]
        for process in removed: self.close_process(process)
        # Eight live sessions bound memory; additional DBs use the existing
        # isolated one-shot query in their worker, with the same health semantics.
        targets.sort(key=lambda item: self.key(item[1], item[2]) not in self.readers)
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = {pool.submit(self.revision, receipt, instance): name for name,receipt,instance in targets[:8]}
            native['database'] = {name: future.result() for future,name in futures.items()}


def native_job(bindings):
    """One narrow native read for a bounded inventory window, never browser targets."""
    import project_groups as groups
    import project_database as db
    names, networks, units = set(), set(), set()
    for binding in bindings[:20]:
        try:
            root, slug = Path(binding['root']), binding['id']
            app.need(identity(root.stat(follow_symlinks=False)) == tuple(binding['identity']), 'conflict')
            app.need(re.fullmatch(r'[a-z][a-z0-9]*(?:-[a-z0-9]+)*', slug) and len(slug) <= 48, 'conflict')
            components = binding['components']
            grouped = len(components) > 1
            for component_name in components:
                if component_name == 'db':
                    receipt = db.state(slug, root)
                    if receipt:
                        container = db.name(receipt)
                        names.add(container); units.add(container+'.service')
                    continue
                component_id = groups.identity(slug, component_name) if grouped else slug
                container = 'gptclaw-app-'+component_id
                names.update((container, container+'-job')); units.add(container+'.service')
            if grouped:
                networks.add('gptclaw-group-'+slug+'-contract')
        except (app.AppError, OSError, KeyError, TypeError, ValueError):
            # Each worker still revalidates its own exact binding/receipts.
            continue
    app.need(len(names) <= 100 and len(units) <= 80, 'conflict')
    result = {'at': time.time(), 'names': sorted(names), 'containers': {}, 'units': {},
              'network_names': sorted(networks), 'networks': [], 'globals': {}}
    if names:
        pattern = '^('+'|'.join(re.escape(n) for n in sorted(names))+')$'
        listed = app.command(['podman','ps','--all','--filter','name='+pattern,'--format','{{.Names}}'], timeout=3)
        present = listed.stdout.splitlines()
        app.need(len(present) == len(set(present)) and set(present) <= names, 'conflict')
        if present:
            formatted = INSPECT_FORMAT.replace('{"Id":', '{"Name":{{json .Name}},"Id":', 1)
            inspected = app.command(['podman','container','inspect',*present,'--format',formatted], timeout=3)
            for line in inspected.stdout.splitlines():
                objects = json.loads(line)
                app.need(isinstance(objects, list) and len(objects) == 1, 'conflict')
                obj = objects[0]; name = obj.pop('Name').lstrip('/')
                app.need(name in present and name not in result['containers'], 'conflict')
                result['containers'][name] = obj
            app.need(set(result['containers']) == set(present), 'conflict')
    if units:
        properties = ['Id','SourcePath','FragmentPath','DropInPaths','ActiveState','SubState','LoadState']
        shown = app.command(['systemctl','--user','show',*sorted(units),
                            *[item for prop in properties for item in ['-p',prop]]], timeout=3)
        for block in shown.stdout.strip().split('\n\n'):
            fields = dict(line.split('=',1) for line in block.splitlines() if '=' in line)
            name = fields.pop('Id', None)
            app.need(name in units and name not in result['units'], 'conflict')
            result['units'][name] = fields
        app.need(set(result['units']) == units, 'conflict')
    if networks:
        pattern = '^('+'|'.join(re.escape(n) for n in sorted(networks))+')$'
        listed = app.command(['podman','network','ls','--filter','name='+pattern,'--format','{{.Name}}'], timeout=3)
        result['networks'] = listed.stdout.splitlines()
        app.need(set(result['networks']) <= networks, 'conflict')
    for argv in (['tailscale','status','--json'], ['tailscale','serve','status','--json']):
        observed = app.command(argv, timeout=3, optional=True)
        output = observed.stdout
        if argv[1] == 'status' and observed.returncode == 0:
            value = json.loads(output)
            output = json.dumps({'BackendState': value.get('BackendState'), 'Self': {
                key: value.get('Self',{}).get(key) for key in ('Online','DNSName')}})
        result['globals'][' '.join(argv)] = {'code': observed.returncode, 'out': output}
    return result


def native_read(snapshot, argv):
    """Translate only exact read shapes; ownership checks still consume the result."""
    if not isinstance(snapshot, dict) or not isinstance(snapshot.get('at'), (int,float)):
        return None
    age = time.time()-snapshot['at']
    if not 0 <= age <= 10:
        return None
    if argv[:3] == ['podman','container','exists'] and len(argv) == 4 and argv[3] in snapshot.get('names',[]):
        return subprocess.CompletedProcess(argv, 0 if argv[3] in snapshot['containers'] else 1, '', '')
    if argv[:3] == ['podman','container','inspect'] and len(argv) == 4 and argv[3] in snapshot.get('names',[]):
        obj = snapshot['containers'].get(argv[3])
        return subprocess.CompletedProcess(argv, 0 if obj else 125, json.dumps([obj]) if obj else '', '')
    if argv[:3] == ['podman','network','exists'] and len(argv) == 4 and argv[3] in snapshot.get('network_names',[]):
        return subprocess.CompletedProcess(argv, 0 if argv[3] in snapshot['networks'] else 1, '', '')
    if argv[:3] == ['systemctl','--user','is-active'] and len(argv) == 4 and argv[3] in snapshot.get('units',{}):
        state = snapshot['units'][argv[3]].get('ActiveState', 'unknown')
        return subprocess.CompletedProcess(argv, 0 if state == 'active' else 3, state+'\n', '')
    if argv[:3] == ['systemctl','--user','show'] and len(argv) >= 6 and argv[3] in snapshot.get('units',{}):
        tail = argv[4:]
        if len(tail)%2 == 0 and all(tail[i] == '-p' for i in range(0,len(tail),2)):
            fields = snapshot['units'][argv[3]]
            if all(prop in fields for prop in tail[1::2]):
                return subprocess.CompletedProcess(argv, 0, ''.join(prop+'='+fields[prop]+'\n' for prop in tail[1::2]), '')
    value = snapshot.get('globals',{}).get(' '.join(argv))
    if value is not None:
        return subprocess.CompletedProcess(argv, value['code'], value['out'], '')
    return None


@contextlib.contextmanager
def cached_reads(*, native=None):
    # Each collector worker observes one project in its own process. Scope and
    # restore this adapter so ordinary CLI/lifecycle commands keep their behavior.
    with READ_LOCK:
        original = app.command
        original_bundle = app.provider_bundle
        original_healthy = app.healthy
        import project_manifest as manifests
        original_parse = manifests.parse_manifest
        parsed = {}
        def parse(text):
            if text not in parsed:
                if len(parsed) >= 16:
                    parsed.clear()
                parsed[text] = original_parse(text)
            return copy.deepcopy(parsed[text])
        import project_templates as templates
        original_catalogue = templates.catalogue
        catalogue_value = []
        health_cache = {}
        def catalogue():
            # One project read sees one fully validated trusted catalogue. Never
            # retain this cache across workers/refreshes or cache project inputs.
            if not catalogue_value:
                catalogue_value.append(TRUSTED_CATALOGUE.get(original_catalogue) if TRUSTED_CATALOGUE else original_catalogue())
            return copy.deepcopy(catalogue_value[0])
        import project_database as db
        original_revision = db.revision
        original_save, original_save_text = app.save, app.save_text
        cache = {}
        def command(argv, timeout=300, optional=False):
            readonly = (argv[:3] in [['podman','container','inspect'], ['podman','container','exists'],
                                    ['podman','network','exists'], ['podman','network','inspect'],
                                    ['podman','image','inspect']]
                        or argv[:3] in [['systemctl','--user','show'], ['systemctl','--user','is-active']]
                        or argv in [['tailscale','status','--json'], ['tailscale','serve','status','--json']]
                        or argv[:2] == ['mountpoint','-q'])
            app.need(readonly, 'conflict')
            key = (tuple(argv), optional)
            if readonly and key in cache:
                return cache[key]
            shared = native_read(native, argv)
            if shared is not None:
                if shared.returncode and not optional:
                    raise app.AppError('command')
                cache[key] = shared
                return shared
            vector = list(argv)
            if vector[:3] == ['podman','container','exists'] and len(vector)==4 and not vector[3].endswith('-job'):
                inspected = original(['podman','container','inspect',vector[3],'--format',INSPECT_FORMAT],timeout=timeout,optional=True)
                if inspected.returncode == 0:
                    cache[(('podman','container','inspect',vector[3]),False)] = inspected
                    result = subprocess.CompletedProcess(argv,0,'','')
                    cache[key] = result
                    return result
                # Inspect errors alone cannot prove absence; preserve the existing
                # exists protocol to distinguish missing from command failure.
            if vector[:3] == ['podman','container','inspect'] and len(vector)==4:
                # Query only ownership, binding and timing fields; never request
                # raw environment, mounts or other container configuration.
                vector += ['--format', INSPECT_FORMAT]
            result = original(vector, timeout=timeout, optional=optional)
            if readonly:
                cache[key] = result
            return result
        def healthy(receipt, contract):
            # Lifecycle probes may wait five seconds. Dashboard reads must leave
            # room for ownership/timing checks inside the four-second budget.
            service = contract['service']
            bounded = {**contract, 'service': {**service, 'health': {
                **service['health'], 'timeout_seconds': min(
                    service['health']['timeout_seconds'], .5)}}}
            key = (receipt['port'], service['health']['path'])
            if key not in health_cache:
                health_cache[key] = http_probe(receipt['port'], service['health']['path'],
                                               bounded['service']['health']['timeout_seconds'])
            return health_cache[key]
        def revision(receipt, generation=None):
            # One authenticated read proves connectivity and migration revision.
            # A missing table fails readiness without a second native query.
            name = db.name(receipt, generation) if isinstance(native,dict) else None
            proof = native.get('database',{}).get(name) if isinstance(native,dict) else None
            obj = native.get('containers',{}).get(name) if isinstance(native,dict) else None
            if proof is not None and obj is not None and generation is None:
                app.need(proof.get('key') == DatabaseReaders.key(receipt, obj.get('Id'))
                         and 0 <= time.time()-proof.get('at',0) <= 10
                         and 'error' not in proof, 'database-command')
                value = proof.get('revision', '')
            else:
                value = db.sql(receipt, 'SELECT version_num FROM public.alembic_version;',
                               generation).strip()
            app.need(re.fullmatch(r'[A-Za-z0-9_]{1,32}', value), 'database-schema')
            return value
        def refuse_write(*_, **__):
            raise app.AppError('conflict')
        app.command = command
        app.healthy = healthy
        manifests.parse_manifest = parse
        templates.catalogue = catalogue
        db.revision = revision
        # verify_unit compares trusted bootstrap bytes. It needs no snapshot
        # publication while observing from source or an installed snapshot.
        app.provider_bundle = lambda: app.REPO
        app.save = app.save_text = refuse_write
        try:
            yield
        finally:
            app.command = original
            app.healthy = original_healthy
            manifests.parse_manifest = original_parse
            templates.catalogue = original_catalogue
            db.revision = original_revision
            app.provider_bundle = original_bundle
            app.save, app.save_text = original_save, original_save_text


def project(root, *, expected=None, clock=time.time):
    with cached_reads(native=expected.get('_native') if expected else None):
        return _project(root, expected=expected, clock=clock)


def _project(root, *, expected=None, clock=time.time):
    now=clock()
    fd=open_directory(Path(root))
    try:
        before=identity(os.fstat(fd))
        if expected is not None:
            app.need(tuple(expected['identity'])==before and expected['root']==str(Path(root)),'conflict')
        root, contract=app.target(root)
        slug=contract['project']['id']
        if expected is not None:
            app.need(slug==expected['id'],'conflict')
        if contract['schema_version'] in (6,9,11,12):
            import metro_sessions
            from dashboard_metro import project as native_project
            descriptor=metro_sessions.status(root)
            native=native_project(descriptor,slug)
            import expo_go
            from dashboard_go import project as go_project
            try:go=go_project(expo_go.presentation(root,descriptor),slug,native)
            except app.AppError:go=None
            app.need(native is not None,'conflict')
            state=native['state']
            overall='ready' if state=='ready' else 'stopped' if state in {'not-started','stopped','expired'} else 'starting' if state in {'preparing','starting','stopping','loopback-running'} else 'failed' if state=='failed' else 'degraded'
            result={'observation_schema':SCHEMA_VERSION,'provider_version':app.VERSION,'project':slug,
                    'observed_at':now,'components':{},'state':overall,'provider_state':overall,
                    'health':'not-applicable','operation_busy':False,'reason':None,'metro':descriptor,'expo_go':go,
                    'publication':{'state':'unavailable','origin':None},
                    'routes':{'schema_version':1,'project':slug,'app_path':None,'docs_path':None}}
            app.need(identity(Path(root).stat(follow_symlinks=False))==before,'conflict')
            return result
        receipt=app.state_for(slug)
        result={'observation_schema':SCHEMA_VERSION,'provider_version':app.VERSION,'project':slug,
                'observed_at':now,'components':{},'state':'unknown','provider_state':'unknown',
                'health':'unknown','operation_busy':False,'reason':None}
        if contract['schema_version'] in (3,4,8):
            import project_groups as groups
            if receipt:
                app.need(receipt['root']==str(root),'conflict')
            with groups.scope(root,contract) as children:
                with ThreadPoolExecutor(max_workers=3) as pool:
                    futures={pool.submit(component,child,declaration,now=now):name for name,(child,declaration) in children.items()}
                    if contract['schema_version'] in (4,8):
                        futures[pool.submit(database,root,contract,now=now)]='db'
                    for future in as_completed(futures):
                        name=futures[future]
                        try:result['components'][name]=future.result()
                        except app.AppError as error:
                            result['components'][name]=unsupported('ownership-conflict' if error.code in {'conflict','path'} else 'observation-unavailable')
                        except (OSError,ValueError,TypeError,KeyError,AttributeError):
                            result['components'][name]=unsupported('observation-unavailable')
            state='stopped' if receipt is None else receipt['phase']
            healthy=bool(result['components']) and all(c['state']=='ready' and c['health']=='healthy' for c in result['components'].values())
            if state=='ready' and not healthy:state='degraded'
            result.update(provider_state=state,state=STATE_MAP.get(state,'unknown'),
                          health='healthy' if healthy and state=='ready' else 'unhealthy' if state=='degraded' else 'unknown')
            result['operation_busy']=any(c['operation_busy'] for c in result['components'].values())
            if receipt:
                result['operation_busy'] |= app.object_owned('network',receipt['network']+'-contract',receipt['token'])
                if result['state']=='ready' and (not receipt['health_ready'] or result['operation_busy']
                        or receipt.get('operation_result') in {'running','unknown'}):
                    result.update(state='degraded',provider_state='unpublished',health='unknown')
            elif any(c['state']!='stopped' for c in result['components'].values()):
                result.update(state='unknown',provider_state='resource-unavailable',health='unknown',reason='observation-inconsistent')
        else:
            current=component(root,contract,now=now)
            result['components'][contract['project']['kind']]=current
            result.update({field:current[field] for field in ('state','provider_state','health','operation_busy','reason')})
            if receipt and result['state']=='ready' and (receipt['phase']!='ready' or not receipt['health_ready']):
                result.update(state='degraded',provider_state='unpublished',health='unhealthy')
        # Publication requires a configured owned Serve route, but route failure must
        # not erase independently observed component health.
        try:
            route=app.route_info(slug)
            published=bool(receipt and receipt['phase']=='ready' and receipt['health_ready']
                           and result['state']=='ready' and result['health']=='healthy' and not result['operation_busy']
                           and route.get('state')=='configured')
            result['publication']={'state':'published' if published else 'unavailable',
                                   'origin':route['url'].split('/projects/',1)[0] if route.get('url') else None}
        except app.AppError:
            result['publication']={'state':'unavailable','origin':None}
        result['routes']=route_descriptor(root,contract,result)
        if identity(Path(root).stat(follow_symlinks=False)) != before:
            raise app.AppError('conflict')
        return result
    finally:
        os.close(fd)


def route_descriptor(root, contract, result):
    slug=contract['project']['id']
    descriptor={'schema_version':1,'project':slug,'app_path':None,'docs_path':None}
    if contract['project']['kind'] in {'web','group'} and contract['schema_version']!=8:
        descriptor['app_path']='/projects/'+slug+'/'
    if contract['project']['kind'] not in {'api','group'}:
        return descriptor
    path='/projects/'+slug+('/docs' if contract['schema_version']==2 else '/api/docs')
    # This is the fixed docs capability of the already validated supported
    # adapter, never a browser/manifest-supplied destination or path crawl.
    if result['publication']['state']=='published':
        single=contract['schema_version'] in (2,7)
        target=root if single else root/contract['components']['api']['root']
        from project_groups import identity as group_identity
        name=slug if single else group_identity(slug,'api')
        receipt=app.state_for(name)
        if receipt and receipt['root']==str(target):
            if http_probe(receipt['port'], path, .25, html=True):
                descriptor['docs_path']=path
    return descriptor


def job(binding):
    try:return project(binding['root'],expected=binding)
    except Exception:
        return {'error':'observation-unavailable'}
