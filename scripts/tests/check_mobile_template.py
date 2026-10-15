#!/usr/bin/env python3
"""Generate and check two native-source apps in owned fixtures; no runtime services."""
import argparse
import hashlib
import json
import os
import shlex
from pathlib import Path
import subprocess
import sys
import uuid
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import private_apps as app
import project_repositories as repos
import yaml


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory');parser.add_argument('--engine',choices=['podman','docker'],default='podman')
    parser.add_argument('--image',default=app.TOOLCHAIN);parser.add_argument('--skip-failure-checks',action='store_true')
    args=parser.parse_args();base=Path(args.directory).absolute()
    app.need(not base.exists() and base.parent.is_dir(),'conflict');base.mkdir(mode=0o700)
    app.PROJECTS=base;app.STORE=base/'.gptclaw-runtime/v1'
    roots=[Path(app.create(name,template='expo-react-native',template_version='1.0.1')['root']) for name in ['mobile-one','mobile-two']]
    for root in roots:repos.adapt_guidance(root,root.name,waived=True)
    name='gptclaw-mobile-check-'+uuid.uuid4().hex;records=[]
    def run(root,argv,passed=True):
        command=[args.engine,'run','--rm','--name',name,'--memory=1536m','--cpus=1','--pids-limit=256','--cap-drop=all','--security-opt=no-new-privileges','--label','com.gptclaw.check-owner='+name]
        command += ['--userns=keep-id'] if args.engine=='podman' else ['--user',str(os.getuid())+':'+str(os.getgid())]
        command += ['--volume',str(root)+':/workspace:rw','--workdir','/workspace','--env','CI=1','--env','EXPO_NO_TELEMETRY=1','--env','EXPO_NO_DOTENV=1',args.image,*argv]
        result=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=300)
        log=base/(root.name+'-'+str(len(records))+'.log');log.write_bytes(result.stdout[-1024*1024:])
        if (result.returncode==0)!=passed:raise RuntimeError('Mobile check outcome differs; inspect '+str(log))
        records.append({'project':root.name,'action':argv[-1],'returncode':result.returncode,'log':log.name})
    for root in roots:
        before={f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in ['package.json','pnpm-lock.yaml','pnpm-workspace.yaml']}
        if args.engine=='docker' and root==roots[0]:
            # Execute the published starter's actual workflow command. A different
            # checkout UID must work; the helper's own Docker flags cannot mask it.
            workflow=yaml.safe_load((root/'.github/workflows/quality.yml').read_text())
            script=workflow['jobs']['quality']['steps'][-1]['run'].replace('gptclaw-mobile-check',shlex.quote(args.image))
            result=subprocess.run(['bash','-eu','-o','pipefail','-c',script],cwd=root,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=900)
            log=base/(root.name+'-generated-ci.log');log.write_bytes(result.stdout[-1024*1024:])
            if result.returncode:raise RuntimeError('Generated workflow failed; inspect '+str(log))
            records.append({'project':root.name,'action':'generated-ci','returncode':0,'log':log.name})
        else:
            run(root,['pnpm','install','--frozen-lockfile','--ignore-scripts','--no-runtime','--pm-on-fail=error','--ignore-pnpmfile','--registry=https://registry.npmjs.org/','--store-dir=/workspace/.gptclaw-cache/pnpm'])
            for step in ['format-check','lint','typecheck','test','sdk','security','build']:
                run(root,['node','checks/quality.cjs',step])
        assert before=={f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in before}
        for platform in ['ios','android']:assert (root/'.gptclaw-build'/platform/'metadata.json').is_file()
    if not args.skip_failure_checks:
        root=roots[0];file=root/'src/components/Counter.tsx';original=file.read_bytes()
        try:
            file.write_text(original.decode().replace('value + 1','value + 0'));run(root,['pnpm','test'],False)
        finally:file.write_bytes(original)
        file=root/'src/app/defect.tsx'
        try:
            file.write_text("const invalid: number = 'wrong';\nexport default invalid;\n");run(root,['pnpm','typecheck'],False)
            file.write_text('export default function Broken( {\n');run(root,['pnpm','lint'],False)
            file.write_text('export default function X(){return null}\n');run(root,['node','checks/quality.cjs','format-check'],False)
        finally:file.unlink(missing_ok=True)
    (base/'result.json').write_text(json.dumps({'state':'passed','artifact_kind':'javascript-assets','projects':[str(p) for p in roots],'checks':records},indent=2)+'\n')
    print(json.dumps({'state':'passed','projects':2,'checks':len(records),'evidence':str(base/'result.json')}))

if __name__=='__main__':main()
