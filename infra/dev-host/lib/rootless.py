#!/usr/bin/env python3
"""SYS-001 bootstrap-only identity/configuration and unprivileged capability checks."""
import argparse
import datetime as dt
import grp
import hashlib
import json
import os
from pathlib import Path
import pwd
import re
import subprocess
import tempfile

UID = GID = 1002
START, COUNT = 231072, 65536
HOME = Path('/home/forge')
GRAPH = HOME / '.local/share/containers/storage'
RUNROOT = Path('/run/user/1002/containers')
STATE = Path('/var/lib/gptclaw')
GENERATOR = '/usr/lib/systemd/user-generators/podman-user-generator'
SYSTEM_UNITS = ('podman.socket', 'podman.service', 'podman-auto-update.service',
                'podman-auto-update.timer', 'podman-restart.service', 'podman-clean-transient.service')
CONFIG = {
    'storage.conf': f'''[storage]
driver = "overlay"
runroot = "{RUNROOT}"
graphroot = "{GRAPH}"
[storage.options.overlay]
mount_program = "/usr/bin/fuse-overlayfs"
''',
    'containers.conf': '''[engine]
cgroup_manager = "systemd"
runtime = "crun"
[network]
network_backend = "netavark"
default_rootless_network_cmd = "slirp4netns"
''',
}
POLICY = {'schema_version': 1, 'uid': UID, 'gid': GID, 'subid_start': START,
          'subid_count': COUNT, 'graphroot': str(GRAPH), 'runroot': str(RUNROOT),
          'configuration_sha256': hashlib.sha256(json.dumps(CONFIG, sort_keys=True).encode()).hexdigest()}


class RootlessError(ValueError):
    pass


def require(ok, message):
    if not ok:
        raise RootlessError(message)


def command(args, *, user=False):
    if user:
        args = ['sudo', '-u', 'forge', '-H', 'env', '-i', 'HOME=/home/forge',
                'USER=forge', 'LOGNAME=forge', 'PATH=/usr/local/bin:/usr/bin:/bin',
                'XDG_RUNTIME_DIR=/run/user/1002',
                'DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1002/bus', *args]
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=90, check=False)
    except (OSError, subprocess.TimeoutExpired):
        raise RootlessError('capability command unavailable or timed out') from None
    require(result.returncode == 0, 'capability command failed; inspect the named bootstrap phase')
    require(len(result.stdout) < 131072, 'capability output exceeds bound')
    return result.stdout.strip()


def safe_path(path):
    for part in [path, *path.parents]:
        require(not part.is_symlink(), 'symlink at managed path')


