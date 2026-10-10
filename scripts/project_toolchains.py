"""Reviewed exact container toolchains; project metadata never supplies commands."""
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import time
import uuid

import project_dependencies as deps

LABEL = 'com.gptclaw.toolchain-profile'
IMAGE_RE = r'sha256:[0-9a-f]{64}'
HASH_RE = r'[0-9a-f]{64}'
ENGINE_RE = r'[0-9.*+^~<>=| -]+'
VERIFY_JS = """const fs=require('node:fs'),cp=require('node:child_process');
const actual={node:process.versions.node,pnpm:cp.execFileSync('pnpm',['--version'],{encoding:'utf8',timeout:10000}).trim()};
const marker=JSON.parse(fs.readFileSync('/usr/local/share/gptclaw-toolchain.json','utf8'));
const engines=JSON.parse(process.argv[1]);
const semver=require('/usr/local/lib/node_modules/npm/node_modules/semver');
for(const [name,range] of Object.entries(engines)) if(!semver.satisfies(actual[name],range)) throw Error('Engine constraint mismatch');
console.log(JSON.stringify({versions:actual,artifact_integrity:marker.artifact_integrity,installed_versions:marker.versions}));"""


def app():
    return deps.app()


def check(value, code='toolchain-policy'):
    app().need(value, code)


def data(path):
    try:
        return deps.json_data(deps.read_bytes(path, 65536))
    except app().AppError as error:
        if error.code == 'path': raise
        raise app().AppError('toolchain-policy') from None


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def declaration(value):
    schema = data(app().REPO/'schemas/toolchains/v1.schema.json')
    check(not list(deps.StrictValidator(schema).iter_errors(value)))
    return value


def registry():
    value = data(app().REPO/'config/toolchains/v1.json')
    check(set(value) == {'schema_version', 'default', 'legacy', 'profiles'})
    check(type(value['schema_version']) is int and value['schema_version'] == 1)
    check(isinstance(value['profiles'], list) and 1 <= len(value['profiles']) <= 100)
    profiles = {}
    for item in value['profiles']:
        check(isinstance(item, dict) and set(item) == {'profile', 'profile_version', 'versions', 'platform', 'base_image', 'pnpm_artifact', 'installer_sha256'})
        declaration({k: item[k] for k in ('profile', 'profile_version', 'versions')} | {'schema_version': 1})
        check(item['platform'] == {'os': 'linux', 'architecture': 'amd64'})
        check(isinstance(item['base_image'], str) and re.fullmatch(r'docker.io/library/node@sha256:[0-9a-f]{64}', item['base_image']))
        artifact = item['pnpm_artifact']
        check(isinstance(artifact, dict) and set(artifact) == {'url', 'integrity'})
        check(artifact['url'] == 'https://registry.npmjs.org/pnpm/-/pnpm-'+item['versions']['pnpm']+'.tgz')
        check(isinstance(artifact['integrity'], str) and re.fullmatch(r'sha512-[A-Za-z0-9+/]{86}==', artifact['integrity']))
        check(isinstance(item['installer_sha256'], str) and re.fullmatch(HASH_RE, item['installer_sha256']))
        installer = deps.read_bytes(app().REPO/'templates/apps/node-toolchain/install-pnpm.cjs', 65536)
        check(hashlib.sha256(installer).hexdigest() == item['installer_sha256'])
        key = (item['profile'], item['profile_version']); check(key not in profiles); profiles[key] = item
    for key in ('default', 'legacy'):
        ref = value[key]
        check(isinstance(ref, dict) and set(ref) == {'profile', 'profile_version'})
        check(isinstance(ref['profile'], str) and type(ref['profile_version']) is int)
        check((ref['profile'], ref['profile_version']) in profiles)
    return value, profiles


def default_declaration():
    r, profiles = registry(); p = profiles[(r['default']['profile'], r['default']['profile_version'])]
    return {'schema_version': 1, **r['default'], 'versions': p['versions']}


