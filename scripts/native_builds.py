"""Owned Android EAS jobs. No network or credentials during source planning."""
import gzip
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import tarfile
import time
import uuid
from urllib.parse import quote

import private_apps as app
import project_dependencies as deps
import project_worktrees as worktrees
import native_contract as contract

ACTIVE = {'submitting', 'queued', 'running', 'unknown'}
STATES = ACTIVE | {'succeeded', 'failed', 'cancelled'}
REMOTE = {'NEW': 'queued', 'IN_QUEUE': 'queued', 'IN_PROGRESS': 'running',
          'PENDING_CANCEL': 'running', 'FINISHED': 'succeeded', 'ERRORED': 'failed', 'CANCELED': 'cancelled'}
ROOT_FILES = {'app.json', 'package.json', 'pnpm-lock.yaml', 'pnpm-workspace.yaml', 'tsconfig.json', 'eas.json'}
MAX_FILES = 256
MAX_ARCHIVE = 32 * 1024 * 1024


def need(value, code='native-policy'):
    app.need(value, code)


def directory(project):
    __import__('project_mobile').identities(project)
    path = app.safe(app.STORE / 'native-builds' / project)
    path.mkdir(parents=True, mode=0o700, exist_ok=True)
    need(path.stat().st_uid == os.getuid() and path.stat().st_mode & 0o077 == 0, 'path')
    return path


def operation(value):
    need(isinstance(value, str) and re.fullmatch(r'[0-9a-f]{32}', value) is not None)
    return value


def git(root, *args):
    return worktrees.git(root, *args)[0].decode('utf-8')


def source(root):
    """Read tracked owned bytes, excluding all local state; reject unsafe tracked input."""
    need(not git(root, 'status', '--porcelain=v1', '--untracked-files=all'), 'native-dirty')
    commit = git(root, 'rev-parse', 'HEAD').strip()
    need(re.fullmatch(r'[0-9a-f]{40}', commit) is not None)
    listing = git(root, 'ls-files', '--stage', '-z').split('\0')
    selected = {}
    total = 0
    for item in listing:
        if not item:
            continue
        meta, name = item.split('\t', 1)
        mode, blob, stage = meta.split()
        need(stage == '0' and mode in {'100644', '100755'}, 'path')
        path = PurePosixPath(name)
        need(not path.is_absolute() and '..' not in path.parts and name == path.as_posix(), 'path')
        if name not in ROOT_FILES and path.parts[0] not in {'src', 'assets'}:
            continue
        need(not any(part.startswith('.') for part in path.parts)
             and not any(re.search(r'(?i)(secret|credential|\.env|\.pem$|\.key$|\.keystore$|\.p12$|\.sqlite|\.db$)', part) for part in path.parts))
        data = deps.read_bytes(app.safe(root / name), MAX_ARCHIVE)
        # Read index bytes too, preventing source/config races during snapshotting.
        need(hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == blob, 'native-dirty')
        need(re.search(rb'(?i)(-----BEGIN [A-Z ]*PRIVATE KEY|EXPO_TOKEN\s*[=:]|gh[pousr]_[A-Za-z0-9_]{20,}|tskey-(?:auth|api)-[A-Za-z0-9-]{10,})', data) is None)
        total += len(data)
        need(total <= MAX_ARCHIVE and len(selected) < MAX_FILES)
        selected[name] = data
    need(ROOT_FILES <= set(selected))
    package = deps.json_data(selected['package.json'])
    need(not any(k.startswith('eas-') or k in {'preinstall', 'postinstall', 'install', 'prepare', 'prepublish'} for k in package.get('scripts', {})))
    need(set(package) <= {'name','version','private','main','license','description','packageManager','engines','gptclawMobile','scripts','dependencies','devDependencies','optionalDependencies'})
    need(not git(root, 'status', '--porcelain=v1', '--untracked-files=all'), 'native-dirty')
    return commit, selected


