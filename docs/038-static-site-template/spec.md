# SPEC-038 — Static site template (TPL-005)

Status: Implementation verified in review; final CI gates and merge pending. Owner: Project owner. Date: 2026-10-21 (America/New_York).
[Technical design](technical-design.md) · [Tasks](tasks.md) ·
[Catalogue](../platform/features.md) · [Architecture](../platform/architecture.md)

## Outcome and authorization

Create a repeatable static website through the existing template catalogue and
managed private application workflow. The generated site exports HTML, CSS and
JavaScript at build time; its private preview serves those files without a
Next.js application server. A developer can edit content, rebuild, and verify
accessible pages, working links and bounded asset sizes before sharing privately.

The project owner requested this planning set and explicitly selected Next.js
static export using the existing stack. That framework choice is recorded;
the project owner subsequently instructed “Ok, lets implement the spec.” This
approves the bounded scope, budgets and explicit rebuild/downtime design and
authorizes implementation and necessary reversible verification. PR review, merge
and owner acceptance remain distinct; public exposure and production are excluded.

## Scope and baseline

Include one immutable catalogue release, a small TypeScript/App Router site,
static export, a containerized private file server, generated quality/CI checks,
provider integration, adaptation guidance and a synthetic end-to-end example.
Reuse the existing Node/pnpm profile, dependency policy, rootless lifecycle,
resource limits, owned routes and project inventory. Keep the default Next.js
starter and all published template releases unchanged.

The existing `nextjs@1.0.0` starter builds Next.js and starts `pnpm dev`; it is
not a static-serving adapter. Its health route and provider validation cannot
simply be relabelled. Catalogue schemas currently extend through v7 and project
manifests through v9. New contract numbers must be allocated at implementation
against the then-current baseline.

Exclude CMS/Markdown pipelines, remote content fetching, search services,
authentication, forms/backends, databases, server actions, request-time rendering,
ISR, runtime image optimization, public previews, production hosting, DNS/CDN,
AWS/HCP changes, host package installation and new application repositories.
Source changes use an explicit managed rebuild; automatic refresh/watch mode is
outside this initial slice. No application data migration is needed.

## Requirements

- STATIC-001 — Exact generation. Discover and select a proposed
  `nextjs-static@1.0.0` release with hashed assets, exact toolchain/dependencies
  and provenance. Discovery stays offline and executes no application code.
  Invalid selection, tampered assets and occupied destinations fail safely.
  Existing templates, defaults, manifests and provider snapshots remain valid.
- STATIC-002 — Usable static starter. Provide a responsive home page, a nested
  information page, shared navigation, local image/icon, metadata and a useful
  missing-page design. Main content and navigation work without JavaScript.
  Export a self-contained `out/` tree with no required third-party requests,
  backend or secrets. Unsupported server features fail the build clearly.
- STATIC-003 — Private path correctness. Serve exported pages, CSS, scripts,
  images and client-navigation payloads under `/projects/<project-id>/`.
  Direct nested loads, browser refresh, navigation, anchors and trailing-slash
  handling work. Unknown paths return HTTP 404, not a home-page fallback.
  Requests outside the prefix, traversal and symlink escapes cannot expose source,
  dotfiles or other projects. Build-time identity mismatches fail activation.
- STATIC-004 — Managed lifecycle and update. Support validate/start/status/logs/
  test/restart/rebuild/stop through existing interfaces, with real exported-output
  readiness and owned route handling. First start builds; source edits become
  visible after a successful explicit rebuild. A failed/interrupted build never
  activates partial or stale output as a successful new revision. Report failure
  and permit repair/rebuild recovery. Stop retains source; unrelated apps remain
  available. Do not assume the existing dependency-only build digest detects edits.
- STATIC-005 — Accessibility and link quality. Include semantic landmarks,
  descriptive page titles, labelled navigation, skip link, visible keyboard focus,
  meaningful image alternatives and readable contrast. Require zero automated
  WCAG 2.2 A/AA rule violations on starter pages and manual keyboard/zoom checks.
  Check all exported internal page, asset and fragment references; broken targets
  fail. External references are inventoried; network link checks are optional and
  separate from deterministic quality gates.
- STATIC-006 — Performance and engineering gates. Provide exact dependencies,
  frozen restore, check-only formatting/lint, strict typecheck, behavior tests,
  static build, link/accessibility/asset-budget checks, security checks, container
  recipe and pinned generated CI. Proposed starter budgets: each page's unique
  first-load assets total at most 300 KiB gzip JavaScript, 50 KiB gzip CSS,
  100 KiB uncompressed HTML and 1 MiB local images/fonts; whole `out/` is at most
  10 MiB uncompressed. Record build/start timing and container resource observations
  against existing runtime deadlines; do not impose network-dependent page-speed
  scores. Deliberate defects must fail their corresponding gates.
- STATIC-007 — Documented adoption and evidence. Explain content/layout editing,
  static limitations, image handling, build-time base paths, rebuild/recovery,
  quality commands and safe starter adaptation. Include example generation and
  scoped cleanup guidance. Record exact revisions, local/CI/private-browser results
  and project-owner acceptance separately before calling this slice Delivered.

## Acceptance criteria

| ID | Observable evidence required | Requirements |
|---|---|---|
| AC-001 | Offline generation/discovery, hash/selection/destination refusals, source/snapshot parity and historical/default-template regressions pass. | STATIC-001 |
| AC-002 | Frozen restore and generated checks pass; `out/` is served with no Next.js application process or runtime content fetch. Direct HTML contains useful content and navigation with JavaScript disabled. An unsupported server-feature fixture fails build. | STATIC-002,006 |
| AC-003 | Actual private HTTPS home/nested refresh/navigation/anchors/assets and missing-page checks pass; automated HTTP tests reject prefix escapes, encoded traversal, symlinks and source/dotfile reads. MIME types and HEAD behavior are correct. | STATIC-003 |
| AC-004 | Managed lifecycle passes for two independent sites. An edit appears after rebuild; injected build failure/interruption never publishes partial output or reports the edit ready. Repair/rebuild succeeds. Stop removes only the owned route and retains source; restart recovers it. | STATIC-004 |
| AC-005 | Automated accessibility and complete internal-reference checks pass. Injected missing alt text, broken route/asset/fragment and over-budget assets fail. Project owner verifies keyboard navigation, visible focus and 200% zoom at desktop and narrow viewport. | STATIC-005,006 |
| AC-006 | Budget report, timings, resource observations, generated CI and container checks pass for the exact reviewed revision. Runbook and adaptation/example instructions are verified; evidence distinguishes local, CI, live behavior and owner acceptance. | STATIC-006,007 |

## Completion and ownership

Deliver through a reviewable implementation PR after scope approval and
implementation authorization. The project owner owns those decisions and final
acceptance. Verification is tracked in [acceptance.md](acceptance.md); local, CI, private
runtime and project-owner results remain distinct. Mark Delivered only after merged implementation and all
required acceptance evidence. Private live fixtures and any later host/provider
installation must use the applicable reviewed procedures and scoped authorization.
