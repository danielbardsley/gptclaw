export async function GET() {
  const address = process.env.GPTCLAW_API_READY_URL;
  if (!address) return Response.json({ status: 'unready' }, { status: 503 });
  try {
    const response = await fetch(address, { cache: 'no-store', signal: AbortSignal.timeout(2000) });
    return Response.json({ status: response.ok ? 'ready' : 'unready' }, { status: response.ok ? 200 : 503 });
  } catch { return Response.json({ status: 'unready' }, { status: 503 }); }
}
