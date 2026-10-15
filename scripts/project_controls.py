"""Typed lifecycle primitives shared by CLI and dashboard; no caller supplied argv.

The outer project lock covers native effects and the durable guard prevents a
second writer after an interrupted operation. Reads never clear that guard.
"""
import contextlib
from contextvars import ContextVar
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import time
import uuid

import private_apps as app

SCHEMA = 1
ACTIONS = ('start', 'stop', 'restart', 'rebuild', 'pause', 'resume')
COMPONENTS = ('web', 'api', 'db', 'metro')
OWNER = ContextVar('lifecycle_operation', default=None)
HELD = ContextVar('lifecycle_project_lock', default=None)
RECONCILING = ContextVar('lifecycle_reconciling', default=False)
EXCLUDED = {'.git', 'node_modules', '.venv', '.next', '.gptclaw-cache', '.cache',
            '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache', 'dist', 'coverage', '.coverage'}
MAX_SOURCE = 64 * 1024 * 1024
MAX_FILES = 10000
SECRET_NAMES = {'.aws', '.ssh', '.secrets', '.netrc', '.npmrc', '.pypirc', 'auth.json', 'id_rsa', 'id_ed25519'}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def guard_path(project):
    app.need(isinstance(project, str) and re.fullmatch(r'[a-z][a-z0-9]*(?:-[a-z0-9]+)*', project) and len(project) <= 48, 'invalid')
    return app.STORE/'control-guards'/f'{project}.json'


def check_guard(project):
    # Non-project locks have no lifecycle guard. Nested component operations are
    # covered by the parent lock; component roots cannot be invoked independently.
    if not re.fullmatch(r'[a-z][a-z0-9]*(?:-[a-z0-9]+)*', project) or len(project) > 48:
        return
    value = app.read_json(app.STORE/'control-guards'/f'{project}.json')
    if value is not None:
        app.need(isinstance(value, dict) and set(value) == {'schema_version', 'project', 'operation_id', 'root'}
                 and value['schema_version'] == SCHEMA and value['project'] == project
                 and isinstance(value['operation_id'], str) and re.fullmatch(r'[0-9a-f]{32}', value['operation_id']), 'control-recovery')
        app.need(OWNER.get() == value['operation_id'], 'control-recovery')


@contextlib.contextmanager
def project_lock(project):
    with app.locked(project):
        token = HELD.set(project)
        try:
            yield
        finally:
            HELD.reset(token)


@contextlib.contextmanager
def source_lock(root):
    root = app.safe(Path(root).absolute())
    key = hashlib.sha256(str(root).encode()).hexdigest()
    with app.locked('control-source-'+key):
        result, value, code = app.validate_project(root)
        if code == 0:
            check_guard(value['project']['id'])
        yield


def source_files(root):
    """Bounded owned regular source only; never follows links or copies secrets."""
    root = app.safe(root)
    result = {}
    total = 0
    folders = 0
    for folder, directories, names in os.walk(root, followlinks=False):
        folders += 1
        app.need(folders <= MAX_FILES, 'control-capacity')
        directories[:] = sorted(d for d in directories if d not in EXCLUDED)
        for name in directories:
            app.need(name not in SECRET_NAMES and not name.startswith('.env'), 'invalid')
            path = Path(folder)/name
            info = path.lstat()
            app.need(stat.S_ISDIR(info.st_mode) and info.st_uid == os.getuid(), 'path')
        for name in sorted(names):
            if name in EXCLUDED:
                continue
            app.need(not name.startswith('.env') and name not in SECRET_NAMES and not name.endswith(('.pem', '.key')), 'invalid')
            path = Path(folder)/name
            info = path.lstat()
            app.need(stat.S_ISREG(info.st_mode) and info.st_uid == os.getuid() and info.st_nlink == 1, 'path')
            total += info.st_size
            app.need(total <= MAX_SOURCE and len(result) < MAX_FILES, 'control-capacity')
            fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
            with os.fdopen(fd, 'rb') as stream:
                current = os.fstat(stream.fileno())
                app.need((current.st_dev, current.st_ino, current.st_mtime_ns, current.st_size) ==
                         (info.st_dev, info.st_ino, info.st_mtime_ns, info.st_size), 'control-changed')
                data = stream.read(MAX_SOURCE + 1)
                app.need(len(data) <= MAX_SOURCE, 'control-capacity')
            result[str(path.relative_to(root))] = hashlib.sha256(data).hexdigest()
    return result


