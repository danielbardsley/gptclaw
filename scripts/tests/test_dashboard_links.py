"""Pure link identity, URL, freshness and future capability behavior; no network/exposure."""
import copy
import json
from pathlib import Path
import socket
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import dashboard_links as links


class LinkTests(unittest.TestCase):
    def setUp(self):
        self.row={'id':'example','key':'1'*32,'kind':'group','identity_state':'valid',
                  'inventory_freshness':'current','repository':'https://github.com/example/project'}
        self.status={'state':'ready','health':'healthy','freshness':'current','last_success_at':100.,
            'publication':{'state':'published','origin':'https://forge-dev.example.ts.net'},
            'routes':{'schema_version':1,'project':'example','app_path':'/projects/example/','docs_path':'/projects/example/api/docs'}}

    def project(self,**kwargs):return links.links(self.row,self.status,100.,**kwargs)
    def find(self,kind,values=None):return next(value for value in values or self.project() if value['kind']==kind)

    def registry(self,**kwargs):
        entry={'project_key':self.row['key'],'route_class':'application-ui','state':'active',
               'url':'https://preview.example.test/projects/example/','approved_origin':'https://preview.example.test',
               'expires_at':120.}
        entry.update(kwargs)
        return {'schema_version':1,'project_key':self.row['key'],'observed_at':100.,'entries':[entry]}

    def test_exact_web_api_and_group_destinations(self):
        self.assertEqual(self.find('app')['url'],'https://forge-dev.example.ts.net/projects/example/')
        self.assertEqual(self.find('api-docs')['url'],'https://forge-dev.example.ts.net/projects/example/api/docs')
        self.assertTrue(self.find('app')['available'])
        self.row['kind']='api';self.status['routes']['docs_path']='/projects/example/docs'
        result=self.project();self.assertNotIn('app',[value['kind'] for value in result])
        self.assertEqual(self.find('api-docs',result)['url'],'https://forge-dev.example.ts.net/projects/example/docs')
        self.row['kind']='web';result=self.project()
        self.assertNotIn('api-docs',[value['kind'] for value in result])

    def test_disabled_private_links_do_not_disable_repository(self):
        for field,value in [('state','stopped'),('state','degraded'),('freshness','stale'),('health','unknown'),('operation_busy',True),('last_success_at',50.)]:
            with self.subTest(field=field,value=value):
                status={**self.status,field:value}
                result=links.links(self.row,status,100.)
                self.assertFalse(self.find('app',result)['available'])
                self.assertTrue(self.find('repository',result)['available'])
        self.row['identity_state']='conflict';self.assertFalse(self.find('app')['available'])
        self.row['identity_state']='valid';self.row['inventory_freshness']='stale'
        self.assertFalse(self.find('app')['available'])

    def test_route_capabilities_not_guessed_from_kind(self):
        self.status['routes']={}
        result=self.project()
        self.assertFalse(self.find('api-docs',result)['available'])
        self.assertEqual(self.find('api-docs',result)['reason'],'route-capability-unavailable')
        self.status['routes']={'schema_version':True,'project':'example','app_path':'/projects/example/'}
        self.assertFalse(self.find('app')['available'])

    def test_missing_logs_and_preview_are_honest_and_future_viewer_is_bound(self):
        self.assertEqual(self.find('logs')['reason'],'log-viewer-not-available')
        self.assertEqual(self.find('preview')['reason'],'preview-registry-not-available')
        capability={'schema_version':1,'viewer_available':True,'project_key':self.row['key']}
        result=self.project(logs=capability)
        self.assertEqual(self.find('logs',result)['url'],'/dashboard/logs/'+self.row['key']+'/')
        capability['project_key']='2'*32
        self.assertFalse(self.find('logs',self.project(logs=capability))['available'])
        self.row['repository']=None
        self.assertEqual(self.find('repository')['reason'],'repository-not-recorded')

    def test_active_expired_revoked_stale_absent_wrong_project_preview(self):
        result=self.project(registry=self.registry());value=self.find('preview',result)
        self.assertTrue(value['available']);self.assertEqual(value['remaining_seconds'],20.)
        for changes,reason in [({'expires_at':99.},'preview-expired'),({'state':'revoked'},'preview-revoked'),
            ({'project_key':'2'*32},'preview-target-invalid'),({'route_class':'database'},'preview-target-invalid'),
            ({'url':'https://preview.example.test/projects/example/api/docs'},'preview-target-invalid')]:
            value=self.find('preview',self.project(registry=self.registry(**changes)))
            self.assertFalse(value['available']);self.assertEqual(value['reason'],reason)
        registry=self.registry();registry['observed_at']=60.
        self.assertEqual(self.find('preview',self.project(registry=registry))['reason'],'preview-registry-stale')
        registry=self.registry();registry['entries']=[]
        self.assertEqual(self.find('preview',self.project(registry=registry))['reason'],'no-active-preview')

    def test_url_injection_and_secrets_rejected_without_network_or_execution(self):
        bad=['javascript:alert(1)','file:///etc/passwd','//github.com/a/b','https://token@github.com/a/b',
             'https://github.com:443/a/b','https://github.com/a/b?token=synthetic','https://github.com/a/../b',
             'https://github.com/a/%2e%2e/b','https://github.com/a/b#fragment','https://github.com\\@attacker.test/a/b']
        with (patch.object(socket,'create_connection',side_effect=AssertionError('network')),
              patch.object(subprocess,'Popen',side_effect=AssertionError('execution'))):
            for url in bad:
                self.row['repository']=url
                result=self.project();self.assertFalse(self.find('repository',result)['available'])
                self.assertNotIn('synthetic',json.dumps(result))
                registry=self.registry(url=url)
                self.assertFalse(self.find('preview',self.project(registry=registry))['available'])
            self.status['publication']['origin']='https://token@forge-dev.example.ts.net'
            self.assertFalse(self.find('app')['available'])


if __name__=='__main__':unittest.main()
