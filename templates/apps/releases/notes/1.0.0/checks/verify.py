"""Portable generated-project checks; bounded containers and synthetic fixtures only."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import uuid


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--engine', choices=['podman', 'docker'], default='docker')
    parser.add_argument('--reuse-node-image')
    parser.add_argument('--reuse-api-image')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    engine = args.engine
    token = uuid.uuid4().hex
    label = 'com.gptclaw.check='+token
    slug = 'notes-check'
    network = 'gptclaw-check-'+token
    names = {name: network+'-'+name for name in ('api','web','browser')}
    uid = str(os.getuid())+':'+str(os.getgid())
    with tempfile.TemporaryDirectory(prefix='gptclaw-notes-check.') as temp:
        work = Path(temp)
        auth = work/'auth.json'; auth.write_text('{"auths":{}}\n'); auth.chmod(0o600)
        docker = work/'docker'; docker.mkdir(); (docker/'config.json').write_text('{"auths":{}}\n')
        prefix = [engine,'--config',str(docker)] if engine=='docker' else [engine]
        def run(vector, timeout=300, optional=False):
            result = subprocess.run([*prefix,*vector],capture_output=True,text=True,timeout=timeout)
            if result.returncode and not optional:
                print((result.stdout+'\n'+result.stderr)[-4096:],flush=True)
                raise RuntimeError('Container check failed')
            return result
        common = ['--memory=1536m','--cpus=1','--pids-limit=256','--cap-drop=all','--security-opt=no-new-privileges', '--user',uid]
        if engine=='podman': common += ['--userns=keep-id']
        guards = {'api':{'PYTHONDONTWRITEBYTECODE':'1','PYTHONPATH':'/workspace/src','UV_PROJECT_ENVIRONMENT':'/workspace/.venv','UV_CACHE_DIR':'/workspace/.gptclaw-cache/uv','UV_PYTHON_DOWNLOADS':'never','UV_NO_CONFIG':'1','UV_NO_ENV_FILE':'1','UV_KEYRING_PROVIDER':'disabled'},
                  'web':{'NEXT_TELEMETRY_DISABLED':'1','NODE_OPTIONS':'--max-old-space-size=1024','pnpm_config_ignore_scripts':'true','pnpm_config_runtime':'false','pnpm_config_pm_on_fail':'error','pnpm_config_ignore_pnpmfile':'true'}}
        images = {}
        for component,recipe,reuse in [('api',root/'api/Containerfile',args.reuse_api_image),('web',root/'checks/Node.Containerfile',args.reuse_node_image)]:
            image = reuse or 'localhost/gptclaw-check:'+token+'-'+component
            if not reuse:
                context=work/component;context.mkdir();shutil.copyfile(recipe,context/'Containerfile')
                if component=='web':
                    for name in ('install-pnpm.cjs','node-profile.json'):shutil.copyfile(root/'checks'/name,context/name)
                    (context/'node-profile.json').rename(context/'profile.json')
                    text=(context/'Containerfile').read_text().replace('node-profile.json','profile.json');(context/'Containerfile').write_text(text)
                flags=['--authfile',str(auth)] if engine=='podman' else []
                run(['build',*flags,'--file',str(context/'Containerfile'),'--memory=1536m','--label',label,'--tag',image,str(context)])
            images[component]=image
            env=[arg for key,value in guards[component].items() for arg in ('--env',key+'='+value)]
            def job(vector):
                return run(['run','--rm',*common,'--volume',str(root/component)+':/workspace:rw','--workdir','/workspace','--env','GPTCLAW_PROJECT_ID='+slug,*env,image,*vector])
            if component=='api':
                job(['uv','sync','--locked','--all-groups','--no-install-project','--no-config','--no-python-downloads','--no-managed-python','--no-build','--keyring-provider=disabled','--default-index=https://pypi.org/simple'])
                job(['/workspace/.venv/bin/python','scripts/quality.py','verify'])
            else:
                job(['pnpm','install','--frozen-lockfile','--ignore-scripts','--no-runtime','--pm-on-fail=error','--ignore-pnpmfile','--registry=https://registry.npmjs.org/'])
                job(['pnpm','verify'])
            print(component+' complete quality passed',flush=True)
        subprocess.run(['python3',str(root/'checks/acquire-browser.py'),str(work/'browser')],check=True,timeout=60)
        browser_image='localhost/gptclaw-check:'+token+'-browser'
        flags=['--authfile',str(auth)] if engine=='podman' else []
        run(['build',*flags,'--file',str(work/'browser/Containerfile'),'--memory=1536m','--label',label,'--tag',browser_image,str(work/'browser')])
        run(['network','create','--internal','--label',label,network])
        try:
            for component in ('api','web'):
                env=[arg for key,value in guards[component].items() for arg in ('--env',key+'='+value)]
                vector=['/workspace/.venv/bin/python','-m','uvicorn','fastapi_app.main:create_app','--factory','--app-dir','src','--host','0.0.0.0','--port','8000','--no-access-log','--no-proxy-headers'] if component=='api' else ['pnpm','dev']
                run(['run','--detach','--name',names[component],'--label',label,*common,'--network='+network,'--network-alias='+component,'--volume',str(root/component)+':/workspace:rw','--workdir','/workspace','--env','GPTCLAW_PROJECT_ID='+slug,'--env','GPTCLAW_DEV_ORIGIN=web','--env','GPTCLAW_API_READY_URL=http://api:8000/projects/'+slug+'/api/ready',*env,images[component],*vector])
            contract=run(['run','--rm',*common,'--network='+network,'--volume',str(root/'web')+':/workspace:rw','--workdir','/workspace','--env','GPTCLAW_CONTRACT_API_URL=http://api:8000/projects/'+slug,images['web'],'pnpm','contract'])
            print(contract.stdout[-2000:],flush=True)
            output=root/'checks/output';output.mkdir(exist_ok=True)
            # Test tooling gets no app source/credential mounts; only test script/output.
            result=run(['run','--rm','--name',names['browser'],'--label',label,*common,'--network='+network,'--volume',str(root/'checks/browser.cjs')+':/checks/browser.cjs:ro','--volume',str(output)+':/checks/output:rw','--env','GPTCLAW_PROJECT_ID='+slug,browser_image,'node','browser.cjs'])
            print(result.stdout[-2000:],flush=True)
        finally:
            for name in reversed(list(names.values())):
                found=run(['container','inspect',name],optional=True)
                if found.returncode==0:
                    info=json.loads(found.stdout)[0]
                    if info.get('Config',{}).get('Labels',{}).get('com.gptclaw.check')!=token:raise RuntimeError('Unknown check owner')
                    run(['rm','--force',name])
            run(['network','rm',network])
        (output/'receipt.json').write_text(json.dumps({'images':images,'browser_image':browser_image})+'\n')
        print('Generated two-service quality, OpenAPI/CRUD contract and browser checks passed.',flush=True)


if __name__ == '__main__': main()
