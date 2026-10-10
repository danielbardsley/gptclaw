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
import time
import urllib.error
import urllib.request
import uuid

from project_manifest import validate_project

VERSION = '1.2.0'
REPO = Path(__file__).resolve().parents[1]
PROJECTS = Path('/srv/forge/projects')
STORE = PROJECTS / '.gptclaw-runtime/v1'
UNITS = Path('/home/forge/.config/containers/systemd')
TEMPLATE = REPO / 'templates/apps/nextjs'
TEMPLATE_FILES = ['package.json','pnpm-lock.yaml','pnpm-workspace.yaml','next.config.ts',
 'next-env.d.ts','tsconfig.json','.gitignore','AGENTS.md.template','app/layout.tsx',
 'app/page.tsx','app/counter.tsx','app/globals.css','app/api/health/route.ts','tests/health.test.ts','README.md']
PORTS = range(18080, 18180)
INGRESS_PORT = 18079
LABEL = 'com.gptclaw.owner'
TOOLCHAIN = 'localhost/gptclaw-node:24.21.0-pnpm12.10.1'
MEMORY = '1536m'
CPU = '1'
PIDS = 256
DEADLINE = 120
MESSAGES = {
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
 finally:
  if temp.exists(): temp.unlink()


def ensure_store():
 safe(STORE); STORE.mkdir(parents=True, exist_ok=True, mode=0o700)
 need(STORE.stat().st_uid == os.getuid(), 'path')


@contextlib.contextmanager
def locked(name):
 ensure_store()
 path = STORE / (name + '.lock'); safe(path)
 fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
 try:
  info = os.fstat(fd)
  need(stat.S_ISREG(info.st_mode) and info.st_uid == os.getuid() and info.st_nlink == 1, 'path')
  try: fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
  except BlockingIOError: raise AppError('busy') from None
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
 root = safe(Path(root).absolute())
 need(root.is_relative_to(PROJECTS) and root != PROJECTS and root != REPO and '.gptclaw-runtime' not in root.parts, 'path')
 need(root.is_dir() and root.stat().st_uid == os.getuid(), 'path')
 result, contract, code = validate_project(root)
 need(code == 0, 'invalid')
 marker = read_json(root / '.gptclaw/template.json')
 need(marker == {'provider': 'nextjs-v1'}, 'invalid')
 need(not any((root/name).exists() for name in ['.env','.env.local','.env.development','.env.production','.npmrc','.ssh','.aws']),'invalid')
 return root, contract


def valid_state(s):
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
 need(s.get('phase') in {'preparing','starting','ready','stopped','failed'})
 need(type(s.get('health_ready')) is bool)
 if 'toolchain_hash' in s:need(isinstance(s['toolchain_hash'],str) and re.fullmatch(r'[0-9a-f]{64}',s['toolchain_hash']))
 need(s.get('operation') in {'start','stop','restart','test','deps'})
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
  s = valid_state(read_json(path)); need(path.stem == s['id']); result.append(s)
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
 labels = obj.get('Config',{}).get('Labels',{}) if kind == 'container' else obj.get('Labels',{})
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
 slug = contract['project']['id']
 with locked('registry'):
  s = state_for(slug)
  if s:
   need(s['root'] == str(root)); return s
  used = {x['port'] for x in states()}
  port = next((p for p in PORTS if p not in used and available(p)), None)
  need(port is not None, 'ports')
  s = {'schema_version':1,'id':slug,'root':str(root),'name':'gptclaw-app-'+slug,
       'token':uuid.uuid4().hex,'port':port,'phase':'preparing','image':'sha256:'+'0'*64,
       'unit_sha256':'0'*64,'operation_id':uuid.uuid4().hex,'operation':'start','health_ready':False}
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
       '--userns=keep-id','--network=slirp4netns','--memory='+MEMORY,'--cpus='+CPU,
       '--pids-limit='+str(PIDS),'--cap-drop=all','--security-opt=no-new-privileges',
       '--volume',s['root']+':/workspace:rw','--workdir','/workspace',
       '--env','GPTCLAW_PROJECT_ID='+s['id'],'--env','NEXT_TELEMETRY_DISABLED=1',
       '--env','NODE_OPTIONS=--max-old-space-size=1024']
 for key,value in deps.GUARD_ENV.items():args += ['--env',key+'='+value]
 if read_only_dependency_files:
  for name in deps.FILES:
   path=safe(Path(s['root'])/name);deps.read_bytes(path)
   args += ['--volume',str(path)+':/workspace/'+name+':ro']
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
 for name in ['package.json','pnpm-lock.yaml','pnpm-workspace.yaml']:
  path=safe(Path(s['root'])/name);need(path.is_file(),'invalid')
  digest.update(name.encode()+b'\0'+path.read_bytes())
 return digest.hexdigest()


