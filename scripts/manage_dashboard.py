"""Own only the private dashboard release, units and socket; never manage project data."""
import argparse
import contextlib
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import sys
import uuid

import private_apps as app

PLATFORM = Path('/srv/forge/platform')
USER_UNITS = Path('/home/forge/.config/systemd/user')
QUADLETS = Path('/home/forge/.config/containers/systemd')
PORT = 18200
COLLECTOR_UNIT = 'gptclaw-dashboard-collector.service'
FRONTEND_UNIT = 'gptclaw-dashboard.service'
CONTROL_UNIT = 'gptclaw-dashboard-control.service'
IMAGE = 'localhost/gptclaw-node:24.21.0-pnpm12.10.1'


class OperatorDirectoryRequired(Exception):
    pass


def owned_directory(path):
    path = app.safe(path)
    if not path.exists():
        if path == PLATFORM and not os.access(path.parent, os.W_OK):
            raise OperatorDirectoryRequired()
        path.mkdir(mode=0o700)
    info = path.lstat()
    app.need(stat.S_ISDIR(info.st_mode) and info.st_uid == os.getuid()
             and stat.S_IMODE(info.st_mode) == 0o700, 'path')
    return path


@contextlib.contextmanager
def operation_lock():
    owned_directory(PLATFORM)
    path = app.safe(PLATFORM/'operation.lock')
    fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        info = os.fstat(fd)
        app.need(stat.S_ISREG(info.st_mode) and info.st_uid == os.getuid()
                 and info.st_nlink == 1 and stat.S_IMODE(info.st_mode) == 0o600, 'path')
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise app.AppError('busy') from None
        yield
    finally:
        os.close(fd)


def read_owned(path):
    # Compiled-file checksum records exceed the app receipt's 64 KiB limit.
    # Keep a separate finite bound without widening any runtime/secret reader.
    path=app.safe(path)
    info = path.lstat()
    app.need(stat.S_ISREG(info.st_mode) and info.st_uid == os.getuid()
             and info.st_nlink == 1 and not info.st_mode & 0o022 and info.st_size<=1048576, 'conflict')
    fd=os.open(path,os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd,'rb') as source:
        opened=os.fstat(source.fileno())
        app.need((opened.st_dev,opened.st_ino)==(info.st_dev,info.st_ino)
                 and stat.S_ISREG(opened.st_mode) and opened.st_uid==os.getuid()
                 and opened.st_nlink==1 and not opened.st_mode & 0o022, 'conflict')
        data=source.read(1048577)
    app.need(len(data)<=1048576,'conflict')
    def unique(pairs):
        value={}
        for key,item in pairs:
            app.need(key not in value,'conflict');value[key]=item
        return value
    return json.loads(data,object_pairs_hook=unique)


def origin():
    return 'https://' + app.node_identity()


def unit_text(release, provider, interpreter, image, public_origin, with_status=False, with_links=False, with_controls=False):
    app.need(re.fullmatch(r'https://[a-z0-9.-]+\.ts\.net', public_origin), 'setup')
    collector = f'''[Unit]
Description=GptClaw private read-only dashboard collector

[Service]
ExecStart={interpreter} -B {provider}/scripts/dashboard_collector.py --projects-root {app.PROJECTS} --socket {PLATFORM}/run/collector.sock --registry {PLATFORM}/metadata.json{' --status' if with_status or with_links or with_controls else ''}{' --links' if with_links else ''}{' --controls' if with_controls else ''}
Restart=on-failure
RestartSec=2
TimeoutStopSec=5
MemoryMax=512M
CPUQuota=200%
TasksMax=256
NoNewPrivileges=true

[Install]
WantedBy=default.target
'''
    frontend = f'''[Unit]
Description=GptClaw private projects dashboard
After={COLLECTOR_UNIT}
Wants={COLLECTOR_UNIT}

[Container]
Image={image}
ContainerName=gptclaw-dashboard
UserNS=keep-id
User={os.getuid()}:{os.getgid()}
Label=com.gptclaw.dashboard=private-platform-v1
PublishPort=127.0.0.1:{PORT}:3000
Volume={release}/web:/app:ro
Volume={PLATFORM}/run:/run/gptclaw:ro
WorkingDir=/app
Environment=HOSTNAME=0.0.0.0
Environment=PORT=3000
Environment=DASHBOARD_ORIGIN={public_origin}
Environment=DASHBOARD_SOCKET=/run/gptclaw/collector.sock
Environment=DASHBOARD_CONTROL_SOCKET=/run/gptclaw/control.sock
Environment=DASHBOARD_CONTROLS={'1' if with_controls else '0'}
Environment=NEXT_TELEMETRY_DISABLED=1
Exec=node server.js
Pull=never
NoNewPrivileges=true
DropCapability=all
PidsLimit=128
PodmanArgs=--memory=768m --cpus=1

[Service]
Restart=on-failure
RestartSec=2
TimeoutStartSec=60
TimeoutStopSec=20

[Install]
WantedBy=default.target
'''
    units = {str(USER_UNITS/COLLECTOR_UNIT): collector,
             str(QUADLETS/'gptclaw-dashboard.container'): frontend}
    if with_controls:
        units[str(USER_UNITS/CONTROL_UNIT)] = f'''[Unit]
Description=GptClaw typed private dashboard controller

[Service]
ExecStart={interpreter} -B {provider}/scripts/dashboard_controls.py serve --projects-root {app.PROJECTS} --socket {PLATFORM}/run/control.sock --state {PLATFORM}/controls/v1 --origin {public_origin} --registry {PLATFORM}/metadata.json --enabled
Restart=on-failure
RestartSec=2
KillMode=control-group
TimeoutStopSec=10
MemoryMax=768M
CPUQuota=200%
TasksMax=256
NoNewPrivileges=true

[Install]
WantedBy=default.target
'''
    return units


