# Python template certifi security patch — October 21, 2026

Owner: Project owner. Status: Authorized maintenance; verification in progress.
[Catalogue specification](spec.md) · [Release procedure](../../runbooks/manage-project-templates.md)

## Problem and authorized scope

SPEC-036 closeout CI at `ca095b927a882fccaa76559aa3763f9cfc182012`
reported `PYSEC-2026-4320` against certifi 2026.7.22 in existing Python template
locks, listing 2026.10.19 as the fix. The four locks were byte-identical to main.
The project owner selected “Prepare the template security fix first” before
merging the accepted closeout.

Publish exact `fastapi@1.0.1`, `notes@1.0.1`, `notes-postgres@1.0.1` and
`fastapi-postgres@1.0.1`. Resolve only certifi to 2026.10.19 with the existing
Python 3.13.16/uv 0.13.0 rootless toolchain. Preserve all 1.0.0 release bytes,
descriptors and explicit selection; append the new descriptors with their own
inventories/digests. Keep the existing Next.js default and all toolchain/schema
contracts. Existing projects and installed provider snapshots are not upgraded.

The implementation adds no advisory exception, audit suppression or weakened
check. Old releases remain selectable for reproducibility; they retain the known
finding and do not become audit-clean merely because a new release exists.
Existing generated projects need a separately reviewed dependency update.

## Technical approach and tasks

- [x] Copy only each published descriptor's inventoried assets into a new 1.0.1
  directory; do not copy local runtime/cache material.
- [x] Run exact `uv lock --upgrade-package certifi==2026.10.19` inside the existing
  bounded rootless Python container with managed downloads, configuration and
  credentials disabled. Confirm certifi is the sole changed package record.
- [x] Append new descriptors in catalogue extensions 2/3/4/7 and recompute only
  their file/release digests; leave historical descriptors untouched.
- [x] Select the patched exact releases in the real standalone/group/database/
  mobile-backend quality fixtures; retain unmodified historical release tests.
- [x] Add offline regression coverage for the narrow graph/asset change and
  explicit generation/provenance of both old and patched releases.

Verification/delivery gates: run release immutability, targeted catalogue tests,
repository checks and real frozen install/security validation; obtain passing
final-head CI before merge, then integrate into SPEC-036's accepted closeout.
Record executed local results below and final CI/merge results in the PR.

## Evidence

The four exact lock resolutions succeeded using existing image
`sha256:5c38ecb767951d1d65f7934ba31ce026d0d62bdddd8f2eb3faa68373fbc692ba`;
each reported only certifi 2026.7.22 → 2026.10.19. Programmatic graph comparison
confirmed every other package record unchanged. Catalogue integrity and baseline
release immutability against `origin/main` passed. The complete catalogue suite
passed all 23 tests, including the two new narrow graph/provenance scenarios.
Further local checks are running; no final CI, merge or installed rollout is
inferred from resolution or local tests. PR checks and the delivery description
record their actual outcome separately.
