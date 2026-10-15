"""Additive owned runtime observation; no lifecycle/repair or project commands."""
import datetime
import contextlib
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import hashlib
import json
import subprocess
import math
import os
from pathlib import Path
import re
import time
import urllib.request

import private_apps as app
from dashboard_inventory import identity, open_directory

SCHEMA_VERSION = 1
STATE_MAP = {'ready':'ready','stopped':'stopped','preparing':'starting','starting':'starting',
             'failed':'failed','degraded':'degraded','unhealthy':'degraded','unpublished':'degraded',
             'recovery-required':'degraded','uninitialized':'stopped'}
HEALTH_MAP = {'ready':'healthy','unhealthy':'unhealthy','unknown':'unknown'}


def unsupported(reason='observation-unavailable'):
    return {'state':'unknown','provider_state':'unknown','health':'unknown','operation_busy':False,
            'reason':reason,'uptime_seconds':None,'uptime_reason':'unavailable',
            'restart_count':None,'restart_reason':'unavailable'}


def timing(obj, active, now):
    if not active:
        return {'uptime_seconds':None,'uptime_reason':'not-applicable',
                'restart_count':None,'restart_reason':'not-applicable','instance':None}
    value={'uptime_seconds':None,'uptime_reason':'unavailable','restart_count':None,
           'restart_reason':'unavailable','instance':None}
    count=obj.get('RestartCount')
    if type(count) is int and 0 <= count <= 2**31-1:
        value.update(restart_count=count,restart_reason=None)
    start=obj.get('State',{}).get('StartedAt')
    identifier=obj.get('Id')
    if not isinstance(start,str) or len(start)>64:
        return value
    if isinstance(identifier,str) and re.fullmatch(r'[0-9a-f]{64}',identifier):
        value['instance']=hashlib.sha256((identifier+'\0'+start).encode()).hexdigest()[:32]
    try:
        # Podman timestamps can contain nanoseconds; datetime uses microseconds.
        parsed=datetime.datetime.fromisoformat(start.replace('Z','+00:00'))
        if parsed.tzinfo is None or not math.isfinite(now):
            raise ValueError
        elapsed=now-parsed.timestamp()
        if not math.isfinite(elapsed) or elapsed < 0:
            value['uptime_reason']='clock-anomaly'
        else:
            value.update(uptime_seconds=int(elapsed),uptime_reason=None)
    except (ValueError,OverflowError):
        value['uptime_reason']='clock-anomaly'
    return value


def owned_inspection(name, token):
    if not app.object_owned('container',name,token):
        return None
    values=app.json_command(['podman','container','inspect',name])
    app.need(isinstance(values,list) and len(values)==1 and isinstance(values[0],dict),'conflict')
    obj=values[0]
    app.need(obj.get('Config',{}).get('Labels',{}).get(app.LABEL)==token,'conflict')
    return obj


def component(root, contract, *, now):
    slug=contract['project']['id']
    receipt=app.state_for(slug)
    if receipt is None:
        name='gptclaw-app-'+slug
        # A missing receipt must not mask an unowned unit/container with that name.
        app.need(not (app.UNITS/(name+'.container')).exists(),'conflict')
        app.need(app.command(['podman','container','exists',name],optional=True).returncode==1,'conflict')
        return {'state':'stopped','provider_state':'never-started','health':'unknown',
                'operation_busy':False,'reason':None,**timing({},False,now)}
    app.need(receipt['root']==str(root),'conflict')
    active, ready=app.inspect_service(receipt,contract)
    obj=owned_inspection(receipt['name'],receipt['token'])
    # Refuse inconsistent resource state instead of treating it as a successful stop.
    app.need(not active or obj is not None,'conflict')
    if obj is not None:
        app.need(type(obj.get('State',{}).get('Running')) is bool,'conflict')
        app.need(obj['State']['Running']==active,'conflict')
    busy=app.object_owned('container',receipt['name']+'-job',receipt['token'])
    provider_state=('ready' if active and ready else 'unhealthy' if active else receipt['phase'])
    inconsistent = not active and receipt['phase']=='ready'
    if inconsistent: provider_state='resource-unavailable'
    return {'state':STATE_MAP.get(provider_state,'unknown'),'provider_state':provider_state,
            'health':'healthy' if ready else 'unhealthy' if active else 'unknown',
            'operation_busy':busy,'reason':'observation-inconsistent' if inconsistent else None,
            **timing(obj or {},active,now)}


