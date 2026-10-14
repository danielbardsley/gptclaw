"""Owned canonical Metro sessions supervised by a bounded forge user service."""
import hashlib
import json
import math
import os
from pathlib import Path
import signal
import threading
import time
import uuid

import private_apps as app
import metro_contract as contract
import metro_protocol as protocol
import metro_proxy as proxy
import metro_routes as routes
import metro_retention as retention
import metro_security as security
import metro_spike as spike
import metro_state as states
import project_dependencies as deps
import project_mobile as mobile
import project_toolchains as tools
import project_worktrees as worktrees

LABEL='com.gptclaw.metro-session'
UNITS=Path('/home/forge/.config/systemd/user')
FILES=('.gptclaw/project.yaml','.gptclaw/template.json','.gptclaw/template-release.json','.gptclaw/toolchain.json',
       'app.json','package.json','pnpm-lock.yaml','pnpm-workspace.yaml','tsconfig.json',
       'checks/sdk.json','checks/advisory-policy.json','checks/toolchain/profile.json','checks/toolchain/install-pnpm.cjs','checks/toolchain/Containerfile')


def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def directory(project):
    mobile.identities(project)
    return app.safe(app.STORE/'metro'/project)
def location(project):return directory(project)/'session.json'
def hashes(root):return {name:hashlib.sha256(deps.read_bytes(root/name)).hexdigest() for name in FILES}
def unit_path(value):return app.safe(UNITS/(value['name']+'.service'))
def network(value):return value['name']+'-net'


def mount_identities(root):
    result={}
    for name in ['src','assets','node_modules']:
        path=root/name;app.safe(path)
        result[name]=worktrees.owned(path) if path.exists() else None
    app.need(result['node_modules'] is not None,'path')
    return result

def load(project,root=None):
    value=app.read_json(location(project))
    if value is None:return None
    states.validate(value)
    app.need(value['project']==project and (root is None or value['root']==str(root)),'conflict')
    return value

def read_events(project):
    value=app.read_json(directory(project)/'events.json')
    if value is None:return []
    app.need(isinstance(value,dict) and set(value)=={'schema_version','events'}
             and type(value['schema_version']) is int and value['schema_version']==1
             and isinstance(value['events'],list) and len(value['events'])<=256,'conflict')
    for event in value['events']:
        app.need(isinstance(event,dict) and set(event)=={'observed_at','generation','phase','operation_result'}
                 and states.number(event['observed_at']) and isinstance(event['generation'],str)
                 and states.HEX32.fullmatch(event['generation']) is not None
                 and isinstance(event['phase'],str) and event['phase'] in states.PHASES
                 and isinstance(event['operation_result'],str) and event['operation_result'] in {'running','passed','failed','unknown'},'conflict')
    return value['events']


def event_time(value):return max(time.time(),value['started_at'])


def save(value):
    states.validate(value);path=directory(value['project']);path.mkdir(parents=True,mode=0o700,exist_ok=True)
    app.need(path.stat().st_uid==os.getuid() and path.stat().st_mode&0o077==0,'path')
    events=read_events(value['project']);stamp=event_time(value)
    events=[e for e in events if 0<=stamp-e['observed_at']<=7*86400]
    event={'observed_at':stamp,'generation':value['generation'],'phase':value['phase'],'operation_result':value['operation_result']}
    if not events or any(events[-1][key]!=event[key] for key in ['generation','phase','operation_result']):
        events.append(event);app.save(path/'events.json',{'schema_version':1,'events':events[-256:]})
    app.save(location(value['project']),value)

