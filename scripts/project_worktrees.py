"""Source-only, single-host Git task allocations. No automatic publication or merge."""
import hashlib
import json
import os
from pathlib import Path
import re
import selectors
import signal
import stat
import subprocess
import time

import private_apps as app
import repository_credentials as broker

SLUG = re.compile(r'[a-z][a-z0-9]*(?:-[a-z0-9]+)*')
HEX = re.compile(r'[0-9a-f]{32}')
SHA = re.compile(r'[0-9a-f]{40}')
MAX_ALLOCATIONS = 256
app.MESSAGES.update({
 'worktree-policy': 'The task, repository, path or configuration does not satisfy the worktree policy.',
 'worktree-drift': 'Task ownership or Git identity changed; retain work and reconcile this allocation.',
 'worktree-source-only': 'Task worktrees are source-only; integrate through review before using the canonical runtime.',
 'worktree-retained': 'This checkout is active, dirty or lacks verified retention; no work was removed.',
 'worktree-command': 'A bounded Git operation failed; retain this allocation and inspect status.',
})


def check(value, code='worktree-policy'):
    app.need(value, code)


def store():
    return app.STORE/'worktrees/v1'


def sources():
    return app.PROJECTS/'.gptclaw-worktrees'


def slug(value):
    check(isinstance(value,str) and len(value)<=48 and SLUG.fullmatch(value))
    return value


def owned(path, directory=True):
    path=app.safe(Path(path))
    try:info=path.lstat()
    except OSError:raise app.AppError('path') from None
    check(info.st_uid==os.getuid() and (stat.S_ISDIR(info.st_mode) if directory else
          stat.S_ISREG(info.st_mode) and info.st_nlink==1))
    return [info.st_dev,info.st_ino]


def small_file(path, limit=65536):
    path=app.safe(path)
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    with os.fdopen(fd,'rb') as stream:
        info=os.fstat(stream.fileno())
        check(stat.S_ISREG(info.st_mode) and info.st_uid==os.getuid() and info.st_nlink==1 and info.st_size<=limit)
        data=stream.read(limit+1);check(len(data)<=limit)
        return data


def managed(root):
    """Lexical exclusion plus admin-ID detection protects moved task/component roots."""
    root=Path(root).absolute()
    if '.gptclaw-worktrees' in root.parts:return True
    for parent in [root,*root.parents]:
        pointer=parent/'.git'
        if pointer.is_file() and not pointer.is_symlink():
            raw=small_file(pointer,4096).decode('utf-8')
            if raw.startswith('gitdir: '):
                admin=Path(raw[8:].strip())
                if HEX.fullmatch(admin.name) and (store()/(admin.name+'.json')).exists():return True
        if parent==app.PROJECTS:break
    return False


def guard(root):
    check(not managed(root),'worktree-source-only')


def git(root,*args,optional=False,timeout=20):
    """No inherited Git overrides, user config, hooks, filters or interactive auth."""
    env={'PATH':'/usr/local/bin:/usr/bin:/bin','HOME':'/home/forge','LANG':'C.UTF-8',
         'GIT_CONFIG_NOSYSTEM':'1','GIT_CONFIG_GLOBAL':'/dev/null','GIT_TERMINAL_PROMPT':'0',
         'GIT_OPTIONAL_LOCKS':'0'}
    command=['git','-c','core.fsmonitor=false','-c','core.hooksPath=/dev/null',
             '-c','protocol.ext.allow=never','-C',str(root),*args]
    process=subprocess.Popen(command,env=env,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,start_new_session=True)
    selector=selectors.DefaultSelector();selector.register(process.stdout,selectors.EVENT_READ)
    output=bytearray();deadline=time.monotonic()+timeout
    try:
        while selector.get_map():
            check(time.monotonic()<deadline,'timeout')
            for key,_ in selector.select(min(.1,max(.001,deadline-time.monotonic()))):
                chunk=os.read(key.fileobj.fileno(),65536)
                if not chunk:selector.unregister(key.fileobj);continue
                output.extend(chunk);check(len(output)<=2*1024*1024,'worktree-command')
        process.wait(timeout=max(.001,deadline-time.monotonic()))
        if not optional:check(process.returncode==0,'worktree-command')
        return bytes(output),process.returncode
    finally:
        selector.close();process.stdout.close()
        # Kill the process group even after leader exit: descendants may still exist.
        try:os.killpg(process.pid,signal.SIGTERM)
        except ProcessLookupError:pass
        if process.poll() is None:
            try:process.wait(timeout=.2)
            except subprocess.TimeoutExpired:
                try:os.killpg(process.pid,signal.SIGKILL)
                except ProcessLookupError:pass
                process.wait()
        try:os.killpg(process.pid,signal.SIGKILL)
        except ProcessLookupError:pass


