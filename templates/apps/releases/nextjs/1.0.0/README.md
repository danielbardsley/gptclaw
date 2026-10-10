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

For dependency work use the GptClaw `deps` interface with exact versions. Stop
this app, add/update/remove through the reviewed container adapter, review the
package.json/pnpm-lock.yaml diff, test and start it again. Frozen installation
keeps dependency source files unchanged. See `runbooks/manage-project-dependencies.md`
in the selected GptClaw repository. Cache/module folders are not source or Git data.

New projects receive an exact `.gptclaw/toolchain.json` selection. Use the reviewed
`gptclawctl toolchain inspect`/`prepare` workflow; do not install or switch host
languages. Toolchain changes require this app stopped and a supported profile.

Template discovery uses `gptclawctl templates list` and `templates show`.
The separate `.gptclaw/template-release.json` records the original starter;
editing app source does not change that provenance. Template upgrades are manual
reviewed application changes, not an automatic catalogue operation.
