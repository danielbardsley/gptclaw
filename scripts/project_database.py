"""Owned persistent PostgreSQL lifecycle; secrets are files, never command values."""
import contextlib
import hashlib
import json
import os
import platform
from pathlib import Path
import re
import selectors
import threading
import secrets
import shutil
import stat
import subprocess
import time
import uuid

import private_apps as a

BASE = a.STORE/'data/projects'
LEGACY_BASE = Path('/srv/forge/data/projects')
STORAGE = 'runtime-volume-v1'
MOUNT = Path('/srv/forge')
ROLES = ('admin', 'migration', 'runtime')
HEX = re.compile(r'^[0-9a-f]{32}$')


def check(ok, code='database-state'):
    a.need(ok, code)


def profile():
    value = a.read_json(a.REPO/'config/databases/v1.json')
    check(isinstance(value, dict) and value.get('schema_version') == 1)
    check(value.get('profile') == 'postgres18-v1' and value.get('major') == 18)
    check(re.fullmatch(r'docker.io/library/postgres@sha256:[0-9a-f]{64}', value.get('image', '')))
    check(value.get('platform') == {'os': 'linux', 'architecture': 'amd64'})
    return value


def private(path, directory=False):
    """Refuse links, unsafe modes and foreign ownership before any file access."""
    path = a.safe(path)
    try: info = path.lstat()
    except OSError: raise a.AppError('database-storage') from None
    check((stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode)), 'path')
    check(info.st_uid == os.getuid() and stat.S_IMODE(info.st_mode) == (0o700 if directory else 0o600), 'path')
    if not directory: check(info.st_nlink == 1, 'path')
    return path


def read(path):
    private(path)
    return a.read_json(path)


def write(path, value):
    private(path.parent, True)
    if path.exists() or path.is_symlink(): private(path)
    a.save(path, value)


def require_storage(contract):
    check(contract.get('database',{}).get('storage')==STORAGE,'database-storage')


def mount():
    if BASE == a.STORE/'data/projects':
        check(not LEGACY_BASE.exists() and not LEGACY_BASE.is_symlink(),'database-storage')
    check(a.command(['mountpoint', '-q', str(MOUNT)], optional=True).returncode == 0, 'database-storage')
    check(MOUNT.stat().st_dev == BASE.parent.stat().st_dev if BASE.parent.exists() else True, 'database-storage')


def home(slug):
    check(re.fullmatch(r'[a-z][a-z0-9]*(?:-[a-z0-9]+)*', slug) and len(slug) <= 48)
    return a.safe(BASE/slug)


def state(slug, root=None):
    mount()
    path = home(slug)
    if not path.exists(): return None
    private(path, True)
    value = read(path/'owner.json')
    fields = {'schema_version','project','root','token','major','image','active','epoch','revision','operation','blocked','rollback'}
    check(isinstance(value, dict) and set(value) == fields and value['schema_version'] == 1)
    check(value['project'] == slug and HEX.fullmatch(value['token']) and HEX.fullmatch(value['epoch']))
    check(HEX.fullmatch(value['active']) and value['major'] == profile()['major'] and value['image'] == profile()['image'])
    operation=value['operation']
    check(operation is None or isinstance(operation,dict) and HEX.fullmatch(operation.get('id','')) and operation.get('action') in {'init','migrate','reset','restore','rotate','prune'} and operation.get('stage') in {'allocated','planned','running','unknown','complete','failed'})
    check(value['rollback'] is None or isinstance(value['rollback'],str) and HEX.fullmatch(value['rollback']))
    if operation:
        check(set(operation)<= {'id','action','stage','binding','selected','backup','generation','previous','next_epoch','old_epoch','rotation_stage'})
        for key in ('backup','generation','previous','next_epoch','old_epoch'):
            check(operation.get(key) is None or isinstance(operation[key],str) and HEX.fullmatch(operation[key]))
        check(operation.get('rotation_stage') is None or operation['rotation_stage'] in {'verified','selected','revoked'})
        selected=operation.get('selected')
        check(selected is None or isinstance(selected,str) and re.fullmatch(r'(?:(?:backup:|generation:)?[0-9a-f]{32})(?:,(?:backup:|generation:)?[0-9a-f]{32})*',selected))
        if 'binding' in operation:
            bound=operation['binding'];check(isinstance(bound,dict) and set(bound)=={'root','generation','epoch','revision','head','source'})
            check(bound['root']==value['root'] and HEX.fullmatch(bound['generation']) and HEX.fullmatch(bound['epoch']))
            check(bound['revision'] is None or isinstance(bound['revision'],str) and re.fullmatch(r'[A-Za-z0-9_]{1,32}',bound['revision']))
            check(isinstance(bound['head'],str) and re.fullmatch(r'[A-Za-z0-9_]{1,32}',bound['head']))
            check(isinstance(bound['source'],dict) and len(bound['source'])<=1000)
            for key,digest in bound['source'].items():check(isinstance(key,str) and re.fullmatch(r'[A-Za-z0-9._/-]{1,200}',key) and not key.startswith('/') and '..' not in Path(key).parts and isinstance(digest,str) and re.fullmatch(r'[0-9a-f]{64}',digest))
    check(type(value['blocked']) is bool and (value['revision'] is None or re.fullmatch(r'[A-Za-z0-9_]{1,32}',value['revision'])))
    check(isinstance(value['root'],str) and a.safe(value['root']).is_relative_to(a.PROJECTS))
    if root is not None: check(value['root'] == str(root), 'conflict')
    private(path/'postgres', True); private(path/'credentials', True); private(path/'backups', True)
    private(path/'postgres'/value['active'], True)
    for role in ROLES: credential(value, role)
    return value


