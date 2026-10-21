#!/usr/bin/env python3
"""Portable QLT gates. Application language commands run in bounded containers.

Metadata/report operations use the Python standard library, need no host packages,
and never import project source. This is a development quality tool, not a sandbox.
"""
from __future__ import annotations

import argparse
import ast
import datetime as dt
import gzip
import hashlib
import json
import math
import platform
import os
import selectors
import signal
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request
import uuid

VERBS = ('format', 'lint', 'typecheck', 'test', 'build', 'security', 'verify')
IGNORE = {'.git', '.cache', 'node_modules', '.venv', '.next', '.expo', '.gptclaw-cache',
          '.gptclaw-build', 'dist', 'coverage', '__pycache__', '.mypy_cache', '.pytest_cache', '.ruff_cache'}
SECRET = re.compile(r'(?:AKIA[A-Z0-9]{16}|gh[pousr]_[A-Za-z0-9_]{20,}|'
                    r'tskey-(?:auth|api)-[A-Za-z0-9-]{10,}|'
                    r'-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----)')
PRIVATE = re.compile(r'https?://[^\s/"<>]+\.(?:ts\.net|internal)(?::\d+)?', re.I)
MAX_FILE = 2 * 1024 * 1024


class GateError(ValueError):
    """A check failed or required evidence is unavailable."""


def need(value, message):
    if not value:
        raise GateError(message)


def pairs(items):
    result = {}
    for key, value in items:
        need(key not in result, 'Duplicate JSON key')
        result[key] = value
    return result


def read_json(path):
    need(not path.is_symlink() and path.is_file(), 'Missing or symlinked JSON input')
    need(path.stat().st_size <= MAX_FILE, 'JSON input too large')
    return json.loads(path.read_text(), object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(GateError('Nonfinite JSON')))


def relative(root, name, directory=False):
    need(isinstance(name, str) and len(name) <= 200, 'Invalid relative path')
    p = PurePosixPath(name)
    need(not p.is_absolute() and '..' not in p.parts and name == p.as_posix(), 'Unsafe path')
    path = root / name
    current = path
    while current != root:
        need(not current.is_symlink(), 'Symlinked path')
        current = current.parent
    need(path.resolve().is_relative_to(root.resolve()), 'Path outside project')
    if directory:
        need(path.is_dir(), 'Missing component directory')
    return path


def files(root):
    """Bounded source inventory without following directory or file symlinks."""
    result = []
    for directory, names, entries in os.walk(root, followlinks=False):
        names[:] = sorted(n for n in names if n not in IGNORE)
        for name in names:
            need(not (Path(directory)/name).is_symlink(), 'Symlinked source directory')
        for name in sorted(entries):
            p = Path(directory)/name
            if p.relative_to(root).as_posix() in {'src/config/backend.generated.ts', '.gptclaw/backend.local.json'}:
                continue  # Reviewed ignored public binding outputs, never uploaded as source/artifacts.
            need(not p.is_symlink(), 'Symlinked source file')
            if p.suffix not in {'.pyc', '.tsbuildinfo'} and p.name not in {'.coverage', 'coverage.json', 'next-env.d.ts'}:
                result.append(p)
        need(len(result) <= 10000, 'Source file count exceeded')
    return result


def source_snapshot(root):
    result = {}
    for p in files(root):
        name = p.relative_to(root).as_posix()
        if name.startswith('checks/output/'):
            continue
        need(p.stat().st_size <= 16*MAX_FILE, 'Source file too large')
        result[name] = hashlib.sha256(p.read_bytes()).hexdigest()
    return result


def source_digest(root):
    digest = hashlib.sha256()
    for name, value in source_snapshot(root).items():
        digest.update(name.encode()+b'\0'+bytes.fromhex(value))
    return digest.hexdigest()


def policy(root):
    findings = []
    for p in files(root):
        name = p.relative_to(root).as_posix()
        if p.name in {'.env', 'auth.json', 'terraform.tfstate'} or p.name.startswith('.env.'):
            findings.append(name+': forbidden authentication/environment file')
        if p.stat().st_size > MAX_FILE:
            continue
        text = p.read_bytes().decode('utf-8', errors='replace')
        if SECRET.search(text) or PRIVATE.search(text):
            findings.append(name+': credential or private-origin pattern (value redacted)')
    need(not findings, '\n'.join(findings))
    return {'state': 'passed', 'scanner': 'bounded credential/private-origin patterns'}


