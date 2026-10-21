# Notes frontend component

This Next.js/React/TypeScript UI belongs to the parent notes project. Use the
parent group root for lifecycle and `--component web` for targeted jobs/logs.
Read [component guidance](AGENTS.md). The frontend runs in its own rootless
container and calls the API at the same private browser origin and project prefix.

Use the notes list and plain-text editor to create, save, paginate and delete;
delete asks for confirmation. Failed requests retain the draft in browser memory.
Refresh loses unsaved drafts but preserves saved notes while the API process lives.
All viewers share the persistent development database; reload and restart retain notes.

`pnpm typecheck`, `pnpm test`, `pnpm build` and `pnpm verify` run inside the exact
reviewed Node/pnpm profile. The provider probes the rendered page for readiness;
`health/` also diagnoses API dependency readiness and `alive/` reports liveness.
Runtime-owned project identity configures the base path and private development
origin. Dependency changes require the whole group stopped; no unpinned installs
or container/host credential forwarding are allowed.
