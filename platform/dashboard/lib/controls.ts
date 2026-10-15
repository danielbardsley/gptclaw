import http from 'node:http';
export function controlRequest(path: string, method = 'GET', body?: unknown, headers: Record<string,string> = {}, timeoutMs = 15000): Promise<{ status: number; data: Record<string,unknown> }> {
  return new Promise((resolve,reject) => {
    const origin = new URL(process.env.DASHBOARD_ORIGIN || '');
    const payload = body == null ? null : Buffer.isBuffer(body) ? body : JSON.stringify(body);
    const request = http.request({socketPath:process.env.DASHBOARD_CONTROL_SOCKET || '/run/gptclaw/control.sock',path,method,timeout:timeoutMs,headers:{host:origin.host,origin:origin.origin,'sec-fetch-site':'same-origin',...(payload ? {'content-type':'application/json','content-length':String(Buffer.byteLength(payload))} : {}),...headers}},response=>{
      const chunks:Buffer[]=[]; let size=0;
      response.on('data',(chunk:Buffer)=>{size+=chunk.length;if(size>1024*1024){response.destroy();reject(new Error('control-unavailable'));}else chunks.push(chunk);});
      response.on('error',()=>reject(new Error('control-unavailable')));
      response.on('end',()=>{try{const data=JSON.parse(Buffer.concat(chunks).toString('utf8'));if(!data || typeof data!=='object' || Array.isArray(data))throw Error();resolve({status:response.statusCode || 503,data});}catch{reject(new Error('control-unavailable'));}});
    });
    request.on('timeout',()=>request.destroy());request.on('error',()=>reject(new Error('control-unavailable')));
    request.end(payload);
  });
}
export function controlResponse(data: unknown, status = 200) { return Response.json(data,{status,headers:{'Cache-Control':'no-store'}}); }
export async function submitControl(request: Request, path: '/v1/intents' | '/v1/operations') {
  if (process.env.DASHBOARD_CONTROLS !== '1') return controlResponse({error:'control-disabled'},503);
  try {
    const { allowedRequest } = await import('./boundary.ts');
    const rejection = allowedRequest(request,process.env.DASHBOARD_ORIGIN || '',true);
    if (rejection) return controlResponse({error:'invalid-request'},rejection);
    if (request.headers.get('content-type') !== 'application/json') return controlResponse({error:'invalid-request'},400);
    const declared = request.headers.get('content-length');
    if (declared && (!/^\d+$/.test(declared) || Number(declared)>8192)) return controlResponse({error:'invalid-request'},413);
    const reader=request.body?.getReader();const chunks:Uint8Array[]=[];let length=0;
    if(!reader)return controlResponse({error:'invalid-request'},400);
    while(true){const chunk=await reader.read();if(chunk.done)break;length+=chunk.value.length;if(length>8192){await reader.cancel();return controlResponse({error:'invalid-request'},413);}chunks.push(chunk.value);}
    // Preserve bytes for the controller's strict JSON parser: decoding and
    // reserializing here would erase duplicate keys and invalid UTF-8.
    const data=Buffer.concat(chunks);
    const cookie = request.headers.get('cookie') || '';
    const sessions = cookie.split(';').map(value=>value.trim()).filter(value=>value.startsWith('__Secure-gptclaw-control='));
    const session=sessions.length===1 ? sessions[0].split('=')[1] : '';
    const csrf=request.headers.get('x-csrf-token') || '';
    if(!/^[0-9a-f]{64}$/.test(session) || !/^[0-9a-f]{64}$/.test(csrf))return controlResponse({error:'invalid-session'},403);
    const result=await controlRequest(path,'POST',data,{'x-control-session':session,'x-csrf-token':csrf});
    return controlResponse(result.data,result.status);
  }catch{return controlResponse({error:'control-unavailable'},503);}
}
