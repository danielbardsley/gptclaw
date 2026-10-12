"""Read-only provider projection, ownership and timing behavior with synthetic runtimes."""
import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock

sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import dashboard_observation as observation
import private_apps as app
import project_groups as groups
import project_database as db


class ObservationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='dashboard-observation-');self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name)
        for target,key,value in ((app,'PROJECTS',self.base),(app,'STORE',self.base/'.runtime'),(app,'UNITS',self.base/'units')):
            mock=patch.object(target,key,value);mock.start();self.addCleanup(mock.stop)
        app.UNITS.mkdir()
        self.calls=[];self.objects={};self.readiness={}
        def command(argv,**kwargs):
            self.calls.append(argv)
            if argv[:3]==['podman','container','exists']:
                return subprocess.CompletedProcess(argv,0 if argv[3] in self.objects else 1,'','')
            if argv[:3]==['podman','container','inspect']:
                return subprocess.CompletedProcess(argv,0,json.dumps([self.objects[argv[3]]]),'') if argv[3] in self.objects else subprocess.CompletedProcess(argv,125,'','missing')
            if argv[:3]==['podman','image','inspect']:
                return subprocess.CompletedProcess(argv,0,'2'*64,'')
            if argv[:3]==['podman','network','exists']:
                return subprocess.CompletedProcess(argv,1,'','')
            raise AssertionError('Unexpected operation: '+str(argv))
        mock=patch.object(app,'command',side_effect=command);mock.start();self.addCleanup(mock.stop)
        mock=patch.object(app,'inspect_service',side_effect=lambda s,c:self.readiness.get(s['id'],(False,False)))
        mock.start();self.addCleanup(mock.stop)
        mock=patch.object(app,'route_info',return_value={'state':'configured','url':'https://forge-dev.example.ts.net/projects/synthetic/'})
        mock.start();self.addCleanup(mock.stop)
        opener=MagicMock()
        response=opener.open.return_value.__enter__.return_value
        response.status=200;response.headers.get_content_type.return_value='text/html'
        mock=patch.object(observation.urllib.request,'build_opener',return_value=opener)
        mock.start();self.addCleanup(mock.stop)

    def root(self,slug,template='nextjs'):
        return Path(app.create(slug,template=template,template_version='1.0.0')['root'])

    def runtime(self,root):
        contract=app.target(root)[1]
        if contract['schema_version'] in (3,4):
            group=groups.reserve(root,contract)
            with groups.scope(root,contract) as children:
                states={name:app.reserve(child,value) for name,(child,value) in children.items()}
            return group,states
        s=app.reserve(root,contract)
        s.update(phase='stopped',health_ready=False,operation_result='passed')
        app.save(app.STORE/(s['id']+'.json'),s)
        return s,{contract['project']['kind']:s}

    def active(self,s,ready=True, count=0):
        s.update(phase='ready',health_ready=True,operation_result='passed')
        app.save(app.STORE/(s['id']+'.json'),s)
        self.readiness[s['id']]=(True,ready)
        self.objects[s['name']]={'Id':'3'*64,'Image':'2'*64,'RestartCount':count,
          'State':{'Running':True,'StartedAt':'2026-10-12T12:00:00.000000000Z'},
          'Config':{'Labels':{app.LABEL:s['token']},'Env':['SYNTHETIC_SECRET=do-not-project']},
          'HostConfig':{'PortBindings':{}},'Mounts':[{'Source':'synthetic-private-path'}]}

    def test_never_started_stopped_ready_unhealthy_and_missing_resource(self):
        root=self.root('web')
        result=observation.project(root)
        self.assertEqual(result['state'],'stopped')
        self.assertEqual(result['components']['web']['provider_state'],'never-started')
        s,_=self.runtime(root)
        result=observation.project(root)
        self.assertEqual(result['state'],'stopped')
        self.assertEqual(result['components']['web']['uptime_reason'],'not-applicable')
        self.active(s,count=2)
        result=observation.project(root)
        self.assertEqual(result['state'],'ready')
        self.assertEqual(result['components']['web']['restart_count'],2)
        self.assertNotIn('SYNTHETIC_SECRET',json.dumps(result))
        self.assertNotIn(s['token'],json.dumps(result))
        self.assertNotIn('Mounts',json.dumps(result))
        self.readiness[s['id']]=(True,False)
        self.assertEqual(observation.project(root)['state'],'degraded')
        self.readiness[s['id']]=(False,False);self.objects.clear()
        self.assertEqual(observation.project(root)['state'],'unknown')

    def test_unowned_resource_without_receipt_and_wrong_label_are_refused(self):
        root=self.root('web')
        self.objects['gptclaw-app-web']={'Config':{'Labels':{app.LABEL:'unowned'}}}
        with self.assertRaises(app.AppError):observation.project(root)
        self.objects.clear();s,_=self.runtime(root);self.active(s)
        self.objects[s['name']]['Config']['Labels'][app.LABEL]='unowned'
        with self.assertRaises(app.AppError):observation.project(root)

    def test_state_mapping_publication_and_busy_are_separate(self):
        root=self.root('web');s,_=self.runtime(root)
        for phase,expected in (('preparing','starting'),('starting','starting'),('failed','failed'),('stopped','stopped')):
            s['phase']=phase;app.save(app.STORE/(s['id']+'.json'),s)
            self.assertEqual(observation.project(root)['state'],expected)
        self.active(s);s['health_ready']=False;app.save(app.STORE/(s['id']+'.json'),s)
        result=observation.project(root)
        self.assertEqual(result['provider_state'],'unpublished')
        self.assertEqual(result['publication']['state'],'unavailable')
        s['health_ready']=True;app.save(app.STORE/(s['id']+'.json'),s)
        self.objects[s['name']+'-job']={'Config':{'Labels':{app.LABEL:s['token']}}}
        self.assertTrue(observation.project(root)['operation_busy'])
        self.objects.pop(s['name']+'-job')
        self.assertEqual(observation.project(root)['publication']['state'],'published')
        with patch.object(app,'route_info',side_effect=app.AppError('setup')):
            result=observation.project(root)
        self.assertEqual(result['health'],'healthy')
        self.assertEqual(result['publication']['state'],'unavailable')

    def test_group_components_partial_failure_never_hide_other_health(self):
        root=self.root('group',template='notes');s,children=self.runtime(root)
        for child in children.values():self.active(child)
        s.update(phase='ready',health_ready=True);app.save(app.STORE/(s['id']+'.json'),s)
        result=observation.project(root)
        self.assertEqual(set(result['components']),{'web','api'})
        self.assertEqual(result['state'],'ready')
        self.objects[children['api']['name']]['Config']['Labels'][app.LABEL]='unowned'
        result=observation.project(root)
        self.assertEqual(result['state'],'degraded')
        self.assertEqual(result['components']['api']['state'],'unknown')
        self.assertEqual(result['components']['web']['health'],'healthy')
        self.assertEqual(result['publication']['state'],'unavailable')

    def test_database_ready_stopped_recovery_and_no_secret_projection(self):
        root=self.root('database',template='notes-postgres');s,children=self.runtime(root)
        for child in children.values():self.active(child)
        s.update(phase='ready',health_ready=True);app.save(app.STORE/(s['id']+'.json'),s)
        receipt={'project':'database','token':'4'*32,'active':'5'*32,'image':'docker.io/library/postgres@sha256:'+'6'*64,
                 'blocked':False,'operation':None}
        self.objects[db.name(receipt)]={'Id':'7'*64,'Image':'2'*64,'RestartCount':0,
            'Config':{'Labels':{app.LABEL:receipt['token']}},'HostConfig':{'PortBindings':{}},
            'State':{'Running':True,'StartedAt':'2026-10-12T12:00:00Z'}}
        with (patch.object(db,'state',return_value=receipt),patch.object(db,'verify_unit'),patch.object(db,'ready',return_value=True)):
            result=observation.project(root)
            self.assertEqual(result['state'],'ready')
            self.assertEqual(result['components']['db']['health'],'healthy')
            self.assertEqual(result['components']['db']['restart_count'],0)
            self.assertNotIn(receipt['token'],json.dumps(result))
            receipt['blocked']=True
            result=observation.project(root)
            self.assertEqual(result['components']['db']['provider_state'],'recovery-required')
            self.assertEqual(result['state'],'degraded')

    def test_timing_progression_instance_reset_unavailable_and_clock_anomaly(self):
        start=datetime.datetime(2026,10,12,12,tzinfo=datetime.timezone.utc).timestamp()
        obj={'Id':'1'*64,'RestartCount':0,'State':{'StartedAt':'2026-10-12T12:00:00.123456789Z'}}
        first=observation.timing(obj,True,start+10)
        self.assertEqual(first['uptime_seconds'],9)
        self.assertEqual(first['restart_count'],0)
        self.assertEqual(observation.timing(obj,True,start+20)['uptime_seconds'],19)
        obj['State']['StartedAt']='2026-10-12T12:00:15Z';obj['Id']='2'*64
        after=observation.timing(obj,True,start+20)
        self.assertEqual(after['uptime_seconds'],5)
        self.assertNotEqual(after['instance'],first['instance'])
        self.assertEqual(observation.timing(obj,True,start)['uptime_reason'],'clock-anomaly')
        obj['State']['StartedAt']='not-a-date';obj['RestartCount']=True
        invalid=observation.timing(obj,True,start)
        self.assertIsNone(invalid['restart_count'])
        self.assertEqual(invalid['uptime_reason'],'clock-anomaly')
        self.assertEqual(observation.timing({},False,start)['uptime_reason'],'not-applicable')

    def test_expected_root_identity_mismatch_and_no_lifecycle_operations(self):
        root=self.root('web')
        expected={'root':str(root),'id':'web','identity':[-1,-1,os.getuid()]}
        with self.assertRaises(app.AppError):observation.project(root,expected=expected)
        observation.project(root)
        self.assertTrue(self.calls)
        allowed={('podman','container','exists'),('podman','container','inspect'),('podman','network','exists'),('podman','image','inspect')}
        self.assertTrue(all(tuple(call[:3]) in allowed for call in self.calls),self.calls)


if __name__=='__main__':unittest.main()