def text(root,*args):
    return git(root,*args)[0].decode('utf-8').strip()


def hook_text(launcher):
    app.safe(launcher)
    return '#!/usr/bin/env bash\nset -euo pipefail\nexec '+str(launcher)+' verify --project-root "$(git rev-parse --show-toplevel)"\n'


def hooks(root,upgrade=False):
    folder=root/'.git/hooks'
    if not folder.exists():return
    owned(folder)
    entries=list(folder.iterdir());check(len(entries)<=64)
    for path in entries:
        owned(path,False)
        if path.name.endswith('.sample'):continue
        check(path.name=='pre-commit')
        raw=small_file(path).decode('utf-8')
        # Only exact platform-generated hook forms with an owned snapshot launcher.
        match=re.fullmatch(r'#!/usr/bin/env bash\nset -euo pipefail\nexec ([A-Za-z0-9/._-]+) verify --project-root (.+)\n',raw)
        check(match is not None)
        launcher=app.safe(Path(match[1]))
        check(launcher.parent.name=='scripts' and launcher.name=='gptclawctl'
              and launcher.parent.parent.parent==app.STORE/'providers'
              and re.fullmatch(r'[0-9a-f]{64}',launcher.parent.parent.name))
        owned(launcher,False)
        check(match[2] in {str(root),'"$(git rev-parse --show-toplevel)"'})
        if upgrade:
            replacement=hook_text(app.provider_bundle()/'scripts/gptclawctl')
            if raw!=replacement:app.save_text(path,replacement);path.chmod(0o700)


def configuration(root):
    # Validate raw canonical config without evaluating any includes or commands.
    broker.validate_git_helper(root)
    raw=small_file(root/'.git/config',8192).decode('utf-8')
    section=None;seen=set();helpers=[]
    for line in raw.splitlines():
        line=line.strip()
        if not line:continue
        if line.startswith('['):
            check(line in {'[core]','[remote "origin"]','[credential]','[user]'} or
                  re.fullmatch(r'\[branch "[A-Za-z0-9._/-]+"\]',line) and '..' not in line)
            section=line;continue
        check(section is not None and '=' in line)
        key,value=[x.strip() for x in line.split('=',1)]
        if section=='[credential]' and key=='helper':helpers.append(value);continue
        check((section,key) not in seen);seen.add((section,key))
        allowed={'[core]':{'repositoryformatversion':'0','filemode':'true','bare':'false','logallrefupdates':'true'},
                 '[remote "origin"]':{'url':'https://github.com/'+broker.repos.ACCOUNT+'/'+broker.bound(root)['name']+'.git',
                                     'fetch':'+refs/heads/*:refs/remotes/origin/*'},
                 '[credential]':{'useHttpPath':'true','username':'x-access-token'}}
        if section.startswith('[branch '):
            check(key in {'remote','merge'} and (value=='origin' if key=='remote' else
                  re.fullmatch(r'refs/heads/[A-Za-z0-9._/-]+',value) and '..' not in value))
        elif section=='[user]':check(key in {'name','email'} and len(value)<=200 and not any(ord(c)<32 for c in value))
        else:check(allowed[section].get(key)==value)
    check(helpers==['',broker.helper_command(root)])
    # Worktree-local config is unsupported; no implicit shared extension changes.
    check(not (root/'.git/config.worktree').exists())
    hooks(root)


