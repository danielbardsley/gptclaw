# SPEC-020 acceptance evidence

- **Status:** Implemented on feature branch; local/live and configured CI passed; review/owner acceptance/merge pending
- **Owner:** Daniel
- **Date:** 2026-10-10 (America/New_York)
- **Specification:** [SPEC-020](spec.md) · [Design](technical-design.md) · [Tasks](tasks.md)
- **Operation:** [Toolchain runbook](../../runbooks/manage-project-toolchains.md)
- **Baseline:** main `020be5ec57432e7e49c6283dfbc3cd2e4c0999c9`; SYS-003 merged in PR #46 and accepted
- **Provider:** 1.2.0, toolchain receipt schema 1; dependency/lifecycle receipt schemas remain 1

Daniel authorized implementation with “Ok, let's implement SYS-002”. The initial
Node/pnpm web slice is implemented; no host packages, AWS changes, credential
access, public exposure or additional real language/version pair was introduced.

## Criteria

| Criterion | State | Evidence / remaining action |
|---|---|---|
| AC-001 | passed locally | Strict bounded sidecar/registry validation, duplicate/unknown/bool/range/conflict/path/config refusal before acquisition; manifest v1 unchanged. Compatible engine constraints validated offline and under selected runtime. |
| AC-002 | passed locally/live | Registry pins Node OCI digest and pnpm tarball SHA-512/helper hash. Trusted installer verifies bytes before offline no-hook installation. Actual Node 24.21.0/pnpm 12.10.1 matched on Linux amd64. Unsupported platforms and sources refused. |
| AC-003 | passed locally/live | Task-owned first image acquisition and matching reuse succeeded with actual executable/artifact checks; serialization, missing image/pin, failed acquisition, bad integrity, version/label/cache/provenance conflict and unknown outcome covered by isolated fixtures. Live negative artifact evidence recorded below. |
| AC-004 | passed locally/live | Synthetic new app used the same selected image for frozen dependencies, build/test and private service. Page/health 200; running prepare refused busy. Distinct reviewed fixture profiles exercise different selection/tag/fingerprint paths offline; no second real pair claimed. Existing demo source/state/image/health/routes unchanged. |
| AC-005 | passed locally/live | New app has exact sidecar; synthetic no-declaration legacy app test/start passed without generated metadata. Explicit re-adoption preserved dependency files. Inspect performs only parsing/receipt/image metadata reads; malformed selection never falls back. |
| AC-006 | pending | Focused/local and live evidence recorded. All three configured CI workflows passed; review, Daniel's final acceptance and implementation merge remain delivery gates. Only the initial web slice can be marked Delivered after those gates. |

## Artifacts and observed execution