def config(root):
    c = read_json(root/'quality.json')
    need(set(c) == {'schema_version', 'template', 'components', 'integration', 'budgets'},
         'Unknown/missing quality fields')
    need(type(c['schema_version']) is int and c['schema_version'] == 1, 'Unsupported quality version')
    need(isinstance(c['template'], str) and re.fullmatch(r'[a-z][a-z0-9-]+@\d+\.\d+\.\d+', c['template']), 'Invalid template')
    need(isinstance(c['components'], dict) and 1 <= len(c['components']) <= 3, 'Invalid components')
    roots = []
    for name, component in c['components'].items():
        need(re.fullmatch(r'[a-z][a-z0-9-]{0,31}', name), 'Invalid component name')
        need(set(component) == {'root', 'stack', 'recipe', 'commands'}, 'Unknown component fields')
        path = relative(root, component['root'], True)
        need(not any(path == old or path.is_relative_to(old) or old.is_relative_to(path) for old in roots), 'Overlapping components')
        roots.append(path)
        need(component['stack'] in {'node', 'python'}, 'Unknown stack')
        recipe = relative(root, component['recipe'])
        need(recipe.is_file(), 'Missing pinned recipe')
        bases = re.findall(r'(?im)^FROM\s+(\S+)', recipe.read_text())
        need(bases and all(re.fullmatch(r'[^\s]+@sha256:[a-f0-9]{64}', v) for v in bases), 'Unpinned toolchain image')
        need(set(component['commands']) == set(VERBS), 'Missing quality command')
        for vector in component['commands'].values():
            need(isinstance(vector, list) and 1 <= len(vector) <= 20 and all(isinstance(x, str) and 0 < len(x) <= 200 and not re.search(r'[\x00-\x1f]', x) for x in vector), 'Invalid command vector')
    need(c['integration'] is None or c['integration'] == 'checks/verify.py', 'Unsupported integration adapter')
    need(isinstance(c['budgets'], dict), 'Invalid budgets')
    return c


def workflow_policy(value):
    need(set(value.get('on', {})) == {'pull_request', 'push'}, 'Unsafe/missing workflow events')
    need(value.get('permissions') == {'contents': 'read'}, 'Workflow token must be read only')
    need(value.get('concurrency', {}).get('cancel-in-progress') is True, 'Missing concurrency bound')
    jobs = value.get('jobs', {})
    need(set(jobs) == {'quality', 'required'}, 'Unexpected required-check graph')
    need(jobs['required'].get('needs') == ['quality'] and jobs['required'].get('if') == 'always()', 'Missing aggregate')
    need("needs.quality.result" in json.dumps(jobs['required']), 'Aggregate must check dependency status')
    for job in jobs.values():
        need(0 < job.get('timeout-minutes', 0) <= 45, 'Unbounded job')
        need('permissions' not in job and 'secrets' not in job, 'Unexpected job privilege')
        for step in job.get('steps', []):
            if 'uses' in step:
                need(re.fullmatch(r'actions/[a-z-]+@[a-f0-9]{40}', step['uses']), 'Unpinned action')
            need('${{ secrets.' not in json.dumps(step), 'Secret in source-quality job')
            if step.get('uses', '').startswith('actions/checkout@'):
                need(step.get('with', {}).get('persist-credentials') is False, 'Persisted checkout credential')
            if step.get('uses', '').startswith('actions/upload-artifact@'):
                need(step.get('with', {}).get('retention-days') == 7 and step.get('with', {}).get('path') == '.gptclaw-cache/quality/report.json', 'Unsafe artifact selection')
            if step.get('uses', '').startswith('actions/cache@'):
                key = step.get('with', {}).get('key', '')
                need(all(word in key for word in ['runner.os', 'runner.arch', 'hashFiles', 'github.ref']), 'Incomplete cache identity')
                need('restore-keys' not in step.get('with', {}), 'Broad cache fallback')
    return {'state': 'passed'}


def updater_policy(value, c):
    need(set(value) == {'version', 'updates'} and value['version'] == 2, 'Invalid updater')
    expected = {('github-actions', '/')}
    for v in c['components'].values():
        expected.add(('pip' if v['stack'] == 'python' else 'npm', '/' if v['root'] == '.' else '/'+v['root']))
    actual = set()
    limit = 0
    for item in value['updates']:
        actual.add((item['package-ecosystem'], item['directory']))
        need(item['schedule'] == {'interval': 'weekly'}, 'Unexpected updater cadence')
        count = item['open-pull-requests-limit']
        need(type(count) is int and 0 < count <= 5, 'Invalid PR cap')
        limit += count
        need(item.get('ignore') and item.get('groups') and 'registries' not in item, 'Missing update boundaries')
    need(actual == expected and len(actual) == len(value['updates']) and limit <= 5, 'Updater coverage/cap mismatch')
    return {'state': 'passed', 'open_pr_cap': limit}


def resolve_refs(document):
    """Verify bundled local OpenAPI references, rejecting remote resolution."""
    def visit(value):
        if isinstance(value, dict):
            if '$ref' in value:
                ref = value['$ref']
                need(isinstance(ref, str) and ref.startswith('#/'), 'External/invalid API reference')
                found = document
                for bit in ref[2:].split('/'):
                    need(isinstance(found, dict), 'Invalid API reference')
                    bit = bit.replace('~1', '/').replace('~0', '~')
                    need(bit in found, 'Missing API reference')
                    found = found[bit]
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)
    need(isinstance(document, dict) and str(document.get('openapi', '')).startswith('3.') and isinstance(document.get('paths'), dict) and document['paths'], 'Missing API contract')
    visit(document)


