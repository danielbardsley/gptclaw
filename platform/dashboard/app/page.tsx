'use client';
import { useEffect, useState } from 'react';
import ProjectRow from './ProjectRow.tsx';
import type { Snapshot } from '../lib/inventory.ts';

const time = (seconds?: number) => seconds == null ? 'Not yet observed' : new Date(seconds * 1000).toLocaleString();
const label = (value: string) => value.charAt(0).toUpperCase() + value.slice(1).replaceAll('-', ' ');

export default function Dashboard() {
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null);
  const [failed, setFailed] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  useEffect(() => {
    let active = true;
    let pending = false;
    let received = performance.now();
    const refresh = async () => {
      if (pending || document.visibilityState === 'hidden') return;
      pending = true;
      try {
        const response = await fetch('/dashboard/api/snapshot/', { cache: 'no-store', signal: AbortSignal.timeout(4000) });
        const data: Snapshot = await response.json();
        if (!active) return;
        if (!response.ok || data.schema_version !== 1) { setFailed(true); return; }
        setSnapshot(data); setFailed(false); received = performance.now(); setElapsed(0);
      } catch { if (active) setFailed(true); }
      finally { pending = false; }
    };
    const visible = () => { if (document.visibilityState === 'visible') void refresh(); };
    document.addEventListener('visibilitychange', visible);
    void refresh();
    const interval = setInterval(() => void refresh(), 5000);
    const aging = setInterval(() => setElapsed((performance.now()-received)/1000), 1000);
    return () => { active = false; document.removeEventListener('visibilitychange', visible); clearInterval(interval); clearInterval(aging); };
  }, []);
  const showStatus = Boolean(snapshot?.status_capacity || snapshot?.rows.some(row => row.status));
  const showLinks = Boolean(snapshot?.rows.some(row => row.links));
  const unavailable = failed || snapshot?.freshness === 'unavailable';
  const stale = failed || snapshot?.freshness === 'stale';
  const hasInventory = snapshot?.last_success_at != null;
  const columns = [['Project',20],['Type',13],['Repository',16],['Runtime',10],...(showStatus ? [['Service status',13]] : []),...(showLinks ? [['Links',13]] : []),['Details',3]] as [string,number][];
  const weight = columns.reduce((sum,[,value]) => sum + value,0);
  const observation = !snapshot && !failed ? 'Loading inventory…' : stale && hasInventory ? 'Inventory stale · collector unavailable' : unavailable ? 'Inventory unavailable' : snapshot?.truncated ? 'Partial inventory · scan limit reached' : snapshot && !snapshot.complete ? 'Partial inventory · some entries unavailable' : 'Inventory current';
  return <>
    <a className="skip" href="#projects">Skip to projects</a>
    <header className="site-header"><div className="brand"><span aria-hidden="true" className="mark">G</span><span>GptClaw</span><span className="brand-divider" aria-hidden="true">/</span><span className="environment"><span className="environment-dot" aria-hidden="true"/>Development</span></div><span className="private"><span className="private-dot" aria-hidden="true"/>Private · Tailscale</span></header>
    <main>
      <div className="heading"><div><p className="eyebrow">Workspace</p><h1>Projects</h1><p className="intro">Your development projects, in one place.</p></div><div className="managed-tile"><strong>{hasInventory ? snapshot!.rows.length : '—'}</strong><span>{stale && hasInventory ? 'Last-known managed' : snapshot && !snapshot.complete && hasInventory ? 'Projects shown' : 'Managed projects'}</span></div></div>
      {snapshot?.diagnostics.length ? <details className="diagnostics"><summary>{snapshot.diagnostics.length} inventory diagnostics</summary><ul>{snapshot.diagnostics.map((d,index) => <li key={index}>{label(d.code)}</li>)}</ul></details> : null}
      {snapshot?.status_capacity?.limited ? <p className="diagnostics">Live observations are being collected in bounded batches. Some project statuses may be stale or unavailable.</p> : null}
      <section id="projects" aria-label="Managed projects" tabIndex={-1} className="overview">
        <div className="observation" role="status"><span className={`dot ${unavailable || stale || !snapshot?.complete ? 'warning' : ''}`} aria-hidden="true"/><span>{observation}</span><span className="observed">Last successful scan: {time(snapshot?.last_success_at)}</span></div>
        {!snapshot && failed || snapshot?.freshness === 'unavailable' && !hasInventory ? <div className="empty"><h2>Inventory is unavailable</h2><p>The observation service could not be reached. This page will refresh automatically.</p></div> : !snapshot ? <div className="empty"><p>Loading projects…</p></div> : !snapshot.rows.length ? <div className="empty"><h2>{snapshot.complete ? 'No managed projects yet' : 'No projects available in this scan'}</h2><p>{snapshot.complete ? 'Projects with a valid GptClaw manifest will appear here, including stopped services.' : 'Read the inventory diagnostics and scan state above. This result does not establish an empty workspace.'}</p></div> : <div className="table-wrap"><table className="projects-table" role="table"><caption className="sr-only">Managed development projects, including stopped services</caption><colgroup>{columns.map(([name,value]) => <col key={name} style={{width:`${value / weight * 100}%`}}/>)}</colgroup><thead role="rowgroup"><tr role="row">{columns.map(([name]) => <th key={name} scope="col" role="columnheader">{name === 'Details' ? <span className="sr-only">Details</span> : name}</th>)}</tr></thead><tbody role="rowgroup">{snapshot.rows.map(row => <ProjectRow key={row.key} row={row} showStatus={showStatus} showLinks={showLinks} serverTime={snapshot.server_time} elapsed={elapsed} stale={stale}/>)}</tbody></table></div>}
      </section>
      <footer>Private project inventory with capability-gated lifecycle controls. Documentation presence indicates files exist; it does not assess their quality.</footer>
    </main>
  </>;
}
