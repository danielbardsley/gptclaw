# Manage private Metro sessions

- **Status:** Source opt-in implemented on the MOB-002 branch; runtime/rollout pending
- **Specification:** [SPEC-033](../docs/033-private-metro-sessions/spec.md)
- **Acceptance:** [Current evidence](../docs/033-private-metro-sessions/acceptance.md)

## Current boundary

The installed provider 1.10.1 supports Expo source creation/quality, with no Metro
lifecycle. The development provider 1.12.0 adds explicit schema-6 source adoption;
it still advertises no Metro session/runtime capability. No command below enables
an advisory exception, creates a Serve listener, launches a phone or starts Metro.
Lifecycle/private transport instructions will be added after the security-cleared
SDK spike and verified adapter. No public tunnel, Funnel, EAS or signing fallback.

Run source checks in the prepared Python 3.12 manifest environment. Do not install
host tools. Operate only a selected canonical owned project. Managed task worktrees
remain source-only; opt-in cannot activate or retarget their parent's runtime.

## Explicit source adoption

Use the reviewed source CLI in the activated prepared environment:

```sh
python -B scripts/gptclawctl.py metro enable --project-root /absolute/canonical/project
```

This reads validated schema-5 source, exact mobile/toolchain/dependency policies,
PRJ-006 canonical identity and clean tracked `.gptclaw` metadata. It returns a
`plan_digest`. Default lifetime is 7200 seconds; `--ttl-seconds` accepts 60–28800.
The project cannot declare an origin, host port, environment or arbitrary SDK mode.

After reviewing that concrete plan, apply the same inputs and digest:

```sh
python -B scripts/gptclawctl.py metro enable --project-root /absolute/canonical/project --apply --confirm-plan PLAN_DIGEST
```

Only `.gptclaw/project.yaml` changes: schema 6 adds the Metro opt-in object. Source,
SDK packages, immutable templates, static identity and provenance are preserved.
Review and commit that metadata change through the project's PR workflow before
use. Dirty/untracked metadata, stale inputs, wrong canonical root, unsupported SDK
or toolchain, unknown field/mode and unresolved publication reject adoption.
Source opt-in is not proof of session readiness or Go-client eligibility.

## Metadata interruption and recovery

Each applied publication has an owned record beneath the runtime store's
`metro-metadata/PROJECT/OPERATION/operation.json`. Normal publication retains
`previous.yaml`; atomic exchange also preserves an editor's racing metadata.
A partial archive operation can retain it at the exact `displaced_path` recorded
in the journal. Unknown ownership/path or a preparing/published/recovery-required
record blocks another migration. Do not delete a record to bypass reconciliation.

Inspect only that selected operation's phase and safe paths. Compare the current
manifest and retained previous version, preserve independent source/metadata edits,
and prepare a targeted restoration or merged correction through the project PR
workflow. Do not reset a checkout, overwrite a newer edit, remove unknown temporary
files or roll back a provider while it still owns an unreconciled runtime. Retain
both metadata copies and the journal until recovery is reviewed. No automatic
restoration is implemented at this preparation stage.

## Gates before runtime and private acceptance

The [runtime security disposition](../docs/033-private-metro-sessions/security-review.md)
is disabled until the owner approves its exact scope. It is separate from MOB-001's
source-only exceptions. The SDK spike is at most five minutes, uses only the exact
approved retained fixtures, and exposes only loopback with no persistent SDK logs.
Subsequent sessions need verified bounded supervision/proxy/expiry and fresh security
admission; private listener/access changes use the exact reviewed operator path.
Forge does not administer Tailscale. Preserve existing `/projects/` and `/dashboard/`
handlers, private access, app/data ownership and Funnel-off state.

Manifest/bundle/asset/reload/WebSocket and native Go behavior require actual pinned
SDK and permitted-device tests. Android and iOS results are independent; desktop
HTTP tests do not establish physical acceptance. Typed session observations and launch
availability must distinguish loopback operation, private transport and real client
acceptance. [SPEC-034](../docs/034-expo-go-workflow/spec.md) owns Go launch/QR/client UX
once this Metro provider is available. All full acceptance criteria remain pending.
