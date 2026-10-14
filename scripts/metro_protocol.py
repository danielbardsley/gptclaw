"""Bounded owned SDK probes; never redirects, publishes or retains manifests."""
import hashlib
import base64
import os
import socket
import ssl
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



class ProbeError(app.AppError):
    def __init__(self,reason,**fields):
        super().__init__('health')
        self.diagnostic={'reason':reason,**fields}

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


def destination(port,advertised,via_proxy,via_private):
    advertised=origin(advertised)
    app.need(type(via_proxy) is bool and type(via_private) is bool and type(port) is int,'invalid')
    if via_private:
        parsed=urlsplit(advertised)
        app.need(via_proxy and parsed.hostname==app.node_identity() and port==parsed.port,'invalid')
        return parsed.hostname,port
    app.need(port in range(18601 if via_proxy else 18600,18632,2),'invalid')
    return '127.0.0.1',port

def request(port,advertised,path,platform,max_bytes=MAX_RESPONSE,deadline=None,manifest=False,via_proxy=False,via_private=False):
    """Stream/hash a fixed loopback or default-trust private TLS response."""
    advertised=origin(advertised)
    host,port=destination(port,advertised,via_proxy,via_private)
    app.need(isinstance(platform,str) and platform in {'ios','android'},'invalid')
    app.need(type(max_bytes) is int and 1<=max_bytes<=MAX_RESPONSE,'invalid')
    app.need(isinstance(path,str) and path.startswith('/') and not path.startswith('//')
             and len(path)<=8192 and all(32<ord(c)<127 for c in path),'invalid')
    deadline=time.monotonic()+10 if deadline is None else deadline
    app.need(type(deadline) in {int,float} and math.isfinite(deadline),'invalid')
    if manifest:app.need(max_bytes<=MAX_MANIFEST,'invalid')
    connection_class=http.client.HTTPSConnection if via_private else http.client.HTTPConnection
    connection=connection_class(host,port,timeout=max(.01,min(2,deadline-time.monotonic())))
    collected=bytearray() if manifest else None;digest=hashlib.sha256();count=0
    try:
        app.need(time.monotonic()<deadline,'timeout')
        connection.request('GET',path,headers={'Host':urlsplit(advertised).netloc,'Expo-Platform':platform,
                                             'Accept':'application/expo+json' if manifest else '*/*','Connection':'close',
                                             'X-Forwarded-Proto':'https','Accept-Encoding':'identity'})
        transport=connection.sock
        transport.settimeout(max(.01,deadline-time.monotonic()))
        response=connection.getresponse()
        app.need(time.monotonic()<deadline,'timeout')
        headers=response.getheaders()
        app.need(sum(len(k)+len(v)+4 for k,v in headers)<=MAX_HEADERS,'health')
        app.need(response.getheader('Content-Encoding') in {None,'identity'},'health')
        # Do not follow an SDK redirect even when it looks plausible.
        if response.status!=200:raise ProbeError('http-status',status=response.status)
        lengths=[v for k,v in headers if k.lower()=='content-length']
        app.need(len(lengths)<=1 and (not lengths or re.fullmatch(r'[0-9]{1,9}',lengths[0]) is not None),'health')
        expected=int(lengths[0]) if lengths else None
        app.need(expected is None or expected<=max_bytes,'health')
        while not response.isclosed():
            app.need(time.monotonic()<deadline,'timeout')
            transport.settimeout(max(.01,min(30,deadline-time.monotonic())))
            chunk=response.read1(min(65536,max_bytes-count+1))
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
    except OSError as error:raise ProbeError('socket',errno=error.errno,timeout=isinstance(error,TimeoutError)) from None
    except http.client.HTTPException:raise ProbeError('http-framing') from None
    finally:connection.close()



def websocket(port,advertised,path,deadline,via_proxy=False,via_private=False):
    """Bounded RFC6455 handshake/ping only; never persist SDK message content."""
    advertised=origin(advertised)
    host,port=destination(port,advertised,via_proxy,via_private)
    app.need(path in {'/message','/hot'},'invalid')
    app.need(type(deadline) in {int,float} and math.isfinite(deadline) and time.monotonic()<deadline,'invalid')
    key=base64.b64encode(os.urandom(16)).decode()
    expected=base64.b64encode(hashlib.sha1((key+'258EAFA5-E914-47DA-95CA-C5AB0DC85B11').encode()).digest()).decode()
    nonce=os.urandom(8);mask=os.urandom(4)
    limit=min(deadline,time.monotonic()+5)
    try:
        with socket.create_connection((host,port),timeout=max(.01,min(2,limit-time.monotonic()))) as raw:
            raw.settimeout(max(.01,limit-time.monotonic()))
            peer=ssl.create_default_context().wrap_socket(raw,server_hostname=host) if via_private else raw
            with peer:
                return websocket_exchange(peer,path,advertised,key,expected,nonce,mask,limit)
    except (OSError,UnicodeError,IndexError):raise ProbeError('websocket-transport') from None