def runtime_rows(root, value):
    """Return private validated runtime identities and native state, never reserve."""
    import project_groups as groups
    project = value['project']['id']
    parent = app.state_for(project)
    if parent:
        app.need(parent['root'] == str(root), 'conflict')
    if value['schema_version'] in (3, 4, 8):
        with groups.scope(root, value) as resolved:
            rows = {name: inspect_component(path, contract) for name, (path, contract) in resolved.items()}
        if value['schema_version'] in (4, 8):
            import project_database as db
            owned = db.state(project, root)
            active = bool(owned and db.active(owned))
            rows['db'] = {'active': active, 'ready': bool(active and not owned['blocked'] and db.ready(owned, value)),
                          'paused': False, 'busy': bool(owned and (db.busy(owned) or owned['operation'] and owned['operation']['stage'] in {'running', 'unknown', 'failed'})),
                          'generation': digest({k: owned[k] for k in ('token', 'active', 'epoch', 'revision')}) if owned else None,
                          'receipt': owned, 'root': str(root)}
        return parent, rows
    if value['schema_version'] in (6, 9):
        import metro_sessions as metro
        owned = metro.load(project, root)
        if owned:
            metro.admitted(owned)
            app.need(time.time() < owned['expires_at'], 'control-expired')
            data=metro.control(owned, allow_frozen=True)
            metro.contract.inputs(root)
            metro.require_idle(root,project)
            identity=metro.worktrees.canonical(root)
            app.need(identity['key']==owned['canonical_key'] and identity['root_identity']==data['root_identity']
                     and metro.mount_identities(root)==data['mount_identities']
                     and owned['input_digest']==metro.digest(metro.hashes(root)), 'control-changed')
            if owned['phase'] == 'running':
                metro.verify_unit(owned)
                app.need(metro.ownership('container', owned['name'], owned['token']) == 'owned', 'conflict')
            app.need(owned['phase'] in {'running', 'stopped'}, 'control-recovery')
        return None, {'metro': {'active': bool(owned and owned['phase'] == 'running'),
                               'ready': bool(owned and owned['phase'] == 'running'), 'paused': False,
                               'busy': False, 'generation': digest(owned) if owned else None,
                               'receipt': owned, 'root': str(root)}}
    return parent, {value['project']['kind']: inspect_component(root, value)}


def inspect_component(root, contract):
    s = app.state_for(contract['project']['id'])
    if not s:
        name = 'gptclaw-app-'+contract['project']['id']
        app.need(not app.unit_path({'name': name}).exists(), 'conflict')
        app.need(not app.object_owned('container', name, ''), 'conflict')
        return {'active': False, 'ready': False, 'paused': False, 'busy': False, 'generation': None, 'receipt': None, 'root': str(root)}
    app.need(s['root'] == str(root), 'conflict')
    exists = app.object_owned('container', s['name'], s['token'])
    obj = app.json_command(['podman', 'container', 'inspect', s['name']])[0] if exists else {}
    paused = obj.get('State', {}).get('Paused') is True
    active, ready = app.inspect_service(s, contract) if s['unit_sha256'] != '0'*64 else (False, False)
    app.need(not active or exists, 'conflict')
    app.need(RECONCILING.get() or s.get('operation_result') not in {'running', 'unknown'}, 'control-recovery')
    app.need(obj.get('State', {}).get('Running', False) == active, 'control-recovery')
    return {'active': active, 'ready': ready and not paused, 'paused': paused,
            'busy': app.object_owned('container', s['name']+'-job', s['token']),
            'generation': digest({'id': obj.get('Id'), 'started': obj.get('State', {}).get('StartedAt'),
                                  'receipt': s}), 'receipt': s, 'root': str(root)}


