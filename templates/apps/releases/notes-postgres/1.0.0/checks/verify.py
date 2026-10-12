"""Portable generated-project checks; bounded containers and synthetic fixtures only."""
import argparse
import json
import os
from pathlib import Path
import shutil
import secrets
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
    manifest=root/'.gptclaw/project.yaml'
    head=json.loads(manifest.read_text())['database']['head'] if manifest.exists() else '0001'
    token = uuid.uuid4().hex
    label = 'com.gptclaw.check='+token
    slug = 'notes-check'
    network = 'gptclaw-check-'+token
    names = {name: network+'-'+name for name in ('db','api','web','browser')}
    uid = str(os.getuid())+':'+str(os.getgid())
    with tempfile.TemporaryDirectory(prefix='gptclaw-notes-check.') as temp:
        work = Path(temp)
        auth = work/'auth.json'; auth.write_text('{"auths":{}}\n'); auth.chmod(0o600)
        docker = work/'docker'; docker.mkdir(); (docker/'config.json').write_text('{"auths":{}}\n')
        prefix = [engine,'--config',str(docker)] if engine=='docker' else [engine]
        passwords=[]
        def run(vector, timeout=300, optional=False, payload=None):
            result = subprocess.run([*prefix,*vector],input=payload,capture_output=True,text=True,timeout=timeout)
            if result.returncode and not optional:
                diagnostic=(result.stdout+'\n'+result.stderr)[-4096:]
                for password in passwords:diagnostic=diagnostic.replace(password,'[redacted]')
                print(diagnostic,flush=True)
                raise RuntimeError('Container check failed')
            return result
        common = ['--memory=1536m','--cpus=1','--pids-limit=256','--cap-drop=all','--security-opt=no-new-privileges', '--user',uid]
        if engine=='podman': common += ['--userns=keep-id']
        guards = {'api':{'PYTHONDONTWRITEBYTECODE':'1','PYTHONPATH':'/workspace/src','UV_PROJECT_ENVIRONMENT':'/workspace/.venv','UV_CACHE_DIR':'/workspace/.gptclaw-cache/uv','UV_PYTHON_DOWNLOADS':'never','UV_NO_CONFIG':'1','UV_NO_ENV_FILE':'1','UV_KEYRING_PROVIDER':'disabled'},
                  'web':{'NEXT_TELEMETRY_DISABLED':'1','NODE_OPTIONS':'--max-old-space-size=1024','pnpm_config_ignore_scripts':'true','pnpm_config_runtime':'false','pnpm_config_pm_on_fail':'error','pnpm_config_ignore_pnpmfile':'true'}}
        database_image='docker.io/library/postgres@sha256:9551dd5bf356409a21b31248f49b33bba9bb1877365f3a7e933aecd9af3cf52d'
        files={}
        for role in ('admin','migration','runtime'):
            password=secrets.token_hex(32);passwords.append(password)
            file=work/(role+'.json');file.write_text(json.dumps({'username':role,'password':password}));file.chmod(0o600);files[role]=file
        admin_password=work/'admin.password';admin_password.write_text(passwords[0]);admin_password.chmod(0o600)
        passfile=work/'admin.passfile';passfile.write_text('*:*:*:admin:'+passwords[0]+'\n');passfile.chmod(0o600)
        data=work/'postgres';data.mkdir(mode=0o700)
        run(['network','create','--internal','--label',label,network])
        def cleanup():
            for name in reversed(list(names.values())):
                found=run(['container','inspect',name],optional=True)
                if found.returncode==0:
                    info=json.loads(found.stdout)[0]
                    if info.get('Config',{}).get('Labels',{}).get('com.gptclaw.check')!=token:raise RuntimeError('Unknown check owner')
                    run(['rm','--force',name])
            run(['network','rm',network],optional=True)
        # Register owned cleanup before any startup or quality failure can occur.
        import atexit
        atexit.register(cleanup)
        run(['run','--detach','--name',names['db'],'--label',label,*common,'--network='+network,'--network-alias=db',
             '--volume',str(data)+':/var/lib/postgresql/data:rw','--volume',str(admin_password)+':/run/secrets/password:ro','--volume',str(passfile)+':/run/secrets/passfile:ro',
             '--env','PGDATA=/var/lib/postgresql/data','--env','POSTGRES_USER=admin','--env','POSTGRES_DB=app','--env','POSTGRES_PASSWORD_FILE=/run/secrets/password',
             '--env','POSTGRES_INITDB_ARGS=--auth-host=scram-sha-256 --auth-local=scram-sha-256',database_image,'postgres','-c','log_statement=none','-c','log_min_error_statement=panic'])
        import time
        for attempt in range(120):
            if run(['exec','--env','PGPASSFILE=/run/secrets/passfile',names['db'],'psql','-h','127.0.0.1','-U','admin','-d','app','-c','SELECT 1;'],optional=True).returncode==0:break
            time.sleep(.5)
        else:raise RuntimeError('Database readiness failed')
        sql=("REVOKE ALL ON DATABASE app FROM PUBLIC; REVOKE ALL ON SCHEMA public FROM PUBLIC; "
             +"CREATE ROLE migration LOGIN PASSWORD '"+passwords[1]+"'; CREATE ROLE runtime LOGIN PASSWORD '"+passwords[2]+"'; "
             +"GRANT CONNECT ON DATABASE app TO migration,runtime; GRANT USAGE ON SCHEMA public TO migration,runtime; GRANT CREATE ON SCHEMA public TO migration; "
             +"ALTER DEFAULT PRIVILEGES FOR ROLE migration IN SCHEMA public GRANT SELECT,INSERT,UPDATE,DELETE ON TABLES TO runtime; "
             +"ALTER DEFAULT PRIVILEGES FOR ROLE migration IN SCHEMA public GRANT USAGE,SELECT ON SEQUENCES TO runtime;")
        run(['exec','--interactive','--env','PGPASSFILE=/run/secrets/passfile',names['db'],'psql','-h','127.0.0.1','-U','admin','-d','app','-X','--set=ON_ERROR_STOP=1'],payload=sql)
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
            def job(vector,role='runtime',database=False):
                dbargs=['--network='+network,'--volume',str(files[role])+':/run/secrets/database.json:ro','--env','GPTCLAW_DATABASE_FILE=/run/secrets/database.json','--env','GPTCLAW_DATABASE_HOST=db','--env','GPTCLAW_DATABASE_HEAD='+head] if database else []
                return run(['run','--rm',*common,'--volume',str(root/component)+':/workspace:rw','--workdir','/workspace','--env','GPTCLAW_PROJECT_ID='+slug,*env,*dbargs,image,*vector])
            if component=='api':
                job(['uv','sync','--locked','--all-groups','--no-install-project','--no-config','--no-python-downloads','--no-managed-python','--no-build','--keyring-provider=disabled','--default-index=https://pypi.org/simple'])
                job(['/workspace/.venv/bin/python','-m','fastapi_app.db_cli','migrate'],role='migration',database=True)
                for gate in ('lint','typecheck','test','security','build'):job(['/workspace/.venv/bin/python','scripts/quality.py',gate],database=gate=='test')
            else:
                job(['pnpm','install','--frozen-lockfile','--ignore-scripts','--no-runtime','--pm-on-fail=error','--ignore-pnpmfile','--registry=https://registry.npmjs.org/'])
                job(['pnpm','verify'])
            print(component+' complete quality passed',flush=True)
        subprocess.run(['python3',str(root/'checks/acquire-browser.py'),str(work/'browser')],check=True,timeout=60)
        browser_image='localhost/gptclaw-check:'+token+'-browser'
        flags=['--authfile',str(auth)] if engine=='podman' else []
        run(['build',*flags,'--file',str(work/'browser/Containerfile'),'--memory=1536m','--label',label,'--tag',browser_image,str(work/'browser')])
        try:
            for component in ('api','web'):
                env=[arg for key,value in guards[component].items() for arg in ('--env',key+'='+value)]
                vector=['/workspace/.venv/bin/python','-m','uvicorn','fastapi_app.main:create_app','--factory','--app-dir','src','--host','0.0.0.0','--port','8000','--no-access-log','--no-proxy-headers'] if component=='api' else ['pnpm','dev']
                dbargs=['--volume',str(files['runtime'])+':/run/secrets/database.json:ro','--env','GPTCLAW_DATABASE_FILE=/run/secrets/database.json','--env','GPTCLAW_DATABASE_HOST=db','--env','GPTCLAW_DATABASE_HEAD='+head] if component=='api' else []
                run(['run','--detach','--name',names[component],'--label',label,*common,'--network='+network,'--network-alias='+component,'--volume',str(root/component)+':/workspace:rw','--workdir','/workspace','--env','GPTCLAW_PROJECT_ID='+slug,'--env','GPTCLAW_DEV_ORIGIN=web','--env','GPTCLAW_API_READY_URL=http://api:8000/projects/'+slug+'/api/ready',*env,*dbargs,images[component],*vector])
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
            atexit.unregister(cleanup)
        (output/'receipt.json').write_text(json.dumps({'images':images,'browser_image':browser_image})+'\n')
        print('Generated persistent three-service quality, OpenAPI/CRUD contract and browser checks passed.',flush=True)


if __name__ == '__main__': main()
