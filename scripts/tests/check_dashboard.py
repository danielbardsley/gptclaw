#!/usr/bin/env python3
"""Build the exact dashboard and verify its HTTP/UI behavior in task-owned containers."""
import argparse
from http.server import BaseHTTPRequestHandler
import json
import os
from pathlib import Path
import socket
import socketserver
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
import uuid

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine',choices=['docker','podman'],default='docker')
    parser.add_argument('--reuse-node-image')
    parser.add_argument('--reuse-browser-image')
    parser.add_argument('--output',required=True)
    args=parser.parse_args()
    output=Path(args.output).absolute();output.mkdir(parents=True,exist_ok=True)
    token=uuid.uuid4().hex
    name='gptclaw-dashboard-check-'+token
    engine=args.engine
    common=['--user',f'{os.getuid()}:{os.getgid()}','--memory=1536m','--cpus=1',
            '--pids-limit=256','--cap-drop=all','--security-opt=no-new-privileges']
    if engine=='podman':common+=['--userns=keep-id']
    def run(argv,**kwargs):
        return subprocess.run([engine,*argv],check=True,timeout=300,**kwargs)
    image=args.reuse_node_image or 'localhost/gptclaw-dashboard-check:'+token+'-node'
    browser_image=args.reuse_browser_image or 'localhost/gptclaw-dashboard-check:'+token+'-browser'
    collector=None
    created=False
    with tempfile.TemporaryDirectory(prefix='.dashboard-check-',dir=ROOT) as temp:
        work=Path(temp)
        if not args.reuse_node_image:
            run(['build','--file',str(ROOT/'templates/apps/node-toolchain/Containerfile'),
                 '--tag',image,str(ROOT/'templates/apps/node-toolchain')])
        def job(vector):
            run(['run','--rm',*common,'--volume',str(ROOT/'platform/dashboard')+':/workspace:rw',
                 '--workdir','/workspace','--env','HOME=/tmp','--env','NEXT_TELEMETRY_DISABLED=1',
                 '--env','NODE_OPTIONS=--max-old-space-size=1024',image,*vector])
        job(['pnpm','install','--frozen-lockfile','--ignore-scripts','--no-runtime','--pm-on-fail=error',
             '--ignore-pnpmfile','--registry=https://registry.npmjs.org/'])
        for command in ('test','typecheck','build'):job(['pnpm',command])
        if not args.reuse_browser_image:
            acquire=ROOT/'templates/apps/releases/notes/1.0.0/checks/acquire-browser.py'
            subprocess.run([sys.executable,str(acquire),str(work/'browser')],check=True,timeout=60)
            run(['build','--file',str(work/'browser/Containerfile'),'--tag',browser_image,str(work/'browser')])
        run(['run','--rm',*common,browser_image,'node','-e',
             "if(require('playwright-core/package.json').version !== '1.64.0')process.exit(1)"])
        # Decode the final SVG rasterization, not just the encoder's internal matrix.
        qr_dir=work/'qr';qr_dir.mkdir(mode=0o700)
        generate_qr="import fs from 'node:fs'; import {localQr} from '/workspace/lib/local-qr.ts'; const payload='exp://forge-dev.example.ts.net:8443/_gptclaw/metro-session/'+'a'.repeat(32); fs.writeFileSync('/qr/code.svg',localQr(payload).svg,{flag:'wx'});"
        run(['run','--rm',*common,'--network=none',
             '--volume',str(ROOT/'platform/dashboard')+':/workspace:ro',
             '--volume',str(qr_dir)+':/qr:rw','--workdir','/workspace',image,
             'node','--input-type=module','--eval',generate_qr])
        run(['run','--rm',*common,'--network=none','--env','HOME=/tmp',
             '--volume',str(qr_dir)+':/qr:ro',
             '--volume',str(ROOT/'platform/dashboard/node_modules')+':/dashboard-modules:ro',
             '--volume',str(ROOT/'scripts/tests/dashboard-qr-browser.cjs')+':/checks/dashboard-qr-browser.cjs:ro',
             browser_image,'node','/checks/dashboard-qr-browser.cjs'])
        # Trusted synthetic fixture constructor; no project command/runtime starts.
        sys.path.insert(0,str(ROOT/'scripts/tests'))
        from test_dashboard_inventory import InventoryTests
        fixtures=InventoryTests();fixtures.setUp()
        try:
            for version,name_part in ((1,'web'),(2,'api'),(3,'group'),(4,'db')):
                fixtures.project(name_part,version)
            run_dir=work/'run';run_dir.mkdir(mode=0o700)
            # No runtime adapter: prove writes traverse the built Next route
            # and fixed Unix transport, then receive a typed refusal.
            class ControlStub(BaseHTTPRequestHandler):
                def log_message(self,*_):pass
                def reply(self,status,value):
                    body=json.dumps(value).encode();self.send_response(status)
                    self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
                def do_GET(self):self.reply(200,{'schema_version':1,'enabled':True,'projects':{}})
                def do_POST(self):
                    data=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                    assert self.path=='/v1/intents' and data=={'schema_version':1,'project_key':'d'*32,'action':'start','component':None}
                    assert self.headers['X-Control-Session']=='a'*64 and self.headers['X-CSRF-Token']=='b'*64
                    self.reply(409,{'error':'control-unsupported'})
            control_stub=socketserver.UnixStreamServer(str(run_dir/'control.sock'),ControlStub)
            control_thread=threading.Thread(target=control_stub.serve_forever,daemon=True);control_thread.start()
            collector=subprocess.Popen([sys.executable,'-B',str(ROOT/'scripts/dashboard_collector_runner.py'),
                '--projects-root',str(fixtures.projects),'--socket',str(run_dir/'collector.sock')],
                stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
            with socket.socket() as probe:
                probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
            origin='http://127.0.0.1:'+str(port)
            app=ROOT/'platform/dashboard/.next'
            (app/'standalone/.next/static').mkdir(exist_ok=True)
            created=True
            run(['run','--detach','--name',name,'--label','com.gptclaw.dashboard-check='+token,*common,
                '--publish','127.0.0.1:'+str(port)+':3000',
                '--volume',str(app/'standalone')+':/app:ro','--volume',str(app/'static')+':/app/.next/static:ro',
                '--volume',str(run_dir)+':/run/gptclaw:ro','--workdir','/app',
                '--env','HOSTNAME=0.0.0.0','--env','DASHBOARD_ORIGIN='+origin,'--env','PORT=3000',
                '--env','DASHBOARD_CONTROLS=1',
                '--env','NEXT_TELEMETRY_DISABLED=1',image,'node','server.js'])
            created=True
            for _ in range(60):
                try:
                    with urllib.request.urlopen(origin+'/dashboard/api/snapshot/',timeout=1) as response:
                        result=json.load(response)
                    if len(result.get('rows',[]))==4:break
                except (OSError,ValueError):pass
                if collector.poll() is not None:raise AssertionError('collector failed')
                time.sleep(.2)
            else:raise AssertionError('dashboard did not observe four synthetic projects')
            checks=[('POST','/dashboard/api/snapshot/',{'Origin':origin,'Sec-Fetch-Site':'same-origin','Content-Type':'application/json'},405),('GET','/dashboard/api/snapshot/?root=/etc',{},400),
                    ('GET','/dashboard/api/snapshot/',{'Origin':'https://untrusted.invalid'},403),
                    ('GET','/dashboard/api/snapshot/',{'Host':'untrusted.invalid'},403),
                    ('GET','/dashboard/',{'Sec-Fetch-Site':'cross-site','Sec-Fetch-Mode':'navigate','Sec-Fetch-Dest':'document'},200),
                    ('GET','/dashboard/api/snapshot/',{'Sec-Fetch-Site':'cross-site','Sec-Fetch-Mode':'navigate','Sec-Fetch-Dest':'document'},403)]
            for method,path,headers,expected in checks:
                try:
                    response=urllib.request.urlopen(urllib.request.Request(origin+path,method=method,headers=headers),timeout=3)
                except urllib.error.HTTPError as error:response=error
                assert response.code==expected,(method,path,response.code)
                response.close()
            write=urllib.request.Request(origin+'/dashboard/api/control-intents/',
                data=json.dumps({'schema_version':1,'project_key':'d'*32,'action':'start','component':None}).encode(),
                headers={'Origin':origin,'Sec-Fetch-Site':'same-origin','Content-Type':'application/json',
                         'Cookie':'__Secure-gptclaw-control='+'a'*64,'X-CSRF-Token':'b'*64})
            try:response=urllib.request.urlopen(write,timeout=5)
            except urllib.error.HTTPError as error:response=error
            with response:
                assert response.code==409 and json.load(response)=={'error':'control-unsupported'},'built write route did not reach controller'
            run(['run','--rm',*common,'--network=host','--env','HOME=/tmp','--env','DASHBOARD_BROWSER_ORIGIN='+origin,
                 '--volume',str(ROOT/'scripts/tests/dashboard-browser.cjs')+':/checks/dashboard-browser.cjs:ro',
                 '--volume',str(output)+':/checks/output:rw',browser_image,'node','dashboard-browser.cjs'])
        finally:
            if 'control_stub' in locals():
                control_stub.shutdown();control_stub.server_close();control_thread.join(timeout=5)
            if created:
                observed=run(['container','inspect',name,'--format','{{index .Config.Labels "com.gptclaw.dashboard-check"}}'],capture_output=True,text=True)
                assert observed.stdout.strip()==token,'refuse unknown container cleanup'
                run(['stop',name]);run(['rm',name])
            if collector:
                collector.terminate()
                try:collector.wait(timeout=5)
                except subprocess.TimeoutExpired:collector.kill();collector.wait()
                collector.stderr.close()
            fixtures.doCleanups()
    print('PASS: frozen dashboard install, tests, typecheck, production build, real socket/HTTP and synthetic browser acceptance')


if __name__=='__main__':main()
