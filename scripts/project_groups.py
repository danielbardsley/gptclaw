"""Two-service orchestration using the existing owned stack lifecycle adapters."""
import contextlib
from contextvars import ContextVar
import hashlib
from pathlib import Path
import re
import uuid

import private_apps as a

SCOPE = ContextVar('gptclaw_components', default={})
ORDER = ('api', 'web')


def identity(slug, component):
    return 'g-'+hashlib.sha256(slug.encode()).hexdigest()[:32]+'-'+component


def contract(slug, toolchains):
    import project_python as py
    api = py.contract(identity(slug, 'api'))
    web = {'schema_version': 1, 'project': {'id': identity(slug, 'web'), 'name': slug, 'kind': 'web'},
           'commands': {'build': ['pnpm', 'build'], 'start': ['pnpm', 'dev'], 'test': ['pnpm', 'test'],
                        'typecheck': ['pnpm', 'typecheck'], 'lint': ['pnpm', 'typecheck'],
                        'verify': ['pnpm', 'verify']},
           'service': {'internal_port': 3000, 'health': {'path': f'/projects/{slug}/', 'timeout_seconds': 5}}}
    api['service']['health']['path'] = f'/projects/{slug}/api/ready'
    components = {}
    for name, child in [('api', api), ('web', web)]:
        service = child['service'].copy()
        service['liveness'] = {'path': f'/projects/{slug}/api/health' if name == 'api' else f'/projects/{slug}/alive/', 'timeout_seconds': 5}
        components[name] = {'root': name, 'adapter': 'fastapi-v1' if name == 'api' else 'nextjs-v1',
                            'commands': child['commands'], 'service': service,
                            'toolchain': toolchains[name], 'depends_on': [] if name == 'api' else ['api']}
    return {'schema_version': 3, 'project': {'id': slug, 'name': slug.replace('-', ' ').title(), 'kind': 'group'},
            'components': components, 'exposure': {'private': True, 'base_path': f'/projects/{slug}/', 'funnel': False},
            'data': {'mode': 'ephemeral'}}


def initialize(stage, slug, release):
    value = contract(slug, release['toolchains'])
    for name in ORDER:
        meta = stage/value['components'][name]['root']/'.gptclaw'
        meta.mkdir()
        a.save(meta/'component.json', {'group': slug, 'component': name})
        a.save(meta/'template.json', {'provider': value['components'][name]['adapter']})
        a.save(meta/'toolchain.json', value['components'][name]['toolchain'])
    return value


def children(root, value):
    """Resolve and validate both component metadata boundaries before execution."""
    result = {}
    slug = value['project']['id']
    for name in ORDER:
        declaration = value['components'][name]
        child = a.safe(root/declaration['root'])
        a.need(child.is_dir() and child.stat().st_uid == root.stat().st_uid, 'path')
        a.need(a.read_json(child/'.gptclaw/component.json') == {'group': slug, 'component': name}, 'invalid')
        a.need(a.read_json(child/'.gptclaw/template.json') == {'provider': declaration['adapter']}, 'invalid')
        a.need(a.read_json(child/'.gptclaw/toolchain.json') == declaration['toolchain'], 'toolchain-policy')
        child_id = identity(slug, name)
        resolved = {'schema_version': 2 if name == 'api' else 1,
                    'project': {'id': child_id, 'name': value['project']['name'], 'kind': name},
                    'commands': declaration['commands'],
                    'service': {k: v for k,v in declaration['service'].items() if k != 'liveness'},
                    'exposure': value['exposure'], 'data': value['data']}
        result[name] = (child, resolved)
    return result


@contextlib.contextmanager
def scope(root, value):
    resolved = children(root, value)
    slug = value['project']['id']
    entries = {path: {'contract': child, 'group': slug, 'component': name} for name,(path,child) in resolved.items()}
    token = SCOPE.set(entries)
    try: yield resolved
    finally: SCOPE.reset(token)


