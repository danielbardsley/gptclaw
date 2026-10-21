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
    parser.add_argument('--reuse-api-image')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    engine = args.engine
    manifest=root/'.gptclaw/project.yaml'
    head=json.loads(manifest.read_text())['database']['head'] if manifest.exists() else '0001'
    token = os.environ.get('GPTCLAW_QUALITY_TOKEN') or uuid.uuid4().hex
    label = 'com.gptclaw.check='+token
    slug = 'notes-check'
    network = 'gptclaw-check-'+token
    names = {name: network+'-'+name for name in ('db','api')}
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
        for component,recipe,reuse in [('api',root/'api/Containerfile',args.reuse_api_image)]:
            image = reuse or 'localhost/gptclaw-check:'+token+'-'+component
            if not reuse:
                context=work/component;context.mkdir();shutil.copyfile(recipe,context/'Containerfile')
                flags=['--authfile',str(auth)] if engine=='podman' else []
                run(['build',*flags,'--file',str(context/'Containerfile'),'--memory=1536m','--label',label,'--tag',image,str(context)])
            images[component]=image
            env=[arg for key,value in guards[component].items() for arg in ('--env',key+'='+value)]
            def job(vector,role='runtime',database=False):
                dbargs=['--network='+network,'--volume',str(files[role])+':/run/secrets/database.json:ro','--env','GPTCLAW_DATABASE_FILE=/run/secrets/database.json','--env','GPTCLAW_DATABASE_HOST=db','--env','GPTCLAW_DATABASE_HEAD='+head] if database else []
                return run(['run','--rm','--label',label,*common,'--volume',str(root/component)+':/workspace:rw','--workdir','/workspace','--env','GPTCLAW_PROJECT_ID='+slug,*env,*dbargs,image,*vector])
            if component=='api':
                job(['uv','sync','--locked','--all-groups','--no-install-project','--no-config','--no-python-downloads','--no-managed-python','--no-build','--keyring-provider=disabled','--default-index=https://pypi.org/simple'])
                job(['/workspace/.venv/bin/python','-m','fastapi_app.db_cli','migrate'],role='migration',database=True)
                for gate in ('lint','typecheck','test','security','build'):job(['/workspace/.venv/bin/python','scripts/quality.py',gate],database=gate=='test')
                # QLT-007: exercise an actual forward change and recovery in this
                # uniquely labelled disposable database, never a managed project.
                info=json.loads(run(['container','inspect',names['db']]).stdout)[0]
                if info.get('Config',{}).get('Labels',{}).get('com.gptclaw.check')!=token:
                    raise RuntimeError('Foreign migration fixture refused')
                dbexec=['exec','--env','PGPASSFILE=/run/secrets/passfile',names['db']]
                def sql(database,statement,optional=False):
                    return run([*dbexec,'psql','-h','127.0.0.1','-U','admin','-d',database,'-X','--set=ON_ERROR_STOP=1','-At','-c',statement],optional=optional)
                denied=sql('app','SET ROLE runtime; CREATE TABLE qlt_forbidden(id integer);',optional=True)
                if denied.returncode==0:raise RuntimeError('Application role unexpectedly has DDL permission')
                client_output=work/'native-client-output';client_output.mkdir(exist_ok=True)
                def native_client(phase):
                    node_image=json.loads((root/'checks/node-client-profile.json').read_text())['image']
                    launch=['/workspace/.venv/bin/python','-m','uvicorn','fastapi_app.main:create_app','--factory','--app-dir','src','--host','0.0.0.0','--port','8000','--no-access-log','--no-proxy-headers']
                    if phase=='measure':
                        launch=['/workspace/.venv/bin/python','-c','import os,uvicorn; from fastapi_app.main import create_app; from fastapi_app.settings import Settings; uvicorn.run(create_app(Settings(project_id=os.environ["GPTCLAW_PROJECT_ID"],request_limit=1000)),host="0.0.0.0",port=8000,access_log=False,proxy_headers=False)']
                    started_ms=str(int(time.time()*1000))
                    run(['run','--detach','--name',names['api'],'--label',label,*common,'--network='+network,'--network-alias=api',
                         '--volume',str(root/'api')+':/workspace:rw','--volume',str(files['runtime'])+':/run/secrets/database.json:ro',
                         '--workdir','/workspace','--env','GPTCLAW_PROJECT_ID='+slug,'--env','PYTHONPATH=/workspace/src',
                         '--env','GPTCLAW_DATABASE_FILE=/run/secrets/database.json','--env','GPTCLAW_DATABASE_HOST=db','--env','GPTCLAW_DATABASE_HEAD='+head,
                         image,*launch])
                    try:
                        run(['run','--rm','--label',label,*common,'--network='+network,'--volume',str(root/'checks/v1-client')+':/client:ro',
                             '--volume',str(client_output)+':/output:rw','--workdir','/client','--env','GPTCLAW_COMPAT_URL=http://api:8000/projects/'+slug+'/api',
                             '--env','GPTCLAW_COMPAT_PHASE='+phase,'--env','QLT_START_MS='+started_ms,'--env','QUALITY_BENCHMARK='+os.environ.get('GPTCLAW_QUALITY_BENCHMARK','0'),node_image,'node','performance.cjs' if phase=='measure' else 'check.cjs'])
                        if phase=='measure':
                            sample=json.loads((client_output/'http-sample.json').read_text());peaks=[]
                            for service in ('api','db'):
                                observed=run(['exec',names[service],'cat','/sys/fs/cgroup/memory.peak'],optional=True)
                                if observed.returncode==0 and observed.stdout.strip().isdigit():peaks.append(int(observed.stdout.strip()))
                            sample['peak_memory_mib']=sum(peaks)/(1024*1024) if len(peaks)==2 else None
                            output=root/'.gptclaw-cache/quality';output.mkdir(parents=True,exist_ok=True)
                            (output/'http-sample.json').write_text(json.dumps(sample,indent=2)+'\n')
                    finally:
                        info=json.loads(run(['container','inspect',names['api']]).stdout)[0]
                        if info.get('Config',{}).get('Labels',{}).get('com.gptclaw.check')!=token:raise RuntimeError('Foreign compatibility container refused')
                        run(['rm','--force',names['api']])
                native_client('before')
                fixture_id='00000000-0000-0000-0000-000000000001'
                sql('app',"INSERT INTO notes(id,title,body) VALUES ('"+fixture_id+"','QLT preserved row','synthetic');")
                run([*dbexec,'pg_dump','-h','127.0.0.1','-U','admin','-d','app','--format=custom','--file=/tmp/qlt-before.dump'])
                sql('postgres','CREATE DATABASE qlt_verified_backup OWNER admin;')
                run([*dbexec,'pg_restore','-h','127.0.0.1','-U','admin','-d','qlt_verified_backup','--exit-on-error','/tmp/qlt-before.dump'])
                assert sql('qlt_verified_backup',"SELECT title FROM notes WHERE id='"+fixture_id+"'").stdout.strip()=='QLT preserved row'
                previous_head=head
                forward=root/'api/migrations/versions/qlt0002.py'
                failing=root/'api/migrations/versions/qlt0003.py'
                if forward.exists() or failing.exists():raise RuntimeError('QLT fixture migration path occupied')
                try:
                    forward.write_text('from alembic import op\nrevision="qlt0002"\ndown_revision='+repr(previous_head)+'\ndef upgrade():\n    op.execute("ALTER TABLE notes ADD COLUMN qlt_marker text")\ndef downgrade():\n    raise RuntimeError("Use verified restore")\n')
                    head='qlt0002'
                    job(['/workspace/.venv/bin/python','-m','fastapi_app.db_cli','migrate'],role='migration',database=True)
                    assert sql('app',"SELECT title FROM notes WHERE id='"+fixture_id+"'").stdout.strip()=='QLT preserved row'
                    assert sql('app',"SELECT count(*) FROM information_schema.columns WHERE table_name='notes' AND column_name='qlt_marker'").stdout.strip()=='1'
                    native_client('after')
                    failing.write_text('revision="qlt0003"\ndown_revision="qlt0002"\ndef upgrade():\n    raise RuntimeError("Synthetic QLT migration failure")\ndef downgrade():\n    raise RuntimeError("Use verified restore")\n')
                    head='qlt0003'
                    try:job(['/workspace/.venv/bin/python','-m','fastapi_app.db_cli','migrate'],role='migration',database=True)
                    except RuntimeError:pass
                    else:raise RuntimeError('Injected failed migration unexpectedly passed')
                    assert sql('app',"SELECT version_num FROM alembic_version").stdout.strip()=='qlt0002'
                    # Promote the already restore-verified backup while no clients run.
                    sql('postgres','ALTER DATABASE app RENAME TO qlt_failed_generation;')
                    sql('postgres','ALTER DATABASE qlt_verified_backup RENAME TO app;')
                    sql('app','REVOKE ALL ON DATABASE app FROM PUBLIC; GRANT CONNECT ON DATABASE app TO migration,runtime;')
                    assert sql('app',"SELECT title FROM notes WHERE id='"+fixture_id+"'").stdout.strip()=='QLT preserved row'
                    assert sql('app',"SELECT version_num FROM alembic_version").stdout.strip()==previous_head
                    head=previous_head
                    native_client('after')
                    sql('app',"DELETE FROM notes WHERE id='"+fixture_id+"';")
                    sql('postgres','DROP DATABASE qlt_failed_generation;')
                finally:
                    head=previous_head
                    forward.unlink(missing_ok=True);failing.unlink(missing_ok=True)
                native_client('measure')
                print('Forward migration preserves old columns/rows; failed migration refused; verified backup restored; runtime DDL denied.',flush=True)
            print(component+' complete quality passed',flush=True)
        before=run(['exec','--env','PGPASSFILE=/run/secrets/passfile',names['db'],'psql','-h','127.0.0.1','-U','admin','-d','app','-At','-c','SELECT count(*) FROM notes']).stdout
        run(['restart',names['db']])
        for attempt in range(120):
            ready=run(['exec','--env','PGPASSFILE=/run/secrets/passfile',names['db'],'psql','-h','127.0.0.1','-U','admin','-d','app','-At','-c','SELECT count(*) FROM notes'],optional=True)
            if ready.returncode==0:break
            time.sleep(.5)
        else:raise RuntimeError('Database restart failed')
        assert ready.stdout==before,'Saved records changed across restart'
        cleanup();atexit.unregister(cleanup)
        print('Generated Python API/DB quality and restart persistence passed.',flush=True)


if __name__ == '__main__': main()