def contract_changes(old, new):
    """Conservative compatibility diff; integration tests cover runtime meaning."""
    resolve_refs(old)
    resolve_refs(new)
    changes = []
    # Conservatively flag schema edits as review-worthy; descriptions/examples can change.
    def semantic(value):
        if isinstance(value, dict):
            return {k: semantic(v) for k, v in value.items() if k not in {'description', 'summary', 'example', 'examples'}}
        if isinstance(value, list):
            return [semantic(v) for v in value]
        return value
    for path, operations in old['paths'].items():
        for method, operation in operations.items():
            if method not in {'get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace'}:
                continue
            current = new['paths'].get(path, {}).get(method)
            if current is None:
                changes.append(method.upper()+' '+path+': removed')
            elif semantic(operation) != semantic(current):
                changes.append(method.upper()+' '+path+': changed; consumer review required')
    previous = old.get('components', {}).get('schemas', {})
    current = new.get('components', {}).get('schemas', {})
    for name, value in previous.items():
        if semantic(current.get(name)) != semantic(value):
            changes.append('schema '+name+': changed; consumer review required')
    return changes


def migration_assessment(root, paths, assessment):
    digest = hashlib.sha256()
    findings = []
    for name in sorted(paths):
        path = relative(root, name)
        data = path.read_bytes()
        digest.update(name.encode()+b'\0'+data)
        if path.suffix == '.py':
            tree = ast.parse(data)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    func = node.func
                    name_ = func.attr if isinstance(func, ast.Attribute) else func.id if isinstance(func, ast.Name) else ''
                    if name_ in {'drop_table', 'drop_column', 'alter_column', 'execute', 'exec', 'eval'}:
                        findings.append(name+': '+name_)
        elif re.search(rb'\b(DROP|TRUNCATE|ALTER|DELETE)\b', data, re.I):
            findings.append(name+': SQL operation needs review')
    need(set(assessment) == {'source_digest', 'risk', 'recovery', 'reviewer', 'backup_required'}, 'Incomplete migration assessment')
    need(assessment['source_digest'] == digest.hexdigest(), 'Stale migration assessment')
    need(assessment['risk'] in {'additive', 'destructive', 'opaque'}, 'Invalid migration risk')
    need(not findings or assessment['risk'] in {'destructive', 'opaque'}, 'Unacknowledged destructive/opaque migration')
    need(isinstance(assessment['recovery'], str) and len(assessment['recovery']) >= 30 and assessment['backup_required'] is True, 'Missing backup/recovery strategy')
    need(isinstance(assessment['reviewer'], str) and len(assessment['reviewer']) >= 3, 'Missing reviewer')
    return {'state': 'passed', 'static_analysis': 'advisory only', 'findings': findings,
            'managed_backup': 'separate target-bound SPEC-026 prerequisite'}


def compare_performance(baseline, sample, budgets):
    need(set(baseline) == set(sample) == {'profile', 'revision', 'metrics'}, 'Invalid measurement report')
    need(baseline['profile'] == sample['profile'], 'Incomparable measurement profile')
    need(isinstance(sample['profile'], dict) and all(k in sample['profile'] for k in ('runner', 'toolchain', 'workload', 'cache')), 'Incomplete measurement profile')
    need(bool(baseline['revision']) and bool(sample['revision']), 'Missing measurement revision')
    need(bool(budgets) and set(sample['metrics']) == set(baseline['metrics']) == set(budgets), 'Missing metric/baseline')
    results = {}
    for name, rule in budgets.items():
        need(set(rule) == {'unit', 'absolute', 'regression'}, 'Invalid budget fields')
        a, b = baseline['metrics'][name], sample['metrics'][name]
        for number in (a, b, rule['absolute'], rule['regression']):
            need(type(number) in (int, float) and math.isfinite(number) and number >= 0, 'Invalid metric/limit')
        need(a > 0 and rule['absolute'] > 0 and rule['unit'] in {'bytes', 'ms', 'MiB'}, 'Invalid baseline/unit')
        limit = min(rule['absolute'], a*(1+rule['regression']))
        results[name] = {'value': b, 'baseline': a, 'limit': limit, 'unit': rule['unit'], 'state': 'passed' if b <= limit else 'failed'}
    return {'state': 'passed' if all(v['state'] == 'passed' for v in results.values()) else 'failed', 'metrics': results}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise GateError('Smoke redirects are refused')


