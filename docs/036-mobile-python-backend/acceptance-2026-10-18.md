# SPEC-036 acceptance continuation — October 18, 2026

Owner: Project owner. Historical status as of October 18: physical Android acceptance pending.
[Specification](spec.md) · [Design](technical-design.md) · [Tasks](tasks.md) ·
[Historical evidence](acceptance.md)

Superseding disposition: [October 21 owner acceptance and closeout](closeout-2026-10-21.md).
The table and remaining-work section below preserve the October 18 checkpoint;
unrun checks closed by the later owner waiver are not reclassified as passes.

## Current criterion mapping

| Criterion | State | Evidence and remaining action |
|---|---|---|
| AC-001 | Passed | Current installed binding/parity and all 12 isolated admission/compatibility regressions pass. |
| AC-002 | Passed | Offline generation/ownership/readiness/routing regressions, two real API/DB-only verifier fixtures and live stop/start/component restart/isolation observations pass; no frontend container or DB host port. |
| AC-003 | Pending | Native/Python quality, generated contract fault checks and private host HTTPS API/docs pass; phone HTTPS docs observation remains. |
| AC-004 | Pending | Owner-reported native CRUD, relaunch and deletion confirmation pass; host pagination/validation pass; live restart/reload and native pagination/empty-state observations remain. |
| AC-005 | Pending | Owner-reported offline/uncertain-save/draft/explicit-recovery/no-duplicate checks pass; live API/DB outage and Metro restart/isolation checks remain. |
| AC-006 | Pending | Static contrast/target checks, native component tests and owner-reported physical accessibility pass; screenshots and final owner visual review remain. |
| AC-007 | Passed with limitation | Final full real-DB migration/v1-client/backup/recovery rerun and selected compatible-provider rollback/roll-forward pass; bounded bundle/log scans pass. Initial transient restore failure remains unexplained and is retained below. |
| AC-008 | Pending | Implementation merge and final-head/generated CI independently rechecked; current source/installed parity and rollout observed; remaining criteria, disposition and owner M1 acceptance remain. |

## Tested identities and boundaries

The project owner requested completion of SPEC-036 acceptance and confirmed
Android 11 / Expo Go 57.0.9 with Tailscale connected in this chat. This is
caller-reported device configuration. Specific physical scenario reports are
attributed below; the criterion mapping identifies the remaining observations.

- Platform source: `fc2c737f1862d34a258238e6d6b5d3feeda402b0` in an isolated
  `codex/spec-036-acceptance-20261018` worktree. The original
  `codex/dashboard-dark-mode` checkout was clean and is preserved.
- Backend: canonical `fieldnotes-api`, source
  `0e28453355cdf8e7434f74f90b43020321e6a93c`; mobile: canonical
  `fieldnotes-mobile`, source `b0b0d4079c5e6d9c2efe928c27a9a5107e0b0f8a`.
  Both tracked working trees were clean before checks.
- Installed provider: 1.15.0, immutable snapshot
  `234f928b41d91a3bff55cb9c0af13111936f6a2ffd6c5b6308e8c41d3598b3a8`.
  Nine selected mobile/backend/lifecycle/schema source files match installed
  bytes. This is a scoped parity check, not a claim that every bundled file was
  compared. Current capabilities include manifests 8/9, group receipt 4,
  catalogue 7 and backend binding/Metro/Go contracts.
- Read-only installed binding inspection resolves `fieldnotes-mobile` to
  `fieldnotes-api`, development profile, API contract 1.
- The existing API/database were Ready. The previous bounded Metro session was
  expired. One installed `start --metro-transport tailnet-http` created generation
  `3d415949724543acaac4e50a6d3baa5a`. Start initially returned route-pending;
  subsequent status proved process Up, protocol Ready and existing private route
  Verified. Go inspection/launch then returned compatible/available for the
  reported device matrix. A QR was generated locally with the existing encoder;
  private launch destinations are excluded from this local acceptance record.
- No source changes, runtime installation, account changes, public exposure,
  privileged listener changes or production operations were performed.

## Executed checks

### Binding, generation and lifecycle regressions

From the isolated platform worktree:

```sh
/srv/forge/projects/gptclaw/.venv-manifest/bin/python -B scripts/tests/test_mobile_backend.py
```