def save(s):
    write(home(s['project'])/'owner.json', s)


def credential(s, role, epoch=None):
    check(role in ROLES)
    selected = epoch or s['epoch']; check(HEX.fullmatch(selected))
    folder = private(home(s['project'])/'credentials'/selected, True)
    value = read(folder/(role+'.json'))
    check(set(value) == {'username','password'} and value['username'] == role+'_'+selected[:16])
    check(isinstance(value['password'],str) and re.fullmatch(r'[0-9a-f]{64}',value['password']))
    return value


def credentials(path, epoch):
    folder = path/'credentials'/epoch
    if folder.exists():private(folder,True)
    else:folder.mkdir(mode=0o700)
    for role in ROLES:
        value = read(folder/(role+'.json')) if (folder/(role+'.json')).exists() else {'username':role+'_'+epoch[:16], 'password':secrets.token_hex(32)}
        check(value['username']==role+'_'+epoch[:16] and re.fullmatch(r'[0-9a-f]{64}',value['password']))
        write(folder/(role+'.json'),value)
        # Fixed container paths; values are never part of argv or environment.
        for suffix, content in [('password',value['password']),('passfile','*:*:*:'+value['username']+':'+value['password']+'\n')]:
            file = folder/(role+'.'+suffix)
            if file.exists():
                private(file);check(file.read_text()==content,'database-recovery');continue
            fd = os.open(file, os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW, 0o600)
            with os.fdopen(fd,'w') as stream:
                stream.write(content); stream.flush(); os.fsync(stream.fileno())


def create(root, contract):
    """Allocate only a previously absent owned database root; no implicit recovery."""
    mount(); slug=contract['project']['id']; path=home(slug)
    check(not path.exists() and not path.is_symlink(), 'conflict')
    a.safe(BASE)
    if BASE == a.STORE/'data/projects':
        a.ensure_store();private(a.STORE,True)
        for directory in (BASE.parent,BASE):
            if not directory.exists():directory.mkdir(mode=0o700)
            private(directory,True)
    else:
        BASE.mkdir(mode=0o700,parents=True,exist_ok=True);private(BASE,True)
    path.mkdir(mode=0o700)
    for child in ('postgres','credentials','backups'): (path/child).mkdir(mode=0o700)
    generation=uuid.uuid4().hex; epoch=uuid.uuid4().hex
    (path/'postgres'/generation).mkdir(mode=0o700); credentials(path,epoch)
    s={'schema_version':1,'project':slug,'root':str(root),'token':uuid.uuid4().hex,
       'major':profile()['major'],'image':profile()['image'],'active':generation,'epoch':epoch,
       'revision':None,'operation':{'id':uuid.uuid4().hex,'action':'init','stage':'allocated'},'blocked':True,'rollback':None}
    save(s); return s


def name(s, generation=None):
    return 'gptclaw-db-'+s['project']+'-'+(generation or s['active'])[:12]


def backend(s): return 'gptclaw-dbnet-'+s['project']


def network(s, create=False):
    owned=a.object_owned('network',backend(s),s['token'])
    if not owned and create:
        a.command(['podman','network','create','--internal','--label',a.LABEL+'='+s['token'],backend(s)])
    return owned


def acquire():
    check(platform.system()=='Linux' and platform.machine() in {'x86_64','amd64'},'database-profile')
    p=profile()
    if a.command(['podman','image','exists',p['image']],optional=True).returncode:
        a.command(['podman','pull','--platform=linux/amd64',p['image']])
    info=a.json_command(['podman','image','inspect',p['image']])[0]
    check(info['Architecture']=='amd64' and info['Os']=='linux','database-profile')
    observed=a.command(['podman','run','--rm','--network=none','--entrypoint=postgres',p['image'],'--version']).stdout.strip()
    check(re.fullmatch(r'postgres \(PostgreSQL\) 18\.[0-9]+(?: .*|)',observed), 'database-profile')
    return observed


def unit(s):
    return a.UNITS/(name(s)+'.container')


