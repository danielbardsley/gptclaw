"""Static opt-in Android build configuration; never evaluates application code."""
import copy
import hashlib
import json
import re
import uuid
from pathlib import Path

import private_apps as app
import project_dependencies as deps
import project_mobile as mobile
import project_worktrees as worktrees

CONFIG = '.gptclaw/development-build.json'
HEX = r'[0-9a-f]{64}'
UUID = r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}'


def need(value):
    app.need(value, 'native-policy')


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def identity(slug):
    value = mobile.identities(slug)
    value['scheme'] += '-dev'
    value['android']['package'] += '.development'
    return value


def contract(slug, bound=False):
    value = mobile.contract(slug)
    value.update(schema_version=12 if bound else 11,
                 metro={'adapter': 'metro-v1', 'mode': 'development-client', 'ttl_seconds': 7200},
                 development_build={'adapter': 'eas-android-v1', 'config': CONFIG})
    value['mobile']['adapter'] = 'expo-dev-v1'
    value['mobile']['targets'] = ['android']
    if bound:
        value['backend'] = {'adapter': 'fastapi-postgres-v1', 'profile': 'development',
                            'contract_version': 1, 'config': '.gptclaw/backend.local.json'}
    return value


def app_config(expo, document):
    expected = identity(document['project']['id'])
    allowed = {'name', 'slug', 'scheme', 'version', 'platforms', 'orientation', 'ios', 'android', 'plugins', 'owner', 'extra'}
    if not isinstance(expo, dict) or not set(expo) <= allowed:
        return False
    if expo.get('name') != document['project']['name'] or not all(expo.get(k) == v for k, v in expected.items()):
        return False
    if (expo.get('platforms') != ['android'] or expo.get('orientation') != 'portrait'
            or expo.get('plugins') != [['expo-dev-client', {'launchMode': 'most-recent'}]]
            or not isinstance(expo.get('version'), str)
            or re.fullmatch(r'\d+\.\d+\.\d+', expo['version']) is None):
        return False
    if 'owner' in expo or 'extra' in expo:
        return (isinstance(expo.get('owner'), str) and re.fullmatch(r'[a-zA-Z0-9_-]{1,64}', expo['owner']) is not None
                and isinstance(expo.get('extra'), dict) and set(expo['extra']) == {'eas'}
                and isinstance(expo['extra']['eas'], dict) and set(expo['extra']['eas']) == {'projectId'}
                and isinstance(expo['extra']['eas']['projectId'], str)
                and re.fullmatch(UUID, expo['extra']['eas']['projectId']) is not None)
    return True


def eas_config():
    matrix = mobile.profile(True)
    return {'cli': {'version': matrix['build']['eas_cli'], 'appVersionSource': 'local'},
            'build': {'development': {'developmentClient': True, 'distribution': 'internal',
                                     'environment': 'development', 'credentialsSource': 'remote',
                                     'node': matrix['toolchain']['versions']['node'],
                                     'pnpm': matrix['toolchain']['versions']['pnpm'],
                                     'env': {'EXPO_NO_DOTENV': '1', 'EXPO_NO_TELEMETRY': '1'},
                                     'android': {'buildType': 'apk', 'image': matrix['build']['cloud_image']}}}}


