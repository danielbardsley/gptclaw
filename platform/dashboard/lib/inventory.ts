import type { ProjectLink } from './links.ts';
import type { ProjectStatus } from './status.ts';

export type ProjectRow = {
  key: string; id: string; name: string; kind: string; components: string[];
  location: string; manifest_version: number; runtime_support: string;
  identity_state: string; owner: string | null; repository: string | null;
  documentation: { readme: string; index: string };
  inventory_freshness?: string; status?: ProjectStatus; links?: ProjectLink[];
};
export type Snapshot = {
  schema_version: number; server_time?: number;
  status_capacity?: { limited: boolean }; observed_at?: number;
  last_success_at?: number; freshness: string; complete: boolean;
  truncated: boolean; rows: ProjectRow[]; diagnostics: { code: string }[];
};
