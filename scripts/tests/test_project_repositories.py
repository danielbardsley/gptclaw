#!/usr/bin/env python3
"""Offline GitHub transport fixtures plus real isolated Git objects/publication."""
import base64
import contextlib
import copy
import datetime as dt
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import private_apps as app
import project_repositories as repos
import project_templates as templates
import gptclawctl as cli


class FakeAPI:
    def __init__(self, bare):
        self.bare = bare; self.remote = None; self.protection = None; self.environments = {}
        self.prs = []; self.calls = []; self.fail_after = None; self.fail_before = None
        self.expiry = (dt.datetime.now(dt.timezone.utc)+dt.timedelta(hours=2)).isoformat()
        self.secrets = {}; self.actor_name = repos.ACCOUNT; self.plan_name = 'pro'
    def actor(self):
        repos.require(self.actor_name == repos.ACCOUNT, 'repository-credential')
        repos.require(self.plan_name == 'pro', 'repository-capability')
        return {'login': self.actor_name, 'plan': self.plan_name, 'credential_kind': 'fine-grained-pat', 'expires_at': self.expiry}
    def raw_git(self, *args, input_bytes=None):
        env = {k:v for k,v in os.environ.items() if not k.startswith('GIT_')}
        env.update(GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL='/dev/null',GIT_AUTHOR_NAME='GptClaw',
                   GIT_AUTHOR_EMAIL='gptclaw@users.noreply.github.com',GIT_COMMITTER_NAME='GptClaw',
                   GIT_COMMITTER_EMAIL='gptclaw@users.noreply.github.com',GIT_AUTHOR_DATE='2000-01-01T00:00:00+0000',
                   GIT_COMMITTER_DATE='2000-01-01T00:00:00+0000')
        out = subprocess.run(['git','-c','core.hooksPath=/dev/null','-C',str(self.bare),*args],env=env,
                             input=input_bytes,capture_output=True)
        if out.returncode: return None
        return out.stdout
    def ref(self, name):
        out = self.raw_git('rev-parse','--verify','refs/heads/'+name)
        return out.decode().strip() if out else None
    def request(self, method, path, body=None, missing=False):
        self.calls.append((method,path,copy.deepcopy(body)))
        if self.fail_before == (method,path):
            self.fail_before = None; raise app.AppError('repository-api')
        result = self.route(method,path,body,missing)
        if self.fail_after == (method,path):
            self.fail_after = None; raise app.AppError('repository-api')
        return copy.deepcopy(result)
    def route(self, method, path, body, missing):
        if method == 'POST' and path == '/user/repos':
            if self.remote: raise app.AppError('repository-api')
            self.remote = {'id': 42,'full_name':repos.ACCOUNT+'/'+body['name'],'private':body['private'],
                'owner':{'login':repos.ACCOUNT,'type':'User'},'archived':False,'description':body['description'],
                'permissions':{'admin':True},'default_branch':'main'}
            return self.remote
        if '/git/ref/heads/' in path:
            name = path.split('/git/ref/heads/')[1];sha = self.ref(name)
            return {'ref':'refs/heads/'+name,'object':{'type':'commit','sha':sha}} if sha else None
        if '/branches/main/protection' in path:
            if method == 'PUT':
                self.protection = {k:{'enabled':v} if isinstance(v,bool) else v for k,v in body.items()}
            return self.protection
        if '/git/blobs' in path:
            sha = self.raw_git('hash-object','-w','--stdin',input_bytes=base64.b64decode(body['content']))
            return {'sha':sha.decode().strip()}
        if '/git/trees' in path:
            self.raw_git('read-tree','--empty')
            for item in body['tree']:
                self.raw_git('update-index','--add','--cacheinfo',item['mode'],item['sha'],item['path'])
            return {'sha':self.raw_git('write-tree').decode().strip()}
        if '/git/commits' in path:
            sha = self.raw_git('commit-tree',body['tree'],'-p',body['parents'][0],input_bytes=body['message'].encode())
            return {'sha':sha.decode().strip()}
        if '/git/refs' in path:
            # Compare-and-create mirrors the endpoint, not Git's fast-forward update.
            if self.ref(body['ref'].removeprefix('refs/heads/')): raise app.AppError('repository-api')
            self.raw_git('update-ref',body['ref'],body['sha'],'0'*40)
            return {'ref':body['ref'],'object':{'sha':body['sha']}}
        if '/secrets/' in path:
            return self.secrets.get(path)
        if '/environments/' in path:
            name=path.split('/environments/')[1]
            if method=='PUT':self.environments[name]={**body,'protection_rules':[]}
            return self.environments.get(name)
        if '/pulls?' in path:
            query=parse_qs(path.split('?')[1]);head=query['head'][0].split(':',1)[1]
            return [p for p in self.prs if p['head']['ref']==head]
        if path.endswith('/pulls') and method=='POST':
            p={'number':len(self.prs)+1,'state':'open','merged_at':None,
               'head':{'ref':body['head'],'sha':self.ref(body['head']),'repo':{'id':42}},
               'base':{'ref':body['base'],'sha':self.ref(body['base']),'repo':{'id':42}}}
            self.prs.append(p);return p
        if method == 'PATCH':self.remote.update(body);return self.remote
        if method == 'GET':return self.remote
        raise AssertionError((method,path,body))


