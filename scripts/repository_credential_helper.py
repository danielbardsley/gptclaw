#!/usr/bin/env python3
"""Git credential protocol only; no reusable-token CLI convenience output."""
import argparse
import json
import os
from pathlib import Path
import stat
import sys
sys.dont_write_bytecode=True

import private_apps as app
import repository_credentials as broker


def main(argv=None):
    parser=argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument('--project-root',required=True)
    parser.add_argument('action',choices=['get','store','erase'])
    args=parser.parse_args(argv)
    if args.action!='get':return 0  # Never persist the credential Git sends back.
    token=None
    try:
        broker.check(stat.S_ISFIFO(os.fstat(0).st_mode) and stat.S_ISFIFO(os.fstat(1).st_mode),'credential-policy')
        raw=sys.stdin.buffer.read(16385);broker.check(len(raw)<=16384)
        fields={}
        for line in raw.decode('utf-8').splitlines():
            if not line:break
            broker.check('=' in line)
            key,value=line.split('=',1)
            if key in {'wwwauth[]','capability[]','state[]'}:continue  # Bounded standard Git hints; never interpreted as authority.
            broker.check(key not in fields);fields[key]=value
        broker.check(set(fields)<={'protocol','host','path','username'})
        binding=broker.validate_git_helper(Path(args.project_root).absolute())
        expected=broker.repos.ACCOUNT+'/'+binding['name']+'.git'
        broker.check(fields.get('protocol')=='https' and fields.get('host')=='github.com'
                     and fields.get('path')==expected
                     and fields.get('username','x-access-token')=='x-access-token','credential-scope')
        with app.locked('credential-'+str(binding['repository_id'])):
            token=broker.Broker().project_token(args.project_root,'git')
            receipt={'schema_version':1,'repository_id':binding['repository_id'],**token.metadata,
                     'revocation':'Git pipe handoff; expires at reported time, no bearer cache'}
            broker.private_directory(broker.location()/'receipts')
            app.save(broker.location()/'receipts'/(str(binding['repository_id'])+'.json'),receipt)
            sys.stdout.write('username=x-access-token\npassword='+token._token+'\n\n');sys.stdout.flush()
        # Git still needs this token after helper exit. Do not revoke it here.
        return 0
    except (app.AppError,OSError,ValueError,UnicodeError,KeyError,TypeError):
        if token is not None:token.close()
        sys.stderr.write('Managed Git credentials unavailable; inspect credentials doctor/status.\n')
        return 1


if __name__=='__main__':raise SystemExit(main())
