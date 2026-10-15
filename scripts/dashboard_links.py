"""Pure typed destination projection; never fetch, issue credentials or mutate exposure."""
import math
import re
from urllib.parse import urlsplit

from dashboard_inventory import repository_url

TAIL_ORIGIN=re.compile(r'https://[a-z0-9](?:[a-z0-9.-]{0,250})\.ts\.net')
KEY=re.compile(r'[0-9a-f]{32}')
PROJECT=re.compile(r'[a-z][a-z0-9]*(?:-[a-z0-9]+)*')


def safe_https(value):
    if not isinstance(value,str) or len(value)>2048 or any(ord(c)<33 for c in value) or '\\' in value or '%' in value:
        return False
    try:
        parsed=urlsplit(value)
        return (parsed.scheme=='https' and bool(parsed.hostname) and not parsed.username and not parsed.password
                and parsed.port is None and not parsed.query and not parsed.fragment
                and parsed.netloc==parsed.hostname and '..' not in parsed.path.split('/')
                and '//' not in parsed.path and re.fullmatch(r'/[A-Za-z0-9._/-]*',parsed.path) is not None)
    except ValueError:return False


def destination(kind,label,scope,*,url=None,available=False,reason=None,observed=None,expires=None,lifetime=None):
    return {'kind':kind,'label':label,'scope':scope,'url':url,'available':available,'reason':reason,
            'observed_at':observed,'expires_at':expires,'remaining_seconds':lifetime}


def preview(row, registry, now):
    missing=destination('preview','Public preview','public',reason='preview-registry-not-available')
    if registry is None:return missing
    if (not isinstance(registry,dict) or type(registry.get('schema_version')) is not int
            or registry['schema_version']!=1 or registry.get('project_key')!=row['key']
            or not isinstance(registry.get('entries'),list) or len(registry['entries'])>8):
        return {**missing,'reason':'preview-registry-invalid'}
    observed=registry.get('observed_at')
    if type(observed) not in (float,int) or not math.isfinite(observed) or observed>now or now-observed>30:
        return {**missing,'reason':'preview-registry-stale'}
    if not registry['entries']:
        return {**missing,'reason':'no-active-preview','observed_at':observed}
    results=[]
    for entry in registry['entries']:
        if not isinstance(entry,dict):continue
        url=entry.get('url');origin=entry.get('approved_origin');expires=entry.get('expires_at')
        state=entry.get('state')
        if (entry.get('project_key')!=row['key'] or entry.get('route_class')!='application-ui'
                or not safe_https(url) or not isinstance(origin,str) or not safe_https(origin+'/')
                or urlsplit(url)._replace(path='',query='',fragment='').geturl()!=origin
                or urlsplit(url).path!='/projects/'+row['id']+'/'
                or type(expires) not in (float,int) or not math.isfinite(expires)):
            results.append(destination('preview','Public preview','public',reason='preview-target-invalid',observed=observed));continue
        reason='preview-expired' if expires<=now else 'preview-revoked' if state=='revoked' else 'preview-inactive' if state!='active' else None
        if row.get('identity_state')!='valid' or row.get('inventory_freshness','current')!='current':reason='identity-unavailable'
        lifetime=max(0,min(expires-now,30-(now-observed)))
        results.append(destination('preview','Public preview','public',url=url if reason is None else None,
            available=reason is None and lifetime>0,reason=reason,observed=observed,expires=expires,lifetime=lifetime))
    return next((item for item in results if item['available']),results[0] if results else {**missing,'reason':'preview-target-invalid'})


def links(row, status, now, *, logs=None, registry=None):
    slug=row['id'];key=row['key']
    if not isinstance(slug,str) or len(slug)>48 or not PROJECT.fullmatch(slug) or not isinstance(key,str) or not KEY.fullmatch(key):
        return []
    result=[]
    status=status or {}
    descriptor=status.get('routes')
    descriptor=descriptor if isinstance(descriptor,dict) and type(descriptor.get('schema_version')) is int and descriptor['schema_version']==1 and descriptor.get('project')==slug else {}
    publication=status.get('publication',{})
    publication=publication if isinstance(publication,dict) else {}
    origin=publication.get('origin') if isinstance(publication,dict) else None
    origin=origin if isinstance(origin,str) and TAIL_ORIGIN.fullmatch(origin) and safe_https(origin+'/') else None
    identity=row.get('identity_state')=='valid' and row.get('inventory_freshness','current')=='current'
    observed=status.get('last_success_at')
    fresh=type(observed) in (float,int) and math.isfinite(observed) and 0<=now-observed<=30 and status.get('freshness')=='current'
    healthy=status.get('state')=='ready' and status.get('health')=='healthy' and not status.get('operation_busy')
    available=bool(identity and fresh and healthy and publication.get('state')=='published' and origin)
    reason=None if available else 'identity-unavailable' if not identity else 'status-stale' if not fresh else 'project-unavailable'
    for kind,label,path_key,expected in (
        ('app','Open app','app_path','/projects/'+slug+'/'),
        ('api-docs','API docs','docs_path','/projects/'+slug+('/docs' if row['kind']=='api' else '/api/docs'))):
        path=descriptor.get(path_key)
        applicable=kind=='app' and row['kind'] in {'web','group'} or kind=='api-docs' and row['kind'] in {'api','group'}
        if not applicable:continue
        supported=path==expected
        url=origin+path if supported and origin else None
        result.append(destination(kind,label,'private',url=url,available=available and supported,
                                  reason=reason if supported else 'route-capability-unavailable',observed=observed))
    repo=repository_url(row.get('repository'))
    result.append(destination('repository','Repository','repository',url=repo,available=repo is not None,
                              reason=None if repo else 'repository-not-recorded'))
    valid_logs=(isinstance(logs,dict) and type(logs.get('schema_version')) is int and logs['schema_version']==1
                and logs.get('project_key')==key and logs.get('viewer_available') is True)
    result.append(destination('logs','Logs','private',url='/dashboard/logs/'+key+'/' if valid_logs else None,
                              available=valid_logs,reason=None if valid_logs else 'log-viewer-not-available'))
    result.append(preview(row,registry,now))
    return result
