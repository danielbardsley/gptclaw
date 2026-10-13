"""Bundled exact template releases. Discovery never executes application code."""
import ctypes
import errno
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import uuid

import project_dependencies as deps
import project_toolchains as tools


def app():
    return deps.app()


def check(value):
    app().need(value, 'template-policy')


def data(path):
    try:
        return deps.json_data(deps.read_bytes(path, 262144))
    except app().AppError as error:
        if error.code == 'path': raise
        raise app().AppError('template-policy') from None


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def relative(value):
    check(isinstance(value, str) and 1 <= len(value) <= 200)
    path = PurePosixPath(value)
    check(bool(path.parts) and not path.is_absolute() and '..' not in path.parts and value == path.as_posix())
    check(re.fullmatch(r'[A-Za-z0-9._/-]+', value) and all(part not in {'.', '..'} for part in path.parts))
    return path


def catalogue():
    value = data(app().REPO/'config/templates/v1.json')
    schema = data(app().REPO/'schemas/templates/v1.schema.json')
    check(not list(deps.StrictValidator(schema).iter_errors(value)))
    extension_path = app().REPO/'config/templates/v2.json'
    has_extension = extension_path.exists() or extension_path.is_symlink()
    if has_extension:
        extension = data(extension_path)
        extension_schema = data(app().REPO/'schemas/templates/v2.schema.json')
        check(not list(deps.StrictValidator(extension_schema).iter_errors(extension)))
        value = {**value, 'schema_version': 2, 'releases': [*value['releases'], *extension['releases']]}
    group_path = app().REPO/'config/templates/v3.json'
    if group_path.exists() or group_path.is_symlink():
        extension = data(group_path)
        check(not list(deps.StrictValidator(data(app().REPO/'schemas/templates/v3.schema.json')).iter_errors(extension)))
        value = {**value, 'schema_version': 3, 'releases': [*value['releases'], *extension['releases']]}
    persistent_path = app().REPO/'config/templates/v4.json'
    if persistent_path.exists() or persistent_path.is_symlink():
        extension = data(persistent_path)
        check(not list(deps.StrictValidator(data(app().REPO/'schemas/templates/v4.schema.json')).iter_errors(extension)))
        value = {**value, 'schema_version': 4, 'releases': [*value['releases'], *extension['releases']]}
    mobile_path = app().REPO/'config/templates/v5.json'
    if mobile_path.exists() or mobile_path.is_symlink():
        extension = data(mobile_path)
        check(not list(deps.StrictValidator(data(app().REPO/'schemas/templates/v5.schema.json')).iter_errors(extension)))
        value = {**value, 'schema_version': 5, 'releases': [*value['releases'], *extension['releases']]}
    releases = {}
    _, profiles = tools.registry()
    for release in value['releases']:
        key = (release['id'], release['version']); check(key not in releases)
        check(release['digest'] == digest({k: v for k, v in release.items() if k != 'digest'}))
        for declaration in (release['toolchains'].values() if release['provider'] in {'notes-v1','notes-postgres-v1'} else [release['toolchain']]):
            declaration=tools.declaration(declaration)
            profile_key = (declaration['profile'], declaration['profile_version'])
            check(profile_key in profiles and profiles[profile_key]['versions'] == declaration['versions'])
        base = app().REPO/'templates/apps/releases'/key[0]/key[1]
        sources, outputs, total, contents = set(), set(), 0, {}
        for item in release['files']:
            source, output = str(relative(item['source'])), str(relative(item['output']))
            check(source not in sources and output not in outputs)
            check(output.split('/')[0] not in {'.gptclaw', '.gptclaw-cache', 'node_modules', '.git', '.env', '.npmrc', '.ssh', '.aws'})
            check(not any(part.startswith('.env.') or part in {'.npmrc','.ssh','.aws','.git','.gptclaw','node_modules','.gptclaw-cache'} for part in PurePosixPath(output).parts))
            check(not any(output.startswith(old+'/') or old.startswith(output+'/') for old in outputs))
            content = deps.read_bytes(base/source, 2*1024*1024)
            total += len(content); check(total <= 8*1024*1024)
            check(hashlib.sha256(content).hexdigest() == item['sha256'])
            sources.add(source); outputs.add(output); contents[output] = content
        if release['provider'] in {'notes-v1','notes-postgres-v1'}:
            check({'AGENTS.md','README.md','web/package.json','web/pnpm-lock.yaml','web/pnpm-workspace.yaml','api/pyproject.toml','api/uv.lock','api/.python-version','api/docs/python-standards.md','api/src/fastapi_app/main.py'} <= outputs)
            package=deps.json_data(contents['web/package.json'])
            check(package['packageManager']=='pnpm@'+release['toolchains']['web']['versions']['pnpm'])
            import project_python as py
            py.dependencies(py.toml(contents['api/pyproject.toml']))
            check(contents['api/.python-version'].decode().strip()==release['toolchains']['api']['versions']['python'])
            releases[key]=(release,contents);continue
        if release['provider'] == 'expo-v1':
            import project_mobile as mobile
            check({'package.json','pnpm-lock.yaml','pnpm-workspace.yaml','app.json','AGENTS.md','README.md','checks/quality.cjs','src/app/index.tsx','tests/counter.test.tsx'} <= outputs)
            mobile.validate_package(deps.json_data(contents['package.json']))
            check(release['mobile_profile_digest']==hashlib.sha256(json.dumps(mobile.profile(),sort_keys=True,separators=(',',':')).encode()).hexdigest())
            releases[key] = (release, contents); continue
        if release['provider'] == 'fastapi-v1':
            import project_python as py
            check({'pyproject.toml','uv.lock','.python-version','AGENTS.md','README.md','src/fastapi_app/main.py','scripts/quality.py','docs/python-standards.md','Containerfile','.pre-commit-config.yaml'} <= outputs)
            manifest = py.toml(contents['pyproject.toml']); py.dependencies(manifest)
            check(contents['.python-version'].decode().strip() == declaration['versions']['python'])
            releases[key] = (release, contents); continue
        check({'package.json','pnpm-lock.yaml','pnpm-workspace.yaml','AGENTS.md','README.md','app/api/health/route.ts'} <= outputs)
        package = deps.json_data(contents['package.json'])
        check(package.get('packageManager') == 'pnpm@'+declaration['versions']['pnpm'])
        engines = package.get('engines', {})
        check(isinstance(engines, dict) and set(engines) <= {'node', 'pnpm'})
        for name, constraint in engines.items():
            check(isinstance(constraint, str) and len(constraint) <= 200)
            check(tools.satisfies(declaration['versions'][name], constraint))
        releases[key] = (release, contents)
    default = value['default']; check((default['id'], default['version']) in releases)
    return value, releases


