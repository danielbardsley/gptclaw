"""Exact Metro runtime admission; source-only exceptions confer no permission."""
from datetime import datetime, timezone
import hashlib
import json
import math
import os
import stat
from pathlib import Path
import re

SCOPE='private-metro-session'
EXPECTED={('GHSA-86w9-cpqp-85rv','node-forge','1.4.0','high'),
          ('GHSA-vfj7-8cjw-p6xm','braces','3.0.3','high')}
LEVELS={'info','low','moderate','high','critical'}


class AdmissionError(ValueError):
    pass


def require(value):
    if not value:raise AdmissionError('Metro runtime security admission failed')


def timestamp(value):
    require(isinstance(value,str) and bool(re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ',value)))
    try:return datetime.fromisoformat(value.replace('Z','+00:00')).timestamp()
    except ValueError:raise AdmissionError('Invalid runtime security date') from None


def policy(value,now=None,approved=True):
    now=datetime.now(timezone.utc).timestamp() if now is None else now
    require(type(now) in {int,float} and math.isfinite(now))
    require(isinstance(value,dict) and set(value)=={'schema_version','scope','approved_at','owner','expires_at','lock_sha256','sdk','expo_cli','max_session_seconds','offline','exceptions'})
    require(type(value['schema_version']) is int and value['schema_version']==1 and value['scope']==SCOPE)
    require(value['owner']=='project owner' and value['offline'] is True)
    require(type(value['sdk']) is int and value['sdk']==57 and value['expo_cli']=='57.0.29')
    require(type(value['max_session_seconds']) is int and value['max_session_seconds']==28800)
    require(isinstance(value['lock_sha256'],str) and bool(re.fullmatch('[0-9a-f]{64}',value['lock_sha256'])))
    expiry=timestamp(value['expires_at']);require(now<expiry)
    if value['approved_at'] is None:require(not approved)
    else:require(timestamp(value['approved_at'])<=now and timestamp(value['approved_at'])<expiry)
    require(isinstance(value['exceptions'],list) and len(value['exceptions'])==2)
    entries=[]
    for entry in value['exceptions']:
        require(isinstance(entry,dict) and set(entry)=={'id','package','version','severity'})
        require(all(isinstance(v,str) for v in entry.values()))
        entries.append((entry['id'],entry['package'],entry['version'],entry['severity']))
    require(len(set(entries))==2 and set(entries)==EXPECTED)
    return value


def evaluate(report,value,lock_bytes,now=None):
    """No side effects/network; rejects incomplete or unexpected advisory evidence."""
    value=policy(value,now)
    require(isinstance(lock_bytes,bytes) and hashlib.sha256(lock_bytes).hexdigest()==value['lock_sha256'])
    require(isinstance(report,dict) and isinstance(report.get('advisories'),dict) and len(report['advisories'])<=4096)
    metadata=report.get('metadata');require(isinstance(metadata,dict))
    reported=metadata.get('vulnerabilities');require(isinstance(reported,dict) and set(reported)==LEVELS)
    require(all(type(v) is int and 0<=v<=4096 for v in reported.values()))
    counts={k:0 for k in LEVELS};accepted=[];ids=set()
    for finding in report['advisories'].values():
        require(isinstance(finding,dict) and isinstance(finding.get('severity'),str) and finding['severity'] in LEVELS)
        severity=finding['severity'];counts[severity]+=1
        require(isinstance(finding.get('module_name'),str) and isinstance(finding.get('github_advisory_id'),str))
        ident=(finding['github_advisory_id'],finding['module_name']);require(ident not in ids);ids.add(ident)
        versions=finding.get('findings');require(isinstance(versions,list) and 1<=len(versions)<=4096)
        require(all(isinstance(v,dict) and isinstance(v.get('version'),str) for v in versions))
        if severity in {'high','critical'}:
            for version in versions:require((ident[0],ident[1],version['version'],severity) in EXPECTED)
            accepted.append(ident[0])
    require(counts==reported)
    return {'scope':SCOPE,'vulnerabilities':counts,'temporary_exceptions':sorted(accepted),
            'expires_at':value['expires_at'],'lock_sha256':value['lock_sha256']}


def read_policy(repo,now=None,approved=True):
    # Repository/provider-owned input, never a project-supplied exception file.
    path=Path(repo)/'config/metro/runtime-security-v1.json'
    try:
        fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
        with os.fdopen(fd,'rb') as source:
            info=os.fstat(source.fileno())
            require(stat.S_ISREG(info.st_mode) and info.st_uid==os.getuid() and info.st_nlink==1 and info.st_size<=16384)
            value=json.loads(source.read(16385))
    except (OSError,ValueError):raise AdmissionError('Invalid runtime policy') from None
    return policy(value,now,approved)
