"""Read-only Expo Go eligibility; host readiness never certifies a phone."""
import hashlib
import re
import time
from urllib.parse import urlsplit

import private_apps as app
import project_dependencies as deps
import project_mobile as mobile
import project_worktrees as worktrees
import project_toolchains as tools
import metro_sessions as sessions
import metro_state as states


def profile():
    value = deps.json_data(deps.read_bytes(app.REPO/'config/mobile/expo-go-v1.json', 16384))
    fields = {'schema_version','adapter','owner','source_profile_sha256','sdk','lock_sha256',
              'config_contract','transport','certification_max_age_seconds','targets','references'}
    app.need(isinstance(value,dict) and set(value)==fields, 'mobile-policy')
    app.need(type(value['schema_version']) is int and value['schema_version']==1
             and value['adapter']=='expo-go-v1' and value['owner']=='project owner'
             and type(value['sdk']) is int and value['sdk']==57
             and value['config_contract']=='static-public-json-v1'
             and value['transport']=='private-tailnet-http'
             and type(value['certification_max_age_seconds']) is int
             and value['certification_max_age_seconds']==604800, 'mobile-policy')
    for field in ['source_profile_sha256','lock_sha256']:
        app.need(isinstance(value[field],str) and states.HEX64.fullmatch(value[field]), 'mobile-policy')
    app.need(value['source_profile_sha256']==hashlib.sha256(
        deps.read_bytes(app.REPO/'config/mobile/v1.json',65536)).hexdigest(), 'mobile-policy')
    app.need(value['references']==['https://expo.dev/go','https://docs.expo.dev/linking/into-your-app/','https://expo.dev/changelog/expo-go-57-login',
        'https://github.com/expo/expo/blob/0607af7a70d0ea3e58a6d55824aac5cfd3e78613/apps/expo-go/android/expoview/src/main/java/host/exp/expoview/Exponent.kt#L286',
        'https://github.com/expo/expo/pull/48275'], 'mobile-policy')
    targets=value['targets']
    app.need(isinstance(targets,dict) and set(targets)=={'ios','android'}, 'mobile-policy')
    for platform,target in targets.items():
        app.need(isinstance(target,dict) and set(target)=={'client_version','reported_os_versions',
                 'status','physical_verified_at','launch_rule_verified','acquisition_source','requires_cli_login','requires_http_devserver'}, 'mobile-policy')
        app.need(target['acquisition_source']=='https://expo.dev/go'
                 and target['requires_cli_login'] is (platform=='ios')
                 and target['requires_http_devserver'] is (platform=='android'), 'mobile-policy')
        app.need(target['client_version']=='57.0.9' and isinstance(target['status'],str) and target['status'] in {'candidate','verified'}, 'mobile-policy')
        if target['status']=='candidate':
            app.need(target['physical_verified_at'] is None and target['launch_rule_verified'] is False, 'mobile-policy')
        else:
            app.need(platform=='android' and states.number(target['physical_verified_at'])
                     and target['physical_verified_at']>0 and target['launch_rule_verified'] is True
                     and bool(target['reported_os_versions']), 'mobile-policy')
        app.need(isinstance(target['reported_os_versions'],list) and len(target['reported_os_versions'])<=8
                 and all(isinstance(v,str) and re.fullmatch(r'[0-9]{1,2}(?:\.[0-9]{1,2}){0,2}',v)
                         for v in target['reported_os_versions']), 'mobile-policy')
    return value


