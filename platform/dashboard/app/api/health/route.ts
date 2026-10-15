export async function GET() { return Response.json({ service: 'gptclaw-dashboard', state: 'ready' }, { headers: { 'Cache-Control': 'no-store' } }); }
