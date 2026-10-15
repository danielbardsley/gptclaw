"""Exact private Serve plans and transport observations; never administer Tailscale."""
from copy import deepcopy
import hashlib
import http.client
import json
from pathlib import Path
import time
from urllib.parse import urlsplit

import private_apps as app
import metro_state as states
import project_worktrees as worktrees

MAX_CONFIG = 32768
HEALTH_PATH = '/_gptclaw/metro-health'


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def config():
    output = app.command(['tailscale', 'serve', 'status', '--json'], timeout=5).stdout
    app.need(len(output.encode()) <= MAX_CONFIG, 'conflict')
    try:
        value = json.loads(output)
    except ValueError:
        raise app.AppError('conflict') from None
    validate_config(value)
    return value


def validate_config(value):
    app.need(isinstance(value, dict) and set(value) <= {'TCP', 'Web', 'AllowFunnel'}
             and len(json.dumps(value).encode()) <= MAX_CONFIG, 'conflict')
    for key in ['TCP', 'Web', 'AllowFunnel']:
        app.need(isinstance(value.get(key, {}), dict), 'conflict')
    app.need(all(flag is False for flag in value.get('AllowFunnel', {}).values()), 'conflict')
    return value


def binding(value):
    states.validate(value)
    parsed = urlsplit(value['origin'])
    slot = (value['metro_port']-18600)//2
    app.need(parsed.port == 8443+slot, 'conflict')
    return str(parsed.port), parsed.netloc, {
        'Handlers': {'/': {'Proxy': 'http://127.0.0.1:'+str(value['proxy_port'])}}
    }


def record_path(project):
    import project_mobile
    project_mobile.identities(project)
    return app.safe(app.STORE/'metro'/project/'route.json')


def validate_record(record):
    keys = {'schema_version', 'project', 'root', 'canonical_key', 'origin',
            'metro_port', 'proxy_port', 'baseline', 'plan_digest', 'recorded_at'}
    app.need(isinstance(record,dict) and type(record.get('schema_version')) is int
             and record['schema_version'] in {1,2},'conflict')
    if record['schema_version']==2:keys.add('previous')
    app.need(set(record) == keys
             and states.number(record['recorded_at'])
             and isinstance(record['plan_digest'], str)
             and states.HEX64.fullmatch(record['plan_digest']), 'conflict')
    import metro_sessions
    import project_mobile
    project_mobile.identities(record['project'])
    entries = metro_sessions.slots()
    item = entries.get(record['project'])
    app.need(item is not None and record['root'] == item['root']
             and record['canonical_key'] == item['canonical_key']
             and type(record['metro_port']) is int and record['metro_port'] == 18600+2*item['slot']
             and type(record['proxy_port']) is int and record['proxy_port'] == record['metro_port']+1,
             'conflict')
    from metro_protocol import origin
    app.need(origin(record['origin']) == record['origin']
             and urlsplit(record['origin']).port == 8443+item['slot'], 'conflict')
    validate_config(record['baseline'])
    parsed=urlsplit(record['origin'])
    if record['schema_version']==1:
        app.need(parsed.scheme=='https','conflict')
    else:
        app.need(parsed.scheme=='http','conflict')
        previous=record['previous']
        if previous is not None:
            app.need(isinstance(previous,dict) and previous.get('schema_version')==1,'conflict')
            validate_record(previous)
            app.need(all(previous[k]==record[k] for k in ['project','root','canonical_key','metro_port','proxy_port','baseline'])
                     and urlsplit(previous['origin']).netloc==parsed.netloc,'conflict')
    payload = {k: record[k] for k in keys-{'plan_digest', 'recorded_at'}}
    app.need(digest(payload) == record['plan_digest'], 'conflict')
    return record


def records():
    import metro_sessions
    result = []
    for project in metro_sessions.slots():
        value = app.read_json(record_path(project))
        if value is not None:
            app.need(isinstance(value, dict) and value.get('project') == project, 'conflict')
            result.append(validate_record(value))
    return result


