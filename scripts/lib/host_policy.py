#!/usr/bin/env python3
"""Manage a reviewed host policy without reading other Codex configuration."""
import argparse
import datetime
import fcntl
import hashlib
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time

SOURCE = 'config/codex/AGENTS.md'
POLICY = 'AGENTS.md'
META = 'gptclaw-host-policy.meta'
PREVIOUS = 'gptclaw-host-policy.previous'
LOCK = 'gptclaw-host-policy.lock'
STAGING = '.gptclaw-host-policy.'
SECTIONS = ('Identity and scope', 'Start and deliver work', 'Infrastructure and access',
            'Secrets and data', 'Tools and exposure', 'Verification and handover',
            'Policy maintenance')
REPO = Path(__file__).resolve().parents[2]


class Failure(Exception):
    def __init__(self, label, message, code=1):
        self.code = code
        super().__init__(f'{label}: {message}')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def validate_policy(data):
    try:
        text = data.decode('utf-8')
    except UnicodeDecodeError:
        raise Failure('invalid-source', 'policy must be UTF-8', 2)
    if not 0 < len(data) <= 8192 or '\x00' in text:
        raise Failure('invalid-source', 'policy must contain 1..8192 bytes without NUL', 2)
    if not text.startswith('# GptClaw host policy\n'):
        raise Failure('invalid-source', 'missing policy identifier', 2)
    versions = re.findall(r'^Policy-Version: ([0-9]+\.[0-9]+\.[0-9]+)$', text, re.M)
    if len(versions) != 1 or any(text.count('## ' + s + '\n') != 1 for s in SECTIONS):
        raise Failure('invalid-source', 'one version and all seven sections required', 2)
    return versions[0]


