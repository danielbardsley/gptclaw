# SPEC-015: Host Tool Profile

- **Status:** Implementation in review; deployment and acceptance pending
- **Owner:** Daniel
- **Feature catalogue:** SYS-004
- **Last updated:** 2026-10-01 (America/New_York)
- **Design:** [TDD-015](technical-design.md)
- **Tasks:** [TASKS-015](tasks.md)
- **Context:** [Architecture](../platform/architecture.md), sections 10 and 14;
  [SYS-001](../014-rootless-container-toolchain/spec.md)

## Outcome and authorization

Make the development host's intentionally installed tools a reviewable profile
in GptClaw code. Daniel can see what is installed, why it is needed, where it
comes from, how its version is selected and how a replacement host verifies it.
A tool addition or update follows the existing infrastructure pipeline rather
than an agent installing a system package interactively.

Daniel authorized implementation with “Implement SYS-004” on October 1, 2026
(America/New_York), approving this specification's scope. He also explicitly
approved retaining the five existing upstream channels through November 1, 2026.
Implementation is authorized; merge, deployment and deployed acceptance remain
pending. See the [acceptance record](acceptance.md).

## Baseline and scope

The committed bootstrap installs an inline apt package list and separately
handles SSM, AWS CLI, Tailscale, CloudWatch Agent and the user-scoped Codex CLI.
Several existing download paths select a current release rather than an immutable
artifact. A completion record captures some component versions. These are source
observations, not an inventory of the live host or a claim of reproducible builds.

Include a versioned, validated profile, integration into provisioning, explicit
ownership of installation and version selection, a sanitized installed receipt,
offline tests and an operator runbook for additions, upgrades and retirement.
Start by representing the existing bootstrap's intentional tools. Any new tool
needs a stated capability and reviewed change; this specification is not a
shopping list of additional host utilities.

The profile covers explicitly requested packages/components, not every transitive
package in Ubuntu. Record the base OS/architecture and resolved AMI in deployment
evidence; the AMI selector remains separately owned by infrastructure. Include
bootstrap-managed user tools such as Codex with their actual installation identity;
listing one does not permit running its installer as root.

SYS-001 owns Podman prerequisites, mappings, networking, storage, Quadlet and
behavioral acceptance. SYS-004 provides their declaration mechanism once their
installation is approved. Either initiative may proceed first: migrate any
already-implemented tool list to the profile without duplicating it; if SYS-004
lands first, do not add or install candidate SYS-001 components until approved.
Neither draft establishes the other's implementation or acceptance.

Exclude project language version management (SYS-002), project dependency policy
(SYS-003), a privilege broker (SYS-005), periodic drift monitoring (RES-005), SBOMs,
package mirrors, automatic updates, live-host reconciliation, arbitrary install
commands, application services, production and public exposure. The reviewed host
AGENTS policy and its installer remain separate; this profile cannot update them.

## Requirements

### HTP-001: One strict, versioned declaration

Keep one authoritative repository-owned profile for intentionally provisioned
host tools. Each entry has a stable unique identifier, purpose/capability owner,
installation method and identity, source, explicit version-selection policy and
verification rule. Record the supported OS and architecture. Reject unknown
schema versions, unknown fields, duplicate identifiers, invalid types, unsupported
methods, missing policy/source and ambiguous package ownership before installation.
The format must not accept arbitrary shell commands or implicit optional tools.

### HTP-002: Explicit source and version policy

Use approved distribution repositories for distro packages by default. Declare
whether each component is exact-version selected, distribution-maintained, or an
explicitly documented existing upstream-channel exception. Immutable downloaded
artifacts require integrity verification before execution. Existing floating
installers must be visible exceptions with owner, reason, scope, review/expiry
date and removal step; do not silently grandfather them or claim exact rebuilds.
Daniel must approve retained exceptions before deployment. New floating sources
or trust changes require a concrete reviewed proposal.

An unavailable selected version or failed integrity check must fail installation;
never substitute a newer version or alternate source silently. Review policy
changes in code. Record actual installed versions even when policy permits distro
security updates. This feature does not disable existing OS security updates or
promise that a host remains at its provisioning-time versions indefinitely.

### HTP-003: Pipeline-owned installation

Render the reviewed profile with the bootstrap from the same Git revision and
install through committed code -> GitHub Actions -> HCP Terraform -> AWS. Preserve
phase ordering, including tools needed to bootstrap the profile itself. Keep
privileged operations inside the reviewed provisioning path; user-scoped tools
run as their declared user. Do not add a local apply/install interface, sudo or
IAM permissions, host security changes, or a dynamic installer fetched from the
working checkout. No second package list may independently control installation.