Registry source was checked against [public pnpm 12.10.1 metadata](https://registry.npmjs.org/pnpm/12.10.1).
No floating version lookup is used during operation. The initial artifact is:

- Node OCI base `docker.io/library/node@sha256:51b1100cc2a83d370c6a60952e3f2989c8a43159d0e38586e090f3b3326efefd`.
- pnpm tarball `https://registry.npmjs.org/pnpm/-/pnpm-12.10.1.tgz`, integrity `sha512-ukCjfrGjcNYP6oxM8dNkwTvMzvUY6YrSvO6VT1OdONo3RY5YJho/pV4GUjRQ6g//+fSXsTW+QfLBXBZCusrObA==`.
- Profile hash `493825c108c8042cf862389663ca7286402e1dcdfdb9592253f3e9b0e40edfe8`.
- Recipe hash `e5cd7670b43c0115a1193ac5f6ac19b5c2f39db03502123fcd8a4797652f1c3b`.
- Acquired image `sha256:58e9f6934cccbcf43a89c12d89f2a1e716ee9a8691e2f12deca7891947a55d50`.
- Cold successful operation `60dddb224b30411880ecc1685cdd7028`, 12.475 seconds CLI wall time; 12.072 seconds acquisition receipt time. Profile image/tag did not exist before acquisition; the reviewed base image was already locally cached. This proves uncached selected-image construction and real tarball fetch, not a cold EC2/base-image download.

Task-owned `/srv/forge/projects/sys002-acceptance` was generated through the source
CLI. Actual managed operations produced these wall timings:

| Operation | Outcome | Seconds |
|---|---|---:|
| toolchain prepare (reuse) | verified, changed false, actual versions rechecked | 1.024 |
| deps install | complete, identical package/lock/workspace hashes | 10.080 |
| test | tests-passed | 5.792 |
| start (including build/readiness) | ready, private route configured | 31.996 |
| private page / health | 200 / 200 | 5.431 / 0.083 |
| prepare while running | busy; no acquisition/switch | — |
| stop | stopped, source retained | 10.643 |
| legacy inspect | legacy true, verified; no sidecar created | 0.124 |
| legacy test / start | tests-passed / ready with same pair | 2.039 / 4.829 |
| legacy stop | stopped, source retained | 10.627 |
| explicit re-adoption inspect | legacy false, verified | 0.125 |

Hello World and Hello Second retained exact hashes of package/lock/workspace,
manifest and template marker, and byte-identical app state including selected
image. Both page/health pairs returned 200 after the synthetic app's operations.
The shared owned ingress was reconciled to a provider snapshot; no existing app
container was restarted or source rewritten. This is observed availability and
identity preservation, not continuous monitoring or hostile-project isolation.

## Development failures and verification

An interrupted SYS-003 publication regression initially failed because a captured
package manifest was temporarily absent. Recovery now validates the journal's
hash-verified saved manifest when resolving the same operation, then preserves
publication/source guards. The 27 dependency tests passed after the fix.

The first acquisition returned a known failed command before any image was built:
Podman 4.9 lacks the newer build `--pids-limit` flag. The reviewed build now uses
supported `--ulimit=nproc=256:256`, with existing CPU/memory limits. Explicit retry
from that absent-image known failure succeeded. Its owned inert job data is
retained for diagnosis; no unknown resources were deleted or permissions changed.

- Existing lifecycle/proxy tests: 32 passed.
- Dependency tests: 27 passed after recovery integration.
- New toolchain tests: 25 passed initially, including strict input, two-profile, cache, locks, bounds, version, recovery and source-preservation fixtures. Four additional integration/reuse/race/service-image cases were added for the final suite.
- Configured CI adds actual Docker profile acquisition/reuse, selected-image
  frozen install/build/test/typecheck and legacy adoption; Passing CI references are recorded below.
- No local Terraform checks/apply: no Terraform source changed.

## Remaining delivery

Implementation verification and source/CI references are recorded below. Review
and owner acceptance/merge remain before marking the initial SYS-002 slice
Delivered. Python/uv/Expo remain separate stage-12 stack obligations. The synthetic
service is stopped; owned source/receipts are retained for review.

## Final local and negative-artifact verification

The full `./scripts/check-repository.sh` passed in the prepared isolated manifest
environment after integration. Bash syntax, Python syntax and Git whitespace
checks passed. The initial focused total was 84 tests (32 lifecycle, 27 dependency,
25 toolchain); the final extended suite is recorded with the PR results below.

Separate task-owned acquisition stores exercised two intentionally invalid
fixture profiles without changing the production registry or app selections:

- Correct public tarball with wrong SHA-512: failed before installation with
  `Artifact integrity mismatch`, no resulting selected image; 1.274 seconds.
- Missing exact public tarball: failed with `Artifact unavailable`, no resulting
  selected image; 1.233 seconds.

Both receipts explicitly recorded failed, not verified. Inert owned diagnostic
job files were retained; no existing image was deleted or global cache pruned.
The synthetic app is stopped with source and receipts retained for review.

The final stable provider was refreshed through a ready Hello World no-op start
(changed false, 1.301 seconds); its version/capabilities report 1.2.0 with toolchain
receipt schema 1. No app container was restarted. Final source verification and
CI references will accompany the implementation PR.

Final full repository checker passed again after the service-image safeguard,
including all **88 focused tests** (32 lifecycle, 27 dependency, 29 toolchain).
All 208 reviewed relative link targets exist. Final installed-provider app status
checks are recorded with the PR handover.

Final inspection review now observes image presence even without a receipt and
refuses an unreceipted image as conflict; produced but failed-verification images
report recovery-required. Future-default/legacy and unreceipted-inspection tests
extend the focused total to 90 (32 lifecycle, 27 dependency, 31 toolchain). Stable
engine ranges also reject leading-zero/unsafe numeric bounds offline.

The first PR app CI run passed offline suites, baseline app build and generated
dependency operations, but failed the new Docker acquisition adapter before
image construction. The adapter added an owned empty Docker CLI configuration and bounded sanitized
build errors. The second run identified the actual fault: Docker defaults to
Dockerfile, while the generated Podman recipe is Containerfile. The CI adapter now
passes the explicit filename. These are CI-only changes; Podman acquisition
already passed live. Neither failed run was counted as passing; the corrected
CI result is recorded below.

The final full offline repository checker passed with all 90 focused tests after
the inspection/range refinements. The synthetic service remains stopped; final
installed inspect reports the matching verified profile/image. The ready Hello
World no-op refresh took 1.338 seconds, changed false.

## Implementation CI and final handover

[PR #48](https://github.com/danielbardsley/gptclaw/pull/48) carries the implementation.
At source `db0cbcc75378a6120016acadaf2d0468ad226f02`, all configured workflows passed:

- [Private application workflow #19](https://github.com/danielbardsley/gptclaw/actions/runs/38080297365): all 90 focused tests; baseline app and dependency workflow; actual integrity-verified image acquisition/reuse, exact runtime checks, selected-image frozen install/build/test/typecheck and legacy adoption.
- [Development-host quality #138](https://github.com/danielbardsley/gptclaw/actions/runs/38080297388): repository and Terraform quality checks; no apply.
- [Federation quality #42](https://github.com/danielbardsley/gptclaw/actions/runs/38080297379): quality checks; no apply.

Final installed provider 1.2.0 reports the new toolchain capability/schema; source
snapshot refresh was a ready no-op and did not restart the app container. Installed
status reports both original demos ready with configured private routes and no
busy operation/error. Synthetic selection inspect reports its matching verified
image; its service is stopped and authored source/receipts retained. Failed owned
acquisition fixtures retain bounded inert diagnosis data; no shared objects were
pruned. No live operator action remains for implementation verification.

Review, Daniel's final acceptance and merge remain AC-006/T-005. SYS-002 stays
In review for this initial web scope; Python/uv/Expo obligations remain later.
