export function GET() {
  return Response.json({ status: 'ok', project: process.env.GPTCLAW_PROJECT_ID });
}
