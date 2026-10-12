export function allowedRequest(request: { method: string; url: string; headers: Headers }, origin: string): number | null {
  let configured: URL;
  try { configured = new URL(origin); } catch { return 503; }
  if (configured.username || configured.password || configured.search || configured.hash || configured.pathname !== '/') return 503;
  if (!['GET', 'HEAD'].includes(request.method)) return 405;
  const host = request.headers.get('host');
  if (host !== configured.host) return 403;
  const from = request.headers.get('origin');
  if (from && from !== configured.origin) return 403;
  let url: URL;
  try { url = new URL(request.url); } catch { return 400; }
  const site = request.headers.get('sec-fetch-site');
  const documentNavigation = request.headers.get('sec-fetch-mode') === 'navigate'
    && request.headers.get('sec-fetch-dest') === 'document'
    && ['/dashboard', '/dashboard/'].includes(url.pathname);
  if (site && !['same-origin', 'none'].includes(site) && !documentNavigation) return 403;
  if (url.search || /[%\\]/.test(url.pathname) || url.pathname.includes('//')) return 400;
  if (!['/dashboard', '/dashboard/', '/dashboard/api/snapshot', '/dashboard/api/snapshot/', '/dashboard/api/health', '/dashboard/api/health/'].includes(url.pathname)
      && !/^\/dashboard\/_next\/static\/[A-Za-z0-9_./-]+$/.test(url.pathname)) return 404;
  return null;
}
