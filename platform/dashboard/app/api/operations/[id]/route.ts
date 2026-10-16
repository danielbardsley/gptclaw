import { controlRequest, controlResponse } from '../../../../lib/controls.ts';
export const dynamic = 'force-dynamic';
export async function GET(_request: Request, context: { params: Promise<{ id: string }> }) {
  if(process.env.DASHBOARD_CONTROLS !== '1')return controlResponse({error:'control-disabled'},503);
  const {id}=await context.params;
  if(!/^[0-9a-f]{32}$/.test(id))return controlResponse({error:'invalid-request'},400);
  try{const result=await controlRequest('/v1/operations/'+id);return controlResponse(result.data,result.status);}
  catch{return controlResponse({error:'control-unavailable'},503);}
}
