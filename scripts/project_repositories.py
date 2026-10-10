"""Opt-in private repository provisioning; journals contain metadata, never tokens."""
import base64
import contextlib
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import urllib.error
import urllib.parse
import urllib.request
import uuid

import private_apps as app
import project_templates as templates

ACCOUNT = 'danielbardsley'
API_VERSION = '2026-03-10'
PROTECTION = {
    'required_status_checks': None,
    'enforce_admins': True,
    'required_pull_request_reviews': {'dismiss_stale_reviews': True,
                                     'require_code_owner_reviews': False,
                                     'required_approving_review_count': 0,
                                     'require_last_push_approval': False},
    'restrictions': None, 'required_linear_history': False,
    'allow_force_pushes': False, 'allow_deletions': False,
    'required_conversation_resolution': True,
    'block_creations': False, 'lock_branch': False,
    'allow_fork_syncing': False,
}
ENVIRONMENT = {'deployment_branch_policy': {'protected_branches': True,
                                           'custom_branch_policies': False}}
MESSAGES = {
    'repository-policy': 'Invalid repository plan, target or unsupported option.',
    'repository-credential': 'Use an explicit private, owned fine-grained token file outside repositories and a future expiry within seven days.',
    'repository-api': 'GitHub denied or could not verify this scoped request; inspect repo status. No permissions were broadened.',
    'repository-recovery': 'Setup requires reconciliation; inspect repo status and resume the same operation. Source and remote resources were retained.',
    'repository-drift': 'Recorded source or remote identity/settings changed; stop and reconcile with the owner.',
    'repository-capability': 'Private branch protection requires a supported account plan; no visibility or policy fallback was selected.',
}
app.MESSAGES.update(MESSAGES)


def require(value, code='repository-policy'):
    app.need(value, code)


def digest(value):
    return templates.digest(value)


def timestamp():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def expiry(value):
    try:
        parsed = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
        require(parsed.tzinfo is not None, 'repository-credential')
        remaining = parsed - dt.datetime.now(dt.timezone.utc)
        require(dt.timedelta(0) < remaining <= dt.timedelta(days=7), 'repository-credential')
        return parsed.isoformat()
    except (ValueError, TypeError, AttributeError):
        raise app.AppError('repository-credential') from None


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


class GitHub:
    """No global credential lookup, redirects, proxies, raw error bodies or retries."""
    def __init__(self, credential_file, expires_at):
        self.expires_at = expiry(expires_at)
        path = app.safe(Path(credential_file).absolute())
        require(not path.is_relative_to(app.PROJECTS) and not path.is_relative_to(app.REPO)
                and path.parent.stat().st_uid == os.getuid()
                and stat.S_IMODE(path.parent.stat().st_mode) == 0o700, 'repository-credential')
        try:
            fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
            with os.fdopen(fd, 'rb') as stream:
                info = os.fstat(stream.fileno())
                require(stat.S_ISREG(info.st_mode) and info.st_uid == os.getuid()
                        and stat.S_IMODE(info.st_mode) == 0o600 and info.st_nlink == 1
                        and info.st_size <= 1024, 'repository-credential')
                token = stream.read(1025).strip().decode('ascii')
            require(re.fullmatch(r'github_pat_[A-Za-z0-9_]{20,950}', token), 'repository-credential')
        except (OSError, UnicodeError):
            raise app.AppError('repository-credential') from None
        self._token = token
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())

    def request(self, method, path, body=None, missing=False):
        require(path.startswith('/') and not path.startswith('//') and '\\' not in path)
        expiry(self.expires_at)
        payload = None if body is None else json.dumps(body).encode()
        require(payload is None or len(payload) <= 10 * 1024 * 1024)
        request = urllib.request.Request('https://api.github.com' + path, data=payload,
            method=method, headers={'Accept': 'application/vnd.github+json',
                'Authorization': 'Bearer ' + self._token, 'X-GitHub-Api-Version': API_VERSION,
                'Content-Type': 'application/json', 'User-Agent': 'GptClaw-repositories/1'})
        try:
            with self.opener.open(request, timeout=30) as response:
                raw = response.read(2 * 1024 * 1024 + 1)
            require(len(raw) <= 2 * 1024 * 1024, 'repository-api')
            return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as error:
            if missing and error.code == 404: return None
            if missing and method == 'GET' and '/git/ref/heads/' in path and error.code == 409:
                # GitHub reports an empty repository as 409 rather than missing ref 404.
                try:
                    raw = error.read(4097)
                    if len(raw) <= 4096 and json.loads(raw).get('message') == 'Git Repository is empty.':
                        return None
                except (OSError, ValueError, AttributeError):
                    pass
            raise app.AppError('repository-api') from None
        except (OSError, ValueError):
            raise app.AppError('repository-api') from None

    def actor(self):
        actor = self.request('GET', '/user')
        require(actor.get('login') == ACCOUNT and actor.get('type') == 'User', 'repository-credential')
        plan = actor.get('plan', {}).get('name')
        require(plan is None or plan in {'pro', 'business', 'enterprise'}, 'repository-capability')
        return {'login': ACCOUNT, 'plan': plan, 'private_protection_readiness': 'endpoint-verification-required' if plan is None else 'supported-plan-reported', 'credential_kind': 'fine-grained-pat',
                'expires_at': self.expires_at,
                'permission_verification': 'endpoint-enforced; grants must be operator-reviewed'}

    @contextlib.contextmanager
    def git_environment(self):
        # Anonymous seekable fd: token values never appear in argv/environment/files.
        fd = os.memfd_create('gptclaw-repository-auth', os.MFD_CLOEXEC)
        try:
            os.write(fd, self._token.encode())
            yield {'GIT_ASKPASS': str(app.REPO/'scripts/repository_askpass.py'),
                   'GPTCLAW_REPOSITORY_AUTH_FD': str(fd)}, (fd,)
        finally:
            os.close(fd)