def control(value,allow_frozen=False):
    data=app.read_json(directory(value['project'])/'control.json')
    app.need(isinstance(data,dict) and set(data)=={'schema_version','project','root','generation','inputs','source','provider','audit','root_identity','mount_identities'}
             and type(data['schema_version']) is int and data['schema_version']==2 and data['project']==value['project']
             and data['root']==value['root'] and data['generation']==value['generation'],'conflict')
    app.need(isinstance(data['inputs'],dict) and set(data['inputs'])==set(FILES)
             and all(isinstance(v,str) and states.HEX64.fullmatch(v) for v in data['inputs'].values()),'conflict')
    app.need(data['source']==str(directory(value['project'])/'sources'/value['generation'])
             and isinstance(data['provider'],str),'conflict')
    if allow_frozen:
        provider=app.safe(Path(data['provider']))
        app.need(provider.parent==app.STORE/'providers' and states.HEX64.fullmatch(provider.name)
                 and hashlib.sha256(unit_text(value,provider).encode()).hexdigest()==value['unit_digest'],'conflict')
    else:app.need(data['provider']==str(app.REPO),'conflict')
    app.need(isinstance(data['root_identity'],list) and len(data['root_identity'])==2
             and all(type(n) is int and n>=0 for n in data['root_identity']),'conflict')
    mounts=data['mount_identities']
    app.need(isinstance(mounts,dict) and set(mounts)=={'src','assets','node_modules'} and mounts['node_modules'] is not None,'conflict')
    for identity in mounts.values():
        app.need(identity is None or isinstance(identity,list) and len(identity)==2
                 and all(type(n) is int and n>=0 for n in identity),'conflict')
    return data

def ownership(kind,name,token):return spike.ownership(kind,name,token,LABEL)
def revoke_path(policy_digest):
    app.need(isinstance(policy_digest,str) and states.HEX64.fullmatch(policy_digest) is not None,'invalid')
    return app.safe(app.STORE/'metro'/'revocations'/(policy_digest+'.json'))
def admitted(value=None):
    policy=security.read_policy(app.REPO);key=digest(policy)
    app.need(not revoke_path(key).exists() and not revoke_path(key).is_symlink(),'conflict')
    if value:app.need(value['policy_digest']==key,'conflict')
    return policy


def slots():
    path=app.safe(app.STORE/'metro'/'registry.json');data=app.read_json(path)
    if data is None:return {}
    app.need(isinstance(data,dict) and set(data)=={'schema_version','entries'} and type(data['schema_version']) is int
             and data['schema_version']==1 and isinstance(data['entries'],dict) and len(data['entries'])<=8,'conflict')
    used=set()
    for project,item in data['entries'].items():
        mobile.identities(project)
        app.need(isinstance(item,dict) and set(item)=={'root','canonical_key','slot'} and isinstance(item['root'],str)
                 and isinstance(item['canonical_key'],str) and states.HEX64.fullmatch(item['canonical_key'])
                 and type(item['slot']) is int and item['slot'] in range(8) and item['slot'] not in used,'conflict')
        used.add(item['slot'])
    return data['entries']

def reserve(root,identity):
    # Sticky project origins are never silently recycled while Serve config may remain.
    with app.locked('registry'):
        values=slots();project=identity['project']
        if project in values:
            item=values[project];app.need(item['root']==str(root) and item['canonical_key']==identity['key'],'conflict')
        else:
            used={v['slot'] for v in values.values()};slot=next((i for i in range(8) if i not in used),None)
            app.need(slot is not None,'ports');item={'root':str(root),'canonical_key':identity['key'],'slot':slot}
            values[project]=item
            path=app.safe(app.STORE/'metro');path.mkdir(mode=0o700,exist_ok=True)
            app.save(path/'registry.json',{'schema_version':1,'entries':values})
        metro=18600+2*item['slot'];app.need(app.available(metro) and app.available(metro+1),'conflict')
        return metro,metro+1,8443+item['slot']


def unit_text(value,provider=None):
    launcher=(provider or app.REPO)/'scripts/gptclawctl'
    return f'''[Unit]
Description=GptClaw owned Metro {value['project']}
StartLimitIntervalSec=300
StartLimitBurst=3

[Service]
ExecStart={launcher} metro supervise --project-root {value['root']} --generation {value['generation']}
Restart=on-failure
RestartSec=2
TimeoutStartSec=300
TimeoutStopSec=30
MemoryMax=192M
CPUQuota=25%
TasksMax=64
NoNewPrivileges=true
StandardOutput=null
StandardError=null

[Install]
WantedBy=default.target
'''

def verify_unit(value):
    path=unit_path(value);app.need(hashlib.sha256(deps.read_bytes(path,65536)).hexdigest()==value['unit_digest'],'conflict')
    output=app.command(['systemctl','--user','show',value['name']+'.service','-p','FragmentPath','-p','DropInPaths'],timeout=10).stdout
    fields=dict(line.split('=',1) for line in output.splitlines() if '=' in line)
    app.need(fields.get('FragmentPath')==str(path) and not fields.get('DropInPaths'),'conflict')


