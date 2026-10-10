# TDD-019: Project dependency policy

- **Status:** Implemented on feature branch; local/live evidence recorded
- **Owner:** Daniel
- **Date:** 2026-10-10 (America/New_York)
- **Specification:** [SPEC-019](spec.md)
- **Tasks:** [TASKS-019](tasks.md)

## Approach and existing boundary

Add a shared policy validator and pnpm adapter around the existing container job
executor in `scripts/private_apps.py`. Reuse target validation, project locks,
bounded output, resource limits and owned-job refusal; do not add a parallel
service controller. Current `prepare()` hardcodes frozen pnpm installation and
hashes package.json, pnpm-lock.yaml, pnpm-workspace.yaml and the image ID. Extend
that fingerprint with effective policy/configuration so a changed policy cannot
reuse a previously prepared result. Retain SPEC-018's private routing behavior.

Keep platform policy in `config/project-dependencies/v1.json` and
bundle its strict schema/validator with the immutable provider snapshot.
The implemented initial policy fixes supported manager/source, denied setup behaviors and
bounds; it accepts no shell snippets or authentication fields. Repository rules
may narrow the permitted operations; they cannot replace the platform policy.
Do not add fields to project manifest v1. Future project exceptions need a
versioned format plus owner provenance, not an unchecked package-manager flag.

## Implemented operation contract

Provider 1.1.0 implements the following surface (1.0.1 lacks it):

- `deps status --project-root ROOT`: inspect validity/preparation and operation
  outcome without fetching or executing project code.
- `deps install --project-root ROOT`: frozen restore under the effective policy.
- `deps add` / `deps update`: typed package-name, exact-version and dependency-kind
  inputs; no arbitrary command arguments, flags or shell text.
- `deps remove`: selected package names, with explicit no-op/not-present results.
- `deps recover --operation-id ID [--abort]`: resume a verified operation or
  abandon it while retaining current coherent source. Status also accepts an
  operation ID for archived receipt lookup.

All mutations use the existing project lock and require stopped service/no busy
job. The caller may stop/start that selected app through its authorized lifecycle
workflow; the dependency adapter itself does not silently stop or restart it.
Use the current fixed toolchain until SPEC-020 supplies its reviewed resolver.
Publish version/capability changes and documented JSON/exit semantics. Results
include operation ID, project, action, terminal/partial state, effective policy
and toolchain hashes, changed file names/hashes and finite duration. Store
receipts/journals in a separate versioned runtime subdirectory, avoiding the
existing top-level app-record enumeration. No credential values or environment
copies belong in receipts.

## Resolution, configuration and publication

1. Validate target, policy and typed request before any network job. Inspect only
   necessary metadata for prohibited authentication/environment files; retain
   current refusal rules. Parse bounded known package/config/lock files as data.
2. Reject executable pnpm configuration/plugins, extra workspace roots, global
   installation/cache escapes, implicit runtime/version downloads, unapproved
   registry/Git/URL/local dependency resolutions and integrity bypass settings.
   Enforce precedence explicitly; do not trust project config to honor policy.
3. Resolve intentional changes inside a bounded owned transaction directory,
   mounted as the job's workspace. Disable install scripts and runtime downloads;
   allow only reviewed public registry operations. Verify the resulting graph,
   lock integrity and frozen installation before accepting the candidate pair.
4. Recheck original dependency-file hashes under the project lock. If an editor
   changed them, preserve both the user's files and the staged operation as a
   conflict; do not restore backups over those edits.
5. Publish the validated manifest/lock pair using a recovery journal, retained
   original copies/inodes and exclusive replacement creation. A detected editor
   replacement is never overwritten. A multi-file
   update is not claimed atomic. On interruption reconcile file hashes and phase
   before resuming. Install disposable project dependencies through a frozen job,
   invalidate old prepared/build fingerprints and mark ready only after success.
   A partial modules directory is repairable state, not successful preparation.
6. The caller runs app test/build and starts it through the existing lifecycle.
   Review changed dependency files in the app's own Git workflow when it has one;
   a synthetic non-Git fixture still records file diffs/hashes. No GitHub creation
   or automatic commit is included.

Exact pnpm 12.10.1 flag behavior and configuration allowlisting were verified.
The no-hook/no-runtime/pmOnFail error controls are applied to installer jobs and
the job/service environment. Frozen dependency files are also mounted read-only.
The builtin alternate @jsr scope is pointed explicitly at the approved npm registry. Official [install documentation](https://pnpm.io/cli/install)
describes frozen installs, lockfile-only resolution, script suppression and
runtime-download suppression. [Settings documentation](https://pnpm.io/settings)
identifies workspace/global configuration sources. These sources guide adapter
selection; acceptance must prove behavior using the pinned executable, including
conflicting project settings. Do not use checksum-refresh/force fallback.

## Components and rollout

| Component | Planned change | Requirements |
|---|---|---|
| Policy/schema and shared parser | Versioned source/operation/setup bounds; safe observation-only validation | DEP-001, DEP-002 |
| Dependency adapter/CLI | Typed requests, transaction/recovery, locks and sanitized results | DEP-003–006 |
| Existing prepare/test path | Same policy gate; policy-sensitive fingerprints; frozen repair | DEP-002, DEP-004, DEP-005 |
| Provider snapshots and app template guidance | Bundle policy/parser; explain allowed routine work, review and failures | DEP-001, DEP-006 |
| Tests, synthetic fixtures, runbook and CI | Contract/denial/recovery coverage and two-app live proof | DEP-001–006 |

Use synthetic task-owned fixtures; do not mutate the existing Hello World apps
for initial migration experiments. Prove template compatibility before enabling
the policy on ordinary startup. Preserve existing projects and caches; a project
that needs unsupported setup receives a clear compatibility error, not silently
changed files. Rollback uses a reviewed provider revision and target-specific
frozen restoration of explicitly selected dependency revisions; do not run Git
reset, prune shared images or delete source. Runtime state must fail explicitly
when an older provider cannot reconcile it. No AWS/host configuration is planned.

## Traceability and implementation decisions

| Requirements | Mechanism | Tasks | Acceptance |
|---|---|---|---|
| DEP-001, DEP-002 | Strict policy/config/source gate | T-001, T-002 | AC-001, AC-002 |
| DEP-003 | Explicit staged changes and frozen reuse | T-003 | AC-003 |
| DEP-004, DEP-005 | Shared locks/bounds, journal and repair | T-003, T-004 | AC-004, AC-005 |
| DEP-006 | Guidance, live workflow, receipts and delivery | T-005 | AC-006 |

T-001 resolved the exact workspace keys, CLI arguments and receipt/journal
semantics in [the runbook](../../runbooks/manage-project-dependencies.md).
Native pnpm lock format 9 accepts its two documents; unknown importers/config
and exotic resolutions fail. Journal phases and per-operation history are
versioned; a rollback provider that cannot parse the `deps` operation marker
fails instead of consuming an unresolved dependency transaction. No host
installation permission or SYS-002 profile registry was introduced. SYS-002 may consume this adapter later, but its new
profile registry is not a prerequisite to the initial implementation.
