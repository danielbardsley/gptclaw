"""Versioned rootless single-web-app lifecycle. No project code executes on the host."""
import contextlib
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import selectors
import shutil
import socket
import stat
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

from project_manifest import validate_project

VERSION = '1.17.0'
REPO = Path(__file__).resolve().parents[1]
PROJECTS = Path('/srv/forge/projects')
STORE = PROJECTS / '.gptclaw-runtime/v1'
UNITS = Path('/home/forge/.config/containers/systemd')
PORTS = range(18080, 18180)
INGRESS_PORT = 18079
LABEL = 'com.gptclaw.owner'
TOOLCHAIN = 'localhost/gptclaw-node:24.21.0-pnpm12.10.1'
MEMORY = '1536m'
CPU = '1'
PIDS = 256
DEADLINE = 120
MESSAGES = {
 'control-unsupported': 'This lifecycle action is unavailable for the selected profile or component.',
 'control-state': 'The selected runtime is not in a state that permits this action.',
 'control-paused': 'Resume or stop the paused project first.',
 'control-dependency': 'A required service is not ready; inspect dependencies before explicit recovery.',
 'control-recovery': 'An interrupted lifecycle operation requires explicit reconciliation before another write.',
 'control-expired': 'The existing Metro session authorization has expired or has insufficient time remaining.',
 'control-changed': 'The project, source or runtime changed; review a new action confirmation.',
 'control-capacity': 'The bounded lifecycle capacity was reached; inspect retained operations or build sources.',
 'metro-capacity': 'Owned Metro runtime retention reached its bounded capacity; inspect metro prune and remove only confirmed inactive generated copies. Source and unknown files are preserved.',
 'metro-prune-recovery': 'An owned Metro copy changed during cleanup; retain the prune-GENERATION staging directory and reconcile its identity before retrying. Canonical source is unchanged.',
 'metro-metadata-recovery': 'A Metro opt-in publication needs scoped reconciliation; inspect its owned metadata record and retained previous file before retrying.',
 'mobile-unsupported': 'Mobile source creation and quality checks are supported; Metro, device and native release operations are not available.',
 'mobile-policy': 'Mobile identity, SDK packages or source configuration do not match the reviewed Expo profile.',
 'database-state': 'Database ownership or persisted state is invalid; no data was initialized or removed.',
 'database-storage': 'Expected persistent database storage is missing or incompatible; use reviewed recovery.',
 'database-profile': 'The exact PostgreSQL profile or data major is incompatible.',
 'database-health': 'The owned database did not reach authenticated readiness.',
 'database-command': 'A scoped database operation failed; credentials and SQL diagnostics were suppressed.',
 'database-schema': 'The database schema does not match the declared migration revision.',
 'database-capacity': 'Database backup or generation limits require reviewed pruning or more capacity.',
 'database-backup': 'The selected database backup is invalid or lacks required verification.',
 'database-recovery': 'A database operation needs explicit recovery before publication.',
 'database-confirmation': 'Apply requires the matching operation ID and exact project confirmation.',
 'database-plan': 'The database plan is stale; prepare a new plan.',
 'invalid': 'Invalid project manifest or unsupported runtime target.',
 'path': 'Use a regular, owned project directory under the projects root; symlinks and unsafe paths are unsupported.',
 'conflict': 'Existing state, resources or route belong to a different target; nothing was overwritten.',
 'busy': 'An operation is already running for this target; observe its status before retrying.',
 'command': 'A scoped runtime command failed; inspect bounded logs for this project.',
 'timeout': 'The operation timed out; reconcile this target with status before retrying.',
 'health': 'The service did not become healthy within its deadline; inspect this project status/logs.',
 'ports': 'No free port is available in the configured range.',
 'operator': 'The private ingress route needs the existing operator to configure it; no permissions were changed.',
 'setup': 'The reviewed Python environment, rootless runtime or toolchain is unavailable.',
 'dependency-policy': 'Dependency files, sources or configuration do not satisfy the reviewed project policy.',
 'dependency-recovery': 'A dependency operation needs reconciliation with deps status and its operation ID before retrying.',
 'toolchain-policy': 'Toolchain declarations, versions or metadata do not match a reviewed supported profile.',
 'toolchain-platform': 'This toolchain supports Linux amd64 only; no fallback was selected.',
 'toolchain-verification': 'The selected image failed its exact executable or artifact verification.',
 'toolchain-recovery': 'An interrupted toolchain acquisition needs scoped operator reconciliation; inspect its receipt before retrying.',
 'template-policy': 'Template selection, release assets or provenance do not match a supported reviewed release.',
 'internal': 'Runtime state could not be reconciled; inspect this target before retrying.',
}


class AppError(Exception):
 def __init__(self, code):
  self.code = code
  super().__init__(MESSAGES[code])


def need(ok, code='conflict'):
 if not ok: raise AppError(code)


def safe(path):
 path = Path(path)
 need(path.is_absolute() and '..' not in path.parts and re.fullmatch(r'[A-Za-z0-9/._-]+', str(path)), 'path')
 for p in [path, *path.parents]:
  if p.exists() or p.is_symlink(): need(not p.is_symlink(), 'path')
 return path


