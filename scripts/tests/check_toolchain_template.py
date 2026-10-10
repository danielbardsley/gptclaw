#!/usr/bin/env python3
"""CI-only Docker adapter for real profile acquisition and selected-image app jobs."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import private_apps as app
import project_dependencies as deps
import project_toolchains as tools


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('directory'); args = parser.parse_args()
    base = Path(args.directory).absolute(); base.mkdir(mode=0o700)
    app.PROJECTS = base; app.STORE = base/'.gptclaw-runtime/v1'; app.UNITS = base/'units'; app.UNITS.mkdir()
    docker_config = base/'docker-config'; docker_config.mkdir(mode=0o700)
    (docker_config/'config.json').write_text('{\"auths\":{}}\n')
    original_command = app.command
    def docker(args, timeout=300, optional=False):
        assert args[0] == 'podman'
        if args[1:3] in (['image','exists'], ['container','exists']):
            kind = 'image' if args[1] == 'image' else 'container'
            # Read scoped existence without executing an image or inspecting credentials.
            listed = original_command(['docker','--config',str(docker_config),kind,'ls','--all','--format','{{.Repository}}:{{.Tag}}' if kind == 'image' else '{{.Names}}'], timeout=30)
            present = args[3] in listed.stdout.splitlines()
            return subprocess.CompletedProcess(args, 0 if present else 1, '', '')
        if args[1] == 'build':
            tag = args[args.index('--tag')+1]; label = args[args.index('--label')+1]
            command = ['docker','build','--file',str(Path(args[-1])/'Containerfile'),'--no-cache','--label',label,'--tag',tag,args[-1]]
        else: command = ['docker',*args[1:]]
        result = original_command(['docker','--config',str(docker_config),*command[1:]],timeout=timeout,optional=True)
        if result.returncode and args[1] == 'build':
            print(app.redact(result.stderr[-4096:]), file=sys.stderr, flush=True)
        if result.returncode and not optional:raise app.AppError('command')
        return result
    def inspect(args):
        info = json.loads(docker(args).stdout)
        for item in info:item['Labels'] = item['Config'].get('Labels',{})
        return info
    app.command = docker; app.json_command = inspect; app.available = lambda _:True; app.object_owned = lambda *_:False
    root = Path(app.create('toolchain-ci')['root'])
    before = {n:(root/n).read_bytes() for n in deps.FILES}
    assert tools.inspect(root)['state'] == 'unprepared'
    prepared = tools.prepare(root); assert prepared['changed'] and prepared['state'] == 'verified'
    reused = tools.prepare(root); assert not reused['changed'] and reused['receipt']['image'] == prepared['receipt']['image']
    image = prepared['receipt']['image']
    def job(s, argv, timeout=300, read_only_dependency_files=False):
        assert s['image'] == image
        if argv[0] == 'pnpm':argv = [argv[0],'--config.@jsr:registry=https://registry.npmjs.org/',*argv[1:]]
        cmd = ['docker','run','--rm','--user',str(os.getuid())+':'+str(os.getgid()),'--workdir','/workspace',
               '--memory=1536m','--cpus=1','--pids-limit=256','--cap-drop=all','--security-opt=no-new-privileges',
               '--volume',s['root']+':/workspace:rw','--env','GPTCLAW_PROJECT_ID='+s['id']]
        for key, value in deps.GUARD_ENV.items():cmd += ['--env',key+'='+value]
        if read_only_dependency_files:
            for name in deps.FILES:cmd += ['--volume',str(Path(s['root'])/name)+':/workspace/'+name+':ro']
        return original_command([*cmd,s['image'],*argv],timeout=timeout)
    app.run_in_app = job
    deps.operate(root,'install'); assert before == {n:(root/n).read_bytes() for n in deps.FILES}
    state = app.state_for('toolchain-ci'); _, contract = app.target(root)
    app.prepare(state,contract,build=True)
    for argv in [['pnpm','test'],['pnpm','typecheck']]:job(state,argv)
    # Explicit legacy adoption changes only the declaration; source/lockfiles remain identical.
    metadata = root/'.gptclaw/toolchain.json'; saved = metadata.read_bytes(); metadata.unlink()
    assert tools.inspect(root)['legacy']; assert tools.prepare(root)['state'] == 'verified'
    metadata.write_bytes(saved); assert not tools.inspect(root)['legacy']
    assert before == {n:(root/n).read_bytes() for n in deps.FILES}
    print('Uncached/reused integrity-verified profile, actual versions, selected-image install/build/test/typecheck and legacy adoption passed.')


if __name__ == '__main__':main()