All 12 tests passed in 110.114 seconds. Coverage includes API/DB-only and native
offline generation/provenance, URL/profile/identity/config rejection, fresh-clone
public config generation, historical-validator refusal, receipt component/version
refusal, DB/API readiness ordering, absence of frontend fallback and scoped stop
with source/data retention. These are isolated automated results, not physical
device observations.

### Installed private HTTPS API

A task-owned Python urllib probe read the existing local public API binding;
neither hostname nor existing record contents were printed or committed. It
checked private health, readiness, bundled docs and OpenAPI; malformed/blank/
overlength/extra-field payloads (422), invalid pagination (422) and an absent
random record (404). Two new uniquely identified synthetic host records were
created (201), one updated (200), single-record pagination and an empty page
checked. Creation Location headers retain the API prefix. The records are retained
temporarily for persistence checks; only their recorded IDs may be cleaned up.

The first probe used incorrect `/healthz`/`readyz` names and stopped at 404 before
creating any record. Source inspection established `/health`/`ready`; the corrected
probe passed. This was a probe correction, not an application repair.

### Static native accessibility evidence

The actual native colour tokens were evaluated using sRGB relative luminance.
Nine normal text/background pairs passed 4.5:1; the lowest measured pair was
muted text on the featured card, 5.06:1. Other examples: muted on paper 5.69:1,
ink on paper 12.93:1, white on cobalt 8.33:1 and error text on notice 6.77:1.
Source declares 48 dp minimum action height, 60 dp title input and 280 dp body
input. UI motion is absent by design. These checks do not establish physical
layout, font scaling, keyboard, TalkBack focus or touch behavior.

### Native quality and exported assets

`pnpm verify` passed in the existing exact
`localhost/gptclaw-node:24.21.0-pnpm12.10.1` rootless container, with a task-owned
`git archive HEAD` copy of the canonical mobile source and its frozen existing
`node_modules` mounted read-only. No live source or Metro inputs were changed.
The job ran with one CPU, 1536 MiB memory and 256 PIDs, dropped capabilities and
no-new-privileges. It passed format-check, lint, typed/generated contract checks,
9 Jest interaction tests, 3 generator/security tests, SDK selection, security and
both platform exports. Combined statement/branch coverage was 93.42%/82.18%.

Security reported 3 moderate and 2 high findings with the existing exact approved
source/export exceptions `GHSA-86w9-cpqp-85rv` and `GHSA-vfj7-8cjw-p6xm`, both
expiring October 28 at 00:00 Eastern. No policy exception was added or extended.
Android and iOS export passed; these are JavaScript/assets, not signed binaries or
physical iOS acceptance. A separate scan of all 54 exported files found no
credential-shaped access keys/private keys/tokens or PostgreSQL credential URLs.
The job received no server credential mount. This bounded scan is not a claim
that every possible secret format can be recognized.

### Implementation and generated CI readback