def read_json(path):
 safe(path)
 try:
  fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
  with os.fdopen(fd,'r') as source:
   info=os.fstat(source.fileno())
   need(stat.S_ISREG(info.st_mode) and info.st_uid==os.getuid() and info.st_nlink==1,'path')
   need(info.st_size<=65536,'conflict')
   return json.loads(source.read(65537))
 except FileNotFoundError: return None
 except (ValueError, OSError): raise AppError('conflict') from None


def save(path, value):
 safe(path)
 temp = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
 fd = os.open(temp, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
 try:
  with os.fdopen(fd, 'w') as out:
   json.dump(value, out, sort_keys=True, indent=2); out.write('\n'); out.flush(); os.fsync(out.fileno())
  os.replace(temp, path)
  directory_fd=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
  try:os.fsync(directory_fd)
  finally:os.close(directory_fd)
 finally:
  if temp.exists(): temp.unlink()


def ensure_store():
 safe(STORE); STORE.mkdir(parents=True, exist_ok=True, mode=0o700)
 need(STORE.stat().st_uid == os.getuid(), 'path')


@contextlib.contextmanager
def locked(name, *, project_guard=True):
 import project_controls as controls
 if controls.HELD.get() == name:
  if project_guard:controls.check_guard(name)
  yield
  return
 ensure_store()
 path = STORE / (name + '.lock'); safe(path)
 fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
 try:
  info = os.fstat(fd)
  need(stat.S_ISREG(info.st_mode) and info.st_uid == os.getuid() and info.st_nlink == 1, 'path')
  try: fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
  except BlockingIOError: raise AppError('busy') from None
  if project_guard:controls.check_guard(name)
  yield
 finally: os.close(fd)


def command(args, timeout=300, optional=False):
 env = {'HOME': '/home/forge', 'PATH': '/usr/local/bin:/usr/bin:/bin',
        'XDG_RUNTIME_DIR': '/run/user/1002', 'DBUS_SESSION_BUS_ADDRESS': 'unix:path=/run/user/1002/bus'}
 try:p=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env)
 except OSError:raise AppError('setup') from None
 out,err=bytearray(),bytearray();deadline=time.monotonic()+timeout
 try:
  with selectors.DefaultSelector() as selector:
   selector.register(p.stdout,selectors.EVENT_READ,out);selector.register(p.stderr,selectors.EVENT_READ,err)
   while selector.get_map():
    if time.monotonic()>=deadline:raise AppError('timeout')
    for key,_ in selector.select(min(.2,max(0,deadline-time.monotonic()))):
     chunk=os.read(key.fileobj.fileno(),65536)
     if not chunk:selector.unregister(key.fileobj);continue
     buffer=key.data
     if len(buffer)<1048576:buffer.extend(chunk[:1048576-len(buffer)])
  p.wait(timeout=max(.1,deadline-time.monotonic()))
 except (AppError,subprocess.TimeoutExpired):
  p.terminate()
  try:p.wait(timeout=2)
  except subprocess.TimeoutExpired:p.kill();p.wait()
  raise AppError('timeout') from None
 finally:p.stdout.close();p.stderr.close()
 r=subprocess.CompletedProcess(args,p.returncode,out.decode('utf-8','replace'),err.decode('utf-8','replace'))
 if r.returncode and not optional:raise AppError('command')
 return r


def json_command(args):
 try: return json.loads(command(args).stdout)
 except ValueError: raise AppError('command') from None


def target(root):
 from project_worktrees import guard
 guard(root)
 root = safe(Path(root).absolute())
 need(root.is_relative_to(PROJECTS) and root != PROJECTS and root != REPO and '.gptclaw-runtime' not in root.parts, 'path')
 need(root.is_dir() and root.stat().st_uid == os.getuid(), 'path')
 if (root/'.gptclaw/component.json').exists() or (root/'.gptclaw/component.json').is_symlink():
  import project_groups as groups
  return groups.component_target(root)
 result, contract, code = validate_project(root)
 need(code == 0, 'invalid')
 marker = read_json(root / '.gptclaw/template.json')
 need(marker == {'provider': 'nextjs-static-v1' if contract['schema_version']==10 else 'expo-notes-v1' if contract['schema_version']==9 else 'fastapi-postgres-v1' if contract['schema_version']==8 else 'expo-v1' if contract['schema_version'] in (5,6,9) else 'notes-postgres-v1' if contract['schema_version'] == 4 else 'notes-v1' if contract['schema_version'] == 3 else 'fastapi-v1' if contract['schema_version'] == 2 else 'fastify-v1' if contract['schema_version'] == 7 else 'nextjs-v1'}, 'invalid')
 import project_templates as templates
 templates.validate_provenance(root)
 need(not any((root/name).exists() for name in ['.env','.env.local','.env.development','.env.production','.npmrc','.ssh','.aws']),'invalid')
 return root, contract