def unit_text(s):
    p=profile(); folder=home(s['project']); role=credential(s,'admin'); cfg=folder/'credentials'/s['epoch']
    for suffix in ('password','passfile'): private(cfg/('admin.'+suffix))
    return f'''[Unit]
Description=GptClaw development database {s['project']}
StartLimitIntervalSec=60
StartLimitBurst=3
[Container]
Image={s['image']}
ContainerName={name(s)}
Label={a.LABEL}={s['token']}
UserNS=keep-id
User={os.getuid()}:{os.getgid()}
Network={backend(s)}
PodmanArgs=--network-alias=db --cpus=1 --memory=1024m --entrypoint=/usr/bin/bash
Volume={folder/'postgres'/s['active']}:/var/lib/postgresql/data:rw
Volume={cfg/'admin.password'}:/run/secrets/admin.password:ro
Volume={cfg/'admin.passfile'}:/run/secrets/admin.passfile:ro
Volume={a.provider_bundle()/'templates/apps/start-development-postgres.sh'}:/opt/gptclaw/start-postgres.sh:ro
Environment=PGDATA=/var/lib/postgresql/data
Environment=POSTGRES_USER={role['username']}
Environment=POSTGRES_DB=app
Environment=POSTGRES_PASSWORD_FILE=/run/secrets/admin.password
Environment=POSTGRES_INITDB_ARGS=--auth-host=scram-sha-256 --auth-local=scram-sha-256
Exec=/opt/gptclaw/start-postgres.sh -c max_connections=30 -c log_statement=none -c log_min_error_statement=panic -c log_connections=off -c log_disconnections=off
Pull=never
NoNewPrivileges=true
DropCapability=all
PidsLimit=128
[Service]
Restart=on-failure
RestartSec=2
TimeoutStartSec=120
TimeoutStopSec=60
[Install]
WantedBy=default.target
'''


def verify_unit(s):
    path=a.safe(unit(s));private(path)
    actual=path.read_text();expected=unit_text(s)
    if actual!=expected:
        # Reconcile only a byte-identical trusted bootstrap path across source
        # and immutable provider runners. Every other unit byte must match.
        suffix=':/opt/gptclaw/start-postgres.sh:ro'
        lines=[line for line in actual.splitlines() if line.startswith('Volume=') and line.endswith(suffix)]
        check(len(lines)==1,'conflict')
        selected=a.safe(Path(lines[0][len('Volume='):-len(suffix)]))
        relative=Path('templates/apps/start-development-postgres.sh')
        provider=a.STORE/'providers'
        known=selected in {a.REPO/relative,a.PROJECTS/'gptclaw'/relative}
        if selected.is_relative_to(provider):
            parts=selected.relative_to(provider).parts
            known=known or len(parts)==4 and bool(re.fullmatch(r'[0-9a-f]{64}',parts[0])) and Path(*parts[1:])==relative
        check(known and selected.is_file(),'conflict')
        info=selected.stat()
        check(info.st_uid==os.getuid() and info.st_nlink==1 and not info.st_mode&0o002
              and (not info.st_mode&0o020 or info.st_gid==os.getgid()),'conflict')
        trusted=a.provider_bundle()/relative
        check(info.st_size==trusted.stat().st_size and selected.read_bytes()==trusted.read_bytes(),'conflict')
        old=lines[0];new='Volume='+str(trusted)+suffix
        check(actual.replace(old,new,1)==expected,'conflict')
    observed=a.command(['systemctl','--user','show',name(s)+'.service','-p','SourcePath','-p','DropInPaths'])
    values=dict(line.split('=',1) for line in observed.stdout.splitlines() if '=' in line)
    check(values.get('SourcePath')==str(path) and not values.get('DropInPaths'),'conflict')


def active(s, generation=None):
    container=name(s,generation)
    if not a.object_owned('container',container,s['token']):return False
    return a.json_command(['podman','container','inspect',container])[0]['State']['Running']


def start(s, generation=None):
    """Activate only owned storage; an initialized missing PG_VERSION is an error."""
    private(home(s['project'])/'postgres'/(generation or s['active']),True)
    if generation is None and s['revision'] is not None:
        pg=home(s['project'])/'postgres'/s['active']/'PG_VERSION'
        check(pg.is_file() and not pg.is_symlink() and pg.read_text().strip()=='18','database-storage')
    network(s,True)
    if active(s,generation): return
    if generation:
        role=credential(s,'admin'); cfg=home(s['project'])/'credentials'/s['epoch']
        args=['podman','run','--detach','--name',name(s,generation),'--label',a.LABEL+'='+s['token'],
              '--userns=keep-id','--user',str(os.getuid())+':'+str(os.getgid()),'--network='+backend(s),
              '--cpus=1','--memory=1024m','--pids-limit=128','--cap-drop=all','--security-opt=no-new-privileges','--entrypoint=/usr/bin/bash',
              '--volume',str(a.REPO/'templates/apps/start-development-postgres.sh')+':/opt/gptclaw/start-postgres.sh:ro',
              '--volume',str(home(s['project'])/'postgres'/generation)+':/var/lib/postgresql/data:rw',
              '--volume',str(cfg/'admin.password')+':/run/secrets/admin.password:ro',
              '--volume',str(cfg/'admin.passfile')+':/run/secrets/admin.passfile:ro',
              '--env','PGDATA=/var/lib/postgresql/data','--env','POSTGRES_USER='+role['username'],
              '--env','POSTGRES_DB=app','--env','POSTGRES_PASSWORD_FILE=/run/secrets/admin.password',
              '--env','POSTGRES_INITDB_ARGS=--auth-host=scram-sha-256 --auth-local=scram-sha-256',
              s['image'],'/opt/gptclaw/start-postgres.sh','-c','max_connections=30','-c','log_statement=none','-c','log_min_error_statement=panic']
        a.command(args)
    else:
        text=unit_text(s); target=a.safe(unit(s))
        a.safe(a.UNITS);a.UNITS.mkdir(parents=True,exist_ok=True)
        if target.exists(): check(target.read_text()==text,'conflict')
        else:
            a.save_text(target,text);target.chmod(0o600)
        a.command(['systemctl','--user','daemon-reload']);verify_unit(s)
        a.command(['systemctl','--user','start',name(s)+'.service'],timeout=150)
    until=time.monotonic()+120
    while time.monotonic()<until:
        try:
            if sql(s,'SELECT 1;',generation=generation).strip()=='1':return
        except a.AppError:pass
        time.sleep(.25)
    raise a.AppError('database-health')


