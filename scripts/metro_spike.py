#!/usr/bin/env python3
"""Bounded, owner-gated SDK spike; no Serve administration or source mutation."""
import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import stat
import math
import time
import threading
import subprocess
import re
from urllib.parse import urlsplit
import uuid

import private_apps as app
import metro_security as security
import metro_protocol as protocol
import project_dependencies as deps
import project_toolchains as tools

LABEL='com.gptclaw.metro-spike'
MAX_FILES=4096
MAX_FILE=32*1024*1024
MAX_SOURCE=128*1024*1024
ROOT_FILES={'app.json','package.json','pnpm-lock.yaml','pnpm-workspace.yaml','tsconfig.json'}
ROOT_DIRS={'src','assets'}
HOST='forge-dev-01-4.tail8c3304.ts.net'
TARGETS={app.PROJECTS/'mob001-accept-one',app.PROJECTS/'mob001-accept-two'}


def origin(value):
    try:
        parsed=urlsplit(value);port=parsed.port
    except ValueError:raise app.AppError('invalid') from None
    app.need(parsed.scheme=='https' and parsed.hostname==HOST and port in range(8443,8451)
             and not parsed.username and not parsed.password and not parsed.query and not parsed.fragment
             and parsed.path in {'','/'},'invalid')
    return 'https://'+HOST+':'+str(port)


@contextmanager
def directory(path=None,parent=None,name=None):
    fd=os.open(path if parent is None else name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=parent)
    try:
        info=os.fstat(fd);app.need(info.st_uid==os.getuid(),'path')
        yield fd
    finally:os.close(fd)


def read_at(parent,name):
    # Anchor every lookup to an opened directory, rejecting symlinks, hardlinks,
    # FIFOs, ownership changes and mutation while reading. Never read a dotfile.
    app.need(name not in {'','.', '..'} and not name.startswith('.') and '/' not in name,'path')
    fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=parent)
    try:
        before=os.fstat(fd)
        app.need(stat.S_ISREG(before.st_mode) and before.st_uid==os.getuid() and before.st_nlink==1,'path')
        app.need(before.st_size<=MAX_FILE,'invalid')
        data=bytearray()
        while len(data)<=MAX_FILE:
            chunk=os.read(fd,min(65536,MAX_FILE+1-len(data)))
            if not chunk:break
            data.extend(chunk)
        after=os.fstat(fd)
        identity=lambda i:(i.st_dev,i.st_ino,i.st_size,i.st_mtime_ns,i.st_ctime_ns)
        app.need(identity(before)==identity(after) and len(data)==before.st_size,'conflict')
        return bytes(data)
    finally:os.close(fd)


def relative_bytes(parent,relative):
    parts=Path(relative).parts
    app.need(parts and not Path(relative).is_absolute() and all(p not in {'','.', '..'} and not p.startswith('.') for p in parts),'path')
    if len(parts)==1:return read_at(parent,parts[0])
    with directory(parent=parent,name=parts[0]) as child:
        return relative_bytes(child,'/'.join(parts[1:]))


def source_inventory(root):
    """Read bounded reviewed source only; omit Git/env/credential trees entirely."""
    output={};total=0;directories=0
    with directory(path=root) as parent:
        def record(parent,name,relative):
            nonlocal total
            data=read_at(parent,name);total+=len(data)
            app.need(total<=MAX_SOURCE and len(output)<MAX_FILES,'invalid')
            output[relative]=hashlib.sha256(data).hexdigest()
            return data
        def walk(parent,prefix):
            nonlocal directories
            directories+=1
            app.need(directories<=MAX_FILES and len(Path(prefix).parts)<=32,'invalid')
            for name in sorted(os.listdir(parent)):
                app.need(not name.startswith('.'),'path')
                info=os.stat(name,dir_fd=parent,follow_symlinks=False)
                relative=prefix+'/'+name
                if stat.S_ISDIR(info.st_mode):
                    with directory(parent=parent,name=name) as child:walk(child,relative)
                else:record(parent,name,relative)
        for name in sorted(ROOT_FILES):record(parent,name,name)
        for name in sorted(ROOT_DIRS):
            try:os.stat(name,dir_fd=parent,follow_symlinks=False)
            except FileNotFoundError:continue
            with directory(parent=parent,name=name) as child:walk(child,name)
        try:config=json.loads(read_at(parent,'app.json'))['expo']
        except (ValueError,KeyError,TypeError):raise app.AppError('invalid') from None
        document=app.validate_project(root)[1]
        if isinstance(document,dict) and document.get('schema_version') in (11,12):
            app.need(__import__('native_contract').app_config(config,document),'native-policy')
        else:app.need(isinstance(config,dict) and not {'extra','updates','plugins'} & set(config),'invalid')
    return output


