#!/usr/bin/env python3
"""Real disposable PostgreSQL generation, role, quality and recovery acceptance."""
import argparse
import contextlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid
from unittest.mock import patch

sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import private_apps as a
import project_database as db
import project_groups as groups


def replace_fixture_source(root,source,contract):
    """Copy evolved source into a newly generated task-owned disposable fixture.

    Generated component provenance is retained; deleted application files and
    project-owned browser checks must match the selected source, not its starter.
    """
    for component in ('api','web','checks'):
        origin=source/(contract['components'][component]['root'] if component != 'checks' else 'checks')
        # Replace task-owned fixture source, retaining only generated provenance.
        # Overlaying leaves removed migrations/tests active in evolved applications.
        for entry in (root/component).iterdir():
            if entry.name == '.gptclaw':continue
            if entry.is_dir():shutil.rmtree(entry)
            else:entry.unlink()
        for entry in origin.rglob('*'):
            if any(part in {'.venv','.gptclaw-cache','.cache','.next','.pytest_cache','.mypy_cache','.ruff_cache','node_modules','.gptclaw','__pycache__'} for part in entry.relative_to(origin).parts):continue
            a.safe(entry)
            if entry.is_file():
                output=root/component/entry.relative_to(origin);output.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(entry,output)


def main():
    parser=argparse.ArgumentParser(description=__doc__,allow_abbrev=False)
    parser.add_argument('directory');parser.add_argument('--engine',choices=['podman','docker'],default='docker')
    parser.add_argument('--api-image');parser.add_argument('--source-root');parser.add_argument('--with-browser',action='store_true');parser.add_argument('--node-image');parser.add_argument('--skip-security',action='store_true')
    args=parser.parse_args();base=Path(args.directory).absolute()
    if base.exists():raise SystemExit('Use a new task-owned fixture directory.')
    base.mkdir(mode=0o700);projects=base/'projects';projects.mkdir();units=base/'units';units.mkdir()
    docker_config=base/'docker-config';docker_config.mkdir(mode=0o700)
    (docker_config/'config.json').write_text('{"auths":{}}\n');(docker_config/'config.json').chmod(0o600)
    slug='dbcheck-'+uuid.uuid4().hex[:12]
    command=a.command;execute=db.execute;start=db.start
    def argv(values):
        values=list(values)
        if values and values[0]=='podman':values[0]=args.engine
        if args.engine=='docker':
            values=[x for x in values if x!='--userns=keep-id']
            if values and values[0]=='docker':values=['docker','--config',str(docker_config),*values[1:]]
        return values
    def run(values,**kw):return command(argv(values),**kw)
    def quiet(values,*rest,**kw):return execute(argv(values),*rest,**kw)
    def owned(kind,name,token):
        result=run([args.engine,kind,'inspect',name],optional=True)
        if result.returncode:return False
        value=json.loads(result.stdout)[0]
        labels=value.get('Config',{}).get('Labels',{}) if kind=='container' else value.get('Labels',value.get('labels',{}))
        a.need(labels and labels.get(a.LABEL)==token,'conflict');return True
    def fixture_start(s,generation=None):return start(s,generation or s['active'])
    image=args.api_image or 'gptclaw-dbcheck-python-'+uuid.uuid4().hex[:12]
    if not args.api_image:
        run([args.engine,'build','--file',str(a.REPO/'templates/apps/python-toolchain/Containerfile'),'--tag',image,str(a.REPO/'templates/apps/python-toolchain')],timeout=300)
    with contextlib.ExitStack() as stack:
        for target,key,value in [(a,'PROJECTS',projects),(a,'STORE',base/'runtime'),(a,'UNITS',units),
                                 (db,'BASE',base/'data'),(db,'mount',lambda:None),(a,'command',run),
                                 (a,'object_owned',owned),(db,'execute',quiet),(db,'start',fixture_start)]:
            stack.enter_context(patch.object(target,key,value))
        snapshot=a.provider_bundle();stack.enter_context(patch.object(a,'REPO',snapshot))
        root=Path(a.create(slug,template='notes-postgres',template_version='1.0.0')['root'])
        value=a.target(root)[1]
        if args.source_root:
            source=Path(args.source_root).absolute();_,original,_=a.validate_project(source);a.need(original is not None and original['schema_version']==4,'invalid')
            replace_fixture_source(root,source,original)
            value['database']=original['database'];a.save(root/'.gptclaw/project.yaml',value)
        s=db.create(root,value)
        def api(action,role='runtime',generation=None,expect=True):
            file=db.home(slug)/'credentials'/s['epoch']/(role+'.json')
            db_action = action[-1] in {'migrate','seed','test'} or '-c' in action
            net = db.backend(s) if db_action else ('slirp4netns' if args.engine=='podman' else 'bridge')
            values=[args.engine,'run','--rm','--user',str(os.getuid())+':'+str(os.getgid()),
                    *(['--userns=keep-id'] if args.engine=='podman' else []),'--network='+net,
                    '--memory=1536m','--cpus=1','--pids-limit=256','--cap-drop=all','--security-opt=no-new-privileges',
                    '--volume',str(root/'api')+':/workspace:rw','--volume',str(file)+':/run/secrets/database.json:ro',
                    '--workdir=/workspace','--env','PYTHONPATH=/workspace/src','--env','PYTHONDONTWRITEBYTECODE=1',
                    '--env','GPTCLAW_DATABASE_FILE=/run/secrets/database.json','--env','GPTCLAW_DATABASE_HOST='+db.name(s,generation),
                    '--env','GPTCLAW_DATABASE_HEAD='+value['database']['head'],image,*action]
            result=run(values,timeout=300,optional=True)
            if expect and result.returncode:
                diagnostic=a.redact((result.stdout+'\n'+result.stderr)[-12000:])
                for secret_role in db.ROLES:diagnostic=diagnostic.replace(db.credential(s,secret_role)['password'],'[redacted]')
                print(diagnostic,file=sys.stderr,flush=True)
                raise a.AppError('database-command')
            return result
        try:
            db.acquire();db.start(s);db.grants(s)
            probe=run([args.engine,'exec',db.name(s),'sh','-c',"! tr '\\0' '\\n' </proc/1/environ | grep -Eq '^(POSTGRES_PASSWORD|PGPASSWORD)='"],optional=True)
            assert probe.returncode==0,'Password appeared in the database process environment'
            api(['uv','sync','--locked','--all-groups','--no-install-project','--no-config','--no-python-downloads','--cache-dir=.gptclaw-cache/uv'])
            api(['.venv/bin/python','scripts/quality.py','format'])
            api(['.venv/bin/python','-m','fastapi_app.db_cli','migrate'],role='migration')
            s.update(revision=db.revision(s),blocked=False);db.save(s)
            assert db.ready(s,value)
            for gate in ['lint','typecheck','test',*(['security'] if not args.skip_security else []),'build']:
                result=api(['.venv/bin/python','scripts/quality.py',gate]);print('PASS: persistent API '+gate,flush=True)
            empty=db.contents(s)
            api(['.venv/bin/python','-m','fastapi_app.db_cli','seed'])
            expected=db.contents(s);assert expected!=empty,'Synthetic seed did not change application records'
            db.stop(s);db.start(s);assert db.contents(s)==expected
            # Actual role denial, with secret-safe captured diagnostics suppressed.
            deny=api(['.venv/bin/python','-c',"from fastapi_app.services.database import Database; from sqlalchemy import text; c=Database().engine.connect(); c.execute(text('CREATE TABLE forbidden(id int)'))"],expect=False)
            assert deny.returncode!=0
            print('PASS: container recreation persistence and runtime DDL denial',flush=True)
            item=db.backup(s,root,value);assert item['verified']
            generation=db.allocate(s);db.start(s,generation)
            try:
                db.restore_into(s,item,generation)
                assert db.contents(s,generation)==expected
            finally:db.stop(s,generation);db.remove_generation(s,generation)
            print('PASS: consistent backup, isolated verified restore and retained active data',flush=True)
            metadata=json.dumps(db.backups(s));inspection=run([args.engine,'inspect',db.name(s)]).stdout
            for role in db.ROLES:
                assert db.credential(s,role)['password'] not in metadata+inspection
            print('PASS: credentials absent from container metadata and backup receipts',flush=True)
            db.stop(s)
            def source_job(root_arg,contract_arg,owner,action,role='migration',generation=None):
                return api(['.venv/bin/python','-m','fastapi_app.db_cli',action],role=role,generation=generation)
            with patch.object(db,'job',source_job):
                reset=db.plan(root,value,s,'reset')
                db.apply(root,value,s,reset['operation_id'],slug)
                db.start(s);assert db.contents(s)==empty;db.stop(s)
                restore=db.plan(root,value,s,'restore',item['id'])
                db.apply(root,value,s,restore['operation_id'],slug)
                db.start(s);assert db.contents(s)==expected;db.stop(s)
                db.start(s)
                api(['.venv/bin/python','-c',"from fastapi_app.services.database import Database; from sqlalchemy import text; e=Database().engine; c=e.begin(); x=c.__enter__(); x.execute(text('CREATE TABLE gptclaw_rotation_parent(id integer PRIMARY KEY)')); x.execute(text('CREATE TABLE gptclaw_rotation_child(id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,parent integer REFERENCES gptclaw_rotation_parent(id))')); x.execute(text('INSERT INTO gptclaw_rotation_parent VALUES(1)')); c.__exit__(None,None,None)"],role='migration')
                db.stop(s)
                old_epoch=s['epoch'];rotate=db.plan(root,value,s,'rotate')
                db.apply(root,value,s,rotate['operation_id'],slug)
                assert s['epoch']!=old_epoch
                db.start(s);assert db.ready(s,value)
                api(['.venv/bin/python','-c',"from fastapi_app.services.database import Database; from sqlalchemy import text; e=Database().engine; c=e.connect(); t=c.begin(); c.execute(text('INSERT INTO gptclaw_rotation_child(parent) VALUES(1)')); t.rollback(); c.close()"])
                api(['.venv/bin/python','-c',"from fastapi_app.services.database import Database; from sqlalchemy import text; e=Database().engine; c=e.begin(); x=c.__enter__(); x.execute(text('DROP TABLE gptclaw_rotation_child')); x.execute(text('DROP TABLE gptclaw_rotation_parent')); c.__exit__(None,None,None)"],role='migration')
                assert db.contents(s)==expected
                print('PASS: post-rotation runtime foreign-key/identity write and migration ownership',flush=True)
                old_role=db.credential(s,'runtime',old_epoch)
                old_pass=db.home(slug)/'credentials'/old_epoch/'runtime.passfile'
                denied=run([args.engine,'run','--rm',*(['--userns=keep-id'] if args.engine=='podman' else []),'--user',str(os.getuid()),'--network='+db.backend(s),'--volume',str(old_pass)+':/run/secrets/passfile:ro','--env','PGPASSFILE=/run/secrets/passfile','--entrypoint=psql',s['image'],'-h',db.name(s),'-U',old_role['username'],'-d','app','-c','SELECT 1;'],optional=True)
                assert denied.returncode!=0
                db.stop(s)
                inactive=[p.name for p in (db.home(slug)/'postgres').iterdir() if p.is_dir() and p.name not in {s['active'],s['rollback']}]
                prune=db.plan(root,value,s,'prune','generation:'+inactive[0])
                db.apply(root,value,s,prune['operation_id'],slug)
                assert not (db.home(slug)/'postgres'/inactive[0]).exists()
                before=s['active'];failure=db.plan(root,value,s,'reset')
                with patch.object(db,'job',side_effect=a.AppError('database-command')):
                    try:db.apply(root,value,s,failure['operation_id'],slug)
                    except a.AppError:pass
                    else:raise AssertionError('Reset failure was reported as success')
                assert s['active']==before and s['blocked'] and s['operation']['stage']=='failed'
                db.start(s);assert db.contents(s)==expected;db.stop(s)

            print('PASS: confirmed reset, staged restore and credential rotation',flush=True)
            dump=db.home(slug)/'backups'/(item['id']+'.dump');original_dump=dump.read_bytes()
            try:
                dump.write_bytes(original_dump[:-1]+bytes([original_dump[-1]^1]))
                try:db.backups(s)
                except a.AppError as error:assert error.code=='database-backup'
                else:raise AssertionError('Corrupt backup accepted')
            finally:dump.write_bytes(original_dump)
            for entry in (db.home(slug)/'postgres').iterdir():
                if entry.is_dir() and entry.name not in {s['active'],s['rollback']}:
                    prune=db.plan(root,value,s,'prune','generation:'+entry.name)
                    db.apply(root,value,s,prune['operation_id'],slug)
            # Compare all domain rows across a forward revision without conflating
            # the expected alembic_version update with application data changes.
            def domain_digest():
                statement="""CREATE OR REPLACE FUNCTION pg_temp.gptclaw_domain() RETURNS text LANGUAGE plpgsql AS $digest$
                DECLARE entry record; value text; combined jsonb := '{}'::jsonb;
                BEGIN
                  FOR entry IN SELECT tablename FROM pg_tables WHERE schemaname='public' AND tablename NOT IN ('alembic_version','gptclaw_acceptance_marker') ORDER BY tablename LOOP
                    EXECUTE format('SELECT md5(coalesce(string_agg(row_to_json(r)::text, %L ORDER BY row_to_json(r)::text),%L)) FROM public.%I r', ',', '', entry.tablename) INTO value;
                    combined := combined || jsonb_build_object(entry.tablename,value);
                  END LOOP;
                  RETURN md5(combined::text);
                END $digest$; SELECT pg_temp.gptclaw_domain();"""
                return db.sql(s,statement).strip().splitlines()[-1]
            db.start(s);before_migration=domain_digest();db.stop(s)
            previous_head=value['database']['head']
            probe_head='probe_'+uuid.uuid4().hex[:16]
            migration=root/('api/migrations/versions/'+probe_head+'.py')
            migration.write_text(f'# Synthetic forward migration.\nfrom alembic import op\nrevision={probe_head!r}\ndown_revision={previous_head!r}\nbranch_labels=None\ndepends_on=None\ndef upgrade():\n    op.execute("CREATE TABLE gptclaw_acceptance_marker(id integer PRIMARY KEY)")\ndef downgrade():\n    raise RuntimeError("Use managed restore")\n')
            value['database']['head']=probe_head;a.save(root/'.gptclaw/project.yaml',value)
            with patch.object(db,'job',source_job):
                upgrade=db.plan(root,value,s,'migrate');db.apply(root,value,s,upgrade['operation_id'],slug)
            assert s['revision']==probe_head
            db.start(s)
            assert domain_digest()==before_migration
            db.stop(s)
            print('PASS: corrupt-backup refusal and explicit data-preserving forward migration',flush=True)
            value['database']['head']=previous_head;a.save(root/'.gptclaw/project.yaml',value);migration.unlink()

            receipt={'schema_version':1,'project':slug,'postgres':db.acquire(),'manifest':4,'database':s['revision'],
                     'passed':['generation','migration','quality','persistence','role-denial','backup','restore','secret-metadata','reset','restore-promotion','rotation','old-login-denial','generation-prune','failed-reset-preservation','corrupt-backup-refusal','forward-migration'],
                     'security':'skipped-explicitly' if args.skip_security else 'passed','fixture':'isolated-rootless' if args.engine=='podman' else 'isolated-docker'}
            (base/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
        finally:
            if owned('container',db.name(s),s['token']):db.stop(s)
            if db.network(s):run([args.engine,'network','rm',db.backend(s)])
    if args.with_browser:
        browser_args=[sys.executable,str(root/'checks/verify.py'),'--engine',args.engine,'--reuse-api-image',image]
        if args.node_image:browser_args+=['--reuse-node-image',args.node_image]
        subprocess.run(browser_args,check=True,timeout=1800)
    print('PASS: real persistent PostgreSQL template workflow; fixture source/data retained at '+str(base),flush=True)


if __name__=='__main__':main()