def smoke(root, target, inspect=None):
    """Read-only bounded probe against an explicit owned loopback test service.

    Real private ingress is checked separately by the existing reviewed runner;
    this adapter never resolves arbitrary user-supplied external hostnames.
    """
    need(set(target) == {'project', 'revision', 'activation', 'container', 'base_url', 'paths', 'expires'}, 'Invalid smoke target')
    need(re.fullmatch(r'[a-z][a-z0-9-]{0,47}', target['project']), 'Invalid project identity')
    need(isinstance(target['activation'], str) and re.fullmatch(r'[a-f0-9]{32}', target['activation']), 'Invalid activation')
    need(dt.datetime.fromisoformat(target['expires']) > dt.datetime.now(dt.timezone.utc), 'Expired smoke target')
    need(target['revision'] == source_digest(root), 'Stale source revision')
    url = urllib.parse.urlsplit(target['base_url'])
    need(url.scheme == 'http' and url.hostname == '127.0.0.1' and url.port and not url.username and not url.password and not url.query and not url.fragment, 'Smoke target must be owned loopback fixture')
    need(url.path == '/projects/'+target['project']+'/', 'Wrong project prefix')
    need(isinstance(target['container'], str) and re.fullmatch(r'gptclaw-quality-[a-z0-9-]+', target['container']), 'Invalid fixture container')
    need(inspect is not None, 'Owned container inspection is required')
    info = inspect(target['container'])
    need(info.get('Config', {}).get('Labels', {}).get('com.gptclaw.quality') == target['activation'], 'Smoke container ownership mismatch')
    need(info.get('State', {}).get('Running') is True, 'Fixture container is not running')
    ports = info.get('NetworkSettings', {}).get('Ports', {})
    need(any(v and any(p.get('HostIp') == '127.0.0.1' and str(p.get('HostPort')) == str(url.port) for p in v) for v in ports.values()), 'Smoke port ownership mismatch')
    paths = target['paths']
    need(isinstance(paths, list) and 1 <= len(paths) <= 12, 'Invalid smoke paths')
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    results = []
    for probe in paths:
        need(set(probe) == {'path', 'contains'} and isinstance(probe['contains'], str) and 0 < len(probe['contains']) <= 200, 'Invalid smoke assertion')
        part = probe['path']
        need(isinstance(part, str) and not part.startswith(('/', '.')) and not re.search(r'[?#:\\\x00-\x20]', part) and '..' not in part.split('/'), 'Unsafe smoke path')
        with opener.open(target['base_url']+part, timeout=5) as response:
            payload = response.read(MAX_FILE+1)
            need(response.status == 200 and len(payload) <= MAX_FILE and probe['contains'].encode() in payload, 'Smoke content mismatch')
        results.append({'path': part, 'state': 'passed'})
    need(source_digest(root) == target['revision'], 'Source changed during smoke')
    return {'state': 'passed', 'vantage': 'loopback fixture', 'revision': target['revision'], 'activation': target['activation'], 'checks': results}


def git(root, *args):
    result = subprocess.run(['git', '-C', str(root), *args], capture_output=True, text=True, timeout=15)
    need(result.returncode == 0, 'Git metadata unavailable')
    return result.stdout.strip()


def release_notes(root, value):
    need(set(value) == {'product', 'version', 'audience', 'baseline', 'target', 'changes'}, 'Invalid notes input')
    for key in ('baseline', 'target'):
        need(re.fullmatch(r'[a-f0-9]{40}', value[key]), 'Release range must use immutable full commits')
        need(git(root, 'rev-parse', value[key]+'^{commit}') == value[key], 'Invalid commit')
    need(value['baseline'] != value['target'], 'Empty release range')
    git(root, 'merge-base', '--is-ancestor', value['baseline'], value['target'])
    commits = set(git(root, 'rev-list', value['baseline']+'..'+value['target']).splitlines())
    need(all(isinstance(value[k], str) and re.fullmatch(r'[A-Za-z0-9 ._-]{1,100}', value[k]) for k in ('product', 'version', 'audience')), 'Invalid release metadata')
    sections = {}; pending = []; seen = set()
    for change in value['changes']:
        need(set(change) == {'commit', 'status', 'category', 'summary', 'evidence'}, 'Invalid change fields')
        need(change['commit'] in commits and change['commit'] not in seen, 'Change outside range or duplicated')
        seen.add(change['commit'])
        need(change['status'] in {'accepted', 'pending'}, 'Invalid acceptance status')
        need(change['category'] in {'Added', 'Fixed', 'Compatibility and migration', 'Known limitations'}, 'Invalid category')
        summary = change['summary']; evidence = change['evidence']
        need(isinstance(summary, str) and 1 <= len(summary) <= 500 and '\n' not in summary and not SECRET.search(summary) and not PRIVATE.search(summary) and not re.search(r'[<>\[\]`]', summary), 'Unsafe release text')
        need(isinstance(evidence, str) and re.fullmatch(r'[A-Za-z0-9._/-]+\.md', evidence), 'Evidence must be a repository Markdown path')
        # Evidence must exist in the immutable target, not merely in the worktree.
        text = git(root, 'show', value['target']+':'+evidence)
        accepted = bool(re.search(r'(?im)^Status:\s*accepted\s*$', text))
        if change['status'] != 'accepted' or not accepted:
            pending.append(change['commit'])
            continue
        sections.setdefault(change['category'], []).append('- '+summary+' ('+change['commit'][:12]+'; '+evidence+')')
    need(bool(seen), 'No reviewed changes')
    output = '# '+value['product']+' '+value['version']+' — draft release notes\n\nAudience: '+value['audience']+'\n\nRange: '+value['baseline']+'..'+value['target']+'\n'
    for category in ('Added', 'Fixed', 'Compatibility and migration', 'Known limitations'):
        if category in sections:
            output += '\n## '+category+'\n\n'+'\n'.join(sections[category])+'\n'
    if pending:
        output += '\nReview required: '+str(len(pending))+' unaccepted changes excluded.\n'
    output += '\nDraft only. Project-owner review is required before publication.\n'
    return {'state': 'pending' if pending else 'draft', 'text': output, 'excluded': pending}


