#!/usr/bin/env python3
"""Offline synthetic lifecycle/proxy tests; no live Podman, systemd, Tailscale or AWS."""
import copy
import hashlib
from http.server import BaseHTTPRequestHandler,HTTPServer
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
import urllib.request

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import private_apps as app
import private_ingress as ingress


class Tests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
  self.base=Path(self.temp.name)/'projects';self.base.mkdir()
  self.units=Path(self.temp.name)/'units';self.units.mkdir()
  p=patch.object(app,'available',return_value=True);p.start();self.addCleanup(p.stop)
  for key,value in [('PROJECTS',self.base),('STORE',self.base/'.gptclaw-runtime/v1'),('UNITS',self.units)]:
   p=patch.object(app,key,value);p.start();self.addCleanup(p.stop)
 def project(self,name='alpha'):
  return Path(app.create(name)['root'])
 def state(self,root):
  _,c=app.target(root);s=app.reserve(root,c);s['image']='sha256:'+'1'*64
  app.save(app.STORE/(s['id']+'.json'),s);return s,c
 def result(self,code=0,out=''):
  return subprocess.CompletedProcess([],code,out,'')
 def test_new_manifest_validates_and_existing_destination_preserved(self):
  root=self.project();sentinel=root/'sentinel';sentinel.write_text('keep')
  self.assertEqual(app.validate_project(root)[2],0)
  with self.assertRaises(app.AppError):app.create('alpha')
  self.assertEqual(sentinel.read_text(),'keep')
 def test_template_omits_cache_artifacts(self):
  root=self.project()
  self.assertFalse((root/'.cache').exists());self.assertFalse((root/'node_modules').exists())
  self.assertTrue((root/'AGENTS.md').exists())
 def test_bad_slug_rejected_before_files(self):
  for slug in ['../alpha','UPPER','alpha%','alpha--beta','x'*49]:
   with self.assertRaises(app.AppError):app.create(slug)
  self.assertEqual(list(self.base.iterdir()),[])
 def test_symlink_and_outside_project_rejected(self):
  root=self.project();link=self.base/'link';link.symlink_to(root,target_is_directory=True)
  with self.assertRaises(app.AppError):app.target(link)
  with self.assertRaises(app.AppError):app.create('outside',Path(self.temp.name)/'outside')
 def test_invalid_manifest_never_invokes_runtime(self):
  root=self.project();(root/'.gptclaw/project.yaml').write_text('bad: field\n')
  with patch.object(app,'command') as run:
   with self.assertRaises(app.AppError):app.start(root)
   run.assert_not_called()
 def test_environment_material_is_not_mounted_by_this_slice(self):
  root=self.project();(root/'.env.local').write_text('synthetic=true')
  with patch.object(app,'command') as run:
   with self.assertRaises(app.AppError):app.start(root)
   run.assert_not_called()
 def test_provider_marker_required(self):
  root=self.project();(root/'.gptclaw/template.json').unlink()
  with self.assertRaises(app.AppError):app.target(root)
 def test_locks_report_busy_without_stealing(self):
  with app.locked('alpha'):
   with self.assertRaises(app.AppError) as e:
    with app.locked('alpha'):pass
   self.assertEqual(e.exception.code,'busy')
 def test_port_allocation_is_stable_independent_and_skips_occupied(self):
  root=self.project();other=self.project('beta')
  with patch.object(app,'available',side_effect=lambda p:p!=18080):
   a,_=self.state(root);b,_=self.state(other)
  self.assertEqual((a['port'],b['port']),(18081,18082))
  _,c=app.target(root);self.assertEqual(app.reserve(root,c)['port'],18081)
 def test_duplicate_project_id_different_root_refused(self):
  root=self.project();self.state(root)
  other=self.project('beta');m=json.loads((root/'.gptclaw/project.yaml').read_text())
  app.save(other/'.gptclaw/project.yaml',m)
  _,c=app.target(other)
  with self.assertRaises(app.AppError):app.reserve(other,c)
 def test_state_cannot_forward_outside_port_range_or_roots(self):
  root=self.project();s,_=self.state(root)
  for change in [{'port':22},{'port':True},{'root':'/etc'},{'id':'../etc'},{'token':'bad'}]:
   x={**s,**change}
   with self.assertRaises(app.AppError):app.valid_state(x)
 def test_changed_unit_refuses_stop_before_runtime_mutation(self):
  root=self.project();s,_=self.state(root)
  app.unit_path(s).write_text('unrelated')
  with patch.object(app,'command') as run,patch.object(app,'object_owned',return_value=False):
   with self.assertRaises(app.AppError):app.stop(root)
   run.assert_not_called()
 def test_effective_dropin_override_is_not_adopted(self):
  root=self.project();s,_=self.state(root);path=app.unit_path(s);path.write_text('owned unit')
  s['unit_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
  with patch.object(app,'command',return_value=self.result(out='SourcePath='+str(path)+'\nDropInPaths=/tmp/unknown.conf\n')):
   with self.assertRaises(app.AppError):app.verify_unit(s)
 def test_engine_error_is_not_absent_container(self):
  with patch.object(app,'command',return_value=self.result(125)):
   with self.assertRaises(app.AppError):app.object_owned('container','app','x')
 def test_other_owner_is_never_stopped(self):
  with patch.object(app,'command',return_value=self.result()),patch.object(app,'json_command',return_value=[{'Config':{'Labels':{app.LABEL:'another'}}}]):
   with self.assertRaises(app.AppError):app.object_owned('container','app','owner')
 def test_container_commands_are_argv_with_limits_and_no_host_shell(self):
  root=self.project();s,_=self.state(root)
  with patch.object(app,'command',side_effect=[self.result(1),self.result()]) as run:
   app.run_in_app(s,['node','literal; $(touch /sentinel)'])
   args=run.call_args.args[0]
   self.assertEqual(args[-2:],['node','literal; $(touch /sentinel)'])
   for flag in ['--userns=keep-id','--cpus=1','--memory=1536m','--pids-limit=256','--cap-drop=all']:
    self.assertIn(flag,args)
   self.assertNotIn('/bin/sh',args)
 def test_stale_job_not_replaced_on_unknown_outcome(self):
  root=self.project();s,_=self.state(root)
  with patch.object(app,'command',return_value=self.result()) as run:
   with self.assertRaises(app.AppError):app.run_in_app(s,['pnpm','test'])
   self.assertEqual(run.call_count,1)
 def test_unit_escapes_systemd_substitution_and_has_loopback_limits(self):
  root=self.project();s,c=self.state(root);c['commands']['start']=['node','literal $HOME %n']
  text=app.unit_text(s,c,'app.example.ts.net')
  self.assertIn('literal $$HOME %%n',text)
  self.assertIn('127.0.0.1:18080:3000',text);self.assertIn('ReadOnly=true',text)
 def test_route_refuses_unrelated_handler_and_funnel(self):
  with patch.object(app,'node_identity',return_value='app.example.ts.net'):
   cfg={'Web':{'app.example.ts.net:443':{'Handlers':{'/projects/':{'Proxy':'http://127.0.0.1:9999/'}}}}}
   with patch.object(app,'serve_config',return_value=cfg):
    with self.assertRaises(app.AppError):app.route_info('alpha')
   with patch.object(app,'json_command',return_value={'AllowFunnel':{'x':True}}):
    with self.assertRaises(app.AppError):app.serve_config()
 def test_route_existing_prefix_and_operator_remediation(self):
  with patch.object(app,'node_identity',return_value='app.example.ts.net'),patch.object(app,'serve_config',return_value={}):
   r=app.route_info('alpha');self.assertEqual(r['state'],'operator-required');self.assertIsNone(r['url'])
  cfg={'Web':{'app.example.ts.net:443':{'Handlers':{'/projects/':{'Proxy':'http://127.0.0.1:18079/projects/'}}}}}
  with patch.object(app,'node_identity',return_value='app.example.ts.net'),patch.object(app,'serve_config',return_value=cfg):
   self.assertEqual(app.route_info('alpha')['url'],'https://app.example.ts.net/projects/alpha/')
 def test_stop_revokes_mapping_and_preserves_source_and_other_state(self):
  root=self.project();s,_=self.state(root);other=self.project('beta');b,_=self.state(other)
  s.update(phase='ready',health_ready=True);app.save(app.STORE/'alpha.json',s)
  with patch.object(app,'object_owned',return_value=False),patch.object(app,'available',return_value=True):r=app.stop(root)
  self.assertTrue(r['source_retained']);self.assertTrue(root.exists())
  self.assertEqual(app.state_for('alpha')['phase'],'stopped');self.assertEqual(app.state_for('beta'),b)
 def test_failed_health_never_publishes_an_app(self):
  root=self.project()
  with patch.object(app,'toolchain',return_value='sha256:'+'2'*64),patch.object(app,'prepare'),patch.object(app,'write_unit'),patch.object(app,'node_identity',return_value='app.example.ts.net'),patch.object(app,'command',return_value=self.result()),patch.object(app,'healthy',return_value=False),patch.object(app.time,'monotonic',side_effect=[0,0,121]),patch.object(app.time,'sleep'),patch.object(app,'ensure_ingress') as publish:
   with self.assertRaises(app.AppError) as e:app.start(root)
   self.assertEqual(e.exception.code,'health');publish.assert_not_called()
  self.assertEqual(app.state_for('alpha')['phase'],'failed')
  self.assertFalse(app.state_for('alpha')['health_ready'])
 def test_preparation_reuses_lock_but_builds_after_test_only_install(self):
  root=self.project();s,c=self.state(root)
  with patch.object(app,'run_in_app') as run:
   app.prepare(s,c,False);(root/'node_modules').mkdir()
   app.prepare(s,c,False);self.assertEqual(run.call_count,1)
   app.prepare(s,c,True);self.assertEqual(run.call_count,3)
   app.prepare(s,c,True);self.assertEqual(run.call_count,3)
 def test_command_output_is_bounded_and_timeout_is_an_unknown_outcome(self):
  result=app.command(['python3','-c','print("x" * 1200000)'])
  self.assertEqual(len(result.stdout),1048576)
  with self.assertRaises(app.AppError) as e:app.command(['python3','-c','import time; time.sleep(5)'],timeout=.05)
  self.assertEqual(e.exception.code,'timeout')
 def test_restart_is_serialized_and_has_real_transitions(self):
  root=self.project();s,_=self.state(root)
  with patch.object(app,'stop',return_value={'operation_id':'stop-one'}) as stop,patch.object(app,'start',return_value={'operation_id':'start-two','state':'ready'}) as start:
   r=app.restart(root)
   self.assertEqual(r['transitions'],['stop-one','start-two'])
   stop.assert_called_once_with(root,take_lock=False);start.assert_called_once_with(root,take_lock=False)
   self.assertEqual(app.state_for('alpha')['operation'],'restart')
 def test_redaction_keeps_project_logs_bounded_without_secrets(self):
  text=app.redact('token=SECRET api_key: SECRET Bearer SECRET')
  self.assertNotIn('SECRET',text);self.assertIn('[redacted]',text)


class PortAvailabilityTests(unittest.TestCase):
 def test_unused_loopback_port_is_available(self):
  with socket.socket() as probe:
   probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
  self.assertTrue(app.available(port))
 def test_active_listener_is_not_available(self):
  with socket.socket() as listener:
   listener.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
   listener.bind(('127.0.0.1',0));listener.listen()
   self.assertFalse(app.available(listener.getsockname()[1]))
 def test_cleanly_closed_connection_does_not_block_port_reuse(self):
  with socket.socket() as listener, socket.socket() as client:
   listener.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
   listener.bind(('127.0.0.1',0));listener.listen()
   port=listener.getsockname()[1];client.settimeout(5)
   client.connect(('127.0.0.1',port));connection,_=listener.accept()
   connection.close();self.assertEqual(client.recv(1),b'')
  self.assertTrue(app.available(port))


class Backend(BaseHTTPRequestHandler):
 def do_GET(self):
  if self.path=='/redirect':
   self.send_response(302);self.send_header('Location','http://127.0.0.1:1/never');self.end_headers();return
  data=('served '+self.path).encode();self.send_response(200);self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
 def log_message(self,*_):pass


class ProxyTests(unittest.TestCase):
 def setUp(self):
  self.backend=HTTPServer(('127.0.0.1',0),Backend)
  self.proxy=ingress.Server(('127.0.0.1',0))
  for server in [self.backend,self.proxy]:
   thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
   self.addCleanup(server.server_close);self.addCleanup(server.shutdown)
  self.record={'phase':'ready','health_ready':True,'port':self.backend.server_port}
  p=patch.object(ingress,'state_for',side_effect=lambda slug:self.record if slug=='alpha' else None);p.start();self.addCleanup(p.stop)
  p=patch.object(ingress,'verify_unit');p.start();self.addCleanup(p.stop)
 def test_proxy_preserves_base_path_query_and_blocks_unknown_apps(self):
  base=f'http://127.0.0.1:{self.proxy.server_port}'
  with urllib.request.urlopen(base+'/projects/alpha/asset.js?x=1') as r:
   self.assertEqual(r.read(),b'served /projects/alpha/asset.js?x=1')
  for path in ['/projects/unknown/','/admin/','/projects/../']:
   with self.assertRaises(urllib.error.HTTPError) as e:urllib.request.urlopen(base+path)
   self.assertEqual(e.exception.code,404)
 def test_stopped_mapping_is_not_published(self):
  self.record['phase']='stopped'
  with self.assertRaises(urllib.error.HTTPError) as e:urllib.request.urlopen(f'http://127.0.0.1:{self.proxy.server_port}/projects/alpha/')
  self.assertEqual(e.exception.code,404)
 def test_health_does_not_follow_redirects(self):
  s={'port':self.backend.server_port};c={'service':{'health':{'path':'/redirect','timeout_seconds':1}}}
  self.assertFalse(app.healthy(s,c))


if __name__=='__main__':unittest.main(verbosity=2)
