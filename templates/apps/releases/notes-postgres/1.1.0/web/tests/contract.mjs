import assert from 'node:assert/strict';
const url = process.env.GPTCLAW_CONTRACT_API_URL;
if (!url)
  throw new Error(
    'An isolated API must be provided by the group contract runner',
  );
let ready = false;
for (let attempt = 0; attempt < 40; attempt++) {
  try {
    ready = (
      await fetch(url + '/api/ready', { signal: AbortSignal.timeout(1000) })
    ).ok;
  } catch {
    /* Retry only within the bounded fixture readiness deadline. */
  }
  if (ready) break;
  await new Promise((resolve) => setTimeout(resolve, 500));
}
assert.ok(ready, 'isolated API readiness');
const schema = await (await fetch(url + '/api/openapi.json')).json();
assert.ok(schema.paths['/api/v1/notes']);
const response = await fetch(url + '/api/v1/notes', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    title: 'Synthetic contract',
    body: '<script>plain text</script>',
  }),
});
assert.equal(response.status, 201);
const note = await response.json();
assert.equal(note.title, 'Synthetic contract');
assert.equal(note.body, '<script>plain text</script>');
const location = `${url}/api/v1/notes/${note.id}`;
assert.equal((await fetch(location)).status, 200);
assert.equal(
  (
    await fetch(location, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: 'Updated contract', body: '' }),
    })
  ).status,
  200,
);
assert.equal((await fetch(location, { method: 'DELETE' })).status, 204);
assert.equal((await fetch(location)).status, 404);
console.log('Cross-service OpenAPI and CRUD contract passed.');
