# TDD-017: Development host acceptance procedure

- **Status:** Draft
- **Owner:** Daniel
- **Date:** 2026-10-09 (America/New_York)
- **Specification:** [SPEC-017](spec.md)
- **Tasks:** [TASKS-017](tasks.md)

## Approach and components

Reuse the installed receipts and existing fixture; no application, installer,
new privileged helper or infrastructure code is introduced. Follow the
[rootless runbook](../../runbooks/manage-rootless-toolchain.md),
[tool-profile runbook](../../runbooks/manage-host-tools.md),
[federation runbook](../../runbooks/manage-tailscale-federation.md) and
[host recovery procedure](../../runbooks/recover-dev-host.md). The AWS CLI-only
session preference takes precedence over older console suggestions.

| Component | Responsibility | Requirements |
|---|---|---|
| Installed receipts and reviewed deployment runs | Provenance, versions and completion consistency | HA-001 |
| CLI SSM and private connection | Recovery, access and independent observation | HA-002, HA-005 |
| Filesystem and identity metadata | Retained project volume and mappings | HA-003 |
| `scripts/rootless-fixture.py` | Owned synthetic build, HTTP, crash and cleanup | HA-003–HA-006 |
| Initiative acceptance records | Results, original criterion mapping and owner acceptance | HA-007 |

## Phase 1: Readiness and baseline

Before fixture work, confirm authorized scope, clean/preserved Git state, intended
instance/account/region and deployed revision using scoped non-secret metadata.
Cross-check protected plan/apply/CI evidence. Compare the installed tool receipt,
bootstrap marker and rootless receipt with the reviewed profile; inspect installed
policy revision through its existing runbook. Record versions, rootless backends,
UID/GID and namespace maps without unrestricted engine or environment dumps.

Baseline UUID is `680fdc21-378e-466b-8b3f-8fa947eabc8d`, forge UID/GID 1002,
and subordinate UID/GID range `231072:65536`. Confirm mount and ownership rather
than changing them. Preserve historical results; fresh observations supplement
rather than rewrite older failure evidence.

Have Daniel or the independent operator open SSM from a separate authorized
client using the actual current instance target. Verify access before depending
on it for logout/reboot. Scope the observer identity so it does not create a
forge login. Record Tailscale Running/online/tag and a private connection; confirm
manual-key-free enrollment history with Daniel and deployed source evidence.
No token exchange logs, keys or authentication files go into evidence.

## Phase 2: Synthetic container behavior

Inspect the reviewed fixture before execution. Select a free high port (18081
is the existing default); do not stop an existing listener. Run as forge from
repository root, retaining the unique directory printed by `start`:

```sh
python3 scripts/rootless-fixture.py start --port 18081
python3 scripts/rootless-fixture.py check --directory "$fixture_directory" --non-loopback "$host_private_ipv4"
python3 scripts/rootless-fixture.py crash --directory "$fixture_directory"
```

Set `fixture_directory` to that printed task-owned directory, and
`host_private_ipv4` to an actual assigned non-loopback IPv4 address. These are
future commands, not executed results. Start pulls the pinned public base image,
builds only copied synthetic sources and installs a bounded user Quadlet. Capture
build/probe results, bind-file ownership, exact listener and unit limits. A local
non-loopback refusal proves this binding check, not every possible ingress path.
Crash kills only the labeled fixture and checks systemd restart and HTTP recovery.

## Phase 3: Last-session logout and reboot

Before interrupting access, record fixture path/name, selected port, expected
HTTP response, current boot ID, recovery connection and the approved window.
Choose an existing reviewed operator path for reboot and read-only observation;
if the operator cannot inspect the user service/loopback HTTP without a forge
login, stop and resolve that prerequisite. Do not add sudo permissions or use
direct AWS instance mutation. Check current backup adequacy and quiesce unrelated
writes before reboot; snapshot creation/restore is outside this slice.

Coordinate closure of every forge session, including this remote agent session.
From the independent operator session, record session absence plus user-manager,
fixture service/listener and expected HTTP response. Reboot only in the agreed
window using the selected operator path. After the host returns, reestablish SSM
as needed, record changed boot ID and verify service/listener/HTTP before any
forge login. If an observer creates a forge session first, repeat the affected
observation in an authorized window; do not call it a pass. Resume normal private
access only after recording independent evidence.

The fixture waits up to 120 seconds for the project mount. Failure or missing
storage stops acceptance; never initialize substitute project storage. A failing
service is diagnosed via scoped SSM metadata. Repairs to bootstrap/configuration
require reviewed code and the existing pipeline, with separate scope as needed.

## Phase 4: Cleanup and reconciliation

Export sanitized results, then run as forge:

```sh
python3 scripts/rootless-fixture.py cleanup --directory "$fixture_directory"
```

Cleanup verifies labels and unit digest before removal and refuses unexpected
files. Preserve failed resources for scoped inspection if it refuses; never use
broad prune/reset or recursive deletion. Shared base image/cache remains.
Verify listener and boot activation removal and compare unrelated inventory.

Update this acceptance record and SPEC-014/015/016 records/tasks by criterion.
Use passed/failed/pending/not applicable with reasons; record skipped checks,
unexecuted rollback and owner acceptance separately. This plan adds no waiver to
SPEC-014's synthetic-source replacement/rebuild requirement. Assess existing
evidence; record the gap and owner follow-up if not proven. Catalogue completion
requires each original feature's full acceptance, not completion of this checklist.

## Traceability

| Requirement | Tasks | Acceptance | Original criteria supported |
|---|---|---|---|
| HA-001 | T-001 | AC-001 | SPEC-014 AC-001; SPEC-015 AC-004/006/007 |
| HA-002 | T-002 | AC-002 | SPEC-016 AC-003 |
| HA-003 | T-001, T-003, T-007 | AC-003 | SPEC-014 AC-002/003; SPEC-016 AC-004 |
| HA-004 | T-003 | AC-004 | SPEC-014 AC-002/004/005 |
| HA-005 | T-004, T-005 | AC-005 | SPEC-014 AC-005 |
| HA-006 | T-006 | AC-006 | SPEC-014 AC-007 |
| HA-007 | T-007 | AC-007 | SPEC-014 AC-006/007; SPEC-015 AC-007; SPEC-016 AC-003/004 |

Documentation checks are Git whitespace and relative links. Existing fixture
execution is host acceptance, not local mocks or CI. No new tests are needed
for this planning-only change; CI retains its configured gates.
