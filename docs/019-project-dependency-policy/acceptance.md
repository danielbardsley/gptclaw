# SPEC-019 acceptance evidence

- **Status:** Implemented on feature branch; local/live and implementation CI passed; review/merge and final owner acceptance pending
- **Owner:** Daniel
- **Date:** 2026-10-10 (America/New_York)
- **Specification:** [SPEC-019](spec.md) · [Design](technical-design.md) · [Tasks](tasks.md)
- **Operation:** [Dependency runbook](../../runbooks/manage-project-dependencies.md)
- **Baseline:** main `1bd0f73a82151010eded4502e431dd36e8424fde`, planning `c5fc0c43848d8caa0f09cf183c3cf069cda35d9d`
- **Provider:** 1.1.0, lifecycle receipt schema 1 and dependency receipt schema 1

Daniel authorized implementation with “Ok, let's implement SYS-003.” This covers
SPEC-019's initial public npm/single-root pnpm adapter, not SYS-002. The existing
Node 24.21.0/pnpm 12.10.1 image was reused. No host packages, credentials,
privilege grants, AWS infrastructure or public exposure changed.

## Criteria

| Criterion | State | Evidence / remaining action |
|---|---|---|
| AC-001 | passed locally/live | Strict policy/schema and bounded duplicate/tag/alias/unknown/path/config validation; read-only status leaves files/runtime unchanged and invokes no installer. Actual template two-document lock parsed without executable loading. |
| AC-002 | passed locally/live | Frozen template install/build/test and synthetic app dependency workflow passed with hooks/runtime downloads disabled and read-only frozen metadata mounts. Install-hook sentinel remained absent. Public-source/config/override denial and mount checks passed; actual @jsr override probe used only registry.npmjs.org. |
| AC-003 | passed locally/live | Added is-number 6.0.0 as a development dependency, updated to 7.0.0, removed it, then froze/reinstalled without source changes. Receipts identify manifest/lock diffs/hashes; unrelated synthetic source and existing demos' dependency hashes were retained. No Git reset/stage/commit was performed on apps. |
| AC-004 | passed locally/live | Running-target mutation refused with busy; selected stopped app mutations obey project/job locks and bounds. Both existing private demo page/health pairs remained 200 and dependency source hashes matched. Startup/test use the policy gate/fingerprint and controlled environment. |
| AC-005 | passed locally/live | Offline injected fetch/timeout, interrupted multi-file/capture publication, replacement editor races, unknown jobs and same-ID recovery/abort checks passed. Actual valid-format bad Next.js integrity failed on an uncached owned fixture, source remained unchanged, status required recovery, same-ID abort plus frozen repair/test passed. |
| AC-006 | pending | Focused tests and full offline repository checker passed; runbook, generated guidance, snapshots and generated-app CI added. All three implementation CI workflows passed; owned backup/staging cleanup completed and the synthetic service was stopped with source retained. Review/merge and owner adapter acceptance remain delivery gates. |

## Live workflow and timings

Task-owned `sys003-acceptance` was generated through the source CLI. Its package
manifest included a synthetic postinstall hook that would write `hook-sentinel`;
that file never appeared. A separate synthetic source sentinel stayed unchanged.
Actual operations used the existing rootless image, not host Node/npm:

- `deps install`: complete, no source changes; 11.325 seconds wall time.
- `deps add --package is-number --version 6.0.0 --kind development`: complete;
  only package.json/pnpm-lock.yaml changed; 17.409 seconds wall time.
- `deps update --package is-number --version 7.0.0`: complete; existing development
  group preserved; 17.265 seconds wall time.
- `test`: tests-passed; 4.716 seconds wall time.
- `start`: ready/configured private URL, including container build/readiness;
  30.969 seconds wall time. Private page and health returned 200.
- Mutation while running: refused with busy; source/route not changed.
- `stop`: passed; 0.930 seconds wall time.
- `deps remove --package is-number`: complete; 20.427 seconds wall time.
- `deps install`: complete with identical package/lock/workspace hashes;
  3.842 seconds wall time.
- Subsequent `start`: ready/private page and health 200; 16.884 seconds wall time.

Before/after hashes of package.json, pnpm-lock.yaml and pnpm-workspace.yaml for
Hello World and Hello Second matched. Both private pages/health endpoints stayed
200 at the observed checkpoints. This proves observed isolation and bounded
operations, not continuous monitoring or isolation from a hostile forge process.