def execute(argv, cwd, timeout=600, env=None):
    # Stream with a hard output bound and deadline; never publish an unrestricted log.
    process = subprocess.Popen(argv, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, start_new_session=True)
    tail = bytearray(); total = 0; deadline = time.monotonic()+timeout
    selector = selectors.DefaultSelector(); selector.register(process.stdout, selectors.EVENT_READ)
    success = False
    try:
        while selector.get_map():
            need(time.monotonic() < deadline, 'Command deadline exceeded')
            for key, _ in selector.select(min(1, max(0, deadline-time.monotonic()))):
                chunk = os.read(key.fileobj.fileno(), 65536)
                if not chunk:
                    selector.unregister(key.fileobj); break
                total += len(chunk); need(total <= 16*MAX_FILE, 'Command output exceeded limit')
                tail.extend(chunk); del tail[:-4000]
        code = process.wait(timeout=max(1, deadline-time.monotonic()))
        if code:
            text = tail.decode('utf-8', errors='replace')
            text = PRIVATE.sub('[private origin]', SECRET.sub('[redacted]', text))
            raise GateError('Command failed ('+str(code)+'): '+text)
        success = True
    finally:
        selector.close(); process.stdout.close()
        if not success:
            try: os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError: pass
        if process.poll() is None:
            process.wait()


