"""Reviewed Python/uv contracts; project metadata is data, never host code."""
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import time
import tomllib
import urllib.parse
import uuid

import project_dependencies as deps

FILES = ('pyproject.toml', 'uv.lock', '.python-version')
GUARD_ENV = {
    'UV_PYTHON_DOWNLOADS': 'never', 'UV_NO_CONFIG': '1',
    'UV_KEYRING_PROVIDER': 'disabled', 'UV_NO_ENV_FILE': '1',
    'UV_PYTHON': '/usr/local/bin/python', 'UV_PROJECT_ENVIRONMENT': '/workspace/.venv',
    'UV_CACHE_DIR': '/workspace/.gptclaw-cache/uv', 'PYTHONDONTWRITEBYTECODE': '1',
    'PYTHONPATH': '/workspace/src',
}
FLAGS = ['--no-config', '--no-python-downloads', '--no-managed-python', '--no-build',
         '--keyring-provider=disabled', '--default-index=https://pypi.org/simple']
VERIFY = "import json,platform,subprocess;print(json.dumps({'python':platform.python_version(),'uv':subprocess.check_output(['uv','--version'],text=True).split()[1]}))"


def app():
    return deps.app()


def is_python(root):
    marker = Path(root)/'.gptclaw/template.json'
    if marker.exists() or marker.is_symlink():
        return app().read_json(marker) == {'provider': 'fastapi-v1'}
    # Owned transaction workspaces contain these exact dependency files, no provider marker.
    return (Path(root)/'pyproject.toml').exists() and not (Path(root)/'package.json').exists()


def files_for(root):
    return FILES if is_python(root) else deps.FILES


def declaration(value):
    schema = deps.json_data(deps.read_bytes(app().REPO/'schemas/toolchains/v2.schema.json', 65536))
    deps.check(not list(deps.StrictValidator(schema).iter_errors(value)), 'toolchain-policy')
    return value


def registry():
    value = deps.json_data(deps.read_bytes(app().REPO/'config/toolchains/v2.json', 65536))
    deps.check(set(value) == {'schema_version', 'default', 'profiles'} and type(value['schema_version']) is int and value['schema_version'] == 2, 'toolchain-policy')
    profiles = {}
    deps.check(isinstance(value['profiles'], list) and 1 <= len(value['profiles']) <= 100, 'toolchain-policy')
    for p in value['profiles']:
        deps.check(set(p) == {'profile', 'profile_version', 'versions', 'platform', 'base_image', 'uv_image'}, 'toolchain-policy')
        declaration({'schema_version': 2, **{k: p[k] for k in ('profile', 'profile_version', 'versions')}})
        deps.check(p['platform'] == {'os': 'linux', 'architecture': 'amd64'}, 'toolchain-policy')
        for field, prefix in [('base_image', 'docker.io/library/python@sha256:'), ('uv_image', 'ghcr.io/astral-sh/uv@sha256:')]:
            deps.check(isinstance(p[field], str) and re.fullmatch(re.escape(prefix)+r'[0-9a-f]{64}', p[field]), 'toolchain-policy')
        key = (p['profile'], p['profile_version']); deps.check(key not in profiles, 'toolchain-policy'); profiles[key] = p
    ref = value['default']
    deps.check(set(ref) == {'profile', 'profile_version'} and type(ref['profile_version']) is int and (ref['profile'], ref['profile_version']) in profiles, 'toolchain-policy')
    return value, profiles


def recipe_for(p):
    return (f"FROM {p['uv_image']} AS uv\nFROM {p['base_image']}\n"
            "COPY --from=uv /uv /usr/local/bin/uv\n"
            "ENV UV_PYTHON_DOWNLOADS=never UV_NO_CONFIG=1 UV_KEYRING_PROVIDER=disabled UV_NO_ENV_FILE=1 PYTHONDONTWRITEBYTECODE=1\n"
            "WORKDIR /workspace\n").encode()