def inspect(root, *, include_source=True):
    root, value = app.target(root)
    app.need(value['schema_version'] in (1, 2, 3, 4, 6, 7, 8, 9), 'invalid')
    parent, rows = runtime_rows(root, value)
    info = root.stat(follow_symlinks=False)
    source = source_files(root) if include_source else {}
    selected = {'root': str(root), 'identity': [info.st_dev, info.st_ino, info.st_uid],
                'manifest': digest(value), 'source': digest(source),
                'runtimes': {name: row['generation'] for name, row in rows.items()}}
    return root, value, parent, rows, digest(selected)


def eligibility(value, rows, action, component=None):
    app.need(action in ACTIONS and (component is None or component in COMPONENTS), 'invalid')
    if component is not None and (action != 'restart' or component not in rows):
        return 'control-unsupported'
    native = 'metro' in rows
    database = 'db' in rows
    if native and rows['metro'].get('receipt') is None:
        return 'control-unsupported'
    if native and (action == 'restart' or action == 'start' and not rows['metro']['active']) and rows['metro']['receipt'].get('expires_at',time.time()+60)-time.time()<60:
        return 'control-expired'
    if (native and action in {'rebuild', 'pause', 'resume'}) or (database and action in {'pause', 'resume'}):
        return 'control-unsupported'
    if database and action not in {'stop','rebuild'} and (rows['db'].get('receipt') is None or rows['db']['receipt'].get('blocked')):
        return 'database-recovery'
    if any(row['busy'] for row in rows.values()):
        return 'busy'
    paused = [row['paused'] for row in rows.values()]
    if any(paused) and not all(paused) and action != 'stop':
        return 'control-recovery'
    if action in {'restart', 'rebuild', 'start'} and any(paused):
        return 'control-paused'
    if action == 'pause' and (not all(row['ready'] for row in rows.values()) or any(paused)):
        return 'control-state'
    if action == 'resume' and not all(paused):
        return 'control-state'
    if component:
        if not rows[component]['active'] or rows[component]['paused']:
            return 'control-state'
        dependencies = value.get('components', {}).get(component, {}).get('depends_on', [])
        if not all(rows[name]['ready'] for name in dependencies):
            return 'control-dependency'
    return None


def capabilities(root):
    root, value, parent, rows, generation = inspect(root)
    check_guard(value['project']['id'])
    actions = []
    for component, verbs in [(None, ACTIONS), *[(name, ('restart',)) for name in rows]]:
        for action in verbs:
            reason = eligibility(value, rows, action, component)
            actions.append({'action': action, 'component': component, 'enabled': reason is None, 'reason': reason})
    return {'schema_version': SCHEMA, 'provider_version': app.VERSION, 'generation': generation,
            'project': value['project']['id'], 'name': value['project']['name'], 'actions': actions,
            'components': list(rows), 'observed_at': time.time()}


def impact(value, action, component):
    target = component.upper() if component else 'entire project'
    parts = [f'{action.capitalize()} {target}.']
    if action in {'stop', 'restart', 'rebuild', 'pause'}:
        parts.append('Active connections and in-flight requests may be interrupted.')
    if component == 'db':
        parts.append('Database records are retained. API/web stay running but requests may fail until database reconnection.')
    if (value.get('data', {}).get('mode') == 'ephemeral' and
            (component == 'api' or component is None) and action in {'stop', 'restart', 'rebuild'}):
        parts.append('API in-memory data can be lost.')
    if action == 'rebuild':
        parts.append('Build current locked source; retain persistent database data and leave a stopped project stopped.')
    if action == 'pause':
        parts.append('Freeze stateless processes and withdraw private app links until Resume reaches readiness.')
    if value['schema_version'] in (6, 9):
        parts.append('The bound backend is unchanged; session authorization and transport are preserved.')
    return ' '.join(parts)