def component_target(root):
    entry = SCOPE.get().get(root)
    a.need(entry is not None, 'invalid')
    a.need(a.read_json(root/'.gptclaw/component.json') == {'group': entry['group'], 'component': entry['component']}, 'invalid')
    return root, entry['contract']


def component_runtime(root):
    entry = SCOPE.get().get(root)
    if not entry: return {}
    slug = entry['group']
    return {'group': slug, 'component': entry['component'], 'runtime_project_id': slug,
            'network': 'gptclaw-group-'+slug, 'network_alias': entry['component'],
            'runtime_api_url': f'http://api:8000/projects/{slug}/api/ready'}


def valid_state(s):
    a.need(isinstance(s, dict) and s.get('schema_version') == 2)
    a.need(set(s) <= {'schema_version','id','root','token','network','components','phase','health_ready','operation','operation_id','operation_result','error','stages','cleanup_errors'})
    a.need(isinstance(s.get('id'), str) and re.fullmatch(r'[a-z][a-z0-9]*(?:-[a-z0-9]+)*', s['id']) and len(s['id']) <= 48)
    root = a.safe(s['root']); a.need(root.is_relative_to(a.PROJECTS) and root != a.PROJECTS and root != a.REPO and '.gptclaw-runtime' not in root.parts)
    a.need(s.get('network') == 'gptclaw-group-'+s['id'])
    a.need(isinstance(s.get('token'),str) and re.fullmatch(r'[0-9a-f]{32}',s['token']))
    a.need(s.get('components') == {name: identity(s['id'],name) for name in ORDER})
    a.need(s.get('phase') in {'preparing','starting','ready','stopped','failed'})
    a.need(type(s.get('health_ready')) is bool)
    a.need(s.get('operation') in {'start','stop','restart','test','build','format','lint','typecheck','security','verify','deps','toolchain'})
    a.need(isinstance(s.get('operation_id'),str) and re.fullmatch(r'[0-9a-f]{32}',s['operation_id']))
    a.need(s.get('operation_result') in {'running','passed','failed','unknown'})
    a.need(s.get('error') is None or s['error'] in a.MESSAGES)
    a.need(isinstance(s.get('stages'),list) and len(s['stages'])<=20 and all(x in {'network','api','web','route'} for x in s['stages']))
    a.need(isinstance(s.get('cleanup_errors',{}),dict) and set(s.get('cleanup_errors',{})) <= {'api','web','network'})
    a.need(all(x in a.MESSAGES for x in s.get('cleanup_errors',{}).values()))
    return s


def save(s):
    valid_state(s); a.save(a.STORE/(s['id']+'.json'),s)


def reserve(root, value):
    slug = value['project']['id']
    with a.locked('registry'):
        s = a.state_for(slug)
        if s:
            a.need(s['schema_version'] == 2 and s['root'] == str(root)); return s
        s = {'schema_version':2, 'id':slug, 'root':str(root), 'token':uuid.uuid4().hex,
             'network':'gptclaw-group-'+slug, 'components':{name:identity(slug,name) for name in ORDER},
             'phase':'stopped', 'health_ready':False, 'operation':'start', 'operation_id':uuid.uuid4().hex,
             'operation_result':'passed', 'error':None, 'stages':[]}
        save(s); return s


def network(s, create=False):
    owned = a.object_owned('network', s['network'], s['token'])
    if not owned and create:
        a.command(['podman','network','create','--internal','--label',a.LABEL+'='+s['token'],s['network']])
    return owned


def observe(s, resolved):
    result = {}
    for name,(root,value) in resolved.items():
        child = a.state_for(s['components'][name])
        if not child:
            result[name] = {'state':'stopped','health':'unknown','operation_busy':False}; continue
        a.need(child['root'] == str(root) and child.get('group') == s['id'])
        active,ready = a.inspect_service(child,value) if a.unit_path(child).exists() else (False,False)
        busy = a.object_owned('container',child['name']+'-job',child['token'])
        result[name] = {'state':'ready' if active and ready else 'unhealthy' if active else child['phase'],
                        'health':'ready' if ready else 'unhealthy' if active else 'unknown','active':active,
                        'operation_busy':busy,'port':child['port'],'unit':child['name'],
                        'operation_id':child['operation_id'],'last_operation':child['operation'],
                        'last_error':child.get('error'),'toolchain_hash':child.get('toolchain_hash'),
                        'image':child['image']}
    return result