def tree_digest(root):
    values = {}
    for path in sorted(root.rglob('*')):
        relative = str(path.relative_to(root))
        if path.is_symlink():
            app.need(path.resolve().is_relative_to(root.resolve()), 'path')
            values[relative] = 'link:' + str(path.readlink())
        elif path.is_file():
            app.need(path.stat().st_uid == os.getuid(), 'path')
            app.need(path.name not in {'.env', '.env.local', 'auth.json'}, 'path')
            values[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    app.need('server.js' in values, 'setup')
    return values


def prepare(with_status=False, with_links=False, with_controls=False):
    source = app.REPO/'platform/dashboard/.next/standalone'
    static = app.REPO/'platform/dashboard/.next/static'
    app.need(source.is_dir() and static.is_dir(), 'setup')
    source_values = tree_digest(source)
    static_values = {str(p.relative_to(static)): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in sorted(static.rglob('*')) if p.is_file()}
    provider = app.provider_bundle()
    image = app.command(['podman','image','inspect',IMAGE,'--format','{{.Id}}']).stdout.strip()
    image = image if image.startswith('sha256:') else 'sha256:' + image
    app.need(re.fullmatch(r'sha256:[0-9a-f]{64}', image), 'setup')
    selected_origin = origin()
    descriptor = {'schema_version': 1, 'source': source_values, 'static': static_values,
                  'provider': str(provider), 'interpreter': sys.executable, 'image': image,
                  'origin': selected_origin, 'port': PORT, 'status_enabled':with_status or with_links or with_controls, 'links_enabled':with_links, 'controls_enabled':with_controls, 'control_schema':1}
    digest = hashlib.sha256(json.dumps(descriptor, sort_keys=True).encode()).hexdigest()
    owned_directory(PLATFORM)
    releases = owned_directory(PLATFORM/'releases')
    owned_directory(PLATFORM/'run')
    destination = releases/digest
    if destination.exists():
        app.need(read_owned(destination/'release.json') == descriptor, 'conflict')
        expected = read_owned(destination/'web-files.json')
        app.need(tree_digest(destination/'web') == expected, 'conflict')
        return digest
    stage = releases/('.'+digest+'.'+uuid.uuid4().hex+'.tmp')
    stage.mkdir(mode=0o700)
    try:
        shutil.copytree(source, stage/'web', symlinks=True)
        out = stage/'web/.next/static'
        if out.exists():
            app.need(out.is_dir() and not any(out.iterdir()), 'conflict')
            out.rmdir()
        shutil.copytree(static, out)
        app.save(stage/'release.json', descriptor)
        app.save(stage/'web-files.json', tree_digest(stage/'web'))
        os.rename(stage, destination)
    except BaseException:
        # Preserve a failed owned stage for inspection; never delete unknown content.
        raise
    return digest


def owner():
    path = PLATFORM/'owner.json'
    if not path.exists():
        return None
    value = read_owned(path)
    app.need(isinstance(value, dict) and value.get('schema_version') == 1
             and re.fullmatch(r'[0-9a-f]{64}', value.get('release',''))
             and isinstance(value.get('units'), dict), 'conflict')
    return value


def verify_units(receipt):
    expected_paths = {str(USER_UNITS/COLLECTOR_UNIT), str(QUADLETS/'gptclaw-dashboard.container')}
    if receipt.get('controls_enabled'):
        expected_paths.add(str(USER_UNITS/CONTROL_UNIT))
    app.need(set(receipt['units']) == expected_paths, 'conflict')
    for filename, digest in receipt['units'].items():
        path = app.safe(filename)
        info = path.stat()
        app.need(info.st_uid == os.getuid() and info.st_nlink == 1 and path.is_file()
                 and hashlib.sha256(path.read_bytes()).hexdigest() == digest, 'conflict')
    for name in (COLLECTOR_UNIT, FRONTEND_UNIT, *([CONTROL_UNIT] if receipt.get('controls_enabled') else [])):
        result = app.command(['systemctl','--user','show',name,'-p','DropInPaths']).stdout.strip()
        app.need(result == 'DropInPaths=', 'conflict')


def activate(release_id):
    app.need(re.fullmatch(r'[0-9a-f]{64}', release_id), 'invalid')
    release = app.safe(PLATFORM/'releases'/release_id)
    descriptor = read_owned(release/'release.json')
    app.need(hashlib.sha256(json.dumps(descriptor, sort_keys=True).encode()).hexdigest() == release_id, 'conflict')
    app.need(type(descriptor.get('controls_enabled',False)) is bool,'conflict')
    if descriptor.get('controls_enabled'):
        app.need(type(descriptor.get('control_schema')) is int and descriptor['control_schema']==1,'control-unsupported')
    provider = Path(descriptor.get('provider', ''))
    app.need(provider.parent == app.STORE/'providers' and re.fullmatch(r'[0-9a-f]{64}', provider.name), 'conflict')
    if descriptor.get('controls_enabled'):
        # The stable CLI must share this provider's durable guard semantics.
        # A new controller alongside the older launcher cannot serialize later
        # CLI mutations after an interrupted worker releases its native lock.
        launcher=app.safe(app.STORE)/'gptclawctl'
        ingress=app.read_json(app.STORE/'ingress-owner.json')
        app.need(launcher.is_symlink() and launcher.readlink()==provider/'scripts/gptclawctl'
                 and ingress is not None and ingress.get('launcher')==str(provider/'scripts/gptclawctl'),'control-unsupported')
    app.need(descriptor.get('interpreter') == sys.executable and descriptor.get('port') == PORT
             and re.fullmatch(r'sha256:[0-9a-f]{64}', descriptor.get('image', '')), 'conflict')
    app.need(tree_digest(release/'web') == read_owned(release/'web-files.json'), 'conflict')
    previous = owner()
    if previous:
        verify_units(previous)
        require_idle_controls()
    texts = unit_text(release, descriptor['provider'], descriptor['interpreter'], descriptor['image'], descriptor['origin'], descriptor.get('status_enabled',False), descriptor.get('links_enabled',False), descriptor.get('controls_enabled',False))
    for filename in texts:
        path = app.safe(filename)
        app.need(path.parent.is_dir() and path.parent.stat().st_uid == os.getuid(), 'path')
        if path.exists():
            app.need(previous and filename in previous['units'], 'conflict')
    if not previous:
        app.need(app.available(PORT), 'conflict')
        app.need(app.command(['podman','container','exists','gptclaw-dashboard'],optional=True).returncode == 1, 'conflict')
    receipt = {'schema_version':1,'release':release_id,'previous':previous['release'] if previous else None,
               'controls_enabled':descriptor.get('controls_enabled',False),
               'units':{p:hashlib.sha256(text.encode()).hexdigest() for p,text in texts.items()}}
    if previous and previous.get('controls_enabled') and not descriptor.get('controls_enabled'):
        app.command(['systemctl','--user','stop',CONTROL_UNIT])
        app.command(['systemctl','--user','disable',CONTROL_UNIT])
        app.safe(USER_UNITS/CONTROL_UNIT).unlink()
    if descriptor.get('controls_enabled'):
        owned_directory(PLATFORM/'controls'); owned_directory(PLATFORM/'controls/v1')
        marker=PLATFORM/'controls/v1/disabled'
        if marker.exists():
            app.need(marker.is_file() and not marker.is_symlink() and marker.stat().st_uid==os.getuid(),'path')
            marker.unlink()
    for filename, text in texts.items():
        app.save_text(Path(filename), text)
    app.save(PLATFORM/'owner.json', receipt)
    app.command(['systemctl','--user','daemon-reload'])
    app.command(['systemctl','--user','enable',COLLECTOR_UNIT])
    app.command(['systemctl','--user','restart',COLLECTOR_UNIT])
    if descriptor.get('controls_enabled'):
        app.command(['systemctl','--user','enable',CONTROL_UNIT])
        app.command(['systemctl','--user','restart',CONTROL_UNIT])
    app.command(['systemctl','--user','restart',FRONTEND_UNIT])
    return {'state':'started','release':release_id,'private_origin':descriptor['origin'],
            'loopback_port':PORT,'serve_path':'/dashboard/','operator_route_pending':True}


def require_idle_controls():
    directory=PLATFORM/'controls/v1'
    if not directory.exists(): return
    import dashboard_controls as controls
    owned_directory(directory)
    paths=list(directory.glob('*.json'))
    app.need(len(paths)<=controls.MAX_RECORDS,'control-capacity')
    for path in paths:
        try:record=controls.read_record(path)
        except controls.Refusal:raise app.AppError('control-recovery') from None
        app.need(record['state'] not in controls.ACTIVE,'control-recovery')
    # A paused runtime cannot be safely handed to an older provider that does
    # not understand pause receipts, even after the action itself completed.
    for state in app.states():
        app.need(state['phase'] not in {'paused','pausing','resuming'},'control-paused')


def disable_controls():
    receipt=owner();app.need(receipt is not None and receipt.get('controls_enabled'),'control-unsupported')
    verify_units(receipt)
    directory=owned_directory(PLATFORM/'controls');directory=owned_directory(directory/'v1')
    path=app.safe(directory/'disabled')
    if path.exists():app.need(path.is_file() and path.stat().st_uid==os.getuid(),'path')
    else:app.save_text(path,'Submissions disabled; retained operations and managed recovery remain available.\n');path.chmod(0o600)
    return {'state':'controls-disabled','release':receipt['release'],'project_data_retained':True}


def stop():
    receipt = owner()
    app.need(receipt is not None, 'conflict')
    verify_units(receipt)
    require_idle_controls()
    for name in (FRONTEND_UNIT, *([CONTROL_UNIT] if receipt.get('controls_enabled') else []), COLLECTOR_UNIT):
        app.command(['systemctl','--user','stop',name])
    return {'state':'stopped','release':receipt['release'],'project_data_retained':True}


def status():
    receipt = owner()
    if receipt is None:
        return {'state':'not-installed'}
    verify_units(receipt)
    return {'release':receipt['release'],'services':{name:app.command(['systemctl','--user','is-active',name],optional=True).stdout.strip()
            for name in (COLLECTOR_UNIT, FRONTEND_UNIT, *([CONTROL_UNIT] if receipt.get('controls_enabled') else []))},'loopback_port':PORT}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['prepare','start','stop','status','rollback','disable-controls'])
    parser.add_argument('--release')
    parser.add_argument('--with-status',action='store_true')
    parser.add_argument('--with-links',action='store_true')
    parser.add_argument('--with-controls',action='store_true')
    args=parser.parse_args()
    try:
        app.need(os.getuid() == 1002 and os.geteuid() != 0, 'setup')
        if args.action == 'status':
            result=status()
        else:
            with operation_lock():
                if args.action == 'prepare': result={'state':'prepared','release':prepare(args.with_status,args.with_links,args.with_controls)}
                elif args.action == 'start': result=activate(args.release or prepare(args.with_status,args.with_links,args.with_controls))
                elif args.action == 'stop': result=stop()
                elif args.action == 'disable-controls': result=disable_controls()
                else:
                    receipt=owner();app.need(receipt and receipt.get('previous'), 'conflict')
                    result=activate(receipt['previous'])
        print(json.dumps(result, sort_keys=True))
    except OperatorDirectoryRequired:
        print(json.dumps({'state':'operator-required','reason':'platform-directory','path':str(PLATFORM)}))
        return 2
    except (app.AppError, OSError, ValueError):
        print(json.dumps({'state':'unavailable','error':'dashboard-operation-refused'}))
        return 1
    return 0


if __name__ == '__main__':
    sys.dont_write_bytecode=True
    raise SystemExit(main())
