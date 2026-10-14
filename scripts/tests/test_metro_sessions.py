#!/usr/bin/env python3
"""Isolated sticky leases, owned cleanup and supervised deadline/admission tests."""
import copy
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import private_apps as app
import metro_sessions as metro
import metro_state


class SessionTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        self.projects=Path(temp.name)/'projects';self.projects.mkdir()
        self.patch(app,'PROJECTS',self.projects);self.patch(app,'STORE',self.projects/'.runtime');self.patch(metro,'UNITS',Path(temp.name)/'units')
        self.root=self.projects/'fixture';self.root.mkdir()
        self.patch(metro.time,'time',lambda:1800000000)
        self.value={'schema_version':1,'adapter':'metro-v1','project':'fixture','root':str(self.root),
                    'canonical_key':'1'*64,'name':'gptclaw-metro-fixture','generation':'2'*32,'token':'3'*32,
                    'image':'sha256:'+'4'*64,'input_digest':'5'*64,'policy_digest':'6'*64,'unit_digest':'7'*64,
                    'metro_port':18600,'proxy_port':18601,'origin':'https://fixture.tail123.ts.net:8443',
                    'phase':'running','started_at':1800000000,'expires_at':1800000300,
                    'operation_id':'8'*32,'operation_result':'passed','observations':{
                    'process':{'state':'up','observed_at':1800000000},'protocol':{'state':'ready','observed_at':1800000000},
                    'route':{'state':'pending','observed_at':None}}}
    def patch(self,obj,name,value):
        p=patch.object(obj,name,value);p.start();self.addCleanup(p.stop)
    def identity(self,project='fixture'):
        return {'project':project,'key':'1'*64}

    def test_established_protocol_timeout_preserves_owned_process_generation_and_lease(self):
        current=copy.deepcopy(self.value)
        with patch.object(metro.protocol,'request',side_effect=app.AppError('health')),patch.object(
                metro.time,'monotonic',return_value=500):
            self.assertTrue(metro.observe_protocol(self.value,current,300,True))
        self.assertEqual(current['observations']['protocol']['state'],'failed')
        self.assertEqual(current['observations']['process'],self.value['observations']['process'])
        for field in ['phase','generation','expires_at','operation_result']:
            self.assertEqual(current[field],self.value[field])
        current['observations']['route']={'state':'verified','observed_at':1800000000}
        with patch.object(metro_state.time,'time',return_value=1800000000):
            result=metro_state.descriptor(current,project='fixture',root=self.root,
                    canonical_key=current['canonical_key'],input_digest=current['input_digest'])
        self.assertEqual(result['state'],'failed')
        self.assertFalse(result['transport_available']);self.assertIsNone(result['origin'])

    def test_first_protocol_startup_timeout_still_has_a_finite_gate(self):
        current=copy.deepcopy(self.value);current.update(phase='starting',operation_result='running')
        with patch.object(metro.protocol,'request',side_effect=app.AppError('health')),patch.object(
                metro.time,'monotonic',return_value=500),self.assertRaises(app.AppError) as error:
            metro.observe_protocol(self.value,current,300,False)
        self.assertEqual(error.exception.code,'health')
        self.assertEqual(current['observations']['protocol']['state'],'failed')

    def test_initial_protocol_retry_does_not_publish_ready(self):
        current=copy.deepcopy(self.value);current.update(phase='starting',operation_result='running')
        with patch.object(metro.protocol,'request',side_effect=app.AppError('health')),patch.object(
                metro.time,'monotonic',return_value=200):
            self.assertFalse(metro.observe_protocol(self.value,current,300,False))
        self.assertEqual(current['phase'],'starting')
        self.assertEqual(current['operation_result'],'running')

    def test_protocol_recovers_in_place_without_extending_expiry(self):
        current=copy.deepcopy(self.value);current['observations']['protocol']['state']='failed'
        with patch.object(metro.protocol,'request',return_value={}):
            self.assertTrue(metro.observe_protocol(self.value,current,300,True))
        self.assertEqual(current['observations']['protocol']['state'],'ready')
        self.assertEqual(current['expires_at'],self.value['expires_at'])
        self.assertEqual(current['generation'],self.value['generation'])

    def test_explicit_rehearsal_lifetime_only_shortens_declared_bound(self):
        source={'metro':{'ttl_seconds':300}}
        self.assertEqual(metro.lifetime(source),300)
        self.assertEqual(metro.lifetime(source,90),90)
        for value in [59,301,True,90.0,'90']:
            with self.assertRaises(app.AppError):metro.lifetime(source,value)

    def test_independent_sticky_ports_and_origins(self):
        with patch.object(app,'available',return_value=True):
            one=metro.reserve(self.root,self.identity());two=metro.reserve(self.projects/'other',self.identity('other'))
            again=metro.reserve(self.root,self.identity())
        self.assertEqual(one,again);self.assertNotEqual(one,two);self.assertEqual(one,(18600,18601,8443))
        self.assertEqual(two,(18602,18603,8444));self.assertEqual(len(metro.slots()),2)
    def test_root_and_canonical_reassignment_rejected_without_recycling(self):
        with patch.object(app,'available',return_value=True):metro.reserve(self.root,self.identity())
        before=(app.STORE/'metro/registry.json').read_bytes()
        with self.assertRaises(app.AppError):metro.reserve(self.projects/'other',self.identity())
        self.assertEqual(before,(app.STORE/'metro/registry.json').read_bytes())
    def test_collision_never_removes_foreign_listener(self):
        with patch.object(app,'available',return_value=False),patch.object(app,'command',side_effect=AssertionError('no cleanup')),self.assertRaises(app.AppError):metro.reserve(self.root,self.identity())
    def test_unknown_registry_shapes_and_duplicate_slots_fail(self):
        path=app.STORE/'metro';path.mkdir(parents=True)
        for value in [{'schema_version':True,'entries':{}},{'schema_version':1,'entries':{'fixture':{'root':str(self.root),'canonical_key':'1'*64,'slot':False}}}]:
            app.save(path/'registry.json',value)
            with self.assertRaises(app.AppError):metro.slots()
    def test_owned_state_roundtrip_and_wrong_root_denial(self):
        metro.save(self.value);self.assertEqual(metro.load('fixture',self.root),self.value)
        with self.assertRaises(app.AppError):metro.load('fixture',self.projects/'other')
    def test_control_unknown_environment_and_source_path_are_rejected(self):
        metro.save(self.value)
        data={'schema_version':2,'project':'fixture','root':str(self.root),'generation':'2'*32,
              'inputs':{p:'0'*64 for p in metro.FILES},'source':str(metro.directory('fixture')/'sources'/('2'*32)),
              'provider':str(app.REPO),'audit':None,'root_identity':[1,2],'mount_identities':{'src':None,'assets':None,'node_modules':[1,2]}}
        app.save(metro.directory('fixture')/'control.json',data);self.assertEqual(metro.control(self.value),data)
        for field,value in [('environment',{'SECRET':'synthetic'}),('source','/home/forge')]:
            changed=copy.deepcopy(data);changed[field]=value;app.save(metro.directory('fixture')/'control.json',changed)
            with self.assertRaises(app.AppError):metro.control(self.value)
    def test_replaced_bound_directory_is_detected_without_retargeting(self):
        for name in ['src','assets','node_modules']:(self.root/name).mkdir()
        before=metro.mount_identities(self.root)
        (self.root/'src').rename(self.root/'src-retained')
        (self.root/'src').mkdir()
        after=metro.mount_identities(self.root)
        self.assertNotEqual(before['src'],after['src'])
        self.assertEqual(before['node_modules'],after['node_modules'])
        self.assertTrue((self.root/'src-retained').is_dir())

    def test_unit_has_bounded_supervision_and_immutable_generation(self):
        text=metro.unit_text(self.value,app.STORE/'providers'/('9'*64))
        for fragment in ['StartLimitIntervalSec=300','StartLimitBurst=3','Restart=on-failure','TimeoutStopSec=30','MemoryMax=192M','CPUQuota=25%','NoNewPrivileges=true','--generation '+self.value['generation']]:self.assertIn(fragment,text)
        self.assertIn('/providers/'+('9'*64)+'/scripts/gptclawctl',text)
        self.assertNotIn('/bin/sh',text);self.assertNotIn('sudo',text)
    def test_cleanup_only_owned_resources(self):
        calls=[]
        with patch.object(metro,'ownership',side_effect=['owned','absent','absent','owned','absent']),patch.object(app,'command',side_effect=lambda argv,**kw:calls.append(argv)):metro.cleanup(self.value)
        self.assertEqual(calls,[['podman','stop','--time','20','gptclaw-metro-fixture'],['podman','network','rm','gptclaw-metro-fixture-net']])
    def test_foreign_cleanup_is_preserved_and_not_killed(self):
        with patch.object(metro,'ownership',return_value='foreign'),patch.object(app,'command') as command,self.assertRaises(app.AppError):metro.cleanup(self.value)
        command.assert_not_called()
    def test_active_or_unknown_session_blocks_source_mutation(self):
        metro.save(self.value)
        with self.assertRaises(app.AppError):metro.assert_stopped(self.root,'fixture')
        self.value['phase']='recovery-required';metro.save(self.value)
        with self.assertRaises(app.AppError):metro.assert_stopped(self.root,'fixture')
        self.value['phase']='stopped';metro.save(self.value)
        with patch.object(metro,'ownership',return_value='absent'),patch.object(metro,'preflight_unit'):metro.assert_stopped(self.root,'fixture')
    def test_live_revocation_blocks_same_frozen_approved_policy(self):
        policy={'scope':'synthetic-exact-policy'}
        with patch.object(metro.security,'read_policy',return_value=policy):
            self.assertEqual(metro.admitted(),policy)
            path=metro.revoke_path(metro.digest(policy));path.parent.mkdir(parents=True);app.save(path,{'revoked':True})
            with self.assertRaises(app.AppError):metro.admitted()
    def simulate_supervisor(self,revoked=False):
        self.value['phase']='starting';self.value['input_digest']=metro.digest({p:'0'*64 for p in metro.FILES})
        self.value['started_at']=1800000000;self.value['expires_at']=1800000300;metro.save(self.value)
        clock={'now':1800000000};commands=[];resources={}
        (self.root/'node_modules').mkdir();(self.root/'pnpm-lock.yaml').write_text('synthetic')
        self.patch(metro.spike,'require_operator',lambda:None)
        self.patch(app,'target',lambda root:(self.root,{'schema_version':6,'project':{'id':'fixture'}}))
        self.patch(metro,'verify_unit',lambda *args:None)
        self.patch(metro,'receipt_for_root',lambda *args:(self.root,metro.load('fixture',self.root)))
        self.patch(metro.worktrees,'canonical',lambda *args:{'key':'1'*64,'root_identity':[1,2]})
        self.patch(metro.worktrees,'owned',lambda *args:[1,2])
        data={'inputs':{p:'0'*64 for p in metro.FILES},'source':str(self.projects/'view'),'audit':None,'root_identity':[1,2],'mount_identities':{'src':None,'assets':None,'node_modules':[1,2]}}
        self.patch(metro,'control',lambda *args:data);self.patch(metro,'hashes',lambda *args:data['inputs'])
        self.patch(metro.spike,'source_inventory',lambda *args:{})
        count={'admission':0}
        def admitted(*args):
            count['admission']+=1
            if revoked and count['admission']>=3:raise app.AppError('conflict')
            return {'scope':'synthetic'}
        self.patch(metro,'admitted',admitted)
        self.patch(metro.security,'evaluate',lambda *args:{'exact':'synthetic'})
        self.patch(metro.time,'time',lambda:clock['now'])
        def command(argv,**kw):
            commands.append(argv)
            if argv[:2]==['podman','run']:return SimpleNamespace(returncode=0,stdout='{}')
            if argv[:3]==['podman','network','create']:resources[argv[-1]]='owned'
            if argv[:2]==['podman','stop']:resources.pop(argv[-1],None)
            if argv[:3]==['podman','network','rm']:resources.pop(argv[-1],None)
            return SimpleNamespace(returncode=0,stdout='')
        self.patch(app,'command',command)
        self.patch(metro,'ownership',lambda kind,name,token:resources.get(name,'absent'))
        def runner(argv):
            commands.append(argv);resources[self.value['name']]='owned'
            if not revoked:clock['now']=1800000301
            return SimpleNamespace(process=SimpleNamespace(poll=lambda:None),finish=lambda:None)
        self.patch(metro.spike,'EphemeralOutput',runner)
        service=SimpleNamespace(thread=SimpleNamespace(is_alive=lambda:True),failure=False,stop=lambda:commands.append(['proxy-stop']))
        service.start=lambda:service
        self.patch(metro.proxy,'Service',lambda value,loader:service)
        result=metro.supervise(self.root,self.value['generation'])
        self.assertEqual(resources,{})
        return result,commands
    def test_supervision_expiry_closes_owned_resources_without_source_mutation(self):
        result,commands=self.simulate_supervisor();self.assertEqual(result['state'],'expired')
        value=metro.load('fixture',self.root);self.assertEqual(value['phase'],'expired')
        sdk=next(c for c in commands if 'node_modules/expo/bin/cli' in c)
        self.assertIn('--timeout=300',sdk);self.assertIn('--offline',sdk);self.assertNotIn('--lan',sdk)
        self.assertIn(['proxy-stop'],commands)
    def test_supervision_revokes_on_changed_or_withdrawn_admission(self):
        result,commands=self.simulate_supervisor(revoked=True);self.assertEqual(result['state'],'failed')
        self.assertTrue(any(c[:2]==['podman','stop'] for c in commands))
        self.assertEqual(metro.load('fixture',self.root)['observations']['process']['state'],'down')
        failure=app.read_json(metro.directory('fixture')/('failure-'+self.value['generation']+'.json'))
        self.assertEqual(failure,{'schema_version':1,'generation':self.value['generation'],'stage':'supervision','code':'conflict'})
        self.assertNotIn(self.value['token'],json.dumps(failure))
    def test_partial_foreign_cleanup_still_closes_other_owned_handles(self):
        resources={'gptclaw-metro-fixture':'foreign','gptclaw-metro-fixture-audit':'owned','gptclaw-metro-fixture-net':'owned'}
        calls=[]
        def command(argv,**kwargs):calls.append(argv);resources.pop(argv[-1],None)
        with patch.object(metro,'ownership',side_effect=lambda kind,name,token:resources.get(name,'absent')),patch.object(app,'command',side_effect=command),self.assertRaises(app.AppError):
            metro.cleanup(self.value)
        self.assertEqual(resources,{'gptclaw-metro-fixture':'foreign'})
        self.assertEqual(len(calls),2);self.assertFalse(any(c[-1]=='gptclaw-metro-fixture' for c in calls))

    def test_stopped_receipt_with_restarting_unit_blocks_source_mutation(self):
        self.value['phase']='failed';metro.save(self.value)
        path=metro.unit_path(self.value);path.parent.mkdir();path.write_text('synthetic')
        with patch.object(metro,'ownership',return_value='absent'),patch.object(metro,'verify_unit'),patch.object(metro,'unit_fields',return_value={'ActiveState':'activating','SubState':'auto-restart'}),self.assertRaises(app.AppError):
            metro.assert_stopped(self.root,'fixture')

    def test_unowned_loaded_unit_blocks_start_before_writes(self):
        self.patch(metro.spike,'require_operator',lambda:None)
        self.patch(app,'target',lambda root:(self.root,{'schema_version':6,'metro':{'ttl_seconds':300}}))
        self.patch(metro,'admitted',lambda:{})
        self.patch(metro.worktrees,'canonical',lambda root:self.identity())
        self.patch(metro,'require_idle',lambda *args:None);self.patch(metro.contract,'inputs',lambda *args:None)
        with patch.object(metro,'unit_fields',return_value={'LoadState':'loaded','ActiveState':'inactive','FragmentPath':'/foreign','DropInPaths':''}),patch.object(metro,'reserve') as reserve,self.assertRaises(app.AppError):
            metro.start(self.root)
        reserve.assert_not_called();self.assertFalse(metro.location('fixture').exists())

    def bound_receipt(self):
        metro.save(self.value)
        path=app.STORE/'metro/registry.json'
        app.save(path,{'schema_version':1,'entries':{'fixture':{'root':str(self.root),'canonical_key':'1'*64,'slot':0}}})

    def test_receipt_recovery_requires_exact_generation_and_registry_binding(self):
        self.bound_receipt()
        self.assertEqual(metro.receipt_for_root(self.root,'2'*32)[1],self.value)
        for root,generation in [(self.root,'9'*32),(self.projects/'foreign','2'*32)]:
            with self.assertRaises(app.AppError):metro.receipt_for_root(root,generation)
        self.value['canonical_key']='9'*64;metro.save(self.value)
        with self.assertRaises(app.AppError):metro.receipt_for_root(self.root,'2'*32)

    def test_recover_stop_does_not_read_invalid_project_configuration(self):
        self.bound_receipt()
        self.patch(metro.spike,'require_operator',lambda:None)
        with patch.object(app,'target',side_effect=AssertionError('invalid source must not be read')),patch.object(metro,'verify_unit'),patch.object(metro,'inactive_unit'),patch.object(metro,'cleanup'),patch.object(app,'command') as command:
            result=metro.recover_stop(self.root,'2'*32)
        self.assertEqual(result['state'],'stopped');self.assertIsNone(result['origin'])
        command.assert_called_once_with(['systemctl','--user','stop','gptclaw-metro-fixture.service'],timeout=40)

    def test_stop_timeout_records_unknown_recovery_and_never_claims_down(self):
        metro.save(self.value)
        with patch.object(metro,'verify_unit'),patch.object(app,'command',side_effect=app.AppError('timeout')),self.assertRaises(app.AppError):metro.stop_owned(self.root,self.value)
        state=metro.load('fixture',self.root)
        self.assertEqual(state['phase'],'recovery-required');self.assertEqual(state['operation_result'],'unknown')
        self.assertEqual(state['observations']['process']['state'],'unknown')

    def test_partial_start_never_stops_an_unverified_unit(self):
        metro.save(self.value)
        with patch.object(metro,'verify_unit',side_effect=app.AppError('conflict')),patch.object(metro,'cleanup'),patch.object(app,'command') as command:metro.failed_start(self.value)
        command.assert_not_called();self.assertEqual(metro.load('fixture',self.root)['phase'],'recovery-required')

    def test_failed_start_stops_verified_unit_and_records_resources_down(self):
        metro.save(self.value)
        with patch.object(metro,'verify_unit'),patch.object(metro,'inactive_unit'),patch.object(metro,'cleanup'),patch.object(app,'command'):metro.failed_start(self.value)
        value=metro.load('fixture',self.root)
        self.assertEqual(value['phase'],'failed');self.assertEqual(value['observations']['process']['state'],'down')

    def test_pre_execution_revocation_closes_orphaned_owned_resources(self):
        self.bound_receipt();self.value['phase']='starting';metro.save(self.value)
        self.patch(metro.spike,'require_operator',lambda:None)
        resources={self.value['name']:'owned',metro.network(self.value):'owned'}
        def command(argv,**kwargs):resources.pop(argv[-1],None)
        with patch.object(metro,'verify_unit'),patch.object(metro,'control',return_value={'source':'/unused'}),patch.object(metro,'admitted',side_effect=app.AppError('conflict')),patch.object(metro,'ownership',side_effect=lambda kind,name,token:resources.get(name,'absent')),patch.object(app,'command',side_effect=command):
            result=metro.supervise(self.root,'2'*32)
        self.assertEqual(resources,{});self.assertEqual(result['state'],'failed')
        self.assertEqual(metro.load('fixture',self.root)['observations']['process']['state'],'down')

    def test_lifecycle_events_never_include_raw_output_tokens_or_origins(self):
        metro.save(self.value);self.value.update(phase='stopped');metro.save(self.value)
        events=metro.read_events('fixture');self.assertEqual([e['phase'] for e in events],['running','stopped'])
        text=(metro.directory('fixture')/'events.json').read_text()
        for value in [self.value['token'],self.value['origin'],str(self.root)]:self.assertNotIn(value,text)
        self.patch(app,'target',lambda root:(self.root,{'schema_version':6,'project':{'id':'fixture'}}))
        self.patch(metro.worktrees,'canonical',lambda root:{})
        result=metro.logs(self.root,1);self.assertEqual(len(result['events']),1);self.assertEqual(result['log_kind'],'lifecycle-events')
        for limit in [0,257,True,'80']:
            with self.assertRaises(app.AppError):metro.logs(self.root,limit)

    def test_lifecycle_event_retention_is_bounded_and_expires(self):
        clock={'now':1800000000};self.patch(metro.time,'time',lambda:clock['now'])
        for i in range(270):
            self.value['generation']=f'{i:032x}';metro.save(self.value)
        self.assertEqual(len(metro.read_events('fixture')),256)
        self.assertLess((metro.directory('fixture')/'events.json').stat().st_size,65536)
        clock['now']+=7*86400+1;self.value['generation']='e'*32;metro.save(self.value)
        self.assertEqual(len(metro.read_events('fixture')),1)

    def test_unknown_log_fields_and_secret_text_are_rejected(self):
        metro.save(self.value);events=metro.read_events('fixture');events[0]['raw_output']='synthetic-secret'
        app.save(metro.directory('fixture')/'events.json',{'schema_version':1,'events':events})
        with self.assertRaises(app.AppError):metro.read_events('fixture')

    def test_revocation_plan_is_read_only_and_exact_apply_is_idempotent(self):
        policy={'scope':'synthetic'};key=metro.digest(policy)
        self.patch(metro.spike,'require_operator',lambda:None)
        with patch.object(metro.security,'read_policy',return_value=policy),patch.object(app,'command',side_effect=AssertionError('no subprocess')):
            self.assertEqual(metro.revoke(key)['state'],'revocation-planned');self.assertFalse(metro.revoke_path(key).exists())
            self.assertTrue(metro.revoke(key,True)['changed']);self.assertFalse(metro.revoke(key,True)['changed'])
            with self.assertRaises(app.AppError):metro.admitted()

    def test_foreign_policy_revocation_cannot_write_marker(self):
        self.patch(metro.spike,'require_operator',lambda:None)
        with patch.object(metro.security,'read_policy',return_value={'scope':'synthetic'}),self.assertRaises(app.AppError):metro.revoke('f'*64,True)
        self.assertFalse(metro.revoke_path('f'*64).exists())

    def test_private_route_is_not_inferred_from_running_status(self):
        self.patch(metro,'admitted',lambda *args:None)
        self.patch(metro,'hashes',lambda root:{'a':'b'});self.value['input_digest']=metro.digest({'a':'b'})
        with patch.object(metro_state.time,'time',return_value=1800000000):result=metro.result(self.value,self.root,{'key':'1'*64})
        self.assertEqual(result['state'],'route-pending');self.assertIsNone(result['origin']);self.assertFalse(result['transport_available'])

    def test_renewal_can_inspect_its_exact_frozen_unit_from_source_provider(self):
        provider=app.STORE/'providers'/('9'*64)
        self.value['unit_digest']=hashlib.sha256(metro.unit_text(self.value,provider).encode()).hexdigest()
        metro.save(self.value)
        data={'schema_version':2,'project':'fixture','root':str(self.root),'generation':'2'*32,
              'inputs':{p:'0'*64 for p in metro.FILES},
              'source':str(metro.directory('fixture')/'sources'/('2'*32)),
              'provider':str(provider),'audit':None,'root_identity':[1,2],
              'mount_identities':{'src':None,'assets':None,'node_modules':[1,2]}}
        app.save(metro.directory('fixture')/'control.json',data)
        self.assertEqual(metro.control(self.value,allow_frozen=True),data)
        with self.assertRaises(app.AppError):metro.control(self.value)
        data['provider']=str(app.STORE/'providers'/('8'*64))
        app.save(metro.directory('fixture')/'control.json',data)
        with self.assertRaises(app.AppError):metro.control(self.value,allow_frozen=True)

    def test_stop_start_race_cannot_reuse_a_different_generation(self):
        self.patch(metro.spike,'require_operator',lambda:None)
        self.patch(app,'target',lambda root:(self.root,{'schema_version':6,'metro':{'ttl_seconds':300}}))
        self.patch(metro,'admitted',lambda:{})
        self.patch(metro.worktrees,'canonical',lambda root:self.identity())
        self.patch(metro,'require_idle',lambda *args:None)
        self.patch(metro.contract,'inputs',lambda *args:None)
        self.patch(metro,'load',lambda *args:self.value)
        with patch.object(metro,'verify_unit') as verify,patch.object(app,'command') as command,self.assertRaises(app.AppError):
            metro.start(self.root,expected_generation='9'*32)
        verify.assert_not_called();command.assert_not_called()

    def test_capacity_denial_precedes_new_lease_provider_or_session_publication(self):
        self.patch(metro.spike,'require_operator',lambda:None)
        self.patch(app,'target',lambda root:(self.root,{'schema_version':6,'metro':{'ttl_seconds':300}}))
        self.patch(metro,'admitted',lambda:{})
        self.patch(metro.worktrees,'canonical',lambda root:self.identity())
        self.patch(metro,'require_idle',lambda *args:None)
        self.patch(metro.contract,'inputs',lambda *args:None)
        self.patch(metro,'preflight_unit',lambda *args:None)
        self.patch(metro,'load',lambda *args:None)
        self.patch(metro.tools,'selection',lambda *args:{})
        self.patch(metro.tools,'observed',lambda *args:{'state':'verified','image_present':True})
        self.patch(metro.spike,'prepared_dependencies',lambda *args:None)
        content=b'{"expo":{}}'
        (self.root/'app.json').write_bytes(content)
        self.patch(metro.spike,'source_inventory',lambda root:{'app.json':hashlib.sha256(content).hexdigest()})
        cache=metro.directory('fixture')/'sources'/('9'*32)
        cache.mkdir(parents=True)
        (cache/'owned-unknown').write_bytes(b'x'*100)
        with patch.object(metro.retention,'MAX_SOURCES',100),patch.object(metro,'reserve') as reserve,patch.object(app,'provider_bundle') as bundle,self.assertRaises(app.AppError) as error:
            metro.start(self.root)
        self.assertEqual(error.exception.code,'metro-capacity')
        reserve.assert_not_called();bundle.assert_not_called()
        self.assertFalse(metro.location('fixture').exists())
        self.assertEqual((cache/'owned-unknown').read_bytes(),b'x'*100)

    def test_status_immediately_disables_transport_on_policy_withdrawal(self):
        self.patch(metro,'hashes',lambda *args:{})
        self.value['input_digest']=metro.digest({})
        self.value['observations']['route']={'state':'verified','observed_at':1800000000}
        with patch.object(metro_state.time,'time',return_value=1800000000),patch.object(metro,'admitted',side_effect=app.AppError('conflict')):
            result=metro.result(self.value,self.root,{'key':'1'*64})
        self.assertEqual(result['state'],'security-unavailable')
        self.assertIsNone(result['origin']);self.assertFalse(result['transport_available'])
        self.assertEqual(result['observations']['process']['state'],'up')

    def test_stopped_state_remains_inspectable_after_policy_expiry(self):
        self.patch(metro,'hashes',lambda *args:{})
        self.value['phase']='stopped'
        with patch.object(metro,'admitted',side_effect=AssertionError('inactive observation needs no new admission')):
            result=metro.result(self.value,self.root,{'key':'1'*64})
        self.assertEqual(result['state'],'stopped')
        self.assertFalse(result['transport_available'])

    def prepare_renewal(self):
        self.value['observations']['route']={'state':'verified','observed_at':1800000000}
        self.patch(metro.time,'time',lambda:1800000000)
        self.patch(metro,'load',lambda *args:copy.deepcopy(self.value))
        self.patch(app,'target',lambda root:(self.root,{'schema_version':6,'metro':{'ttl_seconds':300}}))
        self.patch(metro.worktrees,'canonical',lambda root:{'project':'fixture','key':'1'*64,'root_identity':[1,2]})
        self.patch(metro,'admitted',lambda *args:{'expires_at':'2027-02-01T00:00:00Z'})
        self.patch(metro,'verify_unit',lambda *args:None)
        self.patch(metro,'require_idle',lambda *args:None)
        self.patch(metro.contract,'inputs',lambda *args:None)
        self.patch(metro,'control',lambda *args,**kwargs:{'root_identity':[1,2],'mount_identities':{}})
        self.patch(metro,'mount_identities',lambda *args:{})
        self.patch(metro,'hashes',lambda *args:{})
        self.value['input_digest']=metro.digest({})
        self.patch(metro,'ownership',lambda *args:'owned')
        self.patch(metro,'unit_fields',lambda *args:{'ActiveState':'active'})
        self.patch(metro.routes,'observe',lambda *args:{'state':'verified'})
        self.patch(metro.spike,'require_operator',lambda:None)
        self.patch(metro_state.time,'time',lambda:1800000000)

    def test_renewal_plan_is_read_only_and_never_extends_current_receipt(self):
        self.prepare_renewal()
        before=copy.deepcopy(self.value)
        with patch.object(metro,'stop_owned') as stop,patch.object(metro,'start') as start:
            result=metro.renew(self.root,'2'*32,90)
        self.assertEqual(result['renewal_kind'],'new-generation')
        self.assertEqual(result['ttl_seconds'],90)
        self.assertEqual(self.value,before)
        self.assertFalse(app.STORE.exists())
        stop.assert_not_called();start.assert_not_called()

    def test_explicit_renewal_stops_then_starts_fresh_generation(self):
        self.prepare_renewal()
        plan=metro.renew(self.root,'2'*32)
        calls=[]
        with patch.object(metro,'stop_owned',side_effect=lambda *args:calls.append('stop')),patch.object(metro,'start',side_effect=lambda *args,**kw:(calls.append(kw) or {'generation':'9'*32,'state':'route-pending','changed':True})):
            result=metro.renew(self.root,'2'*32,apply=True,confirm_plan=plan['plan_digest'])
        self.assertEqual(calls,['stop',{'ttl_seconds':300,'expected_generation':'2'*32}])
        self.assertEqual(result['previous_generation'],'2'*32)
        self.assertEqual(result['generation'],'9'*32)

    def test_unconfirmed_or_expired_renewal_preserves_live_session(self):
        self.prepare_renewal()
        with patch.object(metro,'stop_owned') as stop,patch.object(metro,'start') as start:
            with self.assertRaises(app.AppError):metro.renew(self.root,'2'*32,apply=True,confirm_plan='0'*64)
            self.value['expires_at']=1800000000
            with self.assertRaises(app.AppError):metro.renew(self.root,'2'*32)
        stop.assert_not_called();start.assert_not_called()

    def test_renewal_requires_current_private_route_and_source_inputs(self):
        self.prepare_renewal()
        with patch.object(metro,'stop_owned') as stop:
            for state in ['pending','failed']:
                with patch.object(metro.routes,'observe',return_value={'state':state}),self.assertRaises(app.AppError):
                    metro.renew(self.root,'2'*32)
            self.value['input_digest']='0'*64
            with self.assertRaises(app.AppError):metro.renew(self.root,'2'*32)
        stop.assert_not_called()

    def test_renewal_rechecks_plan_before_shutdown(self):
        self.prepare_renewal()
        plan=metro.renew(self.root,'2'*32)
        original=metro.renewal_plan
        count={'calls':0}
        def race(*args):
            count['calls']+=1
            if count['calls']==2:self.value['unit_digest']='0'*64
            return original(*args)
        with patch.object(metro,'renewal_plan',side_effect=race),patch.object(metro,'stop_owned') as stop,self.assertRaises(app.AppError):
            metro.renew(self.root,'2'*32,apply=True,confirm_plan=plan['plan_digest'])
        stop.assert_not_called()

    def test_failed_renewal_shutdown_cannot_start_another_sdk(self):
        self.prepare_renewal()
        plan=metro.renew(self.root,'2'*32)
        with patch.object(metro,'stop_owned',side_effect=app.AppError('timeout')),patch.object(metro,'start') as start,self.assertRaises(app.AppError):
            metro.renew(self.root,'2'*32,apply=True,confirm_plan=plan['plan_digest'])
        start.assert_not_called()

    def test_renewal_respects_policy_expiry_and_declared_lifetime(self):
        self.prepare_renewal()
        for seconds in [59,301,True]:
            with self.assertRaises(app.AppError):metro.renew(self.root,'2'*32,seconds)
        with patch.object(metro.security,'timestamp',return_value=1800000059),self.assertRaises(app.AppError):
            metro.renew(self.root,'2'*32)

    def test_changed_generation_cannot_be_renewed(self):
        self.prepare_renewal()
        with self.assertRaises(app.AppError):metro.renew(self.root,'9'*32)

    def test_renewal_cli_passes_exact_reviewed_inputs(self):
        import contextlib,io,gptclawctl
        output=io.StringIO()
        with patch.object(metro,'renew',return_value={'state':'renewal-planned'}) as renew,patch.object(metro.worktrees,'guard'),contextlib.redirect_stdout(output):
            self.assertEqual(gptclawctl.main(['metro','renew','--project-root',str(self.root),'--generation','2'*32,'--ttl-seconds','90']),0)
        renew.assert_called_once_with(str(self.root),'2'*32,90,False,None)
        self.assertEqual(json.loads(output.getvalue())['state'],'renewal-planned')


if __name__=='__main__':unittest.main()