def stopped(s, resolved):
    status = observe(s,resolved)
    a.need(not any(c.get('active') or c['operation_busy'] for c in status.values()), 'busy')
    for name in ORDER:
        child = a.state_for(s['components'][name])
        if child: a.need(not a.object_owned('container',child['name'],child['token']), 'busy')
    a.need(s['phase'] == 'stopped' and s['operation_result'] != 'running','busy')


def cleanup(s, resolved, names):
    errors = {}
    # A stopped group also reconciles stale isolated contract resources after a
    # bounded job exits. An unresolved web job is retained and reported as busy.
    web = a.state_for(s['components']['web'])
    if web and a.object_owned('container', web['name']+'-job', web['token']):
        errors['web'] = 'busy'
    else:
        api = a.state_for(s['components']['api'])
        try:
            if api and a.object_owned('container',api['name']+'-contract',s['token']):
                a.command(['podman','rm','--force',api['name']+'-contract'])
            if a.object_owned('network',s['network']+'-contract',s['token']):
                a.command(['podman','network','rm',s['network']+'-contract'])
        except a.AppError as error:errors['network'] = error.code
    for name in reversed(ORDER):
        if name not in names: continue
        try: a.stop(resolved[name][0],take_lock=False)
        except a.AppError as error: errors[name] = error.code
    if not errors:
        try:
            if network(s): a.command(['podman','network','rm',s['network']])
        except a.AppError as error: errors['network'] = error.code
    return errors


def start(root, no_route=False, take_lock=True):
    root,value = a.target(root); slug=value['project']['id']
    with (a.locked(slug) if take_lock else contextlib.nullcontext()), scope(root,value) as resolved:
        s=reserve(root,value)
        current=observe(s,resolved)
        a.need(not any(c['operation_busy'] for c in current.values()),'busy')
        a.need(not a.object_owned('network',s['network']+'-contract',s['token']),'busy')
        all_ready=all(c['health']=='ready' for c in current.values())
        if s['phase']=='ready' and all_ready:
            for path,_ in resolved.values():
                import project_toolchains as tools
                tools.assert_active(tools.selection(path),a.state_for(component_target(path)[1]['project']['id']))
            if not no_route:a.ensure_ingress()
            return {**status(root),'changed':False}
        # Partial or interrupted groups must be reconciled by stop before another start.
        a.need(not any(c.get('active') for c in current.values()),'health')
        a.need(s['operation_result'] != 'running','busy')
        if not no_route: a.route_info(slug)
        s.update(phase='preparing',health_ready=False,operation='start',operation_id=uuid.uuid4().hex,
                 operation_result='running',error=None,stages=[],cleanup_errors={});save(s)
        started=[]
        try:
            network(s,create=True);s['stages'].append('network');save(s)
            for name in ORDER:
                # Persist intent before starting, so interrupted effects can be observed.
                s.update(phase='starting');s['stages'].append(name);save(s);started.append(name)
                a.start(resolved[name][0],no_route=True,take_lock=False)
            a.need(all(c['health']=='ready' for c in observe(s,resolved).values()),'health')
            if not no_route: a.ensure_ingress()
            s['stages'].append('route');s.update(phase='ready',health_ready=True,operation_result='passed');save(s)
        except a.AppError as error:
            s.update(phase='failed',health_ready=False,error=error.code,
                     operation_result='unknown' if error.code=='timeout' else 'failed');save(s)
            # Jobs with unknown outcomes are preserved by the adapters' busy checks.
            s['cleanup_errors']=cleanup(s,resolved,started);save(s);raise
        result=status(root);result['changed']=True
        if no_route: result.pop('route',None)
        elif result['route']['state']!='configured':result['state']='operator-required'
        return result


