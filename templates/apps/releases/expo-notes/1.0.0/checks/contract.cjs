// Repository-owned generator v1. Frozen with this starter; no network or plugin execution.
const fs = require('node:fs');
const path = require('node:path');
function generate(schema) {
  const operations = {
    '/api/v1/notes': { get: 'list_notes', post: 'create_note' },
    '/api/v1/notes/{note_id}': {
      get: 'get_note',
      put: 'update_note',
      delete: 'delete_note',
    },
  };
  if (
    JSON.stringify(Object.keys(schema.paths).sort()) !==
    JSON.stringify(Object.keys(operations).sort())
  )
    throw new Error('Unexpected API contract routes');
  for (const [route, methods] of Object.entries(operations))
    for (const [method, id] of Object.entries(methods)) {
      if (schema.paths[route]?.[method]?.operationId !== id)
        throw new Error('Breaking API operation');
    }
  const models = schema.components.schemas;
  if (
    models.NoteInput.properties.title.maxLength !== 120 ||
    models.NoteInput.properties.body.maxLength !== 10000 ||
    !models.NoteInput.required.includes('title')
  )
    throw new Error('Breaking input constraints');
  const type = (value) => {
    if (value.$ref) {
      const name = value.$ref.split('/').pop();
      if (!['Note', 'NoteInput', 'NoteSummary', 'NotesPage'].includes(name))
        throw new Error('Unsupported schema reference');
      return name;
    }
    if (value.type === 'string') return 'string';
    if (value.type === 'integer' || value.type === 'number') return 'number';
    if (value.type === 'array') return type(value.items) + '[]';
    throw new Error('Unsupported API type');
  };
  let output =
    '// Generated from the Python OpenAPI contract; run node checks/contract.cjs --write.\n';
  for (const name of ['NoteInput', 'Note', 'NoteSummary', 'NotesPage']) {
    const model = models[name];
    if (model?.type !== 'object') throw new Error('Missing API model');
    output += `export interface ${name} {\n`;
    for (const [key, value] of Object.entries(model.properties)) {
      if (!/^[a-z][a-z_]*$/.test(key))
        throw new Error('Unsupported property name');
      output += `  ${key}${model.required?.includes(key) ? '' : '?'}: ${type(value)};\n`;
    }
    output += '}\n';
  }
  output += "export const endpoints = { collection: '/v1/notes' } as const;\n";
  return output;
}
module.exports = { generate };
if (require.main === module) {
  const schema = JSON.parse(
    fs.readFileSync(path.join('contract', 'openapi.json'), 'utf8'),
  );
  const output = generate(schema);
  const target = path.join('src', 'api', 'contract.ts');
  if (process.argv.includes('--write')) fs.writeFileSync(target, output);
  else if (fs.readFileSync(target, 'utf8') !== output)
    throw new Error(
      'Generated API client/types are stale; regenerate and review',
    );
}