def archive_bytes(files):
    """Exact portable EAS archive, with stable gzip/tar metadata and project prefix."""
    output = io.BytesIO()
    with gzip.GzipFile(fileobj=output, mode='wb', mtime=0, filename='') as compressed:
        with tarfile.open(fileobj=compressed, mode='w', format=tarfile.USTAR_FORMAT) as archive:
            for name, data in sorted(files.items()):
                item = tarfile.TarInfo('project/' + name)
                item.size = len(data); item.mode = 0o644; item.mtime = 0
                archive.addfile(item, io.BytesIO(data))
    return output.getvalue()


def verify_archive(data, inventory):
    need(len(data) <= MAX_ARCHIVE)
    found = {}
    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
            for item in archive:
                need(item.isfile() and item.name.startswith('project/') and item.size <= MAX_ARCHIVE)
                name = item.name[len('project/'):]
                need(name in inventory and name not in found)
                content = archive.extractfile(item).read(MAX_ARCHIVE + 1)
                need(len(content) == item.size and hashlib.sha256(content).hexdigest() == inventory[name])
                found[name] = inventory[name]
                need(len(found) <= MAX_FILES)
    except (tarfile.TarError, OSError):
        raise app.AppError('native-policy') from None
    need(found == inventory)


def plan(root):
    root, document, config = contract.inspect(root)
    commit, files = source(root)
    inventory = {name: hashlib.sha256(data).hexdigest() for name, data in files.items()}
    archive = archive_bytes(files); verify_archive(archive, inventory)
    value = {'schema_version': 1, 'project': document['project']['id'], 'root': str(root),
             'canonical_key': worktrees.canonical(root)['key'], 'commit': commit,
             'configuration_digest': contract.digest(config), 'native_fingerprint': contract.fingerprint(root),
             'account': config['account'], 'eas_project': config['project_id'], 'platform': 'android',
             'profile': 'development', 'approval_id': config['approval_id'],
             'archive_sha256': hashlib.sha256(archive).hexdigest(), 'inventory': inventory,
             'toolchain_digest': toolchain_digest()}
    value['plan_digest'] = contract.digest(value)
    return value, files, archive


def public_plan(root):
    value, _, data = plan(root)
    return {key: value[key] for key in ['schema_version', 'project', 'commit', 'plan_digest', 'archive_sha256',
                                       'native_fingerprint']} | {'state': 'build-planned', 'file_count': len(value['inventory']),
                                                               'archive_bytes': len(data), 'submits_build': False,
                                                               'contains_private_backend_configuration': 'src/config/backend.generated.ts' in value['inventory']}


def toolchain_digest():
    base = app.REPO / 'templates/apps/eas-toolchain'
    return contract.digest({name: hashlib.sha256(deps.read_bytes(base / name, 2 * 1024 * 1024)).hexdigest()
                            for name in ['Containerfile', 'package.json', 'package-lock.json', 'worker.cjs', '.dockerignore']})


def reviewed_image(tag, digest, label, context, prepare, timeout):
    def inspect():
        return app.command(['podman','image','inspect','--format',
                            '{{.Id}} {{index .Config.Labels "'+label+'"}}',tag],optional=True,timeout=15)
    def valid(result):
        fields=result.stdout.strip().split()
        return result.returncode==0 and len(fields)==2 and re.fullmatch(r'sha256:[0-9a-f]{64}',fields[0]) and fields[1]==digest
    present=app.command(['podman','image','exists',tag],optional=True,timeout=15)
    need(present.returncode in {0,1},'native-toolchain')
    current=inspect() if present.returncode==0 else None
    need(current is None or valid(current),'native-toolchain')
    if current is None:
        need(prepare,'native-toolchain')
        app.command(['podman','build','--label',label+'='+digest,'--tag',tag,str(context)],timeout=timeout)
        current=inspect()
    need(valid(current),'native-toolchain')
    return current.stdout.strip().split()[0]


def toolchain(prepare=False):
    digest = toolchain_digest()
    tag = 'localhost/gptclaw-eas:' + digest
    return reviewed_image(tag,digest,'com.gptclaw.native-toolchain',app.REPO/'templates/apps/eas-toolchain',prepare,600)


