# Static field guide

A small Next.js/TypeScript website exported to HTML, CSS and JavaScript. The
example home/guide pages and leaf asset intentionally demonstrate this template.
No Next.js rendering server is used for preview; Node serves the completed out/.

## Edit and check

Edit app/page.tsx, app/guide/getting-started/page.tsx, app/layout.tsx and
app/globals.css. Put local images in public/ and use lib/site.ts for their prefix.
Keep image dimensions and alternative text. System fonts avoid remote downloads.
All content/navigation works without JavaScript. Use strict TypeScript, descriptive
names, small components, semantic HTML, and check-only formatter/linter commands.
Use prettier --write only when intentionally editing formatting, in the container.

Run pnpm format, lint, typecheck and test in the pinned authoring container.
Set GPTCLAW_PROJECT_ID to the managed project ID, then pnpm build and pnpm links.
The latter validates internal pages/assets/fragments and asset budgets; external
URLs are inventoried, not fetched. pnpm security requires the public advisory
service and fails if unavailable. pnpm browser requires the pinned browser image
in checks/Browser.Containerfile, with this source mounted at /workspace and
PLAYWRIGHT_BROWSERS_PATH=/ms-playwright. It checks WCAG A/AA rules and real exported
navigation; manual keyboard, contrast, focus and 200% zoom review still applies.
pnpm verify runs the authoring/export and online advisory gates. Run pnpm browser
separately in the pinned browser image; CI requires both.

## Private preview and rebuild

Use the reviewed gptclawctl lifecycle with --project-root pointing to this project:
validate, start, status, logs, test, restart, rebuild and stop. Node/pnpm run in
containers, not on the host. start exports once before activation; restart
exports again. Edit then rebuild to publish changes. A running preview is stopped
before export; failed/interrupted export never becomes ready. Inspect bounded
logs/status, repair the source and retry the same managed recovery workflow.
An interrupted lifecycle guard requires control inspection/recovery, not deletion.
A stopped project's rebuild leaves it stopped. Stop removes its owned route and
retains source. Build/verify jobs are refused while this preview runs; use rebuild.

The URL is /projects/<project-id>/. The ID is compiled into the export, including
assets and navigation. Rebuild for a different prefix; do not move output and
pretend it is relocatable. Missing paths return a genuine 404. The reserved
_gptclaw/ready path is not authored content. Export identity/inventory completion
is required at startup. Directory listing, dotfiles, symlinks and traversal are
refused. Use the existing private ingress; no Funnel, CDN or production hosting
is configured. SSR, ISR, cookies, server actions, dynamic routes without known
build-time parameters and runtime image optimization are outside this template.

## Budgets and adaptation

Each exported HTML page permits at most 300 KiB gzip unique first-load JS, 50 KiB
gzip CSS, 100 KiB raw HTML and 1 MiB local images/fonts; the entire out/ is capped
at 10 MiB raw. The report includes shared/preloaded assets and CSS dependencies.
Gzip uses Node zlib with default settings. No network-dependent speed score is
required. Record build/start timings separately under the managed resource limits.

For a real product replace example titles/copy/metadata, leaf asset and guide
route; update layout links, page tests and exported-reference checks together.
Remove unused demonstrations and dependent imports/styles/tests. Keep reusable
health, accessibility and security support. Review rendered routes against the
product spec, documenting any intentionally retained examples. Do not rely on
inherited demonstration tests as product acceptance. Preserve source/data and
published starter releases. No data migrations or CMS integration are included.
