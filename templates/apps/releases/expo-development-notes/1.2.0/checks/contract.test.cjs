const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const { generate } = require('./contract.cjs');
const source = JSON.parse(fs.readFileSync('contract/openapi.json', 'utf8'));
test('deterministic Python contract output and breaking operation/input refusal', () => {
  assert.equal(generate(source), generate(JSON.parse(JSON.stringify(source))));
  for (const alter of [
    (s) => {
      s.paths['/api/v1/notes'].post.operationId = 'incompatible';
    },
    (s) => {
      s.components.schemas.NoteInput.properties.title.maxLength = 999;
    },
    (s) => {
      s.components.schemas.Note.properties.id.type = 'object';
    },
  ]) {
    const changed = JSON.parse(JSON.stringify(source));
    alter(changed);
    assert.throws(() => generate(changed));
  }
});
