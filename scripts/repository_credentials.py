"""User-scoped App broker. Secrets stay in memory/private fds, never receipts."""
import base64
import contextlib
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import time
import urllib.parse
import urllib.request

import private_apps as app
import project_repositories as repos

GRANTS = {'repository_creation': 'write', 'contents': 'write', 'pull_requests': 'write', 'metadata': 'read'}
ROLES = {'audit': {'metadata': 'read'}, 'create': {'repository_creation': 'write', 'metadata': 'read'},
         'git': {'contents': 'write', 'metadata': 'read'},
         'provision': {'contents': 'write', 'pull_requests': 'write', 'metadata': 'read'},
         'pr': {'contents': 'read', 'pull_requests': 'write', 'metadata': 'read'}}
app.MESSAGES.update({
    'credential-policy': 'Credential profile, target or grant does not match the reviewed App policy.',
    'credential-key': 'Use a private owned regular RSA key outside repositories; no key values were displayed.',
    'credential-auth': 'The configured App/key/installation could not authenticate; reconcile its scope without broadening permissions.',
    'credential-scope': 'GitHub did not prove the exact requested repository and permissions; no fallback credential was used.',
    'credential-disabled': 'This profile or repository binding is disabled; activate only the reviewed target.',
    'credential-recovery': 'Credential enrollment or provisioning needs reconciliation with the same operation; resources were retained.',
})


def check(value, code='credential-policy'):
    app.need(value, code)


def location():
    return app.STORE/'credentials'


def private_directory(path):
    app.safe(path)
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    check(path.stat().st_uid == os.getuid() and stat.S_IMODE(path.stat().st_mode) == 0o700, 'path')


def load(path, optional=False):
    app.safe(path)
    if optional and not path.exists() and not path.is_symlink(): return None
    value = repos.read_metadata(path)
    check(stat.S_IMODE(path.stat().st_mode) == 0o600, 'path')
    return value


def profile(value=None):
    if value is None: value = load(location()/'profile.json')
    check(isinstance(value, dict) and set(value) == {'schema_version','account','app_id','installation_id',
          'key_file','bootstrap_repository_ids','policy','active','creation_verified'})
    check(type(value['schema_version']) is int and value['schema_version'] == 1 and value['account'] == repos.ACCOUNT)
    for field in ['app_id','installation_id']:
        check(type(value[field]) is int and value[field] > 0)
    ids = value['bootstrap_repository_ids']
    check(isinstance(ids,list) and 1 <= len(ids) <= 10 and all(type(i) is int and i > 0 for i in ids)
          and ids == sorted(set(ids)))
    check(value['policy'] == 'unprotected-private-dev' and type(value['active']) is bool
          and type(value['creation_verified']) is bool)
    check(isinstance(value['key_file'],str))
    return value


def operations():
    directory=app.STORE/'repositories';app.safe(directory)
    if not directory.exists():return []
    result=[]
    for path in sorted(directory.glob('*/receipt.json')):
        value=repos.read_metadata(path)
        provider=value.get('credential_provider',{})
        if provider.get('kind')!='github-app':continue
        result.append({k:value.get(k) for k in ['operation_id','state','repository_id','intent','last_error','retained_source']})
    check(len(result)<=500)
    return result


def configured():
    value = load(location()/'profile.json', optional=True)
    return profile(value) if value else None


def key_bytes(path):
    path = app.safe(Path(path).absolute())
    check(str(path)==str(path.resolve()) and not path.is_relative_to(app.PROJECTS) and not path.is_relative_to(app.REPO), 'credential-key')
    try:
        check(path.parent.stat().st_uid == os.getuid() and stat.S_IMODE(path.parent.stat().st_mode) == 0o700, 'credential-key')
        fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
        with os.fdopen(fd,'rb') as source:
            info=os.fstat(source.fileno())
            check(stat.S_ISREG(info.st_mode) and info.st_uid == os.getuid() and info.st_nlink == 1
                  and stat.S_IMODE(info.st_mode) == 0o600 and 128 <= info.st_size <= 16384, 'credential-key')
            value=source.read(16385)
        check(len(value)<=16384 and value.startswith(b'-----BEGIN ') and value.splitlines()[0] in [b'-----BEGIN '+kind+b'-----' for kind in [b'RSA PRIVATE KEY',b'PRIVATE KEY']],
              'credential-key')
        return value
    except OSError:
        raise app.AppError('credential-key') from None