def prepare(s,contract,build):
 import project_dependencies as deps
 digest=dependency_digest(s)
 if s.get('prepared_digest')==digest and (Path(s['root'])/'node_modules').is_dir() and (not build or s.get('build_digest')==digest):return
 before=deps.context(Path(s['root']))['hashes']
 run_in_app(s,['pnpm','install','--frozen-lockfile',*deps.INSTALL_FLAGS],read_only_dependency_files=True)
 deps.verify_original(Path(s['root']),before)
 if build:
  run_in_app(s,contract['commands']['build']);s['build_digest']=digest
 s['prepared_digest']=digest;save(STORE/(s['id']+'.json'),s)


def unit_text(s, contract, dns):
 import project_dependencies as deps
 argv = contract['commands']['start']
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
Network=slirp4netns
PublishPort=127.0.0.1:{s['port']}:{contract['service']['internal_port']}
Volume={s['root']}:/workspace:rw
WorkingDir=/workspace
Environment=GPTCLAW_PROJECT_ID={s['id']}
Environment=GPTCLAW_DEV_ORIGIN={dns}
Environment=NEXT_TELEMETRY_DISABLED=1
Environment=NODE_OPTIONS=--max-old-space-size=1024
{''.join('Environment='+key+'='+value+chr(10) for key,value in deps.GUARD_ENV.items())}\
Exec={' '.join(quote(v) for v in ([argv[0],'--config.@jsr:registry=https://registry.npmjs.org/',*argv[1:]] if argv and argv[0]=='pnpm' else argv))}
Pull=never
NoNewPrivileges=true
DropCapability=all
ReadOnly=true
PidsLimit={PIDS}
PodmanArgs=--cpus={CPU} --memory={MEMORY}

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
 return active, healthy(s,contract) if active else False


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
 import project_dependencies as deps
 root,contract=target(root);slug=contract['project']['id']
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
  return result


def stop(root, take_lock=True):
 root,contract=target(root);slug=contract['project']['id']
 with (locked(slug) if take_lock else contextlib.nullcontext()):
  s=state_for(slug)
  if not s:return {'project':slug,'state':'stopped','changed':False}
  need(s['root']==str(root))
  need(not object_owned('container',s['name']+'-job',s['token']),'busy')
  path=unit_path(s)
  if path.exists():verify_unit(s)
  container=object_owned('container',s['name'],s['token'])
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
 root,contract=target(root);slug=contract['project']['id']
 with locked(slug):
  before=state_for(slug)
  stopped=stop(root,take_lock=False)
  started=start(root,take_lock=False)
  s=state_for(slug);s.update(operation='restart',operation_id=uuid.uuid4().hex)
  save(STORE/(slug+'.json'),s)
  return {**started,'operation_id':s['operation_id'],'operation':'restart','changed':True,
          'transitions':[stopped.get('operation_id'),started.get('operation_id')]}


def status(root):
 root,contract=target(root);slug=contract['project']['id'];s=state_for(slug)
 if not s:return {'project':slug,'state':'stopped','health':'unknown'}
 need(s['root']==str(root));active,ready=inspect_service(s,contract)
 busy=object_owned('container',s['name']+'-job',s['token'])
 return {'project':slug,'operation_id':s['operation_id'],'last_operation':s['operation'],
         'state':'ready' if active and ready and s['phase']=='ready' and s['health_ready'] else 'unpublished' if active and ready else 'starting' if active else s['phase'] if s['phase'] in ('failed','preparing','starting') else 'stopped',
         'health':'ready' if ready else 'unhealthy' if active else 'unknown',
         'port':s['port'],'route':route_info(slug),'last_error':s.get('error'),'operation_busy':busy,'operation_result':s.get('operation_result')}