def canonical(root):
    root=app.safe(Path(root).absolute());guard(root)
    check(root.is_relative_to(app.PROJECTS) and root!=app.PROJECTS and root!=app.REPO)
    root_identity=owned(root);common=root/'.git';common_identity=owned(common)
    configuration(root)
    check(text(root,'rev-parse','--show-toplevel')==str(root))
    check(text(root,'rev-parse','--path-format=absolute','--git-common-dir')==str(common))
    check(not (root/'.gitmodules').exists())
    entries=git(root,'ls-files','--stage','-z')[0].split(b'\0')
    check(not any(x.startswith(b'160000 ') for x in entries))
    # Nested Git roots (tracked or untracked) are unsupported; bounded no-follow walk.
    count=0
    for directory,dirs,files in os.walk(root,followlinks=False):
        dirs[:]=[d for d in dirs if d not in {'.git','node_modules','.next','.venv','__pycache__','.gptclaw-cache'}]
        count+=len(dirs)+len(files);check(count<=20000)
        if Path(directory)!=root:check('.git' not in files and not (Path(directory)/'.git').exists())
    binding=broker.bound(root)
    check(not any((common/name).exists() for name in ['MERGE_HEAD','REBASE_HEAD','rebase-merge','rebase-apply','CHERRY_PICK_HEAD','sequencer']))
    from project_manifest import validate_project
    result,contract,code=validate_project(root);check(code==0)
    project=slug(contract['project']['id'])
    key=hashlib.sha256((str(common)+'\0'+str(binding['repository_id'])).encode()).hexdigest()
    return {'root':str(root),'common':str(common),'repository_id':binding['repository_id'],'repository':binding['name'],
            'project':project,'root_identity':root_identity,'common_identity':common_identity,'key':key}


def allocation(identity,task):
    slug(task)
    return hashlib.sha256((identity['key']+'\0'+task).encode()).hexdigest()[:32]


def plan(root,task,owner):
    slug(owner);identity=canonical(root);ident=allocation(identity,task)
    base=text(root,'rev-parse','--verify','refs/remotes/origin/main^{commit}');check(SHA.fullmatch(base))
    if not receipt_path(ident).exists():
        check(not (sources()/identity['project']/ident).exists())
        check(git(root,'show-ref','--verify','refs/heads/codex/'+task+'-'+ident,optional=True)[1]!=0)
    return {'schema_version':1,'identity':identity,'task':task,'owner':owner,'allocation_id':ident,
            'path':str(sources()/identity['project']/ident),'branch':'codex/'+task+'-'+ident,
            'base_ref':'origin/main','base_commit':base,'base_observation':'local-only',
            'base_observed_at':int(time.time()),'state':'planned'}


def receipt_path(ident):
    check(isinstance(ident,str) and HEX.fullmatch(ident))
    return store()/(ident+'.json')


def validate(value,identity,task):
    expected={'schema_version','identity','task','owner','allocation_id','path','branch','base_ref','base_commit',
              'base_observation','base_observed_at','updated_at','state','generation','head','checkout_identity','admin_identity','handoff'}
    check(isinstance(value,dict) and set(value)==expected,'worktree-drift')
    check(value['identity']==identity and value['task']==task and value['allocation_id']==allocation(identity,task),'worktree-drift')
    check(value['schema_version']==1 and type(value['schema_version']) is int)
    check(value['path']==str(sources()/identity['project']/value['allocation_id'])
          and value['branch']=='codex/'+task+'-'+value['allocation_id'] and value['base_ref']=='origin/main')
    check(all(type(value[k]) is int and value[k]>0 for k in ['base_observed_at','updated_at']))
    check(value['base_observation']=='local-only' and SHA.fullmatch(value['base_commit']) and SHA.fullmatch(value['head']))
    slug(value['owner']);check(type(value['generation']) is int and 1<=value['generation']<=1000000)
    check(value['state'] in {'creating','active','handed-off','removing','removed'})
    for key in ['checkout_identity','admin_identity']:
        check(value[key] is None or isinstance(value[key],list) and len(value[key])==2 and all(type(x) is int and x>=0 for x in value[key]))
    report(value['handoff'])
    return value