class Tests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        self.base=Path(temp.name);self.projects=self.base/'projects';self.projects.mkdir()
        self.bare=self.base/'remote.git'
        subprocess.run(['git','init','--bare',str(self.bare)],check=True,capture_output=True)
        self.api=FakeAPI(self.bare)
        for key,value in [('PROJECTS',self.projects),('STORE',self.projects/'.gptclaw-runtime/v1')]:
            p=patch.object(app,key,value);p.start();self.addCleanup(p.stop)
        self.original_git=repos.git
        p=patch.object(repos,'git',self.git);p.start();self.addCleanup(p.stop)
        self.plan=self.new_plan()
    def git(self,root,*args,api=None,input_bytes=None):
        if args[0]=='push':
            # Test transport sends only to a task-owned bare fixture.
            out=subprocess.run(['git','-c','core.hooksPath=/dev/null','-C',str(root),'push',str(self.bare),args[2]],capture_output=True)
            repos.require(out.returncode==0,'repository-recovery')
            if getattr(self,'lost_push',False):
                self.lost_push=False;raise app.AppError('repository-recovery')
            return out.stdout
        return self.original_git(root,*args,input_bytes=input_bytes)
    def new_plan(self,**kwargs):
        return repos.plan('sample',str(self.projects/'sample'),self.api,**kwargs)['plan']
    def apply(self,**kwargs):return repos.apply(self.plan,self.api,**kwargs)
    def resume(self,**kwargs):return repos.resume(self.plan['operation_id'],self.api,**kwargs)
    def receipt(self):return repos.read_receipt(self.plan['operation_id'])
    def reseal(self,value):value['plan_digest']=repos.digest({k:v for k,v in value.items() if k!='plan_digest'});return value
    def test_plan_read_only_exact_and_no_secret_permissions(self):
        before=list(self.base.rglob('*'))
        with patch.object(repos,'git') as run,patch.object(app,'save') as write:
            value=self.new_plan();run.assert_not_called();write.assert_not_called()
        self.assertEqual(list(self.base.rglob('*')),before)
        self.assertEqual(value['template'],templates.provenance(templates.resolve('nextjs','1.0.0')[0]))
        self.assertNotIn('secrets:read-metadata',value['capabilities'])
        self.assertTrue(all(method=='GET' for method,_,_ in self.api.calls))
    def test_local_invalid_input_before_api(self):
        for name in ['../bad','UPPER','bad.git','x'*49]:
            count=len(self.api.calls)
            with self.assertRaises(app.AppError):repos.plan(name,str(self.projects/'sample'),self.api)
            self.assertEqual(count,len(self.api.calls))
        with self.assertRaises(app.AppError):self.new_plan(environments=['production'])
        with self.assertRaises(app.AppError):self.new_plan(environments=['development','development'])
        with self.assertRaises(app.AppError):self.new_plan(secret_references=[{'scope':'repository','name':'SECRET','value':'synthetic'}])
        with self.assertRaises(app.AppError):self.new_plan(secret_references=[{'scope':'production','name':'SECRET'}])
    def test_public_other_account_tampering_and_unsupported_release(self):
        for key,value in [('private',False),('account','other'),('protection',{}),('template',{'id':'python'}),('extra',True)]:
            plan=copy.deepcopy(self.plan);plan[key]=value;self.reseal(plan)
            with self.assertRaises(app.AppError):repos.apply(plan,self.api)
        self.assertIsNone(self.api.remote)
        plan=copy.deepcopy(self.plan);plan['destination']='/tmp/elsewhere';self.reseal(plan)
        with self.assertRaises(app.AppError):repos.apply(plan,self.api)
    def test_existing_destination_symlink_and_remote_collision(self):
        target=self.projects/'sample';target.mkdir();(target/'kept').write_text('user')
        with self.assertRaises(app.AppError):self.apply()
        self.assertEqual((target/'kept').read_text(),'user')
        target.rename(self.projects/'saved');target.symlink_to(self.projects/'saved')
        with self.assertRaises(app.AppError):self.apply()
        target.unlink();self.api.remote={'id':999}
        with self.assertRaises(app.AppError):self.new_plan()
    def test_success_real_git_history_provenance_and_only_initial_pr(self):
        receipt=self.apply();root=self.projects/'sample'
        self.assertEqual(receipt['state'],'repository-ready');self.assertEqual(len(self.api.prs),1)
        self.assertEqual(self.api.ref('main'),receipt['bootstrap_sha'])
        inventory=self.api.raw_git('ls-tree','-r','--name-only','main').decode().splitlines()
        self.assertEqual(inventory,['README.md'])
        self.assertEqual(self.git(root,'rev-parse','HEAD').decode().strip(),receipt['starter_sha'])
        self.assertEqual(app.validate_project(root)[2],0);templates.validate_provenance(root)
        self.assertIn('https://github.com/danielbardsley/sample',(root/'AGENTS.md').read_text())
        self.assertEqual(self.git(root,'remote','get-url','origin').decode().strip(),'https://github.com/danielbardsley/sample.git')
        put_index=next(i for i,c in enumerate(self.api.calls) if '/protection' in c[1] and c[0]=='PUT')
        branch_index=next(i for i,c in enumerate(self.api.calls) if c[1].endswith('/git/refs') and c[0]=='POST')
        self.assertLess(put_index,branch_index)
        self.assertFalse(any('/secrets/' in path or '/environments/' in path for _,path,_ in self.api.calls))
        self.resume();self.assertEqual(len(self.api.prs),1)
    def test_create_only_then_scoped_resume(self):
        receipt=self.apply(create_only=True)
        self.assertEqual(receipt['state'],'operator-required')
        self.assertEqual(receipt['repository_id'],42)
        self.assertFalse((repos.workspace(self.plan['operation_id'])/'source').exists())
        self.assertFalse(any('/protection' in path for _,path,_ in self.api.calls))
        self.assertEqual(self.resume()['state'],'repository-ready')
    def test_creation_response_loss_never_adopts_by_name(self):
        self.api.fail_after=('POST','/user/repos')
        with self.assertRaises(app.AppError):self.apply()
        with self.assertRaises(app.AppError):self.resume()
        self.assertEqual(sum(method=='POST' and path=='/user/repos' for method,path,_ in self.api.calls),1)
        self.assertEqual(repos.status(self.plan['operation_id'],self.api)['remote_observation']['candidate_repository_id'],42)
        with self.assertRaises(app.AppError):self.resume(repository_id=99)
        self.assertIsNone(self.receipt()['repository_id'])
        self.assertEqual(self.resume(repository_id=42)['state'],'repository-ready')
    def test_creation_denial_is_ambiguous_and_preserves_receipt(self):
        self.api.fail_before=('POST','/user/repos')
        with self.assertRaises(app.AppError):self.apply()
        self.assertEqual(self.receipt()['state'],'recovery-required')
        with self.assertRaises(app.AppError):self.resume()
        self.assertIsNone(self.api.remote)
    def test_lost_main_push_reconciles_same_sha(self):
        self.lost_push=True
        with self.assertRaises(app.AppError):self.apply()
        sha=self.api.ref('main');self.assertIsNotNone(sha)
        receipt=self.resume();self.assertEqual(receipt['bootstrap_sha'],sha)
    def test_each_remote_mutation_response_loss_resumes_without_duplicates(self):
        # Fresh independent fixture per subcase; object POSTs are content addressed.
        paths=['/branches/main/protection','/git/blobs','/git/trees','/git/commits','/git/refs','/pulls']
        for suffix in paths:
            with self.subTest(suffix=suffix):
                temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
                bare=Path(temp.name)/'remote.git';subprocess.run(['git','init','--bare',str(bare)],check=True,capture_output=True)
                self.bare=bare;self.api=FakeAPI(bare)
                name='case-'+str(paths.index(suffix));self.plan=repos.plan(name,str(self.projects/name),self.api)['plan']
                self.api.fail_after=('PUT' if 'protection' in suffix else 'POST',repos.prefix(self.plan)+suffix)
                with self.assertRaises(app.AppError):self.apply()
                result=self.resume();self.assertEqual(result['state'],'repository-ready')
                self.assertEqual(len(self.api.prs),1)
    def test_environment_and_secret_metadata(self):
        self.plan=self.new_plan(environments=['development'],secret_references=[{'scope':'development','name':'DB_URL'},{'scope':'repository','name':'API_KEY'}])
        self.api.secrets[repos.prefix(self.plan)+'/actions/secrets/API_KEY']={'name':'API_KEY'}
        receipt=self.apply()
        self.assertEqual(receipt['secret_reference_readback'],[{'scope':'development','name':'DB_URL','state':'pending-provisioning'},
                                                            {'scope':'repository','name':'API_KEY','state':'metadata-verified'}])
        self.assertFalse(any(method!='GET' and '/secrets/' in path for method,path,_ in self.api.calls))
        self.assertTrue(receipt['environment_readback']['development']['verified'])
    def test_environment_response_loss(self):
        self.plan=self.new_plan(environments=['development'])
        path=repos.prefix(self.plan)+'/environments/development';self.api.fail_after=('PUT',path)
        with self.assertRaises(app.AppError):self.apply()
        self.resume();self.assertEqual(sum(m=='PUT' and p==path for m,p,_ in self.api.calls),1)
    def test_protection_denial_stops_before_starter(self):
        self.api.fail_before=('PUT',repos.prefix(self.plan)+'/branches/main/protection')
        with self.assertRaises(app.AppError):self.apply()
        self.assertIsNone(self.api.ref(self.plan['branches']['head']))
        self.assertEqual(self.receipt()['local_phase'],'bootstrap')
    def test_protection_drift_never_repaired_implicitly(self):
        self.apply();self.api.protection['allow_force_pushes']['enabled']=True
        mutations=sum(m!='GET' for m,_,_ in self.api.calls)
        with self.assertRaises(app.AppError):self.resume()
        self.assertEqual(mutations,sum(m!='GET' for m,_,_ in self.api.calls))
    def test_wrong_id_visibility_description_or_deleted_protection(self):
        self.apply();original=copy.deepcopy(self.api.remote)
        for key,value in [('id',99),('private',False),('description','changed'),('archived',True)]:
            self.api.remote={**original,key:value}
            with self.assertRaises(app.AppError):self.resume()
        self.api.remote=original;self.api.protection=None
        with self.assertRaises(app.AppError):self.resume()
    def test_changed_source_or_foreign_local_destination(self):
        self.api.fail_before=('PUT',repos.prefix(self.plan)+'/branches/main/protection')
        with self.assertRaises(app.AppError):self.apply()
        source=repos.workspace(self.plan['operation_id'])/'source';(source/'README.md').write_text('editor')
        with self.assertRaises(app.AppError):self.resume()
        self.assertEqual((source/'README.md').read_text(),'editor')
    def test_completed_local_source_edit_stops_without_overwrite(self):
        self.apply();path=self.projects/'sample'/'README.md';path.write_text('user edit')
        with self.assertRaises(app.AppError):self.resume()
        self.assertEqual(path.read_text(),'user edit')
    def test_rename_response_loss_reconciles_owned_destination(self):
        original=templates.publish
        def lost(stage,dest):
            original(stage,dest)
            if Path(dest)==self.projects/'sample':raise OSError('lost receipt')
        with patch.object(templates,'publish',lost):
            with self.assertRaises(app.AppError):self.apply()
        self.assertEqual(self.resume()['state'],'repository-ready')
    def test_status_observation_only(self):
        self.apply();receipt_path=repos.workspace(self.plan['operation_id'])/'receipt.json';before=receipt_path.read_bytes()
        with patch.object(app,'save') as write:repos.status(self.plan['operation_id'],self.api);write.assert_not_called()
        self.assertEqual(receipt_path.read_bytes(),before)
    def test_same_target_lock_and_second_apply_conflict(self):
        with app.locked('repository-sample'):
            with self.assertRaises(app.AppError) as caught:self.apply()
            self.assertEqual(caught.exception.code,'busy')
        self.assertIsNone(self.api.remote)
        self.apply()
        with self.assertRaises(app.AppError):self.apply()
        self.assertEqual(len(self.api.prs),1)
    def test_unsafe_journal_and_plan_files(self):
        self.apply();path=repos.workspace(self.plan['operation_id'])/'receipt.json';path.unlink();path.symlink_to('/dev/null')
        with self.assertRaises(app.AppError):repos.status(self.plan['operation_id'])
        with self.assertRaises(app.AppError):repos.status('../bad')
    def test_credentials_private_fine_grained_and_expiring(self):
        token=self.base/'token';token.write_text('github_pat_'+'synthetic_'*5);token.chmod(0o600)
        expires=(dt.datetime.now(dt.timezone.utc)+dt.timedelta(hours=2)).isoformat()
        api=repos.GitHub(token,expires)
        self.assertNotIn('synthetic',repr(api))
        for mode in [0o644,0o400]:
            token.chmod(mode)
            with self.assertRaises(app.AppError):repos.GitHub(token,expires)
        token.chmod(0o600)
        for when in ['yesterday','2020-01-01T00:00:00Z',(dt.datetime.now(dt.timezone.utc)+dt.timedelta(days=3)).isoformat()]:
            with self.assertRaises(app.AppError):repos.GitHub(token,when)
        token.write_text('ghp_'+'synthetic'*10)
        with self.assertRaises(app.AppError):repos.GitHub(token,expires)
        token.unlink();token.symlink_to('/dev/null')
        with self.assertRaises(app.AppError):repos.GitHub(token,expires)
    def test_git_auth_fd_and_no_token_environment_or_arguments(self):
        token=self.base/'token';value='github_pat_'+'synthetic_'*5;token.write_text(value);token.chmod(0o600)
        api=repos.GitHub(token,(dt.datetime.now(dt.timezone.utc)+dt.timedelta(hours=2)).isoformat())
        with api.git_environment() as (env,fds):
            self.assertNotIn(value,json.dumps(env));self.assertEqual(len(fds),1)
            out=subprocess.run([str(app.REPO/'scripts/repository_askpass.py'),"Password for 'https://github.com':"],
                               env={**os.environ,**env},pass_fds=fds,capture_output=True,check=True)
            self.assertEqual(out.stdout.strip().decode(),value)
        with self.assertRaises(OSError):os.fstat(fds[0])
    def test_wrong_actor_and_free_plan_fail_before_creation(self):
        self.api.actor_name='other'
        with self.assertRaises(app.AppError):self.apply()
        self.api.actor_name=repos.ACCOUNT;self.api.plan_name='free'
        with self.assertRaises(app.AppError):self.apply()
        self.assertIsNone(self.api.remote)
    def test_local_git_configuration_cannot_redirect_credentials(self):
        self.api.fail_before=('PUT',repos.prefix(self.plan)+'/branches/main/protection')
        with self.assertRaises(app.AppError):self.apply()
        root=repos.workspace(self.plan['operation_id'])/'source'
        with (root/'.git/config').open('a') as out:out.write('[url "https://example.invalid/"]\n insteadOf = https://github.com/\n')
        with self.assertRaises(app.AppError):self.resume()
        self.assertIsNone(self.api.ref(self.plan['branches']['head']))
    def test_symlink_git_metadata_refused(self):
        self.api.fail_before=('PUT',repos.prefix(self.plan)+'/branches/main/protection')
        with self.assertRaises(app.AppError):self.apply()
        root=repos.workspace(self.plan['operation_id'])/'source'
        config=root/'.git/config';config.rename(root/'.git/config-saved');config.symlink_to(root/'.git/config-saved')
        with self.assertRaises(app.AppError):self.resume()
    def test_askpass_refuses_other_hosts(self):
        out=subprocess.run([str(app.REPO/'scripts/repository_askpass.py'),"Password for 'https://example.invalid':"],capture_output=True)
        self.assertNotEqual(out.returncode,0);self.assertEqual(out.stdout,b'')
    def test_http_failures_do_not_echo_raw_token_or_response(self):
        import urllib.error
        token=self.base/'token';value='github_pat_'+'synthetic_'*5;token.write_text(value);token.chmod(0o600)
        api=repos.GitHub(token,(dt.datetime.now(dt.timezone.utc)+dt.timedelta(hours=2)).isoformat())
        error=urllib.error.HTTPError('https://api.github.com/user',403,value,{},io.BytesIO(value.encode()))
        with patch.object(api.opener,'open',side_effect=error):
            with self.assertRaises(app.AppError) as caught:api.request('GET','/user')
            self.assertNotIn(value,str(caught.exception))
        missing=urllib.error.HTTPError('https://api.github.com/user',404,'not found',{},None)
        with patch.object(api.opener,'open',side_effect=missing):self.assertIsNone(api.request('GET','/user',missing=True))
    def test_unsafe_secret_reference_names(self):
        for name in ['../TOKEN','GITHUB_TOKEN','lower-case','A/B']:
            with self.assertRaises(app.AppError):self.new_plan(secret_references=[{'scope':'repository','name':name}])
    def test_closed_pr_and_remote_branch_drift_stop(self):
        receipt=self.apply();self.api.prs[0]['state']='closed'
        with self.assertRaises(app.AppError):self.resume()
        self.api.prs[0]['state']='open'
        self.api.raw_git('update-ref','refs/heads/'+self.plan['branches']['head'],receipt['bootstrap_sha'])
        with self.assertRaises(app.AppError):self.resume()
    def test_foreign_local_destination_after_remote_failure_preserved(self):
        self.api.fail_before=('PUT',repos.prefix(self.plan)+'/branches/main/protection')
        with self.assertRaises(app.AppError):self.apply()
        target=self.projects/'sample';target.mkdir();(target/'user').write_text('keep')
        with self.assertRaises(app.AppError):self.resume()
        self.assertEqual((target/'user').read_text(),'keep')
    def test_local_failure_retains_source_and_never_overwrites(self):
        original=repos.git
        def failure(root,*args,**kwargs):
            if args[:2]==('checkout','-b'):raise app.AppError('repository-recovery')
            return original(root,*args,**kwargs)
        with patch.object(repos,'git',failure):
            with self.assertRaises(app.AppError):self.apply()
        receipt=self.receipt();self.assertEqual(receipt['intent'],'generate-starter')
        self.assertTrue((repos.workspace(self.plan['operation_id'])/'generated').exists())
        with self.assertRaises(app.AppError):self.resume()
        self.assertIsNone(self.api.ref(self.plan['branches']['head']))

    def test_duplicate_json_keys_are_rejected(self):
        path=self.base/'plan.json';path.write_text('{"schema_version":1,"schema_version":1}')
        with self.assertRaises(app.AppError):repos.read_plan(path)
    def test_nested_existing_repository_destination_rejected(self):
        parent=self.projects/'existing';parent.mkdir();(parent/'.git').mkdir()
        with self.assertRaises(app.AppError):repos.plan('sample',str(parent/'sample'),self.api)

    def test_cli_and_provider_bundle(self):
        output=io.StringIO()
        with contextlib.redirect_stdout(output):self.assertEqual(cli.main(['--version']),0)
        self.assertIn('repo',json.loads(output.getvalue())['capabilities'])
        app.ensure_store();bundle=app.provider_bundle()
        self.assertTrue((bundle/'scripts/project_repositories.py').is_file())
        self.assertTrue(os.access(bundle/'scripts/repository_askpass.py',os.X_OK))
        output=subprocess.run([sys.executable,str(bundle/'scripts/gptclawctl.py'),'repo','status','--operation-id','0'*32],capture_output=True,text=True)
        self.assertNotEqual(output.returncode,0)
        self.assertIn('repository-recovery',output.stdout)


if __name__=='__main__':unittest.main()