def configuration(root):
    value = deps.json_data(deps.read_bytes(root / CONFIG, 16384))
    fields = {'schema_version', 'platform', 'environment', 'account', 'project_id', 'signing',
              'certificate_sha256', 'retention_days', 'artifact_access', 'attempt_limit',
              'budget_cents', 'attempt_cost_ceiling_cents', 'credential_scope', 'approval_id', 'expires_at'}
    need(isinstance(value, dict) and set(value) == fields)
    need(type(value['schema_version']) is int and value['schema_version'] == 1
         and value['platform'] == 'android' and value['environment'] == 'development'
         and value['signing'] == 'expo-managed' and value['artifact_access'] == 'authenticated'
         and value['credential_scope'] in {'isolated-account', 'owner-accepted-account-access'})
    for field, pattern in [('account', r'[a-zA-Z0-9_-]{1,64}'), ('project_id', UUID),
                           ('certificate_sha256', HEX), ('approval_id', r'[a-zA-Z0-9_-]{1,100}')]:
        need(isinstance(value[field], str) and re.fullmatch(pattern, value[field]) is not None)
    for field, minimum, maximum in [('retention_days', 1, 30), ('attempt_limit', 1, 20),
                                     ('budget_cents', 0, 100000), ('attempt_cost_ceiling_cents', 0, 10000)]:
        need(type(value[field]) is int and minimum <= value[field] <= maximum)
    import metro_security
    need(metro_security.timestamp(value['expires_at']) > __import__('time').time())
    need(value['attempt_cost_ceiling_cents'] <= value['budget_cents'])
    return value


def inspect(root):
    root, document = app.target(root)
    need(document['schema_version'] in (11, 12))
    worktrees.canonical(root)
    need(mobile.manifest_config(root, document))
    config = configuration(root)
    expo = deps.json_data(deps.read_bytes(root / 'app.json'))['expo']
    need(expo.get('owner') == config['account']
         and expo.get('extra') == {'eas': {'projectId': config['project_id']}})
    need(deps.json_data(deps.read_bytes(root / 'eas.json')) == eas_config())
    mobile.validate_package(deps.json_data(deps.read_bytes(root / 'package.json')))
    if document['schema_version'] == 12:
        import mobile_backend
        binding = mobile_backend.inspect(root)
        need(deps.read_bytes(root / mobile_backend.GENERATED).decode() == mobile_backend.generated(binding))
    return root, document, config


def fingerprint(root):
    # JS edits stay reloadable. Lock/native configuration changes require a new binary.
    files = ['package.json', 'pnpm-lock.yaml', 'pnpm-workspace.yaml', 'app.json', 'eas.json',
             '.gptclaw/project.yaml', '.gptclaw/toolchain.json']
    values = {p: hashlib.sha256(deps.read_bytes(root / p)).hexdigest() for p in files}
    values['profile'] = digest(mobile.profile(True))
    return digest(values)


def configure(root, config_file, apply=False, confirm=None):
    root, document = app.target(root)
    need(document['schema_version'] in (11, 12))
    worktrees.canonical(root)
    raw = deps.read_bytes(app.safe(Path(config_file).absolute()), 16384)
    value = deps.json_data(raw)
    # Validate in a task-owned temporary directory, never write malformed config to source.
    import tempfile
    with tempfile.TemporaryDirectory(prefix='gptclaw-native-config-') as tmp:
        stage = Path(tmp); (stage / '.gptclaw').mkdir()
        (stage / CONFIG).write_bytes(raw)
        configuration(stage)
    expo = deps.json_data(deps.read_bytes(root / 'app.json'))
    need(app_config(expo.get('expo'), document))
    updated = copy.deepcopy(expo)
    updated['expo'].update(owner=value['account'], extra={'eas': {'projectId': value['project_id']}})
    plan = digest({'project': document['project']['id'], 'before': expo, 'after': updated, 'config': value})
    if apply:
        need(confirm == plan)
        with app.locked(document['project']['id']):
            import metro_sessions
            metro_sessions.assert_stopped(root, document['project']['id'])
            need(deps.json_data(deps.read_bytes(root / 'app.json')) == expo)
            # Journal intent first. A partial write fails closed at inspect and retains both inputs.
            directory = app.safe(app.STORE / 'native-config' / document['project']['id'])
            directory.mkdir(parents=True, mode=0o700, exist_ok=True)
            app.save(directory / (uuid.uuid4().hex + '.json'), {'plan': plan, 'previous': expo, 'proposed': updated})
            app.save(root / CONFIG, value)
            app.save(root / 'app.json', updated)
    return {'project': document['project']['id'], 'state': 'configured' if apply else 'configuration-planned',
            'plan_digest': plan, 'changed': apply, 'starts_session': False, 'submits_build': False}