def inactive_unit(value):
    verify_unit(value)
    fields=unit_fields(value['name'],['ActiveState','SubState'])
    app.need(fields.get('ActiveState') in {'inactive','failed'}
             and fields.get('SubState') in {'dead','failed'},'busy')


def unit_fields(name,properties):
    output=app.command(['systemctl','--user','show',name+'.service',
                        *[flag for prop in properties for flag in ['-p',prop]]],timeout=10).stdout
    return dict(line.split('=',1) for line in output.splitlines() if '=' in line)


def preflight_unit(project,old):
    name='gptclaw-metro-'+project;path=app.safe(UNITS/(name+'.service'))
    if path.exists():
        app.need(old is not None,'conflict');inactive_unit(old)
    else:
        fields=unit_fields(name,['LoadState','ActiveState','FragmentPath','DropInPaths'])
        app.need(fields.get('LoadState')=='not-found' and fields.get('ActiveState')=='inactive'
                 and not fields.get('FragmentPath') and not fields.get('DropInPaths'),'conflict')


def receipt_for_root(root,generation):
    # Resolve only from an owned registry/receipt. Invalid or missing app metadata
    # must not prevent an already-owned unit from stopping its resources.
    root=app.safe(Path(root).absolute());worktrees.guard(root)
    matches=[(project,item) for project,item in slots().items() if item['root']==str(root)]
    app.need(len(matches)==1,'conflict');project,item=matches[0];value=load(project,root)
    app.need(value is not None and value['generation']==generation
             and value['canonical_key']==item['canonical_key'],'conflict')
    return root,value


def result(value,root,identity=None):
    identity=identity or worktrees.canonical(root)
    current=digest(hashes(root))
    descriptor=states.descriptor(value,project=value['project'],root=root,canonical_key=identity['key'],input_digest=current)
    if value['phase'] not in states.INACTIVE:
        try:admitted(value)
        except (app.AppError,security.AdmissionError):
            descriptor.update(state='security-unavailable',transport_available=False,origin=None)
    return descriptor

def status(root):
    root,source=app.target(root);app.need(source['schema_version']==6,'mobile-unsupported')
    identity=worktrees.canonical(root);value=load(source['project']['id'],root)
    if value is None:return {'project':source['project']['id'],'state':'not-started','transport_available':False,'origin':None}
    return result(value,root,identity)



def logs(root,lines=80):
    app.need(type(lines) is int and 1<=lines<=256,'invalid')
    root,source=app.target(root);app.need(source['schema_version']==6,'mobile-unsupported');worktrees.canonical(root)
    project=source['project']['id'];value=load(project,root)
    if value is None:return {'project':project,'events':[],'log_kind':'lifecycle-events'}
    events=[event for event in read_events(project) if 0<=time.time()-event['observed_at']<=7*86400]
    return {'project':project,'generation':value['generation'],'events':events[-lines:],'log_kind':'lifecycle-events'}


def revoke(policy_digest,apply=False):
    spike.require_operator();path=revoke_path(policy_digest)
    app.need(digest(security.read_policy(app.REPO))==policy_digest,'conflict')
    result={'policy_digest':policy_digest,'state':'revocation-planned','changed':False}
    if not apply:return result
    with app.locked('registry'):
        if path.exists():return {**result,'state':'revoked'}
        path.parent.mkdir(parents=True,mode=0o700,exist_ok=True)
        app.save(path,{'schema_version':1,'policy_digest':policy_digest,'revoked_at':time.time(),'reason':'owner-revocation'})
    return {**result,'state':'revoked','changed':True}


def require_idle(root,project):
    deps.require_clean(root,project);contract.require_reconciled(root,project);contract.metadata_clean(root)
    state=mobile.load_state(root,project)
    if state:
        app.need(state['phase']!='checking' and state['operation_result'] not in {'running','unknown'},'busy')
        app.need(spike.ownership('container',state['name']+'-job',state['token'],app.LABEL)=='absent','busy')

def assert_stopped(root,project):
    value=load(project,root)
    if value:
        app.need(value['phase'] in {'stopped','expired','failed'} and ownership('container',value['name'],value['token'])=='absent'
                 and ownership('container',value['name']+'-audit',value['token'])=='absent'
                 and ownership('network',network(value),value['token'])=='absent','busy')
        preflight_unit(project,value)