def report(value):
    check(isinstance(value,dict) and set(value)=={'checks','remaining','dirty','publication','pr'})
    check(isinstance(value['checks'],list) and len(value['checks'])<=32 and isinstance(value['remaining'],list) and len(value['remaining'])<=32)
    for item in value['checks']:
        check(isinstance(item,dict) and set(item)=={'check','result','source'})
        slug(item['check']);check(item['result'] in {'passed','failed','skipped'} and item['source']=='owner-reported')
    for item in value['remaining']:slug(item)
    check(type(value['dirty']) is bool and value['publication'] in {'not-observed','remote-head-verified'})
    check(value['pr'] is None or isinstance(value['pr'],dict) and set(value['pr'])=={'number','head','merge','state'}
          and type(value['pr']['number']) is int and value['pr']['number']>0
          and SHA.fullmatch(value['pr']['head']) and (value['pr']['merge'] is None or SHA.fullmatch(value['pr']['merge']))
          and value['pr']['state'] in {'open','closed','merged'}
          and (value['pr']['state']!='merged' or value['pr']['merge'] is not None))


def read(identity,task):
    value=app.read_json(receipt_path(allocation(identity,task)))
    check(value is not None,'worktree-drift')
    check(stat.S_IMODE(receipt_path(value['allocation_id']).stat().st_mode)==0o600)
    return validate(value,identity,task)


def persist(value):
    broker.private_directory(store());value['updated_at']=int(time.time());app.save(receipt_path(value['allocation_id']),value)


def listings(root):
    raw=git(root,'worktree','list','--porcelain','-z')[0]
    rows=[];row={}
    for item in raw.split(b'\0'):
        if not item:
            if row:rows.append(row);row={}
            continue
        key,_,val=item.decode('utf-8').partition(' ');row[key]=val
    return rows


def observe(value,allow_unrecorded=False):
    root=Path(value['identity']['root']);path=Path(value['path']);app.safe(path)
    rows=[x for x in listings(root) if x.get('worktree')==str(path)]
    check(len(rows)==1 and not any(k in rows[0] for k in ['locked','prunable','detached']), 'worktree-drift')
    check(rows[0].get('branch')=='refs/heads/'+value['branch'],'worktree-drift')
    admin=Path(value['identity']['common'])/'worktrees'/value['allocation_id']
    actual=[owned(path),owned(admin)]
    check(small_file(path/'.git',4096)==('gitdir: '+str(admin)+'\n').encode(),'worktree-drift')
    check(small_file(admin/'gitdir',4096)==(str(path/'.git')+'\n').encode(),'worktree-drift')
    check(small_file(admin/'commondir',4096)==b'../..\n','worktree-drift')
    check(not (admin/'config.worktree').exists(),'worktree-policy')
    if not allow_unrecorded:
        check(actual==[value['checkout_identity'],value['admin_identity']],'worktree-drift')
    head=text(path,'rev-parse','HEAD');check(SHA.fullmatch(head))
    dirty=bool(git(path,'status','--porcelain=v1','-z','--untracked-files=all','--ignored=matching')[0])
    busy=any((admin/name).exists() for name in ['index.lock','MERGE_HEAD','rebase-merge','rebase-apply','CHERRY_PICK_HEAD','sequencer'])
    return {'head':head,'dirty':dirty,'git_busy':busy,'checkout_identity':actual[0],'admin_identity':actual[1]}


def authorize(value,owner,generation):
    slug(owner)
    check(value['owner']==owner and type(generation) is int and value['generation']==generation,'worktree-drift')


def lock_key(root):
    # Immutable enrollment metadata selects the lock before reading mutable Git config.
    root=app.safe(Path(root).absolute());guard(root);owned(root/'.git')
    binding=broker.bound(root)
    return hashlib.sha256((str(root/'.git')+'\0'+str(binding['repository_id'])).encode()).hexdigest()


