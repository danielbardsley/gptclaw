import { duration, statusFreshness, type ProjectStatus, type ServiceStatus } from '../lib/status.ts';
const label = (text: string) => text.charAt(0).toUpperCase() + text.slice(1).replaceAll('-', ' ');
const date = (time: number | null | undefined) => time == null ? 'Not observed' : new Date(time * 1000).toLocaleString();
function StatusLabel({ status, freshness }: { status: ServiceStatus; freshness: string }) {
  return <span className={`badge ${freshness !== 'current' || status.state !== 'ready' ? 'warning-text' : 'healthy-text'}`}>
    {freshness === 'unavailable' ? 'Status unavailable' : freshness === 'stale' ? `Last known: ${label(status.state)}` : label(status.state)}
  </span>;
}
export default function StatusPanel({ project, status, serverTime, elapsed, forced }: { project: string; status: ProjectStatus; serverTime?: number; elapsed: number; forced: boolean }) {
  const freshness = statusFreshness(status, serverTime, elapsed, forced);
  return <div className="service-status">
    <StatusLabel status={status} freshness={freshness}/>
    <span className="secondary">{label(freshness)}{status.operation_busy ? ' · Operation in progress' : ''}</span>
    {status.reason ? <span className="secondary">{label(status.reason)}</span> : null}
    <details><summary aria-label={`Service details for ${project}`}>Service details</summary>
      <p className="secondary">Last successful observation: {date(status.last_success_at)}</p>
      <div className="components">{Object.entries(status.components).map(([name, component]) => {
        const componentFreshness = statusFreshness(component, serverTime, elapsed, forced);
        const change = component.last_observed_change;
        return <section className="component" key={name} aria-label={`${name.toUpperCase()} service`}>
          <h3>{name.toUpperCase()} <StatusLabel status={component} freshness={componentFreshness}/></h3>
          <dl><dt>Health</dt><dd>{componentFreshness === 'current' ? label(component.health) : 'Unknown · previous observation retained'}</dd>
            <dt>Current-run uptime</dt><dd>{component.uptime_seconds == null ? label(component.uptime_reason || 'unavailable') : duration(component.uptime_seconds)}</dd>
            <dt>Container-instance restarts</dt><dd>{component.restart_count == null ? label(component.restart_reason || 'unavailable') : component.restart_count}</dd>
            <dt>Last successful observation</dt><dd>{date(component.last_success_at)} · {label(componentFreshness)}</dd>
            <dt>Last observed change</dt><dd>{change ? `${change.kind === 'first-observed' ? 'First observed' : 'Change detected'}: ${date(change.at)}${change.after_gap ? ' · after an observation gap' : ''}` : 'Not observed'}</dd>
          </dl>{component.operation_busy ? <p className="secondary">Operation in progress</p> : null}
          {component.reason ? <p className="secondary">{label(component.reason)}</p> : null}
        </section>;
      })}</div>
      <p className="secondary">Uptime and restart counts describe the current container instance. Replacement resets the count. Change times record when the collector observed a change.</p>
    </details>
  </div>;
}
