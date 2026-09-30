#!/usr/bin/env python3
"""Create the reviewed planning starter. Linux/POSIX, Python stdlib + Git only.

No template command execution, installs, remotes, commits, or automatic repair.
Partial publication preserves the target and its in-progress marker.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import tempfile
import unicodedata

SOURCE_ROOT = Path(__file__).resolve().parents[1]
SOURCE_URL = 'https://github.com/danielbardsley/gptclaw'
STARTER = 'templates/projects/planning/'
SKILL = '.agents/skills/gptclaw-specification/'
TEMPLATES = {
    'README.md.template': 'README.md',
    'AGENTS.md.template': 'AGENTS.md',
    'gitignore.template': '.gitignore',
    'docs/README.md.template': 'docs/README.md',
    'docs/platform/features.md.template': 'docs/platform/features.md',
}
SKILL_FILES = {'SKILL.md', 'assets/spec.md', 'assets/technical-design.md',
               'assets/tasks.md', 'assets/acceptance.md'}
PROVENANCE = 'docs/bootstrap-provenance.json'
MARKER = '.gptclaw-bootstrap-in-progress'
DIRECTORY_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW


class BootstrapError(Exception):
    pass


def git(root, *args, check=True):
    # Do not inherit alternate repositories, global templates, hooks, or config.
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    env.update(GIT_CONFIG_GLOBAL='/dev/null', GIT_CONFIG_NOSYSTEM='1',
               GIT_TERMINAL_PROMPT='0')
    result = subprocess.run(['git', '-c', 'core.hooksPath=/dev/null', '-c', 'core.fsmonitor=false',
                             '-C', str(root), *args], env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and result.returncode:
        raise BootstrapError('Git operation failed: ' + args[0])
    return result


def digest(data):
    return hashlib.sha256(data).hexdigest()


def metadata(name, purpose, owner):
    values = {'PROJECT_NAME': name, 'PROJECT_PURPOSE': purpose, 'PROJECT_OWNER': owner}
    for key, value in values.items():
        if (not value.strip() or len(value) > 1000 or '{{' in value or '}}' in value
                or any(unicodedata.category(c).startswith('C') for c in value)):
            raise BootstrapError('Invalid single-line metadata: ' + key)
    return values


def markdown(value):
    return re.sub(r'([\\`*_{}\[\]()<>#!|])', r'\\\1', value)


def load_payload(source, revision, values):
    if not re.fullmatch(r'[0-9a-f]{40}', revision):
        raise BootstrapError('Source revision must be a full lowercase commit SHA')
    actual = git(source, 'rev-parse', '--verify', revision + '^{commit}').stdout.decode().strip()
    if actual != revision:
        raise BootstrapError('Source must identify a commit, not a tag object')
    entries = {}
    tree = git(source, 'ls-tree', '-r', '-z', revision, '--', STARTER, SKILL).stdout
    for item in tree.split(b'\0'):
        if not item:
            continue
        header, raw_path = item.split(b'\t', 1)
        mode, kind, oid = header.decode().split()
        path = raw_path.decode('utf-8')
        if mode != '100644' or kind != 'blob':
            raise BootstrapError('Source contains non-regular resource: ' + path)
        entries[path] = oid
    expected = {STARTER + x for x in TEMPLATES} | {STARTER + 'VERSION'} | {SKILL + x for x in SKILL_FILES}
    if set(entries) != expected:
        raise BootstrapError('Source package inventory differs from reviewed allowlist')
    blobs = {}
    for path, oid in entries.items():
        size = int(git(source, 'cat-file', '-s', oid).stdout)
        if size > 65536:
            raise BootstrapError('Source resource exceeds 64 KiB: ' + path)
        blobs[path] = git(source, 'cat-file', 'blob', oid).stdout
    version = blobs[STARTER + 'VERSION'].decode().strip()
    if not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', version):
        raise BootstrapError('Invalid starter version')
    payload = {}
    for template, target in TEMPLATES.items():
        def replace(match):
            if match[1] not in values:
                raise BootstrapError('Unknown starter placeholder: ' + match[1])
            return markdown(values[match[1]])
        rendered = re.sub(r'\{\{([^{}]+)\}\}', replace, blobs[STARTER + template].decode())
        if '{{' in rendered or '}}' in rendered:
            raise BootstrapError('Unresolved starter placeholder')
        payload[target] = rendered.encode()
    for filename in SKILL_FILES:
        payload[SKILL + filename] = blobs[SKILL + filename]
    record = {'schema_version': 1, 'source_repository': SOURCE_URL,
              'source_revision': revision, 'starter': 'planning',
              'starter_version': version, 'inputs': values,
              'files': {name: digest(data) for name, data in sorted(payload.items())}}
    payload[PROVENANCE] = (json.dumps(record, indent=2, sort_keys=True) + '\n').encode()
    validate_payload(payload)
    return payload


def validate_payload(payload):
    if len(payload['AGENTS.md']) > 8192:
        raise BootstrapError('Generated guidance exceeds 8 KiB')
    skill_text = payload[SKILL + 'SKILL.md'].decode()
    if not skill_text.startswith('---\nname: gptclaw-specification\n') or '\ndescription: ' not in skill_text:
        raise BootstrapError('Invalid specification skill metadata')
    for name, data in payload.items():
        if not name.endswith('.md'):
            continue
        for link in re.findall(r'(?<!\\)\]\(([^)]+)\)', data.decode('utf-8')):
            if '://' in link or link.startswith('#'):
                continue
            parts = list(PurePosixPath(name).parent.parts)
            for part in PurePosixPath(link.split('#')[0]).parts:
                if part == '..':
                    if not parts:
                        raise BootstrapError('Link escapes generated project')
                    parts.pop()
                elif part not in ('.', ''):
                    parts.append(part)
            if '/'.join(parts) not in payload:
                raise BootstrapError('Broken generated file link: ' + name + ': ' + link)


def identity(st):
    return st.st_dev, st.st_ino


def checked_path(destination):
    raw = Path(destination)
    if '..' in raw.parts:
        raise BootstrapError('Path traversal is not allowed')
    path = Path(os.path.abspath(raw))
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', path.name) or len(path.name) > 64:
        raise BootstrapError('Destination basename must be a lowercase hyphenated slug, max 64 characters')
    for component in [*reversed(path.parents), path]:
        if component.is_symlink():
            raise BootstrapError('Symlink path component: ' + str(component))
    if not path.parent.is_dir():
        raise BootstrapError('Destination parent must already exist')
    for ancestor in path.parents:
        if (ancestor / '.git').exists() or (ancestor / '.git').is_symlink():
            raise BootstrapError('Destination is nested inside an existing Git repository')
    if git(path.parent, 'rev-parse', '--git-dir', check=False).returncode == 0:
        raise BootstrapError('Destination parent belongs to an existing Git repository')
    return path


def file_inventory(root):
    files = set()
    directories = set()
    for parent, dirs, names in os.walk(root, followlinks=False):
        for name in dirs + names:
            path = Path(parent) / name
            mode = path.lstat().st_mode
            if not (stat.S_ISDIR(mode) or stat.S_ISREG(mode)):
                raise BootstrapError('Non-regular output entry: ' + str(path))
        for name in names:
            files.add(str((Path(parent) / name).relative_to(root)))
        for name in dirs:
            directories.add(str((Path(parent) / name).relative_to(root)))
    return files, directories


def verify_output(path, payload, allow_marker=False):
    files, dirs = file_inventory(path)
    project_files = {x for x in files if not x.startswith('.git/')}
    expected = set(payload) | ({MARKER} if allow_marker else set())
    if project_files != expected:
        raise BootstrapError('Occupied, incomplete, or modified destination; preserve and inspect: ' + str(path))
    expected_dirs = {str(parent) for name in payload for parent in PurePosixPath(name).parents if str(parent) != '.'}
    if {x for x in dirs if x != '.git' and not x.startswith('.git/')} != expected_dirs:
        raise BootstrapError('Unexpected output directories')
    for name, data in payload.items():
        p = path / name
        if p.stat().st_size != len(data) or p.read_bytes() != data:
            raise BootstrapError('Modified output: ' + name)
    if not (path / '.git').is_dir():
        raise BootstrapError('Missing local Git directory')
    if Path(git(path, 'rev-parse', '--show-toplevel').stdout.decode().strip()).resolve() != path.resolve():
        raise BootstrapError('Unexpected Git boundary')
    if git(path, 'symbolic-ref', 'HEAD').stdout.strip() != b'refs/heads/main':
        raise BootstrapError('Expected local main branch')
    if git(path, 'rev-parse', '--verify', 'HEAD', check=False).returncode == 0:
        raise BootstrapError('Existing commits require separate adoption')
    if git(path, 'remote').stdout.strip() or git(path, 'ls-files', '-z').stdout:
        raise BootstrapError('Existing remotes or staged files require separate adoption')


def guard(path, root_fd, parent_fd):
    # Validate named identities as well as anchoring writes to opened descriptors.
    if checked_path(path) != path:
        raise BootstrapError('Destination changed')
    if identity(path.parent.stat()) != identity(os.fstat(parent_fd)):
        raise BootstrapError('Destination parent changed')
    if identity(path.lstat()) != identity(os.fstat(root_fd)):
        raise BootstrapError('Destination identity changed; published files preserved')


def copy_exclusive(stage, target_fd, check):
    for entry in sorted(stage.iterdir()):
        check()
        if entry.is_dir():
            os.mkdir(entry.name, mode=0o755, dir_fd=target_fd)
            child_fd = os.open(entry.name, DIRECTORY_FLAGS, dir_fd=target_fd)
            try:
                def child_check():
                    check()
                    st = os.stat(entry.name, dir_fd=target_fd, follow_symlinks=False)
                    if not stat.S_ISDIR(st.st_mode) or identity(st) != identity(os.fstat(child_fd)):
                        raise BootstrapError('Output directory changed during publication')
                copy_exclusive(entry, child_fd, child_check)
            finally:
                os.close(child_fd)
        else:
            # Staging shares the parent filesystem; hardlink creation never replaces.
            os.link(entry, entry.name, dst_dir_fd=target_fd, follow_symlinks=False)


def create(source, revision, destination, name, purpose, owner, check_only=False):
    values = metadata(name, purpose, owner)
    payload = load_payload(source, revision, values)
    path = checked_path(destination)
    print(json.dumps({'destination': str(path), 'source_revision': revision,
                      'files': sorted(payload), 'operation': 'check' if check_only else 'create'}), flush=True)
    original = None
    if path.exists():
        if not path.is_dir():
            raise BootstrapError('Destination is not a directory')
        original = identity(path.stat())
        if any(path.iterdir()):
            verify_output(path, payload)
            return {'status': 'already-created', 'destination': str(path)}
    if check_only:
        return {'status': 'ready', 'destination': str(path)}
    parent_fd = os.open(path.parent, DIRECTORY_FLAGS)
    try:
        # Anchor staging and cleanup to the already-open parent even if renamed.
        # A child Git process can resolve this process's fd through Linux procfs.
        anchored_parent = Path(f'/proc/{os.getpid()}/fd/{parent_fd}')
        with tempfile.TemporaryDirectory(prefix='.gptclaw-staging-', dir=anchored_parent) as scratch:
            stage = Path(scratch)
            for filename, content in payload.items():
                output = stage / filename
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_bytes(content)
                output.chmod(0o644)
            git(stage, 'init', '--quiet', '--initial-branch=main', '--template=')
            verify_output(stage, payload)
            if checked_path(path) != path or identity(path.parent.stat()) != identity(os.fstat(parent_fd)):
                raise BootstrapError('Destination parent changed before publication')
            if original is None:
                os.mkdir(path.name, mode=0o755, dir_fd=parent_fd)
            root_fd = os.open(path.name, DIRECTORY_FLAGS, dir_fd=parent_fd)
            try:
                if original is not None and identity(os.fstat(root_fd)) != original:
                    raise BootstrapError('Existing empty destination changed identity')
                guard(path, root_fd, parent_fd)
                if os.listdir(root_fd):
                    raise BootstrapError('Destination became occupied before publication')
                marker_fd = os.open(MARKER, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                                    0o600, dir_fd=root_fd)
                try:
                    os.write(marker_fd, (revision + '\n').encode())
                    marker_identity = identity(os.fstat(marker_fd))
                finally:
                    os.close(marker_fd)
                guard(path, root_fd, parent_fd)
                if os.listdir(root_fd) != [MARKER]:
                    raise BootstrapError('Destination changed during reservation')
                copy_exclusive(stage, root_fd, lambda: guard(path, root_fd, parent_fd))
                guard(path, root_fd, parent_fd)
                verify_output(path, payload, allow_marker=True)
                if identity(os.stat(MARKER, dir_fd=root_fd, follow_symlinks=False)) != marker_identity:
                    raise BootstrapError('Reservation marker changed')
                os.unlink(MARKER, dir_fd=root_fd)
            finally:
                os.close(root_fd)
    finally:
        os.close(parent_fd)
    return {'status': 'created', 'destination': str(path), 'git': 'main; no commits or remote; generated files untracked',
            'readiness': 'planning only; supported-client discovery unverified'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-revision', required=True)
    parser.add_argument('--destination', required=True)
    parser.add_argument('--name', required=True)
    parser.add_argument('--purpose', required=True)
    parser.add_argument('--owner', required=True)
    parser.add_argument('--check', action='store_true', help='Validate inputs and conflicts without writing')
    args = parser.parse_args()
    try:
        result = create(SOURCE_ROOT, args.source_revision, args.destination, args.name,
                        args.purpose, args.owner, args.check)
        print(json.dumps(result))
    except (BootstrapError, OSError, UnicodeError, ValueError) as error:
        print('Bootstrap stopped: ' + str(error) + '. Preserve the destination; inspect any in-progress marker before recovery.', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
