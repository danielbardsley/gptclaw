# TDD-015: Host Tool Profile

- **Status:** Draft proposal
- **Owner:** Daniel
- **Last updated:** 2026-10-01 (America/New_York)
- **Specification:** [SPEC-015](spec.md)
- **Tasks:** [TASKS-015](tasks.md)

## Approach and existing integration

The [bootstrap template](../../infra/dev-host/templates/bootstrap-forge.sh.tftpl)
contains both the apt list and specialized installers. The
[compute definition](../../infra/dev-host/compute.tf) renders this into user data
and replaces compute on user-data changes. Preserve that deployment path and
existing phase-specific service setup. Do not construct a general package manager.

Propose `infra/dev-host/host-tools.json` with `schema_version: 1`, a target
OS/architecture and a component list. JSON allows Terraform rendering and Python
standard-library parsing without a YAML dependency. A checked-in schema/reference
and strict offline validator define permitted fields and installation policies.
Reject duplicate JSON keys as well as component IDs. Validate the entire profile
before any side effect; test that both the CI and provisioning paths reject the
same invalid fixtures. Python 3 supplied by the target base image must be checked
as a prerequisite before parsing; if unavailable, fail explicitly rather than
maintaining a fallback installation list.

Component records describe data, not commands: identifier, purpose, capability
owner, fixed installer adapter, installation identity, structured source,
version policy and fixed verification adapter. Adapter names are allowlisted in
reviewed code. Reject unexpected root/user combinations, invalid package/version
strings, URLs outside approved source policy and values interpreted as options.
Use argument arrays and no shell evaluation. Unknown adapters fail closed.

Suggested methods are distribution packages and a small set of named existing
component adapters. The inventory must determine the final adapter set. Entries
may refer to an adapter that provisions several tightly related packages, but
package ownership must be unique and the profile must contain the actual desired
package set. Specialized adapters retain service configuration in its existing
phase; profile membership/version policy controls installation. An absent optional
component must not leave a later phase calling its binary; required bootstrap
capabilities cannot be retired without updating and testing their consumers.

## Baseline migration

| Existing source mechanism | Proposed disposition, pending review |
|---|---|
| Inline apt list (`ca-certificates`, `curl`, `e2fsprogs`, `git`, `jq`, `nvme-cli`, `openssh-server`, `python3`, `rsyslog`, `sudo`, `ufw`, `unzip`) | Profile entries with purpose, distro source and distribution-maintained policy; preserve current consumers and privilege boundaries. |
| SSM unit detection with snap fallback | Explicit platform-component adapter; verify an existing supported installation or use a reviewed declared fallback, not an implicit alternate source. |
| AWS CLI downloaded zip | Select a verified immutable artifact or submit a bounded channel exception for Daniel's decision. |
| Tailscale upstream installer | Declare source and version policy; replace with a reviewed fixed method or record a bounded exception. |
| CloudWatch Agent current-release deb | Select a verified immutable artifact or submit a bounded exception. |
| Codex installer as `forge` | Keep unprivileged identity; resolve version/source policy or a bounded exception before deployment. |
| Host policy revision installer | Remains separately pinned and managed; profile does not control its content or installation. |
| SYS-001 package set | Add only when approved; use one profile declaration while SYS-001 owns configuration and capability acceptance. |

This table describes observed committed code and proposed work. It is not a claim
that a version-specific download endpoint exists or that any exception is approved.
Version and integrity mechanisms must be checked against authoritative component
documentation when selecting artifacts. Do not download or execute installers
while writing this plan.

## Rendering, verification and evidence

Read the profile as a Terraform source file and include its canonical content and
digest in the rendered bootstrap payload. Use the existing deployment revision
input for provenance. Ensure the profile is inside the remote Terraform upload
boundary; do not depend on a sibling file omitted from HCP execution. Any schema
or helper required during provisioning must likewise be embedded or included by
the reviewed render path. The implementation must test payload size against the
existing cloud-init transport limit before deployment.

After each adapter, run bounded version/capability probes and aggregate sanitized
results. Proposed receipt path is `/var/lib/gptclaw/host-tools.json`, root-owned
and readable by `forge`, containing only the approved metadata. Write a temporary
file in that directory, then atomically replace the receipt after full success.
Invalidate stale success at the start of an actual provisioning attempt, while
retaining a clearly labeled previous receipt if useful for diagnosis. Couple the
receipt digest/revision with the existing bootstrap completion record. The current
one-shot completion guard means changing the working checkout alone does not
reconcile the running host; the profile is applied through replacement bootstrap.

Separate profile presence, installed version verification and feature behavior.
For example, an installed Podman binary does not prove rootless storage or reboot
persistence. Those checks and acceptance remain in SPEC-014.

## Verification, rollout and recovery

Offline tests use temporary roots and mock installers; never apt, snap, systemd,
network downloads or real users. Cover malformed profiles, conflicting ownership,
argument injection, unsupported adapter/identity combinations, failed downloads,
integrity checks, missing versions, verification failures, partial/stale receipts,
repeat runs and retirement without deletion. Terraform tests inspect rendered
profile provenance, phase ordering and unchanged safeguards.

Run repository and changed-script checks plus pinned Terraform format, validate
and tests for implementation changes. Review CI separately. Deployment requires
Daniel's explicit scope/window approval and the
[replacement procedure](../../runbooks/recover-dev-host.md), including a suitable
recovery point and protected-volume plan review. Verify the deployed profile digest,
installed tools, private access and persistent project ownership afterward.

Rollback is a targeted reviewed revert through the pipeline and may replace
compute again. Review package availability before rollback; distribution/channel
policies may select different versions at different times. Never silently fall
back, uninstall unrelated packages, restore an entire user home or discard the
project disk. Record rollback review versus any actual drill distinctly.

## Planned files and traceability

| Component | Responsibility | Requirements | Tasks | Acceptance |
|---|---|---|---|---|
| Profile and schema/reference | Strict desired-tool contract and policies | HTP-001, HTP-002 | T-002, T-003 | AC-001, AC-002 |
| Validator and fixed adapter helpers | Validation, safe install decisions and verification | HTP-001–HTP-005 | T-003, T-004 | AC-001–AC-005 |
| Bootstrap/rendering and Terraform tests | Same-revision delivery, phase ordering, completion/receipt | HTP-003, HTP-004 | T-004, T-005 | AC-003, AC-004 |
| Isolated fixture tests | Failures, retries, migration and retirement | HTP-001–HTP-005 | T-005 | AC-001–AC-005 |
| Tool-profile runbook and recovery links | Change review, replacement and rollback | HTP-005–HTP-007 | T-006, T-007 | AC-005–AC-007 |
| Initiative acceptance record | Evidence and owner disposition | HTP-007 | T-007 | AC-007 |

Daniel owns policy/exception approval. The implementer resolves adapter feasibility,
artifact verification and existing-state conflicts at T-002. SYS-001 integration
order is resolved against merged code at implementation time, not by assuming
both drafts have already shipped. No new infrastructure resource is proposed.
