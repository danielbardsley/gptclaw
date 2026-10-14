"""Minimal native-session projection; no launch URLs, components or device telemetry."""
import copy
import re

from dashboard_status import number

STATES={'not-started','preparing','starting','running','stopping','stopped','failed','expired',
        'recovery-required','unknown','input-drift','stale','loopback-running','route-failed',
        'route-pending','ready','security-unavailable'}
LAYERS={'process':{'up','down','unknown'},'protocol':{'ready','failed','unknown'},
        'route':{'pending','verified','failed'}}


def project(value,project_id):
    if not isinstance(value,dict) or value.get('project')!=project_id:
        return None
    state=value.get('state')
    if not isinstance(state,str) or state not in STATES:
        return None
    if state=='not-started':
        if value.get('transport_available') is not False or value.get('origin') is not None:
            return None
        return {'schema_version':1,'project':project_id,'state':state,'generation':None,
                'expires_at':None,'observations':{k:{'state':'unknown' if k!='route' else 'pending',
                'observed_at':None} for k in LAYERS},'native_client_acceptance':'unverified',
                'source_quality':'separate-receipt'}
    if (type(value.get('schema_version')) is not int or value['schema_version'] not in {1,2}
            or value.get('adapter')!='metro-v1'
            or not isinstance(value.get('generation'),str)
            or not re.fullmatch('[0-9a-f]{32}',value['generation'])
            or not number(value.get('expires_at'))
            or type(value.get('transport_available')) is not bool
            or value['transport_available']!=(state=='ready')
            or value.get('native_client_acceptance')!='unverified'
            or value.get('source_quality')!='separate-receipt'):
        return None
    if value['schema_version']==2 and value.get('transport')!='private-tailnet-http':
        return None
    observations=value.get('observations')
    if not isinstance(observations,dict) or set(observations)!=set(LAYERS):
        return None
    clean={}
    for name,allowed in LAYERS.items():
        observation=observations[name]
        if (not isinstance(observation,dict) or not isinstance(observation.get('state'),str)
                or observation['state'] not in allowed
                or observation.get('observed_at') is not None and not number(observation['observed_at'])):
            return None
        clean[name]={'state':observation['state'],'observed_at':observation.get('observed_at')}
    return {'schema_version':1,'project':project_id,'state':state,'generation':value['generation'],
            'expires_at':value['expires_at'],'observations':clean,
            'native_client_acceptance':'unverified','source_quality':'separate-receipt'}


def public(value,freshness,now):
    result=copy.deepcopy(value)
    if result is None:
        return None
    result['freshness']=freshness
    expiry=result['expires_at']
    if expiry is not None and now>=expiry:
        result['state']='expired'
    for observation in result['observations'].values():
        stamp=observation['observed_at']
        observation['freshness']='current' if (freshness=='current' and stamp is not None
                                               and 0<=now-stamp<=30) else 'unavailable' if stamp is None else 'stale'
    if result['state']=='ready' and any(o['freshness']!='current' for o in result['observations'].values()):
        result['state']='stale'
    return result
