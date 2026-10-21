# Create and operate a private static site

[SPEC-038](../docs/038-static-site-template/spec.md) adds the exact
`nextjs-static@1.0.0` template and static web manifest v10 in provider 1.16.0.
Use the reviewed Node/pnpm dependency/profile and existing private ingress.
Older snapshots cannot recognize this adapter; inspect `gptclawctl --version`
and use a compatible source runner/provider without rewriting old releases.

## Create and inspect

From the GptClaw source checkout with its prepared manifest environment:

```sh
scripts/gptclawctl templates show --template nextjs-static --template-version 1.0.0
scripts/gptclawctl new my-static-site --local-only --template nextjs-static --template-version 1.0.0
scripts/gptclawctl validate --project-root /srv/forge/projects/my-static-site
scripts/gptclawctl start --project-root /srv/forge/projects/my-static-site
scripts/gptclawctl status --project-root /srv/forge/projects/my-static-site
```

The default template remains `nextjs`; select static export explicitly. Generation
refuses existing destinations. The source, exact lockfile/toolchain and starter
provenance are retained. Node/pnpm run inside rootless containers. No new host
packages, application repository, public URL or production service is created.
The ready result returns the existing private `/projects/my-static-site/` URL.

## Edit, rebuild and recover

Edit `app/`, `lib/` and `public/`. Preserve useful navigation, semantic markup,
image alternatives/dimensions and the base-path helper. Static pages export at
build time; no runtime rendering, CMS, cookies, server actions, ISR or remote
asset service is included. The small Node server serves `out/`, not Next.js dev.

```sh
scripts/gptclawctl test --project-root /srv/forge/projects/my-static-site
scripts/gptclawctl rebuild --project-root /srv/forge/projects/my-static-site
scripts/gptclawctl logs --project-root /srv/forge/projects/my-static-site --lines 40
scripts/gptclawctl restart --project-root /srv/forge/projects/my-static-site
scripts/gptclawctl stop --project-root /srv/forge/projects/my-static-site
```

Rebuild stops this preview and removes its route before export. The brief downtime
is intentional. On success a previously running preview starts again; a stopped
project stays stopped. Each activation exports current source; the dependency-only
cache cannot skip content changes. Start on an already ready service is a no-op;
use rebuild/restart to publish source edits. Ordinary build/verify jobs are refused
while active, because they replace output. Other projects keep their routes.

A failed build invalidates its completion marker and cannot start stale/partial
output. Inspect the bounded result/logs, repair the cause, then rebuild. Interrupted
managed controls retain their guard and operation journal: use the documented
`control capabilities` and explicit `control reconcile` with the same operation ID
and project confirmation before another mutation. Do not remove guards/jobs or
cancel unknown operations by hand. See [constrained controls](manage-dashboard.md)
for the exact recovery interface.

The `_gptclaw/ready` endpoint verifies exported-entry/completion availability.
Startup verifies the full output inventory, project ID and source-input digest.
The private prefix is compiled into files, including client navigation payloads;
changing project ID/prefix requires a rebuild. Missing pages have a real 404.
Dotfiles, source paths, traversal, symlinks and directory listings are refused.
Stop retains source, dependencies and derived output; it is not data deletion.

## Quality and adaptation

The generated README documents format/lint/typecheck/test/build/link/security
commands and the pinned browser image. `verify` runs authoring/export/advisory
gates in the Node profile; browser accessibility/navigation is an additional
required CI gate. Browser acquisition is explicit setup, not an offline test.
Advisory network failures fail the security gate. External links are inventoried
without remote network probes. Manual keyboard/focus/200%-zoom acceptance remains
separate from automated axe checks.

For the synthetic example use two distinct owned IDs such as `static-accept-one`
and `static-accept-two`. Check both private routes; edit/rebuild one, inject and
repair a build failure, and stop/start it while checking the other remains ready.
Record exact revision, timings, resource observations and local/CI/live/owner
results separately. Keep fixture source until reviewed cleanup explicitly names
it; never prune shared runtime storage or delete unrelated project volumes.

The home/guide pages and leaf icon intentionally demonstrate this starter. A
product adaptation replaces or removes these with its own approved content,
metadata, navigation and tests. Review rendered routes and remove dependent
imports/styles/fixtures with any demo removal; preserve published template
releases and user data. No existing application is migrated automatically.

Rollback uses reviewed source/provider reversion. Keep a compatible static
provider for existing static projects; an older unknown adapter must fail clearly.
No AWS, production deployment, database migration or ingress reconfiguration is
part of this workflow.
