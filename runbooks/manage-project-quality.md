# Project quality gates

QLT-001–QLT-010 add application quality tooling, not a runtime installation or
production pipeline. Implementation is reviewed through the QLT PR; no merge or
managed deployment is part of the overnight implementation authorization.

## Select and inspect

Select an exact `1.1.0` quality release for Next.js, FastAPI, Fastify, notes,
notes-postgres, fastapi-postgres, expo-react-native or expo-notes through existing
template discovery/creation. Historical releases keep their bytes and explicit
selection; adoption by existing applications is a reviewed source change. The source
catalogue's default is Next.js 1.1.0; installed providers retain their current
catalogue until a separately authorized rollout. Explicit old release selection
remains available.
Do not replace `.gptclaw` provenance or persistent data to upgrade an application.

Generated `quality.json` version 1 is a separate strict quality contract. It
exposes format/lint/typecheck/test/build/security/verify vectors, component roots
and pinned toolchain recipes without changing existing lifecycle schemas or
installing a provider. Inspection and JSON validation execute no project code:

```bash
python3 checks/gptclaw_quality.py inspect
python3 checks/gptclaw_quality.py verify --engine podman
```

Docker is supported for isolated CI (`--engine docker`). The host needs Python 3
and the selected reviewed container engine. Dependency restore and application language commands run inside bounded
containers. The reviewed Python quality controller and integration adapters
run on the host to operate the container engine; review these scripts before
executing an unfamiliar checkout. Exact lockfiles, image digests
and verified package-manager artifacts are retained. Source-writing `format` is
explicit; verify checks formatting and refuses unexpected source changes. Build outputs (including Next-generated environment declarations), caches and
reviewed ignored mobile public binding outputs are excluded from the source-change
check and artifacts. They remain subject to their existing binding/toolchain rules. Dependency/advisory failures are failures.
Database test actions delegate to the existing owned disposable integration
adapter, which provisions its own PostgreSQL data and synthetic credentials.

Generated CI runs on pull requests and main pushes with read-only permissions,
immutable action commits, no persisted checkout credentials, bounded jobs,
per-ref caches keyed by OS/architecture/lock/toolchain and one final `required`
check. Artifacts contain only the structured quality report with seven-day
retention; raw logs, environment dumps and credentials are not uploaded.
Configuring a repository's required branch checks remains a separate operation.

## Dependency updates

Generated Dependabot configs cover each npm/pip component and Actions weekly,
with one open PR per component/ecosystem (at most four in this matrix). Compatible
patch/minor updates are grouped; majors and coupled Expo/React Native/toolchain
upgrades require explicit review. There is no auto-merge and no private registry
credential. Frozen restore and normal CI apply to updater PRs. Triage failures by
reproducing the exact lockfile; record the owner, reason, review date and expiry
of any deferral. Pause with a reviewed config change. Updating GptClaw's starter
pins means publishing a new immutable release, never editing a historical one.

## Smoke and accessibility

Single web/API releases start an owned service on an internal container network,
then verify readiness, prefixed URL, assets, useful requests and bundled API docs.
Web journeys include real keyboard activation, narrow layout, enlarged text,
reduced motion and automated axe checks. Group projects retain the existing CRUD,
error/draft, persistence and browser assertions plus the bundled axe checks.
The exact axe version, public artifact integrity, license and source are included
in each web-capable release. Native source tests retain role/label/state checks;
source/bundle success does not establish TalkBack or VoiceOver acceptance.

The separate `smoke --input TARGET.json` adapter accepts only an explicit,
unexpired owned loopback fixture: project prefix, source digest, activation token,
container label/running state and loopback port must match before requests. It
rejects proxies, redirects, arbitrary external targets, unexpected content and
stale source. Every probe is bounded and read-only. Do not repurpose it as an
unrestricted URL fetcher. The source provider adds post-start smoke evidence only after explicit per-project
opt-in with `gptclawctl smoke --project-root ROOT --enable-after-start`; use
`--disable-after-start` to disable it. It does not change lifecycle health. No
existing project or test fixture silently enables HTTP probing. `gptclawctl smoke --project-root ROOT` checks an
already owned service and the existing private ingress; adding
`--watch-seconds 28800` opts into a bounded, read-only source observer that checks
changed source revisions. It never starts, restarts or mutates a service. Source
and activation must remain stable during checks. Independent private client
acceptance remains separate from host-side evidence; no production or
managed app is started, restarted or changed by quality verification.

Manual keyboard/focus and assistive-technology checks remain necessary for the
selected product, including errors, focus recovery, contrast, 200% zoom, narrow
layout, reduced motion and enlarged native text. The initial native matrix is
Android-first; iOS results must be recorded only when actually executed.

## API contracts and migrations

API builds export deterministic OpenAPI to `.gptclaw-cache/openapi.json`; the
checked-in `contract/openapi.json` must match, excluding the deployment-specific top-level server declaration. The smoke gate
separately asserts the exact owned prefix/origin for documentation and assets. Existing generated native-client drift
and old-client assertions remain active. Local reference checks refuse remote
schema fetches. To review a change against a previous accepted contract:

```bash
python3 checks/gptclaw_quality.py contract --input NEW.json --baseline PREVIOUS.json
```

The diff is deliberately conservative: changed operation/schema semantics require
consumer review; descriptions and new independent paths can change without a
breaking finding. It supplements stack validation and real client/server tests,
not a claim that structural analysis proves runtime compatibility.

Database releases include fingerprinted `checks/migration-review.json`. Any source
change invalidates the assessment; destructive SQL/opaque Python operations cannot
be declared additive. Static findings are advisory. The disposable database adapter tests fresh setup, a real additive Alembic upgrade
with preserved rows/old columns, an injected failed migration, runtime DDL denial,
and promotion of a separately restore-verified pre-change backup. Previous-client
checks remain in the existing contract fixtures. Managed
migration plan/apply still requires the actual target-bound, restore-verified
backup, roles and locks from SPEC-026. A CI result never substitutes for that
backup, and reverting application/provider code does not undo a schema change.
No automatic downgrade, reset or retained-data deletion is introduced.

## Performance measurements

Single-service browser probes record first observed readiness, 3 × 200 sequential
warm requests with median p95, and available container peak-memory evidence.
The fast verification warmup is 250 ms. The dedicated `benchmark` action uses
five independently started fixtures with 30-second warmups and median startup,
response and peak-memory results. It never restarts a managed service.
API load fixtures explicitly inject the existing Settings factory with a
1000-request allowance for the bounded 600-request sample; the application
default and its admission tests are unchanged. Long warmup requests are throttled.
Measurements identify the exact profile and workload rather than pretending
shared CI hardware is stable. Build collection measures compressed JS assets;
mobile assets remain source bundles, not installed native binaries.

```bash
python3 checks/gptclaw_quality.py measure --output SAMPLE.json
python3 checks/gptclaw_quality.py benchmark --output CALIBRATION.json --engine podman
python3 checks/gptclaw_quality.py performance --input SAMPLE.json --baseline BASELINE.json
```

`quality.json` budgets map each metric to `unit` (`bytes`, `ms`, `MiB`), a numeric
`absolute` cap and allowed fractional `regression`. Comparison requires complete,
finite positive baselines and matching runner/toolchain/workload/cache profiles.
A metric fails if either limit is exceeded. Missing or incomparable samples fail
comparison. New releases enforce explicit absolute ceilings in standard verify. Relative
limits are 10% for bundles and 20% for response/startup/memory against an explicitly
selected matching measured baseline. Initial ceilings are conservative development
limits, not claims of a product performance SLO; runner-specific calibration and
relative acceptance are recorded separately. Never load-test a retained or unrelated application for calibration.

## Release-note drafts

Release notes are opt-in and need no production pipeline. Use explicit full commit
SHAs for the previous accepted baseline and target, product/version/audience and
reviewed change records. Each record has a commit in range, status, category,
summary and a repository Markdown evidence path whose target-revision content
contains `Status: accepted`. A curated acceptance ledger can reference richer
existing evidence; the marker alone is not owner acceptance of generated prose.

```bash
python3 checks/gptclaw_quality.py release-notes --input CHANGES.json --output NOTES.md
```

Only accepted records appear. Pending records produce an incomplete result.
Existing/manual output is never overwritten; identical regeneration is harmless.
Unsafe text/private origins/credential patterns are rejected. Review the draft
against acceptance evidence before copying it into a changelog or product release.
The command never tags, merges, promotes, pushes or publishes a release. Correct
published notes by reviewed amendment, retaining the original release identity.

## Golden matrix and authoring

From the prepared GptClaw manifest environment:

```bash
python scripts/quality_templates.py --list
python scripts/quality_templates.py
python scripts/quality_templates.py --template nextjs --version 1.1.0 --execute --engine podman
```

All exact releases receive integrity and generation checks. The new `1.1.0`
quality releases receive full container checks. Superseded releases retain
historical generation coverage; this is an explicit testing matrix decision, not
silent deletion or an automatic application migration. Newest unclassified
releases fail matrix enumeration. The pinned workflow runs metadata checks and
the full quality matrix on relevant changes, weekly and on manual dispatch.
Physical-device and actual private-ingress trials remain distinct.

Fixture roots, containers and networks are uniquely named and owned. Cleanup
checks labels before removal; cancellation/failure must preserve unrelated data.
Never prune the shared container store. Images are reusable check caches.

For an explicitly unpublished successor release only:

```bash
python scripts/seal-quality-releases.py --version 1.1.0 --baseline origin/main
git add config/templates templates/apps/releases scripts
python scripts/check-template-releases.py --baseline origin/main
```

The sealer refuses releases already in the baseline, prunes development caches
and generated binding/type/state files from its inventory, and hashes source
assets only. The release checker also requires the exact declared bytes in the
Git index, so ignored local files or partially staged changes cannot hide a
missing asset in CI. The canonical portable
runner lives in `scripts/project_quality_core.py` and browser source in
`templates/quality/v1/browser.cjs`; the sealer copies it into
the selected unpublished release. After merge, further changes require a new
release version. Rollback is a reviewed Git change to tooling/adopting source;
no runtime rollout or data rollback is implied.