def stop(root,take_lock=True):
    root,value=a.target(root);slug=value['project']['id']
    with (a.locked(slug) if take_lock else contextlib.nullcontext()), scope(root,value) as resolved:
        s=a.state_for(slug)
        if not s:return {'project':slug,'state':'stopped','changed':False,'source_retained':True}
        a.need(s['root']==str(root));changed=s['phase']!='stopped' or network(s)
        s.update(phase='stopped',health_ready=False,operation='stop',operation_id=uuid.uuid4().hex,
                 operation_result='running',error=None);save(s)
        errors=cleanup(s,resolved,ORDER)
        s.update(cleanup_errors=errors,operation_result='failed' if errors else 'passed',error=next(iter(errors.values()),None));save(s)
        if errors: raise a.AppError(s['error'])
        return {'project':slug,'operation_id':s['operation_id'],'state':'stopped','changed':changed,'source_retained':True}


def restart(root):
    root,value=a.target(root);slug=value['project']['id']
    with a.locked(slug):
        before=stop(root,take_lock=False);after=start(root,take_lock=False)
        s=a.state_for(slug);s.update(operation='restart');save(s)
        return {**after,'operation':'restart','transitions':[before.get('operation_id'),after['operation_id']]}


def status(root):
    root,value=a.target(root);slug=value['project']['id'];s=a.state_for(slug)
    if not s:return {'project':slug,'state':'stopped','health':'unknown','components':{}}
    a.need(s['root']==str(root))
    with scope(root,value) as resolved:
        components=observe(s,resolved)
    ready=all(c['health']=='ready' for c in components.values())
    state='ready' if ready and s['phase']=='ready' else 'degraded' if s['phase']=='ready' else s['phase']
    return {'project':slug,'operation_id':s['operation_id'],'last_operation':s['operation'],
            'operation_result':s['operation_result'],'state':state,'health':'ready' if ready else 'unhealthy',
            'operation_busy':any(c['operation_busy'] for c in components.values()) or a.object_owned('network',s['network']+'-contract',s['token']),
            'components':components,'route':a.route_info(slug),'last_error':s.get('error'),
            'stages':s['stages'],'cleanup_errors':s.get('cleanup_errors',{})}


def upstream(s, path):
    """Return an owned upstream only while both components are currently ready."""
    root,value=a.target(Path(s['root']))
    with scope(root,value) as resolved:
        for name in ORDER:
            child=a.state_for(s['components'][name])
            if not child:return None
            a.need(child['root']==str(resolved[name][0]) and child.get('group')==s['id'])
            a.verify_unit(child)
            if not a.healthy(child,resolved[name][1]):return None
        prefix=value['exposure']['base_path']+'api/'
        if path == prefix[:-1] or path.startswith(prefix):
            suffix=path[len(prefix):]
            if not (suffix.startswith('v1/') or suffix in {'docs','docs/','openapi.json','health','ready'} or suffix.startswith('docs-assets/')): return False
            name='api'
        else:name='web'
        return a.state_for(s['components'][name])


