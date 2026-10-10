#!/usr/bin/env python3
"""GptClaw single-web-app lifecycle CLI; argument vectors execute only in containers."""
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
 for name in ['validate','start','stop','restart','status','logs','test']:
  p=sub.add_parser(name);p.add_argument('--project-root',required=True)
  if name=='start':p.add_argument('--local-only',action='store_true',help='Diagnose without requiring a private route; never claims desktop readiness.')
  if name=='logs':p.add_argument('--lines',type=int,default=80)
 templates=sub.add_parser('templates',help='Discover bundled exact template releases')
 template_actions=templates.add_subparsers(dest='template_action',required=True)
 template_actions.add_parser('list',allow_abbrev=False)
 show=template_actions.add_parser('show',allow_abbrev=False);show.add_argument('--template',required=True);show.add_argument('--template-version',required=True)
 sub.add_parser('ingress',help=argparse.SUPPRESS)
 deps=sub.add_parser('deps',help='Manage project dependencies inside reviewed containers')
 actions=deps.add_subparsers(dest='dependency_action',required=True)
 for name in ['status','install','add','update','remove','recover']:
  p=actions.add_parser(name,allow_abbrev=False);p.add_argument('--project-root',required=True)
  if name in ['add','update','remove']:p.add_argument('--package',required=True)
  if name in ['add','update']:p.add_argument('--version',required=True)
  if name=='status':p.add_argument('--operation-id')
  if name=='add':p.add_argument('--kind',choices=['runtime','development'],default='runtime')
  if name=='recover':
   p.add_argument('--operation-id',required=True);p.add_argument('--abort',action='store_true',help='Abandon the job while preserving current coherent source files')
 tools=sub.add_parser('toolchain',help='Inspect or prepare a reviewed exact container toolchain')
 tool_actions=tools.add_subparsers(dest='toolchain_action',required=True)
 for name in ['inspect','prepare']:
  p=tool_actions.add_parser(name,allow_abbrev=False);p.add_argument('--project-root',required=True)
 repos=sub.add_parser('repo',help='Opt-in private GitHub repository setup')
 repo_actions=repos.add_subparsers(dest='repo_action',required=True)
 for name in ['plan','apply','resume','status']:
  p=repo_actions.add_parser(name,allow_abbrev=False)
  p.add_argument('--credential-file');p.add_argument('--credential-expires-at')
  if name=='plan':
   p.add_argument('--repository',required=True);p.add_argument('--directory',required=True)
   p.add_argument('--environment',action='append',default=[],choices=['development','preview'])
   p.add_argument('--secret-reference',action='append',default=[],help='scope:NAME metadata only')
  if name=='apply':p.add_argument('--plan-file',required=True)
  if name in ['resume','status']:p.add_argument('--operation-id',required=True)
  if name in ['apply','resume']:p.add_argument('--create-only',action='store_true',help='Create private repository, then pause for a repository-specific credential')
  if name=='resume':p.add_argument('--allow-unprotected-main',action='store_true',help='Explicit owner waiver for this recorded operation; no environments or protection removal')
  if name=='resume':p.add_argument('--confirm-repository-id',type=int,help='Explicit owner reconciliation after a lost creation response')
 credentials=sub.add_parser('credentials',help='Private GitHub App setup and managed repository access')
 credential_actions=credentials.add_subparsers(dest='credential_action',required=True)
 for name in ['configure','doctor','status','activate','deactivate','rotate','disable','enable','canary','resume','pull-request']:
  p=credential_actions.add_parser(name,allow_abbrev=False)
  if name=='configure':
   p.add_argument('--app-id',type=int,required=True);p.add_argument('--installation-id',type=int,required=True)
   p.add_argument('--key-file',required=True);p.add_argument('--bootstrap-repository-id',type=int,action='append',required=True)
  if name=='rotate':p.add_argument('--key-file',required=True)
  if name in ['disable','enable','pull-request']:p.add_argument('--project-root',required=True)
  if name=='canary':p.add_argument('--repository',required=True);p.add_argument('--directory',required=True)
  if name=='resume':p.add_argument('--operation-id',required=True);p.add_argument('--confirm-repository-id',type=int)
  if name=='pull-request':
   p.add_argument('--head',required=True);p.add_argument('--title',required=True);p.add_argument('--body-file',required=True)
 args=parser.parse_args(argv)
 began=time.monotonic()
 try:
  import private_apps as app
  if args.provider_version:
   print(json.dumps({'provider':'gptclawctl','version':app.VERSION,'capabilities':['new','validate','start','stop','restart','status','logs','test','deps','toolchain','templates','repo','credentials'],'template_catalogue_schema':1,'receipt_schema':1,'dependency_receipt_schema':1,'toolchain_receipt_schema':1,'credential_profile_schema':1,'credential_binding_schema':1}));return 0
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
  app.need(os.getuid()==1002 and os.geteuid()!=0,'setup')
  if args.action=='credentials':
   import repository_credentials as broker
   action=args.credential_action
   if action=='configure':result=broker.configure(args.app_id,args.installation_id,args.key_file,args.bootstrap_repository_id)
   elif action=='doctor':result=broker.Broker().doctor()
   elif action=='status':
    profile=broker.configured()
    result={'state':'unconfigured' if profile is None else ('active' if profile['active'] else 'local-only'),
            'profile':profile,'bindings':broker.bindings(),'operations':broker.operations()}
   elif action in ['activate','deactivate']:result=broker.set_active(action=='activate')
   elif action=='rotate':result=broker.rotate(args.key_file)
   elif action=='disable':result=broker.disable(args.project_root)
   elif action=='enable':result=broker.enable(args.project_root)
   elif action=='canary':result=broker.create(args.repository,args.directory,canary=True)
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
    result=repos.plan(args.repository,args.directory,api,args.environment,refs)
   elif args.repo_action=='apply':result=repos.apply(repos.read_plan(args.plan_file),api,args.create_only)
   elif args.repo_action=='resume':result=repos.resume(args.operation_id,api,args.confirm_repository_id,args.create_only,args.allow_unprotected_main)
   else:result=repos.status(args.operation_id,api)
  elif args.action=='new':
   import repository_credentials as broker
   result=(broker.preview if args.plan else broker.new_project)(args.slug,args.directory,args.template,args.template_version,args.local_only)
  elif args.action=='start':result=app.start(args.project_root,args.local_only)
  elif args.action=='stop':result=app.stop(args.project_root)
  elif args.action=='restart':result=app.restart(args.project_root)
  elif args.action=='status':result=app.status(args.project_root)
  elif args.action=='test':result=app.test_app(args.project_root)
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