def prepare_view(root,path,inventory):
    app.need(not path.exists(),'conflict');path.mkdir(mode=0o700)
    with directory(path=root) as parent:
        for relative,digest in inventory.items():
            data=relative_bytes(parent,relative)
            app.need(hashlib.sha256(data).hexdigest()==digest,'conflict')
            out=path/relative;out.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
            fd=os.open(out,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600)
            with os.fdopen(fd,'wb') as target:target.write(data)
    (path/'node_modules').mkdir();(path/'.expo').mkdir()


def plan(root,advertised,duration):
    root,contract=app.target(root)
    app.need(root in TARGETS and contract['schema_version']==5 and type(duration) is int and 1<=duration<=300,'invalid')
    advertised=origin(advertised)
    return {'project':contract['project']['id'],'root':str(root),'duration_seconds':duration,
            'advertised_origin':advertised,'source':source_inventory(root),
            'runtime_security':'approved' if security.read_policy(app.REPO,approved=False)['approved_at'] else 'approval-pending',
            'scope':'loopback-sdk-spike; no Serve operation','source_retained':True}


def ownership(kind,name,token,label=LABEL):
    exists=app.command(['podman',kind,'exists',name],timeout=10,optional=True)
    if exists.returncode==1:return 'absent'
    app.need(exists.returncode==0,'command')
    template='{{index .Config.Labels "'+label+'"}}' if kind=='container' else '{{index .Labels "'+label+'"}}'
    result=app.command(['podman',kind,'inspect',name,'--format',template],timeout=10,optional=True)
    app.need(result.returncode==0,'command')
    return 'owned' if result.stdout.strip()==token else 'foreign'


def cleanup(name,network,token):
    # Inspect both independently: an absent/crashed --rm container must not leave
    # its network behind; a foreign object is preserved and reported.
    errors=[]
    for kind,resource in [('container',name),('network',network)]:
        try:
            state=ownership(kind,resource,token)
            app.need(state!='foreign','conflict')
            if state=='owned':
                argv=['podman','stop','--time','20',resource] if kind=='container' else ['podman','network','rm',resource]
                app.command(argv,timeout=30)
        except app.AppError as error:errors.append(error)
    if errors:raise errors[0]


def container_options(view,root,seconds,*,watch=False):
    app.need(type(watch) is bool,'invalid')
    app.safe(root/'node_modules')
    app.need((root/'node_modules').is_dir() and (root/'node_modules').stat().st_uid==os.getuid(),'path')
    return ['--rm','--pull=never','--userns=keep-id','--memory=1536m','--memory-swap=1536m','--cpus=1','--pids-limit=256',
            '--cap-drop=all','--security-opt=no-new-privileges','--read-only','--http-proxy=false','--image-volume=ignore',
            '--timeout='+str(seconds),'--stop-timeout=20','--log-driver=none',
            '--tmpfs=/tmp:rw,size=256m,mode=1777','--tmpfs=/workspace/.expo:rw,size=16m,mode=1777',
            '--volume',str(view)+':/workspace:ro','--volume',str(root/'node_modules')+':/workspace/node_modules:ro','--workdir','/workspace',
            '--env','CI=false' if watch else 'CI=1','--env','HOME=/tmp/gptclaw-home','--env','NODE_OPTIONS=--max-old-space-size=1024',
            '--env','EXPO_NO_TELEMETRY=1','--env','EXPO_NO_DOTENV=1']



