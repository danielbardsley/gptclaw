"""SYS-003: bounded project dependency jobs and recoverable file publication."""
import base64
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import time
import urllib.parse
import uuid

import yaml
from project_manifest import JsonLoader, StrictValidator

FILES = ('package.json', 'pnpm-lock.yaml', 'pnpm-workspace.yaml')
GROUPS = ('dependencies', 'devDependencies', 'optionalDependencies')
VERSION_RE = r'(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?'
NAME_RE = r'(?:@[a-z0-9][a-z0-9._-]*/)?[a-z0-9][a-z0-9._-]*'
GUARD_ENV = {
    'pnpm_config_pm_on_fail': 'error', 'pnpm_config_ignore_scripts': 'true',
    'pnpm_config_runtime': 'false', 'pnpm_config_ignore_pnpmfile': 'true',
    'pnpm_config_verify_deps_before_run': 'false',
    'pnpm_config_registry': 'https://registry.npmjs.org/',
    'pnpm_config_block_exotic_subdeps': 'true',
}
INSTALL_FLAGS = ['--ignore-scripts', '--no-runtime', '--pm-on-fail=error',
                 '--ignore-pnpmfile', '--registry=https://registry.npmjs.org/',
                 '--store-dir=/workspace/.gptclaw-cache/pnpm', '--reporter=silent',
                 '--config.@jsr:registry=https://registry.npmjs.org/']
FORBIDDEN = ('.npmrc', '.pnpmfile.cjs', '.pnpmfile.mjs', '.pnpmfile.js',
             'pnpmfile.cjs', 'pnpmfile.mjs', '.yarnrc', '.yarnrc.yml', '.pnp.cjs',
             '.env', '.env.local', '.env.development', '.env.production', '.ssh', '.aws')
PHASES = {'resolving', 'verified', 'publishing', 'repairing', 'complete', 'failed', 'unknown', 'conflict', 'aborted'}


def app():
    import private_apps
    return private_apps


def check(condition, code='dependency-policy'):
    app().need(condition, code)


def read_bytes(path, limit=2 * 1024 * 1024):
    path = app().safe(Path(path))
    try: fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except OSError: raise app().AppError('dependency-policy') from None
    with os.fdopen(fd, 'rb') as source:
        info = os.fstat(source.fileno())
        check(stat.S_ISREG(info.st_mode) and info.st_uid == os.getuid() and info.st_nlink == 1, 'path')
        check(info.st_size <= limit)
        data = source.read(limit + 1)
        check(len(data) <= limit)
        return data


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        check(key not in result)
        result[key] = value
    return result


