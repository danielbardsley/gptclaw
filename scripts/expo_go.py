"""Read-only Expo Go eligibility; host readiness never certifies a phone."""
import hashlib
import re

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
             and value['transport']=='private-tailnet-https'
             and type(value['certification_max_age_seconds']) is int
             and value['certification_max_age_seconds']==604800, 'mobile-policy')
    for field in ['source_profile_sha256','lock_sha256']:
        app.need(isinstance(value[field],str) and states.HEX64.fullmatch(value[field]), 'mobile-policy')
    app.need(value['source_profile_sha256']==hashlib.sha256(
        deps.read_bytes(app.REPO/'config/mobile/v1.json',65536)).hexdigest(), 'mobile-policy')
    app.need(value['references']==['https://expo.dev/go','https://docs.expo.dev/linking/into-your-app/'], 'mobile-policy')
    targets=value['targets']
    app.need(isinstance(targets,dict) and set(targets)=={'ios','android'}, 'mobile-policy')
    for target in targets.values():
        app.need(isinstance(target,dict) and set(target)=={'client_version','reported_os_versions',
                 'status','physical_verified_at','launch_rule_verified'}, 'mobile-policy')
        app.need(target['client_version']=='57.0.9' and target['status']=='candidate'
                 and target['physical_verified_at'] is None and target['launch_rule_verified'] is False,
                 'mobile-policy')
        app.need(isinstance(target['reported_os_versions'],list) and len(target['reported_os_versions'])<=8
                 and all(isinstance(v,str) and re.fullmatch(r'[0-9]{1,2}(?:\.[0-9]{1,2}){0,2}',v)
                         for v in target['reported_os_versions']), 'mobile-policy')
    return value


def inspect(root,platform,client_version=None,os_version=None):
    app.need(platform in {'ios','android'}, 'invalid')
    for value in [client_version,os_version]:
        app.need(value is None or isinstance(value,str) and len(value)<=32
                 and re.fullmatch(r'[0-9]{1,2}(?:\.[0-9]{1,2}){0,2}',value), 'invalid')
    root,document=app.target(root)
    app.need(document['schema_version'] in {5,6}, 'mobile-unsupported')
    worktrees.canonical(root)
    policy=profile();target=policy['targets'][platform]
    selected=tools.selection(root)
    app.need(selected['declaration']=={'schema_version':1,**mobile.profile()['toolchain']}, 'toolchain-policy')
    package=deps.json_data(deps.read_bytes(root/'package.json',65536))
    mobile.validate_package(package)
    app.need(mobile.manifest_config(root,document), 'mobile-policy')
    lock=hashlib.sha256(deps.read_bytes(root/'pnpm-lock.yaml')).hexdigest()
    source_match=lock==policy['lock_sha256']
    metro=sessions.status(root) if document['schema_version']==6 else {
        'state':'source-only','transport_available':False}
    reason='physical-client-and-launch-rule-unverified'
    state='check-required'
    if not source_match:
        state='unsupported';reason='source-graph-not-in-go-profile'
    elif client_version is None or os_version is None:
        reason='report-installed-client-and-os'
    elif client_version!=target['client_version']:
        state='unsupported';reason='client-version-not-in-go-profile'
    elif os_version not in target['reported_os_versions']:
        reason='os-version-not-verified'
    source_inputs={name:hashlib.sha256(deps.read_bytes(root/name)).hexdigest()
                   for name in ['app.json','package.json','pnpm-lock.yaml','.gptclaw/toolchain.json']}
    source_inputs['source_profile']=policy['source_profile_sha256']
    return {'schema_version':1,'adapter':'expo-go-v1','project':document['project']['id'],
            'platform':platform,'sdk':policy['sdk'],'source_eligible':source_match,'source_inputs':source_inputs,
            'client_version':client_version,'os_version':os_version,'client_evidence':'caller-reported',
            'state':state,'reason':reason,'metro_state':metro['state'],
            'transport_available':metro['transport_available'],
            'physical_client_acceptance':'unverified','launch_available':False,
            'certification_max_age_seconds':policy['certification_max_age_seconds'],
            'follow_up':'MOB-004' if state=='unsupported' else None}
