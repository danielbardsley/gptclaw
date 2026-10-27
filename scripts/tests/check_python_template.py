#!/usr/bin/env python3
"""Real generated Python workflow and fault gates in a bounded container engine."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import private_apps as app
import project_dependencies as deps
import project_python as py
import project_toolchains as tools


def main():
    parser=argparse.ArgumentParser();parser.add_argument('directory');parser.add_argument('--engine',choices=['docker','podman'],default='docker');args=parser.parse_args()
    base=Path(args.directory).absolute();base.mkdir(mode=0o700)
    app.PROJECTS=base;app.STORE=base/'.gptclaw-runtime/v1';app.UNITS=base/'units';app.UNITS.mkdir()
    original=app.command;engine=args.engine
    docker_config=base/'docker-config';docker_config.mkdir(mode=0o700);(docker_config/'config.json').write_text('{"auths":{}}\n')
    def command(argv,timeout=300,optional=False):
        if engine=='podman':
            result=original(argv,timeout=timeout,optional=True)
            if result.returncode and not optional:
                print(app.redact((result.stdout+'\n'+result.stderr)[-4096:]),file=sys.stderr,flush=True)
                raise app.AppError('command')
            return result
        assert argv[0]=='podman'
        if argv[1:3] in (['image','exists'],['container','exists']):
            kind=argv[1];listed=original(['docker','--config',str(docker_config),kind,'ls','--all','--format','{{.Repository}}:{{.Tag}}' if kind=='image' else '{{.Names}}'],timeout=30)
            return subprocess.CompletedProcess(argv,0 if argv[3] in listed.stdout.splitlines() else 1,'','')
        if argv[1]=='build':
            translated=['build','--file',str(Path(argv[-1])/'Containerfile'),'--no-cache','--label',argv[argv.index('--label')+1],'--tag',argv[argv.index('--tag')+1],argv[-1]]
        elif argv[1]=='run':
            translated=[x for x in argv[1:] if x not in {'--userns=keep-id','--network=slirp4netns'}]
            if '--user' not in translated:translated[1:1]=['--user',str(os.getuid())+':'+str(os.getgid())]
        else:translated=argv[1:]
        result=original(['docker','--config',str(docker_config),*translated],timeout=timeout,optional=True)
        if result.returncode and not optional:
            print(app.redact((result.stdout+'\n'+result.stderr)[-4096:]),file=sys.stderr)
            raise app.AppError('command')
        return result
    def inspect(argv):
        value=json.loads(command(argv).stdout)
        if engine=='docker':
            for item in value:item['Labels']=item.get('Config',{}).get('Labels',{})
        return value
    app.command=command;app.json_command=inspect;app.object_owned=lambda *_:False;app.available=lambda _:True
    root=Path(app.create('python-ci',template='fastapi',template_version='1.2.0')['root'])
    before=py.context(root)['hashes']
    assert tools.inspect(root)['state']=='unprepared'
    first=tools.prepare(root);reused=tools.prepare(root)
    assert first['changed'] and not reused['changed'] and first['receipt']['image']==reused['receipt']['image']
    print('Actual verified Python/uv versions:',first['receipt']['versions'],flush=True)
    deps.operate(root,'install');assert py.context(root)['hashes']==before
    state=app.state_for('python-ci');contract=app.target(root)[1]
    app.prepare(state,contract,build=True)
    app.run_in_app(state,contract['commands']['verify'],read_only_dependency_files=True)
    assert py.context(root)['hashes']==before
    faults=[('lint','src/fastapi_app/services/echo.py',lambda text:text+'\nunused= 1\n'),
            ('typecheck','src/fastapi_app/services/echo.py',lambda text:text.replace('return EchoOutput(message=normalized)','return 7')),
            ('test','src/fastapi_app/services/echo.py',lambda text:text.replace('" ".join(message.split())','"broken"')),
            ('lint','src/fastapi_app/services/echo.py',lambda text:text.split('"""',2)[2].lstrip('\n')),
            ('security','src/fastapi_app/services/echo.py',lambda text:text+'\nimport subprocess\nsubprocess.run("echo synthetic", shell=True)\n'),
            ('build','src/fastapi_app/main.py',lambda text:'import nonexistent_synthetic_module\n'+text)]
    for gate,name,mutate in faults:
        path=root/name;saved=path.read_bytes()
        try:
            path.write_text(mutate(saved.decode()))
            try:app.run_in_app(state,contract['commands'][gate],read_only_dependency_files=True)
            except app.AppError as error:assert error.code=='command'
            else:raise AssertionError('Defect passed '+gate)
            print('Seeded defect rejected by',gate,flush=True)
        finally:path.write_bytes(saved)
    # Real low-coverage gate, rather than a copied implementation assertion.
    uncovered=root/'src/fastapi_app/services/uncovered.py'
    try:
        uncovered.write_text('"""Synthetic critical uncovered fixture."""\n'+''.join(f'def branch_{i}(value: int) -> int:\n    if value:\n        return value\n    return 0\n\n' for i in range(100)))
        try:app.run_in_app(state,contract['commands']['test'],read_only_dependency_files=True)
        except app.AppError as error:assert error.code=='command'
        else:raise AssertionError('Insufficient coverage passed')
        print('Real insufficient-coverage defect rejected',flush=True)
    finally:uncovered.unlink()
    deps.operate(root,'add','annotated-doc','0.0.5');assert 'annotated-doc' in py.context(root)['groups']['runtime']
    deps.operate(root,'remove','annotated-doc');assert 'annotated-doc' not in py.context(root)['groups']['runtime']
    deps.operate(root,'add','itsdangerous','2.2.0')
    deps.operate(root,'update','itsdangerous','2.1.2');assert py.context(root)['groups']['runtime']['itsdangerous']=='2.1.2'
    deps.operate(root,'update','itsdangerous','2.2.0')
    deps.operate(root,'remove','itsdangerous')
    baseline=py.context(app.REPO/'templates/apps/releases/fastapi/1.2.0')
    assert py.context(root)['groups']==baseline['groups']
    hashes=py.context(root)['hashes'];deps.operate(root,'install');assert py.context(root)['hashes']==hashes
    app.run_in_app(state,contract['commands']['verify'],read_only_dependency_files=True)
    print('Typed uv add/update/remove, coherent reviewable source, frozen restore, full quality and failure gates passed.',flush=True)


if __name__=='__main__':main()
