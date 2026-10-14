"""Bounded Metro runtime copies and exact owned inactive-copy cleanup."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import time
import uuid

import private_apps as app
import metro_spike as spike
import metro_state as states
import project_worktrees as worktrees

MAX_SOURCES = 1024*1024*1024
MAX_ARTIFACTS = 10*1024*1024
MAX_ENTRIES = 65536
MAX_COPIES = 128
RETENTION_SECONDS = 7*86400
MAX_PRUNE_COPIES = 32
MAX_PRUNE_RECORDS = 64
START_RESERVE = 65536


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def base(project):
    import project_mobile
    project_mobile.identities(project)
    return app.safe(app.STORE/'metro'/project)


def names(path, maximum, code='conflict'):
    result = []
    with spike.directory(path=path) as parent, os.scandir(parent) as entries:
        for entry in entries:
            result.append(entry.name)
            app.need(len(result) <= maximum, code)
    return result


def usage(project):
    """Count only no-follow owned runtime files; never inspect project data."""
    path = base(project)
    result = {'source_bytes': 0, 'artifact_bytes': 0, 'entries': 0}
    if not path.exists():
        return result
    def walk(parent, prefix='', depth=0):
        app.need(depth <= 36, 'conflict')
        with os.scandir(parent) as entries:
            for entry in entries:
                name = entry.name
                result['entries'] += 1
                app.need(result['entries'] <= MAX_ENTRIES, 'conflict')
                info = os.stat(name, dir_fd=parent, follow_symlinks=False)
                app.need(info.st_uid == os.getuid(), 'path')
                relative = prefix+'/'+name if prefix else name
                if stat.S_ISDIR(info.st_mode):
                    with spike.directory(parent=parent, name=name) as child:
                        walk(child, relative, depth+1)
                else:
                    app.need(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, 'path')
                    field = 'source_bytes' if relative.startswith('sources/') else 'artifact_bytes'
                    result[field] += info.st_size
    with spike.directory(path=path) as parent:
        walk(parent)
    return result


def source_bytes(root, inventory):
    total = 0
    with spike.directory(path=root) as parent:
        for relative, expected in inventory.items():
            data = spike.relative_bytes(parent, relative)
            app.need(hashlib.sha256(data).hexdigest() == expected, 'conflict')
            total += len(data)
    app.need(total <= spike.MAX_SOURCE, 'invalid')
    return total


def admit(project, additional):
    app.need(type(additional) is int and 0 <= additional <= spike.MAX_SOURCE, 'invalid')
    observed = usage(project)
    sources = base(project)/'sources'
    app.need(not sources.exists() or len(names(sources, MAX_COPIES, 'metro-capacity')) < MAX_COPIES, 'metro-capacity')
    history = base(project)/'history'
    app.need(not history.exists() or len(names(history, 4096, 'metro-capacity')) < 4096, 'metro-capacity')
    app.need(observed['source_bytes']+additional <= MAX_SOURCES
             and observed['artifact_bytes']+START_RESERVE <= MAX_ARTIFACTS
             and observed['entries']+2*spike.MAX_FILES+32 <= MAX_ENTRIES, 'metro-capacity')
    return observed


def marker_path(project, generation):
    app.need(isinstance(generation, str) and states.HEX32.fullmatch(generation), 'conflict')
    return app.safe(base(project)/'view-owners'/(generation+'.json'))


def fingerprint(view):
    # A runtime copy has an exact filtered shape, with empty mount placeholders.
    with spike.directory(path=view) as parent:
        entries = set(names(view, 16))
        app.need(spike.ROOT_FILES <= entries
                 and entries <= spike.ROOT_FILES | spike.ROOT_DIRS | {'node_modules', '.expo'}, 'conflict')
        for name in ['node_modules', '.expo']:
            with spike.directory(parent=parent, name=name) as child:
                app.need(not os.listdir(child), 'conflict')
    inventory = spike.source_inventory(view)
    return {'directory_identity': worktrees.owned(view),
            'source_digest': digest(inventory),
            'source_bytes': source_bytes(view, inventory)}


def seal(value, inventory):
    states.validate(value)
    view = app.safe(base(value['project'])/'sources'/value['generation'])
    proof = fingerprint(view)
    app.need(proof['source_digest'] == digest(inventory), 'conflict')
    marker = {'schema_version': 1, 'project': value['project'], 'root': value['root'],
              'canonical_key': value['canonical_key'], 'generation': value['generation'],
              'created_at': value['started_at'], **proof}
    path = marker_path(value['project'], value['generation'])
    app.need(not path.exists(), 'conflict')
    path.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
    app.save(path, marker)
    return marker


def marker_record(value):
    marker = app.read_json(marker_path(value['project'], value['generation']))
    if marker is None:
        return None
    fields = {'schema_version', 'project', 'root', 'canonical_key', 'generation',
              'created_at', 'directory_identity', 'source_digest', 'source_bytes'}
    app.need(isinstance(marker, dict) and set(marker) == fields
             and type(marker['schema_version']) is int and marker['schema_version'] == 1
             and states.number(marker['created_at']) and marker['created_at'] == value['started_at']
             and all(marker[key] == value[key] for key in ['project', 'root', 'canonical_key', 'generation']),
             'conflict')
    app.need(type(marker['source_bytes']) is int and 0 <= marker['source_bytes'] <= spike.MAX_SOURCE
             and isinstance(marker['source_digest'], str) and states.HEX64.fullmatch(marker['source_digest'])
             and isinstance(marker['directory_identity'], list) and len(marker['directory_identity']) == 2
             and all(type(n) is int and n >= 0 for n in marker['directory_identity']), 'conflict')
    return marker


def proof(value):
    marker = marker_record(value)
    if marker is None:
        return None
    view = app.safe(base(value['project'])/'sources'/value['generation'])
    actual = fingerprint(view)
    app.need(all(marker[key] == actual[key] for key in actual), 'conflict')
    return marker


def candidates(current):
    """Current, unresolved, edited and pre-marker copies are never selected."""
    root = base(current['project'])
    sources = app.safe(root/'sources')
    selected, retained = [], []
    if not sources.exists():
        return selected, retained
    generations = sorted(names(sources, MAX_COPIES))
    for generation in generations:
        if generation == current['generation']:
            retained.append({'generation': generation, 'reason': 'current'})
            continue
        if not states.HEX32.fullmatch(generation):
            retained.append({'reason': 'unknown-copy'})
            continue
        old = app.read_json(app.safe(root/'history'/(generation+'.json')))
        if old is None:
            retained.append({'generation': generation, 'reason': 'missing-receipt'})
            continue
        states.validate(old)
        app.need(old['generation'] == generation and old['project'] == current['project']
                 and old['root'] == current['root'] and old['canonical_key'] == current['canonical_key'],
                 'conflict')
        if old['phase'] not in {'stopped', 'expired', 'failed'} or old['observations']['process']['state'] != 'down':
            retained.append({'generation': generation, 'reason': 'unresolved'})
            continue
        marker = proof(old)
        if marker is None:
            retained.append({'generation': generation, 'reason': 'missing-marker'})
            continue
        if len(selected) >= MAX_PRUNE_COPIES:
            retained.append({'generation': generation, 'reason': 'next-batch'})
            continue
        selected.append({'generation': generation, 'source_bytes': marker['source_bytes'],
                         'source_digest': marker['source_digest'],
                         'directory_identity': marker['directory_identity']})
    return selected, retained


def retired_records(current, selected):
    """Retire only known inactive receipts/markers/diagnostics after seven days."""
    root = base(current['project'])
    history = app.safe(root/'history')
    if not history.exists():
        return []
    filenames = sorted(names(history, 4096, 'metro-capacity'))
    selected = {item['generation'] for item in selected}
    retired = []
    for name in filenames:
        generation = name.removesuffix('.json')
        if name != generation+'.json' or not states.HEX32.fullmatch(generation) or generation == current['generation']:
            continue
        path = history/name
        old = states.validate(app.read_json(path))
        app.need(old['generation'] == generation and old['project'] == current['project']
                 and old['root'] == current['root'] and old['canonical_key'] == current['canonical_key'], 'conflict')
        stamp = max(old['expires_at'], old['observations']['process']['observed_at'] or old['started_at'])
        if (old['phase'] not in {'stopped', 'expired', 'failed'}
                or old['observations']['process']['state'] != 'down'
                or time.time()-stamp < RETENTION_SECONDS):
            continue
        marker = marker_record(old)
        if marker is None:
            continue
        if (root/'sources'/generation).exists() and generation not in selected:
            continue
        paths = [path, marker_path(current['project'], generation)]
        failure = root/('failure-'+generation+'.json')
        if failure.exists():
            record = app.read_json(failure)
            app.need(isinstance(record, dict) and set(record) == {'schema_version', 'generation', 'stage', 'code'}
                     and type(record['schema_version']) is int and record['schema_version'] == 1
                     and record['generation'] == generation
                     and isinstance(record['stage'], str) and isinstance(record['code'], str)
                     and record['stage'] in {'admission', 'audit', 'network', 'sdk', 'proxy', 'supervision',
                                            'proxy-shutdown', 'owned-cleanup'}
                     and record['code'] in set(app.MESSAGES) | {'security-or-source-admission'}, 'conflict')
            paths.append(failure)
        if len(retired)+len(paths) > MAX_PRUNE_RECORDS:
            break
        for candidate in paths:
            body = app.read_json(candidate)
            retired.append({'path': str(candidate.relative_to(root)), 'digest': digest(body)})
    return retired


def prune_plan(root):
    import metro_sessions
    root, source = app.target(root)
    app.need(source['schema_version'] == 6, 'mobile-unsupported')
    identity = worktrees.canonical(root)
    current = metro_sessions.load(identity['project'], root)
    app.need(current is not None and current['canonical_key'] == identity['key'], 'conflict')
    metro_sessions.assert_stopped(root, current['project'])
    observed = usage(current['project'])
    selected, retained = candidates(current)
    proposal = {'schema_version': 1, 'project': current['project'], 'generation': current['generation'],
                'canonical_key': identity['key'], 'usage': observed, 'copies': selected,
                'retained': retained, 'retired_records': retired_records(current, selected),
                'scope': 'inactive-generated-source-copies-and-aged-owned-metadata'}
    return root, current, {**proposal, 'plan_digest': digest(proposal), 'changed': False, 'state': 'prune-planned'}


def prune(root, apply=False, confirm_plan=None):
    import metro_sessions
    root, current, proposal = prune_plan(root)
    if not apply:
        return proposal
    spike.require_operator()
    app.need(confirm_plan == proposal['plan_digest'], 'conflict')
    app.need(shutil.rmtree.avoids_symlink_attacks, 'setup')
    with app.locked(current['project']):
        _, current, checked = prune_plan(root)
        app.need(checked['plan_digest'] == confirm_plan, 'conflict')
        for item in checked['copies']:
            generation = item['generation']
            view = app.safe(base(current['project'])/'sources'/generation)
            quarantine = app.safe(base(current['project'])/('prune-'+generation+'-'+uuid.uuid4().hex))
            # Move first; a racing replacement is retained, never recursively erased.
            os.rename(view, quarantine)
            try:
                actual = fingerprint(quarantine)
                app.need(all(actual[key] == item[key] for key in actual), 'conflict')
                shutil.rmtree(quarantine)
            except (app.AppError, OSError):
                raise app.AppError('metro-prune-recovery') from None
        for item in checked['retired_records']:
            path = app.safe(base(current['project'])/item['path'])
            quarantine = app.safe(base(current['project'])/('prune-record-'+uuid.uuid4().hex+'.json'))
            os.rename(path, quarantine)
            try:
                app.need(digest(app.read_json(quarantine)) == item['digest'], 'conflict')
                quarantine.unlink()
            except (app.AppError, OSError):
                raise app.AppError('metro-prune-recovery') from None
        return {**checked, 'changed': bool(checked['copies'] or checked['retired_records']), 'state': 'pruned'}