def database(root, contract, *, now):
    import project_database as db
    receipt=db.state(contract['project']['id'],root)
    if receipt is None:
        return {'state':'stopped','provider_state':'uninitialized','health':'unknown',
                'operation_busy':False,'reason':None,**timing({},False,now)}
    db.verify_unit(receipt)
    obj=owned_inspection(db.name(receipt),receipt['token'])
    active=bool(obj and obj.get('State',{}).get('Running'))
    if obj is not None:
        app.need(type(obj.get('State',{}).get('Running')) is bool,'conflict')
        actual=obj.get('Image','');actual=actual if actual.startswith('sha256:') else 'sha256:'+actual
        if obj.get('ImageName') == receipt['image']:
            # The creation reference is an exact immutable profile digest, also
            # matched by the verified unit. No mutable tag is accepted here.
            image_matches=True
        else:
            expected=app.command(['podman','image','inspect',receipt['image'],'--format','{{.Id}}']).stdout.strip()
            expected=expected if expected.startswith('sha256:') else 'sha256:'+expected
            image_matches=actual==expected
        app.need(image_matches and not obj.get('HostConfig',{}).get('PortBindings'),'conflict')
    blocked=receipt['blocked'] or bool(receipt['operation'] and receipt['operation']['stage'] in {'failed','unknown'})
    ready=active and not blocked and db.ready(receipt,contract)
    state='recovery-required' if blocked else 'ready' if ready else 'unhealthy' if active else 'stopped'
    return {'state':STATE_MAP[state],'provider_state':state,
            'health':'healthy' if ready else 'unhealthy' if active else 'unknown',
            'operation_busy':bool(receipt['operation'] and receipt['operation']['stage']=='running'),
            'reason':None,**timing(obj or {},active,now)}


READ_LOCK = threading.Lock()
INSPECT_FORMAT = '[{"Id":{{json .ID}},"Image":{{json .Image}},"ImageName":{{json .ImageName}},"RestartCount":{{json .RestartCount}},"State":{"Running":{{json .State.Running}},"StartedAt":{{json .State.StartedAt}}},"Config":{"Labels":{{json .Config.Labels}}},"HostConfig":{"PortBindings":{{json .HostConfig.PortBindings}}}}]'