def b64(value):
    return base64.urlsafe_b64encode(value).rstrip(b'=').decode()


def jwt(value):
    payload=key_bytes(value['key_file'])
    now=int(time.time())
    header=b64(json.dumps({'alg':'RS256','typ':'JWT'},separators=(',',':')).encode())
    claims=b64(json.dumps({'iat':now-60,'exp':now+540,'iss':str(value['app_id'])},separators=(',',':')).encode())
    message=(header+'.'+claims).encode()
    fd=os.memfd_create('gptclaw-app-key',os.MFD_CLOEXEC)
    try:
        os.write(fd,payload)
        result=subprocess.run(['/usr/bin/openssl','dgst','-sha256','-sign','/proc/self/fd/'+str(fd)],
            input=message,pass_fds=(fd,),stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,
            env={'PATH':'/usr/bin:/bin','OPENSSL_CONF':'/dev/null'},timeout=10)
        check(result.returncode==0 and 256 <= len(result.stdout) <= 1024,'credential-key')
        return message.decode()+'.'+b64(result.stdout)
    except (OSError,subprocess.TimeoutExpired):
        raise app.AppError('credential-key') from None
    finally: os.close(fd)


class Access(repos.GitHub):
    """App token/JWT transport, with format-independent bounded secret validation."""
    requires_admin=False
    def __init__(self, token, expires_at, metadata):
        check(isinstance(token,str) and 1 <= len(token) <= 16384 and re.fullmatch(r'[A-Za-z0-9._~+/-]+=*',token),'credential-auth')
        self._token=token;self.expires_at=expires_at;self.metadata=metadata
        self.opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),repos.NoRedirect())
    def request(self,method,path,body=None,missing=False):
        check(bool(self._token),'credential-auth')
        check(dt.datetime.fromisoformat(self.expires_at)>dt.datetime.now(dt.timezone.utc),'credential-auth')
        repository=self.metadata.get('repository')
        if repository:
            base='/repos/'+repository
            check(path==base or path.startswith(base+'/') or path.startswith(base+'?')
                  or (method=='DELETE' and path=='/installation/token'),'credential-scope')
        return super().request(method,path,body,missing)
    @contextlib.contextmanager
    def git_environment(self):
        check(self.metadata.get('role') in {'git','provision'},'credential-scope')
        with super().git_environment() as auth:yield auth
    def actor(self):
        return {'login':repos.ACCOUNT,'credential_kind':'github-app-installation',**self.metadata}
    def close(self):
        outcome='expires-within-issued-lifetime'
        try:
            self.request('DELETE','/installation/token');outcome='revoked'
        except (app.AppError,ValueError,TypeError): pass
        finally: self._token='';self.metadata['revocation']=outcome
        return outcome


def root_transport(value):
    return Access(jwt(value),(dt.datetime.now(dt.timezone.utc)+dt.timedelta(minutes=8)).isoformat(),{})


def check_repo(value, repo_id=None, name=None):
    check(isinstance(value,dict) and type(value.get('id')) is int and value['id']>0
          and value.get('owner',{}).get('login') == repos.ACCOUNT
          and value.get('owner',{}).get('type') == 'User' and value.get('private') is True,'credential-scope')
    full=value.get('full_name')
    check(isinstance(full,str) and full.startswith(repos.ACCOUNT+'/'),'credential-scope')
    suffix=full.split('/')[1]
    check(re.fullmatch(r'[a-z][a-z0-9]*(?:-[a-z0-9]+)*',suffix) and len(suffix)<=48,'credential-scope')
    if repo_id is not None:check(value['id']==repo_id,'credential-scope')
    if name is not None:check(suffix==name,'credential-scope')
    return value


def binding_path(root):
    root=app.safe(Path(root).absolute())
    return location()/'bindings'/(hashlib.sha256(str(root).encode()).hexdigest()+'.json')