class Containers:
    def __init__(self, root, engine, c):
        self.root, self.engine, self.config = root, engine, c
        self.images = {}
        self.owner = uuid.uuid4().hex
        self.names = set()
        self.auth = tempfile.TemporaryDirectory(prefix='gptclaw-quality-auth-')
        auth = Path(self.auth.name)
        (auth/'auth.json').write_text('{"auths":{}}\n')
        (auth/'config.json').write_text('{"auths":{}}\n')
        self.env = {**os.environ, 'REGISTRY_AUTH_FILE': str(auth/'auth.json'), 'DOCKER_CONFIG': str(auth), 'GPTCLAW_QUALITY_TOKEN': self.owner}

    def execute(self, argv, cwd, timeout=600):
        return execute(argv, cwd, timeout, env=self.env)

    def image(self, name, component):
        if name not in self.images:
            recipe = relative(self.root, component['recipe'])
            digest = hashlib.sha256(b''.join(p.read_bytes() for p in sorted(recipe.parent.iterdir()) if p.is_file())).hexdigest()[:24]
            image = 'localhost/gptclaw-quality:'+digest
            self.execute([self.engine, 'build', '--quiet', '--label', 'com.gptclaw.quality='+self.owner,
                     '--file', str(recipe), '--tag', image, str(recipe.parent)], self.root)
            self.images[name] = image
        return self.images[name]

    def run(self, name, component, argv, network=True):
        identity = ['--userns=keep-id'] if self.engine == 'podman' else ['--user', f'{os.getuid()}:{os.getgid()}']
        cname = 'gptclaw-quality-'+self.owner+'-'+str(len(self.names))
        self.names.add(cname)
        path = relative(self.root, component['root'], True)
        vector = [self.engine, 'run', '--rm', '--name', cname, '--label', 'com.gptclaw.quality='+self.owner,
                  *identity, '--memory=1536m', '--cpus=1', '--pids-limit=256', '--cap-drop=all',
                  '--security-opt=no-new-privileges', '--volume', str(path)+':/workspace:rw',
                  '--workdir', '/workspace', '--env', 'CI=1', '--env', 'GPTCLAW_PROJECT_ID=quality-fixture',
                  '--env', 'NEXT_TELEMETRY_DISABLED=1', '--env', 'EXPO_NO_TELEMETRY=1',
                  '--env', 'EXPO_NO_DOTENV=1', '--env', 'PYTHONPATH=/workspace/src',
                  '--env', 'UV_PROJECT_ENVIRONMENT=/workspace/.venv', '--env', 'UV_CACHE_DIR=/workspace/.gptclaw-cache/uv']
        if not network:
            vector += ['--network=none']
        self.execute([*vector, self.image(name, component), *argv], self.root, 900)

    def restore(self, name, component):
        if component['stack'] == 'node':
            vector = ['pnpm', 'install', '--frozen-lockfile', '--ignore-scripts', '--no-runtime',
                      '--pm-on-fail=error', '--ignore-pnpmfile', '--registry=https://registry.npmjs.org/',
                      '--store-dir=/workspace/.gptclaw-cache/pnpm']
        else:
            vector = ['uv', 'sync', '--locked', '--all-groups', '--no-install-project', '--no-config',
                      '--no-python-downloads', '--no-managed-python', '--no-build', '--keyring-provider=disabled',
                      '--default-index=https://pypi.org/simple']
        self.run(name, component, vector)

    def browser_smoke(self, benchmark=False):
        if len(self.config['components']) != 1 or not (self.root/'checks/browser.json').exists():
            return None
        name, component = next(iter(self.config['components'].items()))
        if 'expo' in self.config['template']:
            return None
        kind = 'web' if self.config['template'].startswith('nextjs@') else 'fastify' if self.config['template'].startswith('fastify@') else 'fastapi'
        port = '3000' if kind == 'web' else '8000'
        network = 'gptclaw-quality-net-'+self.owner
        service = 'gptclaw-quality-service-'+self.owner
        self.names.add(service)
        cache = self.root/'.gptclaw-cache/quality/browser'
        cache.parent.mkdir(parents=True, exist_ok=True)
        if not cache.exists():
            self.execute([sys.executable, str(self.root/'checks/acquire-browser.py'), str(cache)], self.root, 90)
        browser = 'localhost/gptclaw-quality-browser:'+hashlib.sha256((cache/'Containerfile').read_bytes()+(cache/'playwright.tgz').read_bytes()+(cache/'axe.min.js').read_bytes()).hexdigest()[:24]
        self.execute([self.engine, 'build', '--quiet', '--file', str(cache/'Containerfile'), '--tag', browser, str(cache)], self.root)
        self.execute([self.engine, 'network', 'create', '--internal', '--label', 'com.gptclaw.quality='+self.owner, network], self.root)
        try:
            identity = ['--userns=keep-id'] if self.engine == 'podman' else ['--user', f'{os.getuid()}:{os.getgid()}']
            # Use built source and a bounded, explicit fixture-only request allowance.
            # The published application's default admission policy is unchanged.
            startup = ['pnpm', 'start'] if component['stack'] == 'node' else ['.venv/bin/python', '-c',
                'import uvicorn; from fastapi_app.main import create_app; from fastapi_app.settings import Settings; '
                'uvicorn.run(create_app(Settings(project_id="quality-fixture",request_limit=1000)),host="0.0.0.0",port=8000,access_log=False,proxy_headers=False)']
            started = str(int(time.time()*1000))
            self.execute([self.engine, 'run', '--detach', '--name', service, '--label', 'com.gptclaw.quality='+self.owner,
                     *identity, '--network='+network, '--network-alias=service', '--memory=1536m', '--cpus=1', '--pids-limit=256',
                     '--cap-drop=all', '--security-opt=no-new-privileges', '--volume', str(self.root)+':/workspace:rw', '--workdir=/workspace',
                     '--env', 'GPTCLAW_PROJECT_ID=quality-fixture', '--env', 'GPTCLAW_DEV_ORIGIN=service', '--env', 'PYTHONPATH=/workspace/src', '--env', 'NEXT_TELEMETRY_DISABLED=1',
                     self.image(name, component), *startup], self.root)
            browser_name = 'gptclaw-quality-browser-'+self.owner
            self.names.add(browser_name)
            self.execute([self.engine, 'run', '--rm', '--name', browser_name, '--label', 'com.gptclaw.quality='+self.owner, *identity, '--network='+network, '--memory=1536m', '--cpus=1', '--pids-limit=256', '--cap-drop=all', '--security-opt=no-new-privileges',
                     '--volume', str(self.root/'checks/browser.cjs')+':/checks/probe.cjs:ro', '--volume', str(cache.parent)+':/output:rw', '--env', 'QUALITY_START_MS='+started, '--env', 'QUALITY_BENCHMARK='+('1' if benchmark else '0'), '--env', 'QUALITY_KIND='+kind, '--env', 'QUALITY_PORT='+port,
                     browser, 'node', '/checks/probe.cjs'], self.root, 180)
            sample = read_json(cache.parent/'http-sample.json')
            peak = subprocess.run([self.engine, 'exec', service, 'cat', '/sys/fs/cgroup/memory.peak'], capture_output=True, text=True, timeout=10)
            sample['peak_memory_mib'] = int(peak.stdout.strip())/(1024*1024) if peak.returncode == 0 and peak.stdout.strip().isdigit() else None
            (cache.parent/'http-sample.json').write_text(json.dumps(sample, indent=2)+'\n')
            return {'gate': 'isolated-browser-smoke', 'state': 'passed', 'vantage': 'isolated network', 'measurements': sample}
        finally:
            self.cleanup()
            probe = subprocess.run([self.engine, 'network', 'inspect', network], capture_output=True, text=True, timeout=20)
            if probe.returncode == 0:
                meta = json.loads(probe.stdout)[0]
                need(meta.get('Labels', meta.get('labels', {})).get('com.gptclaw.quality') == self.owner, 'Foreign network refused')
                self.execute([self.engine, 'network', 'rm', network], self.root, 30)

    def close(self):
        try:
            self.cleanup()
        finally:
            self.auth.cleanup()

    def cleanup_integrations(self):
        for kind in ('container', 'network'):
            listed = subprocess.run([self.engine, kind, 'ls', '--filter', 'label=com.gptclaw.check='+self.owner, '--format', '{{.ID}}'], capture_output=True, text=True, timeout=20)
            need(listed.returncode == 0, 'Cannot reconcile owned integration resources')
            for name in listed.stdout.splitlines():
                need(re.fullmatch(r'[a-f0-9]{12,64}', name), 'Invalid integration resource identity')
                probe = subprocess.run([self.engine, kind, 'inspect', name], capture_output=True, text=True, timeout=20)
                need(probe.returncode == 0, 'Integration resource inspection failed')
                info = json.loads(probe.stdout)[0]
                labels = info.get('Config', {}).get('Labels', {}) if kind == 'container' else info.get('Labels', info.get('labels', {}))
                need(labels.get('com.gptclaw.check') == self.owner, 'Foreign integration resource refused')
                self.execute([self.engine, kind, 'rm', *(['--force'] if kind == 'container' else []), name], self.root, 30)

    def cleanup(self):
        # Names are generated by this instance. Verify the label before forced removal.
        for name in self.names:
            probe = subprocess.run([self.engine, 'container', 'inspect', name], capture_output=True, text=True, timeout=20)
            if probe.returncode:
                continue
            info = json.loads(probe.stdout)[0]
            need(info.get('Config', {}).get('Labels', {}).get('com.gptclaw.quality') == self.owner, 'Foreign container refused')
            self.execute([self.engine, 'rm', '--force', name], self.root, 30)