def audit_ok(parsed):
    """Counts must agree with the complete package/advisory map, not just a headline."""
    need(isinstance(parsed,dict), 'native-policy')
    actual={k:0 for k in ['info','low','moderate','high','critical']}
    entries=parsed.get('advisories',parsed.get('vulnerabilities'))
    need(isinstance(entries,dict) and len(entries)<=4096,'native-policy')
    for row in entries.values():
        need(isinstance(row,dict) and row.get('severity') in actual,'native-policy')
        actual[row['severity']]+=1
    counts=parsed.get('metadata',{}).get('vulnerabilities',{})
    need(isinstance(counts,dict) and all(type(counts.get(k)) is int and counts[k]==v for k,v in actual.items())
         and actual['high']==0 and actual['critical']==0,'native-policy')
    return actual


def security_gate(root, project):
    """Fresh source/tool audits without credentials; no inherited exceptions."""
    import metro_spike
    import project_toolchains
    import native_runtime
    metro_spike.prepared_dependencies(root, project)
    image = project_toolchains.observed(project_toolchains.selection(root))['receipt']['image']
    for argv in [
        ['podman', 'run', '--rm', '--entrypoint=npm', '--workdir=/opt/eas', toolchain(), 'audit', '--json'],
        ['podman', 'run', '--rm', '--read-only', '--userns=keep-id', '--cap-drop=all',
         '--security-opt=no-new-privileges', '--memory=1536m', '--pids-limit=256',
         '--tmpfs=/tmp:rw,size=128m,mode=1777', '--env=HOME=/tmp',
         '--volume', str(root)+':/workspace:ro', '--workdir=/workspace', image,
         'pnpm', 'audit', '--json', '--registry=https://registry.npmjs.org/']]:
        report = app.command(argv, optional=True, timeout=120)
        need(report.returncode in {0,1}, 'native-policy')
        parsed = json.loads(report.stdout)
        audit_ok(parsed)


def load(project, op):
    value = app.read_json(directory(project) / operation(op) / 'receipt.json')
    fields = {'schema_version', 'operation_id', 'project', 'root', 'state', 'plan', 'job_id', 'updated_at',
              'reserved_cost_cents', 'last_remote_at', 'artifact', 'installed', 'download_sha256'}
    need(isinstance(value, dict) and set(value) == fields and type(value['schema_version']) is int
         and value['schema_version'] == 1 and value['project'] == project and value['operation_id'] == op
         and value['state'] in STATES, 'native-recovery')
    p = value['plan']
    need(isinstance(p, dict) and p.get('project') == project and p.get('root') == value['root'])
    need(type(p.get('schema_version')) is int and p['schema_version']==1 and p.get('platform')=='android' and p.get('profile')=='development','native-recovery')
    need(p.get('plan_digest') == contract.digest({k: v for k, v in p.items() if k != 'plan_digest'}), 'native-recovery')
    need(value['job_id'] is None or isinstance(value['job_id'], str) and re.fullmatch(contract.UUID, value['job_id']) is not None)
    need(type(value['reserved_cost_cents']) is int and value['reserved_cost_cents'] >= 0)
    need(type(value['updated_at']) in {int, float} and value['updated_at'] > 0)
    need(value['last_remote_at'] is None or type(value['last_remote_at']) in {int, float})
    for field in ['native_fingerprint','archive_sha256','configuration_digest','canonical_key','toolchain_digest']:
        need(isinstance(p.get(field),str) and re.fullmatch(contract.HEX,p[field]),'native-recovery')
    downloaded=value['download_sha256']
    need(downloaded is None or isinstance(downloaded,str) and re.fullmatch(contract.HEX,downloaded),'native-recovery')
    artifact=value['artifact']
    if artifact is not None:
        need(isinstance(artifact,dict) and set(artifact)=={'sha256','package','certificate_sha256','job_id','verified_at','expires_at','evidence'}
             and artifact['sha256']==downloaded and isinstance(artifact['certificate_sha256'],str)
             and re.fullmatch(contract.HEX,artifact['certificate_sha256'])
             and artifact['package']==contract.identity(project)['android']['package']
             and artifact['job_id']==value['job_id'] and value['job_id'] is not None
             and artifact['evidence']=='apksig-8.13.0-and-binary-manifest'
             and type(artifact['verified_at']) in {int,float} and type(artifact['expires_at']) in {int,float}
             and 0<artifact['expires_at']-artifact['verified_at']<=30*86400+1,'native-recovery')
    installed=value['installed']
    if installed is not None:
        need(isinstance(installed,dict) and set(installed)=={'artifact_sha256','native_fingerprint','os','reported_at'}
             and value['state']=='succeeded' and artifact is not None
             and installed['artifact_sha256']==artifact['sha256']
             and isinstance(installed['native_fingerprint'],str) and re.fullmatch(contract.HEX,installed['native_fingerprint'])
             and isinstance(installed['os'],str) and re.fullmatch(r'Android [0-9]{1,2}(?:\.[0-9]{1,2})?',installed['os'])
             and type(installed['reported_at']) in {int,float},'native-recovery')
    return value