def valid_state(s):
 if isinstance(s,dict) and s.get('schema_version') in (2,3,4):
  import project_groups as groups
  return groups.valid_state(s)
 need(isinstance(s, dict) and s.get('schema_version') == 1, 'conflict')
 need(isinstance(s.get('id'), str) and re.fullmatch(r'[a-z][a-z0-9]*(?:-[a-z0-9]+)*', s['id']) and len(s['id']) <= 48)
 need(s.get('name') == 'gptclaw-app-' + s['id'])
 need(isinstance(s.get('token'), str) and re.fullmatch(r'[0-9a-f]{32}', s['token']))
 need(type(s.get('port')) is int and s['port'] in PORTS)
 need(isinstance(s.get('root'), str))
 root = safe(Path(s['root']))
 need(root.is_relative_to(PROJECTS) and root != PROJECTS and root != REPO and '.gptclaw-runtime' not in root.parts, 'path')
 need(isinstance(s.get('unit_sha256'), str) and re.fullmatch(r'[0-9a-f]{64}', s['unit_sha256']))
 need(isinstance(s.get('image'), str) and re.fullmatch(r'sha256:[0-9a-f]{64}', s['image']))
 if 'adapter' in s: need(s['adapter'] == 'python')
 if 'group' in s:
  import project_groups as groups
  need(isinstance(s['group'],str) and re.fullmatch(r'[a-z][a-z0-9]*(?:-[a-z0-9]+)*',s['group']) and len(s['group'])<=48)
  need(s.get('component') in groups.ORDER and s['id']==groups.identity(s['group'],s['component']))
  need(s.get('network')=='gptclaw-group-'+s['group'] and s.get('network_alias')==s['component'])
  need(s.get('runtime_project_id')==s['group'] and isinstance(s.get('runtime_api_url'),str))
  try:api_url=urllib.parse.urlsplit(s['runtime_api_url']);api_port=api_url.port
  except ValueError:raise AppError('conflict') from None
  need(api_url.scheme=='http' and api_url.hostname=='api' and api_url.username is None and api_url.password is None and not api_url.query and not api_url.fragment)
  need(type(api_port) is int and 1024<=api_port<=65535 and re.fullmatch(r'/[A-Za-z0-9._/-]*',api_url.path) and not any(p in {'.','..'} for p in api_url.path.split('/')))
 need(s.get('phase') in {'preparing','starting','ready','stopped','failed','paused','pausing','resuming'})
 need(type(s.get('health_ready')) is bool)
 if 'toolchain_hash' in s:need(isinstance(s['toolchain_hash'],str) and re.fullmatch(r'[0-9a-f]{64}',s['toolchain_hash']))
 need(s.get('operation') in {'start','stop','restart','test','deps','build','format','lint','typecheck','security','verify','rebuild','pause','resume'})
 need(isinstance(s.get('operation_id'),str) and re.fullmatch(r'(?:prototype-)?[0-9a-f]{32}',s['operation_id']))
 need(s.get('error') is None or s['error'] in MESSAGES)
 need(s.get('operation_result') is None or s['operation_result'] in {'running','passed','failed','unknown'})
 for key in ['prepared_digest','build_digest']:
  need(s.get(key) is None or isinstance(s[key],str) and re.fullmatch(r'[0-9a-f]{64}',s[key]))
 return s


def state_for(slug):
 s = read_json(STORE / (slug + '.json'))
 if s is not None:
  valid_state(s); need(s['id'] == slug)
 return s


def states():
 if not STORE.exists(): return []
 result = []
 for path in STORE.glob('*.json'):
  if path.name.endswith('-prototype.json') or path.name=='ingress-owner.json': continue
  s = valid_state(read_json(path)); need(path.stem == s['id'])
  if s['schema_version']==1:result.append(s)
 return result


def unit_path(s): return UNITS / (s['name'] + '.container')


def verify_unit(s):
 path = safe(unit_path(s))
 need(path.is_file() and path.stat().st_uid == os.getuid() and path.stat().st_nlink==1)
 need(hashlib.sha256(path.read_bytes()).hexdigest() == s['unit_sha256'])
 r=command(['systemctl','--user','show',s['name']+'.service','-p','SourcePath','-p','DropInPaths'])
 properties=dict(line.split('=',1) for line in r.stdout.splitlines() if '=' in line)
 need(properties.get('SourcePath')==str(path) and not properties.get('DropInPaths'))


def object_owned(kind, name, token):
 r = command(['podman',kind,'exists',name], optional=True)
 if r.returncode:
  need(r.returncode == 1, 'command'); return False
 obj = json_command(['podman',kind,'inspect',name])[0]
 labels = obj.get('Config',{}).get('Labels',{}) if kind == 'container' else obj.get('Labels',obj.get('labels',{}))
 need(labels.get(LABEL) == token)
 return True


def available(port):
 try:
  with socket.socket() as sock:
   # Closed TCP connections in TIME_WAIT are reusable; active listeners are not.
   sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
   sock.bind(('127.0.0.1',port))
  return True
 except OSError: return False


def reserve(root, contract):
 need(contract['schema_version'] not in (5,6,9), 'mobile-unsupported')
 slug = contract['project']['id']
 with locked('registry',project_guard=False):
  s = state_for(slug)
  if s:
   need(s['schema_version']==1 and s['root'] == str(root))
   import project_groups as groups
   runtime=groups.component_runtime(root)
   if runtime and any(s.get(k)!=v for k,v in runtime.items()):
    need(s['phase']=='stopped','busy');s.update(runtime);save(STORE/(slug+'.json'),s)
   return s
  used = {x['port'] for x in states()}
  port = next((p for p in PORTS if p not in used and available(p)), None)
  need(port is not None, 'ports')
  s = {'schema_version':1,'id':slug,'root':str(root),'name':'gptclaw-app-'+slug,
       'token':uuid.uuid4().hex,'port':port,'phase':'preparing','image':'sha256:'+'0'*64,
       'unit_sha256':'0'*64,'operation_id':uuid.uuid4().hex,'operation':'start','health_ready':False}
  if contract['schema_version'] == 2: s['adapter'] = 'python'
  import project_groups as groups
  s.update(groups.component_runtime(root))
  save(STORE/(slug+'.json'),s); return s