def stop(s, generation=None):
    check(not busy(s),'busy')
    container=name(s,generation)
    if generation is None and unit(s).exists():
        verify_unit(s)
        a.command(['systemctl','--user','stop',container+'.service'],timeout=90)
        check(not active(s),'database-health')
        a.safe(unit(s)).unlink()
        a.command(['systemctl','--user','daemon-reload'])
    elif a.object_owned('container',container,s['token']):
        a.command(['podman','stop','--time=60',container],timeout=90)
        a.command(['podman','rm',container])
    check(not active(s,generation),'database-health')


def execute(args, payload=None, output=None, limit=65536):
    """Stream bounded native output without restricting Podman's metadata files."""
    env={'HOME':'/home/forge','PATH':'/usr/local/bin:/usr/bin:/bin','XDG_RUNTIME_DIR':'/run/user/'+str(os.getuid())}
    ceiling=profile()['limits']['dump_bytes'] if output is not None else limit
    process=subprocess.Popen(args,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,env=env)
    def feed():
        try:
            if payload:process.stdin.write(payload)
        except (BrokenPipeError,OSError):pass
        finally:
            try:process.stdin.close()
            except (BrokenPipeError,OSError):pass
    writer=threading.Thread(target=feed,daemon=True);writer.start()
    captured=bytearray();total=0;deadline=time.monotonic()+300
    try:
        with selectors.DefaultSelector() as selector:
            selector.register(process.stdout,selectors.EVENT_READ)
            while selector.get_map():
                if time.monotonic()>deadline:raise a.AppError('timeout')
                for key,_ in selector.select(.2):
                    chunk=os.read(key.fileobj.fileno(),65536)
                    if not chunk:selector.unregister(key.fileobj);continue
                    total+=len(chunk);check(total<=ceiling,'database-capacity')
                    if output is None:captured.extend(chunk)
                    else:output.write(chunk)
            check(process.wait(timeout=max(.1,deadline-time.monotonic()))==0,'database-command')
        return bytes(captured)
    except subprocess.TimeoutExpired:raise a.AppError('timeout') from None
    finally:
        if process.poll() is None:process.kill();process.wait()
        process.stdout.close();writer.join(timeout=1)


def client(s, executable, role='admin', generation=None):
    user=credential(s,role)['username']
    return ['podman','exec','--interactive','--env','PGPASSFILE=/run/secrets/admin.passfile',name(s,generation),
            executable,'--host=127.0.0.1','--username='+user,'--dbname=app']


def sql(s, statement, generation=None):
    return execute([*client(s,'psql',generation=generation),'-X','-A','-t','--set=ON_ERROR_STOP=1'],statement.encode()).decode()


