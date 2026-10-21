#!/usr/bin/env python3
"""Generate and verify an exact static starter, negative gates and exported browser."""
import argparse
import os
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import private_apps as app
import project_dependencies as deps


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory')
    parser.add_argument('--engine',choices=['podman','docker'],default='docker')
    parser.add_argument('--image',default='gptclaw-toolchain-ci')
    args=parser.parse_args()
    base=Path(args.directory).absolute();base.mkdir(mode=0o700)
    app.PROJECTS=base;app.STORE=base/'runtime'
    root=Path(app.create('static-check',template='nextjs-static',template_version='1.0.0')['root'])
    engine=[args.engine]
    if args.engine=='docker':
        config=base/'docker-config';config.mkdir(mode=0o700);(config/'config.json').write_text('{"auths":{}}\n')
        engine+=['--config',str(config)]
    def run(argv,ok=True,timeout=300):
        result=subprocess.run([*engine,*argv],text=True,capture_output=True,timeout=timeout)
        if (result.returncode==0)!=ok:raise AssertionError(app.redact((result.stdout+'\n'+result.stderr)[-6000:]))
        print(app.redact(result.stdout[-2000:]),flush=True)
        return result
    identity=['--userns=keep-id'] if args.engine=='podman' else ['--user',f'{os.getuid()}:{os.getgid()}']
    common=['run','--rm',*identity,'--memory=1536m','--cpus=1','--pids-limit=256','--cap-drop=all','--security-opt=no-new-privileges','--volume',str(root)+':/workspace:rw','--workdir','/workspace','--env','GPTCLAW_PROJECT_ID=static-check','--env','HOME=/tmp']
    for key,value in deps.GUARD_ENV.items():common+=['--env',key+'='+value]
    before={name:(root/name).read_bytes() for name in deps.FILES}
    run([*common,args.image,'pnpm','install','--frozen-lockfile',*deps.INSTALL_FLAGS])
    for action in ['format','lint','typecheck','test','build','links','security']:
        run([*common,args.image,'pnpm',action])
    assert before=={name:(root/name).read_bytes() for name in deps.FILES}
    for action,name,modify in [
        ('format','app/page.tsx',lambda s:s+'\n'),
        ('lint','app/page.tsx',lambda s:s+'\nconst unused = 1;\n'),
        ('typecheck','lib/site.ts',lambda s:s.replace('return `/projects/${slug}`;', 'return 42;')),
        ('links','out/index.html',lambda s:s+'<a href="/projects/static-check/broken/">Broken</a>'),
        ('links','out/index.html',lambda s:s+'<a href="/projects/static-check/guide/getting-started/#absent">Broken</a>'),
    ]:
        path=root/name;original=path.read_text()
        try:path.write_text(modify(original));run([*common,args.image,'pnpm',action],ok=False)
        finally:path.write_text(original)
    # Browser setup is a pinned image acquisition, separate from offline checks.
    browser='gptclaw-static-browser-check'
    run(['build','--tag',browser,'--file',str(root/'checks/Browser.Containerfile'),str(root/'checks')])
    run([*common,browser,'node','scripts/browser.mjs'])
    page=root/'app/page.tsx';original=page.read_text()
    try:
        page.write_text(original.replace('alt="A green leaf within a circle"',''))
        run([*common,args.image,'pnpm','build'])
        run([*common,browser,'node','scripts/browser.mjs'],ok=False)
    finally:page.write_text(original)
    try:
        page.write_text("import { cookies } from 'next/headers';\nexport default async function Page() { const value = await cookies(); return <h1>{value.get('test')?.value}</h1>; }\n")
        run([*common,args.image,'pnpm','build'],ok=False)
        assert not (root/'out/.gptclaw-build.json').exists()
        run([*common,args.image,'pnpm','start'],ok=False)
    finally:page.write_text(original)
    run([*common,args.image,'pnpm','build'])
    run([*common,browser,'node','scripts/browser.mjs'])
    # Compiled image can serve with only the published static export and its source identity.
    run(['build','--tag','gptclaw-static-compiled-check','--build-arg','PROJECT_ID=static-check','--file',str(root/'Containerfile'),str(root)],timeout=600)
    print('Exact generation, frozen restore, quality, fault rejection, exported browser and compiled image checks passed.')


if __name__=='__main__':main()
