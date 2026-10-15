#!/usr/bin/env python3
"""Native container verification in an owned disposable project tree.

Only the systemd/Serve interface is replaced: generated Quadlet fields are
translated to finite Podman argv for task-owned units. No host unit, installed
provider, Serve handler or existing project is changed. This is local native
adapter evidence, not private/systemd or project-owner acceptance.
"""
import argparse
import contextlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
import uuid
from unittest.mock import patch

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import private_apps as app
import project_controls as controls
import project_database as db
import project_groups as groups
import project_toolchains as tools


class NativeUnits:
    def __init__(self, original, units):
        self.original,self.units=original,units
        self.names=set()
    def run(self,argv,timeout=300,optional=False):
        if argv[:2]!=['systemctl','--user']:
            return self.original(argv,timeout=timeout,optional=optional)
        action=argv[2]
        if action=='daemon-reload':return subprocess.CompletedProcess(argv,0,'','')
        app.need(action in {'show','is-active','start','stop','reset-failed'},'invalid')
        name=argv[3].removesuffix('.service')
        unit=app.safe(self.units/(name+'.container'))
        # All selected units must have been generated in this task's private
        # directory. An absent post-stop unit can only be queried, never started.
        app.need(unit.exists() or name in self.names,'conflict')
        if action=='show':
            return subprocess.CompletedProcess(argv,0,'SourcePath='+str(unit)+'\nDropInPaths=\n','')
        if action=='reset-failed':return subprocess.CompletedProcess(argv,0,'','')
        exists=self.original(['podman','container','exists',name],optional=True).returncode==0
        if action=='is-active':
            running=exists and json.loads(self.original(['podman','container','inspect',name]).stdout)[0]['State']['Running']
            return subprocess.CompletedProcess(argv,0 if running else 3,'active\n' if running else 'inactive\n','')
        fields={};section=None
        for line in unit.read_text().splitlines():
            if line.startswith('['):section=line
            elif section=='[Container]' and '=' in line:
                key,value=line.split('=',1);fields.setdefault(key,[]).append(value)
        app.need(fields.get('ContainerName')==[name] and fields.get('Pull')==['never'],'conflict')
        tokens=[value.split('=',1)[1] for value in fields.get('Label',[]) if value.startswith(app.LABEL+'=')]
        app.need(len(tokens)==1,'conflict');token=tokens[0]
        if exists:app.need(app.object_owned('container',name,token),'conflict')
        if action=='stop':
            if exists:
                self.original(['podman','stop','--time=30',name],timeout=90)
                self.original(['podman','rm',name],timeout=30)
            self.names.add(name)
            return subprocess.CompletedProcess(argv,0,'','')
        app.need(not exists,'busy')
        command=['podman','run','--detach','--name',name,'--userns=keep-id','--memory=1536m','--cpus=1',
                 '--pids-limit=256','--cap-drop=all','--security-opt=no-new-privileges']
        for key,flag in [('Label','--label'),('PublishPort','--publish'),('Volume','--volume'),
                         ('WorkingDir','--workdir'),('Environment','--env'),('User','--user')]:
            for value in fields.get(key,[]):command += [flag,value]
        for network in fields.get('Network',[]):command+=['--network',network]
        for value in fields.get('PodmanArgs',[]):
            # Provider-owned typed metadata only; never evaluates shell syntax.
            command+=shlex.split(value)
        if fields.get('ReadOnly')==['true']:command+=['--read-only']
        command += fields['Image']
        command += [arg.replace('$$','$').replace('%%','%') for arg in shlex.split(fields['Exec'][0])]
        self.names.add(name)
        self.original(command,timeout=timeout)
        return subprocess.CompletedProcess(argv,0,'','')


def instances(root):
    _,value=app.target(root)
    _,rows=controls.runtime_rows(root,value)
    result={}
    for name,row in rows.items():
        s=row['receipt']
        if not s:continue
        container=db.name(s) if name=='db' else s['name']
        if app.object_owned('container',container,s['token']):
            result[name]=app.json_command(['podman','container','inspect',container])[0]['Id']
    return result


def request(root,method='GET',suffix='/api/v1/notes',body=None):
    _,value=app.target(root);parent=app.state_for(value['project']['id'])
    s=app.state_for(parent['components']['api']) if value['project']['kind']=='group' else parent
    payload=None if body is None else json.dumps(body).encode()
    url=f"http://127.0.0.1:{s['port']}/projects/{value['project']['id']}"+suffix
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(urllib.request.Request(url,data=payload,method=method,headers={'Content-Type':'application/json'}),timeout=5) as response:
        return json.load(response)


