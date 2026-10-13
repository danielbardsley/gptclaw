import { duration, statusFreshness, type ProjectStatus, type ServiceStatus } from '../lib/status.ts';
const label = (text: string) => text.charAt(0).toUpperCase() + text.slice(1).replaceAll('-', ' ');
const date = (time: number | null | undefined) => time == null ? 'Not observed' : new Date(time * 1000).toLocaleString();

function StatusLabel({ status, freshness }: { status: ServiceStatus; freshness: string }) {
  const tones: Record<string, string> = { ready: 'success', stopped: 'neutral', starting: 'progress', failed: 'danger', degraded: 'warning', unknown: 'danger' };
  const tone = freshness === 'stale' ? 'warning' : freshness !== 'current' ? 'danger' : tones[status.state] || 'neutral';
  return <span className={`status-badge ${tone}`}><span className="status-dot" aria-hidden="true"/>
    {freshness === 'unavailable' ? 'Status unavailable' : freshness === 'stale' ? `Last known: ${label(status.state)}` : label(status.state)}
  </span>;
}
export function StatusSummary({ status, serverTime, elapsed, forced }: { status?: ProjectStatus; serverTime?: number; elapsed: number; forced: boolean }) {
  if (!status) return <span className="secondary">Status unavailable</span>;
  const freshness = statusFreshness(status, serverTime, elapsed, forced);
  return <div className="service-summary"><StatusLabel status={status} freshness={freshness}/>
    <span className="secondary">{label(freshness)}{status.operation_busy ? ' · Operation in progress' : ''}</span>
    {status.reason ? <span className="secondary">{label(status.reason)}</span> : null}
  </div>;
}
export default function StatusPanel({ status, serverTime, elapsed, forced }: { status: ProjectStatus; serverTime?: number; elapsed: number; forced: boolean }) {
  return <section className="component-region" aria-label="Component observations">
    <h3>Component observations</h3>
    <div className="components">{Object.entries(status.components).map(([name, component]) => {
      const freshness = statusFreshness(component, serverTime, elapsed, forced);
      const change = component.last_observed_change;
      return <section className="component" key={name} aria-label={`${name.toUpperCase()} service`}>
        <h4>{name.toUpperCase()} <StatusLabel status={component} freshness={freshness}/></h4>
        <dl><dt>Health</dt><dd>{freshness === 'current' ? label(component.health) : 'Unknown · previous observation retained'}</dd>
          <dt>Provider state</dt><dd>{label(component.provider_state)}</dd>
          <dt>Current-run uptime</dt><dd>{component.uptime_seconds == null ? label(component.uptime_reason || 'unavailable') : duration(component.uptime_seconds)}</dd>
          <dt>Container-instance restarts</dt><dd>{component.restart_count == null ? label(component.restart_reason || 'unavailable') : component.restart_count}</dd>
          <dt>Observed at</dt><dd>{date(component.observed_at)}</dd>
          <dt>Last successful observation</dt><dd>{date(component.last_success_at)} · {label(freshness)}</dd>
          <dt>Last observed change</dt><dd>{change ? `${change.kind === 'first-observed' ? 'First observed' : 'Change detected'}: ${date(change.at)}${change.after_gap ? ' · after an observation gap' : ''}` : 'Not observed'}</dd>
          {change?.after_gap && change.previous_observation_at != null ? <><dt>Previous observation</dt><dd>{date(change.previous_observation_at)}</dd></> : null}
        </dl>
        {component.operation_busy ? <p className="secondary">Operation in progress</p> : null}
        {component.reason ? <p className="secondary">{label(component.reason)}</p> : null}
      </section>;
    })}</div>
    <p className="semantics">Uptime and restart counts describe the current container instance. Replacement resets the count. Change times record when the collector observed a change.</p>
  </section>;
}