def save_parent(s):
    if s.get('schema_version') in (2, 3, 4):
        __import__('project_groups').save(s)
    else:
        app.valid_state(s)
        app.save(app.STORE/(s['id']+'.json'), s)


def publication(parent, ready, phase=None):
    if parent is None:
        return
    parent['health_ready'] = ready
    if phase:
        parent['phase'] = phase
    save_parent(parent)


def restart_runtime(s, contract, stage, prepared=None):
    """Replace the owned runtime with its already prepared image/configuration."""
    app.need(s is not None and s['unit_sha256'] != '0'*64, 'control-state')
    app.verify_unit(s)
    app.need(app.object_owned('container', s['name'], s['token']), 'conflict')
    stage('stop', s.get('component', contract['project']['kind']))
    app.command(['systemctl', '--user', 'stop', s['name']+'.service'], timeout=90)
    if prepared is not None:
        install_prepared(s, contract, prepared, stage)
    stage('start', s.get('component', contract['project']['kind']))
    app.command(['systemctl', '--user', 'start', s['name']+'.service'], timeout=300)
    wait_ready(s, contract)
    s.update(phase='ready', health_ready=True)
    app.save(app.STORE/(s['id']+'.json'), s)


def wait_ready(s, contract):
    until = time.monotonic()+app.DEADLINE
    while time.monotonic() < until:
        if app.inspect_service(s, contract) == (True, True):
            return
        time.sleep(1)
    raise app.AppError('health')


def restart_selected(root, value, parent, rows, component, stage, require_all=True, prepared=None):
    import project_groups as groups
    publication(parent, False)
    if component == 'db':
        import project_database as db
        owned = rows['db']['receipt']
        app.need(owned is not None and not owned['blocked'] and not db.busy(owned), 'database-recovery')
        stage('stop', 'db'); db.stop(owned)
        stage('start', 'db'); db.start(owned)
        app.need(db.ready(owned, value), 'database-health')
    elif value['schema_version'] in (3, 4, 8):
        with groups.scope(root, value) as resolved:
            restart_runtime(rows[component]['receipt'], resolved[component][1], stage, prepared)
    else:
        restart_runtime(rows[component]['receipt'], value, stage, prepared)
    stage('observe', component)
    _, after = runtime_rows(root, value)
    ready = all(row['ready'] for row in after.values())
    if component=='db' and require_all and not ready:
        until=time.monotonic()+app.DEADLINE
        while not ready and time.monotonic()<until:
            time.sleep(1)
            _,after=runtime_rows(root,value)
            ready=all(row['ready'] for row in after.values())
    publication(parent, ready, 'ready' if ready else 'failed')
    if require_all:
        app.need(ready, 'control-dependency')


def freeze(root, value, parent, rows, action, stage):
    ordered = [name for name in ('api', 'web') if name in rows]
    if action == 'pause':
        ordered.reverse()
        publication(parent, False, 'pausing')
    else:
        publication(parent, False, 'resuming')
    for name in ordered:
        s = rows[name]['receipt']
        app.need(s is not None, 'control-state')
        app.verify_unit(s)
        app.need(app.object_owned('container', s['name'], s['token']), 'conflict')
        stage(action, name)
        app.command(['podman', 'pause' if action == 'pause' else 'unpause', s['name']], timeout=30)
        obj = app.json_command(['podman', 'container', 'inspect', s['name']])[0]
        app.need(obj.get('State', {}).get('Paused') is (action == 'pause'), 'control-state')
        s.update(phase='paused' if action == 'pause' else 'starting', health_ready=False)
        app.save(app.STORE/(s['id']+'.json'), s)
        if action == 'resume':
            with (__import__('project_groups').scope(root, value) if value['schema_version'] == 3 else contextlib.nullcontext({name: (root, value)})) as resolved:
                wait_ready(s, resolved[name][1])
            s.update(phase='ready', health_ready=True)
            app.save(app.STORE/(s['id']+'.json'), s)
    publication(parent, action == 'resume', 'ready' if action == 'resume' else 'paused')


