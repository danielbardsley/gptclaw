"""Bounded, observation-only inventory. Repository content is never executed."""
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import time

from project_manifest import MESSAGES, validate_project

DIRECTORY_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
MAX_CANDIDATES = 256
MAX_ENTRIES = 4096
MAX_OUTPUT = 1024 * 1024
MAX_REGISTRY = 128 * 1024
SCAN_SECONDS = 10
# Managed source-only task checkouts are never independent dashboard projects.
NAME = re.compile(r'[A-Za-z0-9][A-Za-z0-9._-]{0,127}')
ID = re.compile(r'[a-z][a-z0-9]*(?:-[a-z0-9]+)*')
REPOSITORY = re.compile(r'https://github\.com/[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})/[A-Za-z0-9_.-]{1,100}')


class InventoryError(Exception):
    """Fixed diagnostic codes only; no raw filesystem or source values."""


def open_directory(path):
    path = Path(path)
    if not path.is_absolute() or '..' in path.parts:
        raise InventoryError('unsafe-path')
    fd = os.open('/', DIRECTORY_FLAGS)
    try:
        for part in path.parts[1:]:
            child = os.open(part, DIRECTORY_FLAGS, dir_fd=fd)
            os.close(fd)
            fd = child
        if os.fstat(fd).st_uid != os.getuid():
            raise InventoryError('ownership')
        return fd
    except BaseException:
        os.close(fd)
        raise


def identity(info):
    return (info.st_dev, info.st_ino, info.st_uid)


def owned_directory(parent, name):
    before = os.stat(name, dir_fd=parent, follow_symlinks=False)
    if not stat.S_ISDIR(before.st_mode) or before.st_uid != os.getuid():
        raise InventoryError('unsafe-path')
    fd = os.open(name, DIRECTORY_FLAGS, dir_fd=parent)
    if identity(before) != identity(os.fstat(fd)):
        os.close(fd)
        raise InventoryError('path-changed')
    return fd


def regular(info):
    return stat.S_ISREG(info.st_mode) and info.st_uid == os.getuid() and info.st_nlink == 1


def presence(root_fd, parts):
    fd = os.dup(root_fd)
    try:
        for part in parts[:-1]:
            child = owned_directory(fd, part)
            os.close(fd)
            fd = child
        info = os.stat(parts[-1], dir_fd=fd, follow_symlinks=False)
        return 'present' if regular(info) else 'unavailable'
    except FileNotFoundError:
        return 'missing'
    except (OSError, InventoryError):
        return 'unavailable'
    finally:
        os.close(fd)


def repository_url(value):
    if not isinstance(value, str) or not REPOSITORY.fullmatch(value):
        return None
    owner, repo = value.removeprefix('https://github.com/').split('/')
    if owner.endswith('-') or repo in ('.', '..') or repo.endswith('.git'):
        return None
    return value


def load_registry(path):
    if path is None:
        return {}, 'missing'
    parent = None
    try:
        path = Path(path)
        parent = open_directory(path.parent)
        before = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
        if not regular(before) or before.st_mode & 0o022 or before.st_size > MAX_REGISTRY:
            raise InventoryError('metadata-invalid')
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        with os.fdopen(fd, 'rb') as stream:
            opened = os.fstat(stream.fileno())
            if not regular(opened) or identity(opened) != identity(before):
                raise InventoryError('metadata-invalid')
            data = stream.read(MAX_REGISTRY + 1)
        if len(data) > MAX_REGISTRY:
            raise InventoryError('metadata-invalid')
        def unique(pairs):
            result = {}
            for key, val in pairs:
                if key in result:
                    raise InventoryError('metadata-invalid')
                result[key] = val
            return result
        value = json.loads(data, object_pairs_hook=unique)
        if (not isinstance(value, dict) or type(value.get('schema_version')) is not int
                or value['schema_version'] != 1 or not isinstance(value.get('projects'), list)
                or len(value['projects']) > MAX_CANDIDATES):
            raise InventoryError('metadata-invalid')
        result = {}
        for item in value['projects']:
            if not isinstance(item, dict):
                raise InventoryError('metadata-invalid')
            root, project = item.get('root'), item.get('id')
            if (not isinstance(root, str) or len(root) > 4096 or not Path(root).is_absolute()
                    or '..' in Path(root).parts or str(Path(root)) != root
                    or not isinstance(project, str) or len(project) > 48 or not ID.fullmatch(project)):
                raise InventoryError('metadata-invalid')
            owner = item.get('owner')
            if owner is not None and (not isinstance(owner, str) or not owner.strip()
                    or len(owner) > 100 or any(ord(c) < 32 or 127 <= ord(c) <= 159 for c in owner)):
                raise InventoryError('metadata-invalid')
            repo = item.get('repository')
            if repo is not None and repository_url(repo) is None:
                raise InventoryError('metadata-invalid')
            key = (root, project)
            if key in result:
                raise InventoryError('metadata-invalid')
            # Unknown fields never enter a response or cause additional reads.
            result[key] = {'owner': owner, 'repository': repo}
        return result, 'available'
    except FileNotFoundError:
        return {}, 'missing'
    except (OSError, ValueError, InventoryError, RecursionError):
        return {}, 'invalid'
    finally:
        if parent is not None:
            os.close(parent)


