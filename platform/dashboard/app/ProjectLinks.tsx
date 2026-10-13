import { activeLink, type ProjectLink } from '../lib/links.ts';
const reasons: Record<string,string> = { 'repository-not-recorded':'Repository not recorded', 'log-viewer-not-available':'Log viewer not available', 'preview-registry-not-available':'Preview registry not available', 'no-active-preview':'No active previews', 'route-capability-unavailable':'Route capability unavailable', 'status-stale':'Status is stale', 'project-unavailable':'Project is unavailable', 'identity-unavailable':'Project identity is unavailable', 'preview-expired':'Preview expired', 'preview-revoked':'Preview revoked', 'preview-registry-stale':'Preview registry is stale', 'preview-target-invalid':'Preview target is unavailable' };
const shortLabels: Record<string,string> = { app:'App', 'api-docs':'API', repository:'Repo', logs:'Logs', preview:'Preview' };
export default function ProjectLinks({ id, projectKey, links, serverTime, elapsed, forced, compact = false }: { id: string; projectKey: string; links: ProjectLink[]; serverTime?: number; elapsed: number; forced: boolean; compact?: boolean }) {
  return <ul className={compact ? 'link-pills' : 'destination-list'} aria-label={`${compact ? 'Quick links' : 'Destinations'} for ${id}`}>{links.map(link => {
    const enabled = activeLink(link,id,projectKey,serverTime,elapsed,forced);
    const reason = enabled ? null : link.reason ? reasons[link.reason] || 'Destination unavailable' : link.kind === 'preview' ? 'Preview expired or stale' : 'Observation is stale or unavailable';
    const scope = link.scope === 'public' ? 'Public preview' : link.scope === 'repository' ? 'GitHub' : 'Private';
    return <li key={link.kind}>
      {enabled ? <a className={compact ? 'link-pill' : undefined} aria-label={link.label} href={link.url!} target={link.kind === 'logs' ? undefined : '_blank'} rel={link.kind === 'logs' ? undefined : 'noopener noreferrer'}>{compact ? shortLabels[link.kind] || link.label : link.label}</a> : <span className={compact ? 'link-pill unavailable' : 'destination-label'}>{compact ? <><span aria-hidden="true">{shortLabels[link.kind] || link.label}</span><span className="sr-only">{link.label} unavailable · {scope} · {reason}</span></> : link.label}</span>}
      {compact ? null : <><span className="link-scope">{scope}</span><span className={enabled ? 'available-note' : 'destination-reason'}>{reason || 'Available'}</span>
        {link.kind === 'preview' && link.expires_at != null ? <span className="expiry">Expires {new Date(link.expires_at * 1000).toLocaleString(undefined,{timeZoneName:'short'})}{enabled ? ` · ${Math.max(0,Math.ceil((link.remaining_seconds || 0) - elapsed))}s remaining` : ''}</span> : null}
      </>}
    </li>;
  })}</ul>;
}