def toml(data):
    try:
        value = tomllib.loads(data.decode('utf-8'))
        def bounded(item, depth=0):
            deps.check(depth <= 16)
            if isinstance(item, dict):
                for child in item.values(): bounded(child, depth+1)
            elif isinstance(item, list):
                deps.check(len(item) <= 10000)
                for child in item: bounded(child, depth+1)
        bounded(value)
        return value
    except (ValueError, UnicodeError, RecursionError):
        raise app().AppError('dependency-policy') from None


def policy():
    value = deps.json_data(deps.read_bytes(app().REPO/'config/project-dependencies/v2.json', 65536))
    expected = {'schema_version': 2, 'manager': 'uv', 'manager_version': '0.13.0', 'index': 'https://pypi.org/simple', 'artifact_origin': 'https://files.pythonhosted.org', 'groups': ['dev', 'test'], 'source_builds': False, 'python_downloads': False}
    deps.check(value == expected and type(value['schema_version']) is int and value['source_builds'] is False and value['python_downloads'] is False)
    return value, hashlib.sha256(json.dumps({'policy': value, 'env': GUARD_ENV, 'flags': FLAGS}, sort_keys=True).encode()).hexdigest()


def dependencies(manifest):
    project = manifest.get('project', {})
    deps.check(isinstance(project, dict) and set(project) <= {'name', 'version', 'description', 'requires-python', 'dependencies'})
    deps.check(isinstance(project.get('name'), str) and re.fullmatch(r'[a-z][a-z0-9-]{0,63}', project['name']))
    deps.check(set(manifest) <= {'project', 'dependency-groups', 'tool'})
    deps.check(not (set(manifest.get('tool', {})) - {'black', 'isort', 'ruff', 'mypy', 'pytest', 'coverage', 'bandit'}))
    groups = manifest.get('dependency-groups', {})
    deps.check(isinstance(groups, dict) and set(groups) <= {'dev', 'test'})
    result = {}; seen = set()
    for group, items in {'runtime': project.get('dependencies', []), **groups}.items():
        deps.check(isinstance(items, list) and len(items) <= 200)
        pairs = {}
        for item in items:
            deps.check(isinstance(item, str) and len(item) <= 200)
            match = re.fullmatch(r'([a-z0-9]+(?:-[a-z0-9]+)*)==([0-9]+(?:\.[0-9]+){1,3})', item)
            deps.check(match is not None)
            name, version = match.groups(); deps.check(name not in seen); seen.add(name); pairs[name] = version
        result[group] = pairs
    return result