def satisfies(version, constraint):
    """Finite stable-version range grammar; unsupported syntax is refused offline."""
    actual = tuple(map(int, version.split('.')))
    alternatives = []
    for alternative in constraint.split('||'):
        alternative = alternative.strip(); check(bool(alternative))
        hyphen = re.fullmatch(r'(\d+\.\d+\.\d+) - (\d+\.\d+\.\d+)', alternative)
        if hyphen:
            alternatives.append(tuple(map(int, hyphen[1].split('.'))) <= actual <= tuple(map(int, hyphen[2].split('.'))))
            continue
        tokens = alternative.split(); match_all = True
        for token in tokens:
            match = re.fullmatch(r'(>=|<=|>|<|=|\^|~)?(\d+|\*)(?:\.(\d+|\*))?(?:\.(\d+|\*))?', token)
            check(match is not None)
            op = match[1] or '='; parts = [match[2], match[3], match[4]]
            first_open = next((i for i, part in enumerate(parts) if part in (None, '*')), 3)
            check(all(part in (None, '*') for part in parts[first_open:]))
            check(all(part in (None, '*', '0') or not part.startswith('0') for part in parts))
            lower = tuple(int(part) if part not in (None, '*') else 0 for part in parts)
            if first_open == 0:
                check(op == '='); good = True
            elif op in {'^', '~'}:
                pivot = min(0 if lower[0] else 1 if lower[1] else 2, first_open-1) if op == '^' else (0 if first_open == 1 else 1)
                upper = tuple(lower[i]+1 if i == pivot else lower[i] if i < pivot else 0 for i in range(3))
                good = lower <= actual < upper
            elif op == '=' and first_open < 3:
                good = actual[:first_open] == lower[:first_open]
            else:
                upper = tuple(lower[i]+1 if i == first_open-1 else lower[i] if i < first_open-1 else 0 for i in range(3))
                good = {'=': actual == lower, '>': actual > lower if first_open == 3 else actual >= upper,
                        '<': actual < lower, '>=': actual >= lower,
                        '<=': actual <= lower if first_open == 3 else actual < upper}[op]
            match_all = match_all and good
        alternatives.append(match_all)
    return any(alternatives)


def selection(root, package=None):
    root = app().safe(Path(root)); r, profiles = registry()
    path = root/'.gptclaw/toolchain.json'
    legacy = not path.exists() and not path.is_symlink()
    if legacy:
        # Only the reviewed SPEC-018 template may use legacy mapping.
        check(app().read_json(root/'.gptclaw/template.json') == {'provider': 'nextjs-v1'})
        ref = r['legacy']
        value = {'schema_version': 1, **ref, 'versions': profiles[(ref['profile'], ref['profile_version'])]['versions']}
    else:
        value = declaration(data(path))
    key = (value['profile'], value['profile_version']); check(key in profiles)
    p = profiles[key]; check(value['versions'] == p['versions'])
    package = data(root/'package.json') if package is None else package
    check(package.get('packageManager') == 'pnpm@'+p['versions']['pnpm'])
    check(not any(k in package for k in ('devEngines', 'pnpm', 'runtimeDependencies', 'packageManagerDependencies')))
    engines = package.get('engines', {})
    check(isinstance(engines, dict) and set(engines) <= {'node', 'pnpm'})
    for name, constraint in engines.items():
        check(isinstance(constraint, str) and len(constraint) <= 200 and re.fullmatch(ENGINE_RE, constraint))
        # Supported ranges are checked offline and again against actual executables.
        check(satisfies(p['versions'][name], constraint))
    for name in ('.node-version', '.nvmrc'):
        path = root/name
        if path.exists() or path.is_symlink():
            try: version = deps.read_bytes(path, 128).decode().strip()
            except UnicodeError: raise app().AppError('toolchain-policy') from None
            check(version == p['versions']['node'])
    # Other version managers and runtime-selection hooks are unsupported metadata.
    for name in ('.tool-versions', '.mise.toml', 'mise.toml', '.node-version.json'):
        check(not (root/name).exists() and not (root/name).is_symlink())
    p, policy_hash = deps.policy(); check(value['versions']['pnpm'] == p['manager_version'])
    profile = profiles[key]
    profile_hash = digest(profile)
    recipe = recipe_for(profile)
    selection_hash = digest({'profile_hash': profile_hash, 'recipe_hash': hashlib.sha256(recipe).hexdigest(), 'engines': engines})
    return {'declaration': {'schema_version': 1, 'profile': key[0], 'profile_version': key[1], 'versions': profile['versions']},
            'legacy': legacy, 'profile': profile, 'profile_hash': profile_hash,
            'recipe_hash': hashlib.sha256(recipe).hexdigest(), 'selection_hash': selection_hash, 'engines': engines}


def recipe_for(profile):
    return (f"FROM {profile['base_image']}\n"
            "COPY install-pnpm.cjs profile.json /tmp/\n"
            "RUN node /tmp/install-pnpm.cjs && rm /tmp/install-pnpm.cjs /tmp/profile.json\n"
            "ENV NEXT_TELEMETRY_DISABLED=1 PNPM_HOME=/tmp/pnpm XDG_CACHE_HOME=/tmp/pnpm-cache XDG_CONFIG_HOME=/tmp/pnpm-config XDG_STATE_HOME=/tmp/pnpm-state\n"
            "WORKDIR /workspace\n").encode()


def supported():
    check(platform.system() == 'Linux' and platform.machine() in {'x86_64', 'amd64'}, 'toolchain-platform')