def build_sources(root, value, rows, stage, ident):
    """Build a bounded source copy; failed preparation cannot change live outputs."""
    import project_groups as groups
    import project_dependencies as deps
    import project_python as py
    import project_toolchains as tools
    paths = groups.scope(root, value) if value['schema_version'] in (3, 4, 8) else contextlib.nullcontext({value['project']['kind']: (root, value)})
    builds = {}
    build_root=app.safe(app.STORE/'control-builds')
    build_root.mkdir(mode=0o700,parents=True,exist_ok=True)
    app.need(len(list(build_root.iterdir())) < 8, 'control-capacity')
    app.need(shutil.disk_usage(build_root).free >= 2*1024**3, 'control-capacity')
    private_stage=build_root/ident
    private_stage.mkdir(mode=0o700)
    app.save(private_stage/'owner.json', {'schema_version':1,'operation_id':ident,'project':value['project']['id'],'created_at':time.time()})
    with paths as resolved:
        for name, (path, contract) in resolved.items():
            stage('build', name)
            original = source_files(path)
            selected = tools.selection(path)
            image = app.toolchain(path, selected)
            dest = app.safe(app.STORE/'control-builds'/ident/name)
            app.need(not dest.exists(), 'conflict')
            dest.mkdir(mode=0o700, parents=True)
            for rel in original:
                out = dest/rel
                out.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
                shutil.copyfile(path/rel, out, follow_symlinks=False)
            app.need(source_files(dest) == original and source_files(path) == original, 'control-changed')
            # These are independent finite build jobs with separate owned names.
            s = {'id': value['project']['id'], 'name': 'gptclaw-build-'+ident+'-'+name,
                 'root': str(dest), 'token': ident, 'image': image,
                 **({'adapter': 'python'} if py.is_python(path) else {})}
            if py.is_python(path):
                py.install(s, dest)
            else:
                app.run_in_app(s, ['pnpm', 'install', '--frozen-lockfile', *deps.INSTALL_FLAGS], timeout=600, read_only_dependency_files=True)
            app.run_in_app(s, contract['commands']['build'], timeout=600, read_only_dependency_files=True)
            app.need(source_files(path) == original, 'control-changed')
            builds[name] = {'directory': str(dest), 'image': image, 'toolchain_hash': selected['selection_hash'],
                            'source': digest(original)}
    return builds


def install_prepared(s, contract, prepared, stage):
    # Switch only generated build/dependency directories after this component
    # stops. Retain displaced outputs for explicit recovery; never edit source.
    root = Path(s['root'])
    app.need(digest(source_files(root)) == prepared['source'], 'control-changed')
    dest = app.safe(Path(prepared['directory']))
    app.need(dest.is_relative_to(app.STORE/'control-builds'), 'path')
    import project_python as py
    generated = ['.venv'] if py.is_python(root) else ['node_modules', '.next', 'dist']
    stage('publish-build', s.get('component', contract['project']['kind']))
    app.need(not app.inspect_service(s, contract)[0], 'busy')
    if app.object_owned('container',s['name'],s['token']):
        app.need(not app.json_command(['podman','container','inspect',s['name']])[0].get('State',{}).get('Running'), 'control-recovery')
    app.save(dest/'build.json', {'schema_version':1, 'project':s['id'], **prepared})
    for name in generated:
        incoming = dest/name
        if not incoming.exists():
            continue
        old = root/name
        for path in (incoming, old):
            if path.exists() or path.is_symlink():
                info = path.lstat()
                app.need(stat.S_ISDIR(info.st_mode) and info.st_uid == os.getuid(), 'path')
        retained = dest/('previous-'+name.lstrip('.'))
        app.need(not retained.exists(), 'conflict')
        stage('publish-'+name.lstrip('.'), s.get('component', contract['project']['kind']))
        if old.exists():
            os.rename(old, retained)
        os.rename(incoming, old)
    s.update(image=prepared['image'], toolchain_hash=prepared['toolchain_hash'])
    s.update(prepared_digest=app.dependency_digest(s), build_digest=app.dependency_digest(s))
    app.save(app.STORE/(s['id']+'.json'), s)
    if app.unit_path(s).exists():
        app.write_unit(s, app.unit_text(s, contract, app.node_identity()))


