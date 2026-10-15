'use client';
import { useEffect, useRef, useState } from 'react';
import { actions, validControls, type Action, type Component, type Operation } from '../lib/control-types.ts';
import { metroView } from '../lib/metro.ts';
import { duration, statusFreshness, type ProjectStatus } from '../lib/status.ts';
type Intent = {intent_id:string;generation:string;prepared_at:number;expires_at:number;impact:string;name:string;action:Action;component:Component|null};
type Auth = {csrf:string;acquiredAt:number};
let authentication: Promise<Auth> | null = null;
const label=(value:string)=>value.charAt(0).toUpperCase()+value.slice(1).replaceAll('-',' ');
const active=(operation:Operation)=>['accepted','running','unknown'].includes(operation.state);
const reason=(code:string)=>({
  'control-unsupported':'Unavailable for this runtime profile.',
  'control-paused':'Resume or stop the paused project first.',
  'control-dependency':'A dependency is unavailable. Inspect service health before recovery.',
  'control-recovery':'Inspect and reconcile the interrupted operation through the managed CLI before another action.',
  'control-state':'The current service state does not permit this action.',
  'control-expired':'The existing Metro session authorization has expired.',
  'control-changed':'Project source or runtime changed. Review a new confirmation.',
  'control-capacity':'Operation capacity is full. Wait for current work or inspect retained results.',
  'control-unavailable':'Controls are unavailable; status and links remain readable.',
  'busy':'A project operation is already running.',
  'intent-expired':'Confirmation expired. Select the action again.',
  'invalid-session':'The control session expired. Select the action again.',
}[code] || 'The operation could not be completed. Inspect the managed project status.');
async function auth():Promise<Auth> {
  if(!authentication) authentication=fetch('/dashboard/api/control-session/',{cache:'no-store',signal:AbortSignal.timeout(5000)})
    .then(async response=>{const data=await response.json();if(!response.ok || typeof data.csrf!=='string' || !/^[0-9a-f]{64}$/.test(data.csrf))throw Error(data.error || 'control-unavailable');return {csrf:data.csrf,acquiredAt:performance.now()};})
    .catch(error=>{authentication=null;throw error;});
  const current=await authentication;
  if(performance.now()-current.acquiredAt>=840000){authentication=null;return auth();}
  return current;
}
async function post(path:string,body:unknown):Promise<Record<string,unknown>> {
  const session=await auth();
  const response=await fetch(path,{method:'POST',cache:'no-store',headers:{'Content-Type':'application/json','X-CSRF-Token':session.csrf},body:JSON.stringify(body),signal:AbortSignal.timeout(35000)});
  const data=await response.json();
  if(!response.ok){if(data.error==='invalid-session')authentication=null;throw Error(data.error || 'control-unavailable');}
  return data;
}
export default function ControlPanel({raw,projectKey,projectId,name,status,serverTime,elapsed,forced}:{raw:unknown;projectKey:string;projectId:string;name:string;status?:ProjectStatus;serverTime?:number;elapsed:number;forced:boolean}) {
  const controls=validControls(raw);
  const [intent,setIntent]=useState<Intent|null>(null);
  const [pending,setPending]=useState<string|null>(null);
  const [operation,setOperation]=useState<Operation|null>(null);
  const [working,setWorking]=useState(false);
  const [error,setError]=useState('');
  const [localResults,setLocalResults]=useState<Operation[]>([]);
  const initiating=useRef<HTMLButtonElement|null>(null);
  const confirmation=useRef<HTMLButtonElement|null>(null);
  const restoreFocus=useRef(false);
  const resultRegion=useRef<HTMLDivElement|null>(null);
  const storageKey='gptclaw-operation-'+projectKey;
  const caps=controls?.capabilities;
  const componentNames=[...new Set([...(caps?.actions.flatMap(item=>item.component ? [item.component] : []) || []),...Object.keys(status?.components || {}).filter((name):name is Component=>['web','api','db'].includes(name))])];
  const age=serverTime==null || caps==null ? Infinity : serverTime+elapsed-caps.observed_at;
  const stale=forced || age<0 || age>30 || Boolean(status && statusFreshness(status,serverTime,elapsed,forced)!=='current');
  const native=status ? metroView(status,projectId,serverTime,elapsed,forced) : null;
  const recent=[...(controls?.recent || []),...localResults].sort((a,b)=>b.updated_at-a.updated_at).filter((item,index,items)=>items.findIndex(other=>other.operation_id===item.operation_id)===index).slice(0,5);
  const blocking=recent.find(active);
  const busy=working || Boolean(pending) || Boolean(blocking) || Boolean(status?.operation_busy);
  const general=!controls ? 'Controls unavailable for this release.' : !controls.enabled ? 'New actions are disabled. Existing results remain available.' : stale ? 'Controls unavailable while observations are stale.' : caps?.reason ? reason(caps.reason) : status?.state==='unknown' ? 'Controls unavailable while runtime state is unknown.' : blocking?.state==='unknown' ? reason('control-recovery') : busy ? 'A project operation is in progress.' : '';
  useEffect(()=>{try{const id=sessionStorage.getItem(storageKey);if(id && /^[0-9a-f]{32}$/.test(id))setPending(id);}catch{/* Server records remain authoritative. */}},[storageKey]);
  useEffect(()=>{
    if(!pending)return;
    let live=true;let timer:ReturnType<typeof setTimeout>;let attempt=0;
    const poll=async()=>{
      try{
        const response=await fetch('/dashboard/api/operations/'+pending+'/',{cache:'no-store',signal:AbortSignal.timeout(5000)});
        const current=await response.json() as Operation;
        if(!live)return;
        if(!response.ok || current.operation_id!==pending || !['accepted','running','succeeded','failed','unknown'].includes(current.state))throw Error();
        setOperation(current);setError('');
        if(!['accepted','running'].includes(current.state)){
          setLocalResults(previous=>[current,...previous.filter(item=>item.operation_id!==current.operation_id)].slice(0,5));
          setPending(null);try{sessionStorage.removeItem(storageKey);}catch{/* Retained on server. */}
          return;
        }
      }catch{if(live)setError('Connection lost. Checking the existing operation; no action was resubmitted.');}
      if(live)timer=setTimeout(()=>void poll(),Math.min(10000,1000*2**Math.min(attempt++,3)));
    };
    void poll();return()=>{live=false;clearTimeout(timer);};
  },[pending,storageKey]);
  useEffect(()=>{
    // A validated intent is newer than the snapshot that initiated it. Missing
    // or older observations cannot revoke that target proof. Submission still
    // rechecks the exact generation; newer evidence and expiry invalidate it.
    const changed=intent && caps && caps.observed_at>=intent.prepared_at && intent.generation!==caps.generation;
    if(intent && (changed || (serverTime || 0)+elapsed>=intent.expires_at)) {restoreFocus.current=true;setIntent(null);setError('Confirmation expired or project changed. Select the action again.');}
  },[intent,caps?.generation,caps?.observed_at,serverTime,elapsed]);
  useEffect(()=>{if(intent)confirmation.current?.focus();},[intent]);
  useEffect(()=>{
    if(restoreFocus.current && !intent && !working){
      if(initiating.current && !initiating.current.disabled)initiating.current.focus();else resultRegion.current?.focus();
      restoreFocus.current=false;
    }
  },[intent,working,pending,general]);
  const execute=async(selected:Intent)=>{
    const id=crypto.randomUUID().replaceAll('-','');
    try{sessionStorage.setItem(storageKey,id);}catch{/* A visible ID still supports inspection. */}
    restoreFocus.current=true;setPending(id);setIntent(null);setWorking(true);setError('');
    try{
      const result=await post('/dashboard/api/operations/',{schema_version:1,intent_id:selected.intent_id,idempotency_key:id});
      setOperation(result as unknown as Operation);
    }catch(problem){
      // The acceptance response may be lost after dispatch. Keep querying the
      // same operation ID; never automatically repeat a mutation.
      if(problem instanceof Error && ['intent-expired','control-changed','busy','invalid-session','control-state','control-capacity','control-conflict'].includes(problem.message)){
        setPending(null);try{sessionStorage.removeItem(storageKey);}catch{/* No mutation was accepted. */}
      }
      setError(problem instanceof Error && ['intent-expired','control-changed','busy','invalid-session','control-state','control-capacity'].includes(problem.message) ? reason(problem.message) : 'Acceptance response unavailable. Checking the existing operation; no action was resubmitted.');
    }finally{setWorking(false);}
  };
  const request=async(action:Action,component:Component|null,event:React.MouseEvent<HTMLButtonElement>)=>{
    initiating.current=event.currentTarget;setWorking(true);setError('');
    try{
      const data=await post('/dashboard/api/control-intents/',{schema_version:1,project_key:projectKey,action,component});
      if(typeof data.intent_id!=='string' || !/^[0-9a-f]{32}$/.test(data.intent_id) || typeof data.impact!=='string' || typeof data.generation!=='string' || typeof data.prepared_at!=='number' || !Number.isFinite(data.prepared_at) || typeof data.expires_at!=='number')throw Error('control-unavailable');
      const selected=data as unknown as Intent;
      if(action==='start' || action==='resume')await execute(selected);else setIntent(selected);
    }catch(problem){setError(reason(problem instanceof Error ? problem.message : 'control-unavailable'));}
    finally{setWorking(false);}
  };
  const button=(action:Action,component:Component|null)=>{
    const capability=caps?.actions.find(item=>item.action===action && item.component===component);
    const disabled=Boolean(general) || Boolean(intent) || !capability?.enabled;
    const text=component ? 'Restart '+component.toUpperCase() : label(action);
    return <span className="control-action" key={action+(component || '')}><button type="button" disabled={disabled} aria-label={`${text}${component ? '' : ' entire project'} for ${name}`} aria-describedby={capability?.reason ? `reason-${projectKey}-${component || 'project'}-${action}` : `control-note-${projectKey}`} onClick={event=>void request(action,component,event)}>{text}</button>{capability?.reason ? <span className="control-reason" id={`reason-${projectKey}-${component || 'project'}-${action}`}>{reason(capability.reason)}</span> : null}</span>;
  };
  return <section className="lifecycle-panel" aria-label={`Lifecycle controls for ${name}`}>
    <div className="lifecycle-toolbar"><h3>Lifecycle <span className="secondary">Entire project</span></h3><div className="project-actions">{actions.map(action=>button(action,null))}</div></div>
    <p className="control-note" id={`control-note-${projectKey}`}>{general || 'Project controls affect this project only. Service Restart affects the named component.'}</p>
    {intent ? <div className="control-confirm" role="region" aria-label={`Confirm ${intent.action} for ${name}`}><div><strong>{label(intent.action)} {intent.component?.toUpperCase() || 'entire project'} for {name}?</strong><p>{intent.impact}</p></div><div className="confirm-actions"><button type="button" onClick={()=>{restoreFocus.current=true;setIntent(null);}}>Cancel</button><button type="button" className="confirm-operation" ref={confirmation} onClick={()=>void execute(intent)}>Confirm {intent.action}</button></div></div> : null}
    <div className="lifecycle-components" role="table" aria-label={`Service restart controls for ${name}`}><div className="lifecycle-component header" role="row"><span role="columnheader">Component</span><span role="columnheader">State</span><span role="columnheader">Uptime</span><span role="columnheader">Restarts</span><span role="columnheader">Actions</span></div>{componentNames.map(componentName=>{
      const component=status?.components[componentName];
      const componentState=component?.state || (componentName==='metro' ? native?.state : null);
      const componentFreshness=component ? statusFreshness(component,serverTime,elapsed,forced) : native?.freshness;
      return <div className="lifecycle-component" role="row" key={componentName}><strong role="rowheader">{componentName.toUpperCase()}</strong><span role="cell"><span className="mobile-label">State: </span>{componentState ? `${componentFreshness!=='current' ? 'Last known: ' : ''}${label(componentState)}` : 'See service observations'}</span><span role="cell"><span className="mobile-label">Uptime: </span>{duration(component?.uptime_seconds)}</span><span role="cell"><span className="mobile-label">Restarts: </span>{component?.restart_count ?? 'Unavailable'}</span><span role="cell">{button('restart',componentName)}</span></div>;
    })}</div>
    <div className="control-result" ref={resultRegion} tabIndex={-1} role="status" aria-live="polite">{operation ? <p><strong>{label(operation.action)} {operation.component?.toUpperCase() || 'entire project'}: {label(operation.state)}</strong> · {operation.stage ? label(operation.stage) : 'Accepted'}<br/><span className="mono">Operation {operation.operation_id}</span>{operation.state==='succeeded' ? <><br/>Completed; health and links follow the latest service observations.</> : null}{operation.reason ? <><br/>{reason(operation.reason)}</> : null}</p> : null}{error ? <p>{error}</p> : null}</div>
    <div className="control-recent"><strong>Recent</strong><span className="secondary">Results retained for seven days.</span>{recent.length ? <ul>{recent.map(item=><li key={item.operation_id}>{label(item.action)} {item.component?.toUpperCase() || 'entire project'} · {label(item.state)} · {new Date(item.updated_at*1000).toLocaleString()}{item.reason ? ' · '+reason(item.reason) : ''}</li>)}</ul> : <span>No recorded actions.</span>}</div>
  </section>;
}