def grants(s, generation=None, epoch=None):
    roles={role:credential(s,role,epoch) for role in ('runtime','migration')}
    statements=['REVOKE ALL ON DATABASE app FROM PUBLIC;','REVOKE ALL ON SCHEMA public FROM PUBLIC;']
    for kind,value in roles.items():
        role=value['username']; password=value['password']
        statements += [f"DO $gptclaw$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='{role}') THEN CREATE ROLE {role} LOGIN PASSWORD '{password}' NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION; END IF; END $gptclaw$;",
                       f'GRANT CONNECT ON DATABASE app TO {role};',f'GRANT USAGE ON SCHEMA public TO {role};']
        if kind=='migration':statements += [f'GRANT CREATE ON SCHEMA public TO {role};']
    migration=roles['migration']['username']; runtime=roles['runtime']['username']
    # Foreign-key triggers execute as the table owner. Keeping an old table
    # owner after changing the schema owner can make writes fail even when the
    # new runtime login has CRUD grants. Transfer only retained, validated
    # project migration identities; never administrative/runtime identities.
    for folder in sorted((home(s['project'])/'credentials').iterdir()):
        if not HEX.fullmatch(folder.name):continue
        previous=credential(s,'migration',folder.name)['username']
        if previous==migration:continue
        statements += [f"DO $gptclaw$ BEGIN IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname='{previous}') THEN REASSIGN OWNED BY {previous} TO {migration}; END IF; END $gptclaw$;"]
    statements += [f'ALTER SCHEMA public OWNER TO {migration};',f'GRANT SELECT,INSERT,UPDATE,DELETE ON ALL TABLES IN SCHEMA public TO {runtime};',
                   f'GRANT USAGE,SELECT ON ALL SEQUENCES IN SCHEMA public TO {runtime};',
                   f'ALTER DEFAULT PRIVILEGES FOR ROLE {migration} IN SCHEMA public GRANT SELECT,INSERT,UPDATE,DELETE ON TABLES TO {runtime};',
                   f'ALTER DEFAULT PRIVILEGES FOR ROLE {migration} IN SCHEMA public GRANT USAGE,SELECT ON SEQUENCES TO {runtime};']
    sql(s,'\n'.join(statements),generation)


def revision(s, generation=None):
    value=sql(s,"SELECT CASE WHEN to_regclass('public.alembic_version') IS NULL THEN '' ELSE 'present' END;",generation).strip()
    if not value:return None
    result=sql(s,'SELECT version_num FROM public.alembic_version;',generation).strip()
    check(re.fullmatch(r'[A-Za-z0-9_]{1,32}',result),'database-schema');return result


def ready(s, contract):
    if contract.get('database',{}).get('storage')!=STORAGE:return False
    try:return not s['blocked'] and active(s) and revision(s)==contract['database']['head']==s['revision']
    except a.AppError:return False


def binding(root, contract, s):
    import project_dependencies as deps
    fingerprints={}
    api=root/contract['components']['api']['root']
    for path in sorted([api/'pyproject.toml',api/'uv.lock',api/'alembic.ini',*(api/'migrations').rglob('*.py'),*(api/'src').rglob('*.py')]):
        fingerprints[str(path.relative_to(api))]=hashlib.sha256(deps.read_bytes(path,2*1024*1024)).hexdigest()
    return {'root':str(root),'generation':s['active'],'epoch':s['epoch'],'revision':s['revision'],
            'head':contract['database']['head'],'source':fingerprints}


def busy(s):
    return a.object_owned('container','gptclaw-dbjob-'+s['project'],s['token'])


def stopped(root):
    import project_groups as g
    root,value=a.target(root)
    owned=state(value['project']['id'],root)
    if owned:check(not busy(owned),'busy')
    with g.scope(root,value) as children:
        receipt=g.reserve(root,value);g.stopped(receipt,children)
    return root,value


def job(root, contract, s, action, role='migration', generation=None):
    """Run source only in a scoped prepared API container; mount one role file."""
    import project_groups as g
    import project_toolchains as tools
    import project_python as py
    with g.scope(root,contract) as children:
        path,child=children['api']; selected=tools.selection(path);runtime=a.reserve(path,child)
        a.prepare(runtime,child,False)
    folder=home(s['project'])/'credentials'/s['epoch']; private(folder/(role+'.json'))
    host=name(s,generation)
    # Source commands see only safe endpoint/path configuration; PostgreSQL resolves via the owned container name.
    check(not busy(s),'busy')
    args=['podman','run','--rm','--name','gptclaw-dbjob-'+s['project'],'--label',a.LABEL+'='+s['token'],
          '--userns=keep-id','--network='+backend(s),'--cpus=1','--memory=1536m','--pids-limit=256',
          '--cap-drop=all','--security-opt=no-new-privileges','--volume',str(path)+':/workspace:rw',
          '--volume',str(folder/(role+'.json'))+':/run/secrets/database.json:ro','--workdir=/workspace',
          '--env','GPTCLAW_DATABASE_FILE=/run/secrets/database.json','--env','GPTCLAW_DATABASE_HOST='+host,
          '--env','GPTCLAW_DATABASE_HEAD='+contract['database']['head']]
    for key,value in py.GUARD_ENV.items():args += ['--env',key+'='+value]
    args += [runtime['image'],'.venv/bin/python','-m','fastapi_app.db_cli',action]
    execute(args)


def allocate(s):
    path=home(s['project'])/'postgres'
    check(len(list(path.iterdir())) < 1+profile()['limits']['inactive_generations'],'database-capacity')
    check(shutil.disk_usage(path).free > profile()['limits']['headroom_bytes']+size(path/s['active']),'database-capacity')
    generation=uuid.uuid4().hex;(path/generation).mkdir(mode=0o700);return generation


def size(path):
    total=0
    for current,dirs,files in os.walk(path,followlinks=False):
        for entry in [*dirs,*files]:check(not (Path(current)/entry).is_symlink(),'path')
        for entry in files:total+=(Path(current)/entry).stat().st_size
    return total