def node_identity():
 s = json_command(['tailscale','status','--json'])
 need(s.get('BackendState') == 'Running' and s.get('Self',{}).get('Online'), 'setup')
 dns = s['Self']['DNSName'].rstrip('.')
 need(re.fullmatch(r'[a-z0-9.-]+\.ts\.net',dns), 'setup')
 return dns


def serve_config():
 config = json_command(['tailscale','serve','status','--json'])
 need(not any(config.get('AllowFunnel',{}).values()), 'conflict')
 return config


def route_info(slug):
 dns = node_identity(); config = serve_config()
 handlers = config.get('Web',{}).get(dns+':443',{}).get('Handlers',{})
 owned = handlers.get('/projects/')
 need(owned is None or owned == {'Proxy':f'http://127.0.0.1:{INGRESS_PORT}/projects/'})
 # A more-specific route must point to the same owned ingress, otherwise it bypasses lifecycle control.
 specific = handlers.get('/projects/'+slug+'/')
 need(specific is None, 'conflict')
 return {'state':'configured' if owned else 'operator-required',
         'url':f'https://{dns}/projects/{slug}/' if owned else None,
         'operator_command':['sudo','tailscale','serve','--bg','--https=443','--set-path=/projects/',
                             f'http://127.0.0.1:{INGRESS_PORT}/projects/'] if not owned else None}


def toolchain(root, selected=None):
 import project_toolchains as tools
 return tools.acquire(selected or tools.selection(root))['receipt']['image']


def run_in_app(s, argv, timeout=300, read_only_dependency_files=False):
 import project_dependencies as deps
 if argv and argv[0]=='pnpm':argv=[argv[0],'--config.@jsr:registry=https://registry.npmjs.org/',*argv[1:]]
 name = s['name']+'-job'
 # Never replace a pre-existing job, including one whose outcome is unknown after a timeout.
 exists = command(['podman','container','exists',name],optional=True)
 need(exists.returncode == 1, 'busy' if exists.returncode == 0 else 'command')
 args=['podman','run','--rm','--name',name,'--label',LABEL+'='+s['token'],
       '--userns=keep-id','--network='+s.get('job_network','slirp4netns'),'--memory='+MEMORY,'--cpus='+CPU,
       '--pids-limit='+str(PIDS),'--cap-drop=all','--security-opt=no-new-privileges',
       '--volume',s['root']+':/workspace:rw','--workdir','/workspace',
       '--env','GPTCLAW_PROJECT_ID='+s.get('runtime_project_id',s['id']),'--env','NEXT_TELEMETRY_DISABLED=1',
       '--env','NODE_OPTIONS=--max-old-space-size=1024']
 import project_python as py
 python_profile = s.get('adapter') == 'python' or py.is_python(s['root'])
 for key,value in (py.GUARD_ENV if python_profile else deps.GUARD_ENV).items():args += ['--env',key+'='+value]
 if read_only_dependency_files:
  for name in py.FILES if python_profile else deps.FILES:
   path=safe(Path(s['root'])/name);deps.read_bytes(path)
   args += ['--volume',str(path)+':/workspace/'+name+':ro']
 for key,value in s.get('job_env',{}).items():args += ['--env',key+'='+value]
 args += [s['image'],*argv]
 return command(args,timeout=timeout)


def dependency_digest(s):
 import project_dependencies as deps
 deps.require_clean(Path(s['root']),s['id'])
 context=deps.context(Path(s['root']))
 import project_toolchains as tools
 selected=tools.selection(Path(s['root']))
 if s.get('toolchain_hash'):need(s['toolchain_hash']==selected['selection_hash'],'busy')
 digest=hashlib.sha256(s['image'].encode())
 digest.update(context['policy_hash'].encode())
 digest.update(selected['selection_hash'].encode())
 import project_python as py
 for name in py.files_for(s['root']):
  path=safe(Path(s['root'])/name);need(path.is_file(),'invalid')
  digest.update(name.encode()+b'\0'+path.read_bytes())
 return digest.hexdigest()


def prepare(s,contract,build):
 import project_dependencies as deps
 digest=dependency_digest(s)
 import project_python as py
 python_profile = py.is_python(s['root'])
 if contract['schema_version'] != 10 and s.get('prepared_digest')==digest and (Path(s['root'])/('.venv' if python_profile else 'node_modules')).is_dir() and (not build or s.get('build_digest')==digest):return
 before=deps.context(Path(s['root']))['hashes']
 if python_profile: py.install(s,Path(s['root']))
 else: run_in_app(s,['pnpm','install','--frozen-lockfile',*deps.INSTALL_FLAGS],read_only_dependency_files=True)
 deps.verify_original(Path(s['root']),before)
 if build:
  run_in_app(s,contract['commands']['build']);s['build_digest']=digest
 s['prepared_digest']=digest;save(STORE/(s['id']+'.json'),s)