def write(path, content, owner=None):
    safe_path(path)
    fd, temporary = tempfile.mkstemp(prefix='.sys001-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
            os.fchmod(stream.fileno(), 0o644)
            if owner:
                os.fchown(stream.fileno(), *owner)
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def mappings(content, accounts):
    """Plan one additive mapping; refuse conflicts before either file is changed."""
    own = []
    for line in content.splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        fields = line.split(':')
        require(len(fields) == 3 and fields[1].isdigit() and fields[2].isdigit(), 'malformed subordinate mapping')
        name, start, count = fields[0], int(fields[1]), int(fields[2])
        require(count > 0, 'invalid subordinate range')
        if name == 'forge':
            own.append((start, count))
        else:
            require(start + count <= START or start >= START + COUNT, 'subordinate ID collision')
    require(not own or own == [(START, COUNT)], 'existing forge mappings differ; migration required')
    require(not any(START <= ident < START + COUNT for ident in accounts), 'subordinate range overlaps real identity')
    return content if own else content + ('' if not content or content.endswith('\n') else '\n') + f'forge:{START}:{COUNT}\n'


def identity(root=Path('/'), runner=command, users=None, groups=None):
    users = pwd.getpwall() if users is None else users
    groups = grp.getgrall() if groups is None else groups
    forge = [u for u in users if u.pw_name == 'forge']
    group = [g for g in groups if g.gr_name == 'forge']
    require(not any(u.pw_uid == UID and u.pw_name != 'forge' for u in users), 'forge UID already assigned')
    require(not any(g.gr_gid == GID and g.gr_name != 'forge' for g in groups), 'forge GID already assigned')
    require(not forge or (len(forge) == 1 and forge[0].pw_uid == UID and forge[0].pw_gid == GID and
                          forge[0].pw_dir == str(HOME)), 'forge identity differs; migration required')
    require(not group or (len(group) == 1 and group[0].gr_gid == GID), 'forge group differs')
    require(not any(g.gr_name in ('sudo', 'docker', 'lxd', 'incus-admin') and 'forge' in g.gr_mem for g in groups),
            'forge has a privileged group; operator review required')
    plans = []
    for name, ids in [('subuid', [u.pw_uid for u in users]), ('subgid', [g.gr_gid for g in groups])]:
        path = root / 'etc' / name
        safe_path(path)
        content = path.read_text() if path.exists() else ''
        plans.append((path, content, mappings(content, ids)))
    # All conflicts checked before creating identity or modifying either mapping.
    if not forge:
        require(not (root / HOME.relative_to('/')).exists(), 'unowned pre-existing forge home; migration required')
    if not group:
        runner(['groupadd', '--gid', str(GID), 'forge'])
    if not forge:
        runner(['useradd', '--uid', str(UID), '--gid', str(GID), '--no-user-group',
                '--create-home', '--shell', '/bin/bash', '-K', 'SUB_UID_COUNT=0',
                '-K', 'SUB_GID_COUNT=0', 'forge'])
    for path, old, new in plans:
        if old != new:
            write(path, new)


def preflight(home=HOME, state=STATE):
    config = home / '.config/containers'
    graph = home / '.local/share/containers'
    safe_path(config)
    safe_path(graph)
    require(home.is_dir() and home.stat().st_uid == UID and home.stat().st_gid == GID,
            'forge home ownership differs')
    for name, content in CONFIG.items():
        path = config / name
        safe_path(path)
        require(not path.exists() or (path.is_file() and path.read_text() == content and
                                     path.stat().st_uid == UID), 'unknown or changed container configuration')
    # Extra config files can override the reviewed policy. Do not remove/adopt them.
    for path in (config / 'containers.conf.d', config / 'containers.conf.modules'):
        safe_path(path)
        require(not path.exists() or (path.is_dir() and not any(path.iterdir())), 'unknown container overrides')
    marker = state / 'rootless-policy.json'
    safe_path(marker)
    if marker.exists():
        require(json.loads(marker.read_text()) == POLICY, 'rootless policy changed; migration required')
    elif graph.exists():
        require(graph.is_dir() and not any(graph.iterdir()), 'existing container storage; migration required')
    return config


def prepare(root=Path('/'), runner=command):
    """Mask package-owned rootful activation before apt can start it."""
    state = root / 'var/lib/gptclaw'
    marker = state / 'rootless-system-policy.json'
    units = root / 'etc/systemd/system'
    policy = {'masked_system_units': list(SYSTEM_UNITS)}
    safe_path(marker)
    safe_path(units)
    if marker.exists():
        require(json.loads(marker.read_text()) == policy, 'system Podman policy changed')
    else:
        require(not (root / 'usr/bin/podman').exists(), 'existing Podman requires operator migration')
        store = root / 'var/lib/containers'
        safe_path(store)
        require(not store.exists() or (store.is_dir() and not any(store.iterdir())),
                'existing rootful storage requires operator migration')
    for name in SYSTEM_UNITS:
        path = units / name
        require(not path.exists() and not path.is_symlink() or
                (path.is_symlink() and os.readlink(path) == '/dev/null'), 'unknown system Podman unit override')
    for name in SYSTEM_UNITS:
        path = units / name
        if not path.is_symlink():
            path.symlink_to('/dev/null')
    write(marker, json.dumps(policy, sort_keys=True) + '\n')
    runner(['systemctl', 'daemon-reload'])


def check_system_units(runner=command):
    for name in SYSTEM_UNITS:
        require(runner(['systemctl', 'show', name, '-p', 'LoadState', '--value']) == 'masked',
                'system Podman activation is not masked')
        require(runner(['systemctl', 'show', name, '-p', 'ActiveState', '--value']) == 'inactive',
                'unexpected active system Podman unit')


def configure(runner=command):
    identity(runner=runner)
    check_system_units(runner)
    config = preflight()
    require(Path('/sys/fs/cgroup/cgroup.controllers').exists(), 'cgroup v2 required')
    require(runner(['findmnt', '-T', str(HOME), '-no', 'TARGET']).strip() == '/', 'container storage must use root filesystem')
    require(runner(['findmnt', '-T', '/srv/forge/projects', '-no', 'TARGET']).strip() == '/srv/forge',
            'protected project volume not mounted')
    for binary in ('/usr/bin/podman', '/usr/bin/newuidmap', '/usr/bin/newgidmap',
                   '/usr/bin/slirp4netns', '/usr/bin/fuse-overlayfs', '/usr/bin/crun', GENERATOR):
        require(os.access(binary, os.X_OK), 'required rootless helper or generator absent')
    # Create only missing directories and files; never recursively chown a user tree.
    for path in (HOME / '.config', config):
        safe_path(path)
        if not path.exists():
            path.mkdir(mode=0o700)
            os.chown(path, UID, GID)
        require(path.is_dir() and path.stat().st_uid == UID, 'configuration directory ownership differs')
    for name, content in CONFIG.items():
        path = config / name
        if not path.exists():
            write(path, content, (UID, GID))
    # Intent marker precedes first engine initialization so an interrupted probe can retry.
    write(STATE / 'rootless-policy.json', json.dumps(POLICY, sort_keys=True) + '\n')
    runner(['loginctl', 'enable-linger', 'forge'])
    runner(['systemctl', 'start', f'user@{UID}.service'])
    require(runner(['loginctl', 'show-user', 'forge', '-p', 'Linger', '--value']) == 'yes', 'linger unavailable')
    runner(['systemctl', '--user', 'daemon-reload'], user=True)
    verify(runner=runner)


def check_info(info):
    host, store = info.get('host', {}), info.get('store', {})
    require(host.get('security', {}).get('rootless') is True, 'Podman is not rootless')
    require(host.get('cgroupVersion') == 'v2' and host.get('cgroupManager') == 'systemd', 'unsupported cgroup setup')
    require(host.get('networkBackend') == 'netavark', 'unexpected network backend')
    require(host.get('slirp4netns', {}).get('executable') in ('/usr/bin/slirp4netns', '/bin/slirp4netns'),
            'rootless networking helper unavailable')
    require(host.get('ociRuntime', {}).get('name') == 'crun', 'unexpected OCI runtime')
    require(store.get('graphDriverName') == 'overlay' and store.get('graphRoot') == str(GRAPH) and
            store.get('runRoot') == str(RUNROOT), 'storage driver or path differs')
    version = info.get('version', {}).get('Version', '')
    require(re.fullmatch(r'4\.9\.[0-9]+', version), 'Podman outside reviewed 4.9 baseline')
    return {'podman': version, 'rootless': True, 'cgroup': 'v2/systemd', 'network': 'netavark',
            'rootless_network': 'slirp4netns', 'runtime': 'crun', 'driver': 'overlay',
            'graphroot': str(GRAPH), 'runroot': str(RUNROOT)}


def verify(runner=command):
    # No image pull and no long-running service: only namespace and generator probes.
    result = check_info(json.loads(runner(['podman', 'info', '--format=json'], user=True)))
    for kind in ('uid', 'gid'):
        rows = [tuple(map(int, line.split())) for line in
                runner(['podman', 'unshare', 'cat', f'/proc/self/{kind}_map'], user=True).splitlines()]
        require(rows == [(0, UID if kind == 'uid' else GID, 1), (1, START, COUNT)], 'unexpected rootless ID map')
    with tempfile.TemporaryDirectory(prefix='gptclaw-quadlet-') as tmp:
        os.chmod(tmp, 0o755)
        unit = Path(tmp) / 'gptclaw-generator-probe.container'
        unit.write_text('[Container]\nImage=localhost/gptclaw-generator-probe:inert\n[Install]\nWantedBy=default.target\n')
        unit.chmod(0o644)
        output = runner(['env', f'QUADLET_UNIT_DIRS={tmp}', GENERATOR, '--user', '--dryrun'], user=True)
        require('gptclaw-generator-probe.service' in output and 'ExecStart=' in output, 'Quadlet generation failed')
    result.update(POLICY)
    result.update(status='passed', observed_at=dt.datetime.now(dt.timezone.utc).isoformat())
    write(STATE / 'rootless-toolchain.json', json.dumps(result, sort_keys=True, indent=2) + '\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', 'identity', 'configure', 'verify'))
    args = parser.parse_args()
    try:
        require(os.geteuid() == 0 and Path(__file__).resolve() == Path('/usr/local/libexec/gptclaw-rootless'),
                'provisioning restricted to installed bootstrap helper')
        (STATE / 'rootless-toolchain.json').unlink(missing_ok=True)
        if args.action == 'prepare':
            prepare()
        elif args.action == 'identity':
            identity()
        elif args.action == 'configure':
            configure()
        else:
            verify()
        print('rootless action=' + args.action + ' status=succeeded')
        return 0
    except (RootlessError, OSError, ValueError, KeyError) as exc:
        reason = str(exc) if isinstance(exc, RootlessError) else 'invalid metadata or filesystem failure'
        print('rootless status=failed reason=' + reason)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
