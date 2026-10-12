export type ProjectLink = { kind: string; label: string; scope: string; url: string | null; available: boolean; reason: string | null; observed_at: number | null; expires_at: number | null; remaining_seconds: number | null };
export function validDestination(link: ProjectLink, id: string, key: string): boolean {
  if (!link.url || /[\\%\s]/.test(link.url) || !/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.test(id) || !/^[0-9a-f]{32}$/.test(key)) return false;
  if (link.kind === 'logs') return link.url === `/dashboard/logs/${key}/`;
  try {
    const url = new URL(link.url);
    if (link.url !== url.origin + url.pathname || link.url.includes('/./') || url.protocol !== 'https:' || url.username || url.password || url.port || url.search || url.hash || link.url.includes('/../')) return false;
    if (link.kind === 'repository') return /^https:\/\/github\.com\/[A-Za-z0-9][A-Za-z0-9-]{0,38}\/[A-Za-z0-9_.-]{1,100}$/.test(link.url) && !['.','..'].includes(url.pathname.split('/')[2]) && !url.pathname.endsWith('.git');
    const prefix = `/projects/${id}/`;
    if (link.kind === 'preview') return url.pathname === prefix && link.scope === 'public';
    if (!/^[a-z0-9][a-z0-9.-]*\.ts\.net$/.test(url.hostname) || link.scope !== 'private') return false;
    if (link.kind === 'app') return url.pathname === prefix;
    if (link.kind === 'api-docs') return [prefix+'docs',prefix+'api/docs'].includes(url.pathname);
  } catch { return false; }
  return false;
}
export function activeLink(link: ProjectLink, id: string, key: string, serverTime: number | undefined, elapsed: number, forced: boolean): boolean {
  if (!link.available || !validDestination(link,id,key)) return false;
  if (['repository','logs'].includes(link.kind)) return true;
  if (forced || link.observed_at == null || serverTime == null) return false;
  const age = serverTime + elapsed - link.observed_at;
  if (age < 0 || age > 30) return false;
  if (link.kind === 'preview') return link.expires_at != null && link.remaining_seconds != null && elapsed < link.remaining_seconds && serverTime+elapsed < link.expires_at;
  return true;
}