def bindings():
    directory=location()/'bindings';app.safe(directory)
    if not directory.exists():return []
    result=[]
    for path in sorted(directory.glob('*.json')):
        value=load(path);validate_binding(value)
        check(path==binding_path(value['root']))
        result.append(value)
    check(len(result)<=500)
    return result


def validate_binding(value):
    check(isinstance(value,dict) and set(value)=={'schema_version','account','app_id','installation_id','repository_id',
          'name','root','operation_id','enabled','helper_command'})
    check(type(value['schema_version']) is int and value['schema_version']==1 and value['account']==repos.ACCOUNT)
    check(all(type(value[k]) is int and value[k]>0 for k in ['app_id','installation_id','repository_id']))
    check(type(value['enabled']) is bool and isinstance(value['name'],str)
          and re.fullmatch(r'[a-z][a-z0-9]*(?:-[a-z0-9]+)*',value['name']) and len(value['name'])<=48)
    check(isinstance(value['operation_id'],str) and re.fullmatch(r'[a-f0-9]{32}',value['operation_id']))
    check(value['root']==str(repos.target_path(value['root'])))
    check(value['helper_command'] is None or value['helper_command']==helper_command(value['root']))
    return value


def bound(root, require_enabled=True):
    root=app.safe(Path(root).absolute())
    value=validate_binding(load(binding_path(root)))
    check(value['root']==str(root))
    if require_enabled:check(value['enabled'],'credential-disabled')
    return value


def helper_command(root):
    # Stable content-addressed provider path is stored with the binding after enrollment.
    value=load(binding_path(root), optional=True)
    if value and value.get('helper_command') is not None:
        command=value['helper_command'];parts=command.split(' ')
        check(len(parts)==3 and parts[1]=='--project-root' and parts[2]==str(root))
        exe=app.safe(Path(parts[0]));check(exe.is_file() and os.access(exe,os.X_OK))
        check(exe.name=='repository-credential-helper' and exe.parent.name=='scripts')
        check(exe.is_relative_to(app.STORE/'providers'))
        return command
    return None