def inspect(root,platform,client_version=None,os_version=None,*,_metro=None):
    app.need(isinstance(platform,str) and platform in {'ios','android'}, 'invalid')
    for value in [client_version,os_version]:
        app.need(value is None or isinstance(value,str) and len(value)<=32
                 and re.fullmatch(r'[0-9]{1,2}(?:\.[0-9]{1,2}){0,2}',value), 'invalid')
    root,document=app.target(root)
    app.need(document['schema_version'] in {5,6,9}, 'mobile-unsupported')
    worktrees.canonical(root)
    policy=profile();target=policy['targets'][platform]
    selected=tools.selection(root)
    app.need(selected['declaration']=={'schema_version':1,**mobile.profile()['toolchain']}, 'toolchain-policy')
    package=deps.json_data(deps.read_bytes(root/'package.json',65536))
    mobile.validate_package(package)
    app.need(mobile.manifest_config(root,document), 'mobile-policy')
    lock=hashlib.sha256(deps.read_bytes(root/'pnpm-lock.yaml')).hexdigest()
    source_match=lock==policy['lock_sha256']
    metro=(_metro if _metro is not None else sessions.status(root)) if document['schema_version'] in (6,9) else {
        'state':'source-only','transport_available':False}
    reason='physical-client-and-launch-rule-unverified'
    state='check-required'
    if not source_match:
        state='unsupported';reason='source-graph-not-in-go-profile'
    elif client_version is None or os_version is None:
        reason='report-installed-client-and-os'
    elif client_version!=target['client_version']:
        state='unsupported';reason='client-version-not-in-go-profile'
    elif target['requires_http_devserver'] and metro.get('schema_version')!=2:
        state='unsupported' if metro['transport_available'] else 'check-required'
        reason='expo-go-android-requires-private-http-session'
    elif target['requires_cli_login']:
        state='unsupported';reason='expo-go-cli-login-outside-scope'
    elif os_version not in target['reported_os_versions']:
        reason='os-version-not-verified'
    elif target['status']=='verified':
        age=time.time()-target['physical_verified_at']
        if 0<=age<policy['certification_max_age_seconds']:
            state='compatible';reason='verified-client-profile'
        else:
            reason='physical-client-certification-expired'
    source_inputs={name:hashlib.sha256(deps.read_bytes(root/name)).hexdigest()
                   for name in ['app.json','package.json','pnpm-lock.yaml','.gptclaw/toolchain.json']}
    source_inputs['source_profile']=policy['source_profile_sha256']
    return {'schema_version':1,'adapter':'expo-go-v1','project':document['project']['id'],
            'platform':platform,'sdk':policy['sdk'],'source_eligible':source_match,'source_inputs':source_inputs,
            'client_version':client_version,'os_version':os_version,'client_evidence':'caller-reported',
            'acquisition_source':target['acquisition_source'],'requires_cli_login':target['requires_cli_login'],
            'requires_http_devserver':target['requires_http_devserver'],
            'state':state,'reason':reason,'metro_state':metro['state'],
            'transport_available':metro['transport_available'],
            'physical_client_acceptance':'profile-verified' if state=='compatible' else 'unverified',
            'physical_verified_at':target['physical_verified_at'],
            'certification_expires_at':(target['physical_verified_at']+policy['certification_max_age_seconds'])
                if target['physical_verified_at'] is not None else None,
            'launch_available':state=='compatible' and metro['transport_available'],
            'certification_max_age_seconds':policy['certification_max_age_seconds'],
            'follow_up':'MOB-004' if state=='unsupported' else None}


