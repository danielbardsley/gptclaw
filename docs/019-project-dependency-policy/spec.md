# SPEC-019: Project dependency policy (SYS-003)

- **Status:** Implementation authorized; implemented on feature branch, acceptance in progress
- **Owner:** Daniel
- **Date:** 2026-10-10 (America/New_York)
- **Feature:** SYS-003; initial adapter for the delivered single-web pnpm workflow
- **Design:** [TDD-019](technical-design.md)
- **Tasks:** [TASKS-019](tasks.md)
- **Context:** [Sequence, stage 2](../platform/sequence.md#2-install-the-minimum-supported-execution-environment) · [Architecture, installation boundary](../platform/architecture.md#14-software-installation-boundary)

## Outcome and scope

An agent implementing a requested app feature can add, remove or update project
packages through a predictable container workflow, without installing software
on EC2 or changing another app. The result includes a reviewable package manifest
and lockfile change, clear failure/recovery state, and relevant app checks.
Normal dependency work already authorized by a development task does not need
another approval prompt for every package; repository and platform policy still
apply. New production scope, credentials or host capabilities are separate.

The baseline is [SPEC-018](../018-first-private-application/acceptance.md):
`gptclawctl` 1.0.1, rootless containers, project locks and a fixed Node/pnpm image.
Its startup already performs frozen pnpm installation. It has no reviewed
add/remove/update dependency interface and no complete dependency-policy parser.
SPEC-019 formalizes and integrates that missing policy; it does not replace the
accepted runtime, service manager or private router.

Define general installation rules and implement their first adapter for one
pnpm root package. Include policy validation, typed dependency operations,
frozen restore, lifecycle integration, sanitized receipts, generated guidance,
regression tests and a runbook. Reuse the current reviewed toolchain; this spec
can ship before [SPEC-020](../020-pinned-language-toolchains/spec.md).

Exclude npm/yarn/Python/uv adapters, multiple-package workspaces, private
registries/authentication, global package installs, host setup, package-manager
self-updates, shared cache management, SBOMs, repositories/credential brokerage,
application data, production promotion and public exposure. Later adapters must
implement this policy contract; unsupported managers/sources fail explicitly.
The containers share forge's identity; this policy is not hostile-project isolation.

## Requirements

- **DEP-001 — Declared authority and boundaries.** Publish one versioned policy
  with a strict parser and documented precedence: platform bounds, repository
  restrictions, then the already-authorized task. Project declarations cannot
  loosen platform bounds. Reject unsafe roots, unknown versions/options and
  executable configuration before invoking a package manager. No dependency job
  mounts a host credential directory, engine socket, sibling project or host
  writable path outside its owned job/project storage.
- **DEP-002 — Reviewed sources and package setup.** Initial packages come from
  the public HTTPS npm registry with locked integrity. Reject Git/URL dependencies,
  remote installer commands, external local paths, private registry/auth settings
  and package-manager runtime downloads. Installation hooks are disabled for this
  first adapter, including project install hooks and executable pnpm config.
  Packages requiring a hook need a reviewed policy extension identifying package,
  exact version, effect and tests; project flags cannot grant that exception.
  Build/test/start scripts remain separately authorized container commands.
- **DEP-003 — Explicit changes and frozen reuse.** Frozen installation must not
  change package manifests, lockfiles or policy. Add/update requests name exact
  package versions; remove requests name selected existing packages. Reject
  implicit latest, broad upgrades and arbitrary forwarded flags. Changes produce
  a coherent manifest/lock pair and a receipt identifying changed files and
  before/after hashes; retain unrelated source and Git work. Dependency files
  belong in the app's branch/PR, not only runtime receipts. Never auto-commit,
  reset Git or hide a lockfile change. Removing all dependencies still produces
  an explicit valid lockfile outcome.
- **DEP-004 — Bounded, serialized execution.** Use the selected reviewed rootless
  toolchain, existing per-project lock and resource/output/deadline limits.
  Dependency mutations require the selected app to be stopped and no unresolved
  job; refuse busy outcomes without cancelling them. Another app stays running.
  Startup/test dependency preparation must use the same policy gate and validated
  fingerprints. Agents must not use build/test declarations as a dependency-policy
  bypass; this is not adversarial inspection of arbitrary application code.
  Read-only validation/status do not install, fetch packages or stop services.
- **DEP-005 — Honest failure and recovery.** Stage requested manifest/lock changes
  before publication, check for concurrent edits, and record interrupted outcomes.
  A failure must not claim ready, publish a route or restore over user edits.
  Preserve authored source; mark incomplete disposable dependencies for a bounded
  frozen repair. Recover the same operation by its ID/status before retrying;
  remove only verified task-owned staging files. Do not silently relax integrity,
  source or script restrictions to make installation succeed.
- **DEP-006 — Usable operation and evidence.** Document how an agent performs a
  normal dependency edit, frozen restore, app verification and recovery without
  host installation. Receipts/logs are bounded and redact credentials without
  dumping environment/configuration. Record real commands, versions, timings,
  package/lock diffs and two-project isolation in synthetic acceptance. Keep
  policy guidance and executable behavior consistent.

## Acceptance criteria

| ID | Observable result and evidence | Requirements |
|---|---|---|
| AC-001 | Valid policy/task/project accepted; malformed, unknown, unsafe or conflicting inputs rejected before any installer call. Read-only checks have no install/network/service effects. | DEP-001, DEP-004 |
| AC-002 | A supported public dependency installs with verified lock integrity and hooks disabled. Synthetic install hooks, executable config, foreign paths/sources, runtime downloads and bypass flags are refused or cannot execute; no host/sibling/auth mount appears. | DEP-001, DEP-002 |
| AC-003 | Add an exact package, update it to another exact version, then remove it. Each intended diff is coherent and reviewable; frozen restore changes none of those source files. Existing dirty/unrelated work survives. | DEP-003 |
| AC-004 | Busy/running target refused; stopped target installation obeys limits/locks. Another live app's health, route and dependency-file hashes remain unchanged. Startup/test preparation uses the same policy gate. | DEP-002, DEP-004 |
| AC-005 | Integrity/fetch failure, timeout, crash during publication and concurrent user edit produce explicit recoverable outcomes without source loss or false readiness. Frozen repair and owned cleanup pass. | DEP-003, DEP-005 |
| AC-006 | Focused/local and configured CI checks pass; a synthetic app builds/tests and its private page works after the selected dependency change. Daniel accepts the adapter; runbook, guidance, sanitized receipts and source/lock evidence are merged. | DEP-006 |

## Completion and decisions

Daniel requested this specification separately from SYS-002, then authorized
implementation with “Ok, let's implement SYS-003” on October 10. This authorizes
this initial pnpm policy/adapter, not SYS-002 implementation. Code and live
verification are recorded in [acceptance.md](acceptance.md). Review/merge and
Daniel's final adapter acceptance remain separate; mark only this initial scope
Delivered after implementation merge and AC-001–006 pass.

Implemented defaults are a public-registry-only, no-install-hooks, single-root
adapter. The existing Next.js starter passed frozen install/build/test under these
settings. A package requiring hooks still needs a named, tested policy extension;
no script allowance was added to make this implementation pass. Python/uv and other adapters have explicit later
owners under the sequence's additional-stack initiatives.