def context(root, coherent=True):
    from project_worktrees import guard
    guard(root)
    root = app().safe(Path(root)); p, digest = policy()
    for item in root.iterdir():
        deps.check(not (item.name.startswith('.env') or item.name in {'.ssh', '.aws', '.netrc', '.pypirc', 'uv.toml', 'pip.conf', '.tool-versions', 'mise.toml', '.mise.toml', 'package.json'}))
    blobs = {name: deps.read_bytes(root/name, 2*1024*1024 if name == 'uv.lock' else 65536) for name in FILES}
    manifest = toml(blobs['pyproject.toml']); groups = dependencies(manifest)
    interpreter = blobs['.python-version'].decode().strip()
    deps.check(re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', interpreter))
    deps.check(manifest['project'].get('requires-python') == '=='+'.'.join(interpreter.split('.')[:2])+'.*')
    lock = toml(blobs['uv.lock'])
    deps.check(set(lock) <= {'version', 'revision', 'requires-python', 'resolution-markers', 'supported-markers', 'options', 'manifest', 'package'})
    deps.check(type(lock.get('version')) is int and lock['version'] == 1)
    deps.check(not lock.get('options') and not lock.get('manifest'))
    deps.check(isinstance(lock.get('package'), list) and 1 <= len(lock['package']) <= 1000)
    own = None; seen = set()
    for package in lock['package']:
        deps.check(isinstance(package, dict) and set(package) <= {'name', 'version', 'source', 'dependencies', 'dev-dependencies', 'optional-dependencies', 'sdist', 'wheels', 'metadata', 'resolution-markers'})
        name = package.get('name'); version = package.get('version')
        deps.check(isinstance(name, str) and len(name)<=100 and re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name))
        deps.check(isinstance(version, str) and len(version)<=64 and re.fullmatch(r'[0-9]+(?:\.[0-9]+){1,3}', version))
        source = package.get('source')
        if source == {'virtual': '.'}:
            deps.check(own is None and name == manifest['project']['name']); own = package
            continue
        deps.check(source == {'registry': p['index']})
        key = (name, version); deps.check(key not in seen); seen.add(key)
        wheels = package.get('wheels', []); deps.check(isinstance(wheels, list) and bool(wheels))
        for artifact in [*wheels, *([package['sdist']] if 'sdist' in package else [])]:
            deps.check(isinstance(artifact, dict) and set(artifact) <= {'url', 'hash', 'size', 'upload-time'})
            url = urllib.parse.urlsplit(artifact.get('url', ''))
            deps.check(url.scheme == 'https' and url.netloc == 'files.pythonhosted.org' and not url.query and not url.fragment)
            deps.check(re.fullmatch(r'sha256:[0-9a-f]{64}', artifact.get('hash', '')))
        # Dependency edges may carry markers/extra selection, never alternate origins.
        for edges in [package.get('dependencies', []), *package.get('optional-dependencies', {}).values(), *package.get('dev-dependencies', {}).values()]:
            deps.check(isinstance(edges, list))
            for edge in edges:
                deps.check(isinstance(edge, dict) and set(edge) <= {'name', 'version', 'source', 'marker', 'extra'})
                if 'source' in edge: deps.check(edge['source'] == {'registry': p['index']})
    deps.check(own is not None)
    if coherent:
        deps.check(lock.get('requires-python') == manifest['project']['requires-python'])
        metadata = own.get('metadata', {})
        def pairs(items):
            deps.check(isinstance(items, list))
            result = {}
            for item in items:
                deps.check(set(item) == {'name', 'specifier'} and isinstance(item['specifier'], str) and item['specifier'].startswith('=='))
                deps.check(item['name'] not in result); result[item['name']] = item['specifier'][2:]
            return result
        deps.check(pairs(metadata.get('requires-dist', [])) == groups['runtime'])
        requires_dev = metadata.get('requires-dev', {})
        deps.check(set(requires_dev) == set(groups)-{'runtime'})
        for group in requires_dev: deps.check(pairs(requires_dev[group]) == groups[group])
    return {'policy': p, 'policy_hash': digest, 'files': blobs, 'manifest': manifest, 'groups': groups, 'hashes': {k: hashlib.sha256(v).hexdigest() for k,v in blobs.items()}}


def selection(root, package=None):
    import project_toolchains as tools
    root = app().safe(Path(root))
    value = declaration(tools.data(root/'.gptclaw/toolchain.json'))
    _, profiles = registry(); key = (value['profile'], value['profile_version'])
    deps.check(key in profiles and value['versions'] == profiles[key]['versions'], 'toolchain-policy')
    manifest = package if package is not None else toml(deps.read_bytes(root/'pyproject.toml', 65536))
    dependencies(manifest)
    deps.check(deps.read_bytes(root/'.python-version', 128).decode().strip() == value['versions']['python'], 'toolchain-policy')
    deps.check(manifest['project'].get('requires-python') == '=='+'.'.join(value['versions']['python'].split('.')[:2])+'.*', 'toolchain-policy')
    deps.check(policy()[0]['manager_version'] == value['versions']['uv'], 'toolchain-policy')
    profile = profiles[key]; recipe = recipe_for(profile); recipe_hash = hashlib.sha256(recipe).hexdigest()
    return {'declaration': value, 'legacy': False, 'profile': profile, 'profile_hash': tools.digest(profile), 'recipe_hash': recipe_hash, 'selection_hash': tools.digest({'profile': profile, 'recipe_hash': recipe_hash}), 'engines': {}}


