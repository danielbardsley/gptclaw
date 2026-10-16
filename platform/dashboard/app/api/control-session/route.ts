import { controlRequest, controlResponse } from '../../../lib/controls.ts';
export const dynamic = 'force-dynamic';
export async function GET() {
  if (process.env.DASHBOARD_CONTROLS !== '1') return controlResponse({error:'control-disabled'},503);
  try {
    const result=await controlRequest('/v1/session');
    if(result.status!==200)return controlResponse(result.data,result.status);
    const {session,csrf,expires_at}=result.data;
    if(typeof session!=='string' || !/^[0-9a-f]{64}$/.test(session) || typeof csrf!=='string' || !/^[0-9a-f]{64}$/.test(csrf))throw Error();
    const response=controlResponse({schema_version:1,csrf,expires_at});
    response.headers.set('Set-Cookie',`__Secure-gptclaw-control=${session}; Secure; HttpOnly; SameSite=Strict; Path=/dashboard/; Max-Age=900`);
    return response;
  }catch{return controlResponse({error:'control-unavailable'},503);}
}
