"""Read-only quality smoke checks against an existing owned development service."""
import contextlib
import json
from pathlib import Path
import re
import time
import urllib.parse
import urllib.request

import private_apps as app


def core():
    import project_quality_core
    return project_quality_core


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        raise app.AppError('health')


def check(root, take_lock=True):
    root, contract = app.target(root)
    app.need((root/'quality.json').is_file() and not (root/'quality.json').is_symlink(), 'invalid')
    q = core(); c = q.config(root)
    slug = contract['project']['id']
    app.need(contract['schema_version'] not in (5, 6, 9), 'mobile-unsupported')
    with (app.locked(slug) if take_lock else contextlib.nullcontext()):
        state = app.state_for(slug)
        app.need(state and state['root'] == str(root) and state['phase'] == 'ready', 'health')
        if contract['schema_version'] in (3, 4, 8):
            import project_groups as groups
            children = groups.children(root, contract)
            component = 'web' if 'web' in children else 'api'
            service = app.state_for(state['components'][component])
            app.need(service is not None and app.object_owned('container', service['name'], service['token']), 'conflict')
            port = service['port']
        else:
            app.need(app.object_owned('container', state['name'], state['token']), 'conflict')
            active, ready = app.inspect_service(state, contract)
            app.need(active and ready, 'health'); port = state['port']
        app.need(type(port) is int and port in app.PORTS, 'conflict')
        revision = q.source_digest(root); activation = state['operation_id']
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
        prefix = '/projects/'+slug
        checks = []
        def fetch(port_, path, kind):
            app.need(path.startswith(prefix+'/') and not re.search(r'[\x00-\x20\\]', path), 'invalid')
            with opener.open('http://127.0.0.1:'+str(port_)+path, timeout=5) as response:
                payload = response.read(2*1024*1024+1)
                app.need(response.status == 200 and len(payload) <= 2*1024*1024, 'health')
            checks.append({'check': kind, 'state': 'passed'})
            return payload
        api = c['template'].split('@')[0] in {'fastapi', 'fastify', 'fastapi-postgres'}
        health = contract['components'][component]['service']['health']['path'] if contract['schema_version'] in (3, 4, 8) else contract['service']['health']['path']
        # Direct readiness and the shared private ingress are separate assertions.
        fetch(port, health, 'service readiness')
        fetch(app.INGRESS_PORT, health, 'private ingress readiness')
        route = '/api/docs' if contract['schema_version'] == 8 else '/docs/' if c['template'].startswith('fastify@') else '/docs' if api else '/'
        document = fetch(app.INGRESS_PORT, prefix+route, 'routed document').decode('utf8', 'replace')
        scripts = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', document, re.I)
        app.need(bool(scripts), 'health')
        for path in scripts[:4]:
            parsed = urllib.parse.urlsplit(path)
            app.need(not parsed.scheme and not parsed.netloc and not parsed.fragment and parsed.path.startswith(prefix+'/'), 'invalid')
            fetch(app.INGRESS_PORT, parsed.path+('?' + parsed.query if parsed.query else ''), 'owned document asset')
        if api or contract['schema_version'] in (3, 4):
            path = '/api/v1/notes?limit=1' if contract['schema_version'] in (3, 4, 8) else '/api/v1/examples?limit=1'
            data = json.loads(fetch(app.INGRESS_PORT, prefix+path, 'read-only API journey'))
            app.need(isinstance(data.get('items'), list), 'health')
        app.need(revision == q.source_digest(root), 'conflict')
        current = app.state_for(slug)
        app.need(current and current['operation_id'] == activation and current['phase'] == 'ready', 'conflict')
        return {'state': 'passed', 'project': slug, 'revision': revision, 'activation': activation,
                'vantage': 'managed host via private ingress', 'checks': checks,
                'client_acceptance': 'separate independent client/device evidence required'}


def observe(root, seconds, interval=1):
    """Bounded opt-in source observer; never starts/restarts/mutates a service."""
    app.need(type(seconds) is int and 0 <= seconds <= 28800, 'invalid')
    app.need(type(interval) in (int, float) and .5 <= interval <= 30, 'invalid')
    root, contract = app.target(root)
    app.need(contract['schema_version'] not in (5, 6, 9), 'mobile-unsupported')
    q = core()
    try: q.config(root)
    except (q.GateError, OSError, ValueError): raise app.AppError('invalid') from None
    last = None; latest = None; deadline = time.monotonic()+seconds
    while True:
        signature = q.source_digest(Path(root))
        if signature != last:
            try:
                report = check(root)
            except (app.AppError, q.GateError, OSError, ValueError):
                report = {'state': 'failed', 'revision': signature, 'error': 'Smoke did not establish acceptance; runtime/source are retained'}
            print(json.dumps(report), flush=True);last = signature; latest = report
        if time.monotonic() >= deadline:
            return 0 if latest and latest['state'] == 'passed' else 1
        time.sleep(min(interval, max(0, deadline-time.monotonic())))


def configure(root, enabled):
    root, contract = app.target(root)
    app.need(type(enabled) is bool and (root/'quality.json').is_file(), 'invalid')
    path = root/'.gptclaw/quality-smoke.json'
    if path.exists() or path.is_symlink():
        existing = app.read_json(path)
        app.need(set(existing) == {'schema_version', 'project', 'enabled'} and type(existing['schema_version']) is int and existing['schema_version'] == 1 and existing['project'] == contract['project']['id'] and type(existing['enabled']) is bool, 'conflict')
    app.save(path, {'schema_version': 1, 'project': contract['project']['id'], 'enabled': enabled})


def after_start(root):
    """Opt-in evidence only; no HTTP in projects that have not enabled this hook."""
    path = Path(root)/'.gptclaw/quality-smoke.json'
    if not path.exists() and not path.is_symlink():
        return None
    try:
        value = app.read_json(path)
        app.need(set(value) == {'schema_version', 'project', 'enabled'} and type(value['schema_version']) is int and value['schema_version'] == 1 and type(value['enabled']) is bool, 'invalid')
        if not value['enabled']:
            return None
        app.need(app.target(root)[1]['project']['id'] == value['project'], 'conflict')
        return check(root, take_lock=False)
    except Exception:
        return {'state': 'failed', 'error': 'Post-start smoke pending; service and data retained'}