@contextlib.contextmanager
def cached_reads():
    # Each collector worker observes one project in its own process. Scope and
    # restore this adapter so ordinary CLI/lifecycle commands keep their behavior.
    with READ_LOCK:
        original = app.command
        original_bundle = app.provider_bundle
        original_healthy = app.healthy
        import project_database as db
        original_revision = db.revision
        original_save, original_save_text = app.save, app.save_text
        cache = {}
        def command(argv, timeout=300, optional=False):
            readonly = (argv[:3] in [['podman','container','inspect'], ['podman','container','exists'],
                                    ['podman','network','exists'], ['podman','network','inspect'],
                                    ['podman','image','inspect']]
                        or argv[:3] in [['systemctl','--user','show'], ['systemctl','--user','is-active']]
                        or argv in [['tailscale','status','--json'], ['tailscale','serve','status','--json']]
                        or argv[:2] == ['mountpoint','-q'])
            app.need(readonly, 'conflict')
            key = (tuple(argv), optional)
            if readonly and key in cache:
                return cache[key]
            vector = list(argv)
            if vector[:3] == ['podman','container','exists'] and len(vector)==4 and not vector[3].endswith('-job'):
                inspected = original(['podman','container','inspect',vector[3],'--format',INSPECT_FORMAT],timeout=timeout,optional=True)
                if inspected.returncode == 0:
                    cache[(('podman','container','inspect',vector[3]),False)] = inspected
                    result = subprocess.CompletedProcess(argv,0,'','')
                    cache[key] = result
                    return result
                # Inspect errors alone cannot prove absence; preserve the existing
                # exists protocol to distinguish missing from command failure.
            if vector[:3] == ['podman','container','inspect'] and len(vector)==4:
                # Query only ownership, binding and timing fields; never request
                # raw environment, mounts or other container configuration.
                vector += ['--format', INSPECT_FORMAT]
            result = original(vector, timeout=timeout, optional=optional)
            if readonly:
                cache[key] = result
            return result
        def healthy(receipt, contract):
            # Lifecycle probes may wait five seconds. Dashboard reads must leave
            # room for ownership/timing checks inside the four-second budget.
            service = contract['service']
            bounded = {**contract, 'service': {**service, 'health': {
                **service['health'], 'timeout_seconds': min(
                    service['health']['timeout_seconds'], .5)}}}
            return original_healthy(receipt, bounded)
        def revision(receipt, generation=None):
            # One authenticated read proves connectivity and migration revision.
            # A missing table fails readiness without a second native query.
            value = db.sql(receipt, 'SELECT version_num FROM public.alembic_version;',
                           generation).strip()
            app.need(re.fullmatch(r'[A-Za-z0-9_]{1,32}', value), 'database-schema')
            return value
        def refuse_write(*_, **__):
            raise app.AppError('conflict')
        app.command = command
        app.healthy = healthy
        db.revision = revision
        # verify_unit compares trusted bootstrap bytes. It needs no snapshot
        # publication while observing from source or an installed snapshot.
        app.provider_bundle = lambda: app.REPO
        app.save = app.save_text = refuse_write
        try:
            yield
        finally:
            app.command = original
            app.healthy = original_healthy
            db.revision = original_revision
            app.provider_bundle = original_bundle
            app.save, app.save_text = original_save, original_save_text


def project(root, *, expected=None, clock=time.time):
    with cached_reads():
        return _project(root, expected=expected, clock=clock)