def save(value):
    app.save(directory(value['project']) / value['operation_id'] / 'receipt.json', value)


def receipts(project):
    values = []
    for path in directory(project).iterdir():
        if not path.is_dir() or re.fullmatch(r'[0-9a-f]{32}', path.name) is None:
            continue
        need(len(values) < 1000)
        values.append(load(project, path.name))
    return values


def public(value):
    return {'project': value['project'], 'operation_id': value['operation_id'], 'state': value['state'],
            'job_id': value['job_id'], 'commit': value['plan']['commit'], 'updated_at': value['updated_at'],
            'last_remote_at': value['last_remote_at'], 'artifact_verified': value['artifact'] is not None,
            'installation_recorded': value['installed'] is not None}


def worker(value, action, credential_file, job=None):
    """Fixed container, bounded outputs; credential is a mounted file, never argv/env."""
    secret = app.safe(Path(credential_file).absolute())
    info = secret.stat()
    need(stat.S_ISREG(info.st_mode) and info.st_uid == os.getuid() and info.st_nlink == 1
         and info.st_mode & 0o077 == 0 and 16 <= info.st_size <= 4096, 'path')
    need(not secret.is_relative_to(app.PROJECTS), 'path')
    image = toolchain()
    base = directory(value['project']) / value['operation_id']
    stage = base / 'source'
    # Dependency preparation has its own credential-free step before submit.
    modules = app.safe(Path(value['root']) / 'node_modules')
    need(modules.is_dir() and not modules.is_symlink(), 'native-toolchain')
    argv = ['podman', 'run', '--rm', '--read-only', '--userns=keep-id', '--user', str(os.getuid()) + ':' + str(os.getgid()),
            '--cap-drop=all', '--security-opt=no-new-privileges', '--pids-limit=256', '--memory=2g', '--cpus=2',
            '--tmpfs=/tmp:rw,size=512m,mode=1777', '--env=HOME=/tmp/home', '--env=CI=1',
            '--volume', str(secret) + ':/run/secrets/expo-token:ro', '--volume', str(base) + ':/input:ro',
            '--volume', str(stage) + ':/workspace:ro', '--volume', str(modules) + ':/workspace/node_modules:ro',
            '--workdir=/workspace', image, action, job or '', 'gptclaw:' + value['operation_id'] + ':' + value['plan']['plan_digest']]
    result = app.command(argv, timeout=240, optional=True)
    need(result.returncode == 0, 'native-remote')
    if action=='cancel':return {}
    try:
        parsed = json.loads(result.stdout)
        if action == 'submit':
            need(isinstance(parsed, list) and len(parsed) == 1)
            parsed = parsed[0]
        return parsed
    except ValueError:
        raise app.AppError('native-remote') from None


