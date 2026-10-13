"""Native source creation and bounded quality jobs. No HTTP lifecycle adapter."""
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import time
import uuid


def app():
    import private_apps
    return private_apps


def check(ok, code='mobile-policy'):
    app().need(ok, code)


def profile():
    import project_dependencies as deps
    value = deps.json_data(deps.read_bytes(app().REPO/'config/mobile/v1.json', 65536))
    check(value.get('schema_version') == 1 and value.get('adapter') == 'expo-v1')
    check(isinstance(value.get('packages'), dict) and len(value['packages']) <= 100)
    for name, version in {**value['packages'], **value.get('allowed_additions', {})}.items():
        deps.package_name(name); deps.exact_version(version)
    return value


def identities(slug):
    check(isinstance(slug, str) and len(slug) <= 48 and re.fullmatch(r'[a-z][a-z0-9]*(?:-[a-z0-9]+)*', slug))
    return {'name':slug.replace('-', ' ').title(), 'slug':slug, 'scheme':'gptclaw-'+slug,
            'ios':{'bundleIdentifier':'dev.gptclaw.'+slug},
            'android':{'package':'dev.gptclaw.'+slug.replace('-', '_')}}


def contract(slug):
    return {'schema_version':5,'project':{'id':slug,'name':identities(slug)['name'],'kind':'mobile'},
            'mobile':{'adapter':'expo-v1','targets':['ios','android'],'app_config':'app.json'},
            'commands':{action:['pnpm',action] for action in ['format','lint','typecheck','test','build','security','verify']}}


def manifest_config(root, document, directory_fd=None):
    """Read only bounded owned static JSON; discovery never evaluates app config."""
    fd = None
    try:
        if directory_fd is None:
            from dashboard_inventory import open_directory
            fd = open_directory(Path(root).absolute())
        else:
            fd = os.dup(directory_fd)
        for name in ['app.config.js','app.config.ts','app.config.json','android','ios']:
            try: os.stat(name, dir_fd=fd, follow_symlinks=False)
            except FileNotFoundError: continue
            return False
        before = os.stat('app.json', dir_fd=fd, follow_symlinks=False)
        if not stat.S_ISREG(before.st_mode) or before.st_uid != os.getuid() or before.st_nlink != 1 or before.st_size > 65536:
            return False
        opened = os.open('app.json', os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC, dir_fd=fd)
        with os.fdopen(opened, 'rb') as stream:
            info = os.fstat(stream.fileno())
            if (info.st_dev,info.st_ino,info.st_uid,info.st_nlink)!=(before.st_dev,before.st_ino,before.st_uid,1):return False
            data = stream.read(65537)
        if len(data)>65536:return False
        import project_dependencies as deps
        value = deps.json_data(data)
        if set(value)!= {'expo'} or not isinstance(value['expo'],dict):return False
        expo=value['expo'];expected=identities(document['project']['id'])
        if set(expo)!= {'name','slug','scheme','version','platforms','orientation','ios','android'}:return False
        if not all(expo.get(key)==val for key,val in expected.items()):return False
        if expo['name']!=document['project']['name'] or expo['platforms']!=['ios','android'] or expo['orientation']!='portrait':return False
        return isinstance(expo['version'],str) and re.fullmatch(r'\d+\.\d+\.\d+',expo['version']) is not None
    except (OSError,ValueError,app().AppError):
        return False
    finally:
        if fd is not None:os.close(fd)


def validate_package(package):
    check(package.get('gptclawMobile')=='expo-v1' and package.get('main')=='expo-router/entry')
    actual={}
    for group in ['dependencies','devDependencies','optionalDependencies']:
        actual.update(package.get(group,{}))
    matrix=profile();required=matrix['packages'];allowed=matrix.get('allowed_additions',{})
    check(all(actual.get(name)==version for name,version in required.items()))
    check(all(name in required or allowed.get(name)==version for name,version in actual.items()))


def location(slug):
    identities(slug)
    return app().safe(app().STORE/'mobile'/slug/'job.json')


def load_state(root, slug):
    path=location(slug)
    if not path.exists():
        check(not path.is_symlink(),'path');return None
    value=app().read_json(path)
    required={'schema_version','adapter','id','root','name','token','phase','image','operation_id','operation_result'}
    check(isinstance(value,dict) and required<=set(value)<=required|{'operation','toolchain_hash'} and type(value.get('schema_version')) is int and value['schema_version']==1 and value.get('adapter')=='mobile','conflict')
    check(value['image'] is None or isinstance(value['image'],str) and re.fullmatch(r'sha256:[0-9a-f]{64}',value['image']),'conflict')
    check(value['operation_id'] is None or isinstance(value['operation_id'],str) and re.fullmatch(r'[0-9a-f]{32}',value['operation_id']),'conflict')
    check(value['operation_result'] in {None,'running','passed','failed','unknown'},'conflict')
    check(value.get('operation') in {None,'deps','format','lint','typecheck','test','build','security','verify'},'conflict')
    check('toolchain_hash' not in value or isinstance(value['toolchain_hash'],str) and re.fullmatch(r'[0-9a-f]{64}',value['toolchain_hash']),'conflict')
    check(value.get('id')==slug and value.get('root')==str(root),'conflict')
    check(isinstance(value.get('token'),str) and re.fullmatch(r'[0-9a-f]{32}',value['token']),'conflict')
    check(value.get('name')=='gptclaw-mobile-'+hashlib.sha256(str(root).encode()).hexdigest()[:24],'conflict')
    check(value.get('phase') in {'idle','checking','failed'},'conflict')
    return value


