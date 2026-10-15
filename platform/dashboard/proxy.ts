import { NextRequest, NextResponse } from 'next/server';
import { allowedRequest } from './lib/boundary.ts';
export function proxy(request: NextRequest) {
  const status = allowedRequest(request, process.env.DASHBOARD_ORIGIN || '', process.env.DASHBOARD_CONTROLS === '1');
  if (status) return new NextResponse(null, { status, headers: { 'Cache-Control': 'no-store', ...(status === 405 ? { Allow: 'GET, HEAD' } : {}) } });
  return NextResponse.next();
}
export const config = { matcher: '/:path*' };
