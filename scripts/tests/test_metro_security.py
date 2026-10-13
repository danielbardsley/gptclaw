#!/usr/bin/env python3
"""Meaningful negative runtime-admission cases; no Metro process or exception enabled."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import metro_security as security


class SecurityTests(unittest.TestCase):
    def setUp(self):
        self.repo=Path(__file__).resolve().parents[2]
        self.value=json.loads((self.repo/'config/metro/runtime-security-v1.json').read_text())
        self.value=copy.deepcopy(self.value);self.value['approved_at']='2026-10-13T20:00:00Z'
        self.lock=(self.repo/'templates/apps/releases/expo-react-native/1.0.1/pnpm-lock.yaml').read_bytes()
        self.now=1791930000
        self.audit={'advisories':{},'metadata':{'vulnerabilities':{k:0 for k in security.LEVELS}}}
        for i,entry in enumerate(self.value['exceptions']):
            self.audit['advisories'][str(i)]={'github_advisory_id':entry['id'],'module_name':entry['package'],'severity':'high','findings':[{'version':entry['version']}]}
        self.audit['metadata']['vulnerabilities']['high']=2
    def check(self,audit=None,value=None,lock=None,now=None):
        return security.evaluate(self.audit if audit is None else audit,self.value if value is None else value,self.lock if lock is None else lock,self.now if now is None else now)
    def test_unapproved_policy_is_not_runtime_authorization(self):
        value=copy.deepcopy(self.value);value['approved_at']=None
        with self.assertRaises(security.AdmissionError):self.check(value=value)
    def test_exact_scoped_evidence_passes_and_moderates_remain_visible(self):
        self.audit['advisories']['moderate']={'github_advisory_id':'GHSA-synthetic-moderate','module_name':'synthetic','severity':'moderate','findings':[{'version':'1.0.0'}]}
        self.audit['metadata']['vulnerabilities']['moderate']=1
        result=self.check();self.assertEqual(result['vulnerabilities']['moderate'],1);self.assertEqual(len(result['temporary_exceptions']),2)
    def test_source_only_policy_is_not_accepted(self):
        for scope in ['source-check-and-export','production','public-metro']:
            value=copy.deepcopy(self.value);value['scope']=scope
            with self.assertRaises(security.AdmissionError):self.check(value=value)
    def test_missing_approval_future_approval_expiry_and_boolean_version(self):
        for key,value in [('approved_at',None),('approved_at','2026-10-27T00:00:00Z'),('expires_at','2026-10-13T00:00:00Z'),('schema_version',True),('offline',False),('owner','other')]:
            proposal=copy.deepcopy(self.value);proposal[key]=value
            with self.subTest(key=key),self.assertRaises(security.AdmissionError):self.check(value=proposal)
        with self.assertRaises(security.AdmissionError):self.check(now=security.timestamp(self.value['expires_at']))
    def test_changed_lock_graph_blocks_admission(self):
        with self.assertRaises(security.AdmissionError):self.check(lock=self.lock+b'\n')
    def test_unknown_high_changed_version_and_critical_block(self):
        for key,value in [('module_name','other'),('github_advisory_id','GHSA-new'),('severity','critical'),('findings',[{'version':'9.0.0'}])]:
            audit=copy.deepcopy(self.audit);audit['advisories']['0'][key]=value
            with self.subTest(key=key),self.assertRaises(security.AdmissionError):self.check(audit=audit)
    def test_duplicate_omitted_and_incomplete_findings_block(self):
        changes=[]
        duplicate=copy.deepcopy(self.audit);duplicate['advisories']['duplicate']=duplicate['advisories']['0'];changes.append(duplicate)
        missing=copy.deepcopy(self.audit);missing['advisories'].pop('0');changes.append(missing)
        empty=copy.deepcopy(self.audit);empty['advisories']['0']['findings']=[];changes.append(empty)
        malformed=copy.deepcopy(self.audit);malformed['metadata']['vulnerabilities']['high']=True;changes.append(malformed)
        malformed_severity=copy.deepcopy(self.audit);malformed_severity['advisories']['0']['severity']=[];changes.append(malformed_severity)
        for audit in changes:
            with self.assertRaises(security.AdmissionError):self.check(audit=audit)
    def test_policy_cannot_broaden_or_suppress_other_advisories(self):
        for entry in [{'id':'GHSA-new','package':'other','version':'1.0.0','severity':'high'},self.value['exceptions'][0]]:
            value=copy.deepcopy(self.value);value['exceptions'][1]=entry
            with self.assertRaises(security.AdmissionError):self.check(value=value)
        value=copy.deepcopy(self.value);value['ignore_severity']='high'
        with self.assertRaises(security.AdmissionError):self.check(value=value)

if __name__=='__main__':unittest.main()
