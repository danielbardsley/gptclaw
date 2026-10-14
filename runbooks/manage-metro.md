# Manage private Metro sessions

- **Status:** Owned loopback lifecycle/proxy verified; private operator/installed/device acceptance pending
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

## Private route preparation and observation

The source provider implements read-only metro route-plan --project-root ROOT.
Its --apply --confirm-plan DIGEST records the exact unchanged plan outside source,
without executing operator commands. No occupied unrecorded listener is adopted.
See the [two-fixture operator plan](../docs/033-private-metro-sessions/operator-plan.md)
for concrete add/remove commands, baseline digest, access-policy prerequisites
and rollback. The project owner approved both exact listeners; operator execution/readback and
access-policy evidence remain pending.

The supervisor compares exact Serve targets and preserved baseline handlers,
then probes default-trust private HTTPS health for its current project/generation/
expiry every ten seconds. A ready process is independent of a pending/failed route;
a host TLS result is independent of phone ACL access/native acceptance. Both
reviewed listeners can coexist; removal of one cannot redirect it to the other.

The corrected full fixture-two proxy probe passed both native bundles, source maps,
icon and WebSocket ping-pong, then cleanly expired with SDK/network absent and proxy
released. The older recovery-required case remains recorded without an invented
cause. Tests now cover expiry while the upstream is stalled before headers, and
probes permit bounded cold compilation within their caller deadline. No private
listener or stable installed-provider change was performed at this checkpoint.

The exact-owned SDK crash rehearsal passed automatic recovery within the original
session expiry, then successful inactive cleanup with source preserved. Both
current fixture sessions are terminal. The full local offline repository gate
passed; installed/private/device acceptance and remaining recovery controls stay
separate. Do not infer a physical client or SSM-disconnect result from this test.

## Explicit renewal and bounded runtime retention

The source controller supports metro renew --project-root ROOT --generation GEN
and optional --ttl-seconds N. Default is a read-only plan. Review its digest before
adding --apply --confirm-plan DIGEST. Renewal requires current owned running state,
unchanged inputs, valid security admission and a verified private route. It stops
the old generation and performs a fresh start/audit with a new generation and
finite lifetime; old launch payloads expire. It never extends the existing
container timeout. If stop/start proof fails, inspect recovery state before retrying.

metro prune --project-root ROOT is also read-only by default. It requires an
inactive owned session. Review selected copies/retained reasons/aged records and
apply only with --apply --confirm-plan DIGEST. It removes only proven inactive
generated copies, preserving current/unresolved/edited/unknown/pre-marker copies
and canonical source. Batches are bounded to 32 copies and 64 metadata records.
Known inactive receipts/markers/fixed diagnostics retire after seven days;
protocol/acceptance evidence remains.

Admission caps each project's runtime store at 1 GiB generated source, 10 MiB
artifacts, 65,536 entries and 128 copies. No automatic cleanup bypasses ownership.
If cleanup reports metro-prune-recovery, retain its prune-* staging and reconcile
the recorded identity/content; do not recursively delete unknown state or source.
Active status hides transport availability if security admission is unavailable,
even before the supervisor's next check. Installed/private acceptance is separate.

## Minimum native inventory observation

A compatible collector can show schema-6 Metro summary and separate process,
protocol/private-route observations, each with freshness, plus finite expiry.
It requires both runtime schema 6 and Metro session schema 1 capability.
Older providers and schema-5 projects retain native source-only presentation.
No native session is represented as a web/API/DB component or Open app/API-doc
target. Source checks and physical-client acceptance remain separate; Go launch
links/QR require SPEC-034. Source implementation/browser checks do not install
a collector release or prove a phone loaded. Current private rollout remains pending.

Established-session protocol probe failures report protocol unavailable and retry
in the same owned process/generation/lifetime; they do not by themselves trigger a
restart. Initial readiness still has a 300-second deadline. Actual SDK exit, owned
proxy failure, security/input/mount drift and expiry retain their cleanup paths.
Supervised development enables the pinned CLI's source watching with CI=false,
closed stdin and non-TTY output; audit/spike jobs retain CI=1. Do not enable a TTY,
public tunnel or credential prompt to obtain Fast Refresh.


## Expo Go inspection during consumer implementation

The development provider supports read-only candidate inspection:

~~~sh
gptclawctl go inspect --project-root /srv/forge/projects/mob001-accept-one --platform android --client-version 57.0.9 --os-version 11
~~~

This command describes the development candidate; the stable installed provider
must advertise `expo_go_inspection_schemas: [1]` before using it. An older provider
must report unsupported rather than silently run another tool. Inspection validates
canonical ownership and the fixed public SDK/graph/config/toolchain profile. Client
and OS arguments are caller reports, not host discovery or certification. Ready Metro
and eligible source still return client check-required and launch unavailable until
Go launch/device evidence is implemented. There is no hidden server start, route
change, account operation, external QR service or native development build.

The owner permits all devices on the development tailnet to access the host. Preserve
the accepted existing access grant and private Serve listeners; off-tailnet access
remains denied. Do not add narrower rules expecting them to override a wildcard allow.


## Bounded transport diagnostics and native launch troubleshooting

With a current owned session, read `/_gptclaw/metro-transport` on its approved
private HTTPS origin to compare fixed aggregate resource/status and rejection
counters before and after a deliberate launch attempt. Counters are transient,
saturating and non-identifying; health/diagnostic probes do not increment upstream
resource categories. Do not collect request headers, URLs, device lists or logs.
A healthy phone-browser endpoint does not prove that Expo Go loaded a manifest.

The tested host entry is `/_gptclaw/metro-session/GENERATION`, using the current
owned generation. It maps only to the SDK manifest root without rewriting its
body/signature or resource URLs. Old entries and unbound manifest aliases return
503. The previous query-based candidate failed in Android Go despite warm bundles;
do not present it as supported or remove generation guards to work around failure.
Actual native launch remains an acceptance gate; use only current unexpired
candidates during the owner check. No automatic restart, renewal or account setup
is part of reading diagnostics or producing a QR.


The exact entry permits the current generation with or without one trailing slash;
Go’s Android kernel removes nonreserved queries and the final slash. Generate the
slash-free path, retain the generation guard and leave manifest bodies/signatures
unchanged. Native client verification is separate from host path tests.


A native “Packager is not running” message at `http://…:8443` after a successful
HTTPS manifest indicates the known SDK-57 Android client development-probe mismatch,
not that the owned Metro process stopped. Verify the HTTPS `/status` and aggregate
stages separately. [The transport decision](../docs/034-expo-go-workflow/client-transport-decision.md)
requires explicit scope selection before changing the approved HTTPS boundary or
building a client. Do not repeat bundle warmups or present this client as supported.


The owner approved private HTTP over Tailscale for the two Metro listeners as a
SDK-57 Go compatibility measure. [Restore HTTPS after a compatible official client
ships and passes native TLS/reload checks](../docs/034-expo-go-workflow/client-transport-decision.md#approved-decision-and-https-restoration-follow-up).
SDK-58 Go drops SDK-57 support, so a store update alone is insufficient; any new
SDK/source/security matrix needs its own review. No scheduled or automatic
conversion is implied.
