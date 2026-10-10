# TDD-020: Project-selected container toolchains

- **Status:** Implemented on feature branch; local/live evidence recorded
- **Owner:** Daniel
- **Date:** 2026-10-10 (America/New_York)
- **Specification:** [SPEC-020](spec.md)
- **Tasks:** [TASKS-020](tasks.md)

## Approach and contracts

The provider replaces its single hardcoded Containerfile selection with a reviewed
profile resolver, keeping rootless execution and the existing lifecycle backend.
The SPEC-018 baseline `toolchain()` hashed `templates/apps/node-toolchain/Containerfile`, builds
an image and verifies its label; `prepare()` includes the image ID in dependency
fingerprints. The implemented declaration/registry/verified receipt adds selection and
actual version/integrity checks.

A separate `.gptclaw/toolchain.json` avoids inserting unsupported fields
into manifest v1. The initial supported selection is:

```json
{
  "schema_version": 1,
  "profile": "node-pnpm",
  "profile_version": 1,
  "versions": { "node": "24.21.0", "pnpm": "12.10.1" }
}
```

Use a bundled strict schema: bounded regular owned files, duplicate/unknown keys
and symlink refusal, exact version strings and integer profile version. Resolve
against the strict `config/toolchains/v1.json` registry; declared versions must match
that immutable profile. Package.json's `packageManager` and any supported exact
runtime-version file must agree. Engine ranges are compatibility constraints,
not version selectors; test them under the selected runtime. Define exactly which
metadata is supported; do not silently accept an alternate-manager/runtime hook.
The source manifest and template provider marker keep their current meanings.

## Profiles, images and receipts

Each reviewed profile records its stable family/revision, exact versions, OS/
architecture, OCI base digest, pnpm artifact URL/integrity, controlled build recipe,
verification arguments and recipe/profile digest. No project-defined URLs or
commands enter the build path. Start with the existing Node 24.21.0/pnpm 12.10.1
pair and base digest in the reviewed Containerfile. The public pnpm 12.10.1 artifact's SHA-512 is pinned in that registry and verified
before installation. The original Containerfile remains for explicit baseline
compatibility/CI; managed acquisition uses a trusted generated recipe and hashed
`install-pnpm.cjs`, with no project-supplied commands or sources.

Build/download only through the approved rootless image job, with limits and a
per-profile lock. Verify the pinned artifact before its container installer runs;
verify actual Node/pnpm versions from the resulting selected image with trusted
fixed arguments and no project source/credentials mounted. Receipt includes
profile/recipe digest, base/artifact integrity references, actual image ID,
observed versions, platform and operation outcome. Store versioned toolchain
records outside the top-level app-state enumeration. Image tags/labels alone are
not sufficient successful-version evidence.

A cached artifact must match its approved receipt/provenance. Missing images may
be recreated; conflicting/unverifiable images fail or use a fresh owned build
path, never overwrite unknown objects. A missing remote pin/integrity failure
is terminal for that preparation; no floating-tag/current-version fallback.
Concurrent requests for one profile share serialized preparation, while unrelated
app services remain available. Shared cache quotas/pruning are SYS-006, not here.

## Implemented interfaces and integration

`gptclawctl toolchain inspect --project-root ROOT` and `toolchain prepare` are
provider 1.2.0 additions. Inspect parses known metadata and
reads receipts/image presence; it does not download/build/launch project code.
Prepare is an explicit mutation using reviewed fixed acquisition/version checks.
Normal start/test invokes that same resolver when preparation is required.
Document supported capabilities, exit/status categories and finite deadlines
before exposing the new commands. Schema/registry files join provider snapshots.

Resolver output is a verified image ID/profile hash, not an executable project
command. SYS-003 consumes it for dependency jobs; lifecycle build/test/service
uses the identical selection. Include profile/policy/image changes in preparation
and build fingerprints. Refuse switching an active/busy project. New selections
must not regenerate another app's units, choose another app's image or change its
routes. Preserve source/lockfiles; an incompatible lock/toolchain pair produces
an error and an explicit dependency-update workflow, not automatic lock rewriting.

New web scaffolds select the reviewed default and write exact metadata.
Legacy `nextjs-v1` projects without the sidecar map to one immutable baseline
profile, explicitly identified as legacy in results. Do not silently map them to
the newest default in future releases. Adoption writes only the known selection
through a separately requested/documented step; inspect/start do not modify
source. An unknown sidecar version remains an error, never a legacy fallback.

## Components and verification

| Component | Implemented change | Requirements |
|---|---|---|
| Sidecar schema/parser and profile registry | Safe exact selection and support matrix | LNG-001, LNG-002 |
| Rootless acquisition/version verifier and receipts | Immutable sources, bounded locks/jobs and honest reuse | LNG-002, LNG-003 |
| Dependency/lifecycle integration | Same image everywhere; policy-aware invalidation; active-target refusal | LNG-004 |
| Template metadata and compatibility adapter | Explicit new selection and non-mutating frozen legacy mapping | LNG-005 |
| Tests, runbook, matrix and provider snapshots | Proven acquisition/use/failure/migration and continued ownership | LNG-001–006 |

