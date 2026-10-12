'use client';
import { useEffect, useState } from 'react';

type Row = { key: string; id: string; name: string; kind: string; components: string[]; location: string; manifest_version: number; runtime_support: string; identity_state: string; owner: string | null; repository: string | null; documentation: { readme: string; index: string }; inventory_freshness?: string };
type Snapshot = { schema_version: number; observed_at?: number; last_success_at?: number; freshness: string; complete: boolean; truncated: boolean; rows: Row[]; diagnostics: { code: string }[] };
const time = (seconds?: number) => seconds ? new Date(seconds * 1000).toLocaleString() : 'Not yet observed';
const label = (value: string) => value.charAt(0).toUpperCase() + value.slice(1).replaceAll('-', ' ');

export default function Dashboard() {
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null);
  const [failed, setFailed] = useState(false);
  useEffect(() => {
    let active = true;
    let pending = false;
    const refresh = async () => {
      if (pending) return;
      pending = true;
      try {
        const response = await fetch('/dashboard/api/snapshot/', { cache: 'no-store', signal: AbortSignal.timeout(4000) });
        const data: Snapshot = await response.json();
        if (!active) return;
        if (!response.ok || data.schema_version !== 1) { setFailed(true); return; }
        setSnapshot(data); setFailed(false);
      } catch { if (active) setFailed(true); }
      finally { pending = false; }
    };
    void refresh();
    const interval = setInterval(() => void refresh(), 5000);
    return () => { active = false; clearInterval(interval); };
  }, []);
  const unavailable = failed || snapshot?.freshness === 'unavailable';
  const stale = failed || snapshot?.freshness === 'stale';
  return <>
    <a className="skip" href="#projects">Skip to projects</a>
    <header><div className="brand"><span aria-hidden="true" className="mark">G</span><span>GptClaw<span className="environment">Development</span></span></div><span className="private">Private · Tailscale</span></header>
    <main>
      <div className="heading"><div><p className="eyebrow">WORKSPACE</p><h1>Projects</h1><p className="intro">Your development projects, in one place.</p></div><div className="summary"><strong>{snapshot?.rows.length ?? '—'}</strong><span>managed projects</span></div></div>
      <div className="observation" role="status"><span className={`dot ${unavailable || stale ? 'warning' : ''}`} aria-hidden="true"/><span>{!snapshot && !failed ? 'Loading inventory…' : stale ? 'Inventory stale · collector unavailable' : unavailable ? 'Inventory unavailable' : snapshot?.truncated ? 'Partial inventory · scan limit reached' : snapshot && !snapshot.complete ? 'Partial inventory · some entries unavailable' : 'Inventory current'}</span><span className="observed">Last successful scan: {time(snapshot?.last_success_at)}</span></div>
      {snapshot?.diagnostics.length ? <details className="diagnostics"><summary>{snapshot.diagnostics.length} inventory diagnostics</summary><ul>{snapshot.diagnostics.map((d, index) => <li key={index}>{label(d.code)}</li>)}</ul></details> : null}
      <section id="projects" aria-label="Managed projects" tabIndex={-1}>
        {!snapshot && failed ? <div className="empty"><h2>Inventory is unavailable</h2><p>The observation service could not be reached. This page will refresh automatically.</p></div> : !snapshot ? <div className="empty"><p>Loading projects…</p></div> : !snapshot.rows.length ? <div className="empty"><h2>{snapshot.complete ? 'No managed projects yet' : 'No projects available in this scan'}</h2><p>{snapshot.complete ? 'Projects with a valid GptClaw manifest will appear here, including stopped services.' : 'Read the inventory diagnostics and scan state above. This result does not establish an empty workspace.'}</p></div> : <div className="table-wrap"><table><caption className="sr-only">Managed development projects, including stopped services</caption><thead><tr><th scope="col">Project</th><th scope="col">Type / components</th><th scope="col">Owner / repository</th><th scope="col">Runtime support</th><th scope="col">Documentation</th></tr></thead><tbody>{snapshot.rows.map(row => <tr key={row.key}><th scope="row"><strong>{row.name}</strong><span className="secondary">{row.id}</span><span className="path">{row.location}</span>{row.inventory_freshness === 'stale' ? <span className="badge warning-text">Inventory metadata stale</span> : null}{row.identity_state === 'conflict' ? <span className="badge warning-text">Conflicting project ID</span> : null}</th><td><span className="badge">{label(row.kind)}</span><span className="secondary">{row.components.join(' · ')}</span><span className="secondary">Manifest v{row.manifest_version}</span></td><td>{row.owner || 'Not recorded'}<span className="secondary">{row.repository || 'Repository not recorded'}</span></td><td><span className="badge">{label(row.runtime_support)}</span></td><td><span className="doc">README: {label(row.documentation.readme)}</span><span className="doc">Docs index: {label(row.documentation.index)}</span></td></tr>)}</tbody></table></div>}
      </section>
      <footer>Read-only project inventory. Documentation presence indicates files exist; it does not assess their quality.</footer>
    </main>
  </>;
}
