#!/usr/bin/env python3
"""Generate and verify native/Python starters without managed host activation."""
import argparse
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import private_apps as a


def main():
    parser=argparse.ArgumentParser(description=__doc__,allow_abbrev=False)
    parser.add_argument('directory');parser.add_argument('--engine',choices=['podman','docker'],default='docker')
    parser.add_argument('--node-image');parser.add_argument('--api-image')
    args=parser.parse_args();base=Path(args.directory).absolute()
    a.need(not base.exists(),'conflict');base.mkdir(mode=0o700)
    projects=base/'projects';projects.mkdir()
    with patch.object(a,'PROJECTS',projects),patch.object(a,'STORE',base/'runtime'):
        backend=Path(a.create('native-api',template='fastapi-postgres',template_version='1.0.0')['root'])
        mobile=Path(a.create('native-notes',template='expo-notes',template_version='1.0.0')['root'])
        a.create('second-api',template='fastapi-postgres',template_version='1.0.0')
        a.create('second-notes',template='expo-notes',template_version='1.0.0')
    image=args.node_image or 'gptclaw-mobile-backend-check'
    if not args.node_image:
        subprocess.run([args.engine,'build','-t',image,'-f',str(mobile/'checks/toolchain/Containerfile'),str(mobile/'checks/toolchain')],check=True,timeout=300)
    common=[args.engine,'run','--rm','--user',str(__import__('os').getuid())+':'+str(__import__('os').getgid()),
            *(['--userns=keep-id'] if args.engine=='podman' else []),'--memory=1536m','--cpus=1','--pids-limit=256',
            '--cap-drop=all','--security-opt=no-new-privileges','--volume',str(mobile)+':/workspace:rw',
            '--workdir=/workspace','--env','CI=1','--env','EXPO_NO_TELEMETRY=1','--env','EXPO_NO_DOTENV=1']
    subprocess.run([*common,image,'pnpm','install','--frozen-lockfile','--ignore-scripts','--no-runtime','--pm-on-fail=error','--ignore-pnpmfile','--registry=https://registry.npmjs.org/'],check=True,timeout=600)
    subprocess.run([*common,image,'pnpm','verify'],check=True,timeout=1200)
    api=[sys.executable,str(a.REPO/'scripts/tests/check_database_template.py'),str(base/'database-check'),
         '--engine',args.engine,'--source-root',str(backend),'--node-image',image]
    if args.api_image:api+=['--api-image',args.api_image]
    subprocess.run(api,check=True,timeout=2400)
    print('PASS: generated native/Python quality, contracts and old-client migration; physical acceptance remains separate.')


if __name__=='__main__':main()
