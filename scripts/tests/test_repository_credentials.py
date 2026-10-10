#!/usr/bin/env python3
"""Synthetic App authority/token transport; real isolated Git and RSA signing."""
import base64
import contextlib
import copy
import datetime as dt
import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import private_apps as app
import project_repositories as repos
import repository_credentials as broker
import repository_credential_helper as helper
import gptclawctl as cli
from test_project_repositories import FakeAPI


def row(repo_id,name):
    return {'id':repo_id,'full_name':repos.ACCOUNT+'/'+name,'private':True,'owner':{'login':repos.ACCOUNT,'type':'User'}}


class Factory:
    def __init__(self, base):
        self.base=base;self.repos={};self.selected={100:row(100,'bootstrap')};self.next_id=101
        self.tokens={};self.calls=[];self.root_calls=[];self.selection='selected';self.account=repos.ACCOUNT
        self.grants=copy.deepcopy(broker.GRANTS);self.mutate=None;self.auto_include=True;self.suspended=False
        self.token_count=0
    def request(self,method,path,body=None,missing=False):
        self.root_calls.append((method,path,copy.deepcopy(body)))
        if path=='/app':return {'id':17,'owner':{'login':self.account},'permissions':self.grants}
        if path=='/app/installations/19':return {'id':19,'app_id':17,'account':{'login':self.account,'type':'User'},
            'suspended_at':'now' if self.suspended else None,'repository_selection':self.selection,'permissions':self.grants}
        if path.endswith('/installation') and path.startswith('/repos/'):
            name=path.split('/')[3]
            if not any(v['full_name']==repos.ACCOUNT+'/'+name for v in self.selected.values()):return None
            return {'id':19,'app_id':17}
        if path.endswith('/access_tokens'):
            ids=body.get('repository_ids')
            if ids is not None and any(i not in self.selected for i in ids):raise app.AppError('credential-scope')
            self.token_count+=1;secret='synthetic_'+str(self.token_count)+'.format-variable-token'
            expires=(dt.datetime.now(dt.timezone.utc)+dt.timedelta(minutes=59)).isoformat()
            data={'token':secret,'expires_at':expires,'permissions':body['permissions'],'repository_selection':self.selection,
                  'repositories':[self.selected[i] for i in (ids if ids is not None else self.selected)]}
            if self.mutate:self.mutate(data)
            self.tokens[secret]={'data':copy.deepcopy(data),'ids':ids,'revoked':False}
            return copy.deepcopy(data)
        raise AssertionError((method,path))
    def access(self,token,method,path,body=None,missing=False):
        if token._token not in self.tokens:raise app.AppError('credential-auth')
        info=self.tokens[token._token]
        if info['revoked']:raise app.AppError('credential-auth')
        self.calls.append((method,path,copy.deepcopy(body),info['ids']))
        if path=='/installation/token' and method=='DELETE':info['revoked']=True;return {}
        if path.startswith('/installation/repositories'):
            return {'repositories':[self.selected[i] for i in (info['ids'] if info['ids'] is not None else self.selected)]}
        if path=='/user/repos':
            if 'repository_creation' not in info['data']['permissions']:raise app.AppError('credential-scope')
            name=body['name'];repo_id=self.next_id;self.next_id+=1
            bare=self.base/(name+'.git');subprocess.run(['git','init','--bare',str(bare)],check=True,capture_output=True)
            api=FakeAPI(bare);remote=api.request(method,path,body)
            remote['id']=repo_id;remote['permissions']={'admin':False,'push':True}
            api.remote=copy.deepcopy(remote)
            self.repos[name]=api
            if self.auto_include:self.selected[repo_id]=row(repo_id,name)
            return copy.deepcopy(remote)
        name=path.split('/')[3];api=self.repos.get(name)
        if api is None:return None
        repo_id=api.remote['id']
        if info['ids'] is not None and repo_id not in info['ids']:raise app.AppError('credential-scope')
        if path.endswith('/pulls') and method=='POST' and 'pull_requests' not in info['data']['permissions']:
            raise app.AppError('credential-scope')
        result=api.request(method,path,body,missing)
        # FakeAPI's PR IDs are fixed to 42; expose actual bound repo identity.
        if '/pulls' in path:
            for pr in (result if isinstance(result,list) else [result]):
                pr['head']['repo']['id']=repo_id;pr['base']['repo']['id']=repo_id
        return result


