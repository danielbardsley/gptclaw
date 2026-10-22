# SPEC-049 acceptance tracking

Status: In progress; first install-stage failure corrected, second free Android development job queued.
Owner: Project owner. Evidence date: October 22, 2026 (America/New_York).
[Specification](spec.md) · [Design](technical-design.md) · [Tasks](tasks.md) ·
[Detailed execution/tooling review](build-tool-review.md)

## Criterion mapping

| Criterion | State | Evidence and remaining action |
|---|---|---|
| AC-001 | Passed locally | Separate development/preview identities and deterministic config; production, foreign/malformed API binding, invalid version/project inputs refused. Both actual 31-file snapshots/archives match reviewed hashes. Historical source/provider behavior is unchanged; no installed provider or immutable starter edit. |
| AC-002 | Pending | Owner approved bardsley/Fieldnotes, free-only builds, Expo-managed keys and the exact expiring exception. Free 0/15 Android allowance and PRIVATE project access readback passed before submission. Development key generated remotely; no local export. Actual artifact access and final binary inspection are pending. |
| AC-003 | Pending | Development job submitted; native compilation and phone installation/Metro/API/native-module checks unobserved. |
| AC-004 | Pending | Preview snapshot prepared/inspected; cloud submission waits for the active development job. No preview binary or physical acceptance yet. |
| AC-005 | Pending | Four local quota/expiry/interruption/duplicate/terminal-state tests passed. Persisted real submission intent reconciles to the same existing remote job. Corrective-binary install/data preservation and a physical recovery drill remain pending. |
| AC-006 | Pending | Source checks and CI passed; no repeated native build/install or owner acceptance is claimed. |

## Executed evidence

Mobile runtime source is `e06625deb1a0624469cbd71db7d93c740f0f3b02` in
[Fieldnotes PR #2](https://github.com/danielbardsley/fieldnotes-mobile/pull/2).
The passed source CI at that revision is
[run 39676688410](https://github.com/danielbardsley/fieldnotes-mobile/actions/runs/39676688410).
Later support-only commit `83f9a49102e8e4d87090e6ac43b6a1fe815942e1` adds the
receipt/recovery tests and documentation; its full source CI passed in
[run 39833697585](https://github.com/danielbardsley/fieldnotes-mobile/actions/runs/39833697585).
Neither PR merge nor installed acceptance is inferred from these runs.

Executed rootless checks: frozen scripts-disabled dependency installation;
`pnpm format`, `pnpm lint`, `pnpm typecheck`, `pnpm test`, `pnpm security`,
`pnpm build`. Nine native Jest tests and seven Node config/contract/security tests
passed, and both iOS/Android JavaScript/assets exported. Source security uses the
unchanged source/export exceptions; the separately approved native-tool exception
has not replaced that policy. Later `pnpm lint` and four new job-recovery tests
passed. Pinned user-scoped Node plus host Git ran eight config/upload isolation
tests successfully. Git-dependent tests are local; hosted CI runs the source and
pure receipt/configuration checks. No host package installation occurred.

Actual `build:inspect --stage archive` checks passed for both profiles after
account/privacy checks. EAS creates a shallow Git directory in addition to the
31 source files; inspection verified one isolated commit, the exact reviewed
tree, local file:// origin, sample-only hooks and no symlinks. The product's
Git history and local state/credentials/database files were excluded. No private
API hostname is committed to this evidence. Retain its public-config digest.

[Development job d89b3748](https://expo.dev/accounts/bardsley/projects/fieldnotes-mobile/builds/d89b3748-fce7-4406-b51e-b9496e367d51)
is IN_QUEUE, submitted at 2026-10-22T18:35:22Z. Its source snapshot is
`8ecf61d5004ff14c2e5086e4bc4434862840335f`; the remote fingerprint is
`d0b846d1c23131a27224a4456cdb6b0a7ea5a16a`. Server metadata currently records
expiration at 2026-11-05T18:35:22Z (November 5, 1:35 p.m. Eastern).
Expiration metadata is not a successful artifact result. Preview snapshot is
`c484cda7d0134c0da9aacee0f060fa5e1c88f185` and remains unsubmitted.

The retained [tool lock](tooling/README.md) pins the actual patched compiler client
inputs. The first offline install refused missing policy metadata; the subsequent
frozen network-enabled metadata fetch passed, reusing all cached package tarballs.
Initial monitor-query and archive-origin-format mismatches were corrected through
read-only diagnosis; no extra cloud job was submitted to resolve them.

## Runtime, adaptation and remaining work

This retains the deliberately selected synthetic Fieldnotes notebook/API demo;
SPEC-049 changes installation/build operation, not its product routes or models.
No production adaptation or user-data migration is selected. Provider 1.17.0
read-only status confirms Fieldnotes API/database stopped, consistent with the
prior accepted closeout. Metro, API, DB, private routes, existing projects and
retained records were not mutated for build preparation.

Wait for the existing remote development job; diagnose its actual result before
any retry. Submit preview only after that job becomes terminal and a fresh Free
quota/privacy/no-active-job check passes. Installation, private networking, restart
persistence, accessibility, compatible corrective install and owner acceptance
need actual phone observations. Keep source PR/review/merge, cloud build and these
native gates separate. The catalogue is not Delivered from this tracking record.


## Corrected development attempt

The original d89b3748 job is ERRORED: strict pnpm install-hook admission failed
after dependency resolution. It is retained as a failed invocation, not relabeled
as passing. The exact standard install was reproduced successfully after adding
explicit false decisions for two hooks and preserving the existing workspace
package-age policy in uploads. Fourteen focused tests/lint and disposable Android
native-project generation passed. See the detailed review for the source revision,
normal install and retained original receipts. No new dependency scripts were enabled.

The current source is `2cb3e0a8ea36d864799f0e1e0802ae5c4257d861`; corrected snapshot
`a1a11e8a1e398228ac16ed0e4b4b865dc7e089f2` is submitted as
[development c789df30](https://expo.dev/accounts/bardsley/projects/fieldnotes-mobile/builds/c789df30-82ca-4849-ad8d-e1a2f1b4ebe5),
currently IN_QUEUE. Fresh preflight still reported 15 free Android builds available.
The corrected preview snapshot `c6aa8fbc22820dd9bb56e199af8bc344f5191ed6` is prepared
and inspected, with no cloud preview job yet. AC-002–006 remain pending; a successful
local install/prebuild is not a signed binary or physical-device test.