def backups(s):
    path=home(s['project'])/'backups'; result={}
    for item in path.glob('*.json'):
        value=read(item);key=item.stem
        check(isinstance(value,dict) and set(value)=={'id','project','major','image','generation','revision','bytes','sha256','verified','created','records_digest'},'database-backup')
        check(HEX.fullmatch(value['generation']) and type(value['verified']) is bool and type(value['bytes']) is int and 0<value['bytes']<=profile()['limits']['dump_bytes'] and type(value['created']) is int,'database-backup')
        check(re.fullmatch(r'[0-9a-f]{64}',value['sha256']) and re.fullmatch(r'[0-9a-f]{32}',value['records_digest']),'database-backup')
        check(HEX.fullmatch(key) and value.get('id')==key and value.get('project')==s['project'])
        check(value.get('major')==s['major'] and value.get('image')==s['image'],'database-profile')
        dump=private(path/(key+'.dump'))
        check(dump.stat().st_size==value['bytes'] and hashlib.sha256(dump.read_bytes()).hexdigest()==value['sha256'],'database-backup')
        result[key]=value
    return result


def contents(s, generation=None):
    statement = """CREATE OR REPLACE FUNCTION pg_temp.gptclaw_contents() RETURNS text LANGUAGE plpgsql AS $digest$
    DECLARE entry record; value text; combined jsonb := '{}'::jsonb;
    BEGIN
      FOR entry IN SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename LOOP
        EXECUTE format('SELECT md5(coalesce(string_agg(row_to_json(r)::text, %L ORDER BY row_to_json(r)::text),%L)) FROM public.%I r', ',', '', entry.tablename) INTO value;
        combined := combined || jsonb_build_object(entry.tablename,value);
      END LOOP;
      RETURN md5(combined::text);
    END $digest$;
    SELECT pg_temp.gptclaw_contents();"""
    result=sql(s,statement,generation).strip().splitlines()[-1]
    check(re.fullmatch(r'[0-9a-f]{32}',result),'database-backup')
    return result

