import { statusFreshness, type ProjectStatus } from './status.ts';
const states = new Set(['not-started','preparing','starting','running','stopping','stopped','failed','expired','recovery-required','unknown','input-drift','stale','loopback-running','route-failed','route-pending','ready','security-unavailable']);
const layers = { process:['up','down','unknown'], protocol:['ready','failed','unknown'], route:['pending','verified','failed'] };
export type MetroView = { state:string; freshness:string; expires_at:number|null; observations:Record<string,{state:string;observed_at:number|null;freshness:string}> };
const record = (value:unknown): value is Record<string,unknown> => typeof value === 'object' && value !== null && !Array.isArray(value);
const number = (value:unknown): value is number => typeof value === 'number' && Number.isFinite(value) && value >= 0;
export function metroView(status:ProjectStatus, project:string, serverTime:number|undefined, elapsed:number, forced=false):MetroView|null {
  const value=status.metro;
  if (!record(value) || value.schema_version !== 1 || value.project !== project || typeof value.state !== 'string'
      || !states.has(value.state) || value.native_client_acceptance !== 'unverified' || value.source_quality !== 'separate-receipt'
      || !record(value.observations)) return null;
  if (value.state === 'not-started') {
    if (value.generation !== null || value.expires_at !== null) return null;
  } else if (typeof value.generation !== 'string' || !/^[0-9a-f]{32}$/.test(value.generation) || !number(value.expires_at)) return null;
  const freshness=statusFreshness(status,serverTime,elapsed,forced);
  const now=serverTime === undefined ? undefined : serverTime+elapsed;
  const observations:MetroView['observations']={};
  for (const [name,allowed] of Object.entries(layers)) {
    const observation=value.observations[name];
    if (!record(observation) || typeof observation.state !== 'string' || !allowed.includes(observation.state)
        || observation.observed_at !== null && !number(observation.observed_at)) return null;
    const stamp=observation.observed_at as number|null;
    const current=freshness === 'current' && stamp !== null && now !== undefined && now-stamp >= 0 && now-stamp <= 30;
    observations[name]={state:observation.state,observed_at:stamp,freshness:current?'current':stamp===null?'unavailable':'stale'};
  }
  const expires=value.expires_at as number|null;
  let state=value.state;
  if (expires !== null && now !== undefined && now >= expires) state='expired';
  else if (state === 'ready' && (Object.values(observations).some(o=>o.freshness !== 'current')
      || observations.process.state !== 'up' || observations.protocol.state !== 'ready' || observations.route.state !== 'verified')) state='stale';
  return {state,freshness,expires_at:expires,observations};
}