def target_path(value):
    path = app.safe(Path(value).absolute())
    require(path.is_relative_to(app.PROJECTS) and path != app.PROJECTS and not path.is_relative_to(app.REPO)
            and not any(part.startswith('.gptclaw') for part in path.relative_to(app.PROJECTS).parts), 'path')
    require(path.parent.is_dir() and path.parent.stat().st_uid == os.getuid(), 'path')
    for parent in path.parents:
        if not parent.is_relative_to(app.PROJECTS): break
        require(not (parent/'.git').exists() and not (parent/'.git').is_symlink()
                and not (parent/'.gptclaw/project.yaml').exists(), 'path')
    return path


def validate_plan(value, vacant=False):
    keys = {'schema_version', 'operation_id', 'account', 'repository', 'private', 'destination',
            'template', 'branches', 'protection', 'environments', 'secret_references',
            'capabilities', 'description', 'plan_digest'}
    require(isinstance(value, dict) and set(value) == keys)
    require(type(value['schema_version']) is int and value['schema_version'] == 1)
    require(isinstance(value['operation_id'], str) and re.fullmatch(r'[a-f0-9]{32}', value['operation_id']))
    require(value['account'] == ACCOUNT and value['private'] is True)
    name = value['repository']
    require(isinstance(name, str) and len(name) <= 48 and re.fullmatch(r'[a-z][a-z0-9]*(?:-[a-z0-9]+)*', name))
    path = target_path(value['destination'])
    if vacant: require(not path.exists() and not path.is_symlink(), 'conflict')
    require(value['destination'] == str(path))
    release, _ = templates.resolve('nextjs', '1.0.0')
    require(value['template'] == templates.provenance(release))
    require(value['branches'] == {'base': 'main', 'head': 'codex/bootstrap-' + value['operation_id']})
    require(value['protection'] == PROTECTION)
    require(value['description'] == 'Private application; GptClaw setup ' + value['operation_id'])
    environments = value['environments']
    require(isinstance(environments, list) and len(environments) <= 2 and environments == sorted(set(environments)))
    require(all(name in {'development', 'preview'} for name in environments))
    refs = value['secret_references']
    require(isinstance(refs, list) and len(refs) <= 20)
    pairs = []
    for ref in refs:
        require(isinstance(ref, dict) and set(ref) == {'name', 'scope'})
        require(isinstance(ref['name'], str) and re.fullmatch(r'[A-Z][A-Z0-9_]{0,63}', ref['name'])
                and not ref['name'].startswith('GITHUB_'))
        require(ref['scope'] == 'repository' or ref['scope'] in environments)
        pairs.append((ref['scope'], ref['name']))
    require(pairs == sorted(set(pairs)))
    require(value['capabilities'] == capabilities(environments, refs))
    require(value['plan_digest'] == digest({k: v for k, v in value.items() if k != 'plan_digest'}))
    return value


