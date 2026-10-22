# SPEC-049 acceptance tracking

Status: In progress; development APK built and inspected; free standalone preview queued.
Owner: Project owner. Evidence date: October 22, 2026 (America/New_York).
[Specification](spec.md) · [Design](technical-design.md) · [Tasks](tasks.md) ·
[Detailed execution/tooling review](build-tool-review.md)

## Criterion mapping

| Criterion | State | Evidence and remaining action |
|---|---|---|
| AC-001 | Passed locally | Separate development/preview identities and deterministic config; production, foreign/malformed API binding, invalid version/project inputs refused. Both corrected 34-file snapshots/archives match reviewed hashes. Historical source/provider behavior is unchanged; no installed provider or immutable starter edit. |
| AC-002 | Pending | Owner approved bardsley/Fieldnotes, free-only builds, Expo-managed keys and the exact expiring exception. Free 0/15 Android allowance and PRIVATE project access readback passed before submission. Development key generated remotely; no local export. Development APK authenticated retrieval/identity/signing-block checks passed; anonymous artifact lookup denied. Preview inspection and physical acceptance remain pending. |
| AC-003 | Pending | Development native cloud compilation passed and APK retrieved. Phone installation/Metro/API/native-module checks remain unobserved. |
| AC-004 | Pending | Standalone preview submitted after development finished and fresh Free/private/no-active-job checks passed; currently queued. No preview binary or physical acceptance yet. |
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

The first development job `d89b3748-fce7-4406-b51e-b9496e367d51` failed during
strict dependency installation; the correction and successful replacement are
recorded below. Its failed result remains preserved.

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

Observe the existing preview job without duplicate submission. Installation,
private networking, restart persistence, accessibility, compatible corrective
install and owner acceptance need actual phone observations. Keep source
PR/review/merge, cloud build and these native gates separate. The catalogue is
not Delivered from this tracking record.

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
FINISHED at 2026-10-22T19:37:51Z. Its corrected-source CI passed in
[run 39836656002](https://github.com/danielbardsley/fieldnotes-mobile/actions/runs/39836656002).
Authenticated official EAS download succeeded; anonymous artifact lookup was denied.
The 258,576,155-byte APK has the expected development package, manifest, DEX and
APK signing block. SHA-256:
`35f526315f3f67d2cad91fc736fd7af82d6beb8b501c3633e8e8cd218166c5bf`.
Signing-block presence is not cryptographic verification or physical installation.
The development APK has no bundled app JavaScript, as expected for a Metro client;
no eligible JavaScript/JSON payload was available for the bounded pattern scan.

The corrected preview snapshot `c6aa8fbc22820dd9bb56e199af8bc344f5191ed6` was submitted
as [preview d580a4b0](https://expo.dev/accounts/bardsley/projects/fieldnotes-mobile/builds/d580a4b0-09df-4cd1-bc67-43d8f8b30c71)
at 2026-10-22T19:39:50Z and is IN_QUEUE. Fresh preflight reported 14 free Android
builds remaining; remote preview signing-key generation succeeded. It is the only
active job. No paid upgrade or usage was requested. AC-002–006 remain pending;
cloud compilation does not establish phone behavior.


## Authorized backend start — October 22

While preview compilation continued, the project owner explicitly requested API
startup. Installed provider 1.17.0 observed the canonical Fieldnotes API/database
stopped with no busy operation and the existing private route configured. One
parent-project start completed in 34.687 seconds, operation
`cf54c29c876d4721b11307a9751abdcd`, result passed. Both API and database reported
ready; an independent post-start status confirmed ready/healthy and no busy job.
The existing private route remains configured. No migration, seed, reset, Metro
startup or new exposure was requested. Runtime source/data and unrelated projects
are preserved. This supersedes the earlier stopped observation; physical phone
access and native CRUD acceptance remain unobserved.