class Broker:
    def __init__(self, value=None):
        self.profile=profile(value)
    def api(self):return root_transport(self.profile)
    def identity(self):
        api=self.api();actual=api.request('GET','/app')
        check(actual.get('id')==self.profile['app_id'] and actual.get('owner',{}).get('login')==repos.ACCOUNT,'credential-auth')
        check(actual.get('permissions')==GRANTS,'credential-scope')
        install=api.request('GET','/app/installations/'+str(self.profile['installation_id']))
        check(install.get('id')==self.profile['installation_id'] and install.get('app_id')==self.profile['app_id']
              and install.get('account',{}).get('login')==repos.ACCOUNT
              and install.get('account',{}).get('type')=='User' and install.get('suspended_at') is None,'credential-auth')
        check(install.get('repository_selection')=='selected' and install.get('permissions')==GRANTS,'credential-scope')
        return {'app_id':self.profile['app_id'],'installation_id':self.profile['installation_id'],
                'account':repos.ACCOUNT,'permissions':GRANTS,'repository_selection':'selected'}
    def issue(self, role, repo_id=None, name=None):
        check(role in ROLES)
        check((role in {'audit','create'}) == (repo_id is None),'credential-scope')
        body={'permissions':ROLES[role]}
        if repo_id is not None:body['repository_ids']=[repo_id]
        data=self.api().request('POST','/app/installations/'+str(self.profile['installation_id'])+'/access_tokens',body)
        token=None
        try:
            check(isinstance(data,dict),'credential-scope')
            perms=data.get('permissions');check(perms==ROLES[role],'credential-scope')
            check(data.get('repository_selection')=='selected','credential-scope')
            expires=data.get('expires_at');parsed=dt.datetime.fromisoformat(expires.replace('Z','+00:00'))
            check(parsed.tzinfo is not None,'credential-scope')
            remaining=parsed-dt.datetime.now(dt.timezone.utc)
            check(dt.timedelta(minutes=5)<remaining<=dt.timedelta(minutes=65),'credential-scope')
            returned=data.get('repositories')
            if repo_id is not None:
                check(isinstance(returned,list) and len(returned)==1,'credential-scope')
                check_repo(returned[0],repo_id,name)
            token=Access(data.get('token'),parsed.isoformat(),{'expires_at':parsed.isoformat(),
                'repository_id':repo_id,'repository':None if repo_id is None else returned[0]['full_name'],'permissions':perms,'role':role})
            return token
        except (ValueError,TypeError,AttributeError):
            raise app.AppError('credential-scope') from None
        except app.AppError:
            # Best-effort revoke an over-granted token without returning it to caller.
            if isinstance(data.get('token'),str) and isinstance(data.get('expires_at'),str):
                with contextlib.suppress(app.AppError):Access(data['token'],data['expires_at'],{}).close()
            raise
    def doctor(self):
        identity=self.identity()
        with self.lease('audit') as token:
            observed=set()
            for page in range(1,11):
                result=token.request('GET','/installation/repositories?per_page=100&page='+str(page))
                items=result.get('repositories');check(isinstance(items,list) and len(items)<=100,'credential-scope')
                for item in items:observed.add(check_repo(item)['id'])
                if len(items)<100:break
            else:raise app.AppError('credential-scope')
        registered=bindings()
        approved=set(self.profile['bootstrap_repository_ids']) | {b['repository_id'] for b in registered}
        required=set(self.profile['bootstrap_repository_ids']) | {b['repository_id'] for b in registered if b['enabled']}
        check(required<=observed<=approved,'credential-scope')
        return {**identity,'state':'ready' if self.profile['creation_verified'] else 'canary-required',
                'active':self.profile['active'],'creation_verified':self.profile['creation_verified'],
                'selected_repository_ids':sorted(observed),'policy':self.profile['policy']}
    @contextlib.contextmanager
    def lease(self, role, repo_id=None, name=None):
        token=self.issue(role,repo_id,name)
        try:yield token
        finally:token.close()
    def project_token(self, root, role):
        check(role in {'git','pr'},'credential-scope')
        with app.locked('credential-profile'):
            current=profile()
            check(current['app_id']==self.profile['app_id'] and current['installation_id']==self.profile['installation_id'])
            self.profile=current
            value=bound(root)
            check(self.profile['active'],'credential-disabled')
            check(value['app_id']==self.profile['app_id'] and value['installation_id']==self.profile['installation_id'])
            self.identity()
            return self.issue(role,value['repository_id'],value['name'])


def configure(app_id,installation_id,key_file,bootstrap_ids):
    value=profile({'schema_version':1,'account':repos.ACCOUNT,'app_id':app_id,'installation_id':installation_id,
        'key_file':str(app.safe(Path(key_file).absolute())),'bootstrap_repository_ids':sorted(bootstrap_ids),
        'policy':'unprotected-private-dev','active':False,'creation_verified':False})
    with app.locked('credential-profile'):
        check(configured() is None,'conflict')
        result=Broker(value).doctor()
        private_directory(location());app.save(location()/'profile.json',value)
    return result


def set_active(active):
    with app.locked('credential-profile'):
        value=profile()
        if active:
            Broker(value).doctor();check(value['creation_verified'],'credential-recovery')
        value['active']=active;app.save(location()/'profile.json',value)
    return {'state':'active' if active else 'local-only','policy':value['policy']}


def rotate(key_file):
    with app.locked('credential-profile'):
        old=profile();candidate={**old,'key_file':str(app.safe(Path(key_file).absolute()))}
        check(candidate['key_file']!=old['key_file'])
        result=Broker(candidate).doctor()
        private_directory(location());app.save(location()/'previous-profile.json',old)
        app.save(location()/'profile.json',candidate)
    return {**result,'state':'rotated','previous_key_retained':True,
            'pending':['owner retires old GitHub signing key; issued tokens are not implicitly revoked']}


def disable(root):
    initial=bound(root,False)
    with app.locked('credential-'+str(initial['repository_id'])):
        value=bound(root,False);check(value['repository_id']==initial['repository_id'])
        value['enabled']=False;app.save(binding_path(root),value)
    return {'state':'disabled','repository_id':value['repository_id'],
            'residual_token_lifetime':'up to GitHub-reported expiry for crashed/in-flight operations'}


