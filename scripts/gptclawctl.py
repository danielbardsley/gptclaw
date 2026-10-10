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
 new=sub.add_parser('new');new.add_argument('slug');new.add_argument('--directory')
 for name in ['validate','start','stop','restart','status','logs','test']:
  p=sub.add_parser(name);p.add_argument('--project-root',required=True)
  if name=='start':p.add_argument('--local-only',action='store_true',help='Diagnose without requiring a private route; never claims desktop readiness.')
  if name=='logs':p.add_argument('--lines',type=int,default=80)
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
 args=parser.parse_args(argv)
 began=time.monotonic()
 try:
  import private_apps as app
  if args.provider_version:
   print(json.dumps({'provider':'gptclawctl','version':app.VERSION,'capabilities':['new','validate','start','stop','restart','status','logs','test','deps'],'receipt_schema':1,'dependency_receipt_schema':1}));return 0
  if not args.action:parser.print_help();return 0
  if args.action=='validate':
   from project_manifest import validate_project
   result,_,code=validate_project(args.project_root);print(json.dumps(result,sort_keys=True));return code
  app.need(os.getuid()==1002 and os.geteuid()!=0,'setup')
  if args.action=='new':result=app.create(args.slug,args.directory)
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
  elif args.action=='ingress':
   from private_ingress import main as ingress
   ingress();return 0
  result['duration_seconds']=round(time.monotonic()-began,3)
  print(json.dumps(result,sort_keys=True))
  return 1 if result.get('state') in {'operator-required','recovery-required','error'} else 0
 except ImportError:
  print(json.dumps({'state':'error','error':'setup','message':'Use the prepared isolated Python environment.'}));return 2
 except app.AppError as e:
  print(json.dumps({'state':'error','error':e.code,'message':str(e)}));return 2 if e.code in {'setup','internal'} else 1
 except (OSError,ValueError,KeyError,TypeError):
  print(json.dumps({'state':'error','error':'internal','message':'Runtime state could not be reconciled; inspect this target before retrying.'}));return 2


if __name__=='__main__':raise SystemExit(main())