def capabilities(environments, refs):
    return ['repository-creation:write', 'administration:write', 'contents:write', 'pull-requests:write'] + (
        ['environments:write'] if environments else []) + (['secrets:read-metadata'] if refs else [])


def plan(name, destination, api, environments=(), secret_references=()):
    # Validate every input locally before observation. No journals/locks/source writes.
    operation = uuid.uuid4().hex
    release, _ = templates.resolve('nextjs', '1.0.0')
    value = {'schema_version': 1, 'operation_id': operation, 'account': ACCOUNT,
             'repository': name, 'private': True, 'destination': str(target_path(destination)),
             'template': templates.provenance(release),
             'branches': {'base': 'main', 'head': 'codex/bootstrap-' + operation},
             'protection': PROTECTION, 'environments': sorted(environments),
             'secret_references': sorted(secret_references, key=lambda r: (r['scope'], r['name'])),
             'capabilities': capabilities(environments, secret_references),
             'description': 'Private application; GptClaw setup ' + operation}
    value['plan_digest'] = digest(value)
    validate_plan(value, vacant=True)
    actor = api.actor()
    require(api.request('GET', prefix(value), missing=True) is None, 'conflict')
    return {'state': 'planned', 'plan': value, 'observation': {'at': timestamp(), 'actor': actor,
            'name_observation': 'not-found-or-not-visible; creation enforces uniqueness', 'readiness': 'rechecked on apply; repository-specific grants pending until creation'}}


def prefix(value):
    return '/repos/' + ACCOUNT + '/' + value['repository']


def workspace(operation):
    require(isinstance(operation, str) and re.fullmatch(r'[a-f0-9]{32}', operation))
    return app.STORE/'repositories'/operation


def read_metadata(path):
    import project_dependencies as deps
    try:
        return deps.json_data(deps.read_bytes(Path(path).absolute(), 65536))
    except app.AppError:
        raise app.AppError('repository-policy') from None


def read_plan(path):
    value = read_metadata(path)
    if isinstance(value, dict) and set(value) in ({'state', 'plan', 'observation'}, {'state', 'plan', 'observation', 'duration_seconds'}):
        require(value['state'] == 'planned' and isinstance(value['observation'], dict))
        if 'duration_seconds' in value:
            require(type(value['duration_seconds']) in {int, float} and value['duration_seconds'] >= 0)
        value = value['plan']
    return validate_plan(value)


def read_receipt(operation):
    path = workspace(operation)/'receipt.json'
    require(path.exists() or path.is_symlink(), 'repository-recovery')
    value = read_metadata(path)
    require(isinstance(value, dict) and value.get('schema_version') == 1
            and value.get('operation_id') == operation, 'repository-recovery')
    validate_plan(value['plan'])
    require(value['plan']['operation_id'] == operation, 'repository-recovery')
    return value


def persist(receipt):
    receipt['updated_at'] = timestamp()
    app.save(workspace(receipt['operation_id'])/'receipt.json', receipt)


def check_git_storage(root):
    folder = root/'.git'
    if not folder.exists(): return
    app.safe(folder)
    require(folder.is_dir(), 'repository-drift')
    paths = list(folder.rglob('*'))
    require(len(paths) <= 1000, 'repository-drift')
    for path in paths:
        app.safe(path)
        require(not path.is_symlink() and path.lstat().st_uid == os.getuid(), 'repository-drift')
        if path.is_file(): require(path.stat().st_nlink == 1, 'repository-drift')
    config = folder/'config'
    require(config.is_file() and config.stat().st_size < 4096, 'repository-drift')
    section = None
    seen = set()
    permitted = {'core': {'repositoryformatversion': '0', 'filemode': 'true',
                         'bare': 'false', 'logallrefupdates': 'true'},
                 'remote "origin"': {'fetch': '+refs/heads/*:refs/remotes/origin/*'}}
    for line in config.read_text().splitlines():
        line = line.strip()
        if not line: continue
        if line.startswith('[') and line.endswith(']'):
            section = line[1:-1]; require(section in permitted, 'repository-drift'); continue
        require(section is not None and '=' in line, 'repository-drift')
        key, value = (piece.strip() for piece in line.split('=', 1))
        require((section, key) not in seen, 'repository-drift'); seen.add((section, key))
        if section == 'remote "origin"' and key == 'url':
            require(re.fullmatch(r'https://github.com/danielbardsley/[a-z][a-z0-9-]{0,47}\.git', value), 'repository-drift')
        else: require(permitted[section].get(key) == value, 'repository-drift')