Connected GitHub readback on October 18 independently confirms implementation
PR #83 merged at `bdd2d7e55d3077e6a651cae15ceed35604d5556c`. All four workflows
on its final head `d206ef2ddb8a8ca17cd1fb62f769b32df30f56d1` are completed/success:
[private apps](https://github.com/danielbardsley/gptclaw/actions/runs/38766903284),
[host](https://github.com/danielbardsley/gptclaw/actions/runs/38766902983),
[Tailscale federation](https://github.com/danielbardsley/gptclaw/actions/runs/38766903077)
and [dashboard](https://github.com/danielbardsley/gptclaw/actions/runs/38766903327).
The canonical generated source commits also retain successful
[backend CI](https://github.com/danielbardsley/fieldnotes-api/actions/runs/38747345148)
and [native CI](https://github.com/danielbardsley/fieldnotes-mobile/actions/runs/38747570563).
These are historical implementation/source CI results rechecked now, not new
workflow executions or physical-device acceptance.

### Disposable PostgreSQL recovery run

The source verifier was invoked with the canonical backend as `--source-root`,
`--engine podman`, the existing API image
`sha256:5c38ecb767951d1d65f7934ba31ce026d0d62bdddd8f2eb3faa68373fbc692ba`
and the existing exact Node image. It created only owned temporary source/data,
roles and isolated containers/network. It passed API lint/typecheck/test/security/
build, container-recreation persistence, runtime DDL denial, verified backup and
isolated restore with identical record digests, and credential absence from
container metadata/backup receipts.

The invocation then exited 1 during staged restore promotion, with a suppressed
`database-command` error from pg_restore. It did not reach rotation or additive
migration/retained-v1-client checks. A fresh isolated restore of the same selected
backup subsequently passed. Its diagnostic wrapper emitted only fixed failure
categories and never printed credential or SQL output. The original invocation
remains failed; no finer cause is established and a full fresh rerun is underway.
All affected data belongs to the disposable fixture; the live Fieldnotes database
was not reset, restored or migrated.

The complete fresh rerun exited 0 with PostgreSQL 18.6, manifest 8 and security
passed. Its sanitized receipt records generation/migration/quality/persistence,
role denial, backup/restore, secret-metadata checks, reset/restore promotion,
rotation/old-login denial, generation pruning, failed-reset preservation,
corrupt-backup refusal and forward migration. The retained compiled native v1
adapter passed real HTTP CRUD both before and after the additive migration.
Owned runtime resources were stopped/removed by the verifier; temporary source,
data and recovery points remain retained. No code change was made to obtain the
pass, and the earlier failure's cause remains unresolved.

Exact successful invocation from the isolated platform worktree:

```sh
/srv/forge/projects/gptclaw/.venv-manifest/bin/python -B scripts/tests/check_database_template.py /tmp/spec036-db-acceptance-rerun-20261018 --engine podman --source-root /srv/forge/projects/fieldnotes-api --api-image sha256:5c38ecb767951d1d65f7934ba31ce026d0d62bdddd8f2eb3faa68373fbc692ba --node-image localhost/gptclaw-node:24.21.0-pnpm12.10.1
```

### Current phone launch result

The owner reported that the app did not open, with Expo Go showing
“Failed to download remote update.” Treat this as a failed launch attempt.
Subsequent installed status still reports Metro process Up/protocol Ready/private
route Verified. Bounded host probes returned 200 for private proxy health,
aggregate transport counters, SDK status and the exact current Android manifest.
Aggregate counters showed four stale-launch refusals; this suggests a saved old
entry may have been used but does not prove that it caused the phone error. The
owner was asked to return to Go home and rescan the current QR. Current-generation
bundle delivery and physical launch remain under investigation.

The owner subsequently confirmed “It opens now” after rescanning. This establishes
owner-reported current native launch, superseding launch-pending for the current
attempt. The PNG was independently decoded locally to the exact generation-bound
URI. A host Android bundle probe returned 503; later aggregate counters show a
successful bundle response and a deadline rejection. Preserve the failed probe;
neither stale-entry causation nor cold-compilation causation is established.
Individual native CRUD/relaunch scenarios are still pending.

The owner then reported all create/list/open/edit/save, full app relaunch and
cancel-then-confirm deletion checks passed, retaining the first synthetic note.
The next owner-reported round passed: offline Save retained the draft, displayed
failure/uncertainty, prevented another save until explicit recovery, recovered
after Tailscale returned and finished with exactly one saved copy. Blank-title
validation also passed. These are attributed physical Android results, not host
inference. Screenshots and remaining native/accessibility scenarios are separate.

### Live backend outage and isolation

On follow-up, the project owner answered “Everything still seems to be working”
to the first outage question. Because the backend had subsequently been restored
for the host rollback/restart checks, the timing of that phone observation is
unknown. It does not establish a successful save while the backend was stopped,
nor prove outage-message or draft-recovery behavior. A new coordinated check was
proposed: prepare an unsaved draft, confirm readiness, then stop the backend and
observe Save before restoration. The owner selected “I can test later.” No second
outage or Metro restart was initiated. The observed first host stop/publication
withdrawal below remains valid; physical outage acceptance remains pending.

The owner separately reported all physical accessibility checks passed: keyboard
editing/scrolling, largest Android text size, TalkBack labels/focus order for title,
body and actions, and Android Remove animations, with fields/actions readable,
reachable and usable. Record this as owner-reported Android accessibility evidence.
It does not substitute for the required list/editor/exceptional-state screenshots
or the separate final visual acceptance.

Installed managed `stop --project-root /srv/forge/projects/fieldnotes-api`
completed in 8.626 seconds, operation `0d1fdafdaa414f8baadf3b7a78c8e484`, state
Stopped with source retained. An actual private notes request then returned 404,
confirming useful API publication was withdrawn. Metro stayed Ready with the
same generation and verified private route. DB status retained generation
`dadb615759694425b662f50dc2d7bcde`, revision `0001`, configured credential state
and the completed original init operation. Both canonical tracked trees remain
clean. Phone outage/draft behavior is being observed before restart.

Seven unrelated application/database/dashboard containers retained identical
running instance IDs; both existing peer private API health endpoints returned
200. A bounded scan of selected mobile lifecycle and API logs (40 lines each)
found no credential-shaped values or PostgreSQL URLs; log contents were suppressed.

### Compatible-provider rollback, roll-forward and persistence

The retained installed immutable 1.14.0 snapshot
`87b27973e04c7612f9a9ab37f718e919f7c1268f04463a5b84fa844af3b73059`
advertises schemas 8/9/group receipt 4 and validated the stopped canonical backend.
Its managed `start --project-root /srv/forge/projects/fieldnotes-api --local-only`
passed/Ready in 27.480 seconds, operation `d2a911c328ab4c13b4c3442acf800267`.
Both host markers were read back with exact saved content over private HTTPS;
database generation/revision remained the original `dadb615759694425b662f50dc2d7bcde`
and `0001`. The same capable provider stopped the group successfully, operation
`d8e938e40f184133bb0124a55bad39b8`, then stable 1.15.0 started it Ready in
27.033 seconds, operation `2eaad08323a444c38efcd917125bab8c`.

This rehearsed selecting the retained compatible installed provider for this
target only. Both starts used `--local-only` to avoid reconfiguring shared
ingress; actual existing private HTTPS was verified separately. The shared stable
launcher remained pointed to snapshot `234f928b…3598b3a8` throughout, and no
dashboard/provider installation or global downgrade occurred. No migration,
schema downgrade, reset or restore was run against live Fieldnotes data.

Stable managed component restarts then succeeded:

- DB: `58f5e731f35f4375b65c28de6c89fc37`, 32.456 seconds.
- API: `c2f3e439a4894d63811d22b22ad427f9`, 27.528 seconds.

A timestamp-only touch of the API notes domain source triggered replacement of
the Python worker without changing file bytes. The first reload observation
overlapped the API restart receipt and an immediate record probe returned 503;
it is not counted as an independent persistence pass. After the restart was
terminal, the reload probe was repeated, confirmed a separate worker replacement,
waited for private API readiness, and read both owned markers with exact saved
content. Both canonical tracked working trees remain clean. Metro retained the
same Ready generation/private route through every backend operation.

The post-launch Android bundle probe also passed: HTTP 200, 6,464,006 bytes,
SHA-256 `68aec52e5b6ea06ab6e4f55363c7446c228805e9fd68099076c541cf745fcc10`.
Its earlier 503 and the initially failed owner launch remain recorded; their
finer causes are not established by this successful later result.

## Remaining acceptance

Phone CRUD, relaunch, offline/uncertain-write/draft recovery and blank-title
validation have owner-reported passes. API/DB outage-message/draft recovery,
phone readback after backend restarts/reload, native pagination/empty-state and
private HTTPS docs checks and list/editor/exceptional-state screenshots remain
pending. Physical accessibility has an owner-reported pass. Metro restart with
backend isolation and a fresh phone launch, final owned-runtime cleanup/retention disposition and owner M1
acceptance remain open. The live backend has been restored Ready on 1.15.0 and
the current bounded Metro remains available for remaining phone checks. MOB-010
and Android M1 are not marked Delivered.

At the latest readback, backend API/DB are Ready and Metro remains Ready in
generation `3d415949724543acaac4e50a6d3baa5a`, expiring October 18 at
2:29:58 p.m. America/New_York. The owner deferred further timed phone testing;
no runtime was changed in response. Recheck actual state/expiry before resuming.
Two task-owned host persistence markers remain for the unfinished Metro check;
only their recorded IDs may be removed at closeout. Source/data disposition and
private listener cleanup remain governed by the existing operator path.

The project owner explicitly approved committing/pushing this evidence branch
and opening a draft PR on October 18. This supersedes the earlier publication
block: automatic approval review had rejected the combined commit/push command
before execution because remote publication had not been explicitly authorized.
That rejected invocation made no commit or push. Publication approval does not
close the remaining acceptance criteria or authorize merge. Local whitespace,
relative-link and sanitized-evidence checks pass. No new CI/deployment result is
claimed for these documentation changes.