def unit_text(s, contract, dns):
 import project_dependencies as deps
 argv = contract['commands']['start']
 import project_python as py
 guard = py.GUARD_ENV if contract['schema_version'] == 2 else deps.GUARD_ENV
 import project_groups as groups
 database_config = groups.database_unit(s)
 def quote(value):
  # Quadlet Exec uses systemd argv parsing, not a shell. Escape its substitutions as well.
  return '"'+value.replace('\\','\\\\').replace('"','\\"').replace('%','%%').replace('$','$$')+'"'
 return f'''[Unit]
Description=GptClaw private application {s['id']}
StartLimitIntervalSec=60
StartLimitBurst=3

[Container]
Image={s['image']}
ContainerName={s['name']}
Label=com.gptclaw.project={s['id']}
Label={LABEL}={s['token']}
UserNS=keep-id
Network={s.get('network','slirp4netns')}
{database_config}PublishPort=127.0.0.1:{s['port']}:{contract['service']['internal_port']}
Volume={s['root']}:/workspace:rw
WorkingDir=/workspace
Environment=GPTCLAW_PROJECT_ID={s.get('runtime_project_id',s['id'])}
{('Environment=GPTCLAW_API_READY_URL='+s['runtime_api_url']+chr(10)) if s.get('component')=='web' else ''}
Environment=GPTCLAW_DEV_ORIGIN={dns}
Environment=NEXT_TELEMETRY_DISABLED=1
Environment=NODE_OPTIONS=--max-old-space-size=1024
{''.join('Environment='+key+'='+value+chr(10) for key,value in guard.items())}\
Exec={' '.join(quote(v) for v in ([argv[0],'--config.@jsr:registry=https://registry.npmjs.org/',*argv[1:]] if argv and argv[0]=='pnpm' else argv))}
Pull=never
NoNewPrivileges=true
DropCapability=all
ReadOnly=true
PidsLimit={PIDS}
PodmanArgs=--cpus={CPU} --memory={MEMORY}{(' --network-alias='+s['network_alias']) if s.get('group') else ''}

[Service]
ExecStartPre=/usr/bin/timeout 120 /bin/sh -c 'until /usr/bin/mountpoint -q /srv/forge; do sleep 1; done'
Restart=on-failure
RestartSec=2
TimeoutStartSec=300
TimeoutStopSec=20

[Install]
WantedBy=default.target
'''


class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self, *_): return None


def healthy(s, contract):
 try:
  # Avoid redirects, proxies and reading an unrestricted health payload.
  opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect())
  url=f"http://127.0.0.1:{s['port']}"+contract['service']['health']['path']
  with opener.open(url,timeout=min(contract['service']['health']['timeout_seconds'],5)) as r:
   return r.status == 200 and r.url == url
 except (OSError, urllib.error.URLError): return False


def inspect_service(s, contract):
 unit=unit_path(s)
 if unit.exists(): verify_unit(s)
 active = command(['systemctl','--user','is-active',s['name']+'.service'],optional=True).stdout.strip() == 'active'
 if active:
  need(object_owned('container',s['name'],s['token']))
  obj=json_command(['podman','container','inspect',s['name']])[0]
  image=obj.get('Image','');image=image if image.startswith('sha256:') else 'sha256:'+image
  need(image==s['image'],'conflict')
  binding=obj.get('HostConfig',{}).get('PortBindings',{}).get(str(contract['service']['internal_port'])+'/tcp',[])
  need(binding == [{'HostIp':'127.0.0.1','HostPort':str(s['port'])}])
 return active, healthy(s,contract) if active and not obj.get('State',{}).get('Paused',False) else False


def write_unit(s, text):
 safe(UNITS);UNITS.mkdir(parents=True,exist_ok=True)
 path=unit_path(s)
 if path.exists():verify_unit(s)
 s['unit_sha256']=hashlib.sha256(text.encode()).hexdigest()
 # Persist expected digest before publishing activation; interrupted writes remain diagnosable.
 save(STORE/(s['id']+'.json'),s)
 save_text(path,text)
 command(['systemctl','--user','daemon-reload'])


def save_text(path,text):
 safe(path);temp=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp')
 with temp.open('x') as f:f.write(text)
 os.replace(temp,path)


def start(root, no_route=False, take_lock=True):
 if target(root)[1]['schema_version'] in (5,6,9): raise AppError('mobile-unsupported')
 if target(root)[1]['schema_version'] in (3,4,8):
  import project_groups as groups
  return groups.start(root,no_route,take_lock)
 import project_dependencies as deps
 root,contract=target(root);slug=contract['project']['id']
 if contract['schema_version'] in (2,7) and not no_route: route_info(slug)
 with (locked(slug) if take_lock else contextlib.nullcontext()):
  deps.require_clean(root,slug);deps.context(root)
  import project_toolchains as tools
  selected=tools.selection(root)
  s=reserve(root,contract)
  active,ready=inspect_service(s,contract) if s['unit_sha256']!='0'*64 else (False,False)
  if active and ready:
   tools.assert_active(selected,s)
   s.update(phase='ready',health_ready=True,operation_result='passed');s.pop('error',None);save(STORE/(slug+'.json'),s)
   result={'operation_id':s['operation_id'],'project':slug,'state':'ready','changed':False,'port':s['port']}
  else:
   need(not active,'health')
   need(available(s['port']), 'conflict')
   s.update(operation_id=uuid.uuid4().hex,operation='start',operation_result='running',phase='preparing',health_ready=False)
   save(STORE/(slug+'.json'),s)
   try:
    s['image']=toolchain(root);s['toolchain_hash']=selected['selection_hash'];save(STORE/(slug+'.json'),s)
    prepare(s,contract,build=True)
    dns=node_identity()
    write_unit(s,unit_text(s,contract,dns));s['phase']='starting';save(STORE/(slug+'.json'),s)
    command(['systemctl','--user','start',s['name']+'.service'],timeout=300)
    deadline=time.monotonic()+DEADLINE
    while time.monotonic()<deadline:
     if healthy(s,contract):break
     time.sleep(1)
    else:raise AppError('health')
    need(inspect_service(s,contract)[0], 'health')
    s.update(phase='ready',health_ready=True,operation_result='passed');s.pop('error',None);save(STORE/(slug+'.json'),s)
   except AppError as error:
    s.update(phase='failed',health_ready=False,operation_result='failed',error=error.code);save(STORE/(slug+'.json'),s);raise
   result={'operation_id':s['operation_id'],'project':slug,'state':'ready','changed':True,'port':s['port']}
  result['local_url']=f"http://127.0.0.1:{s['port']}"+contract['exposure']['base_path']
  if not no_route:
   ensure_ingress();result['route']=route_info(slug)
   if result['route']['state']!='configured':result['state']='operator-required'
  if not no_route:
   import project_smoke
   smoke=project_smoke.after_start(root)
   if smoke is not None: result['smoke']=smoke
  return result