def location(selected):
    return app().STORE/'toolchains'/selected['profile_hash']


def tag_for(selected):
    # Scope the tag to this owned provider store, including isolated acceptance stores.
    namespace = hashlib.sha256(str(app().STORE).encode()).hexdigest()[:12]
    return 'localhost/gptclaw-toolchain:'+namespace+'-'+selected['profile_hash']


def record(selected):
    path = location(selected)/'receipt.json'
    if not path.exists():
        check(not path.is_symlink(), 'path'); return None
    value = data(path)
    keys = {'schema_version', 'profile_hash', 'recipe_hash', 'profile', 'operation_id', 'phase', 'image', 'versions', 'error', 'duration_seconds'}
    check(isinstance(value, dict) and set(value) == keys, 'conflict')
    check(type(value['schema_version']) is int and value['schema_version'] == 1, 'conflict')
    check(value['profile_hash'] == selected['profile_hash'] and value['recipe_hash'] == selected['recipe_hash'] and value['profile'] == selected['profile'], 'conflict')
    check(isinstance(value['operation_id'], str) and re.fullmatch(r'[0-9a-f]{32}', value['operation_id']), 'conflict')
    check(value['phase'] in {'acquiring', 'verified', 'failed', 'unknown'}, 'conflict')
    check(value['image'] is None or isinstance(value['image'], str) and re.fullmatch(IMAGE_RE, value['image']), 'conflict')
    check(value['versions'] is None or value['versions'] == selected['profile']['versions'], 'conflict')
    check(value['phase'] != 'verified' or value['image'] is not None and value['versions'] is not None, 'conflict')
    check(value['error'] is None or value['error'] in app().MESSAGES, 'conflict')
    check(type(value['duration_seconds']) in (int, float) and 0 <= value['duration_seconds'] <= 86400, 'conflict')
    return value


def image_info(selected):
    a = app(); tag = tag_for(selected)
    result = a.command(['podman', 'image', 'exists', tag], optional=True)
    check(result.returncode in (0, 1), 'command')
    if result.returncode == 1: return None
    info = a.json_command(['podman', 'image', 'inspect', tag])[0]
    check(info.get('Labels', {}).get(LABEL) == selected['profile_hash'], 'conflict')
    check(info.get('Os') == 'linux' and info.get('Architecture') == 'amd64', 'toolchain-platform')
    image = info.get('Id', '')
    if not image.startswith('sha256:'): image = 'sha256:'+image
    check(re.fullmatch(IMAGE_RE, image), 'conflict')
    return image


def observed(selected):
    supported(); receipt = record(selected); image = image_info(selected) if receipt else None
    if receipt and receipt['phase'] == 'verified' and image is not None: check(image == receipt['image'], 'conflict')
    return {'selection': selected['declaration'], 'legacy': selected['legacy'],
            'profile_hash': selected['profile_hash'], 'selection_hash': selected['selection_hash'],
            'state': 'verified' if receipt and receipt['phase'] == 'verified' and image else 'recovery-required' if receipt and receipt['phase'] in {'unknown', 'acquiring'} else 'unprepared',
            'receipt': receipt, 'image_present': image is not None}


def verify(selected, image, operation_id):
    a = app(); namespace = hashlib.sha256(str(a.STORE).encode()).hexdigest()[:12]
    name = 'gptclaw-toolchain-'+namespace+'-'+selected['profile_hash'][:24]+'-verify'
    exists = a.command(['podman', 'container', 'exists', name], optional=True)
    check(exists.returncode == 1, 'busy' if exists.returncode == 0 else 'command')
    result = a.command(['podman', 'run', '--rm', '--name', name, '--label', LABEL+'='+selected['profile_hash'],
                        '--network=none', '--read-only', '--tmpfs', '/tmp:rw,size=64m',
                        '--user', '1002:1002', '--memory='+a.MEMORY, '--cpus='+a.CPU,
                        '--pids-limit='+str(a.PIDS), '--cap-drop=all', '--security-opt=no-new-privileges',
                        '--env', 'pnpm_config_pm_on_fail=error', '--env', 'pnpm_config_runtime=false',
                        image, 'node', '-e', VERIFY_JS, json.dumps(selected['engines'])], timeout=30, optional=True)
    check(result.returncode == 0, 'toolchain-verification')
    try: actual = json.loads(result.stdout)
    except ValueError: raise a.AppError('toolchain-verification') from None
    check(actual == {'versions': selected['profile']['versions'], 'installed_versions': selected['profile']['versions'],
                     'artifact_integrity': selected['profile']['pnpm_artifact']['integrity']}, 'toolchain-verification')


