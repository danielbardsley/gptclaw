import { readCollector } from '../../../lib/collector.ts';
export const dynamic = 'force-dynamic';
export async function GET() {
  try { return Response.json(await readCollector(), { headers: { 'Cache-Control': 'no-store' } }); }
  catch { return Response.json({ schema_version: 1, freshness: 'unavailable', complete: false, truncated: false, rows: [], diagnostics: [{ code: 'collector-unavailable' }] }, { status: 503, headers: { 'Cache-Control': 'no-store' } }); }
}