def lifetime(source,seconds=None):
    maximum=source['metro']['ttl_seconds']
    app.need(seconds is None or type(seconds) is int and 60<=seconds<=maximum,'invalid')
    return maximum if seconds is None else seconds


def start(root,no_route=False,ttl_seconds=None,expected_generation=None,transport=None):
    spike.require_operator();root,source=app.target(root);app.need(source['schema_version']==6,'mobile-unsupported')
    app.need(transport in {None,'https','tailnet-http'},'invalid')
    seconds=lifetime(source,ttl_seconds)
    policy=admitted();identity=worktrees.canonical(root);project=identity['project']
    with app.locked(project):
        require_idle(root,project);contract.inputs(root)
        old=load(project,root)
        selected_transport=transport or ('tailnet-http' if old and old['origin'].startswith('http://') else 'https')
        if expected_generation is not None:
            app.need(isinstance(expected_generation,str) and states.HEX32.fullmatch(expected_generation)
                     and old is not None and old['generation']==expected_generation,'conflict')
        if old and old['phase']=='running':
            app.need((old['origin'].startswith('http://'))==(selected_transport=='tailnet-http'),'conflict')
            verify_unit(old);admitted(old)
            app.need(ttl_seconds is None or old['expires_at']-old['started_at']<=seconds,'conflict')
            app.need(unit_fields(old['name'],['ActiveState']).get('ActiveState')=='active','conflict')
            app.need(old['canonical_key']==identity['key'] and time.time()<old['expires_at']
                     and old['input_digest']==digest(hashes(root)) and ownership('container',old['name'],old['token'])=='owned','conflict')
            return {**result(old,root,identity),'changed':False}
        if old:
            app.need(old['phase'] in {'stopped','expired','failed'} and ownership('container',old['name'],old['token'])=='absent'
                     and ownership('container',old['name']+'-audit',old['token'])=='absent'
                     and ownership('network',network(old),old['token'])=='absent','conflict')
        preflight_unit(project,old)
        selected=tools.selection(root);observed=tools.observed(selected)
        app.need(observed['state']=='verified' and observed['image_present'],'toolchain-verification')
        spike.prepared_dependencies(root,project)
        inventory=spike.source_inventory(root)
        retention.admit(project,retention.source_bytes(root,inventory))
        input_files=hashes(root);image=observed['receipt']['image'];token=uuid.uuid4().hex;generation=uuid.uuid4().hex
        metro,proxy,tls=reserve(root,identity)
        origin=('http' if selected_transport=='tailnet-http' else 'https')+'://'+app.node_identity()+':'+str(tls)
        now=time.time();expiry=min(now+seconds,security.timestamp(policy['expires_at']))
        value={'schema_version':2 if selected_transport=='tailnet-http' else 1,
               **({'transport':'private-tailnet-http'} if selected_transport=='tailnet-http' else {}),
               'adapter':'metro-v1','project':project,'root':str(root),'canonical_key':identity['key'],
               'name':'gptclaw-metro-'+project,'generation':generation,'token':token,'image':image,'input_digest':digest(input_files),
               'policy_digest':digest(policy),'unit_digest':'0'*64,'metro_port':metro,'proxy_port':proxy,'origin':origin,
               'phase':'preparing','started_at':now,'expires_at':expiry,'operation_id':uuid.uuid4().hex,'operation_result':'running',
               'observations':{'process':{'state':'unknown','observed_at':None},'protocol':{'state':'unknown','observed_at':None},
                               'route':{'state':'pending','observed_at':None}}}
        snapshot=app.provider_bundle();text=unit_text(value,snapshot);value['unit_digest']=hashlib.sha256(text.encode()).hexdigest()
        if old:
            history=directory(project)/'history';history.mkdir(mode=0o700,exist_ok=True)
            app.save(history/(old['generation']+'.json'),old)
        save(value)
        try:
            view=directory(project)/'sources'/generation;view.parent.mkdir(parents=True,mode=0o700,exist_ok=True)
            spike.prepare_view(root,view,inventory);retention.seal(value,inventory)
            data={'schema_version':2,'project':project,'root':str(root),'generation':generation,'inputs':input_files,
                  'source':str(view),'provider':str(snapshot),'audit':None,'root_identity':identity['root_identity'],'mount_identities':mount_identities(root)};app.save(directory(project)/'control.json',data)
            path=unit_path(value);app.safe(UNITS);UNITS.mkdir(mode=0o700,parents=True,exist_ok=True)
            if path.exists():
                app.need(old is not None and hashlib.sha256(deps.read_bytes(path,65536)).hexdigest()==old['unit_digest'],'conflict')
            app.save_text(path,text);app.command(['systemctl','--user','daemon-reload'],timeout=20)
            app.command(['systemctl','--user','reset-failed',value['name']+'.service'],optional=True,timeout=10)
            value['phase']='starting';save(value)
            app.command(['systemctl','--user','start',value['name']+'.service'],timeout=30)
        except (app.AppError,OSError,ValueError):
            failed_start(value);raise

    deadline=time.monotonic()+min(300,max(0,expiry-time.time()))
    try:
        while time.monotonic()<deadline:
            value=load(project,root)
            if value['phase']=='running':return {**result(value,root,identity),'changed':True}
            app.need(value['phase'] not in states.INACTIVE,'health');time.sleep(1)
        raise app.AppError('timeout')
    except app.AppError:
        with app.locked(project):
            current=load(project,root)
            if current and current['generation']==generation:failed_start(current)
        raise


