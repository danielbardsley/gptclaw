import { mkdir, writeFile } from "node:fs/promises";
import { createApp } from "../src/app.ts";
const app = await createApp();
try {
  const response = await app.inject({
    url: `/projects/${process.env.GPTCLAW_PROJECT_ID ?? "local-api"}/ready`,
  });
  if (response.statusCode !== 200)
    throw new Error("Readiness preflight failed");
  if (!app.swagger().paths) throw new Error("OpenAPI preflight failed");
  await mkdir(".gptclaw-cache", { recursive: true });
  await writeFile(
    ".gptclaw-cache/openapi.json",
    JSON.stringify(app.swagger(), null, 2) + "\n",
  );
} finally {
  await app.close();
}
