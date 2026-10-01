#!/usr/bin/env python3
"""Explicit, unprivileged SYS-001 fixture; never invoked by bootstrap or offline CI."""
import argparse
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import time
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / 'examples/rootless-toolchain'
BASE = Path('/srv/forge/projects')
UNITS = Path.home() / '.config/containers/systemd'
LABEL = 'com.gptclaw.sys001'


class FixtureError(ValueError):
    pass


def need(ok, message):
    if not ok:
        raise FixtureError(message)


def run(args, optional=False):
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=300, check=False)
    except (OSError, subprocess.TimeoutExpired):
        raise FixtureError('fixture command unavailable or timed out') from None
    if optional and result.returncode:
        if args[:3] in (['podman','container','exists'], ['podman','image','exists']):
            need(result.returncode == 1, 'cannot determine fixture object ownership')
        return None
    need(result.returncode == 0, 'fixture command failed: ' + args[0])
    return result.stdout.strip()


def safe(path):
    need(not any(p.is_symlink() for p in [path, *path.parents]), 'symlink in fixture path')


def unit_text(state):
    template = (FIXTURES / 'fixture.container.in').read_text()
    values = {'TOKEN':state['token'], 'IMAGE':state['image'], 'NAME':state['name'],
              'PORT':str(state['port']), 'DATA':str(BASE / state['name'] / 'data')}
    for key, value in values.items():
        template = template.replace('@'+key+'@', value)
    return template


def save(path, state):
    path.write_text(json.dumps(state, indent=2)+'\n')


def load(directory):
    directory = Path(directory).absolute()
    safe(directory)
    need(directory.parent == BASE and re.fullmatch(r'gptclaw-sys001-[0-9a-f]{12}',directory.name), 'not a fixture directory')
    statefile = directory/'state.json'; safe(statefile)
    state = json.loads(statefile.read_text())
    need(state['name'] == directory.name and state['token'] == directory.name.removeprefix('gptclaw-sys001-'), 'fixture identity mismatch')
    need(type(state['port']) is int and 1024 <= state['port'] <= 65535, 'invalid fixture port')
    need(state['image'] == '' or re.fullmatch(r'sha256:[0-9a-f]{64}', state['image']), 'invalid fixture image')
    return directory, state


def owned_object(kind, name, token):
    if run(['podman', kind, 'exists', name], optional=True) is None:
        return False
    record = json.loads(run(['podman', kind, 'inspect', name]))[0]
    labels = record.get('Config', {}).get('Labels', {}) if kind == 'container' else record.get('Labels', {})
    need(labels and labels.get(LABEL) == token, 'refusing unrelated Podman object')
    return True


def start(port):
    need(1024 <= port <= 65535, 'choose an unprivileged port')
    # No listener is displaced if the port is taken; the final bind may still race and fail safely.
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', port))
    token=uuid.uuid4().hex[:12]; name='gptclaw-sys001-'+token
    directory=BASE/name; safe(directory); directory.mkdir(mode=0o700)
    state={'token':token,'name':name,'port':port,'image':'','unit_sha256':'','phase':'building'}
    save(directory/'state.json',state)
    print('Fixture directory: '+str(directory),flush=True)
    data=directory/'data'; data.mkdir()
    (data/'index.html').write_text('SYS-001 '+token+'\n')
    context=directory/'build'; context.mkdir()
    shutil.copyfile(FIXTURES/'Containerfile',context/'Containerfile')
    # A unique tag and label make interrupted builds identifiable without broad pruning.
    tag='localhost/'+name+':test'
    run(['podman','build','--pull=missing','--label',LABEL+'='+token,'--tag',tag,str(context)])
    image=json.loads(run(['podman','image','inspect',tag]))[0]
    state['image']=image['Id'] if image['Id'].startswith('sha256:') else 'sha256:'+image['Id']
    state['phase']='built'; save(directory/'state.json',state)
    # Prove keep-id bind writes, DNS and outbound HTTPS independently of the HTTP listener.
    run(['podman','run','--rm','--name',name+'-probe','--label',LABEL+'='+token,
         '--userns=keep-id','--network=slirp4netns','--memory=128m','--cpus=0.5',
         '--pids-limit=64','--cap-drop=all','--security-opt=no-new-privileges',
         '--volume',str(data)+':/srv/fixture:rw',state['image'],'sh','-ec',
         'printf "owned-by-forge\\n" > /srv/fixture/bind-write; nslookup example.com >/dev/null; wget -q -T 15 -O /dev/null https://example.com'])
    need((data/'bind-write').stat().st_uid == os.getuid(), 'bind write ownership differs')
    with (data/'bind-write').open('a') as out:
        out.write('host-write\n')
    safe(UNITS); UNITS.mkdir(parents=True,exist_ok=True)
    unit=UNITS/(name+'.container'); safe(unit)
    text=unit_text(state); state['unit_sha256']=hashlib.sha256(text.encode()).hexdigest()
    state['phase']='installing-unit'; save(directory/'state.json',state)
    with unit.open('x') as out: out.write(text)
    run(['systemctl','--user','daemon-reload'])
    run(['systemctl','--user','start',name+'.service'])
    state['phase']='running'; save(directory/'state.json',state)
    check(directory, state)