def payload(descriptor,eligibility,*,owned_origin,owned_generation,now=None):
    """Pure serializer for a certified client and the exact owned ready descriptor."""
    now=time.time() if now is None else now
    app.need(states.number(now) and isinstance(owned_generation,str)
             and states.HEX32.fullmatch(owned_generation), 'invalid')
    app.need(isinstance(eligibility,dict) and type(eligibility.get('schema_version')) is int and eligibility.get('schema_version')==1
             and eligibility.get('adapter')=='expo-go-v1' and eligibility.get('platform')=='android'
             and eligibility.get('sdk')==57 and eligibility.get('client_version')=='57.0.9'
             and eligibility.get('os_version')=='11' and eligibility.get('source_eligible') is True
             and eligibility.get('state')=='compatible' and eligibility.get('launch_available') is True
             and eligibility.get('physical_client_acceptance')=='profile-verified'
             and states.number(eligibility.get('physical_verified_at'))
             and states.number(eligibility.get('certification_expires_at'))
             and eligibility['physical_verified_at']<=now<eligibility['certification_expires_at'], 'mobile-unsupported')
    app.need(isinstance(descriptor,dict) and type(descriptor.get('schema_version')) is int
             and descriptor['schema_version']==2 and descriptor.get('adapter')=='metro-v1'
             and descriptor.get('transport')=='private-tailnet-http'
             and descriptor.get('project')==eligibility.get('project')
             and isinstance(descriptor.get('project'),str)
             and re.fullmatch('[a-z][a-z0-9]*(?:-[a-z0-9]+)*',descriptor['project'])
             and len(descriptor['project'])<=48
             and descriptor.get('generation')==owned_generation
             and descriptor.get('requested_mode')=='expo-go'
             and descriptor.get('state')=='ready' and descriptor.get('transport_available') is True
             and descriptor.get('transport_targets')==['ios','android']
             and isinstance(descriptor.get('generation'),str)
             and states.HEX32.fullmatch(descriptor['generation'])
             and states.number(descriptor.get('expires_at')) and now<descriptor['expires_at'], 'health')
    observations=descriptor.get('observations')
    app.need(isinstance(observations,dict) and set(observations)=={'process','protocol','route'}, 'health')
    for field,state in [('process','up'),('protocol','ready'),('route','verified')]:
        observation=observations[field]
        app.need(isinstance(observation,dict) and observation.get('state')==state
                 and states.number(observation.get('observed_at'))
                 and 0<=now-observation['observed_at']<=states.FRESH_SECONDS, 'health')
    from metro_protocol import origin
    advertised=origin(descriptor.get('origin'))
    app.need(advertised==descriptor['origin']==owned_origin and advertised.startswith('http://'), 'invalid')
    uri='exp://'+urlsplit(advertised).netloc+'/_gptclaw/metro-session/'+descriptor['generation']
    app.need(len(uri)<=512,'invalid')
    return {'schema_version':1,'project':descriptor['project'],'platform':'android',
            'generation':descriptor['generation'],'uri':uri,
            'expires_at':min(descriptor['expires_at'],eligibility['certification_expires_at'])}


def launch(root,platform,client_version,os_version,generation):
    """Read-only launch: no session, route, account or source mutation."""
    app.need(isinstance(generation,str) and states.HEX32.fullmatch(generation), 'invalid')
    root,receipt=sessions.receipt_for_root(root,generation)
    descriptor=sessions.status(root)
    app.need(descriptor.get('generation')==generation,'conflict')
    eligibility=inspect(root,platform,client_version,os_version,_metro=descriptor)
    value=payload(descriptor,eligibility,owned_origin=receipt['origin'],owned_generation=generation)
    # Reject a concurrent stop, renewal, expiry or profile drift before publication.
    current=sessions.status(root)
    current_eligibility=inspect(root,platform,client_version,os_version,_metro=current)
    app.need(payload(current,current_eligibility,owned_origin=receipt['origin'],owned_generation=generation)==value,'conflict')
    return {**eligibility,'launch':value}


def presentation(root,descriptor):
    """Dashboard evidence is a reviewed profile, never a detected phone version."""
    target=profile()['targets']['android']
    os_version=target['reported_os_versions'][0] if target['reported_os_versions'] else None
    value=inspect(root,'android',target['client_version'],os_version,_metro=descriptor)
    launch_value=None
    if value['launch_available']:
        _,receipt=sessions.receipt_for_root(root,descriptor['generation'])
        launch_value=payload(descriptor,value,owned_origin=receipt['origin'],owned_generation=receipt['generation'])
    fields=['schema_version','adapter','project','platform','client_version','os_version',
            'state','reason','physical_verified_at','certification_expires_at']
    return {**{key:value[key] for key in fields},'client_evidence':'reviewed-profile',
            'launch':launch_value}
