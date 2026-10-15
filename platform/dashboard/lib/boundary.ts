export function allowedRequest(request: { method: string; url: string; headers: Headers }, origin: string, controls = false): number | null {
  let configured: URL;
  try { configured = new URL(origin); } catch { return 503; }
  if (configured.username || configured.password || configured.search || configured.hash || configured.pathname !== '/') return 503;
  const read = ['GET','HEAD'].includes(request.method);
  if (!read && !(controls && request.method === 'POST')) return 405;
  const host = request.headers.get('host');
  if (host !== configured.host) return 403;
  const from = request.headers.get('origin');
  if (from && from !== configured.origin) return 403;
  let url: URL;
  try { url = new URL(request.url); } catch { return 400; }
  const site = request.headers.get('sec-fetch-site');
  if (!read && (from !== configured.origin || site !== 'same-origin' || request.headers.get('content-type') !== 'application/json')) return 403;
  const documentNavigation = request.headers.get('sec-fetch-mode') === 'navigate'
    && request.headers.get('sec-fetch-dest') === 'document'
    && ['/dashboard', '/dashboard/'].includes(url.pathname);
  if (site && !['same-origin', 'none'].includes(site) && !documentNavigation) return 403;
  if (url.search || /[%\\]/.test(url.pathname) || url.pathname.includes('//')) return 400;
  const controlRead = controls && (['/dashboard/api/control-session','/dashboard/api/control-session/'].includes(url.pathname) || /^\/dashboard\/api\/operations\/[0-9a-f]{32}\/?$/.test(url.pathname));
  const controlWrite = controls && ['/dashboard/api/control-intents','/dashboard/api/control-intents/','/dashboard/api/operations','/dashboard/api/operations/'].includes(url.pathname);
  if (!read) return controlWrite ? null : 405;
  if (controlRead && site !== 'same-origin') return 403;
  if (controlRead) return null;
  if (!['/dashboard', '/dashboard/', '/dashboard/api/snapshot', '/dashboard/api/snapshot/', '/dashboard/api/health', '/dashboard/api/health/'].includes(url.pathname)
      && !/^\/dashboard\/_next\/static\/[A-Za-z0-9_./-]+$/.test(url.pathname)) return 404;
  return null;
}