def check(directory,state,non_loopback=None):
    unit=UNITS/(state['name']+'.container'); safe(unit)
    need(hashlib.sha256(unit.read_bytes()).hexdigest()==state['unit_sha256'],'fixture unit changed')
    run(['systemctl','--user','is-active',state['name']+'.service'])
    need(owned_object('container',state['name'],state['token']),'fixture container missing')
    response=None
    for _ in range(30):
        try:
            with urllib.request.urlopen('http://127.0.0.1:'+str(state['port']),timeout=2) as reply:
                response=reply.read(256).decode()
            break
        except OSError:
            time.sleep(1)
    need(response=='SYS-001 '+state['token']+'\n','HTTP fixture response mismatch')
    sockets=run(['ss','-H','-ltn'])
    listeners=[line.split()[3] for line in sockets.splitlines() if len(line.split())>=4 and
               line.split()[3].endswith(':'+str(state['port']))]
    need(listeners == ['127.0.0.1:'+str(state['port'])], 'listener is absent or not exclusively IPv4 loopback')
    if non_loopback:
        address=ipaddress.ip_address(non_loopback)
        need(not address.is_loopback and not address.is_unspecified and address.version==4,'provide an actual non-loopback host IPv4 address')
        local=json.loads(run(['ip','-j','-4','address','show']))
        need(any(a.get('local')==str(address) for link in local for a in link.get('addr_info',[])), 'probe address is not assigned to this host')
        try:
            connection=socket.create_connection((str(address),state['port']),timeout=3)
        except OSError:
            pass
        else:
            connection.close(); raise FixtureError('fixture reachable through non-loopback address')
    print(json.dumps({'fixture':state['name'],'status':'passed','loopback_http':True,
                      'non_loopback_probe':'passed' if non_loopback else 'pending',
                      'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip()}))


def crash(directory,state):
    need(owned_object('container',state['name'],state['token']), 'fixture absent')
    before=int(run(['systemctl','--user','show',state['name']+'.service','-p','NRestarts','--value']))
    run(['podman','kill','--signal=KILL',state['name']])
    for _ in range(30):
        time.sleep(1)
        after=int(run(['systemctl','--user','show',state['name']+'.service','-p','NRestarts','--value']))
        if after>before and run(['systemctl','--user','is-active',state['name']+'.service'],optional=True)=='active':
            check(directory,state)
            print('Verified systemd restart after deliberate fixture crash.')
            return
    raise FixtureError('fixture did not restart within 30 seconds')


def cleanup(directory,state):
    unit=UNITS/(state['name']+'.container'); safe(unit)
    if unit.exists():
        need(hashlib.sha256(unit.read_bytes()).hexdigest()==state['unit_sha256'],'refusing changed unit')
    # Check ownership of all objects before stopping anything.
    containers=[]
    for name in (state['name'],state['name']+'-probe'):
        if owned_object('container',name,state['token']): containers.append(name)
    tag='localhost/'+state['name']+':test'
    image_exists=owned_object('image',tag,state['token'])
    if unit.exists():
        run(['systemctl','--user','stop',state['name']+'.service'])
        unit.unlink()
        run(['systemctl','--user','daemon-reload'])
        run(['systemctl','--user','reset-failed',state['name']+'.service'],optional=True)
    for name in containers:
        if owned_object('container',name,state['token']): run(['podman','rm','--force',name])
    if image_exists: run(['podman','image','rm',tag])
    # Refuse unexpected paths; preserve state/data for review if interrupted or extended.
    for path in directory.rglob('*'):
        safe(path)
        need(path.relative_to(directory).as_posix() in
             ('state.json','data','data/index.html','data/bind-write','build','build/Containerfile'),
             'unexpected fixture data; preserve and inspect')
    shutil.rmtree(directory)
    need(not unit.exists(), 'fixture boot activation still exists')
    sockets=run(['ss','-H','-ltn'])
    need(not any(len(line.split())>=4 and line.split()[3].endswith(':'+str(state['port']))
                 for line in sockets.splitlines()), 'port still listening after fixture cleanup; inspect without stopping unrelated processes')
    print('Removed only the owned fixture; shared base image/cache retained.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('start','check','crash','cleanup'))
    parser.add_argument('--directory')
    parser.add_argument('--port',type=int,default=18081)
    parser.add_argument('--non-loopback')
    args=parser.parse_args()
    try:
        need(os.getuid()==1002 and os.geteuid()!=0 and Path.home()==Path('/home/forge'), 'run only as the configured forge user')
        if args.action=='start': start(args.port)
        else:
            need(args.directory is not None,'provide the printed fixture directory')
            directory,state=load(args.directory)
            if args.action=='check': check(directory,state,args.non_loopback)
            elif args.action=='crash': crash(directory,state)
            else: cleanup(directory,state)
        return 0
    except (FixtureError,OSError,ValueError,KeyError) as exc:
        print('Fixture failed: '+(str(exc) if isinstance(exc,FixtureError) else 'invalid state or filesystem/network error')+
              '; preserve the printed directory for scoped cleanup.')
        return 1


if __name__=='__main__':
    raise SystemExit(main())