def backup(s, root, contract):
    limits=profile()['limits']; old=backups(s);path=home(s['project'])/'backups'
    check(len(old)<limits['backup_count'] and sum(x['bytes'] for x in old.values())+limits['dump_bytes']<=limits['backup_bytes'],'database-capacity')
    check(shutil.disk_usage(path).free>limits['dump_bytes']+limits['headroom_bytes'],'database-capacity')
    ident=uuid.uuid4().hex;target=path/(ident+'.partial')
    fd=os.open(target,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600)
    try:
        with os.fdopen(fd,'wb') as stream:
            execute([*client(s,'pg_dump'),'--format=custom'],output=stream)
            stream.flush();os.fsync(stream.fileno())
        check(target.stat().st_size<=limits['dump_bytes'],'database-capacity')
        value={'id':ident,'project':s['project'],'major':s['major'],'image':s['image'],
               'generation':s['active'],'revision':revision(s),'bytes':target.stat().st_size,
               'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'verified':False,'created':int(time.time()),'records_digest':contents(s)}
        os.rename(target,path/(ident+'.dump'));write(path/(ident+'.json'),value)
        verify_backup(s,value)
        value['verified']=True;write(path/(ident+'.json'),value);return value
    finally:
        if target.exists():target.unlink()


def restore_into(s, item, generation):
    dump=private(home(s['project'])/'backups'/(item['id']+'.dump'))
    check(hashlib.sha256(dump.read_bytes()).hexdigest()==item['sha256'],'database-backup')
    # Restore as the schema role so every application object retains migration ownership.
    grants(s,generation)
    selected=credential(s,'migration');passfile=private(home(s['project'])/'credentials'/s['epoch']/'migration.passfile')
    args=['podman','run','--rm','--interactive','--userns=keep-id','--user',str(os.getuid())+':'+str(os.getgid()),
          '--network='+backend(s),'--memory=1024m','--cpus=1','--pids-limit=128','--cap-drop=all','--security-opt=no-new-privileges',
          '--volume',str(passfile)+':/run/secrets/passfile:ro','--env','PGPASSFILE=/run/secrets/passfile',
          '--entrypoint=pg_restore',s['image'],'--host='+name(s,generation),'--username='+selected['username'],
          '--dbname=app','--exit-on-error','--no-owner','--no-acl']
    execute(args,dump.read_bytes(),limit=0)
    check(revision(s,generation)==item['revision'],'database-backup')
    check(contents(s,generation)==item['records_digest'],'database-backup')
    # Compare schema/data contents at SQL level without emitting note payloads.
    if sql(s,"SELECT to_regclass('public.notes') IS NOT NULL;",generation).strip()=='t':
        return sql(s,"SELECT count(*) FROM public.notes;",generation).strip()
    return '0'


def verify_backup(s, item):
    generation=allocate(s)
    try:
        start(s,generation);restore_into(s,item,generation)
    finally:
        stop(s,generation)
        # Verification generations are owned disposable allocations, never active.
        remove_generation(s,generation)


def remove_generation(s, generation):
    check(HEX.fullmatch(generation) and generation not in {s['active'],s['rollback']})
    check(not active(s,generation),'busy')
    path=private(home(s['project'])/'postgres'/generation,True)
    shutil.rmtree(path)


def plan(root, contract, s, action, selected=None):
    stopped(root);check(not (s['operation'] and s['operation']['action']=='rotate' and s['operation']['stage'] in {'failed','running'}),'database-recovery')
    check(s['operation'] is None or s['operation'].get('stage') in {'complete','failed','allocated','planned'},'database-recovery')
    check(action in {'migrate','reset','restore','rotate','prune'})
    if action=='restore':check(selected in backups(s),'database-backup')
    if action=='prune':
        ids=selected.split(',') if selected else []
        check(ids and len(ids)==len(set(ids)))
        old=backups(s)
        backup_ids=[x.split(':',1)[-1] for x in ids if not x.startswith('generation:')]
        check(all(x in old for x in backup_ids),'database-backup')
        check(any(x['verified'] and x['id'] not in backup_ids for x in old.values()),'database-backup')
        for value in ids:
            if value.startswith('generation:'):
                generation=value.split(':',1)[1]
                check(HEX.fullmatch(generation) and generation not in {s['active'],s['rollback']})
                private(home(s['project'])/'postgres'/generation,True)
    protected=s['operation'].get('backup') if s['operation'] else None
    operation={'id':uuid.uuid4().hex,'action':action,'stage':'planned','binding':binding(root,contract,s),'selected':selected,'backup':protected}
    s['operation']=operation;save(s)
    return {'project':s['project'],'state':'planned','operation_id':operation['id'],'action':action,
            'generation':s['active'],'source_revision':s['revision'],'target_revision':contract['database']['head'],
            'selected':selected,'confirmation':s['project']}


def apply(root, contract, s, ident, confirm):
    stopped(root);op=s['operation'];check(isinstance(op,dict) and (op['stage']=='planned' or op['action']=='rotate' and op['stage'] in {'failed','running'}),'database-recovery')
    check(op['id']==ident and confirm==s['project'],'database-confirmation')
    current=binding(root,contract,s)
    if op['action']=='rotate' and s['epoch']==op.get('next_epoch'):current['epoch']=op['binding']['epoch']
    check(op['binding']==current,'database-plan')
    action=op['action'];op['stage']='running';save(s)
    start(s)
    generation=None
    try:
        if action in {'migrate','reset','restore'}:
            if s['blocked'] and action=='restore':
                check(op['backup'] in backups(s) and backups(s)[op['backup']]['verified'],'database-backup')
            else:
                item=backup(s,root,contract);op['backup']=item['id'];save(s)
        if action=='migrate':
            check(revision(s)==s['revision'],'database-schema')
            s['blocked']=True;save(s);job(root,contract,s,'migrate')
            s['revision']=revision(s);check(s['revision']==contract['database']['head'],'database-schema')
        elif action in {'reset','restore'}:
            generation=allocate(s);op['generation']=generation;save(s);start(s,generation)
            if action=='restore':
                selected=backups(s)[op['selected']];check(selected['verified'] and selected['revision']==contract['database']['head'],'database-schema')
                restore_into(s,selected,generation)
            else:
                grants(s,generation);job(root,contract,s,'migrate',generation=generation)
            check(revision(s,generation)==contract['database']['head'],'database-schema')
            stop(s,generation);stop(s)
            previous=s['active'];s['active']=generation;s['revision']=contract['database']['head'];op['previous']=previous;s['rollback']=previous;save(s)
        elif action=='prune':
            old=backups(s)
            ids=op['selected'].split(',')
            backup_ids=[x.split(':',1)[-1] for x in ids if not x.startswith('generation:')]
            check(any(x['verified'] and x['id'] not in backup_ids for x in old.values()),'database-backup')
            for value in ids:
                if value.startswith('generation:'):
                    generation=value.split(':',1)[1]
                    check(generation not in {s['active'],s['rollback']})
                    remove_generation(s,generation)
                else:
                    key=value.split(':',1)[-1];check(key!=op.get('backup'))
                    for suffix in ('dump','json'):private(home(s['project'])/'backups'/(key+'.'+suffix)).unlink()
        elif action=='rotate':
            rotate(s)
        s['blocked']=False;op['stage']='complete';save(s)
    except a.AppError as error:
        s['blocked']=True;op['stage']='unknown' if error.code=='timeout' else 'failed';save(s);raise
    finally:
        if generation and generation!=s['active']:stop(s,generation)
        if not busy(s):stop(s)
    return {'project':s['project'],'state':'complete','operation_id':ident,'data_retained':True}


def rotate(s):
    """Resume staged rotation by epoch, selecting verified logins before revocation."""
    op=s['operation'];old=op.setdefault('old_epoch',s['epoch'])
    new=op.get('next_epoch')
    if new is None:
        new=uuid.uuid4().hex;op['next_epoch']=new;save(s)
        credentials(home(s['project']),new)
    else:
        credentials(home(s['project']),new)
        for role in ROLES:credential(s,role,new)
    if s['epoch']==old:
        grants(s,epoch=new)
        admin=credential(s,'admin',new)
        sql(s,f"DO $gptclaw$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='{admin['username']}') THEN CREATE ROLE {admin['username']} LOGIN SUPERUSER PASSWORD '{admin['password']}'; END IF; END $gptclaw$;")
        for role in ROLES:
            value=credential(s,role,new);file=home(s['project'])/'credentials'/new/(role+'.passfile')
            args=['podman','run','--rm','--userns=keep-id','--user',str(os.getuid()),'--network='+backend(s),
                  '--volume',str(file)+':/run/secrets/passfile:ro','--env','PGPASSFILE=/run/secrets/passfile',
                  '--entrypoint=psql',s['image'],'-h',name(s),'-U',value['username'],'-d','app','-X','-A','-t','-c','SELECT 1;']
            check(execute(args).strip()==b'1','database-command')
        for role in ('migration','runtime'):
            before=credential(s,role,old)['username'];after=credential(s,role,new)['username']
            sql(s,f'GRANT {before} TO {after};')
        op['rotation_stage']='verified';save(s)
        stop(s);s['epoch']=new;op['rotation_stage']='selected';save(s);start(s)
    check(s['epoch']==new,'database-recovery')
    for role in ROLES:
        before=credential(s,role,old)['username']
        sql(s,f'ALTER ROLE {before} NOLOGIN;')
    op['rotation_stage']='revoked';save(s)


def dispatch(root, action, selected=None, operation_id=None, confirm=None):
    root,contract=a.target(root);check(contract['schema_version']==4,'invalid');slug=contract['project']['id']
    if action=='status' and contract['database'].get('storage')!=STORAGE:
        return {'project':slug,'state':'storage-upgrade-required','minimum_provider':'1.8.2','data_retained':True}
    require_storage(contract)
    with a.locked(slug):
        s=state(slug,root)
        if action=='status':
            return {'project':slug,'state':'uninitialized' if s is None else 'recovery-required' if s['blocked'] else 'ready' if ready(s,contract) else 'stopped',
                    'generation':s['active'] if s else None,'revision':s['revision'] if s else None,
                    'credential_state':'configured' if s else 'unconfigured','operation':s['operation'] if s else None,
                    'backups':list(backups(s).values()) if s else [],'recovery':'local-only'}
        stopped(root)
        if action=='init':
            if s is None:
                check(operation_id is None,'conflict');acquire();s=create(root,contract)
            else:
                check(operation_id==s['operation']['id'] and s['operation']['action']=='init' and s['operation']['stage'] in {'allocated','failed'},'database-recovery')
                acquire()
            try:
                start(s);grants(s);job(root,contract,s,'migrate');s['revision']=revision(s)
                check(s['revision']==contract['database']['head'],'database-schema')
                s.update(blocked=False,operation={'id':s['operation']['id'],'action':'init','stage':'complete'});save(s)
            finally:stop(s)
            return {'project':slug,'state':'initialized','data_retained':True}
        check(s is not None,'database-state')
        if action=='recover':
            check(operation_id==s['operation']['id'] and confirm==slug,'database-confirmation')
            check(s['operation']['stage'] in {'running','unknown','failed'},'database-recovery')
            check(not busy(s),'busy');s['operation']['stage']='failed';s['blocked']=True;save(s)
            return {'project':slug,'state':'recovery-required','operation_id':operation_id,'data_retained':True}
        if operation_id:
            check(s['operation']['action']==action,'database-plan')
            return apply(root,contract,s,operation_id,confirm)
        if action in {'migrate','reset','restore','rotate','prune'}:return plan(root,contract,s,action,selected)
        if action in {'backup','seed'}:
            start(s)
            try:
                if action=='backup':return {'project':slug,'state':'backed-up','backup':backup(s,root,contract)}
                check(not s['blocked'],'database-recovery');job(root,contract,s,'seed',role='runtime')
                return {'project':slug,'state':'seeded'}
            finally:stop(s)
        raise a.AppError('invalid')


def logs(root, lines=80):
    """Read bounded owned DB logs and remove every retained credential value."""
    check(type(lines) is int and 1<=lines<=200,'invalid')
    root,contract=a.target(root);check(contract['schema_version']==4,'invalid')
    s=state(contract['project']['id'],root);check(s is not None,'database-state')
    check(a.object_owned('container',name(s),s['token']),'database-state')
    result=a.command(['podman','logs','--tail='+str(lines),name(s)])
    output=a.redact((result.stdout+'\n'+result.stderr)[-65536:])
    for folder in (home(s['project'])/'credentials').iterdir():
        check(HEX.fullmatch(folder.name),'database-state')
        for role in ROLES:output=output.replace(credential(s,role,folder.name)['password'],'[redacted]')
    return {'project':s['project'],'component':'db','state':'observed','logs':output}