def test_app(root):
 import project_dependencies as deps
 root,contract=target(root);slug=contract['project']['id']
 with locked(slug):
  deps.require_clean(root,slug);deps.context(root)
  import project_toolchains as tools
  selected=tools.selection(root)
  s=reserve(root,contract)
  need(s['phase'] not in ('preparing','starting') or s['unit_sha256']=='0'*64,'busy')
  active,_=inspect_service(s,contract) if unit_path(s).exists() else (False,False)
  s.update(operation='test',operation_id=uuid.uuid4().hex,operation_result='running')
  save(STORE/(slug+'.json'),s)
  try:
   if not active:
    s['image']=toolchain(root);s['toolchain_hash']=selected['selection_hash'];prepare(s,contract,build=False)
   else:
    tools.assert_active(selected,s)
    need(s.get('prepared_digest')==dependency_digest(s),'busy')
   run_in_app(s,contract['commands']['test'])
  except AppError as error:
   s.update(operation_result='failed',error=error.code)
   if not active:s.update(phase='failed',health_ready=False)
   save(STORE/(slug+'.json'),s);raise
  s.update(operation_result='passed');s.pop('error',None)
  if not active:s.update(phase='stopped',health_ready=False)
  save(STORE/(slug+'.json'),s)
  return {'project':slug,'operation_id':s['operation_id'],'state':'tests-passed'}


def redact(text):
 text=re.sub(r'(?i)((?:password|secret|token|api[_-]?key)\s*[:=]\s*)[^\s,;]+',r'\1[redacted]',text)
 text=re.sub(r'(?i)(Bearer\s+)[A-Za-z0-9._~-]+',r'\1[redacted]',text)
 return text


def logs(root,lines):
 root,contract=target(root);s=state_for(contract['project']['id']);need(s is not None,'invalid')
 need(s['root']==str(root));need(1<=lines<=200,'invalid')
 if unit_path(s).exists():verify_unit(s)
 r=command(['journalctl','--user','-u',s['name']+'.service','--no-pager','-n',str(lines),'--since','1 hour ago'],timeout=15)
 return {'project':s['id'],'logs':redact(r.stdout[-32768:]),'max_lines':lines}


def create(slug,directory=None):
 need(re.fullmatch(r'[a-z][a-z0-9]*(?:-[a-z0-9]+)*',slug) and len(slug)<=48,'invalid')
 path=safe(Path(directory).absolute() if directory else PROJECTS/slug)
 need(path.is_relative_to(PROJECTS) and path!=PROJECTS and path!=REPO and '.gptclaw-runtime' not in path.parts,'path')
 need(path.parent.is_dir() and path.parent.stat().st_uid==os.getuid(),'path')
 try:path.mkdir(mode=0o700)
 except FileExistsError:raise AppError('conflict') from None
 for name in TEMPLATE_FILES:
  source=TEMPLATE/name
  relative=Path(name)
  need(not source.is_symlink(),'path')
  if source.is_file():
   target_file=path/relative;target_file.parent.mkdir(parents=True,exist_ok=True)
   if target_file.name=='AGENTS.md.template':target_file=target_file.with_name('AGENTS.md')
   with target_file.open('xb') as out:out.write(source.read_bytes())
 meta=path/'.gptclaw';meta.mkdir()
 # JSON is a strict YAML subset; reuse the existing validator without a second parser policy.
 contract={'schema_version':1,'project':{'id':slug,'name':slug.replace('-',' ').title(),'kind':'web'},
           'commands':{'build':['pnpm','build'],'start':['pnpm','dev'],'test':['pnpm','test']},
           'service':{'internal_port':3000,'health':{'path':'/projects/'+slug+'/api/health/','timeout_seconds':5}},
           'exposure':{'private':True,'base_path':'/projects/'+slug+'/','funnel':False},'data':{'mode':'ephemeral'}}
 save(meta/'project.yaml',contract);save(meta/'template.json',{'provider':'nextjs-v1'})
 import project_toolchains as tools
 save(meta/'toolchain.json',tools.default_declaration())
 need(validate_project(path)[2]==0,'invalid')
 return {'project':slug,'root':str(path),'state':'created'}


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
 with locked('ingress'):
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
 paths=[Path('scripts')/n for n in ['private_apps.py','private_ingress.py','project_manifest.py','project_dependencies.py','project_toolchains.py','gptclawctl.py','gptclawctl']]
 paths += [Path('config/project-dependencies/v1.json'),Path('schemas/project-dependencies/v1.schema.json')]
 paths += [Path('config/toolchains/v1.json'),Path('schemas/toolchains/v1.schema.json'),Path('templates/apps/node-toolchain/install-pnpm.cjs')]
 paths += [Path('schemas/project/v1.schema.json'),Path('templates/apps/node-toolchain/Containerfile')]
 paths += [Path('templates/apps/nextjs')/name for name in TEMPLATE_FILES]
 digest=hashlib.sha256()
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
 (temp/'.python-path').write_text(str(REPO/'.venv-manifest/bin/python')+'\n')
 (temp/'scripts/gptclawctl').chmod(0o755)
 os.rename(temp,dest)
 return dest