def stop(root, take_lock=True):
 if target(root)[1]['schema_version'] in (5,6,9): raise AppError('mobile-unsupported')
 if target(root)[1]['schema_version'] in (3,4,8):
  import project_groups as groups
  return groups.stop(root,take_lock)
 root,contract=target(root);slug=contract['project']['id']
 with (locked(slug) if take_lock else contextlib.nullcontext()):
  s=state_for(slug)
  if not s:return {'project':slug,'state':'stopped','changed':False}
  need(s['root']==str(root))
  need(not object_owned('container',s['name']+'-job',s['token']),'busy')
  path=unit_path(s)
  if path.exists():verify_unit(s)
  container=object_owned('container',s['name'],s['token'])
  if container and json_command(['podman','container','inspect',s['name']])[0].get('State',{}).get('Paused'):
   command(['podman','unpause',s['name']],timeout=30)
  changed=path.exists() or container or s['phase']!='stopped'
  s.update(phase='stopped',health_ready=False,operation='stop',operation_result='running',operation_id=uuid.uuid4().hex)
  save(STORE/(slug+'.json'),s) # Revoke ingress mapping first.
  if path.exists():
   command(['systemctl','--user','stop',s['name']+'.service']);path.unlink()
   command(['systemctl','--user','daemon-reload'])
   command(['systemctl','--user','reset-failed',s['name']+'.service'],optional=True)
  if object_owned('container',s['name'],s['token']):command(['podman','rm','--force',s['name']])
  need(available(s['port']), 'conflict')
  s['operation_result']='passed';save(STORE/(slug+'.json'),s)
  return {'operation_id':s['operation_id'],'project':slug,'state':'stopped','changed':changed,'source_retained':True}


def restart(root):
 if target(root)[1]['schema_version'] in (5,6,9): raise AppError('mobile-unsupported')
 if target(root)[1]['schema_version'] in (3,4,8):
  import project_groups as groups
  return groups.restart(root)
 root,contract=target(root);slug=contract['project']['id']
 with locked(slug):
  before=state_for(slug)
  need(not before or before['phase'] not in {'paused','pausing','resuming'},'control-paused')
  stopped=stop(root,take_lock=False)
  started=start(root,take_lock=False)
  s=state_for(slug);s.update(operation='restart',operation_id=uuid.uuid4().hex)
  save(STORE/(slug+'.json'),s)
  return {**started,'operation_id':s['operation_id'],'operation':'restart','changed':True,
          'transitions':[stopped.get('operation_id'),started.get('operation_id')]}


def status(root):
 if target(root)[1]['schema_version'] in (5,6,9): raise AppError('mobile-unsupported')
 if target(root)[1]['schema_version'] in (3,4,8):
  import project_groups as groups
  return groups.status(root)
 root,contract=target(root);slug=contract['project']['id'];s=state_for(slug)
 if not s:return {'project':slug,'state':'stopped','health':'unknown'}
 need(s['root']==str(root));active,ready=inspect_service(s,contract)
 busy=object_owned('container',s['name']+'-job',s['token'])
 return {'project':slug,'operation_id':s['operation_id'],'last_operation':s['operation'],
         'state':'paused' if s['phase']=='paused' else 'ready' if active and ready and s['phase']=='ready' and s['health_ready'] else 'unpublished' if active and ready else 'starting' if active else s['phase'] if s['phase'] in ('failed','preparing','starting') else 'stopped',
         'health':'ready' if ready else 'unhealthy' if active else 'unknown',
         'port':s['port'],'route':route_info(slug),'last_error':s.get('error'),'operation_busy':busy,'operation_result':s.get('operation_result')}


def test_app(root):
 return quality_app(root, 'test')