def canonical_contract(document):
    value = json.loads(json.dumps(document))
    # Runtime prefix/origin assertions belong to the independently tested smoke gate.
    value.pop('servers', None)
    return value


def metadata_gates(root, c):
    checks = []
    for name, component in c['components'].items():
        home = relative(root, component['root'], True)
        migrations = sorted(home.glob('migrations/versions/*.py'))
        if migrations:
            paths = [p.relative_to(root).as_posix() for p in migrations]
            assessment = read_json(root/'checks/migration-review.json')
            migration_assessment(root, paths, assessment)
            checks.append({'component': name, 'gate': 'migration-review', 'state': 'passed'})
        generated = home/'.gptclaw-cache/openapi.json'
        contract = home/'contract/openapi.json'
        if generated.exists() and contract.exists():
            current = read_json(generated); accepted = read_json(contract)
            resolve_refs(current); resolve_refs(accepted)
            need(canonical_contract(current) == canonical_contract(accepted), 'OpenAPI output drift; regenerate and review the contract')
            checks.append({'component': name, 'gate': 'contract-drift', 'state': 'passed'})
    return checks


def run_quality(root, action, engine):
    c = config(root)
    before = source_snapshot(root)
    report = {'schema_version': 1, 'template': c['template'], 'source': source_digest(root),
              'vantage': 'generated-container', 'state': 'failed', 'checks': [],
              'recipes': {k: hashlib.sha256(relative(root, v['recipe']).read_bytes()).hexdigest() for k, v in c['components'].items()}}
    runner = Containers(root, engine, c)
    try:
        if action != 'format':
            policy(root)
            workflow_policy(read_json(root/'.github/workflows/quality.yml'))
            updater_policy(read_json(root/'.github/dependabot.yml'), c)
        database = any((relative(root, v['root'])/'migrations').is_dir() for v in c['components'].values())
        for name, component in c['components'].items():
            runner.restore(name, component)
            actions = ('lint', 'typecheck', 'test', 'build', 'security') if action == 'verify' else (action,)
            for gate in actions:
                report['active'] = name+'/'+gate
                print('Quality '+name+'/'+gate, file=sys.stderr, flush=True)
                if gate == 'test' and database and component['stack'] == 'python':
                    need(c['integration'] is not None, 'Database test requires the owned integration adapter')
                    continue  # The adapter provisions an isolated DB and executes the real test gate.
                started = time.monotonic()
                runner.run(name, component, component['commands'][gate], network=gate in {'security', 'build'})
                report['checks'].append({'component': name, 'gate': gate, 'state': 'passed', 'seconds': round(time.monotonic()-started, 3)})
        if action in {'verify', 'test'} and c['integration']:
            try:
                runner.execute([sys.executable, str(relative(root, c['integration'])), '--engine', engine], root, 2400)
            finally:
                runner.cleanup_integrations()
            report['checks'].append({'gate': 'integration', 'state': 'passed'})
        if action == 'verify':
            report['checks'].extend(metadata_gates(root, c))
            smoke_result = runner.browser_smoke()
            if smoke_result:
                report['checks'].append(smoke_result)
            measured = collect_performance(root)
            need(set(measured['metrics']) == set(c['budgets']), 'Required performance metrics are missing')
            for name, value in measured['metrics'].items():
                need(type(value) in (int, float) and math.isfinite(value) and 0 <= value <= c['budgets'][name]['absolute'], 'Absolute performance budget exceeded: '+name)
            report['checks'].append({'gate': 'performance-absolute', 'state': 'passed', 'metrics': measured['metrics'], 'relative_regressions': 'matching calibrated baseline required separately'})
        if action != 'format':
            after = source_snapshot(root)
            changed = sorted(name for name in before.keys() | after.keys() if before.get(name) != after.get(name))
            need(not changed, 'Quality check modified source: '+', '.join(changed[:20]))
        report.pop('active', None)
        report['state'] = 'passed'
        return report
    finally:
        runner.close()
        output = root/'.gptclaw-cache/quality'; output.mkdir(parents=True, exist_ok=True)
        (output/'report.json').write_text(json.dumps(report, indent=2)+'\n')