def accept_remote(value, remote):
    """Accept identity and state only. Never persist remote messages or bearer URLs."""
    p = value['plan']
    need(isinstance(remote, dict) and isinstance(remote.get('id'), str) and re.fullmatch(contract.UUID, remote['id']))
    need(value['job_id'] in {None, remote['id']} and remote.get('platform') == 'ANDROID'
         and remote.get('buildProfile') == 'development' and remote.get('distribution') == 'INTERNAL'
         and remote.get('appIdentifier') == contract.identity(value['project'])['android']['package']
         and isinstance(remote.get('app'), dict) and remote['app'].get('id') == p['eas_project']
         and remote['app'].get('ownerAccount', {}).get('name') == p['account']
         and remote.get('message') == 'gptclaw:' + value['operation_id'] + ':' + p['plan_digest']
         and remote.get('status') in REMOTE, 'native-remote')
    need(value['state'] in ACTIVE or value['state']==REMOTE[remote['status']], 'native-remote')
    value.update(job_id=remote['id'], state=REMOTE[remote['status']], updated_at=time.time(), last_remote_at=time.time())
    return value


def submit(root, confirm_plan, credential_file):
    p, files, archive = plan(root)
    need(confirm_plan == p['plan_digest'], 'native-drift')
    _, _, config = contract.inspect(root)
    security_gate(Path(p['root']), p['project'])
    project = p['project']
    with app.locked('native-submission', project_guard=False), app.locked(project):
        old = receipts(project)
        need(not any(r['state'] in ACTIVE for r in old), 'native-recovery')
        # Limits apply to the approval identity across configuration edits, not per revision.
        prior = [r for r in old if r['plan']['approval_id'] == config['approval_id']]
        need(len(prior) < config['attempt_limit']
             and sum(r['reserved_cost_cents'] for r in prior) + config['attempt_cost_ceiling_cents'] <= config['budget_cents'], 'native-budget')
        # Compare again under locks before intent/archive persistence.
        fresh, files, archive = plan(root); need(fresh == p, 'native-drift')
        op = uuid.uuid4().hex; base = directory(project) / op; base.mkdir(mode=0o700)
        stage = base / 'source'; stage.mkdir(mode=0o700)
        for name, data in files.items():
            out = stage / name; out.parent.mkdir(parents=True, exist_ok=True, mode=0o700); out.write_bytes(data)
        (base / 'archive.tar.gz').write_bytes(archive)
        (base / 'archive.sha256').write_text(p['archive_sha256'] + '\n')
        value = {'schema_version': 1, 'operation_id': op, 'project': project, 'root': str(root), 'state': 'submitting',
                 'plan': p, 'job_id': None, 'updated_at': time.time(), 'last_remote_at': None,
                 'reserved_cost_cents': config['attempt_cost_ceiling_cents'], 'artifact': None, 'installed': None, 'download_sha256': None}
        save(value)  # Durable intent before the first possible external request.
        try:
            accept_remote(value, worker(value, 'submit', credential_file))
        except (app.AppError, OSError, ValueError):
            value.update(state='unknown', updated_at=time.time()); save(value)
            return public(value)
        save(value)
        return public(value)


def observe(root, op, credential_file=None, reconcile_job=None):
    root, document = app.target(root)
    project = document['project']['id']
    with app.locked(project):
        value = load(project, op); need(value['root'] == str(root))
        if credential_file:
            job = reconcile_job or value['job_id']
            need(isinstance(job, str) and re.fullmatch(contract.UUID, job) is not None, 'native-recovery')
            try:
                remote = worker(value, 'observe', credential_file, job)
                accept_remote(value, remote); save(value)
            except (app.AppError, ValueError, OSError):
                # Retain last verified state/time; observation failure cannot release admission.
                return public(value) | {'observation': 'unavailable'}
        return public(value)


def artifact_url(value):
    from urllib.parse import urlsplit
    need(isinstance(value, str) and len(value) <= 8192 and not any(ord(c) < 33 for c in value))
    parsed = urlsplit(value)
    host = parsed.hostname or ''
    allowed = host in {'expo.dev', 'expo.io', 'production-eas-builds.s3.us-east-1.amazonaws.com'} or host.endswith('.storage.googleapis.com')
    need(parsed.scheme == 'https' and parsed.port in {None, 443} and not parsed.username
         and not parsed.password and not parsed.fragment and allowed, 'native-remote')
    return value


