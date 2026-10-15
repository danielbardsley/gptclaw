"""Bounded Expo Go profile/launch projection; no phone discovery or lifecycle."""
import copy
import re
from dashboard_status import number

REASONS={'physical-client-and-launch-rule-unverified','source-graph-not-in-go-profile',
         'report-installed-client-and-os','client-version-not-in-go-profile',
         'expo-go-android-requires-private-http-session','expo-go-cli-login-outside-scope',
         'os-version-not-verified','verified-client-profile','physical-client-certification-expired'}


def project(value,project_id,metro):
    if (not isinstance(value,dict) or type(value.get('schema_version')) is not int
            or value['schema_version']!=1 or value.get('adapter')!='expo-go-v1'
            or value.get('project')!=project_id or value.get('platform')!='android'
            or value.get('client_evidence')!='reviewed-profile'
            or not isinstance(value.get('state'),str) or value.get('state') not in {'compatible','check-required','unsupported'}
            or not isinstance(value.get('reason'),str) or value['reason'] not in REASONS
            or value.get('client_version')!='57.0.9' or not (value.get('os_version') is None or value.get('os_version')=='11')):
        return None
    if value['state']=='compatible' and value['reason']!='verified-client-profile':return None
    verified=value.get('physical_verified_at');expiry=value.get('certification_expires_at')
    if verified is None:
        if expiry is not None or value['state']=='compatible':return None
    elif not number(verified) or not number(expiry) or expiry-verified!=604800:return None
    launch=value.get('launch')
    if launch is not None:
        if (value['state']!='compatible' or not isinstance(metro,dict) or metro.get('state')!='ready'
                or not isinstance(launch,dict) or set(launch)!={'schema_version','project','platform','generation','uri','expires_at'}
                or type(launch.get('schema_version')) is not int or launch['schema_version']!=1
                or launch.get('project')!=project_id or launch.get('platform')!='android'
                or launch.get('generation')!=metro.get('generation')
                or not isinstance(launch.get('generation'),str)
                or not re.fullmatch('[0-9a-f]{32}',launch['generation'])
                or not number(launch.get('expires_at')) or launch['expires_at']!=min(metro['expires_at'],expiry)
                or not isinstance(launch.get('uri'),str)
                or not re.fullmatch(r'exp://[a-z0-9][a-z0-9.-]*\.ts\.net:(?:844[3-9]|8450)/_gptclaw/metro-session/'+launch['generation'],launch['uri'])):
            return None
        launch=dict(launch)
    fields=['schema_version','adapter','project','platform','client_version','os_version',
            'state','reason','physical_verified_at','certification_expires_at','client_evidence']
    return {**{key:value.get(key) for key in fields},'launch':launch}


def public(value,metro,freshness,now):
    result=copy.deepcopy(value)
    if result is None:return None
    expiry=result['certification_expires_at'];verified=result['physical_verified_at']
    if result['state']=='compatible' and (expiry is None or verified is None or not verified<=now<expiry):
        result.update(state='check-required',reason='physical-client-certification-expired',launch=None)
    launch=result['launch']
    if launch is not None and (freshness!='current' or not isinstance(metro,dict)
            or metro.get('state')!='ready' or metro.get('generation')!=launch['generation']
            or now>=launch['expires_at']):
        result['launch']=None
    return result