def websocket_exchange(peer,path,advertised,key,expected,nonce,mask,limit):
    request=('GET '+path+' HTTP/1.1\r\nHost: '+urlsplit(advertised).netloc+'\r\nOrigin: '+advertised+
             '\r\nConnection: Upgrade\r\nUpgrade: websocket\r\nSec-WebSocket-Version: 13\r\nSec-WebSocket-Key: '+key+'\r\n\r\n')
    peer.sendall(request.encode());buffer=bytearray()
    while b'\r\n\r\n' not in buffer:
        app.need(time.monotonic()<limit,'timeout')
        chunk=peer.recv(1024);app.need(bool(chunk),'health');buffer.extend(chunk)
        app.need(len(buffer)<=MAX_HEADERS,'health')
    header,tail=bytes(buffer).split(b'\r\n\r\n',1)
    lines=header.decode('ascii').split('\r\n');app.need(lines[0].split(' ')[1]=='101','health')
    headers={}
    for line in lines[1:]:
        app.need(':' in line,'health');name,value=line.split(':',1);name=name.lower()
        app.need(name not in headers,'health');headers[name]=value.strip()
    app.need(headers.get('sec-websocket-accept')==expected and headers.get('upgrade','').lower()=='websocket'
             and 'upgrade' in [x.strip().lower() for x in headers.get('connection','').split(',')],'health')
    peer.sendall(bytes([0x89,0x80|len(nonce)])+mask+bytes(b^mask[i%4] for i,b in enumerate(nonce)))
    pending=bytearray(tail)
    def read(count):
        while len(pending)<count:
            app.need(time.monotonic()<limit,'timeout');peer.settimeout(max(.01,limit-time.monotonic()))
            chunk=peer.recv(min(4096,count-len(pending)));app.need(bool(chunk),'health');pending.extend(chunk)
        data=bytes(pending[:count]);del pending[:count];return data
    total=0
    for _ in range(16):
        a,b=read(2);app.need(a&0x70==0 and b&0x80==0,'health');length=b&127;opcode=a&15
        if length==126:length=int.from_bytes(read(2),'big')
        elif length==127:length=int.from_bytes(read(8),'big')
        app.need(length<=65536 and total+length<=131072 and (opcode not in {8,9,10} or length<=125),'health')
        payload=read(length);total+=length
        if opcode==10:
            app.need(payload==nonce,'health')
            close_mask=os.urandom(4);peer.sendall(bytes([0x88,0x80])+close_mask)
            return {'status':101,'ping_pong':True,'bytes_observed':total,'path':path}
        app.need(opcode!=8,'health')
    raise ProbeError('websocket-frame-limit')

def sample(port,advertised,deadline,generation=None,via_private=False):
    """Collect sanitized SDK evidence for both native targets, without a phone claim."""
    app.need(generation is None or isinstance(generation,str) and re.fullmatch('[0-9a-f]{32}',generation),'invalid')
    via_proxy=generation is not None
    app.need(type(via_private) is bool and (not via_private or via_proxy),'invalid')
    destination(port,advertised,via_proxy,via_private)
    manifest_path='/' if generation is None else '/_gptclaw/metro-session/'+generation
    native={}
    for platform in ['ios','android']:
        startup=min(deadline,time.monotonic()+75)
        last_error=None
        while True:
            if time.monotonic()>=startup:raise ProbeError('manifest-startup-deadline',last_error=last_error)
            try:
                manifest=request(port,advertised,manifest_path,platform,max_bytes=MAX_MANIFEST,
                                 deadline=min(startup,time.monotonic()+5),manifest=True,via_proxy=via_proxy,via_private=via_private)
                break
            except app.AppError as error:
                if error.code!='health':raise
                last_error=error.diagnostic if isinstance(error,ProbeError) else {'reason':error.code}
                time.sleep(min(.25,max(0,startup-time.monotonic())))
        targets=manifest.pop('targets')
        bundle=request(port,advertised,targets['bundle'],platform,deadline=deadline,via_proxy=via_proxy,via_private=via_private)
        assets=[]
        app.need(len(targets['assets'])<=8,'health')
        for target in targets['assets']:
            assets.append(request(port,advertised,target,platform,deadline=deadline,via_proxy=via_proxy,via_private=via_private))
        asset=request(port,advertised,'/assets/assets/icon.png?platform='+platform,platform,deadline=deadline,via_proxy=via_proxy,via_private=via_private)
        source_map_path=targets['bundle'].replace('.bundle?', '.map?',1)
        app.need(source_map_path!=targets['bundle'],'health')
        source_map=request(port,advertised,source_map_path,platform,deadline=deadline,via_proxy=via_proxy,via_private=via_private)
        native[platform]={'starter_icon':asset,'source_map':source_map,'manifest':manifest,'bundle':bundle,'assets':assets,
                          'bundle_exceeds_two_mib':bundle['bytes']>2*1024*1024}
    channels=[websocket(port,advertised,path,deadline,via_proxy=via_proxy,via_private=via_private) for path in ['/message','/hot']]
    return {'protocol':'private-tls-native-sdk' if via_private else 'loopback-native-sdk','via_proxy':via_proxy,'native':native,'websockets':channels,'physical_client_verified':False,
            'private_route_verified':via_private}


def private_sample(root,generation,seconds=240):
    """Require current exact route ownership before/after sanitized TLS probes."""
    import metro_sessions as sessions
    import metro_routes as routes
    app.need(type(seconds) is int and 1<=seconds<=300,'invalid')
    root,value=sessions.receipt_for_root(root,generation)
    def eligible():
        current=sessions.proxy_receipt(value)
        sessions.verify_unit(current)
        app.need(current['phase']=='running' and current['operation_result']=='passed'
                 and time.time()<current['expires_at']
                 and sessions.ownership('container',current['name'],current['token'])=='owned'
                 and routes.observe(current)['state']=='verified','health')
        return current
    eligible()
    deadline=time.monotonic()+min(seconds,max(0,value['expires_at']-time.time()))
    evidence=sample(urlsplit(value['origin']).port,value['origin'],deadline,generation,via_private=True)
    eligible()
    return {'project':value['project'],'generation':generation,'expires_at':value['expires_at'],**evidence}
