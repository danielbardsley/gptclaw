# TDD-015: Host Tool Profile

- **Status:** Implemented for review; not deployed
- **Owner:** Daniel
- **Last updated:** 2026-10-01 (America/New_York)
- **Specification:** [SPEC-015](spec.md)
- **Tasks:** [TASKS-015](tasks.md)
- **Evidence:** [Acceptance status](acceptance.md)

## Implementation

The authoritative [profile](../../infra/dev-host/host-tools.json) uses version-1
JSON for Ubuntu 24.04 amd64. Its 17 records cover the 12 existing explicit apt
packages and five specialized bootstrap components. Each declares purpose,
capability owner, adapter, identity, source, version policy and verification.
The [structural schema](../../infra/dev-host/host-tools.schema.json) is supplemented
by the [stdlib validator](../../infra/dev-host/lib/host_tools.py): strict JSON
parsing, duplicate keys/IDs, package ownership, safe arguments, fixed source and
identity matching, required bootstrap consumers and exception dates. No field is
shell text. The same validator runs in repository checks and before provisioning.
Python 3 on the Noble image is checked before installation; there is no fallback
package list to bootstrap the parser.

[Compute](../../infra/dev-host/compute.tf) reads the profile and standalone helper
from within the Terraform module and embeds them in
[cloud-init](../../infra/dev-host/templates/cloud-init.yaml.tftpl), together with
the deployment Git revision. Files therefore travel inside the HCP configuration
boundary and change instance user data. Existing replacement behavior remains.
No AWS resource, identity permission or public ingress is added.

Cloud-init writes root-owned files at `/etc/gptclaw/host-tools-profile.json`,
`/etc/gptclaw/host-tools-context.json` and
`/usr/local/libexec/gptclaw-host-tools`. Only `validate` is exposed for use from a
checkout. Provisioning actions require root and that installed helper path; this
is an operational guard, not a sandbox against an administrator editing code.

## Adapters and component disposition

| Adapter | Installation/verification behavior |
|---|---|
| apt | Profile-owned package arguments; distribution-maintained or exact policy; validate selected missing-package version against official Noble archive/security origins; installed matching packages remain untouched. Verify installed dpkg status/version. |
| SSM | Detect exactly one loaded dpkg/snap unit and verify agent version; absence uses the explicitly declared stable snap channel. Two loaded variants fail instead of choosing one. |
| AWS CLI | Verify canonical executable/version; absent tool uses approved channel zip or exact versioned URL plus SHA-256 before extraction. Unknown existing installation trees fail. |
| Tailscale | Verify canonical executable/version; absence uses the existing official installer. Enrollment/service configuration remains in bootstrap. |
| CloudWatch | Verify dpkg installed status/version; absence uses existing official deb; an untracked existing installation directory fails. Existing logging configuration remains in bootstrap. |
| Codex | Verify its canonical user executable/version as `forge`; absence downloads the existing installer and runs it as `forge`, preserving user-scoped installation. |

Daniel explicitly approved the five existing channels through November 1, 2026
(America/New_York). Each profile exception includes owner, scope, reason, approval,
expiry and removal. Version selection is transparent, not immutable: channel
installers retain their upstream behavior and distribution packages may change.
Existing matching installs are not reinstalled or automatically upgraded. Exact
policy currently supports apt and AWS CLI only; other versioned sources require
reviewed adapter work. This avoids inventing artifact URLs for unsupported pins.

Downloads require HTTPS, have a deadline and fail without source fallback. Exact
AWS archives must match the declared digest before extraction. Subprocesses use
argument arrays, fixed adapters and a timeout; raw output is captured rather than
copied to bootstrap logs. Version parsers produce only bounded receipt values.
Unknown/partial installations or exact-version mismatches fail without automatic
uninstall, downgrade, tree replacement or broad cleanup.

The bootstrap no longer has an independent package/install list. Required consumer
checks in the validator protect existing phases; retiring a required capability
needs a coordinated consumer change. Extra apt entries can be retired without
live-host removal, although AMI/transitive dependencies may retain the package.
The separate pinned AGENTS installer is unchanged. Podman is not added; SYS-001
will supply its approved profile entries and own runtime configuration/acceptance.

## Ordering, failure and receipt

[Bootstrap](../../infra/dev-host/templates/bootstrap-forge.sh.tftpl) clears old
success files before parser/profile checks, then invokes the fixed phase adapters.
Base packages precede account setup; Codex follows `forge` creation and the
separately reviewed host-policy installation. Existing service setup stays in its
original phases. Each helper invocation validates the whole profile and checks
target OS/architecture. Expiry is checked against America/New_York calendar dates.

The final phase rechecks every component and atomically writes
`/var/lib/gptclaw/host-tools.json` with canonical profile SHA-256, deployment SHA,
target, UTC observation time, identity, version, policy and verification result.
The bootstrap completion marker is atomically replaced afterward with matching
provenance. Failures clear both success files; partial results cannot masquerade
as current success. The receipt is root-owned, readable by `forge`, and excludes
source secrets, environments and raw diagnostics. It describes provisioning-time
tool verification, not ongoing drift or feature behavior.

## Verification and operation

[Offline tests](../../scripts/tests/test_host_tools.py) exercise strict parsing,
source/version refusal, exception expiry, installer failures, digest failure before
execution, existing-state conflicts, Codex identity, repeat/retirement behavior,
interrupted writes and failed final receipt publication. All installers, network
and systemd interactions are fake and filesystem fixtures are task-owned.
[Terraform tests](../../infra/dev-host/tests/host-tools.tftest.hcl) use mock AWS
and real local cloud-init to check embedded source/provenance, phase ordering,
replacement wiring and compressed payload size. Repository checks include the
same profile validator and focused test suite.

The [runbook](../../runbooks/manage-host-tools.md) defines the version-1 fields,
change workflow, channel exceptions, receipt inspection and retirement. Deployment
requires a reviewed protected plan, suitable recovery point and Daniel's specific
authorization/window, following [host recovery](../../runbooks/recover-dev-host.md).
Post-replacement acceptance must verify SSM/private SSH, original project volume
UUID/ownership and matching receipt; none has been claimed locally.

Rollback uses a reviewed revert through the pipeline and can replace compute
again. Check older package/source availability and exception expiry first; absence
blocks rollback pending a reviewed alternative. Channel-selected versions are not
byte-identical rebuilds. Preserve the protected project disk and do not attempt
live-host package removal or restoration of an entire user home.

## Traceability

| Requirements | Mechanism | Tasks | Acceptance |
|---|---|---|---|
| HTP-001, HTP-002 | Profile/schema, validator, source/version policies | T-002, T-003 | AC-001, AC-002 |
| HTP-003, HTP-004 | Embedded helper/context, ordered adapters, atomic receipt | T-004, T-005 | AC-003, AC-004 |
| HTP-005 | Conflict refusal, no-op verification, consumer checks, no uninstall | T-004, T-005 | AC-005 |
| HTP-006 | Existing pipeline/replacement path and recovery runbook | T-006 | AC-006 |
| HTP-007 | Runbook and distinct local/CI/deployed acceptance evidence | T-006, T-007 | AC-007 |

No component source decision remains pending for this implementation. Review,
merge, deployment authorization and host acceptance remain separate gates.
Daniel owns channel replacement before expiry and final acceptance.
