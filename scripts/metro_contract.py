"""Explicit source-only Metro opt-in migration; never starts or publishes a session."""
import copy
import ctypes
import hashlib
import json
import os
import re
from pathlib import Path
import stat
import uuid

import private_apps as app
import project_dependencies as deps
import project_worktrees as worktrees
import project_toolchains as tools
import project_mobile as mobile
from project_manifest import load_schema,validate_project


# Migration changes only owned tracked metadata, using a read-only plan digest.
# SDK transport/session admission remains a separate capability and security gate.
def metadata_clean(root):
    changed=worktrees.git(root,'status','--porcelain=v1','-z','--untracked-files=all','--','.gptclaw')[0]
    app.need(not changed,'conflict')
    tracked=worktrees.git(root,'ls-files','--error-unmatch','--','.gptclaw/project.yaml',optional=True)
    app.need(tracked[1]==0,'conflict')


def inputs(root):
    paths=['.gptclaw/project.yaml','.gptclaw/template.json','.gptclaw/template-release.json','.gptclaw/toolchain.json','app.json']
    output={name:hashlib.sha256(deps.read_bytes(root/name,65536)).hexdigest() for name in paths}
    context=deps.context(root)
    output.update({'dependency:'+k:v for k,v in context['hashes'].items()})
    selected=tools.selection(root)
    app.need(selected['declaration']=={'schema_version':1,**mobile.profile()['toolchain']},'toolchain-policy')
    output['toolchain-selection']=selected['selection_hash']
    output['mobile-profile']=hashlib.sha256(json.dumps(mobile.profile(),sort_keys=True,separators=(',',':')).encode()).hexdigest()
    output['dependency-policy']=context['policy_hash']
    return output



def require_reconciled(root,slug):
    directory=app.safe(app.STORE/'metro-metadata'/slug)
    if not directory.exists():return
    app.need(directory.is_dir() and directory.stat().st_uid==os.getuid(),'path')
    for index,operation in enumerate(sorted(directory.iterdir())):
        app.need(index<64 and re.fullmatch('[0-9a-f]{32}',operation.name) is not None,'conflict')
        app.safe(operation);app.need(operation.is_dir() and operation.stat().st_uid==os.getuid(),'path')
        record=app.read_json(operation/'operation.json')
        required={'schema_version','project','root','plan_digest','phase','previous_metadata'}
        app.need(isinstance(record,dict) and required<=set(record)<=required|{'displaced_path'}
                 and type(record['schema_version']) is int and record['schema_version']==1
                 and record['project']==slug and record['root']==str(root)
                 and isinstance(record['plan_digest'],str) and re.fullmatch('[0-9a-f]{64}',record['plan_digest']) is not None
                 and record['previous_metadata']==str(operation/'previous.yaml')
                 and record['phase'] in {'preparing','published','complete','failed','recovery-required'},'conflict')
        app.need(record['phase'] in {'complete','failed'},'metro-metadata-recovery')

