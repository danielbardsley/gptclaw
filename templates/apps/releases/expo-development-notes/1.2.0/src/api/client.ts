import { backend } from '../config/backend.generated';
import {
  endpoints,
  type Note,
  type NoteInput,
  type NotesPage,
} from './contract';

export class ApiError extends Error {
  constructor(
    public readonly kind:
      'setup' | 'validation' | 'missing' | 'unavailable' | 'uncertain',
  ) {
    super(
      {
        setup: 'Connect this notebook to its Python backend first.',
        validation: 'Check your title and note length, then try again.',
        missing: 'This note no longer exists. Refresh your notebook.',
        unavailable:
          'Your notebook is out of reach. Check the connection and refresh.',
        uncertain:
          'The server may have received your change. Refresh saved notes before trying again.',
      }[kind],
    );
  }
}

export class NotesClient {
  constructor(
    private readonly config = backend,
    private readonly send: typeof fetch = globalThis.fetch,
  ) {}

  private async request<T>(
    path: string,
    method = 'GET',
    body?: NoteInput,
  ): Promise<T> {
    if (!this.config.enabled) throw new ApiError('setup');
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 15_000);
    try {
      const response = await this.send(this.config.apiUrl + path, {
        method,
        signal: controller.signal,
        headers: {
          Accept: 'application/json',
          ...(body ? { 'Content-Type': 'application/json' } : {}),
        },
        ...(body ? { body: JSON.stringify(body) } : {}),
        redirect: 'error',
      });
      if (!response.ok)
        throw new ApiError(
          response.status === 422
            ? 'validation'
            : response.status === 404
              ? 'missing'
              : method === 'GET'
                ? 'unavailable'
                : 'uncertain',
        );
      return (response.status === 204 ? undefined : await response.json()) as T;
    } catch (error) {
      if (error instanceof ApiError) throw error;
      throw new ApiError(method === 'GET' ? 'unavailable' : 'uncertain');
    } finally {
      clearTimeout(timer);
    }
  }

  list(offset = 0): Promise<NotesPage> {
    return this.request(`${endpoints.collection}?limit=20&offset=${offset}`);
  }
  get(id: string): Promise<Note> {
    return this.request(`${endpoints.collection}/${encodeURIComponent(id)}`);
  }
  save(input: NoteInput, id?: string): Promise<Note> {
    return this.request(
      id
        ? `${endpoints.collection}/${encodeURIComponent(id)}`
        : endpoints.collection,
      id ? 'PUT' : 'POST',
      input,
    );
  }
  remove(id: string): Promise<void> {
    return this.request(
      `${endpoints.collection}/${encodeURIComponent(id)}`,
      'DELETE',
    );
  }
}