def failed_start(value):
    # Exact unit proof is required before stopping; a partial/foreign publication
    # is reported as recovery-required, never cleared by a guessed systemctl stop.
    outcome='failed'
    try:
        verify_unit(value)
        app.command(['systemctl','--user','stop',value['name']+'.service'],timeout=40)
        inactive_unit(value)
    except app.AppError:outcome='recovery-required'
    try:cleanup(value)
    except app.AppError:outcome='recovery-required'
    current=load(value['project'],Path(value['root']))
    if current and current['generation']==value['generation']:
        current.update(phase=outcome,operation_result='unknown' if outcome=='recovery-required' else 'failed')
        current['observations']['process']={'state':'unknown' if outcome=='recovery-required' else 'down','observed_at':event_time(value)}
        save(current)


def cleanup(value):
    failed=False
    # A conflict on one handle does not leave independently owned handles running.
    for kind,name in [('container',value['name']),('container',value['name']+'-audit'),('network',network(value))]:
        try:
            found=ownership(kind,name,value['token']);app.need(found!='foreign','conflict')
            if found=='owned':
                app.command(['podman','stop','--time','20',name] if kind=='container' else ['podman','network','rm',name],timeout=30)
                app.need(ownership(kind,name,value['token'])=='absent','conflict')
        except app.AppError:failed=True
    app.need(not failed,'conflict')


def stop_owned(root,value):
    verify_unit(value)
    value.update(phase='stopping',operation_id=uuid.uuid4().hex,operation_result='running');save(value)
    try:
        app.command(['systemctl','--user','stop',value['name']+'.service'],timeout=40)
        inactive_unit(value);cleanup(value)
    except app.AppError:
        value.update(phase='recovery-required',operation_result='unknown')
        value['observations']['process']={'state':'unknown','observed_at':event_time(value)};save(value)
        raise
    value=load(value['project'],root);value.update(phase='stopped',operation_result='passed')
    value['observations']['process']={'state':'down','observed_at':event_time(value)};save(value)
    return {'project':value['project'],'generation':value['generation'],'state':'stopped','transport_available':False,'origin':None,'changed':True}


def recover_stop(root,generation):
    spike.require_operator();root,value=receipt_for_root(root,generation)
    with app.locked(value['project']):
        root,current=receipt_for_root(root,generation)
        return stop_owned(root,current)


def stop(root):
    spike.require_operator();root,source=app.target(root);app.need(source['schema_version']==6,'mobile-unsupported')
    worktrees.canonical(root);project=source['project']['id']
    with app.locked(project):
        value=load(project,root)
        if value is None:return {'project':project,'state':'not-started','changed':False}
        return stop_owned(root,value)


def restart(root,no_route=False,transport=None):stop(root);return start(root,no_route,transport=transport)