def resolve(template=None, version=None):
    check((template is None) == (version is None))
    value, releases = catalogue()
    key = (value['default']['id'], value['default']['version']) if template is None else (template, version)
    check(key in releases)
    return releases[key]


def discover(template=None, version=None):
    if template is not None or version is not None:
        release, _ = resolve(template, version)
        return {'schema_version': release['catalogue_schema'], 'release': release}
    value, _ = catalogue()
    return value


def provenance(release):
    return {'schema_version': 1, 'id': release['id'], 'version': release['version'], 'digest': release['digest']}


def validate_provenance(root):
    path = root/'.gptclaw/template-release.json'
    if not path.exists() and not path.is_symlink():
        check(app().read_json(root/'.gptclaw/template.json') == {'provider':'nextjs-v1'})
        return
    value = data(path)
    check(set(value) == {'schema_version', 'id', 'version', 'digest'} and type(value['schema_version']) is int and value['schema_version'] == 1)
    check(isinstance(value['id'], str) and isinstance(value['version'], str))
    release, _ = resolve(value['id'], value['version'])
    check(value == provenance(release))
    check(app().read_json(root/'.gptclaw/template.json') == {'provider':release['provider']})
    if release['provider']=='expo-v1':
        __import__('project_mobile').validate_policies(root,release)
    # Provenance is creation identity; subsequent supported toolchain switches
    # are independent and are validated by the toolchain contract.


def publish(stage, destination):
    """Linux atomic rename without replacing even an empty foreign directory."""
    libc = ctypes.CDLL(None, use_errno=True)
    rename = libc.renameat2
    rename.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
    rename.restype = ctypes.c_int
    if rename(-100, os.fsencode(stage), -100, os.fsencode(destination), 1):
        code = ctypes.get_errno()
        if code in (errno.EEXIST, errno.ENOTEMPTY): raise app().AppError('conflict')
        raise OSError(code, 'Template publication failed')