def acquire(selected):
    a = app(); supported(); started = time.monotonic()
    with a.locked('toolchain-'+selected['profile_hash']):
        receipt = record(selected)
        check(not receipt or receipt['phase'] not in {'acquiring', 'unknown'}, 'toolchain-recovery')
        image = image_info(selected)
        if image is not None:
            check(receipt and receipt['phase'] == 'verified' and receipt['image'] == image, 'conflict')
            # Actual executables and current engine constraints are checked on each prepare/reuse.
            try:
                verify(selected, image, receipt['operation_id'])
            except a.AppError as error:
                receipt.update(phase='unknown' if error.code == 'timeout' else 'failed', error=error.code)
                a.save(location(selected)/'receipt.json', receipt)
                raise
            return {**observed(selected), 'changed': False}
        directory = a.safe(location(selected)); directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        check(directory.stat().st_uid == os.getuid(), 'path')
        receipt = {'schema_version': 1, 'profile_hash': selected['profile_hash'], 'recipe_hash': selected['recipe_hash'],
                   'profile': selected['profile'], 'operation_id': uuid.uuid4().hex, 'phase': 'acquiring',
                   'image': None, 'versions': None, 'error': None, 'duration_seconds': 0}
        job = a.safe(directory/'jobs'/receipt['operation_id']); job.mkdir(parents=True, mode=0o700)
        (job/'Containerfile').write_bytes(recipe_for(selected['profile']))
        (job/'profile.json').write_text(json.dumps(selected['profile'])+'\n')
        (job/'install-pnpm.cjs').write_bytes(deps.read_bytes(a.REPO/'templates/apps/node-toolchain/install-pnpm.cjs', 65536))
        (job/'auth.json').write_text('{"auths":{}}\n'); (job/'auth.json').chmod(0o600)
        a.save(directory/'receipt.json', receipt)
        try:
            built = a.command(['podman', 'build', '--authfile', str(job/'auth.json'), '--pull=missing', '--layers=false',
                       '--memory='+a.MEMORY, '--cpu-period=100000', '--cpu-quota=100000', '--ulimit=nproc='+str(a.PIDS)+':'+str(a.PIDS),
                       '--label', LABEL+'='+selected['profile_hash'], '--tag', tag_for(selected), str(job)], timeout=300, optional=True)
            if built.returncode:
                (job/'build.log').write_text(a.redact((built.stdout+'\n'+built.stderr)[-65536:]))
                raise a.AppError('command')
            image = image_info(selected); check(image is not None, 'toolchain-verification')
            verify(selected, image, receipt['operation_id'])
            receipt.update(phase='verified', image=image, versions=selected['profile']['versions'])
        except a.AppError as error:
            receipt.update(phase='unknown' if error.code == 'timeout' else 'failed', error=error.code)
            raise
        finally:
            receipt['duration_seconds'] = round(time.monotonic()-started, 3)
            a.save(directory/'receipt.json', receipt)
            history = directory/'receipts'; history.mkdir(mode=0o700, exist_ok=True)
            a.save(history/(receipt['operation_id']+'.json'), receipt)
        # Only fixed, verified owned job files; do not prune images or unknown builder objects.
        for name in ('Containerfile', 'profile.json', 'install-pnpm.cjs', 'auth.json'):
            path = job/name; deps.read_bytes(path, 65536); path.unlink()
        job.rmdir()
        return {**observed(selected), 'changed': True}


def inspect(root):
    root, contract = app().target(root); selected = selection(root)
    result = observed(selected)
    state = app().state_for(contract['project']['id'])
    result.update(project=contract['project']['id'], active_selection_hash=state.get('toolchain_hash') if state else None,
                  active_image=state['image'] if state else None)
    return result


def prepare(root):
    a = app(); root, contract = a.target(root); slug = contract['project']['id']
    selected = selection(root)
    with a.locked(slug):
        deps.require_clean(root, slug)
        s = deps.stopped_state(root, contract)
        result = acquire(selected)
        check(selection(root)['selection_hash'] == selected['selection_hash'], 'conflict')
        # A stopped target can move to the selected verified image. Source is untouched.
        if s['image'] != result['receipt']['image'] or s.get('toolchain_hash') != selected['selection_hash']:
            s.pop('prepared_digest', None); s.pop('build_digest', None)
        s.update(image=result['receipt']['image'], toolchain_hash=selected['selection_hash'], phase='stopped', health_ready=False)
        a.save(a.STORE/(slug+'.json'), s)
        return {**result, 'project': slug}


def assert_active(selected, state):
    # Existing running SPEC-018 legacy units stay on their accepted image until a managed stop/start.
    check(state.get('toolchain_hash') == selected['selection_hash'] or
          selected['legacy'] and state.get('toolchain_hash') is None, 'busy')
