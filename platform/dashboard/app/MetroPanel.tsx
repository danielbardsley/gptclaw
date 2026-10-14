import { Fragment } from 'react';
import { metroView } from '../lib/metro.ts';
import type { ProjectStatus } from '../lib/status.ts';
const label = (text:string) => text.charAt(0).toUpperCase()+text.slice(1).replaceAll('-',' ');
const date = (stamp:number|null) => stamp === null ? 'Not observed' : new Date(stamp*1000).toLocaleString();
type Props = { status?:ProjectStatus; project:string; version:number; serverTime?:number; elapsed:number; forced:boolean };
export function MetroSummary({status,project,version,serverTime,elapsed,forced}:Props) {
  if (version !== 6) return <span className="secondary">Native source · Metro not enabled</span>;
  const view=status ? metroView(status,project,serverTime,elapsed,forced) : null;
  if (!view) return <span className="secondary">Metro observation unavailable</span>;
  return <div className="service-summary"><span className="secondary">Metro: {label(view.state)}</span>
    <span className="secondary">{view.freshness === 'current' ? 'Current observation' : 'Last-known observation'}</span></div>;
}
export default function MetroPanel({status,project,version,serverTime,elapsed,forced}:Props) {
  const view=status ? metroView(status,project,serverTime,elapsed,forced) : null;
  if (version !== 6 || !view) return null;
  return <section className="component-region" aria-label="Metro session observations"><h3>Metro session observations</h3>
    <dl className="project-metadata">{Object.entries(view.observations).map(([name,observation]) =>
      <Fragment key={name}><dt>{name === 'route' ? 'Private route' : label(name)}</dt>
        <dd>{label(observation.state)} · {label(observation.freshness)} · {date(observation.observed_at)}</dd></Fragment>)}
      <dt>Session expiry</dt><dd>{date(view.expires_at)}</dd>
      <dt>Source quality</dt><dd>Separate source-check result</dd>
      <dt>Native client acceptance</dt><dd>Unverified</dd></dl>
  </section>;
}