def subtract_owned(value, approvals):
    """Remove only exact reviewed listener bindings; preserve every other byte."""
    result = deepcopy(validate_config(value))
    for record in approvals:
        port = str(urlsplit(record['origin']).port)
        authority = urlsplit(record['origin']).netloc
        expected = {'Handlers': {'/': {'Proxy': 'http://127.0.0.1:'+str(record['proxy_port'])}}}
        tcp = result.get('TCP', {}).get(port)
        web = result.get('Web', {}).get(authority)
        allowed={'HTTP'} if record['schema_version']==2 else {'HTTPS'}
        if record.get('previous') is not None:allowed.add('HTTPS')
        app.need((tcp is None and web is None)
                 or (isinstance(tcp,dict) and len(tcp)==1 and set(tcp)<=allowed
                     and next(iter(tcp.values())) is True and web==expected),'conflict')
        if tcp is not None:
            del result['TCP'][port]
            del result['Web'][authority]
    return {key: item for key, item in result.items() if item or key == 'AllowFunnel'}


def payload(value, baseline, previous=None):
    return {'schema_version': value['schema_version'],
            **({'previous':previous} if value['schema_version']==2 else {}),
            'project': value['project'], 'root': value['root'],
            'canonical_key': value['canonical_key'], 'origin': value['origin'],
            'metro_port': value['metro_port'], 'proxy_port': value['proxy_port'],
            'baseline': baseline}