def download_apk(url, destination):
    import urllib.request
    class Redirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, request, response, code, message, headers, newurl):
            artifact_url(newurl)
            return super().redirect_request(request, response, code, message, headers, newurl)
    try:
        opener = urllib.request.build_opener(Redirect())
        with opener.open(artifact_url(url), timeout=60) as response, destination.open('xb') as out:
            total = 0; deadline = time.monotonic() + 120
            while True:
                need(time.monotonic() < deadline, 'native-remote')
                data = response.read(1024 * 1024)
                if not data: break
                total += len(data); need(total <= 256 * 1024 * 1024, 'native-remote'); out.write(data)
            need(total > 0, 'native-remote')
    except Exception:
        destination.unlink(missing_ok=True)
        raise app.AppError('native-remote') from None


def fetch_artifact(root, op, credential_file):
    root, document = app.target(root); project = document['project']['id']
    with app.locked(project):
        value = load(project, op); need(value['root'] == str(root) and value['job_id'] is not None)
        remote = worker(value, 'observe', credential_file, value['job_id'])
        accept_remote(value, remote); save(value); need(value['state'] == 'succeeded', 'native-remote')
        artifacts = remote.get('artifacts'); need(isinstance(artifacts, dict), 'native-remote')
        url = artifacts.get('applicationArchiveUrl') or artifacts.get('buildUrl')
        base = directory(project) / op; path = base / ('artifact-' + uuid.uuid4().hex + '.apk')
        download_apk(url, path)
        path.chmod(0o600)
        try:
            value['download_sha256'] = hashlib.sha256(deps.read_bytes(path, 256 * 1024 * 1024)).hexdigest()
            save(value)
            result = verified_artifact(root, op, path, take_lock=False)
            # Keep one exact verified artifact with a 30-day bounded eligibility receipt.
            os.replace(path, base / 'artifact.apk')
            return result
        finally:
            path.unlink(missing_ok=True)


def apk_toolchain(prepare=False):
    base = app.REPO / 'templates/apps/apk-verifier'
    digest = contract.digest({name: hashlib.sha256(deps.read_bytes(base / name)).hexdigest()
                              for name in ['Containerfile', 'VerifyApk.java']})
    tag = 'localhost/gptclaw-apk-verifier:' + digest
    return reviewed_image(tag,digest,'com.gptclaw.apk-verifier',base,prepare,300)


def verified_artifact(root, op, apk_file, take_lock=True):
    """Verify signed APK bytes/package/certificate before recording install eligibility."""
    root, document = app.target(root); project = document['project']['id']
    with (app.locked(project) if take_lock else contextlib.nullcontext()):
        value = load(project, op); need(value['root'] == str(root) and value['state'] == 'succeeded')
        _, _, config = contract.inspect(root)
        path = app.safe(Path(apk_file).absolute())
        apk = deps.read_bytes(path, 256 * 1024 * 1024)
        need(value['download_sha256'] == hashlib.sha256(apk).hexdigest(), 'native-remote')
        import apk_metadata
        try: package = apk_metadata.package(apk)
        except (ValueError, OSError, IndexError, __import__('struct').error, __import__('zipfile').BadZipFile):
            raise app.AppError('native-policy') from None
        need(package == contract.identity(project)['android']['package'])
        # Snapshot prevents changing the host APK between metadata and signature checks.
        base = directory(project) / op
        snapshot = base / ('verify-' + uuid.uuid4().hex + '.apk')
        with snapshot.open('xb') as out: out.write(apk)
        snapshot.chmod(0o600)
        try:
            response = app.command(['podman', 'run', '--rm', '--read-only', '--network=none',
                                    '--cap-drop=all', '--security-opt=no-new-privileges', '--memory=512m',
                                    '--pids-limit=64', '--userns=keep-id', '--user', str(os.getuid())+':'+str(os.getgid()),
                                    '--volume', str(snapshot)+':/input/app.apk:ro', apk_toolchain(), '/input/app.apk'],
                                   optional=True, timeout=60)
            certificate = response.stdout.strip()
            need(response.returncode == 0 and certificate == config['certificate_sha256'])
        finally:
            snapshot.unlink(missing_ok=True)
        value['artifact'] = {'sha256': hashlib.sha256(apk).hexdigest(), 'package': package,
                             'certificate_sha256': certificate, 'job_id': value['job_id'],
                             'verified_at': time.time(), 'expires_at': time.time() + config['retention_days'] * 86400,
                             'evidence': 'apksig-8.13.0-and-binary-manifest'}
        save(value)
        return public(value)


