export type Action = 'start' | 'stop' | 'restart' | 'rebuild' | 'pause' | 'resume';
export type Component = 'web' | 'api' | 'db' | 'metro';
export type ControlAction = { action: Action; component: Component | null; enabled: boolean; reason: string | null };
export type Operation = { schema_version: number; operation_id: string; project_key: string; project: string; name: string; action: Action; component: Component | null; state: string; stage: string; stage_component: string | null; reason: string | null; observed_at: number | null; created_at: number; updated_at: number };
export type Controls = { schema_version: number; enabled: boolean; capabilities: { schema_version: number; generation?: string; observed_at: number; actions: ControlAction[]; reason?: string }; recent: Operation[]; retention_days: number };
export const actions: Action[] = ['start','stop','restart','rebuild','pause','resume'];
export function validControls(raw: unknown): Controls | null {
  if (!raw || typeof raw !== 'object') return null;
  const value = raw as Controls;
  if (value.schema_version !== 1 || typeof value.enabled !== 'boolean' || !value.capabilities || value.capabilities.schema_version !== 1 || !Number.isFinite(value.capabilities.observed_at) || !Array.isArray(value.capabilities.actions) || value.capabilities.actions.length > 10 || !Array.isArray(value.recent) || value.recent.length > 5) return null;
  if (value.capabilities.actions.length && (typeof value.capabilities.generation !== 'string' || !/^[0-9a-f]{64}$/.test(value.capabilities.generation))) return null;
  if (value.capabilities.generation != null && !/^[0-9a-f]{64}$/.test(value.capabilities.generation)) return null;
  for (const action of value.capabilities.actions) if (!actions.includes(action.action) || ![null,'web','api','db','metro'].includes(action.component) || typeof action.enabled !== 'boolean' || action.reason !== null && typeof action.reason !== 'string') return null;
  for (const operation of value.recent) if (!/^[0-9a-f]{32}$/.test(operation.operation_id) || !['accepted','running','succeeded','failed','unknown'].includes(operation.state) || !actions.includes(operation.action) || ![null,'web','api','db','metro'].includes(operation.component) || !Number.isFinite(operation.created_at)) return null;
  return value;
}