def quality_app(root, action='test'):
 if target(root)[1]['schema_version'] in (5,6,9):
  return __import__('project_mobile').quality(root,action)
 import project_dependencies as deps
 root,contract=target(root);slug=contract['project']['id']
 need(action in contract['commands'], 'invalid')
 with locked(slug):
  deps.require_clean(root,slug);deps.context(root)
  import project_toolchains as tools
  selected=tools.selection(root)
  s=reserve(root,contract)
  need(s['phase'] not in ('preparing','starting') or s['unit_sha256']=='0'*64,'busy')
  active,_=inspect_service(s,contract) if unit_path(s).exists() else (False,False)
  need(action != 'format' or not active, 'busy')
  need(not (contract['schema_version']==10 and active and action in ('build','verify')), 'busy')
  s.update(operation=action,operation_id=uuid.uuid4().hex,operation_result='running')
  save(STORE/(slug+'.json'),s)
  try:
   if not active:
    s['image']=toolchain(root);s['toolchain_hash']=selected['selection_hash'];prepare(s,contract,build=False)
   else:
    tools.assert_active(selected,s)
    need(s.get('prepared_digest')==dependency_digest(s),'busy')
   run_in_app(s,contract['commands'][action],read_only_dependency_files=contract['schema_version'] in (2,7,10))
  except AppError as error:
   s.update(operation_result='failed',error=error.code)
   if not active:s.update(phase='failed',health_ready=False)
   save(STORE/(slug+'.json'),s);raise
  s.update(operation_result='passed');s.pop('error',None)
  if not active:s.update(phase='stopped',health_ready=False)
  save(STORE/(slug+'.json'),s)
  return {'project':slug,'operation_id':s['operation_id'],'state':'tests-passed' if action=='test' else action+'-passed'}


def redact(text):
 text=re.sub(r'(?i)((?:password|secret|token|api[_-]?key)\s*[:=]\s*)[^\s,;]+',r'\1[redacted]',text)
 text=re.sub(r'(?i)(Bearer\s+)[A-Za-z0-9._~-]+',r'\1[redacted]',text)
 return text


def logs(root,lines):
 if target(root)[1]['schema_version'] in (5,6,9): raise AppError('mobile-unsupported')
 root,contract=target(root);s=state_for(contract['project']['id']);need(s is not None,'invalid')
 need(s['root']==str(root));need(1<=lines<=200,'invalid')
 if unit_path(s).exists():verify_unit(s)
 r=command(['journalctl','--user','-u',s['name']+'.service','--no-pager','-n',str(lines),'--since','1 hour ago'],timeout=15)
 return {'project':s['id'],'logs':redact(r.stdout[-32768:]),'max_lines':lines}


def create(slug,directory=None,template=None,template_version=None):
 import project_templates as templates
 need(re.fullmatch(r'[a-z][a-z0-9]*(?:-[a-z0-9]+)*',slug) and len(slug)<=48,'invalid')
 release,contents=templates.resolve(template,template_version)
 path=safe(Path(directory).absolute() if directory else PROJECTS/slug)
 need(path.is_relative_to(PROJECTS) and path!=PROJECTS and path!=REPO and '.gptclaw-runtime' not in path.parts,'path')
 need(path.parent.is_dir() and path.parent.stat().st_uid==os.getuid(),'path')
 # A pathname-derived lock serializes destinations even when slugs differ.
 key='create-'+hashlib.sha256(str(path).encode()).hexdigest()
 with locked(key):
  need(not path.exists() and not path.is_symlink(),'conflict')
  return templates.generate(path,slug,release,contents)


def ensure_ingress():
 safe(UNITS);UNITS.mkdir(parents=True,exist_ok=True)
 path=UNITS.parent.parent/'systemd/user/gptclaw-ingress.service';safe(path);path.parent.mkdir(parents=True,exist_ok=True)
 launcher=provider_bundle()/'scripts/gptclawctl'
 text=f'''[Unit]
Description=GptClaw private loopback app ingress

[Service]
ExecStart={launcher} ingress
Restart=on-failure
RestartSec=2
MemoryMax=192M
CPUQuota=50%
TasksMax=64
NoNewPrivileges=true

[Install]
WantedBy=default.target
'''
 with locked('ingress',project_guard=False):
  meta=read_json(STORE/'ingress-owner.json')
  # ingress-owner is not an app record; states() excludes it below.
  if path.exists():
   need(meta and meta.get('sha256')==hashlib.sha256(path.read_bytes()).hexdigest())
   observed=command(['systemctl','--user','show','gptclaw-ingress.service','-p','FragmentPath','-p','DropInPaths'])
   properties=dict(line.split('=',1) for line in observed.stdout.splitlines() if '=' in line)
   need(properties.get('FragmentPath')==str(path) and not properties.get('DropInPaths'))
  else:
   need(available(INGRESS_PORT),'conflict')
  link=STORE/'gptclawctl'
  if link.exists() or link.is_symlink():
   need(link.is_symlink() and meta and str(link.readlink())==meta.get('launcher'))
  temporary=STORE/('gptclawctl.'+uuid.uuid4().hex+'.tmp')
  temporary.symlink_to(launcher);os.replace(temporary,link)
  changed=not path.exists() or path.read_text()!=text
  if changed:
   save_text(path,text);save(STORE/'ingress-owner.json',{'sha256':hashlib.sha256(text.encode()).hexdigest(),'launcher':str(launcher)})
   command(['systemctl','--user','daemon-reload'])
   command(['systemctl','--user','enable','gptclaw-ingress.service'])
   command(['systemctl','--user','restart','gptclaw-ingress.service'])
  else:command(['systemctl','--user','start','gptclaw-ingress.service'])
  deadline=time.monotonic()+10
  while time.monotonic()<deadline:
   try:
    with urllib.request.urlopen(f'http://127.0.0.1:{INGRESS_PORT}/healthz',timeout=1) as response:
     if response.read(80)==('GptClaw ingress '+VERSION+'\n').encode():break
   except OSError:pass
   time.sleep(.1)
  else:raise AppError('health')
 return True