def generate(path, slug, release, contents):
    if release['provider']=='expo-v1':
        import project_mobile as mobile
        with app().locked('mobile-identity'):
            mobile.assert_identity_vacant(path,slug)
            return _generate(path,slug,release,contents)
    return _generate(path,slug,release,contents)


def _generate(path, slug, release, contents):
    expected={item['output']:item['sha256'] for item in release['files']}
    check(set(contents)==set(expected) and len(expected)==len(release['files']))
    check(all(isinstance(data,bytes) and hashlib.sha256(data).hexdigest()==expected[name] for name,data in contents.items()))
    parent_info = path.parent.stat()
    stage = path.parent/('.gptclaw-create-'+uuid.uuid4().hex)
    stage.mkdir(mode=0o700)
    try:
        for name, content in contents.items():
            output = stage/name; output.parent.mkdir(parents=True, exist_ok=True)
            with output.open('xb') as stream: stream.write(content)
        meta = stage/'.gptclaw'; meta.mkdir()
        contract = {'schema_version':1,'project':{'id':slug,'name':slug.replace('-',' ').title(),'kind':'web'},
            'commands':{'build':['pnpm','build'],'start':['pnpm','dev'],'test':['pnpm','test']},
            'service':{'internal_port':3000,'health':{'path':'/projects/'+slug+'/api/health/','timeout_seconds':5}},
            'exposure':{'private':True,'base_path':'/projects/'+slug+'/','funnel':False},'data':{'mode':'ephemeral'}}
        if release['provider'] == 'expo-v1':
            import project_mobile as mobile
            contract = mobile.contract(slug)
            config = deps.json_data(contents['app.json'])
            config['expo'].update(mobile.identities(slug))
            (stage/'app.json').write_text(json.dumps(config,indent=2)+'\n')
        if release['provider'] == 'fastapi-v1':
            import project_python as py
            contract = py.contract(slug)
        if release['provider'] in {'notes-v1','notes-postgres-v1'}:
            import project_groups as groups
            contract=groups.initialize(stage,slug,release)
        app().save(meta/'project.yaml', contract)
        app().save(meta/'template.json', {'provider':release['provider']})
        if release['provider'] not in {'notes-v1','notes-postgres-v1'}:app().save(meta/'toolchain.json', release['toolchain'])
        app().save(meta/'template-release.json', provenance(release))
        check(app().validate_project(stage)[2] == 0)
        if release['provider'] in {'notes-v1','notes-postgres-v1'}:
            for child,_ in groups.children(stage,contract).values():
                deps.context(child);tools.selection(child)
        else:
            deps.context(stage)
            tools.selection(stage)
        validate_provenance(stage)
        app().safe(path)
        current = path.parent.stat()
        app().need((current.st_dev,current.st_ino,current.st_uid) == (parent_info.st_dev,parent_info.st_ino,os.getuid()), 'path')
        publish(stage, path)
    except (app().AppError, OSError, ValueError) as error:
        # Keep interrupted staging for explicit review. No unknown paths are pruned.
        error.recovery_path = str(stage)
        raise
    return {'project':slug,'root':str(path),'state':'created','template':provenance(release)}


def bundle_paths():
    value, _ = catalogue()
    paths = [Path('scripts/project_templates.py'),Path('config/templates/v1.json'),Path('schemas/templates/v1.schema.json')]
    if (app().REPO/'config/templates/v2.json').exists():
        paths += [Path('config/templates/v2.json'), Path('schemas/templates/v2.schema.json')]
    if (app().REPO/'config/templates/v3.json').exists():
        paths += [Path('config/templates/v3.json'),Path('schemas/templates/v3.schema.json')]
    if (app().REPO/'config/templates/v4.json').exists():
        paths += [Path('config/templates/v4.json'),Path('schemas/templates/v4.schema.json')]
    if (app().REPO/'config/templates/v4.json').exists():
        paths += [Path('config/templates/v4.json'),Path('schemas/templates/v4.schema.json')]
    if (app().REPO/'config/templates/v5.json').exists():
        paths += [Path('config/templates/v5.json'),Path('schemas/templates/v5.schema.json')]
    for release in value['releases']:
        base = Path('templates/apps/releases')/release['id']/release['version']
        paths += [base/item['source'] for item in release['files']]
    return paths
