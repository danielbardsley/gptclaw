import { createApp } from "../src/app.ts";
const app = await createApp();
try {
  const response = await app.inject({
    url: `/projects/${process.env.GPTCLAW_PROJECT_ID ?? "local-api"}/ready`,
  });
  if (response.statusCode !== 200)
    throw new Error("Readiness preflight failed");
  if (!app.swagger().paths) throw new Error("OpenAPI preflight failed");
} finally {
  await app.close();
}
