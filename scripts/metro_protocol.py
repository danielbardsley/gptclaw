"""Bounded loopback SDK probes; never redirects, publishes or retains manifests."""
import hashlib
import http.client
import json
import math
import re
import time
from urllib.parse import urlsplit,parse_qsl

import private_apps as app

MAX_RESPONSE=64*1024*1024
MAX_MANIFEST=1024*1024
MAX_HEADERS=16384


def origin(value):
    app.need(isinstance(value,str) and 1<=len(value)<=255,'invalid')
    try:parsed=urlsplit(value);port=parsed.port
    except ValueError:raise app.AppError('invalid') from None
    app.need(isinstance(value,str) and parsed.scheme=='https' and parsed.hostname is not None
             and re.fullmatch(r'[a-z0-9][a-z0-9.-]*\.ts\.net',parsed.hostname) is not None
             and type(port) is int and port in range(8443,8451) and not parsed.username and not parsed.password
             and parsed.path in {'','/'} and not parsed.query and not parsed.fragment,'invalid')
    return 'https://'+parsed.hostname+':'+str(port)


def relative_url(value,advertised):
    """No caller-provided upstream; reject foreign/LAN/credential URL inputs."""
    advertised=origin(advertised)
    app.need(isinstance(value,str) and len(value)<=8192 and not any(ord(c)<33 or ord(c)>126 for c in value),'invalid')
    try:parsed=urlsplit(value);port=parsed.port
    except ValueError:raise app.AppError('invalid') from None
    expected=urlsplit(advertised)
    app.need(parsed.scheme=='https' and parsed.hostname==expected.hostname and port==expected.port
             and not parsed.username and not parsed.password and not parsed.fragment
             and parsed.path.startswith('/') and not parsed.path.startswith('//')
             and len(parsed.query)<=4096,'invalid')
    # Targets are transient inputs, not retained manifest/evidence records.
    # Decode query names before checking for credential-bearing inputs.
    app.need(all(k.lower() not in {'token','access_token','auth','password','secret','key'}
                 for k,v in parse_qsl(parsed.query,keep_blank_values=True,max_num_fields=64)),'invalid')
    return parsed.path+('?' + parsed.query if parsed.query else '')


def manifest_targets(value,advertised):
    app.need(isinstance(value,dict) and isinstance(value.get('launchAsset'),dict),'health')
    launch=value['launchAsset'].get('url');bundle=relative_url(launch,advertised)
    assets=value.get('assets');app.need(isinstance(assets,list) and len(assets)<=256,'health')
    paths=[]
    for asset in assets:
        app.need(isinstance(asset,dict),'health')
        paths.append(relative_url(asset.get('url'),advertised))
    return {'bundle':bundle,'assets':paths}


def request(port,advertised,path,platform,max_bytes=MAX_RESPONSE,deadline=None,manifest=False):
    """Stream/hash one fixed owned-loopback response with time and byte ceilings."""
    advertised=origin(advertised)
    app.need(type(port) is int and port in range(18600,18632,2) and isinstance(platform,str) and platform in {'ios','android'},'invalid')
    app.need(type(max_bytes) is int and 1<=max_bytes<=MAX_RESPONSE,'invalid')
    app.need(isinstance(path,str) and path.startswith('/') and not path.startswith('//')
             and len(path)<=8192 and all(32<ord(c)<127 for c in path),'invalid')
    deadline=time.monotonic()+10 if deadline is None else deadline
    app.need(type(deadline) in {int,float} and math.isfinite(deadline),'invalid')
    if manifest:app.need(max_bytes<=MAX_MANIFEST,'invalid')
    connection=http.client.HTTPConnection('127.0.0.1',port,timeout=max(.01,min(2,deadline-time.monotonic())))
    collected=bytearray() if manifest else None;digest=hashlib.sha256();count=0
    try:
        app.need(time.monotonic()<deadline,'timeout')
        connection.request('GET',path,headers={'Host':urlsplit(advertised).netloc,'Expo-Platform':platform,
                                             'Accept':'application/expo+json' if manifest else '*/*','Connection':'close',
                                             'X-Forwarded-Proto':'https','Accept-Encoding':'identity'})
        transport=connection.sock
        transport.settimeout(max(.01,min(60,deadline-time.monotonic())))
        response=connection.getresponse()
        headers=response.getheaders()
        app.need(sum(len(k)+len(v)+4 for k,v in headers)<=MAX_HEADERS,'health')
        app.need(response.getheader('Content-Encoding') in {None,'identity'},'health')
        # Do not follow an SDK redirect even when it looks plausible.
        app.need(response.status==200,'health')
        lengths=[v for k,v in headers if k.lower()=='content-length']
        app.need(len(lengths)<=1 and (not lengths or re.fullmatch(r'[0-9]{1,9}',lengths[0]) is not None),'health')
        expected=int(lengths[0]) if lengths else None
        app.need(expected is None or expected<=max_bytes,'health')
        while not response.isclosed():
            app.need(time.monotonic()<deadline,'timeout')
            transport.settimeout(max(.01,min(2,deadline-time.monotonic())))
            chunk=response.read(min(65536,max_bytes-count+1))
            if not chunk:break
            count+=len(chunk);app.need(count<=max_bytes,'health');digest.update(chunk)
            if manifest:collected.extend(chunk)
        app.need(expected is None or count==expected,'health')
        result={'status':200,'bytes':count,'sha256':digest.hexdigest(),'platform':platform}
        if manifest:
            try:value=json.loads(collected)
            except (ValueError,UnicodeError):raise app.AppError('health') from None
            result['targets']=manifest_targets(value,advertised)
        return result
    except (OSError,http.client.HTTPException):raise app.AppError('health') from None
    finally:connection.close()


def sample(port,advertised,deadline):
    """Collect sanitized SDK evidence for both native targets, without a phone claim."""
    native={}
    for platform in ['ios','android']:
        startup=min(deadline,time.monotonic()+75)
        while True:
            app.need(time.monotonic()<startup,'health')
            try:
                manifest=request(port,advertised,'/',platform,max_bytes=MAX_MANIFEST,
                                 deadline=min(startup,time.monotonic()+5),manifest=True)
                break
            except app.AppError as error:
                if error.code!='health':raise
                time.sleep(min(.25,max(0,startup-time.monotonic())))
        targets=manifest.pop('targets')
        bundle=request(port,advertised,targets['bundle'],platform,deadline=deadline)
        assets=[]
        app.need(len(targets['assets'])<=8,'health')
        for target in targets['assets']:
            assets.append(request(port,advertised,target,platform,deadline=deadline))
        native[platform]={'manifest':manifest,'bundle':bundle,'assets':assets,
                          'bundle_exceeds_two_mib':bundle['bytes']>2*1024*1024}
    return {'protocol':'loopback-native-sdk','native':native,'physical_client_verified':False,
            'private_route_verified':False}
