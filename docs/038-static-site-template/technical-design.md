# TDD-038 — Next.js static export and private file preview

Status: Proposed. Owner: Project owner. Date: 2026-10-21 (America/New_York).
[Specification](spec.md) · [Tasks](tasks.md)

## Existing evidence and approach

Read baseline: `origin/main` at `fc2c737`. The existing
[release package](../../templates/apps/releases/nextjs/1.0.0/package.json) pins
Next.js 16.4.0, React 19.3.0 and TypeScript 6.0.3. The
[Node profile](../../config/toolchains/v1.json) pins Node 24.21.0 and pnpm 12.10.1.
These are observed repository pins, not assertions about latest versions or
security status. Reuse a reviewed compatible profile at implementation; freeze
new check dependencies and validate advisories without modifying old releases.

The selected framework supports `output: 'export'`, with `next build` producing
`out/`; `basePath` is fixed at build time. See the official
[static export guide](https://nextjs.org/docs/app/guides/static-exports) and
[basePath reference](https://nextjs.org/docs/app/api-reference/config/next-config-js/basePath),
consulted October 21, 2026. Validate behavior against the exact pinned release;
current documentation alone does not establish compatibility. Use
`trailingSlash: true`, local assets/system fonts and ordinary unoptimized images
with dimensions. Avoid request-dependent routes and default image optimization.

Add a distinct `nextjs-static-v1` adapter and `nextjs-static@1.0.0` catalogue
entry; do not change `nextjs-v1` semantics. Keep project kind `web`, private
exposure and ephemeral derived output. Allocate explicit new manifest/catalogue
schema versions if existing strict contracts cannot express the adapter. Do not
loosen historical schemas or route all unknown providers to Next.js.

## Components and planned changes

| Component | Proposed responsibility | Requirements |
|---|---|---|
| `templates/apps/releases/nextjs-static/1.0.0/` | App Router pages/layout/CSS/assets, export config, file-server script, quality tests, exact lockfile, standards, CI and Containerfile | STATIC-002,003,005,006,007 |
| `config/templates/`, `schemas/templates/`, `schemas/project/` | Add exact release inventory and explicit adapter/command compatibility without changing published contracts | STATIC-001,004 |
| `scripts/project_templates.py`, `project_manifest.py`, new static adapter | Generation, provenance, validation and supported command vectors; reject unsupported versions before execution | STATIC-001,003,004 |
| `scripts/private_apps.py`, dependency/toolchain and control dispatch | Static build readiness/update identity, existing locks/resources/jobs/receipts; source and immutable snapshot capability parity | STATIC-001,004 |
| Existing provider snapshot inventory, CLI capabilities and dashboard projection | Include new assets/contracts and report a private web project through existing observation interfaces; add dispatch only where required | STATIC-001,004 |
| `scripts/tests/`, generated checks and `.github/` quality paths | Synthetic generation, protocol, failure/recovery, historical compatibility and actual exported-browser checks | STATIC-001–006 |
| Runbook, release/example guidance and initiative acceptance | Explain static constraints, source edits/rebuild, evidence and safe retention/cleanup | STATIC-007 |

## Build and serving contract

Propose `pnpm build` for validated export and `pnpm start` for a small Node file
server, using the existing Node container profile. Do not use `next start` or
`next dev` for managed static acceptance. The server only reads a completed export
root; it does not render React or load project source. Bind port 3000 inside the
isolated container, publishing only the existing allocated loopback host port.

Validate the project ID using the existing slug rules. Compile
`/projects/<id>` into Next.js config and record ID, source-input digest and output
inventory with the completed build. The server verifies completion and identity
before readiness. Reserve a prefixed health endpoint outside authored page space;
readiness must verify the expected exported entry and manifest, not merely that
the server process is alive. Specify/test the exact endpoint and collision refusal
when implementing the versioned contract.

Strip exactly one validated prefix, decode paths safely, resolve files inside the
export root and refuse traversal, dotfiles, directory listings and symlinks.
Support GET/HEAD, correct HTML/CSS/JS/image types and bounded error responses;
other methods return 405. Directory routes map to `index.html`; missing paths
serve exported 404 content with 404 status. Explicitly test Next.js navigation
payload requests. No SPA fallback, request proxying or user-controlled filesystem
root. Use revalidation/no-cache for initial preview correctness; avoid stale HTML
and client chunks across rebuilds.

## Update, failure and rollback

Use existing managed locks and bounded jobs. Initially use a stop/build/start
rebuild sequence with accepted preview downtime, rather than introducing hot
publication or a watcher. Stop the owned service before replacing output. Build
in task-owned staging, verify required pages/inventory/identity, and publish only
completed output. Retain diagnostic operation state on interruption. Failure
leaves the service stopped/failed and its route unavailable; retained prior files
must not satisfy readiness for the failed revision. Repair then rebuild is the
recovery path. No automatic stale-output fallback is promised.

The existing `prepare()` build digest covers dependency inputs, not all source.
For this adapter, hash the explicit source/config/public/lock/toolchain inputs
(excluding generated output, caches, Git and credentials), or force export on
start; implementation must prove source edits are not skipped. Record the
successful source revision/digest. Ordinary restart must validate/rebuild changed
inputs. Keep existing adapters' cache behavior unchanged.

Rollback uses reviewed source/provider reversion and a successful rebuild under
the compatible static provider. Historical provider snapshots need not recognize
new adapters; report that limitation rather than reinterpret their marker.
Preserve generated projects, published releases, source and unrelated routes.
There is no persistent database or infrastructure migration.

## Quality and acceptance execution

Use synthetic home/nested pages and local assets only. Pin browser/accessibility
and formatting/lint tools during implementation using the dependency policy;
reuse existing isolated browser/container patterns where compatible. Browser
acquisition is explicit setup, never a silent host install or offline test step.

Run checks against exported files through the static server. Crawl HTML/CSS
references plus generated navigation requests, resolving prefixed URLs and fragment
IDs while excluding the reserved health endpoint from content budgets. Count
unique first-load assets per page with a documented deterministic gzip method;
include shared chunks and preload assets, inventory fonts/images, and cap the
whole export separately. Enforce spec budgets with negative fixtures. Inventory
external references without making offline checks depend on remote availability.

Require zero automated violations from the pinned WCAG 2.2 A/AA ruleset and
manual keyboard/focus/zoom checks; automation alone does not prove accessibility
conformance. Capture browser console/network errors, private HTTPS route behavior,
JavaScript-disabled content and independent-service retention. Security advisory
service failure remains failure, distinct from offline repository tests.

Repository checks, release immutability and generated container checks precede
CI. Live private acceptance needs existing reviewed runtime/ingress prerequisites
and named task-owned fixtures; this planning task starts no service. Record
commands/results, revision, budget measurements, CI links and owner disposition
in a later acceptance record. Keep local, CI and live/owner results separate.

## Traceability and review decisions

| Requirements | Mechanism | Tasks | Acceptance |
|---|---|---|---|
| STATIC-001 | Exact catalogue, strict contracts and snapshot parity | T2,T3,T6 | AC-001 |
| STATIC-002 | Export-only pages, local content and no-JS checks | T3,T5 | AC-002 |
| STATIC-003 | Prefix-bound file server and protocol/browser tests | T3,T5,T7 | AC-003 |
| STATIC-004 | Input-aware build, readiness and stop/build/start recovery | T4,T6,T7 | AC-004 |
| STATIC-005 | Semantic starter, reference crawler and accessibility checks | T3,T5,T7 | AC-005 |
| STATIC-006 | Pinned quality/CI, budgets, faults and measured runtime | T3,T5,T6,T7 | AC-002, AC-005, AC-006 |
| STATIC-007 | Adaptation/runbook/example and acceptance record | T3,T7,T8 | AC-006 |

Framework choice is settled by the project owner: Next.js static export.
Remaining proposed defaults are the release identity, explicit rebuild with
preview downtime, budgets and no CMS/backend. The project owner reviews these
with the planning PR before implementation authorization. Exact new schema numbers
and pinned check-tool versions are implementation decisions, resolved against
current sources and verified in T2/T5; no existing contract version is reserved.