def start_converge(root, value, stage):
    """Start only missing owned group members; never stop healthy siblings."""
    if value['schema_version'] not in (3, 4, 8):
        return app.start(root, take_lock=False)
    import project_groups as groups
    with groups.scope(root, value) as resolved:
        parent = groups.reserve(root, value)
        _, rows = runtime_rows(root, value)
        app.need(not any(row['busy'] for row in rows.values()), 'busy')
        app.need(all(not row['active'] or row['ready'] for row in rows.values()), 'health')
        parent.update(phase='starting', health_ready=False, operation='start',
                      operation_id=uuid.uuid4().hex, operation_result='running', error=None)
        groups.save(parent)
        groups.network(parent, create=True)
        if 'db' in rows and not rows['db']['active']:
            import project_database as db
            owned = rows['db']['receipt']
            app.need(owned is not None and not owned['blocked'], 'database-recovery')
            stage('start', 'db'); db.acquire(); db.start(owned)
            app.need(db.ready(owned, value), 'database-health')
        for name, (path, contract) in resolved.items():
            if not rows[name]['active']:
                stage('start', name); app.start(path, no_route=True, take_lock=False)
        _, rows = runtime_rows(root, value)
        app.need(all(row['ready'] for row in rows.values()), 'health')
        parent.update(operation_result='passed')
        publication(parent, True, 'ready')
        app.ensure_ingress()


def reserve_journal(destination, journal):
    directory=app.safe(app.STORE/'control-journals')
    directory.mkdir(mode=0o700,parents=True,exist_ok=True)
    with app.locked('_control-journal-registry',project_guard=False):
        paths=list(directory.iterdir())
        app.need(len(paths)<=1000,'control-capacity')
        total=0;remaining=0
        for path in paths:
            app.need(re.fullmatch(r'[0-9a-f]{32}\.json',path.name),'control-recovery')
            value=app.read_json(path);info=path.lstat()
            app.need(stat.S_IMODE(info.st_mode)==0o600 and isinstance(value,dict)
                     and value.get('operation_id')==path.stem and value.get('schema_version')==SCHEMA,'control-recovery')
            stamp=value.get('updated_at')
            if (value.get('state') in {'succeeded','failed'} and type(stamp) in (int,float)
                    and 0<=stamp<time.time()-7*86400):
                marker=app.read_json(guard_path(value['project']))
                if not marker or marker.get('operation_id')!=path.stem:
                    path.unlink();continue
            remaining+=1;total+=info.st_size
        app.need(remaining<1000 and total<10*1024*1024-65536,'control-capacity')
        app.need(not destination.exists(),'conflict')
        app.save(destination,journal)