def git(root, *args, api=None, input_bytes=None):
    # No inherited Git config/templates/helpers/hooks, SSH or environment credentials.
    check_git_storage(Path(root))
    env = {'PATH': '/usr/local/bin:/usr/bin:/bin', 'HOME': str(workspace('0'*32)),
           'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': '/dev/null',
           'GIT_TERMINAL_PROMPT': '0', 'GIT_AUTHOR_NAME': 'GptClaw',
           'GIT_AUTHOR_EMAIL': 'gptclaw@users.noreply.github.com',
           'GIT_COMMITTER_NAME': 'GptClaw', 'GIT_COMMITTER_EMAIL': 'gptclaw@users.noreply.github.com',
           'GIT_AUTHOR_DATE': '2000-01-01T00:00:00+0000', 'GIT_COMMITTER_DATE': '2000-01-01T00:00:00+0000'}
    command = ['git', '-c', 'core.hooksPath=/dev/null', '-c', 'core.fsmonitor=false',
               '-c', 'credential.helper=', '-c', 'commit.gpgsign=false', '-c', 'protocol.file.allow=never',
               '-c', 'protocol.ext.allow=never', '-c', 'http.followRedirects=false', '-c', 'http.proxy=', '-C', str(root), *args]
    auth = api.git_environment() if api else contextlib.nullcontext(({}, ()))
    try:
        with auth as (extra, fds):
            result = subprocess.run(command, env={**env, **extra}, pass_fds=fds, input=input_bytes,
                                    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=90)
        require(result.returncode == 0, 'repository-recovery')
        require(len(result.stdout) <= 2*1024*1024, 'repository-recovery')
        return result.stdout
    except (OSError, subprocess.TimeoutExpired):
        raise app.AppError('repository-recovery') from None


