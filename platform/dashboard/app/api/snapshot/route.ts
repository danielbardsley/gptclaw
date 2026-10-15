import { controlRequest } from '../../../lib/controls.ts';
import { validControls } from '../../../lib/control-types.ts';
import { readCollector } from '../../../lib/collector.ts';
export const dynamic = 'force-dynamic';
export async function GET() {
  try {
    const [read,controls]=await Promise.allSettled([readCollector(), process.env.DASHBOARD_CONTROLS === '1' ? controlRequest('/v1/snapshot','GET',undefined,{},750) : Promise.resolve(null)]);
    if(read.status!=='fulfilled')throw Error();
    const snapshot=read.value as {rows?:{key:string;controls?:unknown}[]};
    if(controls.status==='fulfilled' && controls.value?.status===200 && controls.value.data.schema_version===1 && typeof controls.value.data.enabled==='boolean' && controls.value.data.projects && typeof controls.value.data.projects==='object'){
      const projects=controls.value.data.projects as Record<string,unknown>;
      for(const row of snapshot.rows || []){const value=validControls(projects[row.key]);if(value)row.controls=value;}
    }
    return Response.json(snapshot, { headers: { 'Cache-Control': 'no-store' } }); }
  catch { return Response.json({ schema_version: 1, freshness: 'unavailable', complete: false, truncated: false, rows: [], diagnostics: [{ code: 'collector-unavailable' }] }, { status: 503, headers: { 'Cache-Control': 'no-store' } }); }
}