For real integrity failure, the selected fixture was stopped; only its owned
module/cache trees were retained in a task-owned backup to force an uncached
check. One Next.js lock integrity was replaced with a valid SHA-512 encoding of
incorrect bytes. Frozen install failed (`command`), kept those source bytes and
reported recovery-required. The test restored its known original lock bytes,
then explicitly aborted that same operation ID and ran a successful frozen
repair/test. Shared caches/images and existing demo sources were untouched.

## Contract and failures found during development

Native pnpm 12 lockfiles have two YAML documents, including package-manager
metadata. The new parser bounds documents/depth/events and rejects aliases,
tags, duplicate/non-string keys, other importers and exotic resolutions; it
accepts only the supported empty config dependency/exact-manager metadata.
Legacy packageManagerStrict/managePackageManagerVersions settings are removed
in pnpm 12; the implemented controls use pmOnFail error, ignore-scripts,
no-runtime, ignore-pnpmfile and controlled job/service environment. The existing
starter built successfully under the no-hook policy.

Frozen metadata files are read-only bind mounts. Change publication retains
original copies/inodes and uses exclusive replacement creation; an editor's
replacement is preserved. Multi-file state is journaled, not claimed atomic.
Per-operation history survives later jobs. Unknown jobs are never killed or
replaced; detected policy/image/source conflicts require explicit reconciliation.
An abort preserves current coherent files rather than silently reverting them.

An initial injected publication failure exposed a missing sanitized internal
error code; it was added and the recovery test passed. CLI package-version
arguments are kept separate from provider --version metadata. Three cases
specifically cover capture-time crash, editor replacement during publication
and scoped read-only metadata mounts. No failed check was treated as a pass.

## Verification and remaining delivery

- Existing lifecycle/proxy suite: 32 tests passed after integration.
- New dependency suite: 27 tests passed, covering policy/config/lock denial,
  frozen source preservation, exact changes, busy/refusal, recovery, history and
  editor races; all use isolated fixtures and mocked container jobs.
- Full `./scripts/check-repository.sh` in the prepared manifest environment:
  passed, including both suites and existing repository invariants.
- Bash syntax, Python compilation and Git whitespace checks passed.
- Pinned-container frozen install, build/test and live add/update/remove,
  bad-integrity/repair/private routing are separate observed EC2 evidence.
- No local Terraform checks ran: no Terraform source changed. No apply dispatched.

Configured CI now additionally exercises generated synthetic add/update/remove,
frozen reuse, hook suppression and build/test/typecheck using Docker on the runner.
Its passing result and exact source/PR references are recorded below. Owner
acceptance and merge remain separate. SYS-003 stays In review,
and SYS-002 remains an unimplemented draft. Broader managers, hook exceptions,
private registries and shared-cache management are not claimed.

## Implementation CI and cleanup — October 10, 2026 (America/New_York)

[PR #46](https://github.com/danielbardsley/gptclaw/pull/46) carries the implementation
and preserves both planning packages from superseded PR #45. SYS-002 is still
Draft; only SYS-003 implementation was authorized. At exact implementation
revision `2424f6580345cd83f2c7c8ed2009522aa0148e9f`, all configured workflows passed:

- [Private application workflow #12](https://github.com/danielbardsley/gptclaw/actions/runs/38074003556), including generated-app frozen reuse, exact add/update/remove, real package execution, hook suppression, typecheck/build/test and receipt history.
- [Development-host quality #133](https://github.com/danielbardsley/gptclaw/actions/runs/38074003633).
- [Federation quality #37](https://github.com/danielbardsley/gptclaw/actions/runs/38074003577).

The final installed provider snapshot was refreshed through a ready no-op start
(1.353 seconds, changed false); five checked provider/policy/schema files match
the implementation bytes. The app container was not restarted; only the shared
owned user ingress was reconciled to the provider snapshot. Both original demo
source hashes remained unchanged and their private page/health pairs returned 200.
The acceptance app remains stopped with its synthetic source/receipts retained
for review. Its verified task-owned integrity backup was removed; no shared
cache/image or user data was deleted. Successful/aborted owned transaction folders
were cleaned and operation history retained. No further live operation is pending.
Final source review/merge and Daniel's adapter acceptance remain AC-006; do not
mark Delivered until those are established.
