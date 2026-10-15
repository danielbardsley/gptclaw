# Private TypeScript API starter

Generate with `gptclawctl new my-api --template fastify --template-version 1.0.0 --local-only`.
Use `gptclawctl start --project-root PATH`, then the returned private project URL
with `/ready`, `/live`, `/api/v1/echo`, `/api/v1/examples`, `/openapi.json` and
`/docs/`. Echo accepts JSON `{"message":"hello"}`. List accepts offset and limit
(1–100); examples are synthetic and stateless. Swagger assets are bundled.

Use `gptclawctl lint|typecheck|test|build|security|verify --project-root PATH`.
`format` intentionally writes source and requires a stopped service. `security`
queries npm advisories and fails if the service is unavailable or high/critical
advisories exist. Dependencies restore from the frozen lock without install hooks.
Use managed `deps` commands for changes; do not edit installed packages.
The existing Node 24.21.0 / pnpm 12.10.1 profile supplies all commands.
`Containerfile` also builds a standalone compiled API; publish its port only on
loopback. Managed development uses Node watch mode and no unrestricted proxy trust.
`status`, bounded `logs`, `restart` and `stop` use the normal project lifecycle.
Stop retains source. PostgreSQL, migrations, authentication, production and public
exposure are outside this initial slice. Replace the sample API and tests when
adapting this starter to an approved product specification.