def enable(root):
    initial=bound(root,False)
    with app.locked('credential-'+str(initial['repository_id'])),app.locked('credential-profile'):
        value=bound(root,False);current=profile();b=Broker(current);b.identity()
        with b.lease('git',value['repository_id'],value['name']) as token:
            actual=token.request('GET','/repos/'+repos.ACCOUNT+'/'+value['name'])
            check_repo(actual,value['repository_id'],value['name'])
        value['enabled']=True;app.save(binding_path(root),value)
    return {'state':'enabled','repository_id':value['repository_id'],'profile_active':current['active']}


def bind_created(broker, receipt):
    value=receipt['plan'];repo_id=receipt['repository_id'];check(type(repo_id) is int and repo_id>0)
    path=binding_path(value['destination']);old=load(path,optional=True)
    binding={'schema_version':1,'account':repos.ACCOUNT,'app_id':broker.profile['app_id'],
        'installation_id':broker.profile['installation_id'],'repository_id':repo_id,'name':value['repository'],
        'root':value['destination'],'operation_id':value['operation_id'],'enabled':True,'helper_command':None}
    if old:
        validate_binding(old);check({k:v for k,v in old.items() if k!='helper_command'}=={k:v for k,v in binding.items() if k!='helper_command'},'credential-recovery')
    else:
        private_directory(path.parent);app.save(path,binding)
    receipt['credential_provider']={'kind':'github-app','app_id':broker.profile['app_id'],
        'installation_id':broker.profile['installation_id'],'canary':receipt.get('credential_provider',{}).get('canary',False)}
    receipt['protection_waiver']={'repository_id':repo_id,'account':repos.ACCOUNT,
        'authorized_by':'owner-activated-profile','policy':'unprotected-private-dev',
        'scope':'this-operation; private PR workflow without server protection'}
    repos.persist(receipt)


class Provision:
    requires_admin=False
    def __init__(self, broker, value, receipt=None, canary=False):
        self.broker=broker;self.value=value;self.repo_id=receipt.get('repository_id') if receipt else None
        self.token=None;self.canary=canary
    def actor(self):return {'login':repos.ACCOUNT,'credential_kind':'github-app-installation',**self.broker.identity()}
    def prepare_receipt(self,receipt):
        receipt['credential_provider']={'kind':'github-app','app_id':self.broker.profile['app_id'],'installation_id':self.broker.profile['installation_id'],'canary':self.canary}
    def after_creation(self,receipt):
        self.repo_id=receipt['repository_id'];bind_created(self.broker,receipt)
    def scoped(self):
        if self.token is not None:
            expires=dt.datetime.fromisoformat(self.token.expires_at)
            if expires-dt.datetime.now(dt.timezone.utc)>dt.timedelta(minutes=5):return self.token
            self.token.close();self.token=None
        for attempt in range(4):
            installed=self.broker.api().request('GET',repos.prefix(self.value)+'/installation',missing=True)
            if installed is not None:
                check(installed.get('id')==self.broker.profile['installation_id']
                      and installed.get('app_id')==self.broker.profile['app_id'],'credential-scope')
                self.token=self.broker.issue('provision',self.repo_id,self.value['repository'])
                return self.token
            if attempt==3:raise app.AppError('credential-recovery')
            time.sleep(0.25)  # Only absent-inclusion observations are retried.
    def request(self,method,path,body=None,missing=False):
        base=repos.prefix(self.value)
        check(path==base or path.startswith(base+'/') or path.startswith(base+'?') or (method=='POST' and path=='/user/repos'))
        if self.repo_id is None:
            check((method=='GET' and path==base) or (method=='POST' and path=='/user/repos'))
            with self.broker.lease('create') as token:return token.request(method,path,body,missing)
        endpoint=path[len(base):]
        allowed=(method=='GET' and (endpoint=='' or endpoint.startswith('/git/ref/heads/') or endpoint.startswith('/pulls?'))) or (method=='POST' and endpoint in {'/git/blobs','/git/trees','/git/commits','/git/refs','/pulls'})
        check(allowed,'credential-policy')
        return self.scoped().request(method,path,body,missing)
    @contextlib.contextmanager
    def git_environment(self):
        with self.scoped().git_environment() as auth:yield auth
    def close(self):
        return self.token.close() if self.token else 'no-project-token-issued'