def seed_verified_tools(root, canonical_store, aliases):
    """Reuse only matching validated public toolchain metadata and exact images."""
    root,value=app.target(root)
    with (groups.scope(root,value) if value['schema_version'] in (3,4,8) else contextlib.nullcontext({'single':(root,value)})) as children:
        for path,_ in children.values():
            selected=tools.selection(path)
            if tools.record(selected) is not None:continue
            with patch.object(app,'STORE',canonical_store):
                receipt=tools.record(selected);image=tools.image_info(selected)
            app.need(receipt is not None and receipt['phase']=='verified' and image==receipt['image'],'toolchain-verification')
            tag=tools.tag_for(selected)
            app.command(['podman','tag',image,tag])
            aliases[tag]=image
            directory=tools.location(selected);directory.mkdir(mode=0o700,parents=True)
            app.save(directory/'receipt.json',receipt)
            tools.verify(selected,image,uuid.uuid4().hex)


def exercise(root,profile,peer=None):
    stage=lambda phase,component: print('STAGE',profile,phase,component or 'project',flush=True)
    if profile=='database':
        _,value=app.target(root)
        with groups.scope(root,value) as children:
            groups.reserve(root,value)
            for path,contract in children.values():
                s=app.reserve(path,contract);selected=tools.selection(path)
                s.update(image=app.toolchain(path,selected),toolchain_hash=selected['selection_hash'])
                app.save(app.STORE/(s['id']+'.json'),s);app.prepare(s,contract,False)
        db.dispatch(root,'init')
    controls.execute(root,'start',stage=stage)
    before=instances(root)
    controls.execute(root,'start',stage=stage)
    assert instances(root)==before,'start changed an already ready instance'
    if profile=='single':
        controls.execute(root,'pause',stage=stage);paused=instances(root)
        assert paused==before
        controls.execute(root,'resume',stage=stage);assert instances(root)==before
    if profile=='group':
        note=request(root,'POST',body={'title':'Synthetic ephemeral note','body':'Task-owned generated data'})
        assert 'in-memory data can be lost' in controls.impact(app.target(root)[1],'restart','api')
        controls.execute(root,'pause',stage=stage);assert instances(root)==before
        controls.execute(root,'resume',stage=stage);assert instances(root)==before
        controls.execute(root,'restart','web',stage=stage)
        after=instances(root);assert after['api']==before['api'] and after['web']!=before['web']
        assert request(root,suffix='/api/v1/notes/'+note['id'])==note
        if peer:assert app.status(peer)['state']=='ready'
        before=after
    note=None
    if profile=='database':
        note=request(root,'POST',body={'title':'Synthetic control acceptance','body':'Task-owned generated data'})
        owned=db.state(app.target(root)[1]['project']['id'],root);volume=owned['active'];epoch=owned['epoch']
        controls.execute(root,'restart','db',stage=stage)
        after=instances(root);assert after['api']==before['api'] and after['db']!=before['db']
        assert db.state(owned['project'],root)['active']==volume and db.state(owned['project'],root)['epoch']==epoch
        assert request(root,suffix='/api/v1/notes/'+note['id'])==note
        before=after
    target='api' if 'api' in before else 'web'
    controls.execute(root,'restart',target,stage=stage)
    after=instances(root);assert after[target]!=before[target]
    for name in before:
        if name!=target:assert after[name]==before[name]
    if profile=='group':
        assert request(root)['total']==0;note=None
    if note:assert request(root,suffix='/api/v1/notes/'+note['id'])==note
    before_rebuild=instances(root)
    controls.execute(root,'rebuild',stage=stage)
    if profile=='database':assert instances(root)['db']==before_rebuild['db']
    if note:assert request(root,suffix='/api/v1/notes/'+note['id'])==note
    before_restart=instances(root)
    controls.execute(root,'restart',stage=stage)
    after_restart=instances(root)
    assert all(after_restart[name]!=before_restart[name] for name in before_restart)
    if note:assert request(root,suffix='/api/v1/notes/'+note['id'])==note
    if peer:assert app.status(peer)['state']=='ready'
    controls.execute(root,'stop',stage=stage)
    controls.execute(root,'rebuild',stage=stage)
    _,value=app.target(root);_,rows=controls.runtime_rows(root,value)
    assert not any(row['active'] for row in rows.values())
    assert (root/'.gptclaw/project.yaml').is_file()
    print('PASS',profile,'native start/no-op/restart/rebuild/stop and applicable retention/pause/isolation',flush=True)