def _project(root, *, expected=None, clock=time.time):
    now=clock()
    fd=open_directory(Path(root))
    try:
        before=identity(os.fstat(fd))
        if expected is not None:
            app.need(tuple(expected['identity'])==before and expected['root']==str(Path(root)),'conflict')
        root, contract=app.target(root)
        slug=contract['project']['id']
        if expected is not None:
            app.need(slug==expected['id'],'conflict')
        if contract['schema_version'] in (6,9):
            import metro_sessions
            from dashboard_metro import project as native_project
            descriptor=metro_sessions.status(root)
            native=native_project(descriptor,slug)
            import expo_go
            from dashboard_go import project as go_project
            try:go=go_project(expo_go.presentation(root,descriptor),slug,native)
            except app.AppError:go=None
            app.need(native is not None,'conflict')
            state=native['state']
            overall='ready' if state=='ready' else 'stopped' if state in {'not-started','stopped','expired'} else 'starting' if state in {'preparing','starting','stopping','loopback-running'} else 'failed' if state=='failed' else 'degraded'
            result={'observation_schema':SCHEMA_VERSION,'provider_version':app.VERSION,'project':slug,
                    'observed_at':now,'components':{},'state':overall,'provider_state':overall,
                    'health':'not-applicable','operation_busy':False,'reason':None,'metro':descriptor,'expo_go':go,
                    'publication':{'state':'unavailable','origin':None},
                    'routes':{'schema_version':1,'project':slug,'app_path':None,'docs_path':None}}
            app.need(identity(Path(root).stat(follow_symlinks=False))==before,'conflict')
            return result
        receipt=app.state_for(slug)
        result={'observation_schema':SCHEMA_VERSION,'provider_version':app.VERSION,'project':slug,
                'observed_at':now,'components':{},'state':'unknown','provider_state':'unknown',
                'health':'unknown','operation_busy':False,'reason':None}
        if contract['schema_version'] in (3,4,8):
            import project_groups as groups
            if receipt:
                app.need(receipt['root']==str(root),'conflict')
            with groups.scope(root,contract) as children:
                with ThreadPoolExecutor(max_workers=3) as pool:
                    futures={pool.submit(component,child,declaration,now=now):name for name,(child,declaration) in children.items()}
                    if contract['schema_version'] in (4,8):
                        futures[pool.submit(database,root,contract,now=now)]='db'
                    for future in as_completed(futures):
                        name=futures[future]
                        try:result['components'][name]=future.result()
                        except app.AppError as error:
                            result['components'][name]=unsupported('ownership-conflict' if error.code in {'conflict','path'} else 'observation-unavailable')
                        except (OSError,ValueError,TypeError,KeyError,AttributeError):
                            result['components'][name]=unsupported('observation-unavailable')
            state='stopped' if receipt is None else receipt['phase']
            healthy=bool(result['components']) and all(c['state']=='ready' and c['health']=='healthy' for c in result['components'].values())
            if state=='ready' and not healthy:state='degraded'
            result.update(provider_state=state,state=STATE_MAP.get(state,'unknown'),
                          health='healthy' if healthy and state=='ready' else 'unhealthy' if state=='degraded' else 'unknown')
            result['operation_busy']=any(c['operation_busy'] for c in result['components'].values())
            if receipt:
                result['operation_busy'] |= app.object_owned('network',receipt['network']+'-contract',receipt['token'])
                if result['state']=='ready' and (not receipt['health_ready'] or result['operation_busy']
                        or receipt.get('operation_result') in {'running','unknown'}):
                    result.update(state='degraded',provider_state='unpublished',health='unknown')
            elif any(c['state']!='stopped' for c in result['components'].values()):
                result.update(state='unknown',provider_state='resource-unavailable',health='unknown',reason='observation-inconsistent')
        else:
            current=component(root,contract,now=now)
            result['components'][contract['project']['kind']]=current
            result.update({field:current[field] for field in ('state','provider_state','health','operation_busy','reason')})
            if receipt and result['state']=='ready' and (receipt['phase']!='ready' or not receipt['health_ready']):
                result.update(state='degraded',provider_state='unpublished',health='unhealthy')
        # Publication requires a configured owned Serve route, but route failure must
        # not erase independently observed component health.
        try:
            route=app.route_info(slug)
            published=bool(receipt and receipt['phase']=='ready' and receipt['health_ready']
                           and result['state']=='ready' and result['health']=='healthy' and not result['operation_busy']
                           and route.get('state')=='configured')
            result['publication']={'state':'published' if published else 'unavailable',
                                   'origin':route['url'].split('/projects/',1)[0] if route.get('url') else None}
        except app.AppError:
            result['publication']={'state':'unavailable','origin':None}
        result['routes']=route_descriptor(root,contract,result)
        if identity(Path(root).stat(follow_symlinks=False)) != before:
            raise app.AppError('conflict')
        return result
    finally:
        os.close(fd)


def route_descriptor(root, contract, result):
    slug=contract['project']['id']
    descriptor={'schema_version':1,'project':slug,'app_path':None,'docs_path':None}
    if contract['project']['kind'] in {'web','group'} and contract['schema_version']!=8:
        descriptor['app_path']='/projects/'+slug+'/'
    if contract['project']['kind'] not in {'api','group'}:
        return descriptor
    path='/projects/'+slug+('/docs' if contract['schema_version']==2 else '/api/docs')
    # This is the fixed docs capability of the already validated supported
    # adapter, never a browser/manifest-supplied destination or path crawl.
    if result['publication']['state']=='published':
        target=root if contract['schema_version']==2 else root/contract['components']['api']['root']
        from project_groups import identity as group_identity
        name=slug if contract['schema_version']==2 else group_identity(slug,'api')
        receipt=app.state_for(name)
        if receipt and receipt['root']==str(target):
            opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),app.NoRedirect())
            try:
                request=urllib.request.Request('http://127.0.0.1:'+str(receipt['port'])+path,method='GET')
                with opener.open(request,timeout=.25) as response:
                    if response.status==200 and response.headers.get_content_type()=='text/html':
                        descriptor['docs_path']=path
            except (OSError,ValueError):pass
    return descriptor


def job(binding):
    try:return project(binding['root'],expected=binding)
    except Exception:
        return {'error':'observation-unavailable'}