def enroll(root):
    root=app.safe(Path(root).absolute());initial=bound(root)
    with app.locked('credential-'+str(initial['repository_id'])):
        value=bound(root);check(root.is_dir() and value['repository_id']==initial['repository_id'])
        config=root/'.git/config';app.safe(config)
        old=config.read_bytes();check(len(old)<8192)
        if value['helper_command'] and b'[credential]' in old:
            validate_git_helper(root);return value
        # A durable binding may precede the config write after interruption. Repair
        # only a still-valid base config, appending the same owned enrollment.
        repos.check_git_storage(root)
        command=value['helper_command']
        if command is None:
            bundle=app.provider_bundle()
            command=str(bundle/'scripts/repository-credential-helper')+' --project-root '+str(root)
            value['helper_command']=command;app.save(binding_path(root),value)
        addition='\n[credential]\n\thelper =\n\thelper = '+command+'\n\tuseHttpPath = true\n\tusername = x-access-token\n'
        check(config.read_bytes()==old,'credential-recovery')
        import project_dependencies as deps
        deps.write_bytes(config,old+addition.encode())
        validate_git_helper(root)
        return value


def validate_git_helper(root, supplied=None):
    value=bound(root);command=helper_command(root);check(command is not None,'credential-recovery')
    import project_dependencies as deps
    raw=deps.read_bytes(Path(root)/'.git/config',8192).decode('utf-8')
    # Parse only owned credential section; foreign URL rewriting/include/helper sections stop issuance.
    check(len(raw)<8192 and not re.search(r'(?im)^\s*\[(?:url|include|http|credential\s)',raw),'credential-policy')
    sections=re.findall(r'(?ms)^\[credential\]\s*\n(.*?)(?=^\[|\Z)',raw)
    check(len(sections)==1,'credential-recovery')
    lines=[line.strip() for line in sections[0].splitlines() if line.strip()]
    check(lines==['helper =','helper = '+command,'useHttpPath = true','username = x-access-token'],'credential-policy')
    if supplied is not None:check(supplied==['',command])
    # The remote identity is data, never an executable template.
    origin=re.findall(r'(?ms)^\[remote "origin"\]\s*\n(.*?)(?=^\[|\Z)',raw)
    check(len(origin)==1)
    for line in origin[0].splitlines():
        if line.strip():check(re.fullmatch(r'\s*(?:url|fetch)\s*=.*',line),'credential-policy')
    urls=re.findall(r'(?m)^\s*url\s*=\s*(.+)$',origin[0])
    check(urls==['https://github.com/'+repos.ACCOUNT+'/'+value['name']+'.git'],'credential-policy')
    return value


def create(name,directory=None,canary=False):
    broker=Broker();broker.doctor()
    check(canary or broker.profile['active'],'credential-disabled')
    destination=directory or str(app.PROJECTS/name)
    # Creation-only adapter can observe availability, not authenticate as a human.
    provisional={'repository':name}
    adapter=Provision(broker,provisional,canary=canary)
    value=repos.plan(name,destination,adapter)['plan'];adapter.value=value
    try:result=repos.apply(value,adapter)
    finally:adapter.close()
    enroll(value['destination'])
    result['ongoing_git_access']='configured-github-app-helper';result['pending']=['initial PR review/merge','starter quality/runtime checks']+([] if broker.profile['active'] else ['activate reviewed credential profile'])
    repos.persist(result)
    if canary:
        with app.locked('credential-profile'):
            current=profile();check(current['app_id']==broker.profile['app_id'] and current['installation_id']==broker.profile['installation_id'])
            current['creation_verified']=True;app.save(location()/'profile.json',current)
    return result


