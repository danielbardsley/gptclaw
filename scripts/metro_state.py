"""Typed Metro ownership/observation boundary; no execution or device inference."""
import math
from pathlib import Path
import re
import time

import private_apps as app
from metro_protocol import origin as private_origin

PHASES={'preparing','starting','running','stopping','stopped','failed','expired','recovery-required'}
INACTIVE={'stopped','failed','expired','recovery-required'}
FRESH_SECONDS=30
HEX64=re.compile('[0-9a-f]{64}')
HEX32=re.compile('[0-9a-f]{32}')


def need(value):app.need(value,'conflict')
def number(value):return type(value) in {int,float} and math.isfinite(value) and value>=0

def validate(value):
    fields={'schema_version','adapter','project','root','canonical_key','name','generation','token','image',
            'input_digest','policy_digest','unit_digest','metro_port','proxy_port','origin','phase',
            'started_at','expires_at','operation_id','operation_result','observations'}
    need(isinstance(value,dict) and type(value.get('schema_version')) is int
         and value['schema_version'] in {1,2})
    if value['schema_version']==2:fields.add('transport')
    need(set(value)==fields and value['adapter']=='metro-v1')
    project=value['project'];need(isinstance(project,str) and len(project)<=48 and re.fullmatch('[a-z][a-z0-9]*(?:-[a-z0-9]+)*',project) is not None)
    root=value['root'];need(isinstance(root,str) and len(root)<=4096 and re.fullmatch('[A-Za-z0-9/._-]+',root) is not None)
    path=Path(root)
    need(path.is_absolute() and '..' not in path.parts and path.is_relative_to(app.PROJECTS)
         and path not in {app.PROJECTS,app.REPO} and not {'.gptclaw-runtime','.gptclaw-worktrees'} & set(path.parts))
    need(value['name']=='gptclaw-metro-'+project)
    for field in ['canonical_key','input_digest','policy_digest','unit_digest']:
        need(isinstance(value[field],str) and HEX64.fullmatch(value[field]) is not None)
    for field in ['generation','token','operation_id']:
        need(isinstance(value[field],str) and HEX32.fullmatch(value[field]) is not None)
    need(isinstance(value['image'],str) and re.fullmatch('sha256:[0-9a-f]{64}',value['image']) is not None)
    need(type(value['metro_port']) is int and value['metro_port'] in range(18600,18632,2))
    need(type(value['proxy_port']) is int and value['proxy_port']==value['metro_port']+1)
    need(private_origin(value['origin'])==value['origin'])
    if value['schema_version']==1:
        need(value['origin'].startswith('https://'))
    else:
        need(value['transport']=='private-tailnet-http' and value['origin'].startswith('http://'))
    need(isinstance(value['phase'],str) and value['phase'] in PHASES)
    need(isinstance(value['operation_result'],str) and value['operation_result'] in {'running','passed','failed','unknown'})
    need(number(value['started_at']) and number(value['expires_at']) and 0<value['expires_at']-value['started_at']<=28800)
    observations=value['observations'];need(isinstance(observations,dict) and set(observations)=={'process','protocol','route'})
    for field,states in [('process',{'up','down','unknown'}),('protocol',{'ready','failed','unknown'}),('route',{'pending','verified','failed'})]:
        observation=observations[field]
        need(isinstance(observation,dict) and set(observation)=={'state','observed_at'})
        need(isinstance(observation['state'],str) and observation['state'] in states)
        need(observation['observed_at'] is None or number(observation['observed_at']))
        need(observation['observed_at'] is None or observation['observed_at']>=value['started_at'])
        if observation['observed_at'] is None:need(observation['state'] in {'unknown','pending'})
    return value


def descriptor(value,*,project,root,canonical_key,input_digest,now=None):
    """Pure projection; callers must supply actual independent observations."""
    value=validate(value);now=time.time() if now is None else now;need(number(now))
    need(value['project']==project and value['root']==str(root) and value['canonical_key']==canonical_key)
    state=value['phase'];observations=value['observations']
    def fresh(field):
        stamp=observations[field]['observed_at']
        return stamp is not None and 0<=now-stamp<=FRESH_SECONDS
    if state not in INACTIVE:
        if now>=value['expires_at']:state='expired'
        elif now<value['started_at']:state='unknown'
        elif value['input_digest']!=input_digest:state='input-drift'
        elif not fresh('process'):state='stale'
        elif observations['process']['state']=='down':state='failed'
        elif observations['process']['state']!='up':state='unknown'
        elif observations['protocol']['state']=='failed':state='failed' if fresh('protocol') else 'stale'
        elif observations['protocol']['state']!='ready':state='loopback-running'
        elif not fresh('protocol'):state='stale'
        elif observations['route']['state']=='failed':state='route-failed' if fresh('route') else 'stale'
        elif observations['route']['state']!='verified':state='route-pending'
        elif not fresh('route'):state='stale'
        elif value['phase']=='running' and value['operation_result']=='passed':state='ready'
        else:state=value['phase']
    ready=state=='ready'
    return {'schema_version':value['schema_version'],'adapter':'metro-v1','project':project,'generation':value['generation'],
            **({'transport':'private-tailnet-http'} if value['schema_version']==2 else {}),
            'state':state,'transport_available':ready,'origin':value['origin'] if ready else None,
            'expires_at':value['expires_at'],'observations':{k:dict(v) for k,v in observations.items()},
            'requested_mode':'expo-go','transport_targets':['ios','android'],
            'native_client_acceptance':'unverified','source_quality':'separate-receipt'}