def renewal_plan(root,generation,ttl_seconds=None):
    root,source=app.target(root);app.need(source['schema_version']==6,'mobile-unsupported')
    app.need(isinstance(generation,str) and states.HEX32.fullmatch(generation),'invalid')
    seconds=lifetime(source,ttl_seconds);identity=worktrees.canonical(root)
    value=load(identity['project'],root);app.need(value is not None and value['generation']==generation,'conflict')
    policy=admitted(value);verify_unit(value)
    require_idle(root,value['project']);contract.inputs(root)
    data=control(value,allow_frozen=True)
    app.need(value['canonical_key']==identity['key'] and value['input_digest']==digest(hashes(root))
             and identity['root_identity']==data['root_identity']
             and mount_identities(root)==data['mount_identities'],'conflict')
    app.need(value['phase']=='running' and value['operation_result']=='passed'
             and time.time()<value['expires_at']
             and ownership('container',value['name'],value['token'])=='owned'
             and unit_fields(value['name'],['ActiveState']).get('ActiveState')=='active','conflict')
    descriptor=result(value,root,identity)
    app.need(descriptor['state']=='ready' and routes.observe(value)['state']=='verified','health')
    app.need(security.timestamp(policy['expires_at'])-time.time()>=60,'invalid')
    proposal={'schema_version':1,'project':value['project'],'generation':generation,
              'canonical_key':identity['key'],'input_digest':value['input_digest'],
              'policy_digest':value['policy_digest'],'unit_digest':value['unit_digest'],
              'origin':value['origin'],'previous_expires_at':value['expires_at'],
              'ttl_seconds':seconds,'renewal_kind':'new-generation'}
    return root,value,{**proposal,'plan_digest':digest(proposal),'changed':False,'state':'renewal-planned'}


def renew(root,generation,ttl_seconds=None,apply=False,confirm_plan=None):
    # A container's independent timeout is immutable: renewal uses fresh admission,
    # owned shutdown and a new generation. It never rewrites a running lease.
    root,value,proposal=renewal_plan(root,generation,ttl_seconds)
    if not apply:return proposal
    spike.require_operator();app.need(confirm_plan==proposal['plan_digest'],'conflict')
    with app.locked(value['project']):
        root,value,current=renewal_plan(root,generation,ttl_seconds)
        app.need(current['plan_digest']==confirm_plan,'conflict')
        stop_owned(root,value)
    # Guard the stop/start interval against another caller starting a new session.
    started=start(root,ttl_seconds=proposal['ttl_seconds'],expected_generation=generation)
    app.need(started['generation']!=generation,'conflict')
    return {**started,'previous_generation':generation,'renewal_kind':'new-generation'}


def proxy_receipt(value):
    admitted(value)
    current=load(value['project'],Path(value['root']))
    app.need(current is not None and current['generation']==value['generation'],'conflict')
    return current


def observe_protocol(value,current,startup,established):
    """An observation failure is not evidence that a live owned SDK exited."""
    try:
        protocol.request(value['metro_port'],value['origin'],'/', 'android',
                         max_bytes=protocol.MAX_MANIFEST,manifest=True)
    except app.AppError:
        current['observations']['protocol']={'state':'failed','observed_at':event_time(value)}
        # Initial readiness remains bounded. Once established, preserve the same
        # live process and lease while reporting unavailable protocol until recovery.
        if not established:app.need(time.monotonic()<startup,'health')
        return established
    current['observations']['protocol']={'state':'ready','observed_at':event_time(value)}
    current.update(phase='running',operation_result='passed')
    return True


