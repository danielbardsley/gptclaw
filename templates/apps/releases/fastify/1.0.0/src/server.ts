import { createApp } from "./app.ts";
const app = await createApp();
for (const signal of ["SIGINT", "SIGTERM"] as const) {
  process.once(signal, () => {
    void app.close();
  });
}
await app.listen({ host: "0.0.0.0", port: 8000 });