def cleanup(original,roots):
    states=app.states();network_owners={};container_owners={}
    for s in states:
        container_owners[s['name']]=s['token'];container_owners[s['name']+'-job']=s['token']
        if s.get('group'):
            parent=app.state_for(s['group']);network_owners[parent['network']]=parent['token']
    for root in roots:
        _,value=app.target(root)
        if value['schema_version'] in (4,8):
            s=db.state(value['project']['id'],root)
            if s:container_owners[db.name(s)]=s['token'];network_owners[db.backend(s)]=s['token']
        marker=app.read_json(controls.guard_path(value['project']['id']))
        if marker:
            ident=marker['operation_id']
            for component in ['api','web']:
                container_owners['gptclaw-build-'+ident+'-'+component+'-job']=ident
    for name,token in container_owners.items():
        if app.object_owned('container',name,token):original(['podman','rm','--force',name],timeout=90)
    for name,token in network_owners.items():
        if app.object_owned('network',name,token):original(['podman','network','rm',name],timeout=30)
    assert all(not app.object_owned('container',name,token) for name,token in container_owners.items())
    assert all(not app.object_owned('network',name,token) for name,token in network_owners.items())


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--profile',choices=['single','group','database','all'],default='all')
    args=parser.parse_args()
    base=Path(tempfile.mkdtemp(prefix='.dashboard-check-controls-',dir=ROOT));identity=base.stat()
    projects=base/'projects';projects.mkdir(mode=0o700)
    units=base/'units';units.mkdir(mode=0o700)
    original=app.command;canonical_store=app.STORE;adapter=NativeUnits(original,units);roots=[];aliases={};passed=False
    with contextlib.ExitStack() as stack:
        for obj,key,value in [(app,'PROJECTS',projects),(app,'STORE',base/'runtime'),(app,'UNITS',units),
            (db,'BASE',base/'data'),(db,'mount',lambda:None),(app,'command',adapter.run),
            (app,'node_identity',lambda:'synthetic.example.ts.net'),(app,'ensure_ingress',lambda:None),
            (app,'route_info',lambda slug:{'state':'configured','url':'https://synthetic.example.ts.net/projects/'+slug+'/'})]:
            stack.enter_context(patch.object(obj,key,value))
        try:
            profiles=['single','group','database'] if args.profile=='all' else [args.profile]
            for profile in profiles:
                template={'single':'fastify','group':'notes','database':'fastapi-postgres'}[profile]
                slug='dsh009-'+uuid.uuid4().hex[:8]+'-'+profile
                root=Path(app.create(slug,template=template,template_version='1.0.0')['root']);roots.append(root)
                seed_verified_tools(root,canonical_store,aliases)
                peer=None;peer_instances=None
                if profile in {'group','database'}:
                    peer=Path(app.create('dsh009-'+uuid.uuid4().hex[:8]+'-peer',template='fastify',template_version='1.0.0')['root']);roots.append(peer)
                    seed_verified_tools(peer,canonical_store,aliases);controls.execute(peer,'start');peer_instances=instances(peer)
                exercise(root,profile,peer)
                if peer:
                    assert instances(peer)==peer_instances and app.status(peer)['state']=='ready'
                    controls.execute(peer,'stop')
            passed=True
        except BaseException:
            print('RETAINED task-owned source/receipts after failure:',base,flush=True)
            raise
        finally:
            try:
                cleanup(original,roots)
                for tag,image in aliases.items():
                    current=app.json_command(['podman','image','inspect',tag])[0]['Id']
                    app.need(('sha256:'+current.removeprefix('sha256:'))==image,'conflict')
                    original(['podman','image','rm',tag],timeout=30)
            except Exception:
                print('RETAINED task-owned native fixtures for inspection:',base,flush=True)
                raise
    if passed:
        assert not base.is_symlink() and (base.stat().st_dev,base.stat().st_ino)==(identity.st_dev,identity.st_ino)
        shutil.rmtree(base)
        print('PASS: task-owned containers/networks removed; host systemd, Serve and existing projects untouched',flush=True)
    else:print('RETAINED task-owned source/receipts after failure:',base,flush=True)


if __name__=='__main__':
    try:main()
    except app.AppError as error:
        print('FAIL: native control verification:',error.code,flush=True);sys.exit(1)