def provider_bundle():
 paths=[Path('scripts')/n for n in ['private_apps.py','private_ingress.py','project_manifest.py','project_dependencies.py','project_toolchains.py','gptclawctl.py','gptclawctl','project_repositories.py','repository_askpass.py','repository_credentials.py','repository_credential_helper.py','repository-credential-helper']]
 paths += [Path('scripts/project_smoke.py'),Path('scripts/project_quality_core.py')]
 paths += [Path('scripts/dashboard_controls.py'),Path('scripts/project_controls.py'),Path('scripts/project_worktrees.py'),Path('scripts/mobile_backend.py'),Path('schemas/project/v8.schema.json'),Path('schemas/project/v9.schema.json')]
 paths += [Path('scripts/project_mobile.py'), Path('scripts/expo_go.py'), Path('scripts/dashboard_go.py'), Path('config/mobile/expo-go-v1.json'), Path('scripts/metro_contract.py'), Path('scripts/metro_state.py'), Path('scripts/metro_protocol.py'), Path('scripts/metro_proxy.py'), Path('scripts/metro_routes.py'), Path('scripts/metro_retention.py'), Path('scripts/metro_sessions.py'), Path('scripts/metro_spike.py'), Path('scripts/metro_security.py'), Path('config/metro/runtime-security-v1.json'), Path('config/mobile/v1.json'), Path('schemas/project/v5.schema.json'), Path('schemas/project/v6.schema.json')]
 paths += [Path('scripts/dashboard_inventory.py'), Path('scripts/dashboard_collector.py'), Path('scripts/dashboard_observation.py'), Path('scripts/dashboard_status.py'), Path('scripts/dashboard_metro.py'), Path('scripts/dashboard_links.py')]
 paths += [Path('config/project-dependencies/v1.json'),Path('schemas/project-dependencies/v1.schema.json')]
 paths += [Path('config/toolchains/v1.json'),Path('schemas/toolchains/v1.schema.json'),Path('templates/apps/node-toolchain/install-pnpm.cjs')]
 paths += [Path('schemas/project/v1.schema.json'),Path('templates/apps/node-toolchain/Containerfile')]
 import project_templates as templates
 paths += templates.bundle_paths()
 paths += [Path(p) for p in ['scripts/project_python.py','scripts/project_groups.py','scripts/project_database.py','templates/apps/start-development-postgres.sh','scripts/tests/check_database_template.py','config/databases/v1.json','schemas/project/v4.schema.json','schemas/project/v3.schema.json','config/toolchains/v2.json','schemas/toolchains/v2.schema.json','config/project-dependencies/v2.json','schemas/project/v2.schema.json','templates/apps/python-toolchain/Containerfile']]
 interpreter=Path(sys.executable).absolute()
 digest=hashlib.sha256(str(interpreter).encode()+b'\0')
 for rel in sorted(paths):digest.update(str(rel).encode()+b'\0'+(REPO/rel).read_bytes())
 # A bundle already executing from installed storage reuses itself.
 if REPO.parent==STORE/'providers':return REPO
 dest=STORE/'providers'/digest.hexdigest()
 if dest.exists():
  for rel in paths:need((dest/rel).is_file() and (dest/rel).read_bytes()==(REPO/rel).read_bytes())
  return dest
 temp=dest.with_name(dest.name+'.'+uuid.uuid4().hex+'.tmp');temp.mkdir(parents=True,mode=0o700)
 for rel in paths:
  source=REPO/rel;safe(source);out=temp/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,out)
  if rel in {Path('scripts/repository_askpass.py'),Path('scripts/repository-credential-helper')}:out.chmod(0o700)
 (temp/'.python-path').write_text(str(interpreter)+'\n')
 (temp/'scripts/gptclawctl').chmod(0o755)
 os.rename(temp,dest)
 return dest


def install_hooks(root):
 if target(root)[1]['schema_version'] in (3,4,8):
  import project_groups as groups
  return groups.install_hooks(root)
 root,contract=target(root);need(contract['schema_version']==2,'invalid');slug=contract['project']['id']
 import project_dependencies as deps
 with locked(slug):
  deps.require_clean(root,slug);deps.context(root);deps.stopped_state(root,contract)
  directory=safe(root/'.git');need(directory.is_dir() and directory.stat().st_uid==os.getuid(),'conflict')
  hooks=safe(directory/'hooks');hooks.mkdir(exist_ok=True)
  snapshot=provider_bundle();launcher=snapshot/'scripts/gptclawctl'
  from project_worktrees import hook_text, hooks as upgrade_hooks
  upgrade_hooks(root,upgrade=True)
  text=hook_text(launcher)
  path=safe(hooks/'pre-commit')
  if path.exists():
   need(deps.read_bytes(path,65536)==text.encode(),'conflict');return {'project':slug,'state':'hooks-installed','changed':False}
  with path.open('xb') as stream:stream.write(text.encode())
  path.chmod(0o700)
  return {'project':slug,'state':'hooks-installed','changed':True}
