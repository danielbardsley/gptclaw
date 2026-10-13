"""Bounded shared status snapshots and observed transitions; no persistent history."""
from concurrent.futures import ThreadPoolExecutor, as_completed
import copy
import math
import os
import re
import threading
import time

STATES={'ready','stopped','starting','failed','degraded','unknown'}
PROVIDER_STATES={'ready','stopped','preparing','starting','failed','degraded','unhealthy',
                 'unpublished','recovery-required','uninitialized','never-started','resource-unavailable','unknown'}
REASONS={'observation-unavailable','observation-timeout','observation-invalid','ownership-conflict',
         'observation-inconsistent','clock-anomaly','unsupported','inventory-stale','capacity-limited'}
METRIC_REASONS={'not-applicable','unavailable','unsupported','clock-anomaly'}
COMPONENTS={'web','api','db'}


def status_job(binding):
    from dashboard_observation import job
    return job(binding)


def number(value):
    return type(value) in (float,int) and math.isfinite(value) and value>=0


def enum(raw, key, allowed, fallback=None):
    value=raw.get(key)
    return value if isinstance(value,str) and value in allowed else fallback


def project_fields(raw):
    state=enum(raw,'state',STATES,'unknown')
    provider=enum(raw,'provider_state',PROVIDER_STATES,'unknown')
    health=enum(raw,'health',{'healthy','unhealthy','unknown','not-applicable'},'unknown')
    return {'state':state,'provider_state':provider,'health':health,
            'operation_busy':raw.get('operation_busy') is True,
            'reason':enum(raw,'reason',REASONS)}


def component_fields(raw):
    value=project_fields(raw)
    for key,reason_key,maximum in (('uptime_seconds','uptime_reason',10**12),('restart_count','restart_reason',2**31-1)):
        metric=raw.get(key)
        if type(metric) is int and 0<=metric<=maximum:
            value[key],value[reason_key]=metric,None
        else:
            value[key]=None
            reason=raw.get(reason_key)
            value[reason_key]=reason if isinstance(reason,str) and reason in METRIC_REASONS else 'unavailable'
    instance=raw.get('instance')
    value['_instance']=instance if isinstance(instance,str) and re.fullmatch(r'[0-9a-f]{32}',instance) else None
    return value