class EphemeralOutput:
    """Owned Podman CLI output held only in bounded memory, never raw evidence."""
    def __init__(self,argv):
        env={'HOME':'/home/forge','PATH':'/usr/local/bin:/usr/bin:/bin',
             'XDG_RUNTIME_DIR':'/run/user/1002','DBUS_SESSION_BUS_ADDRESS':'unix:path=/run/user/1002/bus'}
        self.process=subprocess.Popen(argv,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env=env)
        self.output=bytearray()
        def drain():
            while True:
                chunk=self.process.stdout.read(4096)
                if not chunk:break
                remaining=65536-len(self.output)
                if remaining>0:self.output.extend(chunk[:remaining])
        self.worker=threading.Thread(target=drain,daemon=True);self.worker.start()
    def category(self):
        for value in ['EROFS','EACCES','ENOENT','EADDRINUSE','ENOSPC','MODULE_NOT_FOUND']:
            if value.encode() in self.output:return value
        return 'sdk-startup-or-protocol-failure'
    def diagnostic(self):
        allowed={'network','internal','port','rootless','permission','denied','readonly','filesystem','memory','pids','exec','command','invalid','option','unrecognized','failed','not','found','workspace','expo','metro','configuration','pnpm','image','container','operation','permitted','mount','lsetxattr','timeout','creating','cgroup','sysctl','unsupported','cannot','error','busy','connect','address','available','limit','log','driver','namespace','bridge','commanderror','offline','host','tunnel','lan','localhost','specify'}
        text=bytes(self.output).decode('utf-8','replace').lower()
        words=[word for word in re.findall('[a-z]+',text) if word in allowed]
        return {'exit_code':self.process.poll(),'captured_bytes':len(self.output),'terms':list(dict.fromkeys(words))[:32]}
    def finish(self):
        try:self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.terminate()
            try:self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:self.process.kill();self.process.wait(timeout=2)
        self.worker.join(timeout=2)
        self.process.stdout.close()

def prepared_dependencies(root,slug):
    # Reuse exact dependency receipts without installing packages or reading a
    # full container inspect/environment. Unknown source jobs require recovery.
    import project_mobile as mobile
    journal=deps.load_journal(slug,root);ctx=deps.context(root)
    app.need(journal is not None and journal['phase']=='complete'
             and journal['policy_hash']==ctx['policy_hash'] and journal['after']==ctx['hashes'],'dependency-policy')
    state=mobile.load_state(root,slug)
    app.need(state is not None and state['phase']!='checking' and state['operation_result'] not in {'running','unknown'},'busy')
    app.need(ownership('container',state['name']+'-job',state['token'],app.LABEL)=='absent','busy')


def remaining_seconds(policy,requested):
    # Podman's own deadline also bounds a disconnected spike by security expiry.
    seconds=min(requested,math.floor(security.timestamp(policy['expires_at'])-time.time()))
    app.need(seconds>=1,'invalid')
    return seconds


def require_operator():
    app.need(os.getuid()==1002 and os.geteuid()!=0,'setup')


