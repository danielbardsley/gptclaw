#!/usr/bin/env python3
"""Real isolated Git, synthetic broker, concurrent processes and failure boundaries."""
import copy
import hashlib
import json
import multiprocessing
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import unittest
from unittest.mock import patch

sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import private_apps as app
import project_worktrees as w
import repository_credentials as broker
import dashboard_inventory as inventory
import gptclawctl as cli
import test_repository_credentials as credential_fixtures


def hold(key,ready):
    with app.locked(key):
        ready.send('locked')
        signal.pause()


def interrupted_create(root,base,ready):
    real=w.git
    def pause(root,*args,**kwargs):
        if args[:2]==('worktree','add'):
            ready.send('intent-recorded');signal.pause()
        return real(root,*args,**kwargs)
    with patch.object(w,'git',side_effect=pause):w.create(root,'interrupted','producer',base)


def edit(path,content,ready):
    (Path(path)/'parallel.txt').write_text(content)
    subprocess.run(['git','-C',str(path),'add','parallel.txt'],check=True,capture_output=True)
    ready.send('done')


class Tests(unittest.TestCase):
    def setUp(self):
        fixture=credential_fixtures.Tests('test_workflow_preflight_precedes_any_remote_operation')
        fixture.setUp();self.addCleanup(fixture.doCleanups);self.fixture=fixture
        fixture.first();self.root=fixture.projects/'first'
        # The synthetic application fixture is integrated at its remote-main observation.
        subprocess.run(['git','-C',str(self.root),'update-ref','refs/remotes/origin/main','HEAD'],check=True)
        (self.root/'.git/hooks').mkdir(exist_ok=True)
        self.base=w.plan(self.root,'one','producer')['base_commit']

    def create(self,task='one',owner='producer'):
        return w.create(self.root,task,owner,self.base)

    def commit(self,value):
        path=Path(value['path']);(path/'task.txt').write_text('synthetic task source\n')
        subprocess.run(['git','-C',str(path),'add','task.txt'],check=True)
        subprocess.run(['git','-c','user.name=Fixture','-c','user.email=fixture@example.invalid','-C',str(path),'commit','-m','task'],check=True,capture_output=True)
        return w.text(path,'rev-parse','HEAD')

    def handoff(self,value,**kwargs):
        return w.handoff(self.root,value['task'],value['owner'],value['generation'],**kwargs)

    def error(self,code,call,*args,**kwargs):
        with self.assertRaises(app.AppError) as result:call(*args,**kwargs)
        self.assertEqual(result.exception.code,code)

    def test_read_only_plan_and_two_dirty_isolated_checkouts(self):
        (self.root/'README.md').write_text('dirty canonical bytes')
        (self.root/'owner.txt').write_text('untracked bytes')
        before=w.git(self.root,'status','--porcelain=v1','-z')[0]
        files={p:p.read_bytes() for p in [self.root/'README.md',self.root/'owner.txt',self.root/'.git/index']}
        receipt_before=list(w.store().glob('*'))
        planned=w.plan(self.root,'one','producer')
        self.assertEqual(planned['base_observation'],'local-only')
        self.assertEqual(list(w.store().glob('*')),receipt_before);self.assertFalse(w.sources().exists())
        one=self.create();two=self.create('two')
        self.assertNotEqual(one['branch'],two['branch']);self.assertNotEqual(one['path'],two['path'])
        self.assertEqual(one,self.create());self.assertEqual(w.git(self.root,'status','--porcelain=v1','-z')[0],before)
        self.assertEqual({p:p.read_bytes() for p in files},files)
        self.assertFalse((Path(one['path'])/'owner.txt').exists())

    def test_actual_parallel_indexes_and_files(self):
        one=self.create();two=self.create('two');processes=[]
        for value,content in [(one,'one'),(two,'two')]:
            parent,child=multiprocessing.Pipe();p=multiprocessing.get_context('fork').Process(target=edit,args=(value['path'],content,child));p.start();processes.append((p,parent))
        for p,parent in processes:self.assertTrue(parent.poll(5));self.assertEqual(parent.recv(),'done');p.join(5);self.assertEqual(p.exitcode,0);parent.close()
        self.assertEqual((Path(one['path'])/'parallel.txt').read_text(),'one')
        self.assertEqual((Path(two['path'])/'parallel.txt').read_text(),'two')
        self.assertFalse((self.root/'parallel.txt').exists())
        self.assertIn(b'parallel.txt',w.git(Path(one['path']),'diff','--cached','--name-only','-z')[0])

    def test_busy_and_killed_lock_releases_without_takeover(self):
        proposed=w.plan(self.root,'one','producer');parent,child=multiprocessing.Pipe()
        p=multiprocessing.get_context('fork').Process(target=hold,args=('worktree-project-'+proposed['identity']['key'],child));p.start()
        try:
            self.assertTrue(parent.poll(5));parent.recv();self.error('busy',self.create)
        finally:p.kill();p.join(5);parent.close()
        value=self.create();self.assertEqual(value['generation'],1)
        self.error('worktree-drift',w.resume,self.root,'one','other',1,'consumer')

    def test_busy_precedes_transient_git_config_observation(self):
        identity=w.canonical(self.root);config=self.root/'.git/config';raw=config.read_bytes()
        with app.locked('worktree-project-'+identity['key']):
            try:
                config.write_bytes(b'transient helper refresh')
                self.error('busy',self.create)
            finally:config.write_bytes(raw)
        self.assertEqual(self.create()['state'],'active')

    def test_other_project_lock_independence(self):
        self.fixture.factory.auto_include=True
        broker.create('second',str(self.fixture.projects/'second'),canary=False)
        second=self.fixture.projects/'second';subprocess.run(['git','-C',str(second),'update-ref','refs/remotes/origin/main','HEAD'],check=True)
        one=w.plan(self.root,'one','producer');two=w.plan(second,'one','producer')
        with app.locked('worktree-project-'+one['identity']['key']):
            value=w.create(second,'one','producer',two['base_commit']);self.assertEqual(value['state'],'active')

    def test_invalid_input_and_existing_collision(self):
        for task in ['../bad','-option','secret/path','bad--name']:
            self.error('worktree-policy',w.plan,self.root,task,'producer')
        self.error('worktree-drift',w.create,self.root,'one','producer','0'*40)
        proposed=w.plan(self.root,'one','producer');path=Path(proposed['path']);path.mkdir(parents=True);(path/'preserve').write_text('keep')
        self.error('worktree-policy',self.create);self.assertEqual((path/'preserve').read_text(),'keep')

    def test_occupied_branch_and_merge_state(self):
        proposed=w.plan(self.root,'one','producer')
        subprocess.run(['git','-C',str(self.root),'branch',proposed['branch']],check=True)
        self.error('worktree-policy',self.create)
        (self.root/'.git/MERGE_HEAD').write_text(self.base)
        self.error('worktree-policy',w.plan,self.root,'two','producer')

    def test_unknown_config_hook_and_submodule_are_not_executed(self):
        config=self.root/'.git/config';original=config.read_bytes()
        config.write_bytes(original+b'\n[core]\n\thooksPath = /unknown\n')
        self.error('worktree-policy',w.plan,self.root,'one','producer');config.write_bytes(original)
        hook=self.root/'.git/hooks/post-checkout';hook.write_text('#!/bin/sh\nexit 0\n');hook.chmod(0o700)
        self.error('worktree-policy',w.plan,self.root,'one','producer');self.assertTrue(hook.exists());hook.unlink()
        (self.root/'.gitmodules').write_text('synthetic unsupported submodule')
        self.error('worktree-policy',w.plan,self.root,'one','producer')

    def test_recognized_hook_migrates_and_task_never_verifies_canonical(self):
        launcher=app.provider_bundle()/'scripts/gptclawctl'
        hook=self.root/'.git/hooks/pre-commit';hook.write_text('#!/usr/bin/env bash\nset -euo pipefail\nexec '+str(launcher)+' verify --project-root '+str(self.root)+'\n');hook.chmod(0o700)
        value=self.create();self.assertEqual(hook.read_text(),w.hook_text(launcher))
        self.assertIn('$(git rev-parse --show-toplevel)',hook.read_text())
        with patch.object(app,'run_in_app',side_effect=AssertionError('must not run')):
            self.error('worktree-source-only',app.quality_app,Path(value['path']),'verify')

    def test_handoff_consumer_and_stale_owner(self):
        value=self.create();head=self.commit(value)
        out=self.handoff(value,checks=[{'check':'source-test','result':'passed','source':'owner-reported'}],remaining=['runtime-check'])
        self.assertEqual(out['head'],head);self.assertEqual(out['handoff']['publication'],'not-observed')
        self.assertEqual(out['state'],'handed-off')
        new=w.resume(self.root,'one','producer',out['generation'],'consumer');self.assertEqual(new['owner'],'consumer')
        self.error('worktree-drift',w.handoff,self.root,'one','producer',1)
        self.assertEqual(w.text(Path(new['path']),'rev-parse','HEAD'),head)
        self.assertFalse((self.root/'task.txt').exists())

    def test_resume_preserves_dirty_work_and_ref_drift_stops(self):
        value=self.create();path=Path(value['path']);(path/'dirty.txt').write_text('keep')
        out=self.handoff(value);self.assertTrue(out['handoff']['dirty'])
        new=w.resume(self.root,'one','producer',out['generation'],'consumer');self.assertEqual((path/'dirty.txt').read_text(),'keep')
        self.commit(new)
        self.error('worktree-drift',w.resume,self.root,'one','consumer',new['generation'],'third')

    def test_cleanup_active_dirty_ignored_and_unpublished_are_retained(self):
        value=self.create();self.error('worktree-retained',w.cleanup,self.root,'one','producer',1,value['head'])
        self.commit(value);out=self.handoff(value);path=Path(value['path'])
        with patch.object(w,'remote_head',return_value=False):self.error('worktree-retained',w.cleanup,self.root,'one','producer',out['generation'],out['head'],True)
        (path/'untracked.txt').write_text('keep')
        self.error('worktree-retained',w.cleanup,self.root,'one','producer',out['generation'],out['head'],True)
        (path/'untracked.txt').unlink();(path/'node_modules').mkdir();(path/'node_modules/private.txt').write_text('synthetic ignored bytes')
        self.error('worktree-retained',w.cleanup,self.root,'one','producer',out['generation'],out['head'],True)
        self.assertTrue(path.exists())

    def test_verified_retention_cleanup_preserves_branch_other_checkout_and_receipt(self):
        value=self.create();other=self.create('two');out=self.handoff(value)
        preview=w.cleanup(self.root,'one','producer',out['generation'],out['head'])
        self.assertEqual(preview['state'],'cleanup-planned');self.assertTrue(Path(value['path']).exists())
        applied=w.cleanup(self.root,'one','producer',out['generation'],out['head'],True)
        self.assertEqual(applied['state'],'removed');self.assertFalse(Path(value['path']).exists());self.assertTrue(Path(other['path']).exists())
        self.assertEqual(w.text(self.root,'rev-parse','refs/heads/'+value['branch']),value['head'])
        self.assertEqual(w.read(value['identity'],'one')['state'],'removed')

    def test_lost_create_response_reconciles_same_allocation(self):
        real=w.persist
        def fail(value):
            if value['state']=='active':raise OSError('synthetic response loss')
            return real(value)
        with patch.object(w,'persist',side_effect=fail):
            with self.assertRaises(OSError):self.create()
        self.assertEqual(w.status(self.root,'one')['recovery'],'interrupted')
        value=self.create();self.assertEqual(value['state'],'active');self.assertEqual(len(w.listings(self.root)),2)

    def test_interrupted_intent_before_git_and_branch_only_recover(self):
        real=w.git
        def fail(root,*args,**kwargs):
            if args[:2]==('worktree','add'):raise OSError('synthetic interruption')
            return real(root,*args,**kwargs)
        with patch.object(w,'git',side_effect=fail):
            with self.assertRaises(OSError):self.create()
        value=w.read(w.canonical(self.root),'one')
        subprocess.run(['git','-C',str(self.root),'branch',value['branch'],self.base],check=True)
        self.assertEqual(self.create()['state'],'active')

    def test_lost_removal_response_reconciles_tombstone(self):
        value=self.create();out=self.handoff(value);real=w.persist
        def fail(value):
            if value['state']=='removed':raise OSError('synthetic response loss')
            return real(value)
        with patch.object(w,'persist',side_effect=fail):
            with self.assertRaises(OSError):w.cleanup(self.root,'one','producer',out['generation'],out['head'],True)
        result=w.cleanup(self.root,'one','producer',out['generation'],out['head'],True)
        self.assertEqual(result['state'],'removed')

    def test_tampering_symlink_moved_admin_and_index_lock(self):
        value=self.create();path=Path(value['path']);admin=Path(value['identity']['common'])/'worktrees'/value['allocation_id']
        (admin/'index.lock').write_text('busy');self.error('worktree-drift',self.handoff,value);(admin/'index.lock').unlink()
        raw=(path/'.git').read_bytes();(path/'.git').write_text('gitdir: /tmp/foreign\n')
        self.error('worktree-drift',w.observe,value);(path/'.git').write_bytes(raw)
        moved=path.with_name('moved');path.rename(moved)
        self.error('worktree-drift',w.observe,value);self.assertTrue(w.managed(moved));self.error('worktree-source-only',w.guard,moved)
        moved.rename(path)
        value['path']=str(self.root);app.save(w.receipt_path(value['allocation_id']),value)
        self.error('worktree-policy',w.read,value['identity'],'one')

    def test_credentials_membership_denial_before_token(self):
        value=self.create();w.validate_invocation(self.root,Path(value['path']))
        before=self.fixture.factory.token_count
        broker.disable(self.root)
        self.error('credential-disabled',w.validate_invocation,self.root,Path(value['path']))
        self.assertEqual(before,self.fixture.factory.token_count)

    def test_managed_runtime_inventory_and_direct_entry_guards(self):
        value=self.create();path=Path(value['path'])
        import project_dependencies as deps
        import project_database as db
        import project_groups as groups
        for call,args in [(app.target,(path,)),(deps.context,(path,)),(db.dispatch,(path,'init')),(groups.component_target,(path/'api',))]:
            self.error('worktree-source-only',call,*args)
        snapshot=inventory.Scanner(str(self.fixture.projects)).scan()
        self.assertFalse(any('.gptclaw-worktrees' in row.get('root','') for row in snapshot['rows']))

    def test_remote_publication_checked_not_assumed_and_tokens_revoked(self):
        value=self.create();self.commit(value)
        head=w.text(Path(value['path']),'rev-parse','HEAD')
        self.fixture.git(Path(value['path']),'push','https://github.com/'+broker.repos.ACCOUNT+'/first.git','HEAD:refs/heads/'+value['branch'])
        out=self.handoff(value,published=True)
        self.assertEqual(out['head'],head);self.assertEqual(out['handoff']['publication'],'remote-head-verified')
        self.assertEqual(self.fixture.factory.calls[-1][1],'/installation/token')
        self.assertEqual(self.fixture.factory.calls[-2][3],[101])

    def test_actual_killed_mutator_recovers_durable_intent(self):
        parent,child=multiprocessing.Pipe()
        p=multiprocessing.get_context('fork').Process(target=interrupted_create,args=(self.root,self.base,child));p.start()
        try:
            self.assertTrue(parent.poll(10));self.assertEqual(parent.recv(),'intent-recorded')
            self.assertEqual(w.status(self.root,'interrupted')['state'],'interrupted')
        finally:p.kill();p.join(5);parent.close()
        value=w.create(self.root,'interrupted','producer',self.base)
        self.assertEqual(value['state'],'active');self.assertEqual(len(w.listings(self.root)),2)

    def test_preserve_existing_upstream_config_and_known_ignored_cache(self):
        subprocess.run(['git','-C',str(self.root),'config','branch.codex/existing.remote','origin'],check=True)
        subprocess.run(['git','-C',str(self.root),'config','branch.codex/existing.merge','refs/heads/codex/existing'],check=True)
        cache=self.root/'api/.gptclaw-cache/uv/sdists-v10/.git';cache.mkdir(parents=True)
        value=self.create();self.assertEqual(value['state'],'active');self.assertTrue(cache.exists())

    def test_actual_hook_process_refuses_task_before_runtime(self):
        launcher=app.provider_bundle()/'scripts/gptclawctl'
        hook=self.root/'.git/hooks/pre-commit';hook.write_text(w.hook_text(launcher));hook.chmod(0o700)
        value=self.create()
        completed=subprocess.run([str(hook)],cwd=value['path'],capture_output=True,text=True,timeout=10)
        self.assertEqual(completed.returncode,1)
        self.assertEqual(json.loads(completed.stdout)['error'],'worktree-source-only')

    def test_forged_membership_unknown_worktree_config_and_moved_inventory(self):
        value=self.create();path=Path(value['path']);admin=Path(value['identity']['common'])/'worktrees'/value['allocation_id']
        before=self.fixture.factory.token_count
        (admin/'config.worktree').write_text('[credential]\nhelper=unknown\n')
        self.error('worktree-policy',w.validate_invocation,self.root,path);(admin/'config.worktree').unlink()
        self.assertEqual(before,self.fixture.factory.token_count)
        moved=self.fixture.projects/'moved-task';path.rename(moved)
        snapshot=inventory.Scanner(self.fixture.projects).scan()
        self.assertFalse(any(row['location']=='moved-task' for row in snapshot['rows']))
        self.error('worktree-drift',w.validate_invocation,self.root,moved)

    def test_squash_retention_revalidates_pr_after_merge(self):
        value=self.create();head=self.commit(value)
        out=self.handoff(value)
        out['handoff']['pr']={'number':23,'head':head,'merge':None,'state':'open'}
        w.persist(out)
        merged={'number':23,'head':head,'merge':self.base,'state':'merged'}
        with patch.object(w,'pr_evidence',return_value=merged),patch.object(w,'remote_head',side_effect=AssertionError('canonical squash suffices')):
            preview=w.cleanup(self.root,'one','producer',out['generation'],head)
            self.assertEqual(preview['retention'],'canonical-squash')
        with patch.object(w,'pr_evidence',return_value={**merged,'state':'closed','merge':None}),patch.object(w,'remote_head',return_value=False):
            self.error('worktree-retained',w.cleanup,self.root,'one','producer',out['generation'],head)

    def test_nonforge_lexical_refusal_does_not_execute_or_read(self):
        import io
        output=io.StringIO()
        with patch.object(cli.os,'getuid',return_value=1234),patch.object(w,'guard',side_effect=AssertionError('no filesystem read')),patch('sys.stdout',output):
            result=cli.main(['verify','--project-root','/tmp/.gptclaw-worktrees/synthetic/task'])
        self.assertEqual(result,1);self.assertEqual(json.loads(output.getvalue())['error'],'worktree-source-only')

    def test_closed_stdout_timeout_returns_fixed_error(self):
        real=subprocess.Popen
        def spawn(*args,**kwargs):return real([sys.executable,'-c','import os,time; os.close(1); time.sleep(30)'],**kwargs)
        with patch.object(w.subprocess,'Popen',side_effect=spawn):
            self.error('timeout',w.git,self.root,'status',timeout=.2)

    def test_timeout_terminates_descendant_group(self):
        # Controlled subprocess spy spawns a child that holds the Git stdout pipe.
        real=subprocess.Popen;pidfile=self.fixture.base/'child.pid'
        script='import os,subprocess,time; p=subprocess.Popen(["sleep","30"]); open("'+str(pidfile)+'","w").write(str(p.pid)); time.sleep(30)'
        def spawn(*args,**kwargs):
            process=real([sys.executable,'-c',script],**kwargs)
            deadline=time.monotonic()+10
            while not pidfile.exists() and time.monotonic()<deadline:time.sleep(.01)
            if not pidfile.exists():
                os.killpg(process.pid,signal.SIGKILL);process.wait();raise AssertionError('fixture startup failed')
            return process
        with patch.object(w.subprocess,'Popen',side_effect=spawn):self.error('timeout',w.git,self.root,'status',timeout=.2)
        pid=int(pidfile.read_text());status=Path('/proc')/str(pid)/'stat'
        # SIGKILL delivery is asynchronous; allow the kernel a bounded scheduling turn.
        deadline=time.monotonic()+2
        while True:
            try:state=status.read_text().split()[2]
            except FileNotFoundError:break
            if state=='Z':break
            self.assertLess(time.monotonic(),deadline,'descendant survived timeout cleanup')
            time.sleep(.01)


if __name__=='__main__':unittest.main(verbosity=2)
