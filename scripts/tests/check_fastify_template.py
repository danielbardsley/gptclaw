#!/usr/bin/env python3
"""Generated Fastify quality, defect rejection and private container smoke checks."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import private_apps as app
import project_dependencies as deps


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory');parser.add_argument('--engine',choices=['docker','podman'],default='docker')
    parser.add_argument('--image',default='gptclaw-toolchain-ci');args=parser.parse_args()
    base=Path(args.directory).absolute();base.mkdir(mode=0o700)
    app.PROJECTS=base;app.STORE=base/'runtime'
    engine=[args.engine]
    if args.engine=='docker':
        config=base/'docker-config';config.mkdir(mode=0o700);(config/'config.json').write_text('{"auths":{}}\n')
        engine += ['--config',str(config)]
    def run(argv,ok=True,timeout=300):
        result=subprocess.run([*engine,*argv],capture_output=True,text=True,timeout=timeout)
        if (result.returncode==0)!=ok:
            raise AssertionError(app.redact((result.stdout+'\n'+result.stderr)[-6000:]))
        return result.stdout
    def container(root):
        identity=['--userns=keep-id'] if args.engine=='podman' else ['--user',f'{os.getuid()}:{os.getgid()}']
        result=['run','--rm',*identity,'--memory=1536m','--cpus=1','--pids-limit=256','--cap-drop=all','--security-opt=no-new-privileges','--volume',str(root)+':/workspace:rw','--workdir','/workspace','--env','GPTCLAW_PROJECT_ID='+root.name]
        for k,v in deps.GUARD_ENV.items():result += ['--env',k+'='+v]
        return result
    roots=[Path(app.create(name,template='fastify',template_version='1.0.0')['root']) for name in ('typed-one','typed-two')]
    for root in roots:
        before={name:(root/name).read_bytes() for name in deps.FILES}
        run([*container(root),args.image,'pnpm','install','--frozen-lockfile',*deps.INSTALL_FLAGS])
        run([*container(root),args.image,'pnpm','verify'])
        assert before=={name:(root/name).read_bytes() for name in deps.FILES}
    root=roots[0]
    for action,name,change in [
        ('lint','src/service.ts',lambda s:s+'\nconst unused = 1;\n'),
        ('typecheck','src/service.ts',lambda s:s.replace('const result =','const result: number =')),
        ('test','src/service.ts',lambda s:s.replace('return result;','return "broken";')),
        ('build','src/app.ts',lambda s:s.replace('await app.ready();','throw new Error("synthetic construction failure");\n  await app.ready();')),
    ]:
        path=root/name;original=path.read_text()
        try:
            path.write_text(change(original));run([*container(root),args.image,'pnpm',action],ok=False)
        finally:path.write_text(original)
    run([*container(roots[0]),args.image,'pnpm','build'])
    names=[]
    def fetch(url):
        with urllib.request.urlopen(url,timeout=2) as response:return response.status,response.read()
    def wait(url,predicate):
        deadline=time.monotonic()+45
        while time.monotonic()<deadline:
            try:
                result=fetch(url)
                if predicate(result):return result
            except (OSError,urllib.error.URLError):pass
            time.sleep(.25)
        raise AssertionError('Container readiness/update deadline exceeded')
    try:
        urls=[]
        for root in roots:
            name='gptclaw-fastify-check-'+uuid.uuid4().hex[:12]
            run([*container(root),'-d','--name',name,'--publish','127.0.0.1::8000',args.image,'pnpm','dev']);names.append(name)
            binding=run(['port',name,'8000/tcp']).strip();assert binding.startswith('127.0.0.1:')
            url='http://'+binding+'/projects/'+root.name;urls.append(url)
            wait(url+'/ready',lambda r:r[0]==200)
            assert fetch(url+'/docs/')[0]==200
            assert fetch(url+'/docs/static/swagger-ui-bundle.js')[0]==200
            assert json.loads(fetch(url+'/openapi.json')[1])['servers']==[{'url':'/projects/'+root.name}]
        path=roots[0]/'src/service.ts';original=path.read_text()
        try:
            path.write_text(original.replace('First example','Updated example'))
            wait(urls[0]+'/api/v1/examples',lambda r:b'Updated example' in r[1])
            path.write_text('invalid syntax !!!\n')
            deadline=time.monotonic()+10;unavailable=False
            while time.monotonic()<deadline:
                try:fetch(urls[0]+'/ready')
                except (OSError,urllib.error.URLError):unavailable=True;break
                time.sleep(.25)
            assert unavailable,'Syntax error never made service unavailable'
            assert fetch(urls[1]+'/ready')[0]==200
            path.write_text(original)
            wait(urls[0]+'/ready',lambda r:r[0]==200)
        finally:path.write_text(original)
    finally:
        for name in names:run(['stop','--time','10',name])
    assert all((root/'src/app.ts').is_file() for root in roots)
    print('Two exact generated APIs: frozen restore, verify/audit, defect rejection, loopback docs/OpenAPI, source reload/error recovery, independent service and stop/source retention passed.')


if __name__=='__main__':main()