### HTP-004: Verification and receipt

Before declaring bootstrap complete, verify every required component is installed
under its declared identity and satisfies its declared version policy and narrow
capability check. Emit a machine-readable, non-secret receipt with profile schema
version, content digest, deployment revision, OS/architecture, component identifiers,
actual versions, verification result and observation time. Use stable paths and
atomic replacement. Failed or partial installation must not leave an apparently
current successful receipt or completion marker. Record sufficient sanitized
failure context for diagnosis without logging credentials, environments or
unrestricted command output. A receipt is provisioning evidence, not continuous
drift detection or feature acceptance.

### HTP-005: Safe changes and retirement

Repeated provisioning with a satisfied profile must preserve unrelated tools,
configuration, project data and user ownership. Detect incompatible existing
state and report it rather than silently downgrading, uninstalling or overwriting.
Removing an entry removes its provisioning intent on future hosts; it must not
trigger broad autoremove or live-host package deletion. A retirement PR must review
bootstrap dependencies and loss of capability, and verify the component is no
longer explicitly provisioned. A component may still exist through the AMI or a
transitive dependency; do not equate removal from the profile with absence.

### HTP-006: Replacement and recovery

Treat profile changes embedded in user data as potential instance replacement.
Before an authorized deployment, review the plan, maintenance window, quiesced
writes and suitable recovery point using the existing runbook. Preserve the
protected project volume, identities and private access. Rollback uses reviewed
code and the protected pipeline; unavailable older packages block rollback until
a reviewed alternative is selected. Do not promise byte-identical rollback for
channel-selected packages or restoration of the disposable root disk.

### HTP-007: Reviewable operation and evidence

Document how to propose a tool, update its policy, inspect a receipt, diagnose
failures and retire a tool. Test profile validation and installation decisions
with synthetic fixtures and mocked package/download commands. Record local, CI,
deployment and owner acceptance separately. Do not mark SYS-004 Delivered until
merged implementation and all required deployed criteria pass.

## Acceptance criteria

| ID | Observable result and evidence | Requirements |
|---|---|---|
| AC-001 | Valid current-baseline fixture passes; wrong schema, unknown fields, duplicate IDs, malformed types, unsupported methods and incomplete policy/source fail before any install call. Every existing intentional bootstrap tool has one reviewed disposition. | HTP-001 |
| AC-002 | Tests prove unavailable versions and integrity mismatches fail without fallback. Every selected source/policy is reviewable; any channel exception has Daniel's recorded decision, expiry and removal step. Receipt versions distinguish selection policy from observed state. | HTP-002 |
| AC-003 | Rendered infrastructure tests bind profile and bootstrap to one revision, preserve phase/user ordering and show profile changes affect user data. Review finds no independent competing list or new privilege grants. | HTP-003 |
| AC-004 | Tests cover partial installation, failed verification, stale receipt and interrupted writes; success is published only after all checks. Deployed receipt digest matches reviewed profile and every required tool passes as its intended user. | HTP-004 |
| AC-005 | Repeat/conflict fixtures preserve unrelated state; synthetic removal stops explicit provisioning without uninstall calls; migration review accounts for all old entries, consumers and configuration. | HTP-005 |
| AC-006 | Protected plan and deployment evidence retain project volume and identities; operator confirms access, original project filesystem/ownership and successful receipt after authorized replacement. Reviewed rollback instructions distinguish tested recovery from unexecuted steps and identify unavailable-version handling. | HTP-006 |
| AC-007 | Runbook and criterion-by-criterion acceptance record contain sanitized revision, checks, CI/deployment references, exception decisions and Daniel's acceptance. | HTP-007 |

## Decisions and completion

The approved baseline uses distribution-maintained apt packages with observed
versions, not an immutable snapshot of OS dependencies. Daniel approved temporary
existing-channel exceptions for SSM's snap fallback, AWS CLI, Tailscale, CloudWatch
Agent and Codex on October 1, 2026, through November 1, 2026 (America/New_York).
Each profile entry records Daniel as owner, its scope/reason and the removal step:
replace it with a reviewed versioned source before expiry. Validation blocks new
provisioning after expiry; operator follow-through is required, and running tools
are not automatically stopped. No approval for new upstream channels is implied.
The [runbook](../../runbooks/manage-host-tools.md) records component dispositions.

Deliver the profile/schema, provisioning integration, tests, receipt, operator
runbook and acceptance record. Acceptance of SYS-004 does not accept SYS-001's
runtime behavior or authorize later tool additions without review.
