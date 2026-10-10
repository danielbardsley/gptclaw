# Manage project dependencies

[SPEC-019](../docs/019-project-dependency-policy/spec.md) supplies the initial
single-root public npm/pnpm adapter. Use the source `scripts/gptclawctl` from the
GptClaw checkout or its installed snapshot launcher. Observe `--version` first;
provider 1.1.0 advertises `deps` and dependency receipt schema 1. Commands execute
only in the reviewed rootless Node/pnpm image, never through host Node/npm.

## Normal app work

A feature task that already authorizes changes to this app authorizes ordinary
dependency work under its repository/platform policy. No additional per-package
approval is required within that scope. This does not authorize new production
scope, private credentials, host packages, public exposure or policy exceptions.
Read applicable app guidance, preserve existing Git work, and stop only this app
before any dependency mutation. Source editing is allowed during normal app
operation; dependency file publication is serialized and checks for editor changes.

```sh
scripts/gptclawctl deps status --project-root /srv/forge/projects/my-app
scripts/gptclawctl stop --project-root /srv/forge/projects/my-app
scripts/gptclawctl deps add --project-root /srv/forge/projects/my-app --package is-number --version 6.0.0 --kind development
scripts/gptclawctl deps update --project-root /srv/forge/projects/my-app --package is-number --version 7.0.0
scripts/gptclawctl deps remove --project-root /srv/forge/projects/my-app --package is-number
scripts/gptclawctl deps install --project-root /srv/forge/projects/my-app
scripts/gptclawctl test --project-root /srv/forge/projects/my-app
scripts/gptclawctl start --project-root /srv/forge/projects/my-app
```

The examples describe supported syntax, not instructions to add that library to
every app. `add` requires an absent package and an exact version; `--kind` is
`runtime` (dependencies, default) or `development` (devDependencies). `update`
requires an existing package and preserves its group. `remove` removes only that
package and is a no-op when absent. No implicit latest, ranges, bulk upgrades,
arbitrary flags or shell text are accepted. Initial direct dependencies are
exact versions; peer ranges are compatibility constraints only.

Review package.json and pnpm-lock.yaml changes with the feature's source changes
in the app's own branch/PR. The adapter never commits, stages, resets or creates a
GitHub repository. Frozen `install` restores modules without changing the package
manifest, lock or workspace settings; all three are mounted read-only during
that job and their hashes are checked. Keep node_modules/ and .gptclaw-cache/ out
of Git; existing projects should add the cache ignore rule through their normal
reviewed source change. Project caches are not shared or automatically pruned.

## Policy and compatibility

The versioned platform policy and strict schema are bundled with the provider.
Its fingerprint includes the effective environment/install controls, package
files and selected image. Both startup and test preparation use the same policy
and refuse unresolved dependency operations. Existing apps are never silently
rewritten, stopped or reinstalled during a provider upgrade. An old preparation
fingerprint needs a selected-app stopped repair/restart before new tests can use
it; the other apps are unaffected.

The adapter supports pnpm 12.10.1 with the existing reviewed Node image. SYS-002
project version selection is separate work. It accepts the native two-document
pnpm lock (manager metadata plus app graph), only the root importer, public npm
resolutions with SHA-512 integrity, and the fixed package-manager declaration.
It disables install scripts, executable pnpm config, runtime/package-manager
selection downloads, and implicit dependency installs before running scripts.
The builtin alternate @jsr scope is explicitly pointed at the approved npm
registry. No package requiring an install hook is grandfathered; a concrete
reviewed extension needs its own package/version/effects/tests.

Workspace settings are limited to an absent or `['.']` package list, a release
age of at least 1440 minutes, and a subset of the existing exact
`@types/node@24.19.2` release-age exclusion. Unknown keys, registries, script
allowlists, caches outside the job/project, runtime/config dependencies, Git/URL/
local dependencies and override settings fail before installation. Authentication/
environment files and executable pnpm files are refused by metadata inspection;
contents are not printed. No credential/home/engine-socket/sibling mounts occur.
These are supported-workflow controls, not adversarial inspection of arbitrary
build/test/app code or isolation between hostile projects sharing forge.

## Receipts, interruption and recovery

Dependency operations share the lifecycle's project lock, one owned job name,
1 CPU/1536 MiB/256 PID limits, 300-second per-job deadline and bounded output.
Busy operations are refused without cancelling or replacing them. Ready/active
app services are refused before dependency writes. State and receipts live under
`.gptclaw-runtime/v1/dependencies/<project>/`, outside source manifests and the
app-record enumeration. Each operation retains a receipt with its ID, action,
request, policy/image hashes, before/after file hashes, changed files and duration.
Status is observation-only; it fetches/installs nothing and runs no project code.

```sh
scripts/gptclawctl deps status --project-root /srv/forge/projects/my-app
scripts/gptclawctl deps status --project-root /srv/forge/projects/my-app --operation-id RECEIPT_ID
scripts/gptclawctl deps recover --project-root /srv/forge/projects/my-app --operation-id RECEIPT_ID
```

Resolution/frozen candidate installation runs in a private owned transaction
workspace. Publication records a journal before changing files, retains original
copies/inodes, and exclusively creates replacements so an editor's newly created
file is not overwritten. Multi-file publication is recoverable, not atomic.
Recovery accepts only the recorded old/new hashes (or the captured original when
publication was interrupted with a file absent). Policy/image changes, an unknown
source hash or a lingering job stop automatic recovery. It never chooses another
operation ID or overrides a newer operation.

A failed resolver with no verified candidate can be abandoned explicitly:

```sh
scripts/gptclawctl deps recover --project-root /srv/forge/projects/my-app --operation-id RECEIPT_ID --abort
```

Abort keeps the current source files; it does not undo already published changes
or revert an editor's work. Current dependency files must form a valid coherent
pair first. For a publication conflict, inspect only this operation's private
`jobs/<id>/original` and `captured` files and reconcile through a normal reviewed
source edit, then abort/recover. Do not restore snapshots over unknown current
files. A partial modules tree is disposable repair state; frozen installation
repairs it before preparation/readiness. Unknown jobs are preserved until their
outcome is reconciled. A policy-valid receipt is not proof of an app's health.

Only verified task-owned transaction folders are removed. `retained_files: true`
means cleanup was deferred because ownership/content/IO could not be established;
preserve that directory for scoped inspection. Terminal `recover` may retry its
owned cleanup. Receipts remain available after later dependency operations.
No raw environment or credential-bearing configuration/output is retained.
For denied/busy/integrity outcomes, do not grant privileges, change registry,
enable hooks, refresh checksums or prune shared images to make the job pass.

Results are JSON. Exit 0 indicates the reported successful observation/operation;
1 indicates policy/conflict/busy/recovery-required/partial private route; 2 is
usage/setup/internal unreconciled failure. Read the receipt and same-target status
before another mutation after lost output or timeout. Build/test/start still need
their own successful outcomes; full owner/CI/merge acceptance is recorded in the
initiative's acceptance record. Rollback uses a reviewed compatible provider and
explicitly selected dependency revisions, retaining source and policy guards.
