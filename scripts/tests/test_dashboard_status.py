"""Status freshness, observed transitions, malformed projection and shared worker bounds."""
import copy
import json
from pathlib import Path
import sys
import threading
import time
import unittest

sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from dashboard_status import StatusStore
from dashboard_collector import bounded


def fake_observation(binding):
    if binding.get('hang'):time.sleep(10)
    return {'observation_schema':1,'provider_version':'1.9.0','project':binding['id'],
        'observed_at':time.time(),'state':'ready','provider_state':'ready','health':'healthy','operation_busy':False,
        'components':{name:{'state':'ready','provider_state':'ready','health':'healthy','operation_busy':False,
             'uptime_seconds':10,'restart_count':0,'instance':'1'*32} for name in binding['components']},
        'publication':{'state':'published','origin':'https://forge-dev.example.ts.net'}}


class StatusTests(unittest.TestCase):
    def setUp(self):
        self.now=100.
        self.binding={'id':'project','components':['web','api','db']}
        self.store=StatusStore(lambda *args:None,clock=lambda:self.now)

    def result(self,state='ready'):
        value=fake_observation(self.binding)
        value.update(observed_at=self.now,state=state,provider_state=state,
                     health='healthy' if state=='ready' else 'unknown')
        for component in value['components'].values():
            component.update(state=state,provider_state=state,health=value['health'])
        return value

    def update(self,value=None):
        self.store.update('key',self.binding,value or self.result())
        return self.store.snapshot('key',self.binding)

    def test_initial_observation_same_polls_change_gap_and_collector_restart(self):
        current=self.update()
        self.assertEqual(current['last_observed_change']['kind'],'first-observed')
        self.assertEqual(current['components']['web']['restart_count'],0)
        self.assertNotIn('instance',json.dumps(current))
        self.now=105;current=self.update()
        self.assertEqual(current['last_observed_change']['at'],100)
        self.now=110;current=self.update(self.result('stopped'))
        self.assertEqual(current['last_observed_change']['kind'],'change-detected')
        self.assertEqual(current['last_observed_change']['at'],110)
        self.now=150;self.store.update('key',self.binding,{'error':'observation-timeout'})
        old=self.store.snapshot('key',self.binding)
        self.assertEqual(old['freshness'],'stale')
        self.assertEqual(old['last_success_at'],110)
        self.now=155;current=self.update()
        self.assertTrue(current['last_observed_change']['after_gap'])
        self.assertEqual(current['last_observed_change']['previous_observation_at'],110)
        fresh=StatusStore(lambda *args:None,clock=lambda:self.now)
        fresh.update('key',self.binding,self.result())
        self.assertEqual(fresh.snapshot('key',self.binding)['last_observed_change']['kind'],'first-observed')

    def test_stale_threshold_clock_rollback_and_publication_disabled(self):
        self.update();self.now=131
        stale=self.store.snapshot('key',self.binding)
        self.assertEqual(stale['freshness'],'stale')
        self.assertEqual(stale['publication']['state'],'unavailable')
        self.now=90;value=self.update()
        self.assertEqual(value['reason'],'clock-anomaly')
        self.assertEqual(value['last_success_at'],100)
        self.now=140;self.assertEqual(self.update()['freshness'],'current')

    def test_component_failure_cannot_inherit_sibling_timestamp(self):
        self.update();self.now=105
        value=self.result();value['components']['api'].update(state='unknown',health='unknown',reason='ownership-conflict')
        current=self.update(value)
        self.assertEqual(current['components']['web']['last_success_at'],105)
        self.assertEqual(current['components']['api']['last_success_at'],100)
        self.assertEqual(current['components']['api']['freshness'],'stale')
        self.assertEqual(current['publication']['state'],'unavailable')
        self.assertEqual(current['components']['db']['health'],'healthy')

    def test_malformed_fields_secret_extras_and_component_change_refused(self):
        value=self.result();value['secret']='synthetic-do-not-project'
        value['components']['web'].update(extra='synthetic-do-not-project',restart_count=True)
        current=self.update(value)
        self.assertNotIn('synthetic-do-not-project',json.dumps(current))
        self.assertIsNone(current['components']['web']['restart_count'])
        self.now=105;value=self.result();value['observation_schema']=True
        current=self.update(value)
        self.assertEqual(current['reason'],'observation-invalid')
        value=self.result();value['components']['web']['state']=[]
        current=self.update(value)
        self.assertEqual(current['components']['web']['freshness'],'stale')
        changed=self.store.snapshot('key',{'id':'project','components':['api']})
        self.assertEqual(changed['freshness'],'unavailable')
        self.assertEqual(set(changed['components']),{'api'})

    def test_instance_replacement_changes_component_observation_and_resets_metrics(self):
        self.update();self.now=105
        value=self.result();value['components']['web'].update(instance='2'*32,uptime_seconds=1,restart_count=0)
        current=self.update(value)
        self.assertEqual(current['components']['web']['uptime_seconds'],1)
        self.assertEqual(current['components']['web']['last_observed_change']['at'],105)
        self.assertEqual(current['components']['web']['restart_count'],0)

    def test_partial_inventory_does_not_evict_and_full_scan_does(self):
        self.update();self.store.retain(set(),complete=False)
        self.assertEqual(self.store.snapshot('key',self.binding)['freshness'],'current')
        self.store.retain(set(),complete=True)
        self.assertEqual(self.store.snapshot('key',self.binding)['freshness'],'unavailable')

    def test_real_twenty_project_workers_timeout_reaping_and_read_coalescing(self):
        store=StatusStore(bounded,observe=fake_observation)
        bindings={f'key-{index:02d}':{'id':f'project-{index}','components':['web','api','db'],'hang':index==0} for index in range(20)}
        started=time.monotonic()
        thread=threading.Thread(target=store.round,args=(bindings,));thread.start()
        # Readers never schedule collection; a competing round is refused.
        time.sleep(.05)
        self.assertFalse(store.round(bindings))
        for _ in range(20):store.snapshot('key-01',bindings['key-01'])
        thread.join(timeout=14)
        self.assertFalse(thread.is_alive())
        self.assertLess(time.monotonic()-started,15)
        self.assertEqual(store.snapshot('key-00',bindings['key-00'])['freshness'],'unavailable')
        self.assertEqual(store.snapshot('key-01',bindings['key-01'])['freshness'],'current')
        self.assertEqual(len(store.entries),20)

    def test_above_target_rotates_bounded_windows_and_cache_is_bounded(self):
        seen=[]
        def run(function,binding,*args):
            seen.append(binding['id']);value=fake_observation(binding);value['observed_at']=100.;return value
        store=StatusStore(run,clock=lambda:100.)
        bindings={str(index):{'id':str(index),'components':['web']} for index in range(21)}
        store.round(bindings);self.assertEqual(len(seen),20)
        self.assertTrue(store.capacity['limited'])
        store.round(bindings);self.assertEqual(len(set(seen)),21)
        for index in range(300):store.update(str(index),bindings['0'],fake_observation(bindings['0']))
        self.assertLessEqual(len(store.entries),256)


if __name__=='__main__':unittest.main()