def installed(root, op, artifact_digest, device_os):
    root, document = app.target(root); project = document['project']['id']
    need(isinstance(device_os, str) and re.fullmatch(r'Android [0-9]{1,2}(?:\.[0-9]{1,2})?', device_os))
    with app.locked(project):
        value = load(project, op); artifact = value['artifact']
        need(value['state']=='succeeded' and value['root'] == str(root) and artifact is not None and artifact['sha256'] == artifact_digest
             and artifact['expires_at'] > time.time())
        value['installed'] = {'artifact_sha256': artifact_digest, 'native_fingerprint': value['plan']['native_fingerprint'],
                              'os': device_os, 'reported_at': time.time()}
        save(value)
        return public(value)


def launch(root, op, generation):
    root, document, _ = contract.inspect(root)
    value = load(document['project']['id'], op)
    need(value['root'] == str(root))
    installation = value['installed']
    need(installation is None or value['state']=='succeeded' and value['artifact'] is not None and installation.get('artifact_sha256')==value['artifact'].get('sha256'))
    if installation is None or value['artifact'] is None:
        return {'project': value['project'], 'state': 'installation-unknown', 'launch': None}
    if installation['native_fingerprint'] != contract.fingerprint(root):
        return {'project': value['project'], 'state': 'rebuild-required', 'launch': None}
    if value['artifact']['expires_at'] <= time.time():
        return {'project': value['project'], 'state': 'evidence-expired', 'launch': None}
    import metro_sessions
    descriptor = metro_sessions.status(root)
    need(descriptor.get('generation') == generation, 'native-drift')
    if not descriptor.get('transport_available') or descriptor.get('requested_mode') != 'development-client':
        return {'project': value['project'], 'state': 'metro-unavailable', 'launch': None}
    origin = descriptor.get('origin')
    need(isinstance(origin, str) and origin.startswith('https://'))
    from metro_protocol import origin as check_origin
    need(check_origin(origin) == origin)
    payload = contract.identity(value['project'])['scheme'] + '://expo-development-client/?url=' + quote(origin, safe='')
    return {'project': value['project'], 'state': 'launch-available', 'generation': generation,
            'launch': payload, 'device_presence': 'unobserved'}


def resolve_not_submitted(root, op, confirmation):
    """Explicit owner/operator attestation after remote-account reconciliation."""
    root, document = app.target(root); project = document['project']['id']
    with app.locked(project):
        value = load(project, op)
        need(value['root']==str(root) and value['state']=='unknown' and value['job_id'] is None
             and confirmation==op+':'+value['plan']['plan_digest'], 'native-recovery')
        value.update(state='failed', updated_at=time.time())
        # Retain full intent and budget reservation; resolution never refunds an attempt.
        app.save(directory(project)/op/'no-remote-job-attestation.json',
                 {'operation_id':op,'plan_digest':value['plan']['plan_digest'],
                  'owner_attested_at':time.time(),'resolution':'no-remote-job'})
        save(value)
        return public(value)


def cancel(root, op, credential_file, confirm_job):
    root, document = app.target(root); project = document['project']['id']
    with app.locked(project):
        value = load(project, op)
        need(value['root']==str(root) and value['job_id'] is not None and value['job_id']==confirm_job
             and value['state'] in ACTIVE, 'native-recovery')
        accept_remote(value,worker(value,'observe',credential_file,value['job_id']))
        save(value)
        if value['state'] in ACTIVE:
            worker(value,'cancel',credential_file,value['job_id'])
            # Cancellation acknowledgement does not establish remote finality or refund.
        return public(value) | {'cancellation_requested': True}