def execute(root, action, component=None, *, expected=None, operation_id=None, stage=None, admitted=False):
    """Execute under one durable identity-bound lock; callback persists stages."""
    app.need(action in ACTIONS and (component is None or component in COMPONENTS), 'invalid')
    root, value = app.target(root)
    project = value['project']['id']
    ident = operation_id or uuid.uuid4().hex
    app.need(isinstance(ident, str) and re.fullmatch(r'[0-9a-f]{32}', ident), 'invalid')
    notify = stage or (lambda *_: None)
    journal = {'schema_version': SCHEMA, 'operation_id': ident, 'project': project,
               'action': action, 'component': component, 'state': 'accepted',
               'started_at': time.time(), 'updated_at': time.time(), 'stages': [], 'reason': None, 'root':str(root)}
    journal_path = app.STORE/'control-journals'/(ident+'.json')
    def stage(phase, selected):
        journal['state'] = 'running'
        journal['updated_at'] = time.time()
        journal['stages'].append({'stage': phase, 'component': selected, 'at': journal['updated_at']})
        app.need(len(journal['stages']) <= 64, 'control-capacity')
        app.save(journal_path, journal)
        notify(phase, selected)
    with source_lock(root), project_lock(project):
        if admitted:
            marker = app.read_json(guard_path(project))
            app.need(marker is not None and marker.get('operation_id') == ident and marker.get('root') == str(root), 'control-recovery')
        root, value, parent, rows, generation = inspect(root)
        app.need(expected is None or generation == expected, 'control-changed')
        reason = eligibility(value, rows, action, component)
        app.need(reason is None, reason or 'invalid')
        path = guard_path(project)
        path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        journal.update(generation=generation, before={name: row['generation'] for name, row in rows.items()})
        reserve_journal(journal_path,journal)
        app.save(path, {'schema_version': SCHEMA, 'project': project, 'root': str(root), 'operation_id': ident})
        token = OWNER.set(ident)
        completed = False
        try:
            stage('validated', component)
            if value['schema_version'] in (6, 9):
                import metro_sessions as metro
                old = rows['metro']['receipt']
                app.need(old is not None, 'control-unsupported')
                # A restart cannot extend the approved lease. Start supports an
                # existing unexpired opted-in session only, never creates consent.
                starting = action == 'restart' or action == 'start' and not rows['metro']['active']
                if starting:
                    ttl = int(old['expires_at']-time.time())
                    app.need(ttl >= 60, 'control-expired')
                if action in {'stop', 'restart'}:
                    stage('stop', 'metro'); metro.stop(root)
                if starting:
                    stage('start', 'metro')
                    metro.start(root, ttl_seconds=ttl, transport='tailnet-http' if old['origin'].startswith('http://') else 'https', lease_expiry=old['expires_at'])
            elif component:
                restart_selected(root, value, parent, rows, component, stage)
            elif action in {'pause', 'resume'}:
                freeze(root, value, parent, rows, action, stage)
            elif action == 'rebuild':
                prepared = build_sources(root, value, rows, stage, ident)
                app.need(inspect(root)[4] == generation, 'control-changed')
                # All builds and input validation finish before any replacement.
                for name in ('api', 'web'):
                    if name in rows and rows[name]['active']:
                        restart_selected(root, value, parent, rows, name, stage, require_all=False, prepared=prepared[name])
                    elif name in rows:
                        import project_groups as groups
                        with (groups.scope(root, value) if value['schema_version'] in (3, 4, 8) else contextlib.nullcontext({name: (root, value)})) as resolved:
                            if value['schema_version'] in (3, 4, 8):
                                parent = groups.reserve(root, value)
                            child = app.reserve(resolved[name][0], resolved[name][1])
                            install_prepared(child, resolved[name][1], prepared[name], stage)
                            child.update(phase='stopped', health_ready=False)
                            app.save(app.STORE/(child['id']+'.json'), child)
            else:
                if action in {'stop', 'restart'}:
                    # systemd cannot gracefully stop a frozen process.
                    for name, row in rows.items():
                        if row['paused']:
                            stage('resume-for-stop', name)
                            app.command(['podman', 'unpause', row['receipt']['name']], timeout=30)
                    stage('stop', None); app.stop(root, take_lock=False)
                if action in {'start', 'restart'}:
                    stage('start', None); start_converge(root, value, stage)
            stage('observe', component)
            _, after = runtime_rows(root, value)
            if action in {'start', 'restart', 'resume'}:
                app.need(all(row['ready'] for row in after.values()), 'health')
            elif action == 'rebuild':
                app.need(all(after[name]['ready'] for name in rows if rows[name]['active']), 'health')
            elif action == 'stop':
                app.need(not any(row['active'] for row in after.values()), 'health')
            elif action == 'pause':
                app.need(all(row['paused'] for row in after.values()), 'control-state')
            journal.update(state='succeeded', updated_at=time.time(), after={name: row['generation'] for name, row in after.items()})
            app.save(journal_path, journal)
            completed = True
            return {'schema_version': SCHEMA, 'operation_id': ident, 'project': project,
                    'action': action, 'component': component, 'state': 'succeeded', 'observed_at': time.time()}
        except BaseException as error:
            journal.update(state='unknown', updated_at=time.time(),
                           reason=error.code if isinstance(error, app.AppError) else 'internal')
            app.save(journal_path, journal)
            raise
        finally:
            # Failed/uncertain effects deliberately retain a guard for explicit
            # reconciliation. Never turn worker exit into permission to retry.
            if completed:
                path.unlink()
            OWNER.reset(token)