def dispatch(root, action, component=None, **kwargs):
    """Component jobs keep the same outer group lock; no independent mutations."""
    import project_dependencies as deps
    import project_toolchains as tools
    root,value=a.target(root);slug=value['project']['id']
    a.need(component in ORDER or component is None,'invalid')
    if action not in {'test','verify'}: a.need(component in ORDER,'invalid')
    with a.locked(slug),scope(root,value) as resolved:
        s=reserve(root,value)
        if action in {'deps','toolchain','format'}:
            # Dependency/toolchain inspection alone is observation-only.
            if kwargs.get('subaction') not in {'status','inspect'}: stopped(s,resolved)
        results={}
        observation=action=='logs' or kwargs.get('subaction') in {'status','inspect'}
        if not observation:
            s.update(operation=action,operation_id=uuid.uuid4().hex,operation_result='running',error=None);save(s)
        try:
            for name in ([component] if component else ORDER):
                path,_=resolved[name]
                if action=='deps':
                    subaction=kwargs.pop('subaction');results[name]=deps.status(path,kwargs.get('operation_id')) if subaction=='status' else deps.operate(path,subaction,**kwargs)
                elif action=='toolchain':
                    results[name]=tools.inspect(path) if kwargs['subaction']=='inspect' else tools.prepare(path)
                elif action=='logs':results[name]=a.logs(path,kwargs['lines'])
                else:results[name]=a.quality_app(path,action)
            if action in {'test','verify'} and component is None:
                cross_service(s,resolved)
        except a.AppError as error:
            if not observation:
                s.update(operation_result='unknown' if error.code=='timeout' else 'failed',error=error.code);save(s)
            raise
        if not observation:s.update(operation_result='passed');save(s)
        return {'project':slug,'operation_id':s['operation_id'],'state': action+'-passed' if action not in {'deps','toolchain','logs'} else results[component]['state'] if 'state' in results[component] else 'observed','components':results}


def cross_service(s, resolved):
    """Run real CRUD in two isolated test containers, separate from live notes."""
    import project_python as py
    api = a.state_for(s['components']['api'])
    web = a.state_for(s['components']['web'])
    net = s['network']+'-contract'
    name = api['name']+'-contract'
    a.need(not a.object_owned('container',name,s['token']),'busy')
    a.need(not a.object_owned('network',net,s['token']),'busy')
    a.command(['podman','network','create','--internal','--label',a.LABEL+'='+s['token'],net])
    try:
        args=['podman','run','--detach','--name',name,'--label',a.LABEL+'='+s['token'],
              '--network='+net,'--network-alias=api','--userns=keep-id','--memory='+a.MEMORY,
              '--cpus='+a.CPU,'--pids-limit='+str(a.PIDS),'--cap-drop=all','--security-opt=no-new-privileges',
              '--volume',api['root']+':/workspace:rw','--workdir','/workspace',
              '--env','GPTCLAW_PROJECT_ID='+s['id']]
        for key,value in py.GUARD_ENV.items():args+=['--env',key+'='+value]
        args += [api['image'],*resolved['api'][1]['commands']['start']]
        a.command(args)
        a.run_in_app({**web,'job_network':net,'job_env':{'GPTCLAW_CONTRACT_API_URL':f"http://api:8000/projects/{s['id']}"}},['pnpm','contract'])
    finally:
        # Never remove an unresolved web job; status retains the owned test resources.
        if not a.object_owned('container',web['name']+'-job',web['token']):
            if a.object_owned('container',name,s['token']):a.command(['podman','rm','--force',name])
            if a.object_owned('network',net,s['token']):a.command(['podman','network','rm',net])


def install_hooks(root):
    """Install an explicit parent-repository hook invoking managed group verify."""
    import os
    import project_dependencies as deps
    root,value=a.target(root);slug=value['project']['id']
    with a.locked(slug),scope(root,value) as resolved:
        s=reserve(root,value);stopped(s,resolved)
        for path,child in resolved.values():deps.require_clean(path,child['project']['id'])
        directory=a.safe(root/'.git');a.need(directory.is_dir() and directory.stat().st_uid==os.getuid())
        hooks=a.safe(directory/'hooks');hooks.mkdir(exist_ok=True)
        launcher=a.provider_bundle()/'scripts/gptclawctl'
        text='#!/usr/bin/env bash\nset -euo pipefail\nexec '+str(launcher)+' verify --project-root '+str(root)+'\n'
        path=a.safe(hooks/'pre-commit')
        if path.exists():
            a.need(deps.read_bytes(path,65536)==text.encode());return {'project':slug,'state':'hooks-installed','changed':False}
        with path.open('xb') as stream:stream.write(text.encode())
        path.chmod(0o700)
        return {'project':slug,'state':'hooks-installed','changed':True}
