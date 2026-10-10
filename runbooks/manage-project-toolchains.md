# Project-selected Node/pnpm toolchains

Provider 1.2.0 adds the initial [SYS-002 web slice](../docs/020-pinned-language-toolchains/spec.md).
Use the managed CLI as forge; no host Node, npm, version-manager installer or sudo
is needed. Dependencies continue through the [SYS-003 adapter](manage-project-dependencies.md).

## Supported matrix and selection

| Profile / revision | Exact versions | Platform | Ownership |
|---|---|---|---|
| node-pnpm / 1 | Node 24.21.0, pnpm 12.10.1 | Linux amd64 (including this EC2 x86-64 host) | Daniel; additions/retirement through reviewed platform PRs |

[Registry v1](../config/toolchains/v1.json) records the OCI base digest, public
pnpm tarball URL/SHA-512 and trusted installer hash. The registry and
[declaration schema](../schemas/toolchains/v1.schema.json) are bundled with the
provider. Node's exact executable is checked against its reviewed digest; the
pnpm artifact is fetched over HTTPS without redirects, bounded to 16 MiB, checked
before installation, installed offline with hooks disabled and version-checked.
Profile revisions are immutable after merge. A second pair needs a new reviewed
revision, tests and dependency-policy compatibility; arbitrary project versions
and image URLs are refused. Python/uv and Expo belong to the selected stage-12
stack initiatives, owned by Daniel; they require separate adapters and evidence.

New apps receive `.gptclaw/toolchain.json`:

```json
{
  "schema_version": 1,
  "profile": "node-pnpm",
  "profile_version": 1,
  "versions": { "node": "24.21.0", "pnpm": "12.10.1" }
}
```

Keep manifest v1 unchanged. The sidecar must be a bounded regular owned file;
unknown/duplicate fields, ranges, malformed versions, symlinks and hardlinks fail.
`packageManager` must agree. Optional `.node-version`/`.nvmrc` must contain the
exact Node version (no `v` prefix or aliases). `engines.node`/`engines.pnpm` may
constrain the selected stable versions using numeric comparators, caret/tilde,
partial/wildcard versions, space-separated intersections, `||` or exact hyphen
ranges. Unsupported syntax and unsatisfied constraints fail offline; the trusted
runtime repeats the compatibility check. Alternate runtime/version-manager
metadata such as devEngines, pnpm runtime downloads, `.tool-versions` and mise
configuration is refused. Changing project metadata never grants an installer.

## Inspect and prepare

```bash
/srv/forge/projects/.gptclaw-runtime/v1/gptclawctl --version
/srv/forge/projects/.gptclaw-runtime/v1/gptclawctl toolchain inspect --project-root /srv/forge/projects/my-app
/srv/forge/projects/.gptclaw-runtime/v1/gptclawctl toolchain prepare --project-root /srv/forge/projects/my-app
```

Inspect is observation-only: validates selection/metadata and reads receipts and
image presence/labels/platform. It does not install, build, run an image, modify
source or create state. `unprepared` is a successful observation, not readiness;
`verified` reports a matching successful receipt and present matching image.
`active_image` and `active_selection_hash` identify the last managed app state;
they do not assert a service is currently running. Use app `status` for health.

Prepare requires the target stopped, no unresolved dependency operation and no
owned job. It acquires a per-project lock and a nonblocking per-profile lock;
busy requests fail without cancellation. Cold acquisition has a 300-second build
limit, CPU 1, memory 1536 MiB and nproc 256; actual version verification has a
30-second limit, a read-only image, no network/project/credential mounts, CPU 1,
memory 1536 MiB and PID 256. stdout/stderr are bounded to 1 MiB each. Public image
pull uses a generated empty authentication file; no credentials are read into a
job or committed. Image storage/authentication machinery remains Podman's host
service concern; this is not hostile-process isolation.

A matching cache receipt/image is verified again using actual Node/pnpm
executables on prepare. Missing verified images can be recreated from the same
pins. Foreign/unreceipted/retagged cache images or recipe/provenance mismatch fail
without overwriting or deleting them. Start/test/dependency operations use this
resolver and the same selected image. Selection/image/policy changes invalidate
only that app's dependency/build fingerprints. Automatic frozen installation
never rewrites authored dependency files.

Exit codes: 0 for successful observation/preparation; 1 for policy, platform,
verification, conflict, busy, failed command or recovery-required outcomes; 2 for
usage/setup/internal failures. Results include selection, legacy flag, hashes,
receipt, image presence and changed. CLI receipts use toolchain schema 1.

## Legacy adoption and switching

A reviewed `nextjs-v1` app without the sidecar maps to the immutable **legacy**
node-pnpm/1 profile, independently of future defaults. Inspect/start do not write
it. Existing running legacy units stay on their accepted image during a ready
start no-op; they have no retroactive artifact-verification claim. A managed
stop followed by start/test/prepare obtains the verified baseline and records
selection/image outside source. Active legacy tests with an old preparation
fingerprint may require this stop/prepare transition. Stop remains usable even
when toolchain metadata is invalid so a failed selection can be corrected.

For explicitly requested adoption, stop the named app with `gptclawctl stop`,
add only the declaration above in its normal branch/PR, inspect it, then prepare,
test and start. Preserve package/lock/source bytes. A future supported switch
uses the same stopped-target sequence and exact matching metadata. Unknown or
incompatible selections fail without rewriting source; reconcile dependencies
through the explicit SYS-003 workflow. Running apps are never auto-upgraded.

## Failure, recovery and rollback

Receipts live under `.gptclaw-runtime/v1/toolchains/<profile-hash>/receipt.json`,
with completed attempt history under `receipts/<operation-id>.json`. Known failed
builds retain their owned job directory and bounded sanitized `build.log` when
available. An absent image after a known failed attempt can be retried explicitly;
unknown/acquiring outcomes or an image produced without successful verification
require scoped reconciliation. Failed reuse verification invalidates readiness.

On interrupted acquisition, inspect the same profile receipt/operation ID and
named verification container; do not blindly retry, remove shared images, cancel
unknown jobs or reset the receipt. A timeout can leave Buildah external objects.
The reviewed operator must establish the exact owned objects' state and approve
any required targeted cleanup/receipt reconciliation; this interface deliberately
has no automatic takeover or force-recovery operation. Preserve unknown resources
and report the blocking observation. Retained job files are inert provider data,
not app source. Successful jobs remove only their verified known owned files.

Rollback stops only the selected app, selects a still-reviewed previous profile
and compatible source/dependency revisions, then prepares/tests/starts through
the managed interface. Provider rollback uses the prior reviewed snapshot.
Do not silently downgrade or prune images. If no compatible prior profile exists,
report blocked. Retirement needs owner, reason, affected projects and an explicit
migration/rollback window in a PR; it never changes running selections.