def create(root,task,owner,base_commit):
    with app.locked('worktree-project-'+lock_key(root)):
        proposed=plan(root,task,owner);identity=proposed['identity']
        check(base_commit==proposed['base_commit'],'worktree-drift')
        existing=app.read_json(receipt_path(proposed['allocation_id']))
        if existing:
            value=validate(existing,identity,task)
            check(value['owner']==owner and value['base_commit']==base_commit and value['state'] in {'creating','active'},'worktree-drift')
            if value['state']=='active':
                observe(value);return value
        else:
            check(not Path(proposed['path']).exists())
            check(not git(root,'show-ref','--verify','refs/heads/'+proposed['branch'],optional=True)[1]==0)
            check(len(list(store().glob('*.json'))) < MAX_ALLOCATIONS)
            value={**proposed,'state':'creating','generation':1,'head':base_commit,'checkout_identity':None,'admin_identity':None,
                   'handoff':{'checks':[],'remaining':[],'dirty':False,'publication':'not-observed','pr':None}}
            persist(value)
        path=Path(value['path']);app.safe(path)
        broker.private_directory(sources());broker.private_directory(path.parent)
        broker.upgrade_registered_helpers(roots={str(Path(root))})
        hooks(Path(root),upgrade=True)
        if not path.exists():
            check(not any(x.get('branch')=='refs/heads/'+value['branch'] for x in listings(root)),'worktree-drift')
            branch_exists=git(root,'show-ref','--verify','refs/heads/'+value['branch'],optional=True)[1]==0
            if branch_exists:
                check(text(root,'rev-parse','refs/heads/'+value['branch'])==base_commit,'worktree-drift')
                git(root,'worktree','add',str(path),value['branch'])
            else:git(root,'worktree','add','-b',value['branch'],str(path),base_commit)
        actual=observe(value,allow_unrecorded=True)
        check(actual['head']==base_commit and not actual['dirty'] and not actual['git_busy'],'worktree-drift')
        value.update({k:actual[k] for k in ['checkout_identity','admin_identity']});value['state']='active';persist(value)
        return value


def status(root,task):
    identity=canonical(root);value=read(identity,task)
    result=dict(value)
    if value['state']!='removed':
        try:
            if value['state'] in {'creating','removing'} and not Path(value['path']).exists():
                check(not any(x.get('branch')=='refs/heads/'+value['branch'] for x in listings(root)),'worktree-drift')
                result['observed']={'state':'intent-recorded'};result['state']='interrupted'
            else:result['observed']=observe(value,allow_unrecorded=value['state']=='creating')
        except app.AppError:result['observed']={'state':'conflicted'};result['state']='conflicted'
        if value['state'] in {'creating','removing'}:result['recovery']='interrupted'
    result['unmanaged_count']=sum(x.get('worktree')!=str(root) and
        not (HEX.fullmatch(Path(x.get('worktree','')).name or '') and receipt_path(Path(x['worktree']).name).exists())
        for x in listings(root))
    return result


def remote_head(value):
    # Exact ref read through the canonical singleton credential, never cached refs.
    root=Path(value['identity']['root']);broker.validate_git_helper(root)
    token=broker.Broker().project_token(root,'git')
    try:
        observed=token.request('GET','/repos/'+broker.repos.ACCOUNT+'/'+value['identity']['repository']+'/git/ref/heads/'+value['branch'],missing=True)
    finally:token.close()
    if observed is None:return False
    check(isinstance(observed,dict) and observed.get('ref')=='refs/heads/'+value['branch']
          and observed.get('object',{}).get('type')=='commit','worktree-drift')
    return observed['object']['sha']==value['head']


def pr_evidence(value,number):
    check(type(number) is int and number>0)
    root=Path(value['identity']['root']);broker.validate_git_helper(root)
    token=broker.Broker().project_token(root,'pr')
    try:
        item=token.request('GET','/repos/'+broker.repos.ACCOUNT+'/'+value['identity']['repository']+'/pulls/'+str(number))
    finally:token.close()
    check(item.get('number')==number and item.get('head',{}).get('repo',{}).get('id')==value['identity']['repository_id']
          and item.get('base',{}).get('repo',{}).get('id')==value['identity']['repository_id']
          and item.get('base',{}).get('ref')=='main' and item.get('head',{}).get('ref')==value['branch']
          and item.get('head',{}).get('sha')==value['head'],'worktree-drift')
    merged=item.get('merged') is True;merge=item.get('merge_commit_sha') if merged else None
    check(item.get('state') in {'open','closed'} and (isinstance(merge,str) and SHA.fullmatch(merge) if merged else merge is None))
    return {'number':number,'head':value['head'],'merge':merge,'state':'merged' if merged else item['state']}


