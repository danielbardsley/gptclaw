# Your private web app

Edit `app/page.tsx` and `app/globals.css` to make the starter your own. Keep
`app/api/health/route.ts` and the declared base path working. Read AGENTS.md before
material work; create the product's own specification when developing a feature.

Use the installed GptClaw runner at
`/srv/forge/projects/.gptclaw-runtime/v1/gptclawctl` with `--project-root` set to
this directory. `start` returns the actual private URL; `status` reports health
and route readiness; `logs --lines 40` returns scoped diagnostics. `test` runs
the health test in the pinned container. `restart` deliberately transitions the
service; `stop` removes its mapping/runtime resources and preserves source.

Node/pnpm live inside the reviewed toolchain container. The frozen lockfile
makes dependency preparation repeatable; no host language installation is needed.
Source and local build caches are retained, but application data is ephemeral.
Secrets, databases, public sharing and production are outside this first slice.
