import { useState } from 'react';
import { goView } from '../lib/expo-go.ts';
import { localQr } from '../lib/local-qr.ts';
import type { ProjectStatus } from '../lib/status.ts';
type Props={status?:ProjectStatus;project:string;serverTime?:number;elapsed:number;forced:boolean;compact?:boolean};
export default function ExpoGoPanel({status,project,serverTime,elapsed,forced,compact=false}:Props) {
  const [showQr,setShowQr]=useState(false);
  const [copied,setCopied]=useState('');
  const view=status ? goView(status,project,serverTime,elapsed,forced) : null;
  if (!view) return <span className="secondary">Expo Go inspection unavailable</span>;
  const hint=view.state==='compatible' ? 'Requires Expo Go '+view.client_version+' on Android '+view.os_version+' with Tailscale connected.' : view.reason.replaceAll('-',' ');
  if (compact) return view.uri ? <a href={view.uri}>Open in Expo Go (Android)</a> : <span className="secondary">Expo Go: {view.state==='compatible' ? 'Session unavailable' : view.state.replaceAll('-',' ')}</span>;
  const svg=view.uri && showQr ? localQr(view.uri).svg : null;
  return <section className="component-region" aria-label="Expo Go launch"><h3>Expo Go</h3>
    <p>{hint}</p><p className="secondary">Compatibility uses the last verified client profile; the dashboard does not detect your phone or its installed version.</p>
    {view.uri ? <><a href={view.uri}>Open in Expo Go (Android)</a>{' '}
      <button type="button" onClick={async()=>{try{await navigator.clipboard.writeText(view.uri!);setCopied('Launch URL copied.');}catch{setCopied('Copy unavailable. Select the launch URL below.');}}}>Copy Expo Go URL</button>{' '}
      <button type="button" aria-expanded={showQr} aria-controls={'expo-go-qr-'+project} onClick={()=>setShowQr(v=>!v)}>{showQr ? 'Hide QR' : 'Show QR'}</button>
      <p className="mono">{view.uri}</p><p>Launch expires: {new Date(view.expires_at!*1000).toLocaleString()}</p>
      <div id={'expo-go-qr-'+project} hidden={!showQr}>{svg ? <img style={{maxWidth:'100%',height:'auto'}} width="320" height="320" alt={'Expo Go launch QR for '+project} src={'data:image/svg+xml,'+encodeURIComponent(svg)}/> : null}</div>
      <p role="status" aria-live="polite">{copied}</p></> : <p>Launch unavailable. Check the current Metro session and client compatibility.</p>}
  </section>;
}