def collect_performance(root):
    c = config(root)
    metrics = {}
    bundles = []
    for component in c['components'].values():
        home = relative(root, component['root'], True)
        candidates = [home/'.next/static', home/'dist', home/'.gptclaw-build']
        for directory in candidates:
            if directory.is_dir():
                bundles.extend(p for p in directory.rglob('*') if p.suffix in {'.js', '.hbc'} and p.is_file() and not p.is_symlink())
    if bundles:
        need(len(bundles) <= 10000 and sum(p.stat().st_size for p in bundles) <= 128*1024*1024 and all(p.stat().st_size <= 32*1024*1024 for p in bundles), 'Build metrics exceed resource bound')
        metrics['bundle_bytes'] = sum(len(gzip.compress(p.read_bytes(), mtime=0)) for p in bundles)
    sample = root/'.gptclaw-cache/quality/http-sample.json'
    if sample.exists():
        observed = read_json(sample)
        for name in ('latency_ms', 'startup_ms', 'peak_memory_mib'):
            if observed.get(name) is not None:
                metrics[name] = observed[name]
    need(bool(metrics), 'No measured build/runtime metrics; run verify first')
    cpu = Path('/proc/cpuinfo')
    model = next((line.split(':', 1)[1].strip() for line in cpu.read_text().splitlines() if line.startswith('model name')), platform.machine()) if cpu.exists() else platform.machine()
    profile = {'runner': platform.system()+'/'+platform.machine()+'/'+model,
               'toolchain': hashlib.sha256(c['template'].split('@')[0].encode()+json.dumps(c['components'], sort_keys=True).encode()+b''.join(relative(root, v['recipe']).read_bytes() for v in c['components'].values())).hexdigest(),
               'workload': 'isolated one CPU/1536MiB; warm '+str(observed['warmup_ms'] if sample.exists() else 0)+'ms; 3x200 sequential requests; median p95; API fixture allowance 1000/min; '+(observed.get('driver', 'Playwright single-service route') if sample.exists() else 'build assets only'), 'cache': 'warm response; built gzip JS'}
    return {'profile': profile, 'revision': source_digest(root), 'metrics': metrics}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    p.add_argument('action', choices=[*VERBS, 'inspect', 'policy', 'measure', 'benchmark', 'contract', 'migration', 'performance', 'smoke', 'release-notes'])
    p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument('--engine', choices=['docker', 'podman'], default='podman')
    p.add_argument('--input', type=Path); p.add_argument('--baseline', type=Path); p.add_argument('--output', type=Path)
    args = p.parse_args(argv); root = args.root.resolve()
    signal.signal(signal.SIGTERM, lambda *_: (_ for _ in ()).throw(KeyboardInterrupt()))
    try:
        if args.action in VERBS:
            result = run_quality(root, args.action, args.engine)
        elif args.action == 'inspect':
            result = config(root)
        elif args.action == 'policy':
            result = policy(root)
        elif args.action == 'benchmark':
            c = config(root); policy(root)
            need(c['integration'] is not None or (root/'checks/browser.json').exists(), 'Dedicated native runtime benchmarks require a physical-device adapter')
            runner = Containers(root, args.engine, c); observations = []
            try:
                for name, component in c['components'].items():
                    runner.restore(name, component); runner.run(name, component, component['commands']['build'])
                for _ in range(5):
                    if c['integration']:
                        runner.env['GPTCLAW_QUALITY_BENCHMARK'] = '1'
                        try:
                            runner.execute([sys.executable, str(relative(root, c['integration'])), '--engine', args.engine], root, 2400)
                        finally:
                            runner.cleanup_integrations()
                    else:
                        need(runner.browser_smoke(benchmark=True) is not None, 'No HTTP benchmark adapter')
                    observations.append(collect_performance(root))
                result = observations[-1]
                for metric in ('startup_ms', 'latency_ms', 'peak_memory_mib'):
                    values = sorted(v['metrics'][metric] for v in observations if metric in v['metrics'])
                    need(len(values) == 5, 'Incomplete repeated performance samples')
                    result['metrics'][metric] = values[2]
                result['profile']['workload'] += '; five independent starts, median aggregate'
                samples = root/'.gptclaw-cache/quality/benchmark-samples.json'
                samples.parent.mkdir(parents=True, exist_ok=True)
                samples.write_text(json.dumps(observations, indent=2)+'\n')
                need(args.output is not None, '--output is required')
                with args.output.open('x') as output:
                    output.write(json.dumps(result, indent=2)+'\n')
            finally:
                runner.close()
        elif args.action == 'measure':
            result = collect_performance(root)
            need(args.output is not None, '--output is required')
            with args.output.open('x') as output:
                output.write(json.dumps(result, indent=2)+'\n')
        else:
            need(args.input is not None, '--input is required')
            value = read_json(args.input)
            if args.action == 'contract':
                resolve_refs(value)
                changes = contract_changes(read_json(args.baseline), value) if args.baseline else []
                result = {'state': 'failed' if changes else 'passed', 'changes': changes}
            elif args.action == 'migration':
                result = migration_assessment(root, value['paths'], value['assessment'])
            elif args.action == 'performance':
                need(args.baseline is not None, '--baseline is required')
                result = compare_performance(read_json(args.baseline), value, config(root)['budgets'])
            elif args.action == 'smoke':
                def inspect(name):
                    output = subprocess.check_output([args.engine, 'container', 'inspect', name], text=True, timeout=20)
                    return json.loads(output)[0]
                result = smoke(root, value, inspect)
            else:
                result = release_notes(root, value)
                need(args.output is not None, '--output is required')
                text = result.pop('text')
                if args.output.exists():
                    need(args.output.read_text() == text, 'Existing/manual draft differs; choose a new output')
                else:
                    with args.output.open('x') as stream:
                        stream.write(text)
        print(json.dumps(result, sort_keys=True))
        return 1 if result.get('state') in {'failed', 'pending'} else 0
    except (GateError, OSError, KeyError, TypeError, SyntaxError, subprocess.SubprocessError, ValueError, KeyboardInterrupt) as error:
        print(json.dumps({'state': 'failed', 'error': PRIVATE.sub('[private origin]', SECRET.sub('[redacted]', str(error)))[:4500]}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