class StatusStore:
    def __init__(self, run, *, clock=time.time, observe=status_job, deadline=4, window=20, workers=None):
        self.run,self.clock,self.observe=run,clock,observe
        self.deadline,self.window=deadline,window
        self.workers=workers if workers is not None else min(4,max(1,os.cpu_count() or 1))
        self.lock=threading.RLock()
        self.round_lock=threading.Lock()
        self.entries={}
        self.offset=0
        self.capacity={'limited':False,'projects':0,'supported_projects':window}

    def _success(self, previous, value, observed):
        if value['state']=='unknown':
            return self._failure(previous,value.get('reason') or 'observation-unavailable')
        if previous and previous.get('last_success_at') is not None and observed<previous['last_success_at']:
            return self._failure(previous,'clock-anomaly')
        old_success=previous.get('last_success_at') if previous else None
        fingerprint=(value['state'],value['health'],value['operation_busy'],value.get('_instance'))
        transition=previous.get('last_observed_change') if previous else None
        gap=bool(previous and (previous.get('failure') or old_success is not None and observed-old_success>30))
        if transition is None:
            transition={'kind':'first-observed','at':observed,'after_gap':False,'previous_observation_at':None}
        elif previous.get('_fingerprint')!=fingerprint:
            transition={'kind':'change-detected','at':observed,'after_gap':gap,
                        'previous_observation_at':old_success if gap else None}
        return {**value,'observed_at':observed,'last_success_at':observed,
                'last_observed_change':transition,'failure':None,'_fingerprint':fingerprint}

    def _failure(self, previous, reason):
        if previous:
            result=copy.deepcopy(previous);result['failure']=reason
            return result
        return {**project_fields({}),'observed_at':None,'last_success_at':None,
                'last_observed_change':None,'failure':reason}

    def update(self, key, binding, result):
        now=self.clock()
        with self.lock:
            if key not in self.entries and len(self.entries)>=256:
                return
            previous=self.entries.get(key,{'overall':None,'components':{},'publication':{'state':'unavailable','origin':None}})
            if (not isinstance(result,dict) or type(result.get('observation_schema')) is not int or result['observation_schema']!=1
                    or result.get('project')!=binding['id'] or not number(result.get('observed_at'))
                    or not isinstance(result.get('components'),dict)
                    or set(result['components'])!=set(binding['components'])
                    or not set(binding['components'])<=COMPONENTS
                    or result['observed_at']>now+1):
                reason=result.get('error') if isinstance(result,dict) else None
                reason=reason if isinstance(reason,str) and reason in REASONS else 'observation-invalid'
                previous['overall']=self._failure(previous['overall'],reason)
                previous['components']={name:self._failure(previous['components'].get(name),reason)
                                        for name in binding['components']}
                previous['publication']={'state':'unavailable','origin':None}
                self.entries[key]=previous
                return
            observed=result['observed_at']
            current={'overall':self._success(previous['overall'],project_fields(result),observed),
                     'components':{},'publication':{'state':'unavailable','origin':None}}
            for name in binding['components']:
                raw=result['components'][name]
                if not isinstance(raw,dict):raw={}
                current['components'][name]=self._success(previous['components'].get(name),component_fields(raw),observed)
            publication=result.get('publication',{})
            if isinstance(publication,dict):
                origin=publication.get('origin')
                if isinstance(origin,str) and re.fullmatch(r'https://[a-z0-9.-]+\.ts\.net',origin):
                    current['publication']={'state':'published' if publication.get('state')=='published' else 'unavailable','origin':origin}
            version=result.get('provider_version')
            current['provider_version']=version if isinstance(version,str) and re.fullmatch(r'\d{1,3}\.\d{1,3}\.\d{1,3}',version) else None
            routes=result.get('routes',{})
            if isinstance(routes,dict) and type(routes.get('schema_version')) is int and routes['schema_version']==1 and routes.get('project')==binding['id']:
                prefix='/projects/'+binding['id']+'/'
                current['routes']={'schema_version':1,'project':binding['id'],
                    'app_path':prefix if routes.get('app_path')==prefix else None,
                    'docs_path':routes['docs_path'] if routes.get('docs_path') in (prefix+'docs',prefix+'api/docs') else None}
            self.entries[key]=current

    def round(self, bindings):
        if not self.round_lock.acquire(blocking=False):
            return False
        try:
            keys=sorted(key for key,binding in bindings.items() if binding['components'])
            with self.lock:
                self.capacity={'limited':len(keys)>self.window,'projects':len(keys),'supported_projects':self.window}
            if not keys:return True
            offset=self.offset%len(keys)
            selected=(keys[offset:]+keys[:offset])[:self.window]
            self.offset=(offset+len(selected))%len(keys)
            with ThreadPoolExecutor(max_workers=self.workers) as pool:
                futures={pool.submit(self.run,self.observe,bindings[key],self.deadline,65536):key for key in selected}
                for future in as_completed(futures):
                    key=futures[future]
                    try:result=future.result()
                    except Exception:result={'error':'observation-unavailable'}
                    self.update(key,bindings[key],result)
            return True
        finally:
            self.round_lock.release()

    def retain(self, keys, *, complete):
        if complete:
            with self.lock:
                self.entries={key:value for key,value in self.entries.items() if key in keys}

    def _public(self, entry):
        value={key:copy.deepcopy(val) for key,val in entry.items() if not key.startswith('_') and key!='failure'}
        last=entry.get('last_success_at')
        stale=last is not None and (entry.get('failure') is not None or self.clock()-last>30 or self.clock()<last)
        value['freshness']='stale' if stale else 'current' if last is not None else 'unavailable'
        if entry.get('failure'):value['reason']=entry['failure']
        return value

    def snapshot(self, key, binding):
        if not binding['components']:
            return {**self._public(self._failure(None,'unsupported')),'components':{},'publication':{'state':'unavailable','origin':None},'provider_version':None}
        with self.lock:
            entry=self.entries.get(key)
            if entry is None or set(entry['components'])!=set(binding['components']):
                reason='capacity-limited' if len(self.entries)>=256 else 'observation-unavailable'
                empty=self._public(self._failure(None,reason))
                return {**empty,'components':{name:copy.deepcopy(empty) for name in binding['components']},
                        'publication':{'state':'unavailable','origin':None},'provider_version':None}
            overall=self._public(entry['overall'])
            components={name:self._public(value) for name,value in entry['components'].items()}
            publication=copy.deepcopy(entry['publication'])
            if overall['freshness']!='current' or any(c['freshness']!='current' for c in components.values()):
                publication['state']='unavailable'
            return {**overall,'components':components,'publication':publication,
                    'provider_version':entry.get('provider_version'),'routes':copy.deepcopy(entry.get('routes'))}
