"""Go projection rejects untrusted links and withdraws stale launch capability."""
import copy
from pathlib import Path
import sys
import unittest
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import dashboard_go as go
from dashboard_status import StatusStore

class Tests(unittest.TestCase):
    def setUp(self):
        self.now=1000.;self.generation='1'*32
        self.metro={'adapter':'metro-v1','transport_available':True,'schema_version':1,'project':'fixture','generation':self.generation,
            'state':'ready','expires_at':2000.,'native_client_acceptance':'unverified','source_quality':'separate-receipt',
            'observations':{k:{'state':v,'observed_at':1000.} for k,v in [('process','up'),('protocol','ready'),('route','verified')]}}
        self.value={'schema_version':1,'adapter':'expo-go-v1','project':'fixture','platform':'android',
            'client_version':'57.0.9','os_version':'11','state':'compatible','reason':'verified-client-profile',
            'physical_verified_at':900.,'certification_expires_at':605700.,'client_evidence':'reviewed-profile',
            'launch':{'schema_version':1,'project':'fixture','platform':'android','generation':self.generation,
                'uri':'exp://synthetic.tail123.ts.net:8443/_gptclaw/metro-session/'+self.generation,'expires_at':2000.}}
    def project(self):return go.project(self.value,'fixture',self.metro)
    def test_only_bounded_profile_and_launch_fields_project(self):
        self.value.update(token='do-not-project',device_id='do-not-project')
        result=self.project();self.assertEqual(result['launch'],self.value['launch'])
        self.assertNotIn('do-not-project',str(result))
    def test_malformed_values_and_false_phone_discovery_are_unavailable(self):
        for field,value in [('schema_version',True),('project','other'),('platform','ios'),('state',[]),
                            ('reason','secret'),('reason','physical-client-and-launch-rule-unverified'),('client_evidence','detected-phone'),('os_version',[]),
                            ('physical_verified_at',True),('certification_expires_at',float('nan'))]:
            original=copy.deepcopy(self.value);self.value[field]=value
            with self.subTest(field=field):self.assertIsNone(self.project())
            self.value=original
    def test_foreign_generation_secret_scheme_origin_or_expiry_cannot_publish(self):
        for field,value in [('project','other'),('generation','2'*32),('expires_at',2001.),
                ('uri','https://untrusted.invalid'),('uri',self.value['launch']['uri']+'?token=secret'),
                ('uri',self.value['launch']['uri'].replace('exp:','javascript:'))]:
            original=copy.deepcopy(self.value);self.value['launch'][field]=value
            with self.subTest(field=field):self.assertIsNone(self.project())
            self.value=original
    def test_candidate_never_publishes_launch(self):
        self.value.update(state='check-required',reason='physical-client-and-launch-rule-unverified',
                          physical_verified_at=None,certification_expires_at=None)
        self.assertIsNone(self.project());self.value['launch']=None
        self.assertIsNotNone(self.project())
    def test_stale_expired_future_or_wrong_session_withdraws_uri(self):
        value=self.project()
        for freshness,now,metro in [('stale',1000.,self.metro),('current',2000.,self.metro),
                ('current',1000.,{**self.metro,'generation':'2'*32}),('current',1000.,{**self.metro,'state':'stopped'})]:
            self.assertIsNone(go.public(value,metro,freshness,now)['launch'])
        for now in [899.,605700.]:
            result=go.public(value,self.metro,'current',now)
            self.assertEqual(result['reason'],'physical-client-certification-expired');self.assertIsNone(result['launch'])
    def test_missing_capability_preserves_native_observation_without_go(self):
        binding={'id':'fixture','components':[],'native_session':1}
        store=StatusStore(lambda *args:None,clock=lambda:self.now)
        result={'observation_schema':1,'project':'fixture','observed_at':1000.,'components':{},
            'state':'ready','provider_state':'ready','health':'not-applicable','operation_busy':False,
            'metro':self.metro,'expo_go':self.value}
        store.update('key',binding,result);self.assertNotIn('expo_go',store.snapshot('key',binding))
        binding['expo_go']=1;store.update('key',binding,result)
        self.assertEqual(store.snapshot('key',binding)['expo_go']['launch'],self.value['launch'])
        self.now=1031.;self.assertIsNone(store.snapshot('key',binding)['expo_go']['launch'])

if __name__=='__main__':unittest.main()