def plan(root, apply=False, confirm_plan=None):
    """Default is read-only. Apply records a reviewed plan, never a Serve change."""
    import metro_sessions
    root, source = app.target(root)
    app.need(source['schema_version'] in (6,9), 'mobile-unsupported')
    identity = worktrees.canonical(root)
    value = metro_sessions.load(identity['project'], root)
    app.need(value is not None and value['canonical_key'] == identity['key'], 'conflict')
    parsed=urlsplit(value['origin'])
    app.need(value['origin'] == parsed.scheme+'://'+app.node_identity()+':'+str(8443+(value['metro_port']-18600)//2),
             'conflict')
    port, authority, web = binding(value)
    current = config()
    approved = records()
    old = next((r for r in approved if r['project'] == value['project']), None)
    if old is None:
        app.need(port not in current.get('TCP', {}) and authority not in current.get('Web', {}),
                 'conflict')
        baseline = current
    else:
        app.need(all(old[k] == value[k] for k in ['root', 'canonical_key', 'metro_port', 'proxy_port'])
                 and urlsplit(old['origin']).netloc==authority,
                 'conflict')
        baseline = old['baseline']
        app.need(digest(subtract_owned(current, approved)) == digest(subtract_owned(baseline, approved)), 'conflict')
    previous=old if old is not None and old['schema_version']==1 else old.get('previous') if old else None
    proposal = payload(value, baseline, previous)
    key = digest(proposal)
    validate_record({**proposal, 'plan_digest': key, 'recorded_at': time.time()})
    target = 'http://127.0.0.1:'+str(value['proxy_port'])
    flag='--http=' if parsed.scheme=='http' else '--https='
    result = {'schema_version': 2 if value['schema_version']==2 or old and old['schema_version']==2 else 1, 'project': value['project'], 'plan_digest': key,
              'existing_config_digest': digest(current),
              'origin': value['origin'], 'state': 'planned', 'changed': False,
              'operator_add': ['sudo', 'tailscale', 'serve', '--bg', flag+port, target],
              'operator_remove': ['sudo', 'tailscale', 'serve', '--bg', flag+port, 'off'],
              'access_policy': 'operator-confirmation-required',
              'physical_client_acceptance': 'unverified'}
    changing=old is not None and old['origin']!=value['origin']
    if changing:
        old_flag='--http=' if urlsplit(old['origin']).scheme=='http' else '--https='
        result['operator_replace']=[['sudo','tailscale','serve',old_flag+port,'off'],result['operator_add']]
        result['operator_rollback']=[['sudo','tailscale','serve',flag+port,'off'],
                                     ['sudo','tailscale','serve','--bg',old_flag+port,target]]
        result['record_after_replacement']=value['schema_version']==1
    if apply:
        import metro_spike
        metro_spike.require_operator()
        app.need(confirm_plan == key, 'conflict')
        with app.locked('registry'):
            # Re-read under lock; never record a stale config or lease.
            app.need(config() == current, 'conflict')
            validate_record({**proposal, 'plan_digest': key, 'recorded_at': time.time()})
            path = record_path(value['project'])
            existing = app.read_json(path)
            app.need(existing is None or existing == old, 'conflict')
            if old is None or old['plan_digest']!=key:
                # HTTP conversion retains the exact original HTTPS record in schema 2.
                # Restoring schema 1 waits until the owned HTTP listener is removed/replaced.
                if changing and value['schema_version']==1:
                    tcp=current.get('TCP',{}).get(port)
                    app.need(tcp is None or isinstance(tcp,dict) and set(tcp)=={'HTTPS'} and tcp['HTTPS'] is True,'conflict')
                path.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
                if old is not None:
                    history=app.safe(path.parent/('route-history-'+old['plan_digest']+'.json'))
                    stored=app.read_json(history)
                    app.need(stored is None or stored==old,'conflict')
                    if stored is None:app.save(history,old)
                app.save(path, {**proposal, 'plan_digest': key, 'recorded_at': time.time()})
                result['changed'] = True
        result['state'] = 'operator-required'
    return result


def health(value):
    """Fixed node/origin; HTTPS uses default trust, HTTP stays on the owned tailnet route."""
    parsed = urlsplit(value['origin'])
    app.need(parsed.hostname==app.node_identity(),'conflict')
    connection_type=http.client.HTTPSConnection if parsed.scheme=='https' else http.client.HTTPConnection
    connection = connection_type(parsed.hostname, parsed.port, timeout=3)
    try:
        connection.request('GET', HEALTH_PATH, headers={'Accept': 'application/json',
                                                      'Connection': 'close'})
        response = connection.getresponse()
        app.need(response.status == 200
                 and sum(len(k)+len(v)+4 for k, v in response.getheaders()) <= 16384
                 and response.getheader('Content-Encoding') in {None, 'identity'}, 'health')
        body = response.read(4097)
        app.need(len(body) <= 4096, 'health')
        data = json.loads(body)
        app.need(data == {'adapter': 'metro-v1', 'project': value['project'],
                          'generation': value['generation'], 'expires_at': value['expires_at']},
                 'health')
        return True
    except (OSError, ValueError, http.client.HTTPException):
        raise app.AppError('health') from None
    finally:
        connection.close()


def observe(value):
    states.validate(value)
    stamp = max(time.time(), value['started_at'])
    try:
        approved = records()
        record = next((r for r in approved if r['project'] == value['project']), None)
        if record is None:
            return {'state': 'pending', 'observed_at': stamp}
        app.need(all(record[k] == value[k] for k in ['root', 'canonical_key', 'origin', 'metro_port', 'proxy_port']),
                 'conflict')
        current = config()
        app.need(digest(subtract_owned(current, approved)) == digest(subtract_owned(record['baseline'], approved)),
                 'conflict')
        port, authority, web = binding(value)
        if port not in current.get('TCP', {}) and authority not in current.get('Web', {}):
            return {'state': 'pending', 'observed_at': stamp}
        protocol='HTTP' if urlsplit(value['origin']).scheme=='http' else 'HTTPS'
        tcp=current.get('TCP',{}).get(port)
        app.need(isinstance(tcp,dict) and set(tcp)=={protocol} and tcp[protocol] is True
                 and current.get('Web', {}).get(authority) == web, 'conflict')
        app.need(value['phase'] == 'running' and time.time() < value['expires_at'], 'health')
        health(value)
        return {'state': 'verified', 'observed_at': stamp}
    except app.AppError:
        return {'state': 'failed', 'observed_at': stamp}
