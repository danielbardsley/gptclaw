#!/usr/bin/env python3
"""GptClaw versioned private project lifecycle CLI; argument vectors execute only in containers."""
import argparse
import json
import os
import sys
import time
sys.dont_write_bytecode=True


def main(argv=None):
 parser=argparse.ArgumentParser(description=__doc__,allow_abbrev=False)
 parser.add_argument('--version',dest='provider_version',action='store_true')
 sub=parser.add_subparsers(dest='action')
 new=sub.add_parser('new');new.add_argument('slug');new.add_argument('--directory');new.add_argument('--template');new.add_argument('--template-version');new.add_argument('--local-only',action='store_true');new.add_argument('--plan',action='store_true',help='Preview local or activated-profile GitHub creation without publishing source')
 for name in ['validate','start','stop','restart','rebuild','pause','resume','status','observe','logs','test','build','format','lint','typecheck','security','verify','hooks']:
  p=sub.add_parser(name);p.add_argument('--project-root',required=True)
  if name=='restart':p.add_argument('--component',choices=['web','api','db','metro'])
  if name in {'logs','test','build','format','lint','typecheck','security','verify'}:p.add_argument('--component',choices=['web','api','db'] if name=='logs' else ['web','api'])
  if name in {'start','restart'}:p.add_argument('--metro-transport',choices=['https','tailnet-http'],help='Explicit native Metro transport; HTTP remains inside the development tailnet.')
  if name=='start':p.add_argument('--local-only',action='store_true',help='Diagnose without requiring a private route; never claims desktop readiness.')
  if name=='logs':p.add_argument('--lines',type=int,default=80)
 control=sub.add_parser('control',help='Typed lifecycle capabilities and explicit interrupted-operation reconciliation')
 control_actions=control.add_subparsers(dest='control_action',required=True)
 for name in ['capabilities','reconcile']:
  p=control_actions.add_parser(name,allow_abbrev=False);p.add_argument('--project-root',required=True)
  if name=='reconcile':p.add_argument('--operation-id',required=True);p.add_argument('--confirm',required=True)
 backend=sub.add_parser('backend',help='Explicit Python mobile development binding')
 backend_actions=backend.add_subparsers(dest='backend_action',required=True)
 for name in ['bind','inspect']:
  p=backend_actions.add_parser(name,allow_abbrev=False);p.add_argument('--project-root',required=True)
  if name=='bind':p.add_argument('--backend-root',required=True);p.add_argument('--api-url',required=True)
 go=sub.add_parser('go',help='Read-only Expo Go compatibility inspection')
 go_actions=go.add_subparsers(dest='go_action',required=True)
 for name in ['inspect','launch']:
  inspect_go=go_actions.add_parser(name,allow_abbrev=False)
  inspect_go.add_argument('--project-root',required=True);inspect_go.add_argument('--platform',required=True,choices=['ios','android'])
  inspect_go.add_argument('--client-version');inspect_go.add_argument('--os-version')
  if name=='launch':inspect_go.add_argument('--generation',required=True)
 metro=sub.add_parser('metro',help='Native Metro opt-in, owned supervision and recovery')
 metro_actions=metro.add_subparsers(dest='metro_action',required=True)
 enable=metro_actions.add_parser('enable',allow_abbrev=False)
 enable.add_argument('--project-root',required=True);enable.add_argument('--ttl-seconds',type=int,default=7200)
 enable.add_argument('--apply',action='store_true');enable.add_argument('--confirm-plan')
 supervise=metro_actions.add_parser('supervise',allow_abbrev=False);supervise.add_argument('--project-root',required=True);supervise.add_argument('--generation',required=True)
 recover=metro_actions.add_parser('recover-stop',allow_abbrev=False);recover.add_argument('--project-root',required=True);recover.add_argument('--generation',required=True)
 renew=metro_actions.add_parser('renew',allow_abbrev=False);renew.add_argument('--project-root',required=True);renew.add_argument('--generation',required=True);renew.add_argument('--ttl-seconds',type=int);renew.add_argument('--apply',action='store_true');renew.add_argument('--confirm-plan')
 prune=metro_actions.add_parser('prune',allow_abbrev=False);prune.add_argument('--project-root',required=True);prune.add_argument('--apply',action='store_true');prune.add_argument('--confirm-plan')
 route=metro_actions.add_parser('route-plan',allow_abbrev=False);route.add_argument('--project-root',required=True);route.add_argument('--apply',action='store_true');route.add_argument('--confirm-plan')
 revoke=metro_actions.add_parser('revoke',allow_abbrev=False);revoke.add_argument('--policy-digest',required=True);revoke.add_argument('--apply',action='store_true')
 templates=sub.add_parser('templates',help='Discover bundled exact template releases')
 template_actions=templates.add_subparsers(dest='template_action',required=True)
 template_actions.add_parser('list',allow_abbrev=False)
 show=template_actions.add_parser('show',allow_abbrev=False);show.add_argument('--template',required=True);show.add_argument('--template-version',required=True)
 database=sub.add_parser('db',help='Owned development PostgreSQL operations')
 database_actions=database.add_subparsers(dest='database_action',required=True)
 for name in ['status','init','backup','seed','migrate','restore','reset','rotate','prune','recover']:
  p=database_actions.add_parser(name,allow_abbrev=False);p.add_argument('--project-root',required=True)
  if name=='init':p.add_argument('--operation-id')
  if name in {'migrate','restore','reset','rotate','prune','recover'}:
   p.add_argument('--operation-id');p.add_argument('--confirm');p.add_argument('--backup-id' if name=='restore' else '--ids',dest='selected')
 sub.add_parser('ingress',help=argparse.SUPPRESS)
 deps=sub.add_parser('deps',help='Manage project dependencies inside reviewed containers')
 actions=deps.add_subparsers(dest='dependency_action',required=True)
 for name in ['status','install','add','update','remove','recover']:
  p=actions.add_parser(name,allow_abbrev=False);p.add_argument('--project-root',required=True);p.add_argument('--component',choices=['web','api'])
  if name in ['add','update','remove']:p.add_argument('--package',required=True)
  if name in ['add','update']:p.add_argument('--version',required=True)
  if name=='status':p.add_argument('--operation-id')
  if name=='add':p.add_argument('--kind',choices=['runtime','development','test'],default='runtime')
  if name=='recover':
   p.add_argument('--operation-id',required=True);p.add_argument('--abort',action='store_true',help='Abandon the job while preserving current coherent source files')
 tools=sub.add_parser('toolchain',help='Inspect or prepare a reviewed exact container toolchain')
 tool_actions=tools.add_subparsers(dest='toolchain_action',required=True)
 for name in ['inspect','prepare']:
  p=tool_actions.add_parser(name,allow_abbrev=False);p.add_argument('--project-root',required=True);p.add_argument('--component',choices=['web','api'])
 repos=sub.add_parser('repo',help='Opt-in private GitHub repository setup')
 repo_actions=repos.add_subparsers(dest='repo_action',required=True)
 for name in ['plan','apply','resume','status']:
  p=repo_actions.add_parser(name,allow_abbrev=False)
  p.add_argument('--credential-file');p.add_argument('--credential-expires-at')
  if name=='plan':
   p.add_argument('--repository',required=True);p.add_argument('--directory',required=True)
   p.add_argument('--template');p.add_argument('--template-version')
   p.add_argument('--environment',action='append',default=[],choices=['development','preview'])
   p.add_argument('--secret-reference',action='append',default=[],help='scope:NAME metadata only')
  if name=='apply':p.add_argument('--plan-file',required=True)
  if name in ['resume','status']:p.add_argument('--operation-id',required=True)
  if name in ['apply','resume']:p.add_argument('--create-only',action='store_true',help='Create private repository, then pause for a repository-specific credential')
  if name=='resume':p.add_argument('--allow-unprotected-main',action='store_true',help='Explicit owner waiver for this recorded operation; no environments or protection removal')
  if name=='resume':p.add_argument('--confirm-repository-id',type=int,help='Explicit owner reconciliation after a lost creation response')
 worktrees=sub.add_parser('worktrees',help='Source-only task checkouts and explicit handoff')
 worktree_actions=worktrees.add_subparsers(dest='worktree_action',required=True)
 for name in ['plan','create','status','handoff','resume','cleanup']:
  p=worktree_actions.add_parser(name,allow_abbrev=False);p.add_argument('--project-root',required=True);p.add_argument('--task',required=True)
  if name!='status':p.add_argument('--owner',required=True)
  if name=='create':p.add_argument('--base-commit',required=True)
  if name in {'handoff','resume','cleanup'}:p.add_argument('--generation',type=int,required=True)
  if name=='handoff':
   p.add_argument('--checks-file');p.add_argument('--remaining',action='append',default=[]);p.add_argument('--published',action='store_true');p.add_argument('--pr',type=int)
  if name=='resume':p.add_argument('--target-owner',required=True)
  if name=='cleanup':p.add_argument('--head',required=True);p.add_argument('--apply',action='store_true')
 credentials=sub.add_parser('credentials',help='Private GitHub App setup and managed repository access')
 credential_actions=credentials.add_subparsers(dest='credential_action',required=True)
 for name in ['configure','installation-policy','workflow-policy','doctor','status','activate','deactivate','rotate','disable','enable','canary','resume','pull-request']:
  p=credential_actions.add_parser(name,allow_abbrev=False)
  if name=='configure':
   p.add_argument('--app-id',type=int,required=True);p.add_argument('--installation-id',type=int,required=True)
   p.add_argument('--key-file',required=True);p.add_argument('--bootstrap-repository-id',type=int,action='append',required=True)
   p.add_argument('--repository-selection',choices=['selected','all'],default='selected')
  if name=='installation-policy':p.add_argument('--repository-selection',choices=['selected','all'],required=True)
  if name=='workflow-policy':
   selection=p.add_mutually_exclusive_group(required=True);selection.add_argument('--repository',action='append');selection.add_argument('--disable',action='store_true')
  if name=='rotate':p.add_argument('--key-file',required=True)
  if name in ['disable','enable','pull-request']:p.add_argument('--project-root',required=True)
  if name=='canary':
   p.add_argument('--repository',required=True);p.add_argument('--directory',required=True)
   p.add_argument('--template');p.add_argument('--template-version')
  if name=='resume':p.add_argument('--operation-id',required=True);p.add_argument('--confirm-repository-id',type=int)
  if name=='pull-request':
   p.add_argument('--head',required=True);p.add_argument('--title',required=True);p.add_argument('--body-file',required=True)
 smoke=sub.add_parser('smoke',help='Read-only owned private-ingress quality checks')
 smoke.add_argument('--project-root',required=True);smoke.add_argument('--watch-seconds',type=int,default=0);smoke.add_argument('--poll-seconds',type=float,default=1)
 smoke_opt=smoke.add_mutually_exclusive_group();smoke_opt.add_argument('--enable-after-start',action='store_true');smoke_opt.add_argument('--disable-after-start',action='store_true')
 args=parser.parse_args(argv)
 began=time.monotonic()
 try:
  import private_apps as app
  if args.provider_version:
   print(json.dumps({'provider':'gptclawctl','version':app.VERSION,'worktree_receipt_schema':1,'capabilities':['smoke','control','backend','metro','worktrees','db','new','validate','start','stop','restart','rebuild','pause','resume','status','observe','logs','test','deps','toolchain','templates','repo','credentials','build','format','lint','typecheck','security','verify','hooks'],'lifecycle_control_schema':1,'lifecycle_actions':['start','stop','restart','rebuild','pause','resume'],'component_restart':['web','api','db','metro'],'backend_actions':['bind','inspect'],'backend_contract_schemas':[1],'metro_actions':['enable','renew','prune','route-plan','recover-stop','revoke'],'metro_contract_manifest_schemas':[6,9],'metro_session_schemas':[1,2],'metro_control_schemas':[2,3],'expo_go_inspection_schemas':[1],'expo_go_launch_schemas':[1],'project_manifest_schemas':[1,2,3,4,5,6,7,8,9,10],'project_kinds':['web','api','group','mobile'],'runtime_manifest_schemas':[1,2,3,4,6,7,8,9,10],'toolchain_schemas':[1,2],'template_catalogue_schema':8,'receipt_schema':1,'group_receipt_schema':4,'group_receipt_schemas':[2,3,4],'dependency_receipt_schema':1,'dependency_receipt_schemas':[1,2],'toolchain_receipt_schema':1,'credential_profile_schema':5,'credential_profile_schemas':[1,2,3,4,5],'credential_binding_schema':1,'dashboard_observation_schema':1,'dashboard_route_schema':1}));return 0
  if not args.action:parser.print_help();return 0
  if args.action=='templates':
   import project_templates as templates
   result=templates.discover() if args.template_action=='list' else templates.discover(args.template,args.template_version)
   print(json.dumps(result,sort_keys=True));return 0
  if args.action=='validate':
   from project_manifest import validate_project
   result,_,code=validate_project(args.project_root)
   if code==0:
    from pathlib import Path
    import project_templates as templates
    templates.validate_provenance(Path(args.project_root).absolute())
   print(json.dumps(result,sort_keys=True));return code
  # A lexical refusal performs no project reads or execution and is user-independent.
  if hasattr(args,'project_root') and args.action not in {'worktrees','credentials','repo','validate'}:
   from pathlib import Path
   import project_worktrees
   app.need('.gptclaw-worktrees' not in Path(args.project_root).parts,'worktree-source-only')
  app.need(os.getuid()==1002 and os.geteuid()!=0,'setup')
  if hasattr(args,'project_root') and args.action not in {'worktrees','credentials','repo','validate'}:
   from project_worktrees import guard
   guard(args.project_root)
  if args.action=='smoke':
   import project_smoke
   if args.enable_after_start or args.disable_after_start: project_smoke.configure(args.project_root,args.enable_after_start)
   return project_smoke.observe(args.project_root,args.watch_seconds,args.poll_seconds)
  if args.action=='go':
   import expo_go
   result=expo_go.inspect(args.project_root,args.platform,args.client_version,args.os_version) if args.go_action=='inspect' else expo_go.launch(args.project_root,args.platform,args.client_version,args.os_version,args.generation)
  elif args.action=='backend':
   import mobile_backend
   result=mobile_backend.bind(args.project_root,args.backend_root,args.api_url) if args.backend_action=='bind' else {k:v for k,v in mobile_backend.inspect(args.project_root).items() if k not in {'root','api_url'}}
   print(json.dumps(result));return 0
  elif args.action=='metro':
   if args.metro_action=='prune':
    import metro_retention
    print(json.dumps(metro_retention.prune(args.project_root,args.apply,args.confirm_plan),sort_keys=True));return 0
   if args.metro_action=='renew':
    import metro_sessions
    print(json.dumps(metro_sessions.renew(args.project_root,args.generation,args.ttl_seconds,args.apply,args.confirm_plan),sort_keys=True));return 0
   if args.metro_action=='route-plan':
    import metro_routes
    print(json.dumps(metro_routes.plan(args.project_root,args.apply,args.confirm_plan),sort_keys=True));return 0
   if args.metro_action=='revoke':
    import metro_sessions
    print(json.dumps(metro_sessions.revoke(args.policy_digest,args.apply),sort_keys=True));return 0
   if args.metro_action=='recover-stop':
    import metro_sessions
    print(json.dumps(metro_sessions.recover_stop(args.project_root,args.generation),sort_keys=True));return 0
   if args.metro_action=='supervise':
    import metro_sessions
    result=metro_sessions.supervise(args.project_root,args.generation)
    return 1 if result['state'] in {'failed','recovery-required'} else 0
   import metro_contract
   result=metro_contract.public(metro_contract.enable(args.project_root,args.ttl_seconds,args.apply,args.confirm_plan))
   print(json.dumps(result,sort_keys=True))
   return 1 if result['state']=='metadata-recovery-required' else 0
  elif args.action=='worktrees':
   import project_worktrees as worktrees
   action=args.worktree_action
   common=(args.project_root,args.task)
   if action=='status':result=worktrees.status(*common)
   elif action=='plan':result=worktrees.plan(*common,args.owner)
   elif action=='create':result=worktrees.create(*common,args.owner,args.base_commit)
   elif action=='handoff':
    from pathlib import Path
    checks=json.loads(worktrees.small_file(Path(args.checks_file).absolute())) if args.checks_file else []
    result=worktrees.handoff(*common,args.owner,args.generation,checks,args.remaining,args.published,args.pr)
   elif action=='resume':result=worktrees.resume(*common,args.owner,args.generation,args.target_owner)
   else:result=worktrees.cleanup(*common,args.owner,args.generation,args.head,args.apply)
  elif args.action=='control':
   import project_controls as controls
   result=controls.capabilities(args.project_root) if args.control_action=='capabilities' else __import__('dashboard_controls').reconcile_operation(args.project_root,args.operation_id,args.confirm)
  elif args.action in {'rebuild','pause','resume'} or args.action=='restart' and getattr(args,'component',None) is not None:
   import project_controls as controls
   app.need(getattr(args,'metro_transport',None) is None,'invalid')
   result=controls.execute(args.project_root,args.action,getattr(args,'component',None))
  elif args.action in {'start','stop','restart','status','observe','logs','test','build','format','lint','typecheck','security','verify','deps','toolchain','db','hooks'} and app.target(args.project_root)[1]['schema_version'] in (5,6,9):
   import project_mobile as mobile
   result=mobile.dispatch(args)
  elif getattr(args,'metro_transport',None) is not None:
   raise app.AppError('mobile-unsupported')
  elif args.action=='db':
   import project_database as database
   result=database.dispatch(args.project_root,args.database_action,getattr(args,'selected',None),getattr(args,'operation_id',None),getattr(args,'confirm',None))
  elif args.action=='credentials':
   import repository_credentials as broker
   action=args.credential_action
   if action=='configure':result=broker.configure(args.app_id,args.installation_id,args.key_file,args.bootstrap_repository_id,args.repository_selection)
   elif action=='installation-policy':result=broker.set_installation_policy(args.repository_selection)
   elif action=='workflow-policy':result=broker.set_workflow_policy([] if args.disable else args.repository)
   elif action=='doctor':result=broker.Broker().doctor()
   elif action=='status':
    profile=broker.configured()
    result={'state':'unconfigured' if profile is None else ('active' if profile['active'] else 'local-only'),
            'profile':profile,'bindings':broker.bindings(),'operations':broker.operations()}
   elif action in ['activate','deactivate']:result=broker.set_active(action=='activate')
   elif action=='rotate':result=broker.rotate(args.key_file)
   elif action=='disable':result=broker.disable(args.project_root)
   elif action=='enable':result=broker.enable(args.project_root)
   elif action=='canary':result=broker.create(args.repository,args.directory,canary=True,template=getattr(args,'template',None),version=getattr(args,'template_version',None))
   elif action=='resume':result=broker.resume(args.operation_id,args.confirm_repository_id)
   elif action=='pull-request':
    from pathlib import Path
    import project_dependencies as deps
    body=deps.read_bytes(Path(args.body_file).absolute(),10000).decode('utf-8')
    result=broker.open_pr(args.project_root,args.head,args.title,body)
  elif args.action=='repo':
   import project_repositories as repos
   app.need(bool(args.credential_file)==bool(args.credential_expires_at),'repository-credential')
   api=repos.GitHub(args.credential_file,args.credential_expires_at) if args.credential_file else None
   if args.repo_action!='status':app.need(api is not None,'repository-credential')
   if args.repo_action=='plan':
    refs=[]
    for ref in args.secret_reference:
     app.need(ref.count(':')==1,'repository-policy')
     scope,name=ref.split(':');refs.append({'scope':scope,'name':name})
    result=repos.plan(args.repository,args.directory,api,args.environment,refs,args.template,args.template_version)
   elif args.repo_action=='apply':result=repos.apply(repos.read_plan(args.plan_file),api,args.create_only)
   elif args.repo_action=='resume':result=repos.resume(args.operation_id,api,args.confirm_repository_id,args.create_only,args.allow_unprotected_main)
   else:result=repos.status(args.operation_id,api)
  elif args.action=='new':
   import repository_credentials as broker
   result=(broker.preview if args.plan else broker.new_project)(args.slug,args.directory,args.template,args.template_version,args.local_only)
  elif args.action=='logs' and getattr(args,'component',None)=='db':
   import project_database as database
   result=database.logs(args.project_root,args.lines)
  elif args.action in {'logs','test','build','format','lint','typecheck','security','verify','deps','toolchain'} and app.target(args.project_root)[1]['schema_version'] in (3,4,8):
   import project_groups as groups
   kwargs={}
   if args.action=='logs':kwargs={'lines':args.lines}
   elif args.action=='deps':
    kwargs={'subaction':args.dependency_action,'name':getattr(args,'package',None),'version':getattr(args,'version',None),'kind':getattr(args,'kind','runtime'),'operation_id':getattr(args,'operation_id',None),'abort':getattr(args,'abort',False)}
   elif args.action=='toolchain':kwargs={'subaction':args.toolchain_action}
   result=groups.dispatch(args.project_root,args.action,getattr(args,'component',None),**kwargs)
  elif args.action=='start':result=app.start(args.project_root,args.local_only)
  elif args.action=='stop':result=app.stop(args.project_root)
  elif args.action=='restart':result=app.restart(args.project_root)
  elif args.action=='status':result=app.status(args.project_root)
  elif args.action=='observe':
   from dashboard_observation import project
   result=project(args.project_root)
  elif args.action=='test':result=app.test_app(args.project_root)
  elif args.action in {'build','format','lint','typecheck','security','verify'}:result=app.quality_app(args.project_root,args.action)
  elif args.action=='hooks':result=app.install_hooks(args.project_root)
  elif args.action=='logs':result=app.logs(args.project_root,args.lines)
  elif args.action=='deps':
   import project_dependencies as deps
   if args.dependency_action=='status':result=deps.status(args.project_root,getattr(args,'operation_id',None))
   else:result=deps.operate(args.project_root,args.dependency_action,getattr(args,'package',None),getattr(args,'version',None),getattr(args,'kind','runtime'),getattr(args,'operation_id',None),getattr(args,'abort',False))
  elif args.action=='toolchain':
   import project_toolchains as tools
   result=tools.inspect(args.project_root) if args.toolchain_action=='inspect' else tools.prepare(args.project_root)
  elif args.action=='ingress':
   from private_ingress import main as ingress
   ingress();return 0
  result['duration_seconds']=round(time.monotonic()-began,3)
  print(json.dumps(result,sort_keys=True))
  return 1 if result.get('state') in {'operator-required','recovery-required','error'} else 0
 except ImportError:
  print(json.dumps({'state':'error','error':'setup','message':'Use the prepared isolated Python environment.'}));return 2
 except app.AppError as e:
  failure={'state':'error','error':e.code,'message':str(e)}
  if hasattr(e,'recovery_path'):failure['retained_staging']=e.recovery_path
  print(json.dumps(failure));return 2 if e.code in {'setup','internal'} else 1
 except (OSError,ValueError,KeyError,TypeError) as e:
  failure={'state':'error','error':'internal','message':'Runtime state could not be reconciled; inspect this target before retrying.'}
  if hasattr(e,'recovery_path'):failure['retained_staging']=e.recovery_path
  print(json.dumps(failure));return 2


if __name__=='__main__':raise SystemExit(main())
