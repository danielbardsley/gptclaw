import { useState } from 'react';
import type { ProjectRow as Row } from '../lib/inventory.ts';
import StatusPanel, { StatusSummary } from './StatusPanel.tsx';
import ProjectLinks from './ProjectLinks.tsx';
import MetroPanel, { MetroSummary } from './MetroPanel.tsx';
import ExpoGoPanel from './ExpoGoPanel.tsx';
const label = (value: string) => value.charAt(0).toUpperCase() + value.slice(1).replaceAll('-', ' ');
const date = (value: number | null | undefined) => value == null ? 'Not observed' : new Date(value * 1000).toLocaleString();
function Documentation({ row }: { row: Row }) {
  return <div className="doc-chips">{([['README',row.documentation.readme],['Index',row.documentation.index]] as const).map(([name,state]) => <span key={name} className={`doc-chip ${state === 'present' ? 'present' : ''}`} aria-label={`${name === 'Index' ? 'Docs index' : name}: ${label(state)}`}>{name}: {label(state)}</span>)}</div>;
}
export default function ProjectRow({ row, showStatus, showLinks, serverTime, elapsed, stale }: { row: Row; showStatus: boolean; showLinks: boolean; serverTime?: number; elapsed: number; stale: boolean }) {
  const [open,setOpen] = useState(false);
  const detailId = `project-details-${row.key}`;
  const headingId = `project-name-${row.key}`;
  const forced = stale || row.inventory_freshness === 'stale';
  const linkProps = { id:row.id, projectKey:row.key, links:row.links || [], serverTime, elapsed, forced };
  return <>
    <tr role="row" className={`project-row ${open ? 'expanded' : ''}`} data-project-key={row.key}>
      <th role="rowheader" scope="row" className="project-name"><strong id={headingId}>{row.name}</strong><span className="project-id">{row.id}</span>
        {row.inventory_freshness === 'stale' ? <span className="row-warning">Inventory metadata stale</span> : null}
        {row.identity_state === 'conflict' ? <span className="row-warning">Conflicting project ID</span> : null}
      </th>
      <td role="cell" data-label="Type"><span className="mobile-label" aria-hidden="true">Type</span><div><span className="type-chip">{label(row.kind)}</span><span className="secondary">{row.components.join(' · ') || 'Native source'} · v{row.manifest_version}</span></div></td>
      <td role="cell" data-label="Repository"><span className="mobile-label" aria-hidden="true">Repository</span><span className={`repository ${row.repository ? 'recorded' : ''}`}>{row.repository?.replace(/^https:\/\/github\.com\//,'') || 'Repository not recorded'}</span></td>
      <td role="cell" data-label="Runtime"><span className="mobile-label" aria-hidden="true">Runtime</span><span className="runtime"><span className={`runtime-dot ${row.runtime_support === 'supported' ? 'supported' : ''}`} aria-hidden="true"/>{row.kind === 'mobile' ? row.manifest_version === 6 && row.runtime_support === 'supported' ? 'Metro supported' : 'Not yet available' : label(row.runtime_support)}</span></td>
      <td role="cell" data-label="Docs"><span className="mobile-label" aria-hidden="true">Docs</span><Documentation row={row}/></td>
      {showStatus ? <td role="cell" data-label="Status"><span className="mobile-label" aria-hidden="true">Status</span>{row.kind === 'mobile' ? <MetroSummary status={row.status} project={row.id} version={row.manifest_version} serverTime={serverTime} elapsed={elapsed} forced={forced}/> : <StatusSummary status={row.status} serverTime={serverTime} elapsed={elapsed} forced={forced}/>}</td> : null}
      {showLinks ? <td role="cell" data-label="Links"><span className="mobile-label" aria-hidden="true">Links</span>{row.kind === 'mobile' ? <ExpoGoPanel status={row.status} project={row.id} serverTime={serverTime} elapsed={elapsed} forced={forced} compact/> : null}{row.links ? <ProjectLinks {...linkProps} compact/> : <span className="secondary">Links unavailable</span>}</td> : null}
      <td role="cell" className="disclosure-cell"><button className="disclosure" type="button" aria-label={`Service details for ${row.name}`} aria-expanded={open} aria-controls={detailId} onClick={() => setOpen(value => !value)}><svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true" fill="none"><path d="m6 4 4 4-4 4" stroke="currentColor" strokeWidth="1.6"/></svg></button></td>
    </tr>
    <tr role="row" className="project-detail" id={detailId} hidden={!open}><td role="cell" colSpan={6 + Number(showStatus) + Number(showLinks)}>{open ? <div className="project-detail-content" role="region" aria-labelledby={headingId}>
      <div className="detail-panels">
        <section className="detail-panel"><h3>Service details</h3><dl className="project-metadata">
          {showStatus ? <><dt>Status</dt><dd>{row.kind === 'mobile' ? <MetroSummary status={row.status} project={row.id} version={row.manifest_version} serverTime={serverTime} elapsed={elapsed} forced={forced}/> : <StatusSummary status={row.status} serverTime={serverTime} elapsed={elapsed} forced={forced}/>}</dd></> : null}
          <dt>Components</dt><dd className="mono">{row.components.join(' · ') || 'Native source'}</dd><dt>Manifest</dt><dd>v{row.manifest_version}</dd>
          <dt>Owner</dt><dd>{row.owner || 'Not recorded'}</dd><dt>Project location</dt><dd className="mono">{row.location}</dd>
          <dt>Repository</dt><dd>{row.repository || 'Repository not recorded'}</dd><dt>Runtime support</dt><dd>{label(row.runtime_support)}</dd>
          <dt>README</dt><dd>{label(row.documentation.readme)}</dd><dt>Docs index</dt><dd>{label(row.documentation.index)}</dd>
          {row.status ? <><dt>Observed at</dt><dd>{date(row.status.observed_at)}</dd><dt>Last successful observation</dt><dd>{date(row.status.last_success_at)}</dd><dt>Provider state</dt><dd>{label(row.status.provider_state)}</dd></> : null}
        </dl></section>
        {showLinks ? <section className="detail-panel destinations"><h3>Links</h3>{row.links ? <ProjectLinks {...linkProps}/> : <p className="secondary">Links unavailable</p>}</section> : null}
      </div>
      {row.kind === 'mobile' ? <MetroPanel status={row.status} project={row.id} version={row.manifest_version} serverTime={serverTime} elapsed={elapsed} forced={forced}/> : null}
      {row.kind === 'mobile' && showLinks ? <ExpoGoPanel status={row.status} project={row.id} serverTime={serverTime} elapsed={elapsed} forced={forced}/> : null}
      {row.kind !== 'mobile' && row.status ? <StatusPanel status={row.status} serverTime={serverTime} elapsed={elapsed} forced={forced}/> : null}
    </div> : null}</td></tr>
  </>;
}
