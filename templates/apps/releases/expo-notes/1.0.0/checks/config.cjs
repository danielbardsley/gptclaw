const fs = require('node:fs');
const target = 'src/config/backend.generated.ts';
if (!fs.existsSync(target)) {
  fs.mkdirSync('src/config', { recursive: true });
  fs.writeFileSync(
    target,
    'export const backend: { enabled: boolean; profile: string; contractVersion: number; apiUrl: string } = { enabled: false, profile: "development", contractVersion: 1, apiUrl: "https://fixture.invalid/projects/example/api" };\n',
  );
}