Offline tests use synthetic registries/receipts and at least two distinct profile
selections; invalid selections must not invoke acquisition. Live verification
uses owned synthetic projects and a task-owned uncached image namespace, rather
than pruning global images to simulate cold setup. Record actual download/build/
reuse durations and versions. Test missing/bad artifacts, failed verification,
cache conflict, busy locks, interrupted acquisition, metadata mismatch, legacy
migration and unaffected second-app state. Run the selected pair's frozen
install/build/test and private page/health acceptance with the SYS-003 adapter.

Profile revisions are immutable: upgrades add a tested new revision; old projects
remain pinned. Retirement records owner, reason, affected projects and an explicit
migration/rollback window. Never delete shared images or source as an upgrade.
Rollback selects a still-reviewed previous profile/provider and restores matching
project dependency revisions through SYS-003; if no valid previous profile exists,
report blocked rather than inventing fallback. This is not a host package update
or infrastructure deployment.

## Traceability and decisions

| Requirements | Mechanism | Tasks | Acceptance |
|---|---|---|---|
| LNG-001, LNG-002 | Sidecar validation and immutable registry | T-001, T-002 | AC-001, AC-002 |
| LNG-003 | Owned acquisition/verification and reuse | T-003 | AC-003 |
| LNG-004, LNG-005 | Runtime integration and compatibility | T-004 | AC-004, AC-005 |
| LNG-006 | Matrix, migration, live evidence and delivery | T-005 | AC-006 |

T-001 resolves profile/declaration/receipt schemas, metadata precedence and exact
artifact checks against the selected sources. Preserve the current working pair
unless an explicit reviewed change is needed; no alternate live pair is assumed
approved. SYS-003's accepted adapter is the gate for dependency/lifecycle use.
Python/uv and Expo toolchain support remain owned by the stage-12 stack initiatives;
they need exact sources, policy adapters and their own live/CI evidence.

## Resolved implementation contracts

The declaration uses [schema v1](../../schemas/toolchains/v1.schema.json);
[registry v1](../../config/toolchains/v1.json) accepts only exact reviewed profile
fields, source origins/digests, platforms and installer hashes. Duplicate keys,
unsafe/non-owned/non-regular/hardlinked files and unknown values fail. Stable
engine-range grammar and exact version files are documented in the
[runbook](../../runbooks/manage-project-toolchains.md); compatibility is checked
offline and again under the verified runtime. Manifest v1 is unchanged.

Profile receipts use schema 1 with profile/recipe hash, full approved provenance,
operation ID, acquiring/verified/failed/unknown phase, image ID, observed versions,
sanitized error and bounded duration. They live under the toolchains subtree,
with attempt history outside app-state enumeration. Tags are scoped by owned
provider-store path and profile hash. Matching receipt/image/provenance is required
for reuse; actual executables are rechecked. A failed reuse invalidates verified
state. Acquiring/unknown attempts and produced but unverified cache objects refuse
automatic takeover; operator reconciliation preserves unknown resources.

Cold build limit is 300 seconds, memory 1536 MiB, CPU quota 1 and nproc 256
(the supported Podman 4.9 build flag). Verification is a named 30-second
read-only/no-network container with PID 256 and no source/credential mounts.
Artifact fetch has a 60-second request timeout and 16-MiB limit; npm installation
runs offline/no hooks with a 60-second timeout. Public acquisition uses a generated
empty auth file. Output limits reuse the provider's 1-MiB-per-stream command runner.
Known failure logs are sanitized/bounded. Successful cleanup removes only verified
fixed owned job files; failure job data is retained. No shared cache/image pruning.

Dependencies and start/test use the same selected verified image and selection
hash; project locks protect operation/state changes. A stopped selection change
invalidates dependency/build fingerprints. Active switching fails with busy;
existing running legacy units permit a ready start no-op without retroactive
artifact provenance. Future defaults cannot alter the separate fixed legacy
registry reference. Explicit adoption changes only the sidecar after a managed
stop, with exact metadata and source/lock retention. Interrupted SYS-003 publication
resolves against its hash-verified saved manifest until publication is coherent,
so a missing captured manifest does not block safe same-ID recovery.

CI uses a synthetic Docker adapter for real integrity-checked acquisition/reuse
and selected-image frozen install/build/test/typecheck, plus the baseline workflow.
Docker CI build uses a 300-second command/15-minute job bound; Podman build resource
flags and private service behavior are separately proven on EC2. It adds no host
language installation, AWS changes, alternate real pair or privileged access.