def reconcile(root, operation_id, confirm, *, allow_absent=False):
    """Explicitly acknowledge observed partial effects, without repeating an action.

    The outer lock proves no live provider worker owns this project. Owned native
    jobs and inconsistent native state still block recovery. A new action requires
    a fresh capability/intent after this inspection.
    """
    root, value = app.target(root)
    project = value['project']['id']
    app.need(confirm == project and isinstance(operation_id, str) and re.fullmatch(r'[0-9a-f]{32}', operation_id), 'control-changed')
    marker = app.read_json(guard_path(project))
    if marker is None and not allow_absent:
        journal=app.read_json(app.STORE/'control-journals'/(operation_id+'.json'))
        app.need(journal is not None and journal.get('root')==str(root) and journal.get('project')==project
                 and journal.get('operation_id')==operation_id and journal.get('state') in {'accepted','running','unknown'},'control-recovery')
        allow_absent=True
    app.need((marker is None and allow_absent) or marker is not None and marker.get('operation_id') == operation_id and marker.get('root') == str(root), 'control-recovery')
    token = OWNER.set(operation_id)
    recovery = RECONCILING.set(True)
    try:
        with project_lock(project):
            root, value, parent, rows, generation = inspect(root)
            app.need(not any(row['busy'] for row in rows.values()), 'busy')
            for name in rows:
                app.need(not app.object_owned('container', 'gptclaw-build-'+operation_id+'-'+name+'-job', operation_id), 'busy')
            for name, row in rows.items():
                s = row['receipt']
                if not s or name in {'db', 'metro'}:
                    continue
                s.update(phase='paused' if row['paused'] else 'ready' if row['ready'] else 'failed' if row['active'] else 'stopped',
                         health_ready=row['ready'], operation_result='failed')
                save_parent(s)
            all_ready = all(row['ready'] for row in rows.values())
            if parent:
                parent.update(operation_result='failed', error=None)
                publication(parent, all_ready, 'ready' if all_ready else 'paused' if all(row['paused'] for row in rows.values()) else 'failed')
            path = app.STORE/'control-journals'/(operation_id+'.json')
            journal = app.read_json(path)
            if journal is None:
                journal = {'schema_version': SCHEMA, 'operation_id': operation_id, 'project': project, 'stages': []}
                path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            app.need(journal.get('operation_id') == operation_id and journal.get('project') == project, 'control-recovery')
            journal.update(state='failed', updated_at=time.time(), reason='control-recovery', reconciled_at=time.time())
            app.save(path, journal)
            guard_path(project).unlink(missing_ok=allow_absent)
            return {'schema_version': SCHEMA, 'project': project, 'operation_id': operation_id,
                    'state': 'reconciled', 'observed_at': time.time(),
                    'components': {name: {k: row[k] for k in ('active', 'ready', 'paused')} for name, row in rows.items()}}
    finally:
        RECONCILING.reset(recovery)
        OWNER.reset(token)
