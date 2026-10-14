import { metroView } from './metro.ts';
import { statusFreshness, type ProjectStatus } from './status.ts';
const record=(v:unknown):v is Record<string,unknown>=>typeof v==='object' && v!==null && !Array.isArray(v);
const number=(v:unknown):v is number=>typeof v==='number' && Number.isFinite(v) && v>=0;
const reasons=new Set(['physical-client-and-launch-rule-unverified','source-graph-not-in-go-profile',
  'report-installed-client-and-os','client-version-not-in-go-profile','expo-go-android-requires-private-http-session',
  'expo-go-cli-login-outside-scope','os-version-not-verified','verified-client-profile','physical-client-certification-expired']);
export type GoView={state:string;reason:string;uri:string|null;expires_at:number|null;client_version:string;os_version:string|null;physical_verified_at:number|null};
export function goView(status:ProjectStatus,project:string,serverTime:number|undefined,elapsed:number,forced=false):GoView|null {
  const v=status.expo_go;
  if (!record(v) || v.schema_version!==1 || v.adapter!=='expo-go-v1' || v.project!==project || v.platform!=='android'
      || v.client_evidence!=='reviewed-profile' || typeof v.state!=='string' || !['compatible','check-required','unsupported'].includes(v.state)
      || typeof v.reason!=='string' || !reasons.has(v.reason) || v.client_version!=='57.0.9' || v.os_version!==null && v.os_version!=='11') return null;
  if (v.state==='compatible' && v.reason!=='verified-client-profile') return null;
  const verified=v.physical_verified_at,expiry=v.certification_expires_at;
  if (verified===null ? expiry!==null || v.state==='compatible' : !number(verified) || !number(expiry) || expiry-verified!==604800) return null;
  const now=serverTime===undefined ? undefined : serverTime+elapsed;
  let state=v.state,reason=v.reason,uri:string|null=null,expires:number|null=null;
  if (state==='compatible' && (now===undefined || !number(verified) || !number(expiry) || now<verified || now>=expiry)) {
    state='check-required';reason='physical-client-certification-expired';
  }
  const launch=v.launch,metro=metroView(status,project,serverTime,elapsed,forced);
  if (launch!==null) {
    if (!record(launch) || launch.schema_version!==1 || launch.project!==project || launch.platform!=='android'
        || !record(status.metro) || launch.generation!==status.metro.generation
        || typeof launch.generation!=='string' || !/^[0-9a-f]{32}$/.test(launch.generation)
        || typeof launch.uri!=='string' || !number(launch.expires_at) || !number(expiry)
        || !number(status.metro.expires_at) || launch.expires_at!==Math.min(expiry,status.metro.expires_at)
        || !new RegExp('^exp://[a-z0-9][a-z0-9.-]*\\.ts\\.net:(?:844[3-9]|8450)/_gptclaw/metro-session/'+launch.generation+'$').test(launch.uri)) return null;
    if (state==='compatible' && metro?.state==='ready' && statusFreshness(status,serverTime,elapsed,forced)==='current'
        && now!==undefined && now<launch.expires_at) {uri=launch.uri;expires=launch.expires_at;}
  }
  return {state,reason,uri,expires_at:expires,client_version:v.client_version,
    os_version:v.os_version as string|null,physical_verified_at:verified as number|null};
}