class Tests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);self.base=Path(temp.name)
        self.projects=self.base/'projects';self.projects.mkdir();self.key=self.base/'app.pem'
        subprocess.run(['/usr/bin/openssl','genpkey','-algorithm','RSA','-pkeyopt','rsa_keygen_bits:2048','-out',str(self.key)],
                       check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        self.key.chmod(0o600)
        for key,value in [('PROJECTS',self.projects),('STORE',self.projects/'.gptclaw-runtime/v1')]:
            p=patch.object(app,key,value);p.start();self.addCleanup(p.stop)
        self.factory=Factory(self.base)
        p=patch.object(broker,'root_transport',lambda value:self.factory);p.start();self.addCleanup(p.stop)
        self.production_access_request=broker.Access.request
        p=patch.object(broker.Access,'request',lambda token,*a,**k:self.factory.access(token,*a,**k));p.start();self.addCleanup(p.stop)
        self.real_git=repos.git
        p=patch.object(repos,'git',self.git);p.start();self.addCleanup(p.stop)
    def git(self,root,*args,api=None,input_bytes=None):
        if args[0]=='push':
            name=args[1].rsplit('/',1)[1].removesuffix('.git');bare=self.factory.repos[name].bare
            result=subprocess.run(['git','-c','core.hooksPath=/dev/null','-C',str(root),'push',str(bare),args[2]],capture_output=True)
            broker.check(result.returncode==0,'credential-recovery');return result.stdout
        return self.real_git(root,*args,input_bytes=input_bytes)
    def configure(self):return broker.configure(17,19,str(self.key),[100])
    def first(self):
        self.configure();result=broker.create('first',str(self.projects/'first'),canary=True);broker.set_active(True);return result
    def test_setup_is_private_and_ready_only_after_canary(self):
        result=self.configure();self.assertEqual(result['state'],'canary-required')
        with self.assertRaises(app.AppError):broker.set_active(True)
        p=broker.profile();self.assertFalse(p['active']);self.assertFalse(p['creation_verified'])
        self.assertEqual(stat.S_IMODE((broker.location()/'profile.json').stat().st_mode),0o600)
        self.assertTrue(all(v['revoked'] for v in self.factory.tokens.values()))
    def test_two_project_creation_after_one_setup(self):
        first=self.first();second=broker.create('second',str(self.projects/'second'))
        self.assertEqual(first['state'],'repository-ready');self.assertEqual(second['state'],'repository-ready')
        self.assertNotEqual(first['repository_id'],second['repository_id'])
        self.assertTrue(first['protection_waiver']);self.assertFalse(first['remote_readback']['protection']['verified'])
        self.assertEqual(len(self.factory.repos['first'].prs),1);self.assertEqual(len(self.factory.repos['second'].prs),1)
        self.assertFalse(any('/protection' in path for _,path,_,_ in self.factory.calls))
        for name in ['first','second']:
            root=self.projects/name;binding=broker.validate_git_helper(root)
            self.assertTrue(binding['helper_command']);repos.check_git_storage(root)
            self.assertEqual(app.validate_project(root)[2],0)
        self.assertEqual(set(broker.Broker().doctor()['selected_repository_ids']),{100,101,102})
    def test_project_lease_has_exact_scope_and_no_creation_or_admin(self):
        self.first();root=self.projects/'first'
        a=broker.Broker().project_token(root,'git');b=broker.Broker().project_token(root,'pr')
        self.assertEqual(a.metadata['repository_id'],101)
        self.assertEqual(a.metadata['permissions'],{'contents':'write','metadata':'read'})
        self.assertNotIn('repository_creation',b.metadata['permissions']);self.assertNotIn('administration',b.metadata['permissions'])
        a.close();b.close()
    def test_cross_repository_token_access_denied(self):
        self.first();broker.create('second',str(self.projects/'second'))
        token=broker.Broker().project_token(self.projects/'first','git')
        with self.assertRaises(app.AppError):token.request('GET','/repos/'+repos.ACCOUNT+'/second')
        token.close()
    def test_tokens_are_fresh_and_revocation_does_not_need_owner(self):
        self.first();root=self.projects/'first';b=broker.Broker()
        a=b.project_token(root,'git');a.close()
        with self.assertRaises(app.AppError):a.request('GET','/repos/'+repos.ACCOUNT+'/first')
        fresh=b.project_token(root,'git');self.assertNotEqual(a._token,fresh._token);fresh.close()
        self.assertTrue(all(v['revoked'] for v in self.factory.tokens.values()))
    def test_omitted_or_extra_scope_rejected_and_token_revoked(self):
        self.configure()
        variants=[lambda d:d.update(permissions={**d['permissions'],'administration':'write'}),
                  lambda d:d.update(repository_selection='all'),lambda d:d.update(repositories=[]),
                  lambda d:d['repositories'][0].update(id=999)]
        for mutate in variants:
            self.factory.mutate=mutate
            with self.assertRaises(app.AppError):broker.Broker().issue('git',100,'bootstrap')
            self.assertTrue(list(self.factory.tokens.values())[-1]['revoked'])
    def test_expired_short_long_or_missing_expiry_denied(self):
        self.configure()
        for offset in [dt.timedelta(minutes=-1),dt.timedelta(minutes=2),dt.timedelta(hours=2)]:
            self.factory.mutate=lambda d:d.update(expires_at=(dt.datetime.now(dt.timezone.utc)+offset).isoformat())
            with self.assertRaises(app.AppError):broker.Broker().issue('git',100,'bootstrap')
        self.factory.mutate=lambda d:d.update(expires_at='missing')
        with self.assertRaises(app.AppError):broker.Broker().issue('git',100,'bootstrap')
    def test_all_repo_wrong_account_grants_or_suspension_rejected(self):
        for field,value in [('selection','all'),('account','other'),('grants',{**broker.GRANTS,'administration':'write'}),('suspended',True)]:
            old=getattr(self.factory,field);setattr(self.factory,field,value)
            with self.assertRaises(app.AppError):self.configure()
            self.assertIsNone(broker.configured());setattr(self.factory,field,old)
    def test_unapproved_selection_is_not_hidden_by_single_repo_token(self):
        self.factory.selected[999]=row(999,'unrelated')
        with self.assertRaises(app.AppError):self.configure()
    def test_missing_auto_inclusion_stops_after_one_create(self):
        self.configure();self.factory.auto_include=False
        with self.assertRaises(app.AppError):broker.create('first',str(self.projects/'first'),canary=True)
        receipt=list((app.STORE/'repositories').glob('*/receipt.json'))[0]
        data=repos.read_metadata(receipt);self.assertEqual(data['repository_id'],101)
        self.assertEqual(data['state'],'recovery-required')
        self.assertFalse(broker.profile()['creation_verified'])
        self.assertEqual(sum(path=='/user/repos' for _,path,_,_ in self.factory.calls),1)
        self.assertFalse((self.projects/'first').exists())
    def test_scoped_resume_retains_operation_and_one_pr(self):
        self.first();binding=broker.bound(self.projects/'first')
        result=broker.resume(binding['operation_id'])
        self.assertEqual(result['repository_id'],101);self.assertEqual(len(self.factory.repos['first'].prs),1)
    def test_disable_blocks_future_credentials_without_deleting_source(self):
        self.first();root=self.projects/'first';original=(root/'README.md').read_bytes()
        broker.disable(root)
        with self.assertRaises(app.AppError):broker.Broker().project_token(root,'git')
        self.assertEqual(original,(root/'README.md').read_bytes());self.assertIn('first',self.factory.repos)
    def test_deactivate_restores_local_only_and_keeps_bindings(self):
        self.first();broker.set_active(False)
        self.assertFalse(broker.profile()['active']);self.assertTrue(broker.bindings())
        with self.assertRaises(app.AppError):broker.Broker().project_token(self.projects/'first','git')
    def test_rotation_keeps_old_key_and_source(self):
        self.first();other=self.base/'replacement.pem'
        subprocess.run(['/usr/bin/openssl','genpkey','-algorithm','RSA','-pkeyopt','rsa_keygen_bits:2048','-out',str(other)],
                       check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        other.chmod(0o600);self.assertFalse(other.read_bytes()==self.key.read_bytes())
        before=(self.projects/'first'/'README.md').read_bytes()
        result=broker.rotate(other);self.assertTrue(result['previous_key_retained'])
        self.assertEqual(broker.profile()['key_file'],str(other));self.assertTrue(self.key.exists())
        self.assertEqual(before,(self.projects/'first'/'README.md').read_bytes())
    def test_private_key_ownership_modes_symlinks_hardlinks_and_type(self):
        for mode in [0o644,0o400]:
            self.key.chmod(mode)
            with self.assertRaises(app.AppError):broker.key_bytes(self.key)
        self.key.chmod(0o600);link=self.base/'linked';link.symlink_to(self.key)
        with self.assertRaises(app.AppError):broker.key_bytes(link)
        link.unlink();os.link(self.key,link)
        with self.assertRaises(app.AppError):broker.key_bytes(self.key)
        link.unlink();self.key.write_text('not a key')
        with self.assertRaises(app.AppError):broker.key_bytes(self.key)
    def test_real_jwt_signature_and_claims_without_key_output(self):
        value={'key_file':str(self.key),'app_id':17};signed=broker.jwt(value)
        header,payload,signature=signed.split('.')
        claims=json.loads(base64.urlsafe_b64decode(payload+'='*((-len(payload))%4)))
        self.assertEqual(claims['iss'],'17');self.assertLessEqual(claims['exp']-int(__import__('time').time()),540)
        public=self.base/'public.pem';sig=self.base/'signature'
        subprocess.run(['/usr/bin/openssl','pkey','-in',str(self.key),'-pubout','-out',str(public)],check=True,capture_output=True)
        sig.write_bytes(base64.urlsafe_b64decode(signature+'='*((-len(signature))%4)))
        result=subprocess.run(['/usr/bin/openssl','dgst','-sha256','-verify',str(public),'-signature',str(sig)],
                              input=(header+'.'+payload).encode(),capture_output=True)
        self.assertEqual(result.returncode,0)
    def test_unsafe_binding_and_git_url_rewrite_preserved_rejected(self):
        self.first();root=self.projects/'first'
        with (root/'.git/config').open('a') as out:out.write('[url "https://example.invalid/"]\n insteadOf = https://github.com/\n')
        with self.assertRaises(app.AppError):broker.validate_git_helper(root)
        self.assertIn('example.invalid',(root/'.git/config').read_text())
    def test_foreign_helper_or_remote_rejected(self):
        self.first();root=self.projects/'first';config=root/'.git/config';old=config.read_text()
        for modified in [old.replace('useHttpPath = true','useHttpPath = false'),old.replace('/first.git','/second.git'),old.replace('helper =\n','helper = evil\n')]:
            config.write_text(modified)
            with self.assertRaises(app.AppError):broker.validate_git_helper(root)
        config.write_text(old)
    def test_helper_mints_only_requested_project_and_has_no_cache(self):
        self.first();root=self.projects/'first';out=io.StringIO();err=io.StringIO()
        class Input:
            buffer=io.BytesIO(('protocol=https\nhost=github.com\npath='+repos.ACCOUNT+'/first.git\n\n').encode())
        real_fstat=os.fstat
        with patch.object(helper.sys,'stdin',Input()),patch.object(helper.sys,'stdout',out),patch.object(helper.sys,'stderr',err),\
             patch.object(helper.os,'fstat',side_effect=lambda fd:type('S',(),{'st_mode':stat.S_IFIFO})() if fd in [0,1] else real_fstat(fd)):
            # fstat patch also affects key I/O; mint is a known reviewed synthetic lease here.
            token=broker.Access('synthetic_helper_token',(dt.datetime.now(dt.timezone.utc)+dt.timedelta(minutes=59)).isoformat(),
                {'repository_id':101,'permissions':broker.ROLES['git'],'expires_at':'fixture'})
            self.factory.tokens[token._token]={'data':{'permissions':broker.ROLES['git']},'ids':[101],'revoked':False}
            with patch.object(broker.Broker,'project_token',return_value=token):
                code=helper.main(['--project-root',str(root),'get'])
        self.assertEqual(code,0);self.assertIn('username=x-access-token',out.getvalue());self.assertEqual(err.getvalue(),'')
        for path in broker.location().rglob('*.json'):self.assertNotIn('synthetic_helper_token',path.read_text())
    def test_helper_ignores_store_erase_and_rejects_terminal(self):
        self.assertEqual(helper.main(['--project-root',str(self.projects/'missing'),'store']),0)
        self.assertEqual(helper.main(['--project-root',str(self.projects/'missing'),'erase']),0)
        with patch.object(helper.os,'fstat',return_value=type('S',(),{'st_mode':stat.S_IFCHR})()),contextlib.redirect_stderr(io.StringIO()):
            self.assertNotEqual(helper.main(['--project-root',str(self.projects/'missing'),'get']),0)
    def test_metadata_and_bundle_never_include_secret_material(self):
        self.first();bundle=app.provider_bundle()
        self.assertTrue((bundle/'scripts/repository_credentials.py').exists())
        self.assertTrue(os.access(bundle/'scripts/repository-credential-helper',os.X_OK))
        for path in broker.location().rglob('*.json'):
            text=path.read_text();self.assertNotIn('synthetic_',text);self.assertFalse(self.key.read_text() in text,'Private key material reached metadata')
        self.assertFalse(list(bundle.rglob('*.pem')))
    def test_later_requested_pr_scoped_and_idempotent(self):
        self.first();root=self.projects/'first';api=self.factory.repos['first']
        head='codex/later'
        repos.git(root,'checkout','-b',head)
        with (root/'README.md').open('a') as out:out.write('\nReviewed fixture change.\n')
        repos.git(root,'add','--','README.md');repos.git(root,'commit','-m','Review fixture change')
        repos.git(root,'push','https://github.com/'+repos.ACCOUNT+'/first.git','HEAD:refs/heads/'+head,api=None)
        result=broker.open_pr(root,head,'Later change','Review this change')
        self.assertEqual(result['state'],'pull-request-open')
        broker.open_pr(root,head,'Later change','Review this change');self.assertEqual(len(api.prs),2)
        self.assertNotIn('repository_creation',result['credential']['permissions'])
    def test_normal_new_after_activation_uses_combined_path(self):
        self.first();result=broker.new_project('second')
        self.assertEqual(result['state'],'repository-ready');self.assertEqual(result['repository_id'],102)
        before=len(self.factory.repos);local=broker.new_project('local',local_only=True)
        self.assertEqual(local['state'],'created');self.assertEqual(len(self.factory.repos),before)
        with self.assertRaises(app.AppError):broker.new_project('third',template='nextjs')
    def test_interrupted_git_helper_enrollment_reconciles_without_overwrite(self):
        import project_dependencies as deps
        self.configure();original=deps.write_bytes
        with patch.object(deps,'write_bytes',side_effect=OSError('injected publication failure')):
            with self.assertRaises(OSError):broker.create('first',str(self.projects/'first'),canary=True)
        value=broker.bound(self.projects/'first');self.assertIsNotNone(value['helper_command'])
        broker.resume(value['operation_id']);self.assertTrue(broker.profile()['creation_verified'])
        broker.validate_git_helper(self.projects/'first');self.assertEqual(len(self.factory.repos['first'].prs),1)
    def test_project_disable_obeys_credential_lock(self):
        self.first()
        with app.locked('credential-101'):
            with self.assertRaises(app.AppError) as caught:broker.disable(self.projects/'first')
            self.assertEqual(caught.exception.code,'busy')
        self.assertTrue(broker.bound(self.projects/'first')['enabled'])
    def test_issuance_after_deactivation_and_key_switch_uses_current_profile(self):
        self.first();old=broker.Broker();broker.set_active(False)
        with self.assertRaises(app.AppError):old.project_token(self.projects/'first','git')
    def test_creation_credentials_cannot_enter_git_channel(self):
        self.configure();token=broker.Broker().issue('create')
        with self.assertRaises(app.AppError):
            with token.git_environment():pass
        token.close()
    def test_request_scope_is_enforced_before_http_transport(self):
        self.first();token=broker.Broker().project_token(self.projects/'first','git')
        # Invoke the production transport method under a fake opener; cross-target
        # rejection must happen before any HTTP request is attempted.
        from unittest.mock import Mock
        token.opener=Mock()
        # Check the production method separately because setUp supplies a private transport.
        method=self.production_access_request
        with self.assertRaises(app.AppError):method(token,'GET','/repos/'+repos.ACCOUNT+'/second')
        token.opener.open.assert_not_called();token.close()
    def test_expiring_provision_token_is_renewed_without_write_replay(self):
        self.first();binding=broker.bound(self.projects/'first');receipt=repos.read_receipt(binding['operation_id'])
        adapter=broker.Provision(broker.Broker(),receipt['plan'],receipt)
        first=adapter.scoped();secret=first._token
        first.expires_at=(dt.datetime.now(dt.timezone.utc)+dt.timedelta(minutes=1)).isoformat()
        second=adapter.scoped();self.assertNotEqual(secret,second._token)
        self.assertTrue(self.factory.tokens[secret]['revoked']);adapter.close()
    def native_helper_fixture(self,root):
        fixture=self.base/'credential-fixture.py'
        code="""import sys,datetime as dt
from pathlib import Path
sys.path.insert(0, SCRIPTS)
import private_apps as app
app.PROJECTS=Path(PROJECTS);app.STORE=Path(STORE)
import repository_credentials as broker
import repository_credential_helper as helper
class FixtureBroker:
 def project_token(self,root,role):
  return broker.Access('synthetic-native-git-wire', (dt.datetime.now(dt.timezone.utc)+dt.timedelta(minutes=59)).isoformat(), {'repository_id':101,'role':'git','permissions':broker.ROLES['git'],'expires_at':(dt.datetime.now(dt.timezone.utc)+dt.timedelta(minutes=59)).isoformat()})
broker.Broker=FixtureBroker
raise SystemExit(helper.main(sys.argv[1:]))
"""
        prefix='SCRIPTS='+repr(str(app.REPO/'scripts'))+'\nPROJECTS='+repr(str(self.projects))+'\nSTORE='+repr(str(app.STORE))+'\n'
        fixture.write_text(prefix+code)
        return sys.executable+' '+str(fixture)+' --project-root '+str(root)

    def test_native_git_credential_protocol_calls_owned_helper(self):
        self.first();root=self.projects/'first'
        command=self.native_helper_fixture(root)
        env={'PATH':'/usr/bin:/bin','GIT_CONFIG_NOSYSTEM':'1','GIT_CONFIG_GLOBAL':'/dev/null','GIT_TERMINAL_PROMPT':'0'}
        result=subprocess.run(['git','-C',str(root),'-c','credential.helper=','-c','credential.helper='+command,'credential','fill'],
            input=('url=https://github.com/'+repos.ACCOUNT+'/first.git\n\n').encode(),capture_output=True,env=env)
        self.assertEqual(result.returncode,0)
        self.assertTrue(b'password=synthetic-native-git-wire' in result.stdout)
        self.assertFalse(b'synthetic-native-git-wire' in result.stderr)
        for path in broker.location().rglob('*.json'):self.assertFalse('synthetic-native-git-wire' in path.read_text())
        # A changed target produces no credential bytes or network fallback.
        denied=subprocess.run(['git','-C',str(root),'-c','credential.helper=','-c','credential.helper='+command,'credential','fill'],
            input=('url=https://github.com/'+repos.ACCOUNT+'/second.git\n\n').encode(),capture_output=True,env=env)
        self.assertNotEqual(denied.returncode,0);self.assertEqual(denied.stdout,b'')

    def test_normal_git_fetch_and_push_with_authentication_over_private_fixture(self):
        import http.server,ssl,threading,urllib.parse
        self.first();root=self.projects/'first';command=self.native_helper_fixture(root)
        certificate=self.base/'tls-cert.pem'
        subprocess.run(['/usr/bin/openssl','req','-new','-x509','-key',str(self.key),'-out',str(certificate),
                        '-days','1','-subj','/CN=github.com','-addext','subjectAltName=DNS:github.com'],
                        check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        tls=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);tls.load_cert_chain(certificate,self.key)
        authenticated=[];fixture_base=self.base
        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def finish(self):
                try:super().finish()
                finally:self.connection.close()
            def do_CONNECT(self):
                if self.path!='github.com:443':self.send_error(403);return
                self.send_response(200);self.end_headers();self.wfile.flush()
                self.connection=tls.wrap_socket(self.connection,server_side=True)
                self.rfile=self.connection.makefile('rb');self.wfile=self.connection.makefile('wb')
                self.close_connection=True;self.handle_one_request();self.close_connection=True
            def serve_git(self):
                auth=self.headers.get('Authorization','')
                expected='Basic '+base64.b64encode(b'x-access-token:synthetic-native-git-wire').decode()
                if auth!=expected:
                    self.send_response(401);self.send_header('WWW-Authenticate','Basic realm="fixture"')
                    self.send_header('Content-Length','0');self.send_header('Connection','close');self.end_headers()
                    self.close_connection=True;return
                parsed=urllib.parse.urlsplit(self.path)
                if not parsed.path.startswith('/'+repos.ACCOUNT+'/first.git/'):
                    self.send_error(403);self.close_connection=True;return
                authenticated.append((self.command,parsed.path))
                length=int(self.headers.get('Content-Length','0'))
                if length>2*1024*1024:self.send_error(413);return
                data=self.rfile.read(length)
                env={'PATH':'/usr/bin:/bin','GIT_CONFIG_NOSYSTEM':'1','GIT_CONFIG_GLOBAL':'/dev/null',
                     'GIT_PROJECT_ROOT':str(fixture_base),'GIT_HTTP_EXPORT_ALL':'1',
                     'PATH_INFO':parsed.path.removeprefix('/'+repos.ACCOUNT),
                     'QUERY_STRING':parsed.query,'REQUEST_METHOD':self.command,
                     'CONTENT_TYPE':self.headers.get('Content-Type',''),'CONTENT_LENGTH':str(length),
                     'REMOTE_USER':'fixture','AUTH_TYPE':'Basic',
                     'GIT_PROTOCOL':self.headers.get('Git-Protocol','')}
                result=subprocess.run(['git','-c','core.hooksPath=/dev/null','http-backend'],input=data,
                                      env=env,capture_output=True,timeout=20)
                headers,body=result.stdout.split(b'\r\n\r\n',1)
                status_code=200;extra=[]
                for line in headers.decode().splitlines():
                    key,value=line.split(':',1)
                    if key.lower()=='status':status_code=int(value.strip().split()[0])
                    elif key.lower() not in {'content-length','connection'}:extra.append((key,value.strip()))
                self.send_response(status_code)
                for key,value in extra:self.send_header(key,value)
                self.send_header('Content-Length',str(len(body)));self.send_header('Connection','close');self.end_headers()
                self.wfile.write(body);self.wfile.flush();self.close_connection=True
            def do_GET(self):self.serve_git()
            def do_POST(self):self.serve_git()
        server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
        worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
        def cleanup():server.shutdown();server.server_close();worker.join(timeout=5)
        self.addCleanup(cleanup)
        env={'PATH':'/usr/bin:/bin','GIT_CONFIG_NOSYSTEM':'1','GIT_CONFIG_GLOBAL':'/dev/null','GIT_TERMINAL_PROMPT':'0'}
        args=['git','-C',str(root),'-c','credential.helper=','-c','credential.helper='+command,
              '-c','http.proxy=http://127.0.0.1:'+str(server.server_port),'-c','http.sslCAInfo='+str(certificate)]
        fetched=subprocess.run([*args,'fetch','origin'],capture_output=True,env=env,timeout=30)
        self.assertEqual(fetched.returncode,0)
        repos.git(root,'checkout','-b','codex/authenticated-wire')
        with (root/'README.md').open('a') as out:out.write('\nPrivate authenticated transport fixture.\n')
        repos.git(root,'add','--','README.md');repos.git(root,'commit','-m','Verify private transport')
        pushed=subprocess.run([*args,'push','origin','HEAD:refs/heads/codex/authenticated-wire'],
                              capture_output=True,env=env,timeout=30)
        self.assertEqual(pushed.returncode,0)
        self.assertEqual(self.factory.repos['first'].ref('codex/authenticated-wire'),repos.git(root,'rev-parse','HEAD').decode().strip())
        self.assertTrue(any(method=='POST' and path.endswith('git-receive-pack') for method,path in authenticated))
        self.assertFalse(b'synthetic-native-git-wire' in fetched.stderr+pushed.stderr)

    def test_preview_reports_effective_standing_policy_without_publication(self):
        self.first();before=len(self.factory.repos)
        result=broker.preview('second')
        self.assertEqual(result['policy'],{'id':'unprotected-private-dev','protection_enforced':False})
        self.assertNotIn('administration',result['credential_provider']['provision'])
        self.assertEqual(len(self.factory.repos),before);self.assertFalse((self.projects/'second').exists())
        local=broker.preview('local',local_only=True);self.assertFalse(local['github'])
        self.assertFalse((self.projects/'local').exists())

    def test_disabled_unselected_repo_does_not_block_other_projects(self):
        self.first();broker.create('second',str(self.projects/'second'))
        broker.disable(self.projects/'first');self.factory.selected.pop(101)
        broker.Broker().doctor()
        token=broker.Broker().project_token(self.projects/'second','git');token.close()
        with self.assertRaises(app.AppError):broker.enable(self.projects/'first')
        self.factory.selected[101]=row(101,'first');broker.enable(self.projects/'first')
        self.assertTrue(broker.bound(self.projects/'first')['enabled'])

    def test_key_path_is_canonical_and_helper_config_symlinks_stop_before_mint(self):
        with self.assertRaises(app.AppError):broker.key_bytes('//'+str(self.key).lstrip('/'))
        self.first();root=self.projects/'first';config=root/'.git/config'
        saved=root/'.git/config-saved';config.rename(saved);config.symlink_to(saved)
        before=self.factory.token_count
        with self.assertRaises(app.AppError):broker.validate_git_helper(root)
        self.assertEqual(before,self.factory.token_count)
    def test_ambiguous_creation_operation_is_visible_without_token_values(self):
        self.configure();original=self.factory.access
        def lost(token,method,path,body=None,missing=False):
            result=original(token,method,path,body,missing)
            if method=='POST' and path=='/user/repos':raise app.AppError('repository-api')
            return result
        with patch.object(self.factory,'access',side_effect=lost):
            with self.assertRaises(app.AppError):broker.create('first',str(self.projects/'first'),canary=True)
        summaries=broker.operations();self.assertEqual(len(summaries),1)
        self.assertEqual(summaries[0]['intent'],'create-repository');self.assertIsNone(summaries[0]['repository_id'])
        with self.assertRaises(app.AppError):broker.resume(summaries[0]['operation_id'])
        self.assertEqual(len(self.factory.repos),1)
        completed=broker.resume(summaries[0]['operation_id'],repo_id=101)
        self.assertEqual(completed['repository_id'],101);self.assertEqual(len(self.factory.repos['first'].prs),1)

    def test_manual_pat_operation_is_not_implicitly_adopted(self):
        self.first();binding=broker.bound(self.projects/'first')
        receipt=repos.read_receipt(binding['operation_id']);receipt.pop('credential_provider');repos.persist(receipt)
        before=len(self.factory.root_calls)
        with self.assertRaises(app.AppError):broker.resume(binding['operation_id'])
        self.assertEqual(before,len(self.factory.root_calls))

    def test_failed_revoke_cleanup_does_not_mask_scope_rejection(self):
        self.configure();self.factory.mutate=lambda d:d.update(permissions={**d['permissions'],'administration':'write'})
        original=self.factory.access
        def cleanup_failure(token,method,path,body=None,missing=False):
            if method=='DELETE':raise ValueError('fixture cleanup failure')
            return original(token,method,path,body,missing)
        with patch.object(self.factory,'access',side_effect=cleanup_failure):
            with self.assertRaises(app.AppError) as caught:broker.Broker().issue('git',100,'bootstrap')
            self.assertEqual(caught.exception.code,'credential-scope')

    def test_profile_unknown_keys_and_boolean_ids_rejected(self):
        self.configure();value=broker.profile()
        for change in [{'app_id':True},{'account':'other'},{'active':'yes'},{'extra':'unsafe'}]:
            with self.assertRaises(app.AppError):broker.profile({**value,**change})
    def test_cli_unconfigured_and_local_only(self):
        output=io.StringIO()
        with contextlib.redirect_stdout(output):self.assertEqual(cli.main(['--version']),0)
        self.assertIn('credentials',json.loads(output.getvalue())['capabilities'])
        self.assertIsNone(broker.configured())
        with patch.object(broker,'configured',side_effect=AssertionError('local-only must not read profile')):
            # Creation function independently preserves the unchanged local path.
            root=Path(broker.new_project('local',local_only=True)['root']);self.assertEqual(app.validate_project(root)[2],0)
        self.assertFalse(self.factory.repos)


if __name__=='__main__':unittest.main()