def supervise(root,generation):
    spike.require_operator();root,value=receipt_for_root(root,generation);project=value['project']
    app.need(value is not None and value['generation']==generation and value['phase'] in {'starting','running','failed'},'conflict')
    stopping=threading.Event()
    signal.signal(signal.SIGTERM,lambda *_:stopping.set());signal.signal(signal.SIGINT,lambda *_:stopping.set())
    runner=None;bridge=None;outcome='failed';stage='admission';failure=None
    try:
        verify_unit(value);data=control(value);view=Path(data['source']);policy=admitted(value)
        _,source=app.target(root);identity=worktrees.canonical(root)
        app.need(source['schema_version']==6 and source['project']['id']==project
                 and identity['key']==value['canonical_key'] and identity['root_identity']==data['root_identity'],'conflict')
        value.update(phase='starting',operation_result='running');save(value)
        app.need(hashes(root)==data['inputs'] and mount_identities(root)==data['mount_identities'],'conflict')
        app.need(ownership('container',value['name'],value['token'])=='absent' and ownership('container',value['name']+'-audit',value['token'])=='absent','conflict')
        stage='audit'
        audit_name=value['name']+'-audit'
        audit_seconds=min(120,math.floor(value['expires_at']-time.time()));app.need(audit_seconds>0,'invalid')
        audit=app.command(['podman','run','--name',audit_name,'--label',LABEL+'='+value['token'],
                           *spike.container_options(view,root,audit_seconds),value['image'],'pnpm','audit','--json','--registry=https://registry.npmjs.org/'],timeout=audit_seconds+20,optional=True)
        app.need(audit.returncode in {0,1},'command');data['audit']=security.evaluate(json.loads(audit.stdout),policy,deps.read_bytes(root/'pnpm-lock.yaml'))
        app.save(directory(project)/'control.json',data);admitted(value);app.need(hashes(root)==data['inputs'],'conflict')
        app.need(ownership('network',network(value),value['token'])=='absent','conflict')
        stage='network'
        app.command(['podman','network','create','--internal','--label',LABEL+'='+value['token'],network(value)],timeout=20)
        seconds=math.floor(value['expires_at']-time.time());app.need(seconds>0,'invalid')
        args=['podman','run','--name',value['name'],'--label',LABEL+'='+value['token'],'--network',network(value),
              '--publish','127.0.0.1:'+str(value['metro_port'])+':8081',*spike.container_options(view,root,seconds,watch=True)]
        live_mounts=mount_identities(root);app.need(live_mounts==data['mount_identities'],'conflict')
        for name in ['src','assets']:
            if live_mounts[name] is not None:args+=['--volume',str(root/name)+':/workspace/'+name+':ro']
        args+=['--env','EXPO_OFFLINE=1','--env','EXPO_PACKAGER_PROXY_URL='+value['origin'],value['image'],
               'node','node_modules/expo/bin/cli','start','--offline','--go','--port','8081']
        stage='sdk'
        runner=spike.EphemeralOutput(args)
        stage='proxy'
        bridge=proxy.Service(value,lambda:proxy_receipt(value));bridge.start()
        startup=time.monotonic()+min(300,seconds)
        stage='supervision';next_route=0;protocol_established=False
        while not stopping.is_set():
            current=load(project,root);app.need(current is not None and current['generation']==generation,'conflict')
            if current['phase']=='stopping':stopping.set();break
            app.need(time.time()>=value['started_at'],'conflict')
            if time.time()>=value['expires_at']:outcome='expired';break
            admitted(value);app.need(hashes(root)==data['inputs'],'conflict')
            app.need(bridge.thread.is_alive() and not bridge.failure,'health')
            app.need(worktrees.owned(root)==data['root_identity'] and mount_identities(root)==data['mount_identities'],'conflict')
            app.target(root);spike.source_inventory(root)
            if runner.process.poll() is not None:raise app.AppError('health')
            up=ownership('container',value['name'],value['token'])=='owned'
            current['observations']['process']={'state':'up' if up else 'unknown','observed_at':event_time(value)}
            if up:
                protocol_established=observe_protocol(value,current,startup,protocol_established)
            if time.monotonic()>=next_route and current['phase']=='running':
                # The proxy checks the durable process/protocol receipt independently.
                save(current)
                current['observations']['route']=routes.observe(current)
                next_route=time.monotonic()+10
            save(current);stopping.wait(2)
        if stopping.is_set():outcome='stopped'
    except (app.AppError,security.AdmissionError,OSError,ValueError) as error:
        outcome='failed'
        failure={'stage':stage,'code':error.code if isinstance(error,app.AppError) and error.code in app.MESSAGES else 'security-or-source-admission'}
    finally:
        if bridge:
            try:bridge.stop()
            except app.AppError:
                outcome='recovery-required';failure={'stage':'proxy-shutdown','code':'timeout'}
        try:cleanup(value)
        except app.AppError:
            outcome='recovery-required';failure={'stage':'owned-cleanup','code':'conflict'}
        if runner:runner.finish()
        if failure:
            app.save(directory(project)/('failure-'+generation+'.json'),
                     {'schema_version':1,'generation':generation,**failure})
        current=load(project,root)
        if current and current['generation']==generation:
            current.update(phase=outcome,operation_result='passed' if outcome in {'stopped','expired'} else 'failed')
            current['observations']['process']={'state':'unknown' if outcome=='recovery-required' else 'down','observed_at':event_time(value)};save(current)
    return {'project':project,'state':outcome}