class Scanner:
    def __init__(self, projects, *, registry=None, capabilities=None, clock=time.time,
                 monotonic=time.monotonic, max_candidates=MAX_CANDIDATES, max_entries=MAX_ENTRIES,
                 deadline=SCAN_SECONDS, max_output=MAX_OUTPUT):
        self.projects = Path(projects)
        self.registry = registry
        self.capabilities = capabilities
        self.clock, self.monotonic = clock, monotonic
        self.max_candidates, self.max_entries = max_candidates, max_entries
        self.deadline, self.max_output = deadline, max_output
        self.bindings = {}

    def support(self, version):
        caps = self.capabilities
        if (not isinstance(caps, dict) or caps.get('provider') != 'gptclawctl'
                or not isinstance(caps.get('project_manifest_schemas'), list)):
            return 'unavailable'
        return 'supported' if version in caps['project_manifest_schemas'] else 'unsupported'

    def candidate(self, root_fd, name, metadata):
        fd = owned_directory(root_fd, name)
        try:
            info = os.fstat(fd)
            from project_worktrees import managed
            from private_apps import AppError
            try:is_task=managed(self.projects/name)
            except AppError:raise InventoryError('unsafe-path') from None
            if is_task:raise FileNotFoundError
            meta = owned_directory(fd, '.gptclaw')
            try:
                file_info = os.stat('project.yaml', dir_fd=meta, follow_symlinks=False)
                if not regular(file_info):
                    raise InventoryError('unsafe-manifest')
            finally:
                os.close(meta)
            result, contract, code = validate_project(self.projects / name, directory_fd=fd)
            if code:
                reason = result['errors'][0]['code'] if result.get('errors') else 'internal'
                raise InventoryError(reason if reason in MESSAGES else 'validation-failed')
            # Refuse directory replacement, even when the pinned original validated.
            after = os.stat(name, dir_fd=root_fd, follow_symlinks=False)
            if identity(after) != identity(info) or not stat.S_ISDIR(after.st_mode):
                raise InventoryError('path-changed')
            project = contract['project']
            root = str(self.projects / name)
            key = hashlib.sha256((root + '\0' + project['id'] + '\0' + str(identity(info))).encode()).hexdigest()[:32]
            components = sorted(contract['components']) if contract['schema_version'] in (3, 4) else [project['kind']]
            fields = metadata.get((root, project['id']), {})
            row = {'key': key, 'id': project['id'], 'name': project['name'], 'kind': project['kind'],
                   'components': components, 'location': name, 'manifest_version': contract['schema_version'],
                   'runtime_support': self.support(contract['schema_version']), 'identity_state': 'valid',
                   'owner': fields.get('owner'), 'repository': fields.get('repository'),
                   'documentation': {'readme': presence(fd, ['README.md']),
                                     'index': presence(fd, ['docs', 'README.md'])}}
            binding = {'root': root, 'id': project['id'], 'identity': identity(info), 'components': components}
            return row, binding
        finally:
            os.close(fd)

    def scan(self):
        observed = self.clock()
        result = {'schema_version': 1, 'snapshot_id': '0'*32, 'observed_at': observed, 'last_success_at': None,
                  'freshness': 'unavailable', 'complete': False, 'truncated': False,
                  'metadata_state': 'missing', 'rows': [], 'diagnostics': []}
        diagnostics = result['diagnostics']
        metadata, result['metadata_state'] = load_registry(self.registry)
        if result['metadata_state'] == 'invalid':
            diagnostics.append({'code': 'metadata-invalid'})
        root_fd = None
        started = self.monotonic()
        bindings = {}
        try:
            root_fd = open_directory(self.projects)
            names = []
            with os.scandir(root_fd) as entries:
                for count, entry in enumerate(entries):
                    if count >= self.max_entries or self.monotonic() - started >= self.deadline:
                        result['truncated'] = True
                        break
                    if entry.name.startswith('.'):
                        continue
                    if not NAME.fullmatch(entry.name):
                        diagnostics.append({'code': 'unsafe-entry'})
                        continue
                    if entry.is_symlink():
                        diagnostics.append({'code': 'unsafe-path'})
                        continue
                    if entry.is_dir(follow_symlinks=False):
                        names.append(entry.name)
            names.sort()
            if len(names) > self.max_candidates:
                result['truncated'] = True
            for name in names[:self.max_candidates]:
                if self.monotonic() - started >= self.deadline:
                    result['truncated'] = True
                    break
                try:
                    row, binding = self.candidate(root_fd, name, metadata)
                    result['rows'].append(row)
                    bindings[row['key']] = binding
                except FileNotFoundError:
                    # No declaration: outside managed inventory, not an invalid project.
                    continue
                except PermissionError:
                    diagnostics.append({'code': 'input_unreadable'})
                except InventoryError as error:
                    diagnostics.append({'code': str(error)})
                except OSError:
                    diagnostics.append({'code': 'input_unreadable'})
            counts = Counter(row['id'] for row in result['rows'])
            for row in result['rows']:
                if counts[row['id']] > 1:
                    row['identity_state'] = 'conflict'
                    bindings.pop(row['key'], None)
            # Cap diagnostics as well as rows; do not echo invalid candidate contents/names.
            if len(diagnostics) > 50:
                result['truncated'] = True
                del diagnostics[50:]
            result.update(freshness='current', last_success_at=self.clock(),
                          complete=not result['truncated'] and not diagnostics)
            while len(json.dumps(result).encode()) > self.max_output and result['rows']:
                removed = result['rows'].pop()
                bindings.pop(removed['key'], None)
                result.update(truncated=True, complete=False)
            self.bindings = bindings
        except (OSError, InventoryError):
            result['diagnostics'] = [{'code': 'inventory-unavailable'}]
        finally:
            if root_fd is not None:
                os.close(root_fd)
        result['snapshot_id'] = hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest()[:32]
        return result
