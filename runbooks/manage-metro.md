# Manage private Metro sessions

- **Status:** Source opt-in and supervised controller prepared; live lifecycle/private rollout pending
- **Specification:** [SPEC-033](../docs/033-private-metro-sessions/spec.md)
- **Acceptance:** [Current evidence](../docs/033-private-metro-sessions/acceptance.md)

## Current boundary

The installed provider 1.10.1 supports Expo source creation/quality, with no Metro
lifecycle. The development provider 1.12.0 adds explicit schema-6 source adoption;
it still advertises no Metro session/runtime capability. The source controller has
real bounded loopback unit/proxy evidence on the approved fixtures; private and
installed lifecycle acceptance remain pending.
The recovery/security commands below operate only owned state and create no Serve
listener or native-client launch. Live start/private transport instructions remain
pending the verified adapter. No public tunnel, Funnel, EAS or signing fallback.

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
or toolchain, unknown field/mode, unresolved publication and active/unknown source
jobs reject adoption. An idle saved job must also have no extant container;
unknown containers are preserved, never stopped to make adoption succeed.
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
was approved by the project owner for the exact two tooling findings, retained
synthetic fixtures and bounded offline runtime scope. Approval provenance and expiry
are recorded in that review; the two subsequent loopback SDK spikes passed. It is
separate from MOB-001's source-only exceptions and grants no private route approval. The SDK spike is at most five minutes, uses only the exact
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

## Prepared controller recovery and logs

These source commands require the prepared Python 3.12 environment. They are not
claims about the current installed provider or a completed live lifecycle rehearsal.
The controller freezes its provider before launching an owned forge user unit. A
registry binds each project/root/canonical identity to a sticky paired loopback slot;
stop never recycles an origin that an operator listener could still forward to.

Ordinary dependency/toolchain/format/integration jobs require both an inactive exact
user unit and absent owned containers/network. A failed receipt alone does not make
an automatically restarting unit safe to mutate. Foreign units, drop-ins, containers,
networks and listeners are preserved. Partial start/stop outcomes record recovery
required and unknown process observation when shutdown cannot be proven.

If source metadata becomes invalid, use the exact recorded generation and root to
stop an existing owned session without loading the invalid app configuration:

```sh
python -B scripts/gptclawctl.py metro recover-stop --project-root /absolute/canonical/project --generation GENERATION
```

This requires a matching registry/receipt and exact unit-file/readback ownership.
It does not retarget a moved checkout or stop an unknown unit. Retain the receipt,
previous generation history and source view for review if proof fails; do not erase
state or manually kill an unrelated process to retry.

`logs --project-root ROOT --lines N` on opted-in source returns lifecycle events
only. N is 1–256. Events contain timestamps, generation and enumerated operation/
phase states; no raw SDK output, request headers, client identifiers, tokens or
origins are retained. Retention is bounded to 256 events, at most 64 KiB, and seven
days; repeated readiness observations do not append duplicate lifecycle events.

To withdraw this exact runtime policy, inspect a read-only revocation plan:

```sh
python -B scripts/gptclawctl.py metro revoke --policy-digest POLICY_DIGEST
```

Only after deciding to revoke that concrete policy, add `--apply`. It records a
persistent marker in the shared owned store, blocks new admission and is checked
by frozen running supervisors. Revocation does not grant a replacement exception,
reset another policy or remove an operator route. There is no automatic un-revoke;
replacement runtime disposition requires review. Real shutdown/revocation evidence
remains pending; isolated tests cover both pre-execution and running revocation.


The current acceptance record includes real five-minute loopback and paired-session
rehearsals. One expiry under a timed-out native probe required reconciliation;
do not treat that as an accepted recovery baseline yet. Internal control schema 2
records root and live source/assets/dependency directory identities. Replacing a
bound directory requires controlled restart; it cannot silently retarget an active
session. Failure records contain only generation and fixed stage/code values,
never raw SDK errors, request headers or source bodies. See acceptance for the
remaining reproduction and private/operator/device gates.
