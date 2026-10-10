"""Unprivileged private ingress for owned healthy app mappings, including dev WebSockets."""
import concurrent.futures
import http.client
from http.server import BaseHTTPRequestHandler, HTTPServer
import select
import socket
import threading
import time
from urllib.parse import urlsplit

from private_apps import AppError, INGRESS_PORT, VERSION, state_for, verify_unit

MAX_BODY = 2 * 1024 * 1024
HOP = {'connection','keep-alive','proxy-authenticate','proxy-authorization','te','trailer','transfer-encoding','upgrade'}


class Handler(BaseHTTPRequestHandler):
 protocol_version = 'HTTP/1.1'
 def log_message(self, *_): pass  # Never persist request/query/identity headers.

 def fail(self, code):
  self.send_response(code); self.send_header('Content-Length','0'); self.send_header('Connection','close');self.end_headers()
  self.close_connection=True

 def do_GET(self): self.proxy()
 def do_HEAD(self): self.proxy()
 def do_POST(self): self.proxy()
 def do_PUT(self): self.proxy()
 def do_PATCH(self): self.proxy()
 def do_DELETE(self): self.proxy()
 def do_OPTIONS(self): self.proxy()

 def proxy(self):
  if self.path == '/healthz' and self.command in {'GET','HEAD'}:
   body=('GptClaw ingress '+VERSION+'\n').encode()
   self.send_response(200);self.send_header('Content-Length',str(len(body)));self.end_headers()
   if self.command!='HEAD':self.wfile.write(body)
   return
  try:
   self.connection.settimeout(15)
   if len(self.path)>8192 or len(str(self.headers))>16384:return self.fail(431)
   parsed=urlsplit(self.path)
   if parsed.scheme or parsed.netloc:return self.fail(400)
   parts=parsed.path.split('/')
   if len(parts)<3 or parts[1]!='projects':return self.fail(404)
   slug=parts[2]
   import re
   if not re.fullmatch(r'[a-z][a-z0-9]*(?:-[a-z0-9]+)*',slug) or len(slug)>48:return self.fail(404)
   s=state_for(slug)
   if not s or s['phase']!='ready' or not s.get('health_ready'):return self.fail(404)
   verify_unit(s)
   if self.headers.get('Transfer-Encoding'):return self.fail(400)
   length=int(self.headers.get('Content-Length','0'))
   if length<0 or length>MAX_BODY:return self.fail(413)
   headers={k:v for k,v in self.headers.items() if k.lower() not in HOP}
   if any('\r' in k+v or '\n' in k+v for k,v in headers.items()):return self.fail(400)
   if self.headers.get('Upgrade','').lower()=='websocket':
    return self.websocket(s,headers)
   body=self.rfile.read(length) if length else None
   if length and len(body)!=length:return self.fail(400)
   connection=http.client.HTTPConnection('127.0.0.1',s['port'],timeout=15)
   try:
    connection.request(self.command,self.path,body=body,headers=headers)
    response=connection.getresponse();data=response.read(MAX_BODY+1)
    if len(data)>MAX_BODY:return self.fail(502)
    self.send_response(response.status)
    for key,value in response.getheaders():
     if key.lower() not in HOP|{'content-length'}:self.send_header(key,value)
    self.send_header('Content-Length',response.getheader('Content-Length','0') if self.command=='HEAD' else str(len(data)));self.end_headers()
    if self.command!='HEAD':self.wfile.write(data)
   finally:connection.close()
  except (AppError,OSError,ValueError,http.client.HTTPException):
   try:self.fail(502)
   except OSError:pass

 def websocket(self,s,headers):
  upstream=socket.create_connection(('127.0.0.1',s['port']),timeout=15)
  try:
   headers.update({'Connection':'Upgrade','Upgrade':'websocket'})
   request=f'{self.command} {self.path} HTTP/1.1\r\n'+''.join(f'{k}: {v}\r\n' for k,v in headers.items())+'\r\n'
   upstream.sendall(request.encode('latin-1'))
   response=b''
   while b'\r\n\r\n' not in response:
    chunk=upstream.recv(4096)
    if not chunk or len(response)+len(chunk)>16384:return self.fail(502)
    response+=chunk
   head,remaining=response.split(b'\r\n\r\n',1)
   if not head.split(b'\r\n',1)[0].startswith(b'HTTP/1.1 101 '):return self.fail(502)
   self.wfile.write(head+b'\r\n\r\n'+remaining);self.wfile.flush();self.close_connection=True
   deadline=time.monotonic()+120
   while time.monotonic()<deadline:
    ready,_,_=select.select([self.connection,upstream],[],[],min(5,max(0,deadline-time.monotonic())))
    for source in ready:
     data=source.recv(65536)
     if not data:return
     (upstream if source is self.connection else self.connection).sendall(data)
     deadline=time.monotonic()+120
  finally:upstream.close()


class Server(HTTPServer):
 def __init__(self,address):
  super().__init__(address,Handler)
  self.pool=concurrent.futures.ThreadPoolExecutor(max_workers=16)
  self.slots=threading.BoundedSemaphore(16)
 def process_request(self,request,client_address):
  if not self.slots.acquire(blocking=False):self.shutdown_request(request);return
  self.pool.submit(self.worker,request,client_address)
 def worker(self,request,client_address):
  try:
   request.settimeout(15);self.finish_request(request,client_address)
  finally:self.shutdown_request(request);self.slots.release()
 def server_close(self):
  super().server_close();self.pool.shutdown(wait=True)


def main():
 with Server(('127.0.0.1',INGRESS_PORT)) as server:server.serve_forever()