def git(*args):
    try:
        return subprocess.run(['git', '-C', str(REPO), *args], check=True,
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise Failure('prerequisite', 'requested source commit/blob is unavailable locally', 2)


def source(revision):
    if not re.fullmatch(r'[0-9a-f]{40}', revision or ''):
        raise Failure('invocation', 'revision must be a full 40-character commit SHA', 2)
    if git('cat-file', '-t', revision).strip() != b'commit':
        raise Failure('invalid-source', 'revision must identify a commit', 2)
    entry = git('ls-tree', revision, '--', SOURCE).split()
    if len(entry) != 4 or entry[0] != b'100644' or entry[1] != b'blob':
        raise Failure('invalid-source', 'policy must be a regular non-executable Git blob', 2)
    data = git('show', f'{revision}:{SOURCE}')
    version = validate_policy(data)
    return data, metadata(data, version, revision)


def metadata(data, version, revision):
    values = dict(format='1', policy_version=version, commit=revision,
                  source=SOURCE, sha256=digest(data),
                  installed_utc=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'))
    return ''.join(f'{key}={value}\n' for key, value in values.items()).encode()


def exists(path):
    return os.path.lexists(path)


def inspect(path, directory=False):
    """Reject links, special files, hardlinks, foreign owners and loose modes."""
    info = path.lstat()
    valid_type = stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode)
    if not valid_type or (not directory and info.st_nlink != 1):
        raise Failure('unsafe-path', f'{path}: requires a plain {"directory" if directory else "file"}')
    if info.st_uid != os.getuid():
        raise Failure('unsafe-owner', f'{path}: must belong to the executing user')
    mode = 0o700 if directory else 0o600
    if stat.S_IMODE(info.st_mode) != mode:
        raise Failure('unsafe-mode', f'{path}: requires {mode:04o}; remediate explicitly, not recursively')


def read_private(path):
    inspect(path)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o600:
            raise Failure('unsafe-path', f'{path}: changed during inspection')
        return stream.read(16385)


def pair(directory):
    data = read_private(directory / POLICY)
    raw = read_private(directory / META)
    try:
        lines = raw.decode('ascii').splitlines()
        values = dict(line.split('=', 1) for line in lines)
        fields = {'format', 'policy_version', 'commit', 'source', 'sha256', 'installed_utc'}
        if len(lines) != 6 or set(values) != fields or values['format'] != '1' or values['source'] != SOURCE:
            raise ValueError()
        if not re.fullmatch(r'[0-9a-f]{40}', values['commit']) or not re.fullmatch(r'[0-9a-f]{64}', values['sha256']):
            raise ValueError()
        datetime.datetime.strptime(values['installed_utc'], '%Y-%m-%dT%H:%M:%SZ')
        version = validate_policy(data)
        if values['policy_version'] != version:
            raise ValueError()
    except (ValueError, UnicodeError, Failure):
        raise Failure('incomplete', f'{directory}: invalid policy/provenance; preserve and reconcile')
    if digest(data) != values['sha256']:
        raise Failure('drifted', f'{directory}: checksum mismatch; preserve and reconcile')
    return data, raw, values


def destination(raw):
    path = Path(raw)
    if not path.is_absolute() or '..' in path.parts or path == Path('/'):
        raise Failure('invocation', 'Codex home must be an absolute non-root path without ..', 2)
    for item in [*reversed(path.parents), path]:
        if exists(item):
            if item.is_symlink() or not item.is_dir():
                raise Failure('unsafe-path', f'{item}: directory symlinks/special files are refused')
    if not path.parent.is_dir():
        raise Failure('prerequisite', 'Codex home parent must already exist', 2)
    return path


def preflight(home):
    destination(str(home))
    if not exists(home):
        return None
    inspect(home, directory=True)
    if exists(home / 'AGENTS.override.md'):
        raise Failure('shadowed', 'global override exists; preserve it and reconcile explicitly')
    for name in (POLICY, META, LOCK):
        if exists(home / name):
            inspect(home / name)
    if exists(home / PREVIOUS):
        inspect(home / PREVIOUS, directory=True)
        if set(p.name for p in (home / PREVIOUS).iterdir()) != {POLICY, META}:
            raise Failure('incomplete', 'previous directory contains unexpected or missing entries')
        pair(home / PREVIOUS)
    if any(p.name.startswith(STAGING) for p in home.iterdir()):
        raise Failure('incomplete', 'staging directory remains; inspect/reconcile under the policy lock')
    present = [exists(home / name) for name in (POLICY, META)]
    if any(present) and not all(present):
        raise Failure('incomplete', 'unmanaged policy or missing policy/provenance; preserve and reconcile')
    if not any(present) and exists(home / PREVIOUS):
        raise Failure('incomplete', 'previous policy exists without a current pair; reconcile explicitly')
    return pair(home) if all(present) else None


def write_new(path, data):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def lock(home):
    fd = os.open(home / LOCK, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600)
    try:
        inspect(home / LOCK)
        deadline = time.monotonic() + 5
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return fd
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise Failure('busy', 'another policy operation holds the lock; retry later')
                time.sleep(0.05)
    except BaseException:
        os.close(fd)
        raise


def publish(home, data, raw, current):
    stage = Path(tempfile.mkdtemp(prefix=STAGING, dir=home))
    # Keep failed staging for explicit recovery. Never scan/delete other stages.
    write_new(stage / POLICY, data)
    write_new(stage / META, raw)
    pair(stage)
    if current:
        backup = stage / 'next-previous'
        backup.mkdir(mode=0o700)
        write_new(backup / POLICY, current[0])
        write_new(backup / META, current[1])
        pair(backup)
        if exists(home / PREVIOUS):
            os.replace(home / PREVIOUS, stage / 'retired-previous')
        os.replace(backup, home / PREVIOUS)
    os.replace(stage / POLICY, home / POLICY)
    os.replace(stage / META, home / META)
    result = pair(home)
    if result[0] != data or result[1] != raw:
        raise Failure('incomplete', 'published pair failed verification; staging retained')
    shutil.rmtree(stage)


def execute(args):
    if args.command == 'validate-source':
        validate_policy((REPO / SOURCE).read_bytes())
        print('valid: canonical policy encoding, size, identifier, version and sections')
        return
    if args.command != 'verify' and os.getuid() == 0:
        raise Failure('invocation', 'run as the unprivileged policy owner, not root', 2)
    if args.expected and not re.fullmatch(r'[0-9a-f]{64}', args.expected):
        raise Failure('invocation', 'expected checksum must be 64 lowercase hexadecimal characters', 2)
    if args.command == 'rollback':
        if args.revision or not args.expected:
            raise Failure('invocation', 'rollback requires expected checksum and no revision', 2)
        desired = None
    else:
        if args.command == 'verify' and args.expected:
            raise Failure('invocation', 'verify does not accept an expected-current checksum', 2)
        desired = source(args.revision)
    home = destination(args.codex_home)
    current = preflight(home)
    if args.command == 'verify':
        if not current:
            raise Failure('missing', 'managed host policy is not installed')
        if current[0] != desired[0] or current[2]['commit'] != args.revision:
            raise Failure('drifted', 'installed revision/content differs from requested revision')
        print(f'current: {home / POLICY} commit={current[2]["commit"]} sha256={digest(current[0])}')
        return
    os.umask(0o077)
    if not exists(home):
        if args.command == 'rollback' or args.expected:
            raise Failure('missing', 'no current managed policy to replace')
        home.mkdir(mode=0o700)
    fd = lock(home)
    try:
        current = preflight(home)
        if args.expected and (not current or digest(current[0]) != args.expected):
            raise Failure('conflict', 'expected-current checksum differs; nothing replaced')
        if args.command == 'install' and current and current[0] == desired[0] and current[2]['commit'] == args.revision:
            print(f'current: no-op commit={args.revision} sha256={digest(current[0])}')
            return
        if current and not args.expected:
            raise Failure('conflict', 'replacement requires --expected-current-sha256')
        if args.command == 'rollback':
            if not current or not exists(home / PREVIOUS):
                raise Failure('missing', 'no previous managed revision to restore')
            previous = pair(home / PREVIOUS)
            desired = previous[:2]
        publish(home, *desired, current)
        result = pair(home)
        print(f'{args.command}: {home / POLICY} commit={result[2]["commit"]} sha256={digest(result[0])}; verify in a fresh remote task')
    finally:
        os.close(fd)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('install', 'verify', 'rollback', 'validate-source'))
    parser.add_argument('--revision')
    parser.add_argument('--codex-home', default=os.environ.get('CODEX_HOME', str(Path.home() / '.codex')))
    parser.add_argument('--expected-current-sha256', dest='expected')
    try:
        execute(parser.parse_args())
    except Failure as error:
        print(str(error), file=sys.stderr)
        return error.code
    except OSError as error:
        print(f'incomplete: filesystem operation failed ({error.strerror}); inspect state before retrying', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
