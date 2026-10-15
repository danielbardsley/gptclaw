const assert = require('node:assert/strict');
const fs = require('node:fs');
const { NotesClient } = require('./api/client.js');
const client = new NotesClient({ enabled: true, profile: 'development', contractVersion: 1, apiUrl: process.env.GPTCLAW_COMPAT_URL });
(async () => {
  let ready = false;
  for (let attempt = 0; attempt < 30; attempt++) {
    try { await client.list(); ready = true; break; } catch { await new Promise(resolve => setTimeout(resolve, 500)); }
  }
  assert(ready, 'Python API did not become ready');
  const file = '/output/native-v1.json';
  if (process.env.GPTCLAW_COMPAT_PHASE === 'before') {
    const note = await client.save({ title: 'Native v1 compatibility', body: 'Persisted before migration.' });
    const updated = await client.save({ title: note.title, body: 'The old native client still works.' }, note.id);
    assert.deepEqual(await client.get(note.id), updated);
    assert((await client.list()).items.some(item => item.id === note.id));
    fs.writeFileSync(file, JSON.stringify(updated));
  } else {
    const note = JSON.parse(fs.readFileSync(file, 'utf8'));
    assert.deepEqual(await client.get(note.id), note);
    const updated = await client.save({ title: note.title, body: 'Updated after additive migration.' }, note.id);
    assert.equal(updated.id, note.id);
    await client.remove(note.id);
    await assert.rejects(client.get(note.id), { kind: 'missing' });
  }
  console.log('PASS: retained native v1 client ' + process.env.GPTCLAW_COMPAT_PHASE + ' migration');
})().catch(() => { console.error('Retained native API contract check failed'); process.exitCode = 1; });
