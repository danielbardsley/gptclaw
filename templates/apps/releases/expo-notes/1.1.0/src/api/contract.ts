// Generated from the Python OpenAPI contract; run node checks/contract.cjs --write.
export interface NoteInput {
  body?: string;
  title: string;
}
export interface Note {
  body?: string;
  id: string;
  title: string;
}
export interface NoteSummary {
  id: string;
  preview: string;
  title: string;
}
export interface NotesPage {
  items: NoteSummary[];
  limit: number;
  offset: number;
  total: number;
}
export const endpoints = { collection: '/v1/notes' } as const;
