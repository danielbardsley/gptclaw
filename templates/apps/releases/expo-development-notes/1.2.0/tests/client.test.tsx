import { ApiError, NotesClient } from '../src/api/client';
const config = {
  enabled: true,
  profile: 'development',
  contractVersion: 1,
  apiUrl: 'https://fixture.invalid/projects/backend/api',
};
const reply = (status: number, json = {}) =>
  ({ ok: status < 400, status, json: async () => json }) as Response;

test('uses explicit prefixed paths, correct verbs and never retries writes', async () => {
  const send = jest.fn().mockResolvedValue(reply(200, { title: 'note' }));
  const client = new NotesClient(config, send);
  await client.list(20);
  await client.get('a/b');
  await client.save({ title: 'new' });
  await client.save({ title: 'edit' }, 'one');
  send.mockResolvedValueOnce(reply(204));
  await client.remove('one');
  expect(send.mock.calls.map((call) => call[1].method)).toEqual([
    'GET',
    'GET',
    'POST',
    'PUT',
    'DELETE',
  ]);
  expect(send.mock.calls[0]?.[0]).toBe(
    config.apiUrl + '/v1/notes?limit=20&offset=20',
  );
  expect(send.mock.calls[1]?.[0]).toContain('a%2Fb');
  expect(send.mock.calls[2]?.[1].redirect).toBe('error');
});

test('classifies missing, validation and uncertain outcomes without unsafe retries', async () => {
  for (const [status, kind] of [
    [404, 'missing'],
    [422, 'validation'],
    [503, 'uncertain'],
  ] as const) {
    const send = jest.fn().mockResolvedValue(reply(status));
    await expect(
      new NotesClient(config, send).save({ title: 'draft' }),
    ).rejects.toMatchObject({ kind });
    expect(send).toHaveBeenCalledTimes(1);
  }
  const send = jest.fn().mockRejectedValue(new Error('network'));
  await expect(new NotesClient(config, send).list()).rejects.toMatchObject({
    kind: 'unavailable',
  });
  await expect(
    new NotesClient(config, send).save({ title: 'draft' }),
  ).rejects.toMatchObject({ kind: 'uncertain' });
  await expect(
    new NotesClient({ ...config, enabled: false }, send).list(),
  ).rejects.toBeInstanceOf(ApiError);
  expect(send).toHaveBeenCalledTimes(2);
});

test('request deadlines abort pending requests without another network attempt', async () => {
  jest.useFakeTimers();
  const send = jest
    .fn()
    .mockImplementation(
      (_url: string, options: RequestInit) =>
        new Promise((_resolve, reject) =>
          options.signal?.addEventListener('abort', () =>
            reject(new Error('aborted')),
          ),
        ),
    );
  const request = new NotesClient(config, send).list();
  const expected = expect(request).rejects.toMatchObject({
    kind: 'unavailable',
  });
  await jest.advanceTimersByTimeAsync(15_000);
  await expected;
  expect(send).toHaveBeenCalledTimes(1);
  jest.useRealTimers();
});