def handoff(root,task,owner,generation,checks=None,remaining=None,published=False,pr=None):
    with app.locked('worktree-project-'+lock_key(root)):
        identity=canonical(root)
        value=read(identity,task);authorize(value,owner,generation)
        check(value['state']=='active','worktree-drift');actual=observe(value);check(not actual['git_busy'],'worktree-drift')
        value['head']=actual['head']
        summary={'checks':checks or [],'remaining':remaining or [],'dirty':actual['dirty'],'publication':'not-observed','pr':None}
        report(summary)
        if published:
            check(remote_head(value),'worktree-drift');summary['publication']='remote-head-verified'
        if pr is not None:summary['pr']=pr_evidence(value,pr)
        value['handoff']=summary;value['state']='handed-off';value['generation']+=1;persist(value)
        return value


def resume(root,task,owner,generation,target_owner):
    slug(target_owner)
    with app.locked('worktree-project-'+lock_key(root)):
        identity=canonical(root)
        value=read(identity,task);authorize(value,owner,generation)
        check(value['state'] in {'active','handed-off'},'worktree-drift')
        actual=observe(value);check(actual['head']==value['head'] and not actual['git_busy'],'worktree-drift')
        # Active-to-active transfer is explicit recovery, not timeout-based takeover.
        value['owner']=target_owner;value['generation']+=1;value['state']='active';persist(value)
        return value


def retention(value):
    root=Path(value['identity']['root'])
    if git(root,'merge-base','--is-ancestor',value['head'],'HEAD',optional=True)[1]==0:return 'canonical-ancestry'
    recorded=value['handoff']['pr']
    if recorded:
        observed=pr_evidence(value,recorded['number'])
        if observed['state']=='merged' and observed['head']==value['head'] and git(root,'merge-base','--is-ancestor',observed['merge'],'HEAD',optional=True)[1]==0:return 'canonical-squash'
    if remote_head(value):return 'remote-head'
    return None


def cleanup(root,task,owner,generation,head,apply=False):
    # Preview reads only. Apply locks and re-observes before removing the exact tree.
    import contextlib
    with (app.locked('worktree-project-'+lock_key(root)) if apply else contextlib.nullcontext()):
        identity=canonical(root)
        value=read(identity,task);authorize(value,owner,generation)
        check(head==value['head'],'worktree-drift')
        path=Path(value['path'])
        if value['state']=='removed':return {'state':'removed','allocation':value,'branch_retained':True}
        if value['state']=='removing' and not path.exists():
            check(not any(x.get('worktree')==str(path) or x.get('branch')=='refs/heads/'+value['branch'] for x in listings(root)),'worktree-drift')
            check(text(root,'rev-parse','refs/heads/'+value['branch'])==head,'worktree-drift')
            if apply:value['state']='removed';persist(value)
            return {'state':'removed' if apply else 'removal-interrupted','allocation':value,'branch_retained':True}
        actual=observe(value)
        check(value['state'] in {'handed-off','removing'} and not actual['dirty'] and not actual['git_busy']
              and actual['head']==head,'worktree-retained')
        kept=retention(value);check(kept is not None,'worktree-retained')
        if apply:
            value['state']='removing';persist(value)
            git(root,'worktree','remove',str(path))
            value['state']='removed';persist(value)
        return {'state':'removed' if apply else 'cleanup-planned','allocation':value,'retention':kept,'branch_retained':True}


def validate_invocation(root,cwd):
    """Used by the credential helper before token issuance for managed task Git."""
    if not managed(cwd):return
    check(not any(key.startswith('GIT_CONFIG') and key not in {'GIT_CONFIG_NOSYSTEM','GIT_CONFIG_GLOBAL'} for key in os.environ),'worktree-policy')
    identity=canonical(root)
    top=Path(text(cwd,'rev-parse','--show-toplevel'))
    ident=top.name;check(HEX.fullmatch(ident),'worktree-drift')
    value=app.read_json(receipt_path(ident));check(value is not None,'worktree-drift')
    value=validate(value,identity,value['task'])
    check(value['state'] in {'active','handed-off'} and top==Path(value['path']),'worktree-drift')
    observe(value)