def uv_job(s, root, args, readonly=False):
    return app().run_in_app({**s, 'root': str(root), 'adapter': 'python'}, ['uv', *args, *FLAGS], read_only_dependency_files=readonly)


def install(s, root):
    return uv_job(s, root, ['sync', '--locked', '--all-groups', '--no-install-project'], True)


def operate(root, action, name=None, version=None, kind='runtime', operation_id=None, abort=False):
    a = app(); root, contract = a.target(root); slug = contract['project']['id']
    deps.check(action in {'install', 'add', 'update', 'remove', 'recover'} and kind in {'runtime', 'development', 'test'})
    if action in {'add','update','remove'}: deps.check(isinstance(name, str) and len(name)<=100 and re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name))
    else: deps.check(name is None)
    if action in {'add', 'update'}: deps.check(isinstance(version, str) and len(version)<=64 and re.fullmatch(r'[0-9]+(?:\.[0-9]+){1,3}', version))
    else: deps.check(version is None)
    if action == 'recover': deps.check(isinstance(operation_id, str) and re.fullmatch(r'[0-9a-f]{32}', operation_id))
    else: deps.check(operation_id is None and not abort)
    with a.locked(slug):
        s = deps.stopped_state(root, contract)
        if action == 'recover':
            journal = deps.load_journal(slug, root)
            deps.check(journal is not None and journal['operation_id'] == operation_id, 'conflict')
            if journal['phase'] in {'complete', 'aborted'}:
                if journal['retained_files']: deps.attempt_cleanup(journal)
                return {**deps.public_result(journal), 'state': journal['phase'], 'changed': False}
            if not abort:
                original = deps.read_bytes(deps.workspace(journal).parent/'original/pyproject.toml', 65536) if journal['after'] and journal['action'] != 'install' else deps.read_bytes(root/'pyproject.toml',65536)
                if journal['after'] and journal['action'] != 'install': deps.check(hashlib.sha256(original).hexdigest() == journal['before']['pyproject.toml'], 'conflict')
                selected = selection(root, toml(original))
                deps.check(s.get('toolchain_hash') == selected['selection_hash'] and a.toolchain(root, selected) == journal['image'], 'conflict')
            started = time.monotonic()
            try:
                if abort:
                    context(root); deps.invalidate(s); s.update(phase='stopped', operation_result='failed'); s.pop('error',None)
                    a.save(a.STORE/(slug+'.json'),s); journal.update(phase='aborted',error=None); deps.save_journal(journal); deps.attempt_cleanup(journal)
                elif journal['after']: deps.finish(root,s,journal)
                elif journal['action']=='install':
                    deps.verify_original(root,journal['before']); context(root); install(s,root); deps.verify_original(root,journal['before'])
                    deps.invalidate(s,complete=True); journal.update(after=journal['before'],phase='complete',error=None); deps.save_journal(journal)
                else: deps.check(False,'dependency-recovery')
            except (a.AppError,OSError) as error:
                fail(journal,error,started); raise
            journal['duration_seconds']=round(time.monotonic()-started,3);deps.save_journal(journal)
            return {**deps.public_result(journal),'state':journal['phase'],'changed':bool(journal['changed_files'])}
        deps.require_clean(root,slug); ctx=context(root)
        groups=[g for g,v in ctx['groups'].items() if name in v] if name else []
        if action=='add': deps.check(not groups and name is not None)
        if action=='update': deps.check(len(groups)==1)
        if action=='remove' and not groups: return {'project':slug,'state':'complete','changed':False,'changed_files':[]}
        group=groups[0] if groups else {'runtime':'runtime','development':'dev','test':'test'}[kind]
        selected=selection(root); s.update(image=a.toolchain(root),toolchain_hash=selected['selection_hash'])
        journal={'schema_version':2,'project':slug,'root':str(root),'operation_id':uuid.uuid4().hex,'action':action,'phase':'resolving','before':ctx['hashes'],'after':{},'policy_hash':ctx['policy_hash'],'image':s['image'],'changed_files':[],'error':None,'duration_seconds':0,'retained_files':False,'request':{'package':name,'version':version,'kind':kind} if action in {'add','update'} else {'package':name} if action=='remove' else {}}
        deps.invalidate(s,operation_id=journal['operation_id']); deps.location(slug).mkdir(parents=True,exist_ok=True,mode=0o700);deps.save_journal(journal);started=time.monotonic()
        try:
            if action=='install':
                install(s,root);deps.verify_original(root,ctx['hashes']);context(root);journal['after']=ctx['hashes'];deps.invalidate(s,complete=True);journal['phase']='complete'
            else:
                candidate=deps.workspace(journal);candidate.mkdir(parents=True,mode=0o700);candidate.parent.chmod(0o700)
                deps.write_bytes(candidate.parent/'owner.json',json.dumps({'operation_id':journal['operation_id'],'project':slug}).encode())
                original=candidate.parent/'original';original.mkdir(mode=0o700)
                for file,data in ctx['files'].items():deps.write_bytes(candidate/file,data);deps.write_bytes(original/file,data)
                args=['remove',name,'--no-sync'] if action=='remove' else ['add',name+'=='+version,'--no-sync','--raw']
                if group!='runtime':args+=['--group',group]
                uv_job(s,candidate,args)
                after=context(candidate); expected=copy.deepcopy(ctx['groups'])
                if action=='remove':del expected[group][name]
                else:expected.setdefault(group,{})[name]=version
                deps.check(after['groups']==expected,'conflict')
                old=copy.deepcopy(ctx['manifest']);new=copy.deepcopy(after['manifest'])
                for item in (old,new):item['project'].pop('dependencies',None);item.pop('dependency-groups',None)
                deps.check(old==new and after['files']['.python-version']==ctx['files']['.python-version'],'conflict')
                install(s,candidate);deps.verify_original(candidate,after['hashes']);deps.verify_original(root,ctx['hashes'])
                journal.update(after=after['hashes'],phase='verified',changed_files=[f for f in FILES if ctx['hashes'][f]!=after['hashes'][f]])
                deps.save_journal(journal);deps.finish(root,s,journal)
            journal.update(error=None,duration_seconds=round(time.monotonic()-started,3));deps.save_journal(journal)
            return {**deps.public_result(journal),'state':'complete','changed':bool(journal['changed_files'])}
        except (a.AppError,OSError) as error:
            fail(journal,error,started);raise


def fail(journal,error,started):
    code=error.code if isinstance(error,app().AppError) else 'internal'
    journal.update(phase='unknown' if code=='timeout' else 'conflict' if code=='conflict' else 'failed',error=code,duration_seconds=round(time.monotonic()-started,3));deps.save_journal(journal)


def contract(slug):
    python='/workspace/.venv/bin/python'
    return {'schema_version':2,'project':{'id':slug,'name':slug.replace('-',' ').title(),'kind':'api'},'commands':{**{action:[python,'scripts/quality.py',action] for action in ['build','test','format','lint','typecheck','security','verify']},'start':[python,'-m','uvicorn','fastapi_app.main:create_app','--factory','--app-dir','src','--reload','--reload-dir','src','--host','0.0.0.0','--port','8000','--no-access-log','--no-proxy-headers']},'service':{'internal_port':8000,'health':{'path':'/projects/'+slug+'/ready','timeout_seconds':5}},'exposure':{'private':True,'base_path':'/projects/'+slug+'/','funnel':False},'data':{'mode':'ephemeral'}}
