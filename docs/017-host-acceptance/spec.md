# SPEC-017: Development host acceptance

- **Status:** Draft; planning requested, execution not authorized by this request
- **Owner:** Daniel
- **Date:** 2026-10-09 (America/New_York)
- **Related features:** SYS-001, SYS-004 and SPEC-016 enrollment
- **Design:** [TDD-017](technical-design.md)
- **Tasks:** [TASKS-017](tasks.md)
- **Evidence:** [Acceptance record](acceptance.md)

## Outcome and scope

Prove the replacement development host can support private development, recover
through SSM, run an unprivileged container, and keep an explicitly configured
service alive after logout and reboot. Record results against the existing
[SPEC-014](../014-rootless-container-toolchain/spec.md),
[SPEC-015](../015-host-tool-profile/spec.md) and
[SPEC-016](../016-tailscale-workload-identity/spec.md) criteria before owner sign-off.
This initiative coordinates acceptance; it does not replace their requirements.

Daniel requested a new specification for the acceptance steps discussed in this
chat. Earlier implementation, repair and deployment authorizations remain valid.
Writing or merging this plan does not authorize fixture execution, closing
sessions, reboot, another replacement, or infrastructure changes. Daniel owns
execution scope and the interruption window; preserve any explicit authorization
already supplied when execution starts.

Include deployed provenance, installed receipts, private access, independent SSM
recovery, storage/identity checks, the existing synthetic rootless fixture,
logout/reboot observation, scoped cleanup and final evidence reconciliation.
Exclude new host packages, local Terraform, runtime implementation, public routes,
production, backup restore drills and a new replacement rehearsal. AWS inspection
and SSM access use the CLI. Infrastructure changes remain on the protected
GitHub Actions -> HCP Terraform -> AWS path.

## Observed starting point

October 9 read-only checks found successful bootstrap/tool/rootless receipts at
revision `6d90105136de55f7932c7e6857ba0bf6415db249`, with matching profile digest,
all 26 tool components passed, Tailscale Running/online with `tag:gptclaw-dev`,
and active SSM/CloudWatch services. The original project filesystem UUID and
forge ownership match; user manager and linger are active. Git authentication
and push succeeded after restoring a repository deploy key.

These observations do not prove an independent SSM login, container networking,
logout/reboot survival, or synthetic-source preservation across replacement.
Receipt timestamps are provisioning observations, not current drift guarantees.
Daniel reports replacement/enrollment success; confirm whether enrollment required
any manual key. Detailed baseline and limitations are in the acceptance record.

## Requirements

- HA-001: Tie checks to the actual instance, reviewed deployed revision, protected
  plan/apply and CI references. Validate current profile/receipt/marker consistency,
  tool usability as forge and installed host-policy revision. Never infer deployment
  from the current checkout or merge alone.
- HA-002: Prove independent CLI SSM access and private Tailscale/SSH access, expected
  node state/tag, and fresh-host enrollment without manual key entry. Attribute
  owner reports and retain unknown enrollment provenance as pending.
- HA-003: Verify filesystem UUID, forge UID/GID, subordinate mappings and project
  ownership against recorded baselines. Use only synthetic fixture files; record
  any missing pre-replacement source evidence without claiming it retrospectively.
- HA-004: Use the existing digest-pinned fixture as forge to prove build/run,
  bind-write ownership, DNS/outbound HTTPS, loopback-only HTTP, non-loopback refusal,
  declared resource limits, status and bounded restart after deliberate crash.
- HA-005: An independent observer must prove the fixture remains active after
  every forge session closes and starts after reboot before a new forge login.
  Record session/boot identity and HTTP/service evidence. Agree the window and
  reviewed operator reboot/observation method before interruption; do not improvise
  privilege grants or AWS instance mutations.
- HA-006: Stop on failed gates, retain bounded diagnostics and owned-resource
  inventory, and use independent SSM for recovery. Clean up only fixture-owned
  resources and verify listener/boot activation removal. Preserve shared caches,
  project data, credentials and unrelated workloads.
- HA-007: Publish sanitized commands/results, dates, revisions, limitations and
  owner decisions. Reconcile each original criterion, retain unresolved items,
  and mark a feature Delivered only after all its required evidence and Daniel's
  acceptance exist. No new replacement is implied by an unresolved criterion.

## Acceptance criteria

| ID | Required result and evidence | Requirements |
|---|---|---|
| AC-001 | Actual instance/deployment provenance, matching receipts and reviewed profile/policy; versions and usability checks recorded. | HA-001 |
| AC-002 | Independent CLI SSM connection, private connection and expected tagged online node; manual-key-free replacement enrollment supported by attributed or observed evidence. | HA-002 |
| AC-003 | Filesystem/identity/mappings match baseline; fixture writes belong to forge; missing replacement-source proof is explicitly tracked in the original criterion. | HA-003 |
| AC-004 | Fixture build, DNS/HTTPS, local HTTP, non-loopback refusal, resource configuration and bounded crash restart checks pass. | HA-004 |
| AC-005 | Independent evidence shows zero forge sessions with service/HTTP still working, then a changed boot ID and service/HTTP working before a new forge login. | HA-005 |
| AC-006 | Only owned fixture resources are removed, listener and activation are gone, and unrelated state is preserved; failure recovery disposition recorded where applicable. | HA-006 |
| AC-007 | Original criteria reconciled individually, unresolved scope assigned, evidence PR reviewed and Daniel's acceptance recorded without premature Delivered claims. | HA-007 |

## Completion and owner decisions

Daniel reviews this plan and supplies execution scope, an independent CLI SSM
session, and a maintenance window/operator path for logout and reboot. The agent
can prepare and run authorized ordinary checks, manage the owned fixture and
write evidence. The independent observer must remain outside the forge session
being tested; the disconnected agent cannot establish boot-before-login proof.

Existing SPEC-014 AC-003 requires synthetic-source preservation and cache rebuild
across replacement. First assess earlier evidence. If unavailable, keep that
criterion pending and propose a separately authorized follow-up; this initiative
cannot waive it or silently launch another replacement. Full SYS-001 acceptance
may therefore remain open after this plan's current-host checks pass.
