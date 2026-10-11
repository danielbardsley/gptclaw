"use client";
import { useCallback, useEffect, useState } from 'react';

type Note = { id: string; title: string; body: string };
type Summary = { id: string; title: string; preview: string };
type Page = { items: Summary[]; total: number; limit: number; offset: number };
const base = `${process.env.NEXT_PUBLIC_PROJECT_PATH}/api/v1/notes`;

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, { ...options, cache: 'no-store', signal: AbortSignal.timeout(10000) });
  if (!response.ok) throw new Error(response.status === 409 ? 'The 100-note limit has been reached.' : 'The request failed. Your draft has been kept. Try again when the API is ready.');
  return response.status === 204 ? undefined as T : await response.json() as T;
}

export default function Notes() {
  const [page, setPage] = useState<Page>({ items: [], total: 0, limit: 20, offset: 0 });
  const [offset, setOffset] = useState(0);
  const [selected, setSelected] = useState<string | null>(null);
  const [title, setTitle] = useState('');
  const [body, setBody] = useState('');
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const load = useCallback(async () => {
    setLoading(true);
    try { setPage(await request<Page>(`${base}?limit=20&offset=${offset}`)); }
    catch (failure) { setError(failure instanceof Error ? failure.message : 'Could not load notes.'); }
    finally { setLoading(false); }
  }, [offset]);
  useEffect(() => { void load(); }, [load]);
  function clear() { setSelected(null); setTitle(''); setBody(''); setError(''); }
  async function save(event: React.FormEvent) {
    event.preventDefault(); setBusy(true); setError('');
    try {
      const note = await request<Note>(selected ? `${base}/${selected}` : base, {
        method: selected ? 'PUT' : 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: title.trim(), body }),
      });
      setSelected(note.id); setTitle(note.title); setBody(note.body); await load();
    } catch (failure) { setError(failure instanceof Error ? failure.message : 'Could not save.'); }
    finally { setBusy(false); }
  }
  async function select(id: string) {
    setBusy(true); setError('');
    try { const note = await request<Note>(`${base}/${id}`); setSelected(note.id); setTitle(note.title); setBody(note.body); }
    catch (failure) { setError(failure instanceof Error ? failure.message : 'Could not open note.'); }
    finally { setBusy(false); }
  }
  async function remove() {
    if (!selected || !window.confirm('Delete this note?')) return;
    setBusy(true); setError('');
    try { await request<void>(`${base}/${selected}`, { method: 'DELETE' }); clear(); await load(); }
    catch (failure) { setError(failure instanceof Error ? failure.message : 'Could not delete.'); }
    finally { setBusy(false); }
  }
  return <main>
    <header><p className="eyebrow">PRIVATE WORKSPACE</p><h1>Notes</h1>
      <p>A small place for temporary ideas.</p></header>
    <aside className="notice">Shared, temporary notes. All notes are lost when the API reloads or this project restarts.</aside>
    <div className="workspace">
      <section aria-label="Notes list"><div className="list-heading"><h2>Your notes <span>{page.total}</span></h2>
        <button onClick={clear} disabled={busy}>New note</button></div>
        {loading && <p role="status">Loading notes…</p>}
        {!loading && page.items.length === 0 && <p>No notes yet. Write your first idea.</p>}
        <ul>{page.items.map(note => <li key={note.id}><button className={selected === note.id ? 'chosen' : ''} disabled={busy} onClick={() => void select(note.id)}>
          <strong>{note.title}</strong><span>{note.preview || 'Empty note'}</span></button></li>)}</ul>
        <nav aria-label="Note pages"><button disabled={busy || loading || offset === 0} onClick={() => setOffset(Math.max(0, offset - 20))}>Previous</button>
          <button disabled={busy || loading || offset + 20 >= page.total} onClick={() => setOffset(offset + 20)}>Next</button></nav>
      </section>
      <section aria-label="Note editor"><h2>{selected ? 'Edit note' : 'New note'}</h2>
        <form onSubmit={save}><label htmlFor="title">Title</label>
          <input id="title" value={title} onChange={e => setTitle(e.target.value)} maxLength={120} required disabled={busy} />
          <label htmlFor="body">Note</label><textarea id="body" value={body} onChange={e => setBody(e.target.value)} maxLength={10000} rows={12} disabled={busy} />
          <p className="count">{body.length.toLocaleString()} / 10,000 characters</p>
          {error && <p role="alert">{error}</p>}
          <div className="actions"><button type="submit" disabled={busy || !title.trim()}>{busy ? 'Saving…' : 'Save note'}</button>
            {selected && <button type="button" className="danger" onClick={() => void remove()} disabled={busy}>Delete note</button>}</div>
        </form>
      </section>
    </div>
  </main>;
}
