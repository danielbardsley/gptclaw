export type Change = { kind: string; at: number; after_gap: boolean; previous_observation_at: number | null };
export type ServiceStatus = {
  state: string; provider_state: string; health: string; operation_busy: boolean;
  reason?: string | null; freshness: string; observed_at?: number | null;
  last_success_at?: number | null; last_observed_change?: Change | null;
  uptime_seconds?: number | null; uptime_reason?: string | null;
  restart_count?: number | null; restart_reason?: string | null;
};
export type ProjectStatus = ServiceStatus & { components: Record<string, ServiceStatus>; publication: { state: string; origin: string | null }; provider_version: string | null };
export function statusFreshness(status: ServiceStatus, serverTime: number | undefined, elapsed: number, forced = false): string {
  if (forced) return status.last_success_at == null ? 'unavailable' : 'stale';
  if (status.freshness !== 'current') return status.freshness;
  if (status.last_success_at == null || serverTime == null) return 'unavailable';
  const age = serverTime + elapsed - status.last_success_at;
  return age < 0 || age > 30 ? 'stale' : 'current';
}
export function duration(seconds: number | null | undefined): string {
  if (seconds == null) return 'Unavailable';
  const days = Math.floor(seconds / 86400), hours = Math.floor(seconds % 86400 / 3600), minutes = Math.floor(seconds % 3600 / 60);
  if (days) return `${days}d ${hours}h`;
  if (hours) return `${hours}h ${minutes}m`;
  if (minutes) return `${minutes}m ${Math.floor(seconds % 60)}s`;
  return `${seconds}s`;
}
