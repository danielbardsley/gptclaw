#!/usr/bin/env python3
"""CI generated-app dependency workflow using scoped Docker jobs, never project host code."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import private_apps as app
import project_dependencies as deps


def main():
    parser=argparse.ArgumentParser();parser.add_argument('directory');parser.add_argument('--image',required=True)
    args=parser.parse_args();base=Path(args.directory).absolute();base.mkdir(mode=0o700)
    app.PROJECTS=base;app.STORE=base/'.gptclaw-runtime/v1';app.UNITS=base/'units';app.UNITS.mkdir()
    image=subprocess.check_output(['docker','image','inspect',args.image,'--format','{{.Id}}'],text=True).strip()
    app.toolchain=lambda:image
    app.object_owned=lambda *_:False
    app.available=lambda _:True
    def container(s,argv,timeout=300,read_only_dependency_files=False):
        cmd=['docker','run','--rm','--user',str(os.getuid())+':'+str(os.getgid()),'--workdir','/workspace',
             '--memory=1536m','--cpus=1','--pids-limit=256','--cap-drop=all','--security-opt=no-new-privileges',
             '--volume',s['root']+':/workspace:rw','--env','GPTCLAW_PROJECT_ID='+s['id']]
        for key,val in deps.GUARD_ENV.items():cmd+=['--env',key+'='+val]
        if read_only_dependency_files:
            for name in deps.FILES:cmd+=['--volume',str(Path(s['root'])/name)+':/workspace/'+name+':ro']
        return subprocess.run([*cmd,image,*argv],check=True,timeout=timeout)
    app.run_in_app=container
    root=Path(app.create('dependency-ci')['root'])
    p=root/'package.json';manifest=json.loads(p.read_text())
    manifest['scripts']['postinstall']='node -e "require(\'fs\').writeFileSync(\'hook-sentinel\',\'forbidden\')"'
    p.write_text(json.dumps(manifest,indent=2)+'\n')
    deps.operate(root,'install')
    before=deps.context(root)['hashes'];deps.operate(root,'install');assert before==deps.context(root)['hashes']
    first=deps.operate(root,'add','is-number','6.0.0','development')
    assert first['request']['version']=='6.0.0'
    deps.operate(root,'update','is-number','7.0.0')
    state=app.state_for('dependency-ci')
    container(state,['node','-e',"if(require('is-number')('4')!==true)process.exit(1)"])
    for command in ('test','typecheck','build'):container(state,['pnpm',command])
    assert not (root/'hook-sentinel').exists()
    deps.operate(root,'remove','is-number')
    assert 'is-number' not in json.loads((root/'package.json').read_text())['devDependencies']
    assert not (root/'hook-sentinel').exists()
    assert not list((deps.location('dependency-ci')/'jobs').iterdir())
    assert deps.status(root,first['operation_id'])['operation']['phase']=='complete'
    print('Generated-app dependency add/update/remove/frozen reuse, hook suppression, build/test/typecheck and receipt history passed.')


if __name__=='__main__':main()
