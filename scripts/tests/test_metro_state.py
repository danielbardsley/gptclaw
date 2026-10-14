#!/usr/bin/env python3
"""Ownership/freshness/expiry observations cannot imply native/device readiness."""
import copy
import json
from pathlib import Path
import sys
import unittest
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import private_apps as app
import metro_state as state


class StateTests(unittest.TestCase):
    def setUp(self):
        self.now=1800000000
        self.value={'schema_version':1,'adapter':'metro-v1','project':'fixture','root':str(app.PROJECTS/'fixture'),
                    'canonical_key':'1'*64,'name':'gptclaw-metro-fixture','generation':'2'*32,'token':'3'*32,
                    'image':'sha256:'+'4'*64,'input_digest':'5'*64,'policy_digest':'6'*64,'unit_digest':'7'*64,
                    'metro_port':18600,'proxy_port':18601,'origin':'https://fixture.tail123.ts.net:8443',
                    'phase':'running','started_at':self.now-10,'expires_at':self.now+600,
                    'operation_id':'8'*32,'operation_result':'passed','observations':{
                        'process':{'state':'up','observed_at':self.now},'protocol':{'state':'ready','observed_at':self.now},
                        'route':{'state':'verified','observed_at':self.now}}}
    def project(self,**kwargs):
        args={'project':'fixture','root':app.PROJECTS/'fixture','canonical_key':'1'*64,'input_digest':'5'*64,'now':self.now};args.update(kwargs)
        return state.descriptor(self.value,**args)
    def test_ready_transport_is_not_native_acceptance_or_web_url(self):
        result=self.project();self.assertTrue(result['transport_available']);self.assertEqual(result['state'],'ready')
        self.assertEqual(result['native_client_acceptance'],'unverified');self.assertNotIn('launch_uri',result)
        self.assertNotIn('token',result);self.assertNotIn('image',result);self.assertNotIn('device',result)
    def test_process_up_without_protocol_and_route_is_loopback_only(self):
        self.value['observations']['protocol']={'state':'unknown','observed_at':None}
        self.value['observations']['route']={'state':'pending','observed_at':None}
        result=self.project();self.assertEqual(result['state'],'loopback-running');self.assertFalse(result['transport_available']);self.assertIsNone(result['origin'])
    def test_protocol_ready_without_verified_route_is_pending(self):
        self.value['observations']['route']={'state':'pending','observed_at':None}
        self.assertEqual(self.project()['state'],'route-pending');self.assertIsNone(self.project()['origin'])
    def test_each_observation_has_independent_freshness(self):
        self.value['started_at']=self.now-100
        for field in ['process','protocol','route']:
            original=copy.deepcopy(self.value['observations']);self.value['observations'][field]['observed_at']=self.now-31
            with self.subTest(field=field):
                result=self.project();self.assertEqual(result['state'],'stale');self.assertFalse(result['transport_available'])
            self.value['observations']=original
    def test_future_observation_cannot_grant_availability(self):
        for field in ['process','protocol','route']:
            self.value['observations'][field]['observed_at']=self.now+1
            self.assertFalse(self.project()['transport_available']);self.value['observations'][field]['observed_at']=self.now
    def test_expiry_disables_even_recent_ready_observations(self):
        self.value['expires_at']=self.now
        self.assertEqual(self.project()['state'],'expired');self.assertIsNone(self.project()['origin'])
    def test_inactive_and_unknown_operation_outcomes_never_publish(self):
        for phase in state.INACTIVE:
            self.value['phase']=phase;self.assertFalse(self.project()['transport_available'])
        self.value['phase']='running';self.value['operation_result']='unknown';self.assertFalse(self.project()['transport_available'])
    def test_expected_project_root_and_canonical_identity_cannot_be_substituted(self):
        for args in [{'project':'other'},{'root':app.PROJECTS/'other'},{'canonical_key':'9'*64}]:
            with self.assertRaises(app.AppError):self.project(**args)
    def test_input_drift_hides_available_target(self):
        result=self.project(input_digest='0'*64);self.assertEqual(result['state'],'input-drift');self.assertIsNone(result['origin'])
    def test_invalid_ports_lifetime_and_image_rejected(self):
        for key,value in [('metro_port',True),('metro_port',18080),('proxy_port',18604),('image','mutable:latest'),('expires_at',self.now+28801),('started_at',float('nan'))]:
            receipt=copy.deepcopy(self.value);receipt[key]=value
            with self.subTest(key=key),self.assertRaises(app.AppError):state.validate(receipt)
    def test_untrusted_fields_and_phase_types_fail_closed(self):
        for key,value in [('environment',{'SECRET':'synthetic'}),('device_online',True),('argv',['unreviewed']),('phase',[])]:
            receipt=copy.deepcopy(self.value);receipt[key]=value
            with self.assertRaises(app.AppError):state.validate(receipt)
    def test_non_private_credential_and_path_origins_rejected(self):
        for origin in ['http://127.0.0.1:18600','https://public.example:8443','https://user@fixture.tail123.ts.net:8443','https://fixture.tail123.ts.net:8443/project/']:
            receipt=copy.deepcopy(self.value);receipt['origin']=origin
            with self.assertRaises(app.AppError):state.validate(receipt)
    def test_source_only_runtime_root_and_path_traversal_rejected(self):
        for root in [str(app.PROJECTS/'.gptclaw-worktrees/fixture/task'),str(app.PROJECTS/'.gptclaw-runtime/v1'),str(app.PROJECTS/'fixture/../other'),'/home/forge/fixture']:
            receipt=copy.deepcopy(self.value);receipt['root']=root
            with self.assertRaises(app.AppError):state.validate(receipt)
    def test_projection_does_not_mutate_saved_state(self):
        before=json.dumps(self.value,sort_keys=True);result=self.project();result['observations']['process']['state']='down'
        self.assertEqual(json.dumps(self.value,sort_keys=True),before)

if __name__=='__main__':unittest.main()
