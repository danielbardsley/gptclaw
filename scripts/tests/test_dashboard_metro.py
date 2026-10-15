"""Separate native-state freshness, privacy, ownership and collector behavior."""
import copy
from pathlib import Path
import sys
import unittest
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import dashboard_metro as native
from dashboard_status import StatusStore


class Tests(unittest.TestCase):
    def setUp(self):
        self.now=100.
        self.binding={'id':'fixture','components':[],'native_session':1}
        self.value={'schema_version':1,'adapter':'metro-v1','project':'fixture','generation':'1'*32,
                    'state':'ready','expires_at':200.,'transport_available':True,
                    'origin':'https://synthetic.tail123.ts.net:8443','native_client_acceptance':'unverified',
                    'source_quality':'separate-receipt',
                    'observations':{k:{'state':s,'observed_at':100.} for k,s in
                                    [('process','up'),('protocol','ready'),('route','verified')]}}
        self.store=StatusStore(lambda *args:None,clock=lambda:self.now)

    def observation(self):
        return {'observation_schema':1,'project':'fixture','observed_at':self.now,'components':{},
                'state':'ready','provider_state':'ready','health':'not-applicable','operation_busy':False,
                'metro':copy.deepcopy(self.value),'publication':{'state':'published','origin':'https://foreign.ts.net'},
                'routes':{'schema_version':1,'project':'fixture','app_path':'/projects/fixture/','docs_path':None}}

    def update(self):
        self.store.update('key',self.binding,self.observation())
        return self.store.snapshot('key',self.binding)

    def test_only_native_state_and_no_origins_credentials_or_device_ids(self):
        self.value.update(secret='do-not-project',device_id='do-not-project',token='do-not-project')
        result=self.update()
        self.assertEqual(result['components'],{})
        self.assertEqual(result['metro']['state'],'ready')
        self.assertNotIn('do-not-project',str(result))
        self.assertNotIn('origin',str(result['metro']))
        self.assertEqual(result['publication'],{'state':'unavailable','origin':None})
        self.assertIsNone(result['routes']['app_path'])

    def test_http_descriptor_version_is_supported_without_publishing_transport_origin(self):
        self.value.update(schema_version=2, transport='private-tailnet-http',
                          origin='http://fixture.tail123.ts.net:8443')
        result = native.project(self.value, 'fixture')
        self.assertIsNotNone(result)
        self.assertEqual(result['state'], 'ready')
        self.assertNotIn('origin', result)
        self.assertEqual(result['native_client_acceptance'], 'unverified')
        self.value['transport'] = 'public-http'
        self.assertIsNone(native.project(self.value, 'fixture'))

    def test_each_layer_ages_and_expiry_does_not_remain_ready(self):
        self.update();self.now=131.
        result=self.store.snapshot('key',self.binding)
        self.assertEqual(result['metro']['state'],'stale')
        self.assertEqual(result['metro']['observations']['process']['freshness'],'stale')
        self.now=200.
        self.assertEqual(self.store.snapshot('key',self.binding)['metro']['state'],'expired')

    def test_route_pending_preserves_process_and_protocol(self):
        self.value.update(state='route-pending',transport_available=False,origin=None)
        self.value['observations']['route']={'state':'pending','observed_at':100.}
        result=self.update()
        self.assertEqual(result['metro']['state'],'route-pending')
        self.assertEqual(result['metro']['observations']['process']['state'],'up')
        self.assertEqual(result['metro']['observations']['protocol']['state'],'ready')

    def test_bad_project_version_generation_timestamp_and_acceptance_are_denied(self):
        for field,value in [('project','foreign'),('schema_version',True),('generation','bad'),
                            ('expires_at',float('nan')),('state',[]),('native_client_acceptance','accepted'),
                            ('transport_available',1)]:
            candidate={**self.value,field:value}
            with self.subTest(field=field):
                self.assertIsNone(native.project(candidate,'fixture'))
        candidate=copy.deepcopy(self.value);candidate['observations']['process']['observed_at']=True
        self.assertIsNone(native.project(candidate,'fixture'))

    def test_failure_preserves_only_last_known_without_publication(self):
        self.update();self.now=105.
        bad=self.observation();bad['metro']['generation']='foreign'
        self.store.update('key',self.binding,bad)
        result=self.store.snapshot('key',self.binding)
        self.assertEqual(result['reason'],'observation-invalid')
        self.assertEqual(result['metro']['freshness'],'stale')
        self.assertEqual(result['metro']['state'],'stale')
        self.assertEqual(result['publication']['state'],'unavailable')

    def test_never_started_has_no_fake_component_or_device_observation(self):
        self.value={'project':'fixture','state':'not-started','transport_available':False,'origin':None}
        result=self.update()
        self.assertEqual(result['metro']['state'],'not-started')
        self.assertIsNone(result['metro']['generation'])
        self.assertTrue(all(o['observed_at'] is None for o in result['metro']['observations'].values()))

    def test_capability_absent_and_schema5_still_do_not_poll_native(self):
        called=[]
        store=StatusStore(lambda *args:called.append(args),observe=lambda b:{},clock=lambda:self.now)
        store.round({'key':{'id':'fixture','components':[]}})
        self.assertEqual(called,[])
        self.assertEqual(store.snapshot('key',{'id':'fixture','components':[]})['reason'],'unsupported')

    def test_native_uses_existing_bounded_worker_round(self):
        called=[]
        def run(fn,binding,*args):
            called.append(binding);return self.observation()
        store=StatusStore(run,clock=lambda:self.now)
        self.assertTrue(store.round({'key':self.binding}))
        self.assertEqual(len(called),1)
        self.assertEqual(store.snapshot('key',self.binding)['metro']['state'],'ready')


if __name__=='__main__':unittest.main()