def save_state(value):
    path=location(value['id']);path.parent.mkdir(parents=True,mode=0o700,exist_ok=True)
    check(path.parent.stat().st_uid==os.getuid() and path.parent.stat().st_mode & 0o077 == 0,'path')
    app().save(path,value)


def job_state(root, document):
    a=app();slug=document['project']['id'];state=load_state(root,slug)
    if state is None:
        check(a.state_for(slug) is None,'conflict')
        state={'schema_version':1,'adapter':'mobile','id':slug,'root':str(root),
               'name':'gptclaw-mobile-'+hashlib.sha256(str(root).encode()).hexdigest()[:24],
               'token':uuid.uuid4().hex,'phase':'idle','image':None,'operation_id':None,'operation_result':None}
        save_state(state)
    check(not a.object_owned('container',state['name']+'-job',state['token']),'busy')
    return state


def invalidate(state, complete=False, operation_id=None):
    state.update(phase='idle' if complete else 'failed',operation='deps',operation_result='passed' if complete else 'unknown')
    if operation_id:state['operation_id']=operation_id
    save_state(state)


def quality(root, action):
    import project_dependencies as deps
    import project_toolchains as tools
    a=app();root,document=a.target(root);check(document['schema_version']==5)
    check(action in document['commands'],'mobile-unsupported')
    slug=document['project']['id']
    # Preparation is a shared transactional operation; it owns its own lock.
    status=deps.status(root)
    if status['state']!='dependencies-ready':
        deps.require_clean(root,slug);deps.operate(root,'install')
    with a.locked(slug):
        deps.require_clean(root,slug);ctx=deps.context(root)
        check(manifest_config(root,document))
        state=job_state(root,document);selected=tools.selection(root)
        state.update(image=a.toolchain(root,selected),toolchain_hash=selected['selection_hash'],
                     phase='checking',operation=action,operation_id=uuid.uuid4().hex,operation_result='running')
        save_state(state)
        try:
            steps=['format-check','lint','typecheck','test','sdk','security','build'] if action=='verify' else [action]
            for step in steps:
                argv=['node','checks/quality.cjs',step] if action=='verify' else document['commands'][action]
                a.run_in_app(state,argv,read_only_dependency_files=True)
                deps.verify_original(root,ctx['hashes'])
        except a.AppError:
            state.update(phase='failed',operation_result='failed');save_state(state);raise
        state.update(phase='idle',operation_result='passed');save_state(state)
        return {'project':slug,'state':action+'-passed','operation_id':state['operation_id'],
                'artifact_kind':'javascript-assets' if action in {'build','verify'} else None}


def dispatch(args):
    a=app();root,document=a.target(args.project_root)
    check(getattr(args,'component',None) is None,'mobile-unsupported')
    if args.action=='deps':
        import project_dependencies as deps
        if args.dependency_action=='status':return deps.status(root,getattr(args,'operation_id',None))
        return deps.operate(root,args.dependency_action,getattr(args,'package',None),getattr(args,'version',None),getattr(args,'kind','runtime'),getattr(args,'operation_id',None),getattr(args,'abort',False))
    if args.action=='toolchain':
        import project_toolchains as tools
        return tools.inspect(root) if args.toolchain_action=='inspect' else tools.prepare(root)
    if args.action in document['commands']:return quality(root,args.action)
    raise a.AppError('mobile-unsupported')


def creation_inputs(slug, release):
    return {'identity':identities(slug),'profile_digest':hashlib.sha256(json.dumps(profile(),sort_keys=True,separators=(',',':')).encode()).hexdigest(),
            'release_digest':release['digest']}


def assert_identity_vacant(destination, slug):
    """Only immediate owned project metadata; never execute project content."""
    from project_manifest import validate_project
    a=app()
    for index, path in enumerate(a.PROJECTS.iterdir()):
        check(index<4096,'conflict')
        if path.name.startswith('.') or path==destination or path.is_symlink() or not path.is_dir():continue
        if path.stat().st_uid != os.getuid():continue
        result,document,code=validate_project(path)
        if not code and document['project']['id']==slug:raise a.AppError('conflict')



def validate_policies(root, release):
    import project_dependencies as deps
    protected={'checks/sdk.json','checks/advisory-policy.json','checks/toolchain/profile.json','checks/toolchain/install-pnpm.cjs','checks/toolchain/Containerfile'}
    expected={item['output']:item['sha256'] for item in release['files'] if item['output'] in protected}
    check(set(expected)==protected)
    for name,digest in expected.items():
        check(hashlib.sha256(deps.read_bytes(root/name)).hexdigest()==digest)