def inventory(root):
    result = {}
    for path in sorted(root.rglob('*')):
        rel = path.relative_to(root)
        if '.git' in rel.parts: continue
        app.safe(path)
        info = path.lstat()
        require(info.st_uid == os.getuid() and not path.is_symlink(), 'repository-drift')
        if path.is_dir(): continue
        require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and info.st_size <= 2*1024*1024, 'repository-drift')
        require(not any(part in {'node_modules', '.env', '.ssh', '.aws', '.npmrc', '.gptclaw-cache'}
                        or part.startswith('.env.') for part in rel.parts), 'repository-drift')
        result[rel.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    require(len(result) <= 200 and result, 'repository-drift')
    return result


def bootstrap(receipt):
    root = workspace(receipt['operation_id'])/'source'
    root.mkdir(mode=0o700)
    (root/'README.md').write_text('# ' + receipt['plan']['repository'] + '\n\nPrivate application setup is in progress. Review the initial pull request.\n')
    git(root, 'init', '--initial-branch=main', '--template=')
    git(root, 'add', '--', 'README.md')
    git(root, 'commit', '-m', 'Initialize private application review base')
    receipt['bootstrap_sha'] = git(root, 'rev-parse', 'HEAD').decode().strip()
    receipt['bootstrap_inventory'] = inventory(root)
    receipt['local_phase'] = 'bootstrap'
    persist(receipt)


def starter(receipt):
    root = workspace(receipt['operation_id'])/'source'
    require(inventory(root) == receipt['bootstrap_inventory'], 'repository-drift')
    release, contents = templates.resolve('nextjs', '1.0.0')
    generated = workspace(receipt['operation_id'])/'generated'
    # Generate first; retain an interrupted staging outcome rather than overwrite.
    templates.generate(generated, receipt['plan']['repository'], release, contents)
    git(root, 'checkout', '-b', receipt['plan']['branches']['head'])
    for path in sorted(generated.rglob('*')):
        if path.is_file():
            out = root/path.relative_to(generated)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(path.read_bytes())
    extra = '\n\nRepository: https://github.com/' + ACCOUNT + '/' + receipt['plan']['repository'] + '\nDefault branch: main. Use codex/ branches and pull requests; never bypass main protection.\n'
    if receipt.get('protection_waiver'):
        extra = extra.replace('never bypass main protection.', 'the owner explicitly waived main branch protection for this repository; PR review remains the workflow, with no server enforcement claim.')
    with (root/'AGENTS.md').open('a') as out: out.write(extra)
    adaptation = {'schema_version': 1, 'operation_id': receipt['operation_id'],
                  'repository': ACCOUNT+'/'+receipt['plan']['repository'],
                  'template': receipt['plan']['template'],
                  'main_protection': 'owner-waived' if receipt.get('protection_waiver') else 'verified',
                  'guidance_sha256': hashlib.sha256((root/'AGENTS.md').read_bytes()).hexdigest()}
    app.save(root/'.gptclaw/repository-bootstrap.json', adaptation)
    # Track only the reviewed inventory, never git add . or unrelated files.
    files = list(inventory(root))
    git(root, 'add', '--', *files)
    git(root, 'commit', '-m', 'Add reviewed private application starter')
    receipt['starter_sha'] = git(root, 'rev-parse', 'HEAD').decode().strip()
    receipt['source_inventory'] = inventory(root)
    receipt['local_phase'] = 'starter'
    persist(receipt)


def identity(receipt, remote):
    value = receipt['plan']
    require(isinstance(remote, dict) and type(remote.get('id')) is int
            and remote.get('id') == receipt.get('repository_id')
            and remote.get('full_name') == ACCOUNT+'/'+value['repository']
            and remote.get('owner', {}).get('login') == ACCOUNT
            and remote.get('owner', {}).get('type') == 'User'
            and remote.get('private') is True and remote.get('archived') is False
            and remote.get('description') == value['description']
            and remote.get('permissions', {}).get('admin') is True, 'repository-drift')


def sha_ref(api, value, branch):
    result = api.request('GET', prefix(value)+'/git/ref/heads/'+branch, missing=True)
    if result is None: return None
    require(result.get('ref') == 'refs/heads/'+branch and result.get('object', {}).get('type') == 'commit', 'repository-drift')
    sha = result['object'].get('sha')
    require(isinstance(sha, str) and re.fullmatch('[a-f0-9]{40}', sha), 'repository-drift')
    return sha


def protection_readback(value):
    require(isinstance(value, dict), 'repository-drift')
    reviews = value.get('required_pull_request_reviews', {})
    require(isinstance(reviews, dict) and type(reviews.get('required_approving_review_count')) is int
            and reviews['required_approving_review_count'] == 0
            and reviews.get('dismiss_stale_reviews') is True
            and reviews.get('require_code_owner_reviews') is False
            and reviews.get('require_last_push_approval', False) is False, 'repository-drift')
    for key in ['enforce_admins', 'required_conversation_resolution']:
        require(value.get(key, {}).get('enabled') is True, 'repository-drift')
    for key in ['allow_force_pushes', 'allow_deletions', 'required_linear_history', 'lock_branch']:
        require(value.get(key, {}).get('enabled', False) is False, 'repository-drift')
    require(value.get('required_status_checks') is None and value.get('restrictions') is None, 'repository-drift')
    return {'policy': 'single-owner-pr-v1', 'verified': True,
            'required_approvals': 0, 'enforce_admins': True,
            'conversation_resolution': True, 'force_pushes': False, 'deletions': False}


def environment_readback(value):
    require(isinstance(value, dict) and value.get('deployment_branch_policy') == ENVIRONMENT['deployment_branch_policy']
            and value.get('protection_rules', []) == [], 'repository-drift')
    return {'deployment_branch_policy': ENVIRONMENT['deployment_branch_policy'], 'verified': True}


def publish_starter(api, receipt, root):
    """Content-addressed objects then exclusive ref creation; never update a ref."""
    value = receipt['plan']; base = prefix(value)
    tree = []
    for name in sorted(receipt['source_inventory']):
        blob = api.request('POST', base+'/git/blobs',
                           {'content': base64.b64encode((root/name).read_bytes()).decode(), 'encoding': 'base64'})
        expected = git(root, 'hash-object', '--', name).decode().strip()
        require(blob.get('sha') == expected, 'repository-drift')
        tree.append({'path': name, 'mode': '100644', 'type': 'blob', 'sha': expected})
    remote_tree = api.request('POST', base+'/git/trees', {'tree': tree})
    expected_tree = git(root, 'rev-parse', receipt['starter_sha']+'^{tree}').decode().strip()
    require(remote_tree.get('sha') == expected_tree, 'repository-drift')
    who = {'name': 'GptClaw', 'email': 'gptclaw@users.noreply.github.com', 'date': '2000-01-01T00:00:00Z'}
    commit = api.request('POST', base+'/git/commits', {'message': 'Add reviewed private application starter\n',
             'tree': expected_tree, 'parents': [receipt['bootstrap_sha']], 'author': who, 'committer': who})
    require(commit.get('sha') == receipt['starter_sha'], 'repository-drift')
    api.request('POST', base+'/git/refs', {'ref': 'refs/heads/'+value['branches']['head'], 'sha': receipt['starter_sha']})


def references(api, value):
    result = []
    for ref in value['secret_references']:
        scope, name = ref['scope'], ref['name']
        path = prefix(value) + ('/actions/secrets/' if scope == 'repository'
                               else '/environments/'+scope+'/secrets/') + name
        metadata = api.request('GET', path, missing=True)
        if metadata is not None: require(metadata.get('name') == name, 'repository-drift')
        result.append({**ref, 'state': 'metadata-verified' if metadata else 'pending-provisioning'})
    return result


def find_pr(api, receipt):
    value = receipt['plan']
    query = urllib.parse.urlencode({'state': 'all', 'head': ACCOUNT+':'+value['branches']['head'],
                                   'base': 'main', 'per_page': 100})
    matches = api.request('GET', prefix(value)+'/pulls?'+query)
    require(isinstance(matches, list) and len(matches) <= 1, 'repository-drift')
    if not matches: return None
    pr = matches[0]
    require(pr.get('state') == 'open' and pr.get('merged_at') is None
            and pr.get('head', {}).get('sha') == receipt['starter_sha']
            and pr.get('head', {}).get('ref') == value['branches']['head']
            and pr.get('head', {}).get('repo', {}).get('id') == receipt['repository_id']
            and pr.get('base', {}).get('sha') == receipt['bootstrap_sha']
            and pr.get('base', {}).get('ref') == 'main'
            and pr.get('base', {}).get('repo', {}).get('id') == receipt['repository_id']
            and type(pr.get('number')) is int and pr['number'] > 0, 'repository-drift')
    return {'number': pr['number'], 'url': 'https://github.com/'+ACCOUNT+'/'+value['repository']+'/pull/'+str(pr['number'])}


def observe(receipt, api):
    value = receipt['plan']; base = prefix(value)
    remote = api.request('GET', base, missing=True)
    if receipt.get('repository_id') is None:
        return {'candidate_repository_id': remote.get('id') if isinstance(remote, dict) else None,
                'reconciliation': 'explicit repository ID confirmation required; never adopted by name alone'}
    identity(receipt, remote)
    main = sha_ref(api, value, 'main')
    head = sha_ref(api, value, value['branches']['head'])
    require(main is None or main == receipt.get('bootstrap_sha'), 'repository-drift')
    require(head is None or head == receipt.get('starter_sha'), 'repository-drift')
    if receipt.get('main_published'): require(main == receipt['bootstrap_sha'], 'repository-drift')
    if receipt.get('branch_published'): require(head == receipt['starter_sha'], 'repository-drift')
    if receipt.get('protection_waiver'):
        require(not receipt.get('protection_verified'), 'repository-drift')
        policy = {'verified': False, 'state': 'owner-waived', 'repository_id': receipt['repository_id']}
    else:
        policy = api.request('GET', base+'/branches/main/protection', missing=True) if main else None
        if policy is not None: policy = protection_readback(policy)
        if receipt.get('protection_verified'): require(policy is not None, 'repository-drift')
    envs = {}
    for name in value['environments']:
        actual = api.request('GET', base+'/environments/'+name, missing=True)
        if actual is not None: envs[name] = environment_readback(actual)
        if name in receipt.get('environment_readback', {}): require(actual is not None, 'repository-drift')
    pr = find_pr(api, receipt) if receipt.get('starter_sha') else None
    if receipt.get('pull_request'): require(pr == receipt['pull_request'], 'repository-drift')
    return {'main': main, 'head': head, 'protection': policy, 'environments': envs, 'pull_request': pr,
            'default_branch': remote.get('default_branch')}


def status(operation, api=None):
    receipt = read_receipt(operation)
    # Status is observation-only: no locks/journal timestamp changes.
    result = {**receipt, 'state': receipt['state']}
    if api:
        result['actor'] = api.actor()
        result['remote_observation'] = observe(receipt, api)
    return result


def apply(value, api, create_only=False):
    validate_plan(value, vacant=True)
    operation = value['operation_id']
    with app.locked('repository-'+value['repository']), app.locked('create-'+hashlib.sha256(value['destination'].encode()).hexdigest()):
        root = workspace(operation)
        require(not root.exists(), 'repository-recovery')
        actor = api.actor()
        require(api.request('GET', prefix(value), missing=True) is None, 'conflict')
        root.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        require(root.parent.stat().st_uid == os.getuid() and stat.S_IMODE(root.parent.stat().st_mode) == 0o700, 'path')
        root.mkdir(mode=0o700)
        receipt = {'schema_version': 1, 'operation_id': operation, 'plan': value,
                   'state': 'in-progress', 'actor': actor, 'repository_id': None,
                   'ongoing_git_access': 'pending-per-repository-credential',
                   'retained_source': str(root/'source'), 'intent': None}
        persist(receipt)
        return run(receipt, api, create_only=create_only)


def resume(operation, api, repository_id=None, create_only=False, allow_unprotected_main=False):
    receipt = read_receipt(operation); value = receipt['plan']
    with app.locked('repository-'+value['repository']), app.locked('create-'+hashlib.sha256(value['destination'].encode()).hexdigest()):
        receipt = read_receipt(operation)
        if allow_unprotected_main:
            require(receipt['repository_id'] is not None and not receipt.get('protection_verified')
                    and not value['environments'], 'repository-policy')
            receipt['protection_waiver'] = {'repository_id': receipt['repository_id'],
                'account': ACCOUNT, 'authorized_by': 'explicit-owner-request', 'at': timestamp(),
                'scope': 'this-operation-only; no protection removal or visibility change'}
            persist(receipt)
        if repository_id is not None:
            require(type(repository_id) is int and repository_id > 0 and receipt['repository_id'] is None
                    and receipt.get('intent') == 'create-repository', 'repository-recovery')
            remote = api.request('GET', prefix(value))
            receipt['repository_id'] = repository_id
            identity(receipt, remote)
            persist(receipt)
        return run(receipt, api, create_only=create_only)


def run(receipt, api, create_only=False):
    value = receipt['plan']; base = prefix(value); root = workspace(receipt['operation_id'])/'source'
    url = 'https://github.com/'+ACCOUNT+'/'+value['repository']+'.git'
    def intent(step):
        receipt['intent'] = step; receipt['state'] = 'in-progress'; persist(receipt)
    try:
        receipt['actor'] = api.actor()
        if receipt['repository_id'] is None:
            require(receipt['intent'] != 'create-repository', 'repository-recovery')
            require(api.request('GET', base, missing=True) is None, 'conflict')
            intent('create-repository')
            remote = api.request('POST', '/user/repos', {'name': value['repository'], 'private': True,
                 'description': value['description'], 'auto_init': False, 'has_wiki': False,
                 'has_projects': False, 'allow_auto_merge': False})
            receipt['repository_id'] = remote.get('id')
            # A creation-only token may lack admin: bind minimum returned identity now;
            # full identity/admin verification is mandatory before configuration.
            require(type(receipt['repository_id']) is int and remote.get('full_name') == ACCOUNT+'/'+value['repository']
                    and remote.get('private') is True and remote.get('description') == value['description'], 'repository-drift')
            receipt['intent'] = None; persist(receipt)
        if create_only:
            receipt['state'] = 'operator-required'
            receipt['pending'] = ['repository-specific administration/contents/PR credential; resume the same operation']
            persist(receipt); return receipt
        observed = observe(receipt, api)
        destination = Path(value['destination'])
        if (not receipt.get('published_local') and receipt.get('intent') == 'publish-local'
                and not root.exists() and destination.is_dir()):
            require(inventory(destination) == receipt.get('source_inventory'), 'repository-drift')
            require(git(destination, 'rev-parse', 'HEAD').decode().strip() == receipt.get('starter_sha'), 'repository-drift')
            receipt['published_local'] = True; receipt['retained_source'] = str(destination); persist(receipt)
        if receipt.get('published_local'):
            require(destination.is_dir() and inventory(destination) == receipt['source_inventory'], 'repository-drift')
            require(git(destination, 'rev-parse', 'HEAD').decode().strip() == receipt['starter_sha'], 'repository-drift')
        else:
            require(not destination.exists() and not destination.is_symlink(), 'conflict')
        if not receipt.get('local_phase'):
            require(not root.exists(), 'repository-recovery')
            intent('local-bootstrap'); bootstrap(receipt)
        if receipt['local_phase'] == 'bootstrap':
            require(inventory(root) == receipt['bootstrap_inventory'], 'repository-drift')
        if receipt['local_phase'] == 'starter' and not receipt.get('published_local'):
            require(inventory(root) == receipt['source_inventory'], 'repository-drift')
            require(git(root, 'rev-parse', 'HEAD').decode().strip() == receipt['starter_sha'], 'repository-drift')
        # Reobserve after creating local SHAs and before each remote write.
        observed = observe(receipt, api)
        if observed['main'] is None:
            intent('publish-main')
            git(root, 'push', url, receipt['bootstrap_sha']+':refs/heads/main', api=api)
            observed = observe(receipt, api)
        require(observed['main'] == receipt['bootstrap_sha'], 'repository-drift')
        receipt['main_published'] = True; persist(receipt)
        if observed['default_branch'] != 'main':
            intent('default-branch'); api.request('PATCH', base, {'default_branch': 'main'})
            observed = observe(receipt, api)
            require(observed['default_branch'] == 'main', 'repository-drift')
        if not receipt.get('protection_waiver'):
            if observed['protection'] is None:
                require(not receipt.get('protection_verified'), 'repository-drift')
                intent('protect-main'); api.request('PUT', base+'/branches/main/protection', PROTECTION)
                observed = observe(receipt, api)
            require(observed['protection'] is not None, 'repository-drift')
            receipt['protection_verified'] = observed['protection']; persist(receipt)
        if receipt['local_phase'] == 'bootstrap':
            intent('generate-starter'); starter(receipt)
        observed = observe(receipt, api)
        if observed['head'] is None:
            intent('publish-starter')
            publish_starter(api, receipt, root)
            observed = observe(receipt, api)
        require(observed['head'] == receipt['starter_sha'], 'repository-drift')
        receipt['branch_published'] = True; persist(receipt)
        for name in value['environments']:
            observed = observe(receipt, api)
            if name not in observed['environments']:
                intent('environment-'+name); api.request('PUT', base+'/environments/'+name, ENVIRONMENT)
                observed = observe(receipt, api)
            receipt['environment_readback'] = observed['environments']; persist(receipt)
        receipt['secret_reference_readback'] = references(api, value); persist(receipt)
        observed = observe(receipt, api)
        if observed['pull_request'] is None:
            # Query by operation-owned head first; after response loss resume finds it.
            intent('initial-pr')
            api.request('POST', base+'/pulls', {'title': 'Review private application starter',
                'head': value['branches']['head'], 'base': 'main',
                'body': 'Exact starter '+value['template']['id']+'@'+value['template']['version']+
                    '. Review manifest, guidance and dependency/toolchain pins. Local quality checks remain required; no CI workflow or deployment is implied.'})
            observed = observe(receipt, api)
        require(observed['pull_request'] is not None, 'repository-recovery')
        receipt['pull_request'] = observed['pull_request']; persist(receipt)
        if not receipt.get('published_local'):
            require(inventory(root) == receipt['source_inventory'], 'repository-drift')
            # Add an unauthenticated remote; ongoing auth handoff stays pending.
            existing = git(root, 'remote').decode().splitlines()
            require(existing in ([], ['origin']), 'repository-drift')
            if not existing: git(root, 'remote', 'add', 'origin', url)
            require(git(root, 'remote', 'get-url', 'origin').decode().strip() == url, 'repository-drift')
            intent('publish-local')
            templates.publish(root, destination)
            receipt['published_local'] = True; receipt['retained_source'] = str(destination); persist(receipt)
        final = observe(receipt, api)
        require(final['default_branch'] == 'main', 'repository-drift')
        receipt['remote_readback'] = final; receipt['intent'] = None; receipt['last_error'] = None
        receipt['state'] = 'repository-ready'
        receipt['pending'] = ['ongoing per-repository Git credential', 'initial PR review/merge',
                              'starter quality/runtime checks']
        persist(receipt)
        return receipt
    except (app.AppError, OSError, ValueError, KeyError, TypeError) as error:
        receipt['last_error'] = error.code if isinstance(error, app.AppError) else 'repository-recovery'
        receipt['state'] = 'recovery-required'
        persist(receipt)
        raise app.AppError('repository-recovery') from None