def json_data(data):
    try:
        value = json.loads(data, object_pairs_hook=unique_pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
        check(isinstance(value, dict))
        return value
    except (ValueError, UnicodeError, RecursionError):
        raise app().AppError('dependency-policy') from None


def yaml_documents(data, maximum=1):
    try:
        text = data.decode('utf-8'); depth = count = documents = 0
        for event in yaml.parse(text, Loader=JsonLoader):
            count += 1
            check(count <= 100000)
            check(not isinstance(event, yaml.events.AliasEvent) and getattr(event, 'anchor', None) is None)
            check(getattr(event, 'tag', None) is None)
            if isinstance(event, yaml.events.DocumentStartEvent):
                documents += 1; check(documents <= maximum)
            if isinstance(event, (yaml.events.MappingStartEvent, yaml.events.SequenceStartEvent)):
                depth += 1; check(depth <= 32)
            elif isinstance(event, (yaml.events.MappingEndEvent, yaml.events.SequenceEndEvent)):
                depth -= 1
        check(1 <= documents <= maximum)
        loader = JsonLoader(text)
        try:
            def construct(node):
                if isinstance(node, yaml.nodes.MappingNode):
                    result = {}
                    for key, val in node.value:
                        check(isinstance(key, yaml.nodes.ScalarNode) and key.tag == 'tag:yaml.org,2002:str')
                        check(key.value != '<<' and key.value not in result)
                        result[key.value] = construct(val)
                    return result
                if isinstance(node, yaml.nodes.SequenceNode):
                    return [construct(n) for n in node.value]
                check(node.tag in {'tag:yaml.org,2002:str', 'tag:yaml.org,2002:int',
                                   'tag:yaml.org,2002:bool', 'tag:yaml.org,2002:null', 'tag:yaml.org,2002:float'})
                return loader.construct_object(node)
            result = []
            while loader.check_node():
                value = construct(loader.get_node()); check(isinstance(value, dict)); result.append(value)
            return result
        finally:
            loader.dispose()
    except (yaml.YAMLError, UnicodeError, ValueError, RecursionError):
        raise app().AppError('dependency-policy') from None


def policy():
    a = app()
    value = json_data(read_bytes(a.REPO/'config/project-dependencies/v1.json', 65536))
    schema = json_data(read_bytes(a.REPO/'schemas/project-dependencies/v1.schema.json', 65536))
    check(not list(StrictValidator(schema).iter_errors(value)))
    effective={'policy':value,'environment':GUARD_ENV,'install_flags':INSTALL_FLAGS}
    return value, hashlib.sha256(json.dumps(effective, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def package_name(name):
    check(isinstance(name, str) and len(name) <= 214 and re.fullmatch(NAME_RE, name))
    return name


def exact_version(version):
    check(isinstance(version, str) and len(version) <= 100 and re.fullmatch(VERSION_RE, version))
    return version


def package_key(key):
    check(isinstance(key, str))
    base = key.split('(', 1)[0]
    match = re.fullmatch('('+NAME_RE+')@('+VERSION_RE+')', base)
    check(match is not None)
    return match.group(1), match.group(2)


def validate_package(value, p):
    check(value.get('packageManager') == 'pnpm@'+p['manager_version'])
    check(not any(k in value for k in ('pnpm', 'workspaces', 'devEngines', 'configDependencies',
                                     'packageManagerDependencies', 'runtimeDependencies', 'resolutions', 'overrides')))
    engines = value.get('engines', {})
    check(isinstance(engines, dict) and set(engines) <= {'node', 'pnpm'})
    scripts = value.get('scripts', {})
    check(isinstance(scripts, dict) and all(isinstance(k, str) and isinstance(v, str) for k, v in scripts.items()))
    seen = set()
    for group in GROUPS:
        deps = value.get(group, {}); check(isinstance(deps, dict) and len(deps) <= 500)
        for name, version in deps.items():
            package_name(name); exact_version(version)
            check(name not in seen); seen.add(name)
    # Peer ranges may constrain compatibility but may not introduce exotic sources.
    peers = value.get('peerDependencies', {}); check(isinstance(peers, dict))
    for name, version in peers.items():
        package_name(name)
        check(isinstance(version, str) and re.fullmatch(r'[0-9A-Za-z.*+^~<>=| -]+', version))


def validate_workspace(value, p):
    check(set(value) <= {'packages', 'minimumReleaseAge', 'minimumReleaseAgeExclude'})
    check(value.get('packages', ['.']) == ['.'])
    age = value.get('minimumReleaseAge', 1440)
    check(type(age) is int and 1440 <= age <= 525600)
    exclusions = value.get('minimumReleaseAgeExclude', [])
    check(isinstance(exclusions, list) and all(isinstance(x, str) and x in p['release_age_exclusions'] for x in exclusions))
    check(len(exclusions) == len(set(exclusions)))


def validate_lock(documents, manifest, p, coherent=True):
    applications = []
    manager_count = 0
    for document in documents:
        check(document.get('lockfileVersion') == '9.0')
        check(set(document) <= {'lockfileVersion', 'settings', 'importers', 'packages', 'snapshots'})
        importers = document.get('importers'); check(isinstance(importers, dict) and set(importers) == {'.'})
        importer = importers['.']; check(isinstance(importer, dict))
        if 'packageManagerDependencies' in importer or 'configDependencies' in importer:
            manager_count += 1; check(manager_count <= 1)
            check(set(importer) <= {'packageManagerDependencies', 'configDependencies'})
            check(importer.get('configDependencies', {}) == {})
            check(importer.get('packageManagerDependencies') == {'pnpm': {'specifier': p['manager_version'], 'version': p['manager_version']}})
        else:
            applications.append((importer, document.get('packages', {}))); check(set(importer) <= set(GROUPS))
        settings = document.get('settings', {})
        check(isinstance(settings, dict) and set(settings) <= {'autoInstallPeers', 'excludeLinksFromLockfile'})
        check(settings.get('autoInstallPeers', True) is True and settings.get('excludeLinksFromLockfile', False) is False)
        packages = document.get('packages', {}); check(isinstance(packages, dict))
        for key, value in packages.items():
            package_key(key); check(isinstance(value, dict))
            resolution = value.get('resolution'); check(isinstance(resolution, dict) and set(resolution) <= {'integrity', 'tarball'})
            integrity = resolution.get('integrity', '')
            check(isinstance(integrity, str) and integrity.startswith('sha512-'))
            try: check(len(base64.b64decode(integrity[7:], validate=True)) == 64)
            except (ValueError, base64.binascii.Error): raise app().AppError('dependency-policy') from None
            if 'tarball' in resolution:
                url = urllib.parse.urlsplit(resolution['tarball'])
                check(url.scheme == 'https' and url.netloc == 'registry.npmjs.org' and not url.query and not url.fragment)
        snapshots = document.get('snapshots', {}); check(isinstance(snapshots, dict))
        for key, value in snapshots.items():
            name, version = package_key(key); check(name+'@'+version in packages and isinstance(value, dict))
            for group in ('dependencies', 'optionalDependencies'):
                deps = value.get(group, {}); check(isinstance(deps, dict))
                for name, version in deps.items():
                    package_name(name); check(isinstance(version, str)); exact_version(version.split('(', 1)[0])
                    check(name+'@'+version.split('(', 1)[0] in packages)
    check(len(applications) == 1)
    importer, packages = applications[0]
    for group in GROUPS:
        declarations = manifest.get(group, {}); entries = importer.get(group, {})
        check(isinstance(entries, dict))
        if coherent: check(set(entries) == set(declarations))
        for name, entry in entries.items():
            package_name(name); check(isinstance(entry, dict) and set(entry) == {'specifier', 'version'})
            exact_version(entry['specifier']); check(isinstance(entry['version'], str)); exact_version(entry['version'].split('(', 1)[0])
            check(name+'@'+entry['version'].split('(', 1)[0] in packages)
            if coherent: check(entry['specifier'] == declarations[name] and entry['version'].split('(', 1)[0] == declarations[name])


def context(root, coherent=True):
    root = app().safe(Path(root)); p, digest = policy()
    for name in FORBIDDEN:
        path = root/name
        check(not path.exists() and not path.is_symlink())
    blobs = {name: read_bytes(root/name, 65536 if name != 'pnpm-lock.yaml' else 2*1024*1024) for name in FILES}
    manifest = json_data(blobs['package.json']); validate_package(manifest, p)
    workspace = yaml_documents(blobs['pnpm-workspace.yaml'])[0]; validate_workspace(workspace, p)
    validate_lock(yaml_documents(blobs['pnpm-lock.yaml'], 2), manifest, p, coherent)
    return {'policy': p, 'policy_hash': digest, 'files': blobs, 'manifest': manifest,
            'hashes': {k: hashlib.sha256(v).hexdigest() for k, v in blobs.items()}}


def location(slug):
    package_name(slug)
    check('/' not in slug and not slug.startswith('@'))
    return app().safe(app().STORE/'dependencies'/slug)


def load_journal(slug, root, operation_id=None):
    if operation_id is not None:
        check(isinstance(operation_id,str) and re.fullmatch(r'[0-9a-f]{32}',operation_id))
    path = location(slug)/'receipts'/(operation_id+'.json') if operation_id else location(slug)/'journal.json'
    if not path.exists():
        check(not path.is_symlink(), 'path'); return None
    value = json_data(read_bytes(path, 65536))
    keys = {'schema_version', 'project', 'root', 'operation_id', 'action', 'phase', 'before', 'after',
            'policy_hash', 'image', 'changed_files', 'error', 'duration_seconds', 'retained_files', 'request'}
    check(set(value) == keys and type(value.get('schema_version')) is int and value['schema_version'] == 1)
    check(value.get('project') == slug and value.get('root') == str(root), 'conflict')
    check(isinstance(value.get('operation_id'), str) and re.fullmatch(r'[0-9a-f]{32}', value['operation_id']))
    check(operation_id is None or value['operation_id']==operation_id, 'conflict')
    check(type(value.get('retained_files')) is bool)
    request=value.get('request'); check(isinstance(request,dict) and set(request) <= {'package','version','kind'})
    if request:
        package_name(request.get('package'))
        if 'version' in request: exact_version(request['version'])
        check(request.get('kind','runtime') in {'runtime','development','optional'})
    check(value.get('phase') in PHASES and value.get('action') in {'install', 'add', 'update', 'remove'})
    for field in ('before', 'after'):
        hashes = value.get(field, {})
        check(isinstance(hashes, dict) and (set(hashes) == set(FILES) if hashes else field == 'after'))
        check(all(isinstance(v, str) and re.fullmatch(r'[0-9a-f]{64}', v) for v in hashes.values()))
    check(isinstance(value.get('policy_hash'),str) and re.fullmatch(r'[0-9a-f]{64}', value['policy_hash']) is not None)
    check(isinstance(value.get('image'),str) and re.fullmatch(r'sha256:[0-9a-f]{64}', value['image']) is not None)
    check(isinstance(value.get('changed_files'), list) and set(value['changed_files']) <= set(FILES))
    check(value.get('error') is None or value['error'] in app().MESSAGES)
    check(type(value.get('duration_seconds')) in (int, float) and 0 <= value['duration_seconds'] <= 86400)
    return value


def pending(root, slug):
    journal = load_journal(slug, root)
    return journal if journal and journal['phase'] not in {'complete', 'aborted'} else None


def require_clean(root, slug):
    check(pending(root, slug) is None, 'dependency-recovery')


def write_bytes(path, data):
    path = app().safe(path); check(not path.is_symlink(), 'path')
    if path.exists(): read_bytes(path)
    temporary = path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp')
    fd = os.open(temporary, os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(fd, 'wb') as target:
            target.write(data); target.flush(); os.fsync(target.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists(): temporary.unlink()


def save_journal(journal):
    root=location(journal['project']); archive=app().safe(root/'receipts'); archive.mkdir(mode=0o700,exist_ok=True)
    app().save(root/'journal.json', journal)
    app().save(archive/(journal['operation_id']+'.json'),journal)


def workspace(journal):
    return location(journal['project'])/'jobs'/journal['operation_id']/'candidate'


def public_result(journal):
    return {k: journal[k] for k in ('project', 'operation_id', 'action', 'phase', 'before', 'after',
                                  'policy_hash', 'image', 'changed_files', 'error', 'duration_seconds', 'retained_files', 'request')}


def status(root, operation_id=None):
    a = app(); root, contract = a.target(root); slug = contract['project']['id']
    journal = load_journal(slug, root, operation_id)
    check(operation_id is None or journal is not None, 'conflict')
    result = {'project': slug, 'state': 'dependencies-ready' if journal and journal['phase'] == 'complete' else 'unprepared',
              'operation': public_result(journal) if journal else None}
    try:
        ctx = context(root); result.update(policy='valid', policy_hash=ctx['policy_hash'], files=ctx['hashes'])
        if journal and journal['phase']=='complete' and (journal['policy_hash']!=ctx['policy_hash'] or journal['after']!=ctx['hashes'] or not (root/'node_modules').is_dir()):
            result['state']='unprepared'
    except a.AppError as error:
        result.update(policy='invalid', error=error.code, state='error')
    s = a.state_for(slug)
    result['operation_busy'] = a.object_owned('container', s['name']+'-job', s['token']) if s else False
    if journal and journal['phase'] not in {'complete', 'aborted'}: result['state'] = 'recovery-required'
    return result


def stopped_state(root, contract):
    a = app(); s = a.reserve(root, contract)
    check(not a.object_owned('container', s['name']+'-job', s['token']), 'busy')
    active, _ = a.inspect_service(s, contract) if a.unit_path(s).exists() else (False, False)
    check(not active and not a.object_owned('container', s['name'], s['token']), 'busy')
    check(s['phase'] not in {'preparing', 'starting'} or s['unit_sha256'] == '0'*64, 'busy')
    return s


def invalidate(s, complete=False, operation_id=None):
    s.update(phase='stopped' if complete else 'failed', health_ready=False, operation='deps',
             operation_result='passed' if complete else 'unknown')
    if operation_id: s['operation_id'] = operation_id
    s.pop('prepared_digest', None); s.pop('build_digest', None)
    if complete: s.pop('error', None)
    else: s['error'] = 'dependency-recovery'
    app().save(app().STORE/(s['id']+'.json'), s)


def job(s, root, args):
    selected = {**s, 'root': str(app().safe(root))}
    return app().run_in_app(selected, ['pnpm', *args, *INSTALL_FLAGS], read_only_dependency_files='--frozen-lockfile' in args)


def verify_original(root, hashes):
    for name, expected in hashes.items():
        check(hashlib.sha256(read_bytes(root/name)).hexdigest() == expected, 'conflict')


def file_hash(path):
    app().safe(path)
    if not path.exists():
        check(not path.is_symlink(), 'path'); return None
    return hashlib.sha256(read_bytes(path)).hexdigest()


def captured_files(journal):
    return workspace(journal).parent/'captured'


def check_captured(journal):
    for name in FILES:
        value = file_hash(captured_files(journal)/name)
        check(value is None or value == journal['before'][name], 'conflict')


def publish_file(root, name, journal):
    source = root/name; captured = captured_files(journal)/name
    current = file_hash(source)
    if current == journal['after'][name]: return
    check(current is None or current == journal['before'][name], 'conflict')
    captured.parent.mkdir(mode=0o700, exist_ok=True)
    if current is not None:
        # Move the current inode aside; never replace a file created by an editor in this window.
        check(not captured.exists() and not captured.is_symlink(), 'conflict')
        os.rename(source, captured)
    captured_hash = file_hash(captured)
    if captured_hash != journal['before'][name]:
        if not source.exists() and captured_hash is not None:
            try:
                os.link(captured, source, follow_symlinks=False); captured.unlink()
            except FileExistsError: pass
        check(False, 'conflict')
    data = read_bytes(workspace(journal)/name)
    temporary = captured.parent/('publish-'+uuid.uuid4().hex)
    write_bytes(temporary, data)
    try:
        # Exclusive creation protects a concurrent editor's replacement. The original inode remains retained.
        try: os.link(temporary, source, follow_symlinks=False)
        except FileExistsError: raise app().AppError('conflict') from None
    finally:
        temporary.unlink()


def finish(root, s, journal):
    candidate = workspace(journal); check(context(candidate)['hashes'] == journal['after'], 'conflict')
    check(journal['policy_hash'] == policy()[1] and s['image'] == journal['image'], 'conflict')
    # A publishing crash may leave a mix of old/new files; only those exact states can resume.
    for name in FILES:
        current = file_hash(root/name)
        check(current in {journal['before'][name], journal['after'][name]} or
              current is None and file_hash(captured_files(journal)/name) == journal['before'][name], 'conflict')
    check_captured(journal)
    journal['phase'] = 'publishing'; save_journal(journal)
    for name in FILES: publish_file(root, name, journal)
    verify_original(root, journal['after'])
    journal['phase'] = 'repairing'; save_journal(journal)
    job(s, root, ['install', '--frozen-lockfile'])
    verify_original(root, journal['after'])
    context(root); check_captured(journal)
    invalidate(s, complete=True)
    journal.update(phase='complete', error=None); save_journal(journal)
    attempt_cleanup(journal)


def cleanup(journal):
    directory = workspace(journal).parent
    if directory.exists():
        app().safe(directory); check(directory.stat().st_uid == os.getuid() and directory.stat().st_mode & 0o077 == 0, 'path')
        check_captured(journal)
        marker = json_data(read_bytes(directory/'owner.json', 65536))
        check(marker == {'operation_id': journal['operation_id'], 'project': journal['project']}, 'conflict')
        # rmtree uses descriptor-based symlink protection; only this owned transaction is removed.
        check(shutil.rmtree.avoids_symlink_attacks, 'setup')
        shutil.rmtree(directory)


def attempt_cleanup(journal):
    try:
        cleanup(journal); journal['retained_files']=False
    except (app().AppError, OSError):
        journal['retained_files']=True
    save_journal(journal)


def operate(root, action, name=None, version=None, kind='runtime', operation_id=None, abort=False):
    a = app(); root, contract = a.target(root); slug = contract['project']['id']
    check(action in {'install', 'add', 'update', 'remove', 'recover'})
    check(kind in {'runtime', 'development'})
    if action in {'add', 'update', 'remove'}: package_name(name)
    if action in {'add', 'update'}: exact_version(version)
    else: check(version is None)
    if action == 'recover': check(isinstance(operation_id, str) and re.fullmatch(r'[0-9a-f]{32}', operation_id))
    else: check(operation_id is None and not abort)
    with a.locked(slug):
        s = stopped_state(root, contract)
        if action == 'recover':
            journal = load_journal(slug, root)
            check(journal is not None and journal['operation_id'] == operation_id, 'conflict')
            if journal['phase'] in {'complete', 'aborted'}:
                if journal['retained_files']:attempt_cleanup(journal)
                return {**public_result(journal), 'state': journal['phase'], 'changed': False}
            started = time.monotonic()
            try:
                if abort:
                    # Abandon without reverting user edits; a partial pair must first be reconciled.
                    context(root)
                    invalidate(s); s.update(phase='stopped', operation_result='failed'); s.pop('error',None)
                    a.save(a.STORE/(slug+'.json'),s)
                    journal.update(phase='aborted', error=None); save_journal(journal); attempt_cleanup(journal)
                elif journal['after']:
                    finish(root, s, journal)
                elif journal['action'] == 'install':
                    verify_original(root, journal['before']); context(root)
                    job(s, root, ['install', '--frozen-lockfile']); verify_original(root, journal['before'])
                    invalidate(s, complete=True); journal.update(after=journal['before'], phase='complete', error=None); save_journal(journal)
                else:
                    check(False, 'dependency-recovery')
            except (a.AppError, OSError) as failure:
                error = failure if isinstance(failure,a.AppError) else a.AppError('internal')
                journal.update(phase='unknown' if error.code == 'timeout' else 'conflict' if error.code == 'conflict' else 'failed', error=error.code)
                save_journal(journal); raise
            journal['duration_seconds'] = round(time.monotonic()-started, 3); save_journal(journal)
            return {**public_result(journal), 'state': journal['phase'], 'changed': bool(journal['changed_files'])}
        require_clean(root, slug)
        ctx = context(root)
        manifest = copy.deepcopy(ctx['manifest'])
        groups = [g for g in GROUPS if name in manifest.get(g, {})] if name else []
        if action == 'add': check(not groups)
        if action == 'update': check(len(groups) == 1)
        if action == 'remove' and not groups:
            return {'project': slug, 'state': 'complete', 'changed': False, 'changed_files': []}
        if action in {'add', 'update'}:
            group = groups[0] if groups else 'dependencies' if kind == 'runtime' else 'devDependencies'
            manifest.setdefault(group, {})[name] = version
        elif action == 'remove':
            for group in groups: del manifest[group][name]
        s['image'] = a.toolchain()
        journal = {'schema_version': 1, 'project': slug, 'root': str(root), 'operation_id': uuid.uuid4().hex,
                   'action': action, 'phase': 'resolving', 'before': ctx['hashes'], 'after': {},
                   'policy_hash': ctx['policy_hash'], 'image': s['image'], 'changed_files': [], 'error': None, 'duration_seconds': 0, 'retained_files': False,
                   'request': {'package':name,'version':version,'kind':('development' if group=='devDependencies' else 'optional' if group=='optionalDependencies' else 'runtime')} if action in {'add','update'} else {'package':name} if action=='remove' else {}}
        invalidate(s, operation_id=journal['operation_id'])
        directory = location(slug); directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        save_journal(journal); started = time.monotonic()
        try:
            if action == 'install':
                job(s, root, ['install', '--frozen-lockfile']); verify_original(root, ctx['hashes']); context(root)
                journal['after'] = ctx['hashes']; invalidate(s, complete=True); journal['phase'] = 'complete'
            else:
                candidate = workspace(journal); candidate.mkdir(parents=True, mode=0o700)
                candidate.parent.chmod(0o700)
                write_bytes(candidate.parent/'owner.json', json.dumps({'operation_id': journal['operation_id'], 'project': slug}).encode())
                original = candidate.parent/'original'; original.mkdir(mode=0o700)
                for file, data in ctx['files'].items():
                    write_bytes(candidate/file, data); write_bytes(original/file, data)
                write_bytes(candidate/'package.json', (json.dumps(manifest, indent=2)+'\n').encode())
                # Validate old lock sources without demanding coherence until candidate resolution completes.
                context(candidate, coherent=False)
                job(s, candidate, ['install', '--lockfile-only'])
                candidate_ctx = context(candidate)
                check(candidate_ctx['files']['pnpm-workspace.yaml'] == ctx['files']['pnpm-workspace.yaml'])
                job(s, candidate, ['install', '--frozen-lockfile'])
                check(context(candidate)['hashes'] == candidate_ctx['hashes'], 'conflict')
                verify_original(root, ctx['hashes'])
                journal.update(after=candidate_ctx['hashes'], phase='verified', changed_files=[f for f in FILES if ctx['hashes'][f] != candidate_ctx['hashes'][f]])
                save_journal(journal); finish(root, s, journal)
            journal.update(error=None, duration_seconds=round(time.monotonic()-started, 3)); save_journal(journal)
            return {**public_result(journal), 'state': 'complete', 'changed': bool(journal['changed_files'])}
        except (a.AppError, OSError) as error:
            code = error.code if isinstance(error, a.AppError) else 'internal'
            journal.update(phase='unknown' if code == 'timeout' else 'conflict' if code == 'conflict' else 'failed', error=code,
                           duration_seconds=round(time.monotonic()-started, 3))
            save_journal(journal)
            raise a.AppError(code) from None
