#!/usr/bin/env python3
"""Behavioral QLT gates: real failure cases, source safety and generated metadata."""
import copy
import datetime as dt
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('quality', ROOT/'scripts/project_quality_core.py')
q = importlib.util.module_from_spec(spec); spec.loader.exec_module(q)


class QualityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='gptclaw-quality-unit-')
        self.addCleanup(self.temp.cleanup); self.root = Path(self.temp.name)

    def put(self, name, content):
        path = self.root/name; path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(content) if isinstance(content, (dict, list)) else content)
        return path

    def test_json_rejects_duplicates_nonfinite_oversize_and_symlink(self):
        for text in ['{"a":1,"a":2}', '{"a":NaN}', ' '* (q.MAX_FILE+1)]:
            with self.assertRaises((ValueError, q.GateError)): q.read_json(self.put('x.json', text))
        self.put('good.json', '{}'); (self.root/'bad.json').symlink_to(self.root/'good.json')
        with self.assertRaises(q.GateError): q.read_json(self.root/'bad.json')

    def test_paths_cannot_escape_or_follow_symlink(self):
        self.put('good/x', 'x'); (self.root/'link').symlink_to(self.root/'good', target_is_directory=True)
        for name in ['../x', '/tmp/x', 'good/../x', 'good//x', 'link/x']:
            with self.assertRaises(q.GateError): q.relative(self.root, name)
        self.assertEqual(q.relative(self.root, 'good/x').read_text(), 'x')

    def test_policy_redacts_secret_value_and_private_origin(self):
        secret = 'gh'+'p_'+'a'*30
        for text in [secret, 'https://'+'synthetic.example.ts.net/projects/one/']:
            self.put('source.txt', text)
            with self.assertRaises(q.GateError) as error: q.policy(self.root)
            self.assertNotIn(text, str(error.exception))
        self.put('source.txt', 'ordinary code'); q.policy(self.root)
        self.put('.env', 'synthetic=1')
        with self.assertRaises(q.GateError): q.policy(self.root)

    def test_digest_ignores_caches_but_detects_source_change(self):
        self.put('src/app.py', 'one'); before=q.source_digest(self.root)
        self.put('.gptclaw-cache/out', 'output'); self.assertEqual(before,q.source_digest(self.root))
        self.put('src/app.py', 'two'); self.assertNotEqual(before,q.source_digest(self.root))

    def workflow(self):
        return json.loads((ROOT/'templates/apps/releases/nextjs/1.1.0/.github/workflows/quality.yml').read_text())

    def test_generated_workflow_policy_and_faults(self):
        value=self.workflow(); q.workflow_policy(value)
        changes=[lambda v:v['permissions'].update(contents='write'),
                 lambda v:v['on'].update(pull_request_target={}),
                 lambda v:v['jobs']['quality']['steps'][0].update(uses='actions/checkout@main'),
                 lambda v:v['jobs']['quality']['steps'][0]['with'].update({'persist-credentials':True}),
                 lambda v:v['jobs']['required'].update({'if':'success()'}),
                 lambda v:v['jobs']['quality'].update({'timeout-minutes':0}),
                 lambda v:v['jobs']['quality']['steps'][1]['with'].update({'restore-keys':'any'}),
                 lambda v:v['jobs']['quality']['steps'][3]['with'].update({'path':'**/*'})]
        for change in changes:
            broken=copy.deepcopy(value);change(broken)
            with self.assertRaises(q.GateError):q.workflow_policy(broken)

    def test_updater_coverage_cap_and_registry_faults(self):
        root=ROOT/'templates/apps/releases/notes/1.1.0'; c=q.config(root)
        value=q.read_json(root/'.github/dependabot.yml');q.updater_policy(value,c)
        for change in [lambda x:x['updates'].pop(),lambda x:x['updates'][0].update({'open-pull-requests-limit':6}),lambda x:x['updates'][0].update({'registries':['private']})]:
            broken=copy.deepcopy(value);change(broken)
            with self.assertRaises(q.GateError):q.updater_policy(broken,c)

    def contract(self):
        return {'openapi':'3.1.0','paths':{'/notes':{'get':{'responses':{'200':{'description':'OK','content':{'application/json':{'schema':{'$ref':'#/components/schemas/Note'}}}}}}}},'components':{'schemas':{'Note':{'type':'object','properties':{'title':{'type':'string'}}}}}}

    def test_contract_additions_and_descriptions_are_compatible(self):
        old=self.contract();new=copy.deepcopy(old);new['paths']['/health']={'get':{'responses':{'200':{'description':'fine'}}}}
        new['paths']['/notes']['get']['summary']='New description'
        self.assertEqual(q.contract_changes(old,new),[])

    def test_contract_removal_required_input_and_schema_narrowing_fail(self):
        old=self.contract()
        for change in [lambda x:x['paths'].pop('/notes'),lambda x:x['paths']['/notes']['get'].update({'parameters':[{'name':'required','in':'query','required':True}]}),lambda x:x['components']['schemas']['Note']['properties']['title'].update({'maxLength':2})]:
            new=copy.deepcopy(old);change(new)
            if not new['paths']:new['paths']['/other']={'get':{'responses':{'200':{'description':'ok'}}}}
            self.assertTrue(q.contract_changes(old,new))

    def test_contract_references_reject_remote_and_missing(self):
        for ref in ['https://example.invalid/schema', '#/components/schemas/Missing']:
            value=self.contract();value['components']['schemas']['Note']={'$ref':ref}
            with self.assertRaises(q.GateError):q.resolve_refs(value)

    def assessment(self, text):
        self.put('migrations/one.py',text)
        digest=hashlib.sha256(b'migrations/one.py\0'+text.encode()).hexdigest()
        return {'source_digest':digest,'risk':'opaque','recovery':'Restore the separately verified project backup after excluding all writers.','reviewer':'project owner','backup_required':True}

    def test_migration_stale_assessment_and_opaque_risk(self):
        text='from alembic import op\ndef upgrade():\n    op.execute("DROP TABLE notes")\n'
        value=self.assessment(text); self.assertTrue(q.migration_assessment(self.root,['migrations/one.py'],value)['findings'])
        for change in [lambda x:x.update(risk='additive'),lambda x:x.update(source_digest='0'*64),lambda x:x.update(backup_required=False)]:
            broken=copy.deepcopy(value);change(broken)
            with self.assertRaises(q.GateError):q.migration_assessment(self.root,['migrations/one.py'],broken)

    def performance(self):
        profile={'runner':'synthetic','toolchain':'pinned','workload':'bounded','cache':'warm'}
        baseline={'profile':profile,'revision':'baseline','metrics':{'bundle':100}}
        sample={'profile':profile,'revision':'target','metrics':{'bundle':110}}
        budget={'bundle':{'unit':'bytes','absolute':120,'regression':.1}}
        return baseline,sample,budget

    def test_performance_boundaries_and_regressions(self):
        a,b,c=self.performance();self.assertEqual(q.compare_performance(a,b,c)['state'],'passed')
        b['metrics']['bundle']=111;self.assertEqual(q.compare_performance(a,b,c)['state'],'failed')
        c['bundle']['absolute']=109;self.assertEqual(q.compare_performance(a,b,c)['state'],'failed')

    def test_performance_missing_nonfinite_and_incomparable_fail(self):
        for change in [lambda a,b,c:b['metrics'].clear(),lambda a,b,c:b.update(profile={'runner':'other'}),lambda a,b,c:b['metrics'].update(bundle=float('nan')),lambda a,b,c:a['metrics'].update(bundle=0)]:
            a,b,c=self.performance();change(a,b,c)
            with self.assertRaises(q.GateError):q.compare_performance(a,b,c)

    def test_command_failure_propagates_and_redacts_tail(self):
        with self.assertRaises(q.GateError):q.execute([sys.executable,'-c','raise SystemExit(3)'],self.root)
        q.execute([sys.executable,'-c','pass'],self.root)

    def test_release_range_acceptance_manual_draft_and_no_publication(self):
        def git(*args):return subprocess.check_output(['git','-C',str(self.root),*args],text=True).strip()
        git('init','-q');git('config','user.name','Fixture');git('config','user.email','fixture@example.invalid')
        self.put('README.md','synthetic');git('add','.');git('commit','-qm','base');baseline=git('rev-parse','HEAD')
        self.put('acceptance.md','Status: accepted\n');git('add','.');git('commit','-qm','accepted');target=git('rev-parse','HEAD')
        value={'product':'Synthetic','version':'1.0.0','audience':'Developers','baseline':baseline,'target':target,'changes':[{'commit':target,'status':'accepted','category':'Fixed','summary':'Preserve a draft after a failed request.','evidence':'acceptance.md'}]}
        result=q.release_notes(self.root,value);self.assertEqual(result['state'],'draft');self.assertIn('Preserve a draft',result['text'])
        value['changes'][0]['status']='pending';result=q.release_notes(self.root,value);self.assertEqual(result['state'],'pending');self.assertNotIn('Preserve a draft',result['text'])
        value['baseline']=target
        with self.assertRaises(q.GateError):q.release_notes(self.root,value)
        self.assertEqual(git('rev-parse','HEAD'),target);self.assertEqual(git('tag'),'')


    def test_smoke_checks_ownership_source_content_and_redirects(self):
        root=self.root;self.put('source.txt','one')
        class Handler(BaseHTTPRequestHandler):
            def do_GET(inner):
                if inner.path.endswith('redirect'):
                    inner.send_response(302);inner.send_header('Location','https://example.invalid/');inner.end_headers();return
                inner.send_response(200);inner.end_headers();inner.wfile.write(b'expected')
            def log_message(*args):pass
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        self.addCleanup(server.server_close);self.addCleanup(server.shutdown)
        port=server.server_port
        value={'project':'one','revision':q.source_digest(root),'activation':'a'*32,'container':'gptclaw-quality-owned','base_url':f'http://127.0.0.1:{port}/projects/one/','paths':[{'path':'ready','contains':'expected'}],'expires':(dt.datetime.now(dt.timezone.utc)+dt.timedelta(minutes=1)).isoformat()}
        info={'Config':{'Labels':{'com.gptclaw.quality':'a'*32}},'State':{'Running':True},'NetworkSettings':{'Ports':{'8000/tcp':[{'HostIp':'127.0.0.1','HostPort':str(port)}]}}}
        inspect=lambda _:info
        self.assertEqual(q.smoke(root,value,inspect)['state'],'passed')
        changes=[lambda x:x.update(revision='0'*64),lambda x:x.update(activation='b'*32),lambda x:x.update(base_url='http://example.invalid/projects/one/'),lambda x:x['paths'][0].update(contains='wrong'),lambda x:x['paths'][0].update(path='redirect')]
        for change in changes:
            broken=copy.deepcopy(value);change(broken)
            with self.assertRaises(q.GateError):q.smoke(root,broken,inspect)

    def test_command_deadline_and_source_guard(self):
        with self.assertRaises(q.GateError):q.execute([sys.executable,'-c','import time;time.sleep(3)'],self.root,.05)


    def test_quality_contract_is_strict_and_inspection_does_not_execute(self):
        c={'schema_version':1,'template':'synthetic@1.0.0','components':{'app':{'root':'.','stack':'node','recipe':'checks/Containerfile','commands':{v:['pnpm',v] for v in q.VERBS}}},'integration':None,'budgets':{}}
        self.put('checks/Containerfile','FROM docker.io/library/node@sha256:'+'a'*64+'\n')
        self.put('quality.json',c);self.assertEqual(q.config(self.root),c)
        for change in [lambda x:x.update(schema_version=True),lambda x:x.update(extra=True),lambda x:x['components']['app']['commands'].pop('lint'),lambda x:x['components']['app'].update(root='../escape'),lambda x:x['components']['app']['commands'].update(test=['pnpm','bad\ncommand'])]:
            broken=copy.deepcopy(c);change(broken);self.put('quality.json',broken)
            with self.assertRaises(q.GateError):q.config(self.root)
        self.put('quality.json',c);self.put('checks/Containerfile','FROM node:latest\n')
        with self.assertRaises(q.GateError):q.config(self.root)

    def test_cleanup_refuses_foreign_container(self):
        from unittest.mock import patch
        runner=q.Containers(self.root,'podman',{});self.addCleanup(runner.auth.cleanup);runner.names.add('gptclaw-quality-synthetic')
        result=subprocess.CompletedProcess([],0,json.dumps([{'Config':{'Labels':{'com.gptclaw.quality':'foreign'}}}]),'')
        with patch.object(q.subprocess,'run',return_value=result),patch.object(q,'execute') as remove:
            with self.assertRaises(q.GateError):runner.cleanup()
            remove.assert_not_called()

    def test_sealer_refuses_published_and_excludes_nested_caches(self):
        script=ROOT/'scripts/seal-quality-releases.py'
        spec=importlib.util.spec_from_file_location('sealer',script);module=importlib.util.module_from_spec(spec)
        sys.path.insert(0,str(ROOT/'scripts'));spec.loader.exec_module(module)
        def git(*args):return subprocess.check_output(['git','-C',str(self.root),*args],text=True).strip()
        git('init','-q');git('config','user.name','Fixture');git('config','user.email','fixture@example.invalid')
        self.put('scripts/project_quality_core.py','synthetic runner')
        self.put('templates/quality/v1/browser.cjs','synthetic browser')
        self.put('templates/apps/releases/nextjs/1.0.0/checks/gptclaw_quality.py','published')
        git('add','.');git('commit','-qm','published');baseline=git('rev-parse','HEAD')
        self.put('templates/apps/releases/nextjs/1.1.0/checks/gptclaw_quality.py','unpublished')
        self.put('templates/apps/releases/nextjs/1.1.0/.cache/metadata.json','synthetic cache')
        self.put('templates/apps/releases/nextjs/1.1.0/node_modules/ignored.js','synthetic dependency')
        self.put('config/templates/v1.json',{'releases':[{'id':'nextjs','version':'1.1.0','files':[]}]})
        module.seal(self.root,'1.1.0',baseline)
        data=q.read_json(self.root/'config/templates/v1.json')['releases'][0]
        self.assertEqual({p['source'] for p in data['files']},{'checks/gptclaw_quality.py','checks/browser.cjs'})
        self.put('config/templates/v1.json',{'releases':[{'id':'nextjs','version':'1.0.0','files':[]}]})
        with self.assertRaises(ValueError):module.seal(self.root,'1.0.0',baseline)
        self.assertEqual((self.root/'templates/apps/releases/nextjs/1.0.0/checks/gptclaw_quality.py').read_text(),'published')


if __name__=='__main__':unittest.main()