def resume(operation,repo_id=None):
    receipt=repos.read_receipt(operation);provider=receipt.get('credential_provider')
    check(isinstance(provider,dict) and provider.get('kind')=='github-app','credential-policy')
    broker=Broker()
    check(provider['app_id']==broker.profile['app_id'] and provider['installation_id']==broker.profile['installation_id'])
    adapter=Provision(broker,receipt['plan'],receipt,canary=provider.get('canary',False) if provider else False)
    try:result=repos.resume(operation,adapter,repo_id)
    finally:adapter.close()
    enroll(receipt['plan']['destination']);result['ongoing_git_access']='configured-github-app-helper'
    result['pending']=['initial PR review/merge','starter quality/runtime checks']+([] if broker.profile['active'] else ['activate reviewed credential profile']);repos.persist(result)
    if provider and provider.get('canary'):
        with app.locked('credential-profile'):
            current=profile();check(current['app_id']==broker.profile['app_id'] and current['installation_id']==broker.profile['installation_id'])
            current['creation_verified']=True;app.save(location()/'profile.json',current)
    return result


def preview(name,directory=None,template=None,version=None,local_only=False):
    import project_templates as templates
    value=None if local_only else configured()
    release,_=templates.resolve(template,version)
    check(isinstance(name,str) and re.fullmatch(r'[a-z][a-z0-9]*(?:-[a-z0-9]+)*',name) and len(name)<=48)
    destination=app.safe(Path(directory).absolute() if directory else app.PROJECTS/name)
    if value and value['active']:
        check((release['id'],release['version'])==('nextjs','1.0.0'))
        b=Broker(value);b.doctor();adapter=Provision(b,{'repository':name})
        planned=repos.plan(name,str(destination),adapter)['plan']
        return {'state':'planned','project':name,'root':str(destination),'template':planned['template'],
                'private':True,'repository':repos.ACCOUNT+'/'+name,'branches':planned['branches'],
                'policy':{'id':'unprotected-private-dev','protection_enforced':False},
                'credential_provider':{'app_id':value['app_id'],'installation_id':value['installation_id'],
                  'creation':ROLES['create'],'provision':ROLES['provision'],'ongoing_git':ROLES['git']},
                'side_effects':['create private repository','publish starter branch','open initial PR','enroll scoped Git helper'],
                'environments':[],'secret_references':[]}
    check(destination.is_relative_to(app.PROJECTS) and destination not in {app.PROJECTS,app.REPO}
          and '.gptclaw-runtime' not in destination.parts,'path')
    check(destination.parent.is_dir() and destination.parent.stat().st_uid==os.getuid(),'path')
    check(not destination.exists() and not destination.is_symlink(),'conflict')
    return {'state':'planned','project':name,'root':str(destination),'template':templates.provenance(release),
            'credential_provider':None,'side_effects':['create local starter only'],'github':False}


def new_project(name,directory=None,template=None,version=None,local_only=False):
    value=None if local_only else configured()
    if value and value['active']:
        check((template is None)==(version is None))
        check(template in {None,'nextjs'} and version in {None,'1.0.0'})
        return create(name,directory)
    return app.create(name,directory,template,version)


def open_pr(root,head,title,body):
    value=validate_git_helper(Path(root).absolute());check(re.fullmatch(r'codex/[a-zA-Z0-9._/-]{1,120}',head) and '..' not in head)
    check(isinstance(title,str) and 1<=len(title)<=200 and isinstance(body,str) and len(body)<=10000)
    broker=Broker();token=broker.project_token(root,'pr')
    base='/repos/'+repos.ACCOUNT+'/'+value['name']
    query=urllib.parse.urlencode({'state':'all','head':repos.ACCOUNT+':'+head,'base':'main','per_page':100})
    try:
        found=token.request('GET',base+'/pulls?'+query);check(isinstance(found,list) and len(found)<=1,'credential-recovery')
        if not found:found=[token.request('POST',base+'/pulls',{'head':head,'base':'main','title':title,'body':body})]
        item=found[0]
        check(item.get('state')=='open' and item.get('head',{}).get('repo',{}).get('id')==value['repository_id']
              and item.get('head',{}).get('ref')==head and item.get('base',{}).get('ref')=='main'
              and item.get('base',{}).get('repo',{}).get('id')==value['repository_id'],'credential-scope')
        number=item.get('number');check(type(number) is int and number>0)
        return {'state':'pull-request-open','url':'https://github.com/'+repos.ACCOUNT+'/'+value['name']+'/pull/'+str(number),
                'repository_id':value['repository_id'],'credential':token.metadata}
    finally:token.close()