def run(root,advertised,duration):
    require_operator()
    value=plan(root,advertised,duration);root=Path(value['root'])
    # Default admission checks happen before locks/store/toolchain writes.
    policy=security.read_policy(app.REPO)
    lock=deps.read_bytes(root/'pnpm-lock.yaml',2*1024*1024)
    app.need(hashlib.sha256(lock).hexdigest()==policy['lock_sha256'],'invalid')
    with app.locked(value['project']):
        deps.require_clean(root,value['project'])
        prepared_dependencies(root,value['project'])
        app.need(value['source']==source_inventory(root),'conflict')
        observed=tools.observed(tools.selection(root))
        app.need(observed['state']=='verified' and observed['image_present'],'toolchain-verification')
        image=observed['receipt']['image']
        token=uuid.uuid4().hex;name='gptclaw-metro-spike-'+token;network=name+'-net';audit_name=name+'-audit'
        stage=app.safe(app.STORE/'metro-spikes'/token);view=stage/'source'
        stage.mkdir(parents=True,mode=0o700);prepare_view(root,view,value['source'])
        receipt={'schema_version':1,'name':name,'token':token,'network':network,'project':value['project'],'phase':'preparing'}
        app.save(stage/'spike.json',receipt)
        runner=None
        try:
            audit=app.command(['podman','run','--name',audit_name,'--label',LABEL+'='+token,
                               *container_options(view,root,120),image,'pnpm','audit','--json','--registry=https://registry.npmjs.org/'],timeout=140,optional=True)
            app.need(audit.returncode in {0,1},'command')
            try:report=json.loads(audit.stdout)
            except ValueError:raise security.AdmissionError('Fresh complete audit required') from None
            result=security.evaluate(report,policy,lock)
            app.need(source_inventory(root)==value['source'],'conflict')
            # Registry is held only through allocation and bind, not through the spike.
            with app.locked('registry',project_guard=False):
                port=next((p for p in range(18600,18632,2) if app.available(p)),None)
                app.need(port is not None,'ports')
                receipt.update(port=port,phase='starting');app.save(stage/'spike.json',receipt)
                app.command(['podman','network','create','--internal','--label',LABEL+'='+token,network],timeout=20)
                argv=['podman','run','--name',name,'--label',LABEL+'='+token,'--network',network,
                      '--publish','127.0.0.1:'+str(port)+':8081',*container_options(view,root,remaining_seconds(policy,duration)),
                      '--env','EXPO_OFFLINE=1','--env','EXPO_PACKAGER_PROXY_URL='+value['advertised_origin'],
                      image,'node','node_modules/expo/bin/cli','start','--offline','--go','--port','8081']
                deadline=time.monotonic()+remaining_seconds(policy,duration)
                receipt['probe_phase']='container-bind';app.save(stage/'spike.json',receipt)
                runner=EphemeralOutput(argv)
                bind_deadline=min(deadline,time.monotonic()+20)
                while ownership('container',name,token)!='owned':
                    app.need(runner.process.poll() is None,'health')
                    app.need(time.monotonic()<bind_deadline,'timeout')
                    time.sleep(.1)
            receipt.update(phase='running',probe_phase='native-protocol',expires_at=time.time()+duration);app.save(stage/'spike.json',receipt)
            evidence={};finished=threading.Event()
            def observe():
                try:evidence['protocol']=protocol.sample(port,value['advertised_origin'],deadline)
                except (app.AppError,OSError,ValueError) as error:
                    evidence['failed']=True;evidence['failure_code']=error.code if isinstance(error,app.AppError) else 'system'
                    if isinstance(error,protocol.ProbeError):evidence['diagnostic']=error.diagnostic
                finally:finished.set()
            observer=threading.Thread(target=observe,daemon=True);observer.start()
            while time.monotonic()<deadline:
                current=security.read_policy(app.REPO)
                app.need(current==policy,'conflict')
                app.need(ownership('container',name,token)=='owned','health')
                if finished.is_set():break
                time.sleep(min(1,max(0,deadline-time.monotonic())))
            if evidence.get('failure_code'):receipt['protocol_failure_code']=evidence['failure_code']
            if evidence.get('diagnostic'):receipt['protocol_diagnostic']=evidence['diagnostic']
            app.need(finished.is_set() and not evidence.get('failed'),'health')
            app.need(value['source']==source_inventory(root),'conflict')
            receipt.update(phase='complete',protocol=evidence['protocol'])
            return {'project':value['project'],'state':'spike-complete','port':port,'audit':result,'source_unchanged':True,'protocol':evidence['protocol']}
        except (app.AppError,security.AdmissionError,OSError,ValueError) as error:
            receipt.update(phase='failed',failure_code=error.code if isinstance(error,app.AppError) else 'admission-or-system')
            if runner:receipt['failure_category']=runner.category()
            raise
        finally:
            failures=[]
            for container in [name,audit_name]:
                try:cleanup(container,network,token)
                except app.AppError as error:failures.append(error)
            if runner:
                runner.finish()
                if receipt['phase']=='failed':
                    receipt['failure_category']=runner.category();receipt['failure_diagnostic']=runner.diagnostic()
            if failures:receipt.update(phase='recovery-required')
            app.save(stage/'spike.json',receipt)
            if failures:raise failures[0]


def main():
    p=argparse.ArgumentParser(description=__doc__,allow_abbrev=False)
    p.add_argument('--project-root',required=True);p.add_argument('--origin',required=True);p.add_argument('--seconds',type=int,default=60);p.add_argument('--apply',action='store_true')
    args=p.parse_args()
    try:
        result=run(args.project_root,args.origin,args.seconds) if args.apply else plan(args.project_root,args.origin,args.seconds)
        if 'source' in result:result['source_files']=len(result.pop('source'))
        print(json.dumps(result,sort_keys=True));return 0
    except (app.AppError,security.AdmissionError,OSError,ValueError):
        print(json.dumps({'state':'blocked','reason':'runtime-admission-or-owned-spike-failed','source_retained':True}));return 1

if __name__=='__main__':raise SystemExit(main())