def plan(root,ttl_seconds=7200):
    app.need(type(ttl_seconds) is int and 60<=ttl_seconds<=28800,'invalid')
    root,source=app.target(root)
    app.need(source['schema_version'] in (5,6),'mobile-unsupported')
    identity=worktrees.canonical(root)
    require_reconciled(root,source['project']['id'])
    metadata_clean(root)
    current=inputs(root)
    value=copy.deepcopy(source)
    value['schema_version']=6
    value['metro']={'adapter':'metro-v1','mode':'expo-go','ttl_seconds':ttl_seconds}
    app.need(not list(load_schema(6)[1].iter_errors(value)),'invalid')
    if source['schema_version']==6:app.need(source==value,'conflict')
    body={'plan_schema':1,'root':str(root),'identity':identity,'inputs':current,'manifest':value}
    digest=hashlib.sha256(json.dumps(body,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return {**body,'plan_digest':digest,'project':source['project']['id'],
            'state':'already-enabled' if source['schema_version']==6 else 'opt-in-planned',
            'starts_session':False,'private_route_changed':False}


def enable(root,ttl_seconds=7200,apply=False,confirm_plan=None):
    value=plan(root,ttl_seconds)
    if not apply:return value
    app.need(isinstance(confirm_plan,str) and confirm_plan==value['plan_digest'],'conflict')
    if value['state']=='already-enabled':return value
    root=Path(value['root'])
    with app.locked(value['project']):
        deps.require_clean(root,value['project'])
        source_job=mobile.load_state(root,value['project'])
        if source_job:
            app.need(source_job['phase']!='checking' and source_job['operation_result'] not in {'running','unknown'},'busy')
            present=app.command(['podman','container','exists',source_job['name']+'-job'],timeout=10,optional=True)
            app.need(present.returncode==1,'busy' if present.returncode==0 else 'command')
        fresh=plan(root,ttl_seconds)
        app.need(fresh['plan_digest']==value['plan_digest'],'conflict')
        # Atomic exchange retains the displaced inode. Even an editor racing
        # the last comparison cannot have its metadata unlinked by publication.
        directory=root/'.gptclaw';app.safe(directory)
        fd=os.open(directory,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
        temporary='project.yaml.'+uuid.uuid4().hex+'.tmp'
        archive=app.safe(app.STORE/'metro-metadata'/value['project']/uuid.uuid4().hex)
        archive.mkdir(mode=0o700,parents=True)
        record={'schema_version':1,'project':value['project'],'root':str(root),
                'plan_digest':value['plan_digest'],'phase':'preparing','previous_metadata':str(archive/'previous.yaml')}
        app.save(archive/'operation.json',record)
        exchanged=False
        try:
            before=os.stat('project.yaml',dir_fd=fd,follow_symlinks=False)
            app.need(stat.S_ISREG(before.st_mode) and before.st_uid==os.getuid() and before.st_nlink==1,'path')
            app.need(hashlib.sha256(deps.read_bytes(directory/'project.yaml',65536)).hexdigest()==fresh['inputs']['.gptclaw/project.yaml'],'conflict')
            out=os.open(temporary,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600,dir_fd=fd)
            with os.fdopen(out,'w') as stream:
                json.dump(fresh['manifest'],stream,sort_keys=True,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
            now=os.stat('project.yaml',dir_fd=fd,follow_symlinks=False)
            app.need((before.st_dev,before.st_ino,before.st_mtime_ns,before.st_ctime_ns,before.st_size)==
                     (now.st_dev,now.st_ino,now.st_mtime_ns,now.st_ctime_ns,now.st_size),'conflict')
            app.need(directory.stat().st_dev==os.fstat(fd).st_dev and directory.stat().st_ino==os.fstat(fd).st_ino,'conflict')
            exchange(fd,temporary);exchanged=True;record['phase']='published';app.save(archive/'operation.json',record)
            displaced=os.stat(temporary,dir_fd=fd,follow_symlinks=False)
            unchanged=(before.st_dev,before.st_ino,before.st_mtime_ns,before.st_size)==(displaced.st_dev,displaced.st_ino,displaced.st_mtime_ns,displaced.st_size)
            if unchanged:
                unchanged=hashlib.sha256(deps.read_bytes(directory/temporary,65536)).hexdigest()==fresh['inputs']['.gptclaw/project.yaml']
            # NOREPLACE protects a foreign archive; EXDEV/unknown outcome leaves
            # the displaced metadata at its exact temporary name for recovery.
            from project_templates import publish
            record['displaced_path']=str(directory/temporary);app.save(archive/'operation.json',record)
            publish(directory/temporary,archive/'previous.yaml');os.fsync(fd)
            if not unchanged:
                record['phase']='recovery-required';app.save(archive/'operation.json',record)
                return {**value,'state':'metadata-recovery-required','previous_metadata':record['previous_metadata']}
            record['phase']='complete';app.save(archive/'operation.json',record)
        except (app.AppError,OSError,ValueError):
            record['phase']='recovery-required' if exchanged else 'failed'
            app.save(archive/'operation.json',record)
            raise
        finally:
            if not exchanged:
                try:os.unlink(temporary,dir_fd=fd)
                except FileNotFoundError:pass
            os.close(fd)
    if validate_project(root)[2]!=0:
        record['phase']='recovery-required';app.save(archive/'operation.json',record)
        return {**value,'state':'metadata-recovery-required','previous_metadata':record['previous_metadata']}
    return {**value,'state':'opt-in-enabled','metadata_commit_required':True,'previous_metadata':record['previous_metadata']}



def exchange(directory_fd,temporary):
    rename=ctypes.CDLL(None,use_errno=True).renameat2
    rename.argtypes=[ctypes.c_int,ctypes.c_char_p,ctypes.c_int,ctypes.c_char_p,ctypes.c_uint]
    rename.restype=ctypes.c_int
    if rename(directory_fd,temporary.encode(),directory_fd,b'project.yaml',2)!=0:
        raise OSError(ctypes.get_errno(),'Atomic metadata exchange failed')

def public(value):
    return {k:v for k,v in value.items() if k not in {'inputs','identity','manifest'}}
