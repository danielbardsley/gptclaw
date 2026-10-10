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
 parser.add_argument('--version',action='store_true')
 sub=parser.add_subparsers(dest='action')
 new=sub.add_parser('new');new.add_argument('slug');new.add_argument('--directory')
 for name in ['validate','start','stop','restart','status','logs','test']:
  p=sub.add_parser(name);p.add_argument('--project-root',required=True)
  if name=='start':p.add_argument('--local-only',action='store_true',help='Diagnose without requiring a private route; never claims desktop readiness.')
  if name=='logs':p.add_argument('--lines',type=int,default=80)
 sub.add_parser('ingress',help=argparse.SUPPRESS)
 args=parser.parse_args(argv)
 began=time.monotonic()
 try:
  import private_apps as app
  if args.version:
   print(json.dumps({'provider':'gptclawctl','version':app.VERSION,'capabilities':['new','validate','start','stop','restart','status','logs','test'],'receipt_schema':1}));return 0
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
  elif args.action=='ingress':
   from private_ingress import main as ingress
   ingress();return 0
  result['duration_seconds']=round(time.monotonic()-began,3)
  print(json.dumps(result,sort_keys=True))
  return 1 if result.get('state')=='operator-required' else 0
 except ImportError:
  print(json.dumps({'state':'error','error':'setup','message':'Use the prepared isolated Python environment.'}));return 2
 except app.AppError as e:
  print(json.dumps({'state':'error','error':e.code,'message':str(e)}));return 1
 except (OSError,ValueError,KeyError,TypeError):
  print(json.dumps({'state':'error','error':'internal','message':'Runtime state could not be reconciled; inspect this target before retrying.'}));return 2


if __name__=='__main__':raise SystemExit(main())
