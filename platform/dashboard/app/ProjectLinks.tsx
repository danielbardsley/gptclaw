import { activeLink, type ProjectLink } from '../lib/links.ts';
const reasons: Record<string,string> = { 'repository-not-recorded':'Repository not recorded', 'log-viewer-not-available':'Log viewer not available', 'preview-registry-not-available':'Preview registry not available', 'no-active-preview':'No active previews', 'route-capability-unavailable':'Route capability unavailable', 'status-stale':'Status is stale', 'project-unavailable':'Project is unavailable', 'identity-unavailable':'Project identity is unavailable', 'preview-expired':'Preview expired', 'preview-revoked':'Preview revoked', 'preview-registry-stale':'Preview registry is stale', 'preview-target-invalid':'Preview target is unavailable' };
export default function ProjectLinks({ id, projectKey, links, serverTime, elapsed, forced }: { id: string; projectKey: string; links: ProjectLink[]; serverTime?: number; elapsed: number; forced: boolean }) {
  return <ul className="project-links" aria-label={`Links for ${id}`}>{links.map(link => {
    const enabled=activeLink(link,id,projectKey,serverTime,elapsed,forced);
    const reason=enabled ? null : link.reason ? reasons[link.reason] || 'Destination unavailable' : link.kind==='preview' ? 'Preview expired or stale' : 'Observation is stale or unavailable';
    return <li key={link.kind}>
      {enabled ? <a href={link.url!} target={link.kind==='logs' ? undefined : '_blank'} rel={link.kind==='logs' ? undefined : 'noopener noreferrer'}>{link.label}</a> : <span>{link.label}</span>}
      <span className="link-scope">{link.scope==='public' ? 'Public preview' : link.scope==='repository' ? 'GitHub' : 'Private'}</span>
      {reason ? <span className="secondary">{reason}</span> : null}
      {link.kind==='preview' && link.expires_at != null ? <span className="secondary">Expires {new Date(link.expires_at*1000).toLocaleString(undefined,{timeZoneName:'short'})}{enabled ? ` · ${Math.max(0,Math.ceil((link.remaining_seconds || 0)-elapsed))}s remaining` : ''}</span> : null}
    </li>;
  })}</ul>;
}
